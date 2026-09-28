"""Research Mission Manager for PROJECT AION.

Manages the complete lifecycle of autonomous research missions:
creation, planning, execution, pause/resume, cancellation, and retry.
"""
import uuid
import json
import logging
import datetime
from typing import Optional, Dict, Any, List, Callable

from database.db_manager import DBManager
from database.models import (
    ResearchMission, MissionStatus, MissionEvent
)
from research.modes import ResearchMode, ModeConfig, get_mode_config

logger = logging.getLogger('aion.missions')


class MissionError(Exception):
    """Raised when a mission operation fails."""
    pass


class InvalidTransitionError(MissionError):
    """Raised when an invalid mission state transition is attempted."""
    pass


class MissionManager:
    """Manages the lifecycle of autonomous research missions.

    Responsibilities:
    - Create missions with configurable parameters
    - Validate and enforce state machine transitions
    - Persist mission state to database
    - Track progress and emit events
    - Support pause/resume with checkpointing
    - Search for similar past missions (research memory)
    """

    def __init__(self, db: Optional[DBManager] = None):
        self.db = db or DBManager()

    def create_mission(
        self,
        objective: str,
        domain: str = '',
        mode: str = 'DEEP_RESEARCH',
        user_constraints: str = '',
        time_limit_hours: float = 0.0,
        budgets: Optional[Dict[str, int]] = None
    ) -> ResearchMission:
        """Create a new research mission.

        Args:
            objective: The research question or goal
            domain: Scientific domain (e.g., 'battery science', 'genomics')
            mode: Research mode (QUICK, DEEP_RESEARCH, AUTONOMOUS_DISCOVERY, etc.)
            user_constraints: User-specified constraints on the research
            time_limit_hours: Maximum time for the mission (0 = use mode default)
            budgets: Optional dict overriding mode defaults for agent_budget, literature_budget, etc.

        Returns:
            ResearchMission with PENDING status
        """
        # Validate mode
        try:
            research_mode = ResearchMode(mode)
        except ValueError:
            research_mode = ResearchMode.DEEP_RESEARCH
            logger.warning(f"Invalid mode '{mode}', defaulting to DEEP_RESEARCH")

        mode_config = get_mode_config(research_mode)

        mission_id = f"MISSION-{uuid.uuid4().hex[:12].upper()}"

        # Apply budgets from mode config, with user overrides
        agent_budget = (budgets or {}).get('agent_budget', mode_config.max_agent_calls)
        literature_budget = (budgets or {}).get('literature_budget', mode_config.max_papers)
        hypothesis_budget = (budgets or {}).get('hypothesis_budget', mode_config.initial_population_size)
        simulation_budget = (budgets or {}).get('simulation_budget', mode_config.max_simulations)
        effective_time_limit = time_limit_hours if time_limit_hours > 0 else mode_config.mission_timeout_hours

        mission_data = {
            'mission_id': mission_id,
            'objective': objective,
            'domain': domain,
            'mode': research_mode.value,
            'status': MissionStatus.PENDING.value,
            'user_constraints': user_constraints,
            'research_depth': mode_config.max_generations,
            'agent_budget': agent_budget,
            'literature_budget': literature_budget,
            'hypothesis_budget': hypothesis_budget,
            'simulation_budget': simulation_budget,
            'time_limit_hours': effective_time_limit
        }

        self.db.create_mission(mission_data)

        self._emit_event(mission_id, 'MISSION_CREATED', 
                        f'Mission created: {objective[:100]}',
                        phase='PENDING',
                        data={'mode': research_mode.value, 'domain': domain})

        # Check for similar past missions
        similar = self.db.search_similar_missions(objective, domain)
        if similar:
            self._emit_event(mission_id, 'SIMILAR_MISSION_FOUND',
                           f'Found {len(similar)} similar past mission(s). Review before proceeding.',
                           data={'similar_mission_ids': [m['mission_id'] for m in similar]})

        logger.info(f"Mission {mission_id} created: {objective[:80]}")

        return ResearchMission(
            mission_id=mission_id,
            objective=objective,
            domain=domain,
            mode=research_mode.value,
            agent_budget=agent_budget,
            literature_budget=literature_budget,
            hypothesis_budget=hypothesis_budget,
            simulation_budget=simulation_budget,
            time_limit_hours=effective_time_limit
        )

    def start_mission(self, mission_id: str) -> Dict[str, Any]:
        """Transition mission from PENDING to PLANNING."""
        return self._transition(mission_id, MissionStatus.PLANNING.value, 
                               'Mission started — entering planning phase')

    def pause_mission(self, mission_id: str, checkpoint: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Pause a running mission and save checkpoint state."""
        mission = self._get_mission_or_raise(mission_id)
        current_status = mission['status']

        # Can pause from any running state
        pausable_states = [
            MissionStatus.PLANNING.value, MissionStatus.RESEARCHING.value,
            MissionStatus.GENERATING_HYPOTHESES.value, MissionStatus.EVOLVING_HYPOTHESES.value,
            MissionStatus.FALSIFYING.value, MissionStatus.EXPERIMENTING.value,
            MissionStatus.PEER_REVIEW.value, MissionStatus.SYNTHESIS.value
        ]
        if current_status not in pausable_states:
            raise InvalidTransitionError(
                f"Cannot pause mission in state {current_status}. "
                f"Pausable states: {pausable_states}"
            )

        # Save checkpoint
        if checkpoint:
            self.db.update_mission_progress(mission_id, {
                'checkpoint_json': json.dumps({
                    'paused_from_state': current_status,
                    'checkpoint_data': checkpoint,
                    'paused_at': datetime.datetime.utcnow().isoformat()
                })
            })

        self.db.update_mission_status(mission_id, MissionStatus.PAUSED.value)
        self._emit_event(mission_id, 'MISSION_PAUSED',
                        f'Mission paused from state: {current_status}',
                        phase=MissionStatus.PAUSED.value,
                        data={'paused_from': current_status})

        logger.info(f"Mission {mission_id} paused from {current_status}")
        return self.get_mission_status(mission_id)

    def resume_mission(self, mission_id: str) -> Dict[str, Any]:
        """Resume a paused mission from its last checkpoint."""
        mission = self._get_mission_or_raise(mission_id)

        if mission['status'] != MissionStatus.PAUSED.value:
            raise InvalidTransitionError(
                f"Cannot resume mission in state {mission['status']}. Must be PAUSED."
            )

        # Determine resume state from checkpoint
        checkpoint = json.loads(mission.get('checkpoint_json', '{}') or '{}')
        resume_state = checkpoint.get('paused_from_state', MissionStatus.PLANNING.value)

        self.db.update_mission_status(mission_id, resume_state)
        self._emit_event(mission_id, 'MISSION_RESUMED',
                        f'Mission resumed to state: {resume_state}',
                        phase=resume_state,
                        data={'resumed_to': resume_state})

        logger.info(f"Mission {mission_id} resumed to {resume_state}")
        return self.get_mission_status(mission_id)

    def cancel_mission(self, mission_id: str, reason: str = 'Cancelled by user') -> Dict[str, Any]:
        """Cancel a mission. Terminal state."""
        mission = self._get_mission_or_raise(mission_id)

        if mission['status'] in (MissionStatus.COMPLETED.value,):
            raise InvalidTransitionError("Cannot cancel a completed mission.")

        self.db.update_mission_status(mission_id, MissionStatus.FAILED.value, error_message=reason)
        self._emit_event(mission_id, 'MISSION_CANCELLED', reason, phase=MissionStatus.FAILED.value)

        logger.info(f"Mission {mission_id} cancelled: {reason}")
        return self.get_mission_status(mission_id)

    def retry_mission(self, mission_id: str) -> Dict[str, Any]:
        """Retry a failed mission from the beginning."""
        mission = self._get_mission_or_raise(mission_id)

        if mission['status'] != MissionStatus.FAILED.value:
            raise InvalidTransitionError(
                f"Cannot retry mission in state {mission['status']}. Must be FAILED."
            )

        self.db.update_mission_status(mission_id, MissionStatus.PENDING.value, error_message='')
        self._emit_event(mission_id, 'MISSION_RETRY', 'Mission retried — resetting to PENDING',
                        phase=MissionStatus.PENDING.value)

        logger.info(f"Mission {mission_id} reset for retry")
        return self.get_mission_status(mission_id)

    def complete_mission(self, mission_id: str, discovery_index: float = 0.0,
                         findings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mark a mission as successfully completed."""
        progress_updates = {'discovery_index': discovery_index}
        if findings:
            progress_updates['findings_json'] = findings
        self.db.update_mission_progress(mission_id, progress_updates)
        self.db.update_mission_status(mission_id, MissionStatus.COMPLETED.value)
        self._emit_event(mission_id, 'MISSION_COMPLETED',
                        f'Mission completed with Discovery Index: {discovery_index:.1f}',
                        phase=MissionStatus.COMPLETED.value,
                        data={'discovery_index': discovery_index})
        logger.info(f"Mission {mission_id} completed — Discovery Index: {discovery_index:.1f}")
        return self.get_mission_status(mission_id)

    def fail_mission(self, mission_id: str, error_message: str) -> Dict[str, Any]:
        """Mark a mission as failed with an error message."""
        self.db.update_mission_status(mission_id, MissionStatus.FAILED.value, error_message=error_message)
        self._emit_event(mission_id, 'MISSION_FAILED', f'Mission failed: {error_message}',
                        phase=MissionStatus.FAILED.value)
        logger.error(f"Mission {mission_id} failed: {error_message}")
        return self.get_mission_status(mission_id)

    def advance_phase(self, mission_id: str, new_phase: str, progress: float = 0.0) -> Dict[str, Any]:
        """Advance mission to the next phase."""
        self.db.update_mission_status(mission_id, new_phase)
        self.db.update_mission_progress(mission_id, {
            'current_phase': new_phase,
            'progress': progress
        })
        self._emit_event(mission_id, 'PHASE_TRANSITION',
                        f'Entering phase: {new_phase}',
                        phase=new_phase)
        logger.info(f"Mission {mission_id} advanced to {new_phase}")
        return self.get_mission_status(mission_id)

    def update_progress(self, mission_id: str, progress_data: Dict[str, Any]):
        """Update mission progress counters."""
        self.db.update_mission_progress(mission_id, progress_data)

    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Get full mission status including progress and health metrics."""
        mission = self._get_mission_or_raise(mission_id)
        health = self.db.get_mission_health(mission_id)
        mission['health'] = health
        return mission

    def get_mission_history(self, mission_id: str) -> List[Dict[str, Any]]:
        """Get the complete event timeline for a mission."""
        return self.db.get_mission_events(mission_id)

    def list_all_missions(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List missions with optional status filter."""
        return self.db.list_missions(status=status, limit=limit)

    def log_event(self, mission_id: str, event_type: str, message: str,
                  agent_role: str = '', phase: str = '', data: Optional[Dict[str, Any]] = None):
        """Public method to log a mission event."""
        self._emit_event(mission_id, event_type, message, agent_role=agent_role,
                        phase=phase, data=data or {})

    # --- Private Helpers ---

    def _get_mission_or_raise(self, mission_id: str) -> Dict[str, Any]:
        """Retrieve a mission or raise MissionError if not found."""
        mission = self.db.get_mission(mission_id)
        if not mission:
            raise MissionError(f"Mission not found: {mission_id}")
        return mission

    def _transition(self, mission_id: str, new_status: str, message: str) -> Dict[str, Any]:
        """Execute a validated state transition."""
        mission = self._get_mission_or_raise(mission_id)
        current = mission['status']

        valid = MissionStatus.valid_transitions()
        if current in valid and new_status not in valid.get(current, []):
            raise InvalidTransitionError(
                f"Invalid transition: {current} -> {new_status}. "
                f"Valid transitions from {current}: {valid.get(current, [])}"
            )

        self.db.update_mission_status(mission_id, new_status)
        self.db.update_mission_progress(mission_id, {'current_phase': new_status})
        self._emit_event(mission_id, 'STATE_TRANSITION', message, phase=new_status,
                        data={'from': current, 'to': new_status})
        logger.info(f"Mission {mission_id}: {current} -> {new_status}")
        return self.get_mission_status(mission_id)

    def _emit_event(self, mission_id: str, event_type: str, message: str,
                   agent_role: str = '', phase: str = '',
                   data: Optional[Dict[str, Any]] = None):
        """Emit and persist a mission event."""
        self.db.insert_mission_event({
            'mission_id': mission_id,
            'event_type': event_type,
            'message': message,
            'agent_role': agent_role,
            'phase': phase,
            'data': data or {}
        })
