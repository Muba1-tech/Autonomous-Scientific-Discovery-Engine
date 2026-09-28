"""
AION X 2.0 — Professional Observability & Telemetry Subsystem
Tracks structured execution traces, agent latencies, token expenditures, and system health:
- Trace ID hierarchy (MISSION -> PHASE -> AGENT -> TOOL)
- Live agent latency breakdown
- Failure heatmap
- Compute & token utilization
"""

import time
import logging
from typing import Dict, Any, List, Optional
from database.db_manager import DBManager

logger = logging.getLogger(__name__)


class TelemetryLogger:
    """Collects and stores granular execution metrics for observability."""

    def __init__(self, mission_id: str, db_manager: Optional[DBManager] = None):
        self.mission_id = mission_id
        self.db = db_manager
        self._spans: List[Dict[str, Any]] = []

    def log_agent_span(
        self,
        agent_role: str,
        latency_seconds: float,
        model_name: str = "fast-router",
        prompt_tokens: int = 150,
        completion_tokens: int = 250,
        cost_usd: float = 0.0006,
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        """Logs a single agent execution span."""
        trace_id = f"{self.mission_id}:{agent_role.replace(' ', '_')}"
        span = {
            "mission_id": self.mission_id,
            "trace_id": trace_id,
            "agent_role": agent_role,
            "latency_seconds": round(latency_seconds, 3),
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": round(cost_usd, 6),
            "status": status,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self._spans.append(span)

        if self.db:
            try:
                self.db.insert_telemetry_log(
                    mission_id=self.mission_id,
                    trace_id=trace_id,
                    agent_role=agent_role,
                    model_name=model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_seconds=latency_seconds,
                    cost_usd=cost_usd,
                    status=status
                )
            except Exception as e:
                logger.warning(f"Failed to record telemetry in DB: {e}")

        return span

    def get_summary(self) -> Dict[str, Any]:
        """Returns aggregate execution statistics."""
        if not self._spans:
            return {
                "total_spans": 0,
                "total_latency_seconds": 0.0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "spans": []
            }

        total_lat = sum(s["latency_seconds"] for s in self._spans)
        total_tokens = sum(s["prompt_tokens"] + s["completion_tokens"] for s in self._spans)
        total_cost = sum(s["cost_usd"] for s in self._spans)

        return {
            "total_spans": len(self._spans),
            "total_latency_seconds": round(total_lat, 2),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "spans": self._spans
        }
