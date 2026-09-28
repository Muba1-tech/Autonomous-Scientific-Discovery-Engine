import sqlite3
import csv
import io
import json
import threading
from typing import List, Dict, Any, Optional
from database.migrations import run_migrations
from config import Config

class DBManager:
    _lock = threading.Lock()

    def __init__(self, db_name=None):
        self.db_name = db_name or Config.DB_PATH
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False, timeout=20.0)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        with self._lock:
            run_migrations(self.conn)
            self._safe_commit()

    def _safe_commit(self):
        try:
            self.conn.commit()
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            pass
        except Exception:
            pass

    # --- Backward-Compatible Existing Methods ---
    def insert_paper(self, title: str, abstract: str, source: str, research_id: str = None, url: str = None, authors: str = None, year: int = None):
        with self._lock:
            cursor = self.conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO papers (research_id, title, abstract, source, url, authors, year) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (research_id, title, abstract, source, url, authors, year)
                )
                self._safe_commit()
                return cursor.lastrowid
            except sqlite3.OperationalError:
                run_migrations(self.conn)
                cursor.execute(
                    "INSERT INTO papers (research_id, title, abstract, source, url, authors, year) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (research_id, title, abstract, source, url, authors, year)
                )
                self._safe_commit()
                return cursor.lastrowid

    def insert_hypothesis(self, content: str, verdict: str, score: float, research_id: str = None, domain: str = None, title: str = None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO hypotheses (research_id, content, verdict, score, domain, title) VALUES (?, ?, ?, ?, ?, ?)", 
                (research_id, content, verdict, score, domain, title)
            )
            self._safe_commit()
            return cursor.lastrowid
        except sqlite3.OperationalError:
            run_migrations(self.conn)
            cursor.execute(
                "INSERT INTO hypotheses (research_id, content, verdict, score, domain, title) VALUES (?, ?, ?, ?, ?, ?)", 
                (research_id, content, verdict, score, domain, title)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_approved_hypotheses(self, limit: int = 3) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM hypotheses WHERE verdict LIKE '%Approved%' ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_all_approved_hypotheses(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM hypotheses WHERE verdict LIKE '%Approved%'")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_success_rate(self) -> float:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hypotheses")
        total = cursor.fetchone()[0]
        if total == 0:
            return 1.0
        cursor.execute("SELECT COUNT(*) FROM hypotheses WHERE verdict LIKE '%Approved%'")
        approved = cursor.fetchone()[0]
        return approved / total

    def clear_memory(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM papers")
        cursor.execute("DELETE FROM hypotheses")
        cursor.execute("DELETE FROM research_gaps")
        cursor.execute("DELETE FROM agent_memory")
        cursor.execute("DELETE FROM research_history")
        cursor.execute("DELETE FROM citation_verifications")
        self._safe_commit()

    def export_hypotheses_to_csv(self) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, content, verdict, score FROM hypotheses")
        rows = cursor.fetchall()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Content', 'Verdict', 'Score'])
        writer.writerows(rows)
        return output.getvalue()

    def export_papers_to_csv(self) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, abstract, source FROM papers")
        rows = cursor.fetchall()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Title', 'Abstract', 'Source'])
        writer.writerows(rows)
        return output.getvalue()

    # --- New System Methods ---

    # Research Gaps
    def insert_research_gap(self, gap_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO research_gaps 
            (gap_id, research_id, topic, description, supporting_papers, evidence, paper_count, confidence_score, potential_direction, related_concepts, research_domain)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                gap_data.get('gap_id'),
                gap_data.get('research_id'),
                gap_data.get('topic'),
                gap_data.get('description'),
                json.dumps(gap_data.get('supporting_papers', [])),
                json.dumps(gap_data.get('evidence', [])),
                gap_data.get('paper_count', 0),
                gap_data.get('confidence_score', 0.0),
                gap_data.get('potential_direction', ''),
                json.dumps(gap_data.get('related_concepts', [])),
                gap_data.get('research_domain', '')
            )
        )
        self._safe_commit()

    def get_research_gaps(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if domain and domain.strip():
            cursor.execute("SELECT * FROM research_gaps WHERE research_domain LIKE ? ORDER BY id DESC", (f"%{domain}%",))
        else:
            cursor.execute("SELECT * FROM research_gaps ORDER BY id DESC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d['supporting_papers'] = json.loads(d['supporting_papers']) if d.get('supporting_papers') else []
            d['evidence'] = json.loads(d['evidence']) if d.get('evidence') else []
            d['related_concepts'] = json.loads(d['related_concepts']) if d.get('related_concepts') else []
            results.append(d)
        return results

    # Hypothesis Scores
    def insert_hypothesis_scores(self, hypothesis_id: int, research_id: str, scores: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO hypothesis_scores 
            (hypothesis_id, research_id, novelty_score, feasibility_score, potential_impact_score, evidence_strength, priority_score, sub_metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                hypothesis_id,
                research_id,
                scores.get('novelty_score', 0.0),
                scores.get('feasibility_score', 0.0),
                scores.get('potential_impact_score', 0.0),
                scores.get('evidence_strength', 0.0),
                scores.get('priority_score', 0.0),
                json.dumps(scores.get('sub_metrics', {}))
            )
        )
        self._safe_commit()

    # Evolutionary Memory
    def insert_agent_memory(self, memory_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO agent_memory 
            (research_id, domain, hypothesis, evidence, methodology, experiment_result, outcome, user_feedback, novelty_score, feasibility_score, impact_score, patterns_extracted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                memory_data.get('research_id'),
                memory_data.get('domain'),
                memory_data.get('hypothesis'),
                memory_data.get('evidence'),
                memory_data.get('methodology'),
                memory_data.get('experiment_result'),
                memory_data.get('outcome', 'SUCCESS'),
                memory_data.get('user_feedback', ''),
                memory_data.get('novelty_score', 0.0),
                memory_data.get('feasibility_score', 0.0),
                memory_data.get('impact_score', 0.0),
                json.dumps(memory_data.get('patterns_extracted', []))
            )
        )
        self._safe_commit()

    def get_agent_memory(self, domain: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if domain:
            cursor.execute("SELECT * FROM agent_memory WHERE domain LIKE ? ORDER BY id DESC LIMIT ?", (f"%{domain}%", limit))
        else:
            cursor.execute("SELECT * FROM agent_memory ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d['patterns_extracted'] = json.loads(d['patterns_extracted']) if d.get('patterns_extracted') else []
            results.append(d)
        return results

    # Citation Verifications
    def insert_citation_verifications(self, research_id: str, verifications: List[Dict[str, Any]]):
        cursor = self.conn.cursor()
        for v in verifications:
            cursor.execute('''INSERT INTO citation_verifications 
                (research_id, claim_text, status, supporting_source, relevant_evidence, confidence)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    research_id,
                    v.get('claim_text'),
                    v.get('status'),
                    v.get('supporting_source'),
                    v.get('relevant_evidence'),
                    v.get('confidence', 0.0)
                )
            )
        self._safe_commit()

    # Research History
    def insert_research_history(self, history_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO research_history 
            (research_id, domain, question, papers_json, gaps_json, hypothesis_text, scores_json, experiment_json, verifications_json, explainability_json, report_markdown, package_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                history_data.get('research_id'),
                history_data.get('domain'),
                history_data.get('question'),
                json.dumps(history_data.get('papers', [])),
                json.dumps(history_data.get('gaps', [])),
                history_data.get('hypothesis_text'),
                json.dumps(history_data.get('scores', {})),
                json.dumps(history_data.get('experiment', {})),
                json.dumps(history_data.get('verifications', [])),
                json.dumps(history_data.get('explainability', {})),
                history_data.get('report_markdown', ''),
                history_data.get('package_path', '')
            )
        )
        self._safe_commit()

    def get_research_history_list(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, research_id, domain, question, created_at, package_path FROM research_history ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def get_research_history_by_id(self, research_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM research_history WHERE research_id = ?", (research_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d['papers'] = json.loads(d['papers_json']) if d.get('papers_json') else []
        d['gaps'] = json.loads(d['gaps_json']) if d.get('gaps_json') else []
        d['scores'] = json.loads(d['scores_json']) if d.get('scores_json') else {}
        d['experiment'] = json.loads(d['experiment_json']) if d.get('experiment_json') else {}
        d['verifications'] = json.loads(d['verifications_json']) if d.get('verifications_json') else []
        d['explainability'] = json.loads(d['explainability_json']) if d.get('explainability_json') else {}
        return d

    # Cross Domain Connections
    def insert_cross_domain_connection(self, connection_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO cross_domain_connections 
            (research_id, source_domain, target_domain, transferred_concept, rationale, novelty_score, impact_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                connection_data.get('research_id'),
                connection_data.get('source_domain'),
                connection_data.get('target_domain'),
                connection_data.get('transferred_concept'),
                connection_data.get('rationale'),
                connection_data.get('novelty_score', 0.0),
                connection_data.get('impact_score', 0.0)
            )
        )
        self._safe_commit()

    # ========================================================================
    # PROJECT AION — Advanced Autonomous Scientist Upgrade Methods
    # ========================================================================

    # --- Mission CRUD ---

    def create_mission(self, mission_data: Dict[str, Any]) -> int:
        """Create a new research mission and return its database ID."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO missions 
            (mission_id, objective, domain, mode, status, user_constraints, research_depth,
             agent_budget, literature_budget, hypothesis_budget, simulation_budget, time_limit_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                mission_data['mission_id'],
                mission_data['objective'],
                mission_data.get('domain', ''),
                mission_data.get('mode', 'DEEP_RESEARCH'),
                mission_data.get('status', 'PENDING'),
                mission_data.get('user_constraints', ''),
                mission_data.get('research_depth', 5),
                mission_data.get('agent_budget', 100),
                mission_data.get('literature_budget', 50),
                mission_data.get('hypothesis_budget', 20),
                mission_data.get('simulation_budget', 50),
                mission_data.get('time_limit_hours', 2.0)
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a mission by its mission_id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d['findings'] = json.loads(d.get('findings_json', '{}') or '{}')
        d['evidence'] = json.loads(d.get('evidence_json', '[]') or '[]')
        d['checkpoint'] = json.loads(d.get('checkpoint_json', '{}') or '{}')
        return d

    def update_mission_status(self, mission_id: str, status: str, error_message: str = ''):
        """Update mission status and timestamp."""
        cursor = self.conn.cursor()
        now = __import__('datetime').datetime.utcnow().isoformat()
        if status in ('COMPLETED', 'FAILED'):
            cursor.execute(
                "UPDATE missions SET status = ?, error_message = ?, updated_at = ?, completed_at = ? WHERE mission_id = ?",
                (status, error_message, now, now, mission_id)
            )
        else:
            cursor.execute(
                "UPDATE missions SET status = ?, error_message = ?, updated_at = ? WHERE mission_id = ?",
                (status, error_message, now, mission_id)
            )
        self._safe_commit()

    def update_mission_progress(self, mission_id: str, progress_data: Dict[str, Any]):
        """Update mission progress counters and current phase."""
        cursor = self.conn.cursor()
        now = __import__('datetime').datetime.utcnow().isoformat()
        sets = ["updated_at = ?"]
        vals = [now]
        allowed_fields = [
            'progress', 'current_phase', 'papers_found', 'claims_extracted',
            'hypotheses_generated', 'hypotheses_survived', 'experiments_run',
            'falsification_tests', 'peer_reviews', 'discovery_index'
        ]
        for field_name in allowed_fields:
            if field_name in progress_data:
                sets.append(f"{field_name} = ?")
                vals.append(progress_data[field_name])
        # JSON fields
        for json_field in ['findings_json', 'evidence_json', 'checkpoint_json']:
            if json_field in progress_data:
                sets.append(f"{json_field} = ?")
                vals.append(json.dumps(progress_data[json_field]) if not isinstance(progress_data[json_field], str) else progress_data[json_field])
        vals.append(mission_id)
        cursor.execute(f"UPDATE missions SET {', '.join(sets)} WHERE mission_id = ?", tuple(vals))
        self._safe_commit()

    def list_missions(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List missions, optionally filtered by status."""
        cursor = self.conn.cursor()
        if status:
            cursor.execute(
                "SELECT * FROM missions WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute("SELECT * FROM missions ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]

    def search_similar_missions(self, objective: str, domain: str = '', limit: int = 5) -> List[Dict[str, Any]]:
        """Search for missions with similar objectives or domains."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM missions WHERE (objective LIKE ? OR domain LIKE ?) AND status = 'COMPLETED' ORDER BY created_at DESC LIMIT ?",
            (f"%{objective[:50]}%", f"%{domain}%", limit)
        )
        return [dict(r) for r in cursor.fetchall()]

    # --- Agent Run Tracking ---

    def insert_agent_run(self, run_data: Dict[str, Any]) -> int:
        """Record an agent execution attempt."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO agent_runs 
            (mission_id, research_id, agent_role, agent_class, status, input_summary,
             output_summary, output_data_json, confidence, execution_time_seconds,
             token_usage_json, error_message, attempt_number, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                run_data.get('mission_id', ''),
                run_data.get('research_id', ''),
                run_data['agent_role'],
                run_data.get('agent_class', ''),
                run_data.get('status', 'PENDING'),
                run_data.get('input_summary', ''),
                run_data.get('output_summary', ''),
                json.dumps(run_data.get('output_data', {})),
                run_data.get('confidence', 0.0),
                run_data.get('execution_time_seconds', 0.0),
                json.dumps(run_data.get('token_usage', {})),
                run_data.get('error_message', ''),
                run_data.get('attempt_number', 1),
                run_data.get('started_at'),
                run_data.get('completed_at')
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_agent_runs(self, mission_id: str, agent_role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get agent runs for a mission, optionally filtered by role."""
        cursor = self.conn.cursor()
        if agent_role:
            cursor.execute(
                "SELECT * FROM agent_runs WHERE mission_id = ? AND agent_role = ? ORDER BY id",
                (mission_id, agent_role)
            )
        else:
            cursor.execute("SELECT * FROM agent_runs WHERE mission_id = ? ORDER BY id", (mission_id,))
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            d['output_data'] = json.loads(d.get('output_data_json', '{}') or '{}')
            d['token_usage'] = json.loads(d.get('token_usage_json', '{}') or '{}')
            results.append(d)
        return results

    def update_agent_run_status(self, run_id: int, status: str, output_summary: str = '',
                                 confidence: float = 0.0, execution_time: float = 0.0,
                                 error_message: str = ''):
        """Update an agent run's status after completion or failure."""
        cursor = self.conn.cursor()
        now = __import__('datetime').datetime.utcnow().isoformat()
        cursor.execute(
            """UPDATE agent_runs SET status = ?, output_summary = ?, confidence = ?,
               execution_time_seconds = ?, error_message = ?, completed_at = ? WHERE id = ?""",
            (status, output_summary, confidence, execution_time, error_message, now, run_id)
        )
        self._safe_commit()

    # --- Mission Event Logging ---

    def insert_mission_event(self, event_data: Dict[str, Any]) -> int:
        """Log a mission lifecycle event for the activity timeline."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO mission_events 
            (mission_id, event_type, message, agent_role, phase, data_json)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                event_data['mission_id'],
                event_data['event_type'],
                event_data['message'],
                event_data.get('agent_role', ''),
                event_data.get('phase', ''),
                json.dumps(event_data.get('data', {}))
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_mission_events(self, mission_id: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Get the event timeline for a mission."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mission_events WHERE mission_id = ? ORDER BY timestamp ASC LIMIT ?",
            (mission_id, limit)
        )
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            d['data'] = json.loads(d.get('data_json', '{}') or '{}')
            results.append(d)
        return results

    # --- Evolving Hypotheses ---

    def insert_evolving_hypothesis(self, hyp_data: Dict[str, Any]) -> int:
        """Insert a hypothesis into the evolutionary population."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO evolving_hypotheses 
            (hypothesis_id, mission_id, research_id, statement, domain, generation,
             parent_ids_json, assumptions_json, supporting_evidence_json, contradicting_evidence_json,
             novelty_score, evidence_score, feasibility_score, impact_score,
             falsifiability_score, reproducibility_score, confidence, uncertainty, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                hyp_data['hypothesis_id'],
                hyp_data['mission_id'],
                hyp_data.get('research_id', ''),
                hyp_data['statement'],
                hyp_data.get('domain', ''),
                hyp_data.get('generation', 0),
                json.dumps(hyp_data.get('parent_ids', [])),
                json.dumps(hyp_data.get('assumptions', [])),
                json.dumps(hyp_data.get('supporting_evidence', [])),
                json.dumps(hyp_data.get('contradicting_evidence', [])),
                hyp_data.get('novelty_score', 0.0),
                hyp_data.get('evidence_score', 0.0),
                hyp_data.get('feasibility_score', 0.0),
                hyp_data.get('impact_score', 0.0),
                hyp_data.get('falsifiability_score', 0.0),
                hyp_data.get('reproducibility_score', 0.0),
                hyp_data.get('confidence', 0.0),
                hyp_data.get('uncertainty', 1.0),
                hyp_data.get('status', 'ACTIVE')
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_evolving_hypotheses(self, mission_id: str, generation: Optional[int] = None,
                                 status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get hypotheses from the evolutionary population."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM evolving_hypotheses WHERE mission_id = ?"
        params: list = [mission_id]
        if generation is not None:
            query += " AND generation = ?"
            params.append(generation)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY novelty_score DESC"
        cursor.execute(query, tuple(params))
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            for jf in ['parent_ids_json', 'assumptions_json', 'supporting_evidence_json', 'contradicting_evidence_json']:
                key = jf.replace('_json', '')
                d[key] = json.loads(d.get(jf, '[]') or '[]')
            results.append(d)
        return results

    def update_hypothesis_status(self, hypothesis_id: str, status: str, scores: Optional[Dict[str, float]] = None):
        """Update an evolving hypothesis status and optionally its scores."""
        cursor = self.conn.cursor()
        if scores:
            cursor.execute(
                """UPDATE evolving_hypotheses SET status = ?, novelty_score = ?, evidence_score = ?,
                   feasibility_score = ?, impact_score = ?, falsifiability_score = ?,
                   reproducibility_score = ?, confidence = ?, uncertainty = ? WHERE hypothesis_id = ?""",
                (status, scores.get('novelty', 0), scores.get('evidence', 0),
                 scores.get('feasibility', 0), scores.get('impact', 0),
                 scores.get('falsifiability', 0), scores.get('reproducibility', 0),
                 scores.get('confidence', 0), scores.get('uncertainty', 1.0), hypothesis_id)
            )
        else:
            cursor.execute(
                "UPDATE evolving_hypotheses SET status = ? WHERE hypothesis_id = ?",
                (status, hypothesis_id)
            )
        self._safe_commit()

    # --- Debates ---

    def insert_debate(self, debate_data: Dict[str, Any]) -> int:
        """Store a scientific debate record."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO debates 
            (debate_id, mission_id, hypothesis_id, advocate_arguments_json, skeptic_arguments_json,
             evidence_used_json, evidence_quality, logical_weaknesses_json, unresolved_questions_json,
             methodology_review, statistical_review, verdict, judge_rationale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                debate_data['debate_id'],
                debate_data.get('mission_id', ''),
                debate_data.get('hypothesis_id', ''),
                json.dumps(debate_data.get('advocate_arguments', [])),
                json.dumps(debate_data.get('skeptic_arguments', [])),
                json.dumps(debate_data.get('evidence_used', [])),
                debate_data.get('evidence_quality', 0.0),
                json.dumps(debate_data.get('logical_weaknesses', [])),
                json.dumps(debate_data.get('unresolved_questions', [])),
                debate_data.get('methodology_review', ''),
                debate_data.get('statistical_review', ''),
                debate_data.get('verdict', 'UNCERTAIN'),
                debate_data.get('judge_rationale', '')
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_debates(self, mission_id: str) -> List[Dict[str, Any]]:
        """Get all debates for a mission."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM debates WHERE mission_id = ? ORDER BY created_at", (mission_id,))
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            for jf in ['advocate_arguments_json', 'skeptic_arguments_json', 'evidence_used_json',
                        'logical_weaknesses_json', 'unresolved_questions_json']:
                key = jf.replace('_json', '')
                d[key] = json.loads(d.get(jf, '[]') or '[]')
            results.append(d)
        return results

    # --- Peer Reviews ---

    def insert_peer_review(self, review_data: Dict[str, Any]) -> int:
        """Store a peer review record."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO peer_reviews 
            (review_id, mission_id, research_id, reviewer_role, methodology_assessment,
             evidence_assessment, reproducibility_assessment, statistical_validity,
             strengths_json, weaknesses_json, recommendations_json, overall_quality_score, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                review_data['review_id'],
                review_data.get('mission_id', ''),
                review_data.get('research_id', ''),
                review_data.get('reviewer_role', 'PeerReviewer'),
                review_data.get('methodology_assessment', ''),
                review_data.get('evidence_assessment', ''),
                review_data.get('reproducibility_assessment', ''),
                review_data.get('statistical_validity', ''),
                json.dumps(review_data.get('strengths', [])),
                json.dumps(review_data.get('weaknesses', [])),
                json.dumps(review_data.get('recommendations', [])),
                review_data.get('overall_quality_score', 0.0),
                review_data.get('confidence', 0.0)
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    # --- Falsification ---

    def insert_falsification_result(self, result_data: Dict[str, Any]) -> int:
        """Store a falsification test result."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO falsification_results 
            (falsification_id, mission_id, hypothesis_id, criterion, test_description,
             test_type, evidence_json, result, explanation, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                result_data['falsification_id'],
                result_data.get('mission_id', ''),
                result_data.get('hypothesis_id', ''),
                result_data['criterion'],
                result_data['test_description'],
                result_data.get('test_type', 'conceptual'),
                json.dumps(result_data.get('evidence', {})),
                result_data.get('result', 'INCONCLUSIVE'),
                result_data.get('explanation', ''),
                result_data.get('confidence', 0.0)
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_falsification_results(self, hypothesis_id: str) -> List[Dict[str, Any]]:
        """Get all falsification test results for a hypothesis."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM falsification_results WHERE hypothesis_id = ? ORDER BY created_at",
            (hypothesis_id,)
        )
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            d['evidence'] = json.loads(d.get('evidence_json', '{}') or '{}')
            results.append(d)
        return results

    def get_falsification_summary(self, hypothesis_id: str) -> Dict[str, Any]:
        """Get aggregate falsification stats for a hypothesis."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT result, COUNT(*) as cnt FROM falsification_results WHERE hypothesis_id = ? GROUP BY result",
            (hypothesis_id,)
        )
        summary = {'hypothesis_id': hypothesis_id, 'tests_attempted': 0, 'tests_passed': 0,
                    'tests_failed': 0, 'tests_inconclusive': 0}
        for row in cursor.fetchall():
            r = dict(row)
            count = r['cnt']
            summary['tests_attempted'] += count
            if r['result'] == 'PASSED':
                summary['tests_passed'] = count
            elif r['result'] == 'FAILED':
                summary['tests_failed'] = count
            elif r['result'] == 'INCONCLUSIVE':
                summary['tests_inconclusive'] = count
        if summary['tests_attempted'] > 0:
            summary['survival_score'] = round((summary['tests_passed'] / summary['tests_attempted']) * 100, 1)
        else:
            summary['survival_score'] = 0.0
        return summary

    # --- Contradiction Records ---

    def insert_contradiction(self, contradiction_data: Dict[str, Any]) -> int:
        """Store a contradiction record."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO contradiction_records 
            (contradiction_id, mission_id, claim_text, claim_type,
             supporting_evidence_json, contradicting_evidence_json,
             methodology_comparison, dataset_comparison, condition_comparison,
             contradiction_strength, possible_explanation, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                contradiction_data['contradiction_id'],
                contradiction_data.get('mission_id', ''),
                contradiction_data['claim_text'],
                contradiction_data.get('claim_type', 'HYPOTHESIS'),
                json.dumps(contradiction_data.get('supporting_evidence', [])),
                json.dumps(contradiction_data.get('contradicting_evidence', [])),
                contradiction_data.get('methodology_comparison', ''),
                contradiction_data.get('dataset_comparison', ''),
                contradiction_data.get('condition_comparison', ''),
                contradiction_data.get('contradiction_strength', 0.0),
                contradiction_data.get('possible_explanation', ''),
                contradiction_data.get('confidence', 0.0)
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_contradictions(self, mission_id: str) -> List[Dict[str, Any]]:
        """Get all contradiction records for a mission."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM contradiction_records WHERE mission_id = ? ORDER BY contradiction_strength DESC",
            (mission_id,)
        )
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            d['supporting_evidence'] = json.loads(d.get('supporting_evidence_json', '[]') or '[]')
            d['contradicting_evidence'] = json.loads(d.get('contradicting_evidence_json', '[]') or '[]')
            results.append(d)
        return results

    # --- Knowledge Graph Nodes & Edges ---

    def insert_knowledge_node(self, node_data: Dict[str, Any]) -> int:
        """Insert or update a knowledge graph node."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO knowledge_nodes 
            (node_id, node_type, label, properties_json, mission_id)
            VALUES (?, ?, ?, ?, ?)''',
            (
                node_data['node_id'],
                node_data['node_type'],
                node_data['label'],
                json.dumps(node_data.get('properties', {})),
                node_data.get('mission_id', '')
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def insert_knowledge_edge(self, edge_data: Dict[str, Any]) -> int:
        """Insert a knowledge graph edge."""
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO knowledge_edges 
            (source_node_id, target_node_id, relation_type, weight, properties_json, mission_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                edge_data['source_node_id'],
                edge_data['target_node_id'],
                edge_data['relation_type'],
                edge_data.get('weight', 1.0),
                json.dumps(edge_data.get('properties', {})),
                edge_data.get('mission_id', '')
            )
        )
        self._safe_commit()
        return cursor.lastrowid

    def query_knowledge_graph(self, node_id: Optional[str] = None, node_type: Optional[str] = None,
                               mission_id: Optional[str] = None) -> Dict[str, Any]:
        """Query the knowledge graph for nodes and their relationships."""
        cursor = self.conn.cursor()
        # Get nodes
        node_query = "SELECT * FROM knowledge_nodes WHERE 1=1"
        node_params: list = []
        if node_id:
            node_query += " AND node_id = ?"
            node_params.append(node_id)
        if node_type:
            node_query += " AND node_type = ?"
            node_params.append(node_type)
        if mission_id:
            node_query += " AND mission_id = ?"
            node_params.append(mission_id)
        cursor.execute(node_query, tuple(node_params))
        nodes = []
        for r in cursor.fetchall():
            d = dict(r)
            d['properties'] = json.loads(d.get('properties_json', '{}') or '{}')
            nodes.append(d)

        # Get edges
        edge_query = "SELECT * FROM knowledge_edges WHERE 1=1"
        edge_params: list = []
        if mission_id:
            edge_query += " AND mission_id = ?"
            edge_params.append(mission_id)
        if node_id:
            edge_query += " AND (source_node_id = ? OR target_node_id = ?)"
            edge_params.extend([node_id, node_id])
        cursor.execute(edge_query, tuple(edge_params))
        edges = []
        for r in cursor.fetchall():
            d = dict(r)
            d['properties'] = json.loads(d.get('properties_json', '{}') or '{}')
            edges.append(d)

        return {'nodes': nodes, 'edges': edges}

    # --- Mission Health & Observability ---

    def get_mission_health(self, mission_id: str) -> Dict[str, Any]:
        """Get observability metrics for a mission."""
        cursor = self.conn.cursor()
        # Agent run stats
        cursor.execute(
            "SELECT status, COUNT(*) as cnt FROM agent_runs WHERE mission_id = ? GROUP BY status",
            (mission_id,)
        )
        agent_stats = {}
        for row in cursor.fetchall():
            agent_stats[row['status']] = row['cnt']

        # Average latency
        cursor.execute(
            "SELECT AVG(execution_time_seconds) as avg_time FROM agent_runs WHERE mission_id = ? AND status = 'COMPLETED'",
            (mission_id,)
        )
        avg_row = cursor.fetchone()
        avg_latency = avg_row['avg_time'] if avg_row and avg_row['avg_time'] else 0.0

        # Event count
        cursor.execute(
            "SELECT COUNT(*) as cnt FROM mission_events WHERE mission_id = ?",
            (mission_id,)
        )
        event_count = cursor.fetchone()['cnt']

        return {
            'mission_id': mission_id,
            'agent_stats': agent_stats,
            'active_agents': agent_stats.get('RUNNING', 0),
            'completed_agents': agent_stats.get('COMPLETED', 0),
            'failed_agents': agent_stats.get('FAILED', 0),
            'average_latency_seconds': round(avg_latency, 2),
            'total_events': event_count
        }

    # --- User Feedback & Star Rating ---

    def insert_user_feedback(self, domain: str, hypothesis_title: str, rating: int, feedback_text: str = "", user_name: str = 'Researcher') -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO user_feedback (domain, hypothesis_title, rating, feedback_text) VALUES (?, ?, ?, ?)",
                (domain, hypothesis_title, int(rating), feedback_text)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_user_feedback(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if domain:
            cursor.execute("SELECT * FROM user_feedback WHERE domain = ? ORDER BY id DESC", (domain,))
        else:
            cursor.execute("SELECT * FROM user_feedback ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    # --- Collaborative Team Discussions ---

    def insert_team_comment(self, domain: str, user_name: str, comment: str, tag: str = 'General') -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO team_discussions (domain, user_name, comment, tag) VALUES (?, ?, ?, ?)",
            (domain, user_name, comment, tag)
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_team_comments(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if domain:
            cursor.execute("SELECT * FROM team_discussions WHERE domain = ? ORDER BY id ASC", (domain,))
        else:
            cursor.execute("SELECT * FROM team_discussions ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    # ========================================================================
    # AION X 2.0 — Provenance, Lineage & Scientific OS Database Accessors
    # ========================================================================

    # --- Provenance & Lineage Graph ---
    def insert_provenance_record(self, source_entity_id: str, source_entity_type: str, target_entity_id: str, target_entity_type: str, relation: str, mission_id: str = '') -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO provenance_records (source_entity_id, source_entity_type, target_entity_id, target_entity_type, relation, mission_id) VALUES (?, ?, ?, ?, ?, ?)",
                (source_entity_id, source_entity_type, target_entity_id, target_entity_type, relation, mission_id)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_provenance_records(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if mission_id:
            cursor.execute("SELECT * FROM provenance_records WHERE mission_id = ? ORDER BY id ASC", (mission_id,))
        else:
            cursor.execute("SELECT * FROM provenance_records ORDER BY id DESC LIMIT 200")
        return [dict(r) for r in cursor.fetchall()]

    # --- Claims Lineage & Evidence Firewall ---
    def insert_claim_lineage(self, claim_id: str, text: str, claim_type: str, verification_status: str, source_ids: List[str], passage_ids: List[str], confidence: float, contradiction_ids: List[str] = None, mission_id: str = '') -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO claims_lineage (claim_id, text, claim_type, verification_status, source_ids_json, passage_ids_json, confidence, contradiction_ids_json, mission_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (claim_id, text, claim_type, verification_status, json.dumps(source_ids), json.dumps(passage_ids), confidence, json.dumps(contradiction_ids or []), mission_id)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_claims_lineage(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if mission_id:
            cursor.execute("SELECT * FROM claims_lineage WHERE mission_id = ? ORDER BY id ASC", (mission_id,))
        else:
            cursor.execute("SELECT * FROM claims_lineage ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        claims = []
        for r in rows:
            d = dict(r)
            d['source_ids'] = json.loads(d.get('source_ids_json') or '[]')
            d['passage_ids'] = json.loads(d.get('passage_ids_json') or '[]')
            d['contradiction_ids'] = json.loads(d.get('contradiction_ids_json') or '[]')
            claims.append(d)
        return claims

    # --- Death Certificates & Falsification ---
    def insert_death_certificate(self, certificate_id: str, hypothesis_id: str, final_statement: str, cause_of_failure: str, fatal_evidence: str, experiment_responsible: str = '', failed_prediction: str = '', confidence: float = 0.9, replication_status: str = 'FAILED', assumptions_violated: List[str] = None, surviving_components: List[str] = None, reusable_lessons: List[str] = None, falsification_stage: str = 'Adversarial Simulation') -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO death_certificates (certificate_id, hypothesis_id, final_statement, cause_of_failure, fatal_evidence, experiment_responsible, failed_prediction, confidence, replication_status, assumptions_violated_json, surviving_components_json, reusable_lessons_json, falsification_stage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (certificate_id, hypothesis_id, final_statement, cause_of_failure, fatal_evidence, experiment_responsible, failed_prediction, confidence, replication_status, json.dumps(assumptions_violated or []), json.dumps(surviving_components or []), json.dumps(reusable_lessons or []), falsification_stage)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_death_certificates(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM death_certificates ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        certs = []
        for r in rows:
            d = dict(r)
            d['assumptions_violated'] = json.loads(d.get('assumptions_violated_json') or '[]')
            d['surviving_components'] = json.loads(d.get('surviving_components_json') or '[]')
            d['reusable_lessons'] = json.loads(d.get('reusable_lessons_json') or '[]')
            certs.append(d)
        return certs

    # --- Scientific Failure Vault ---
    def insert_failed_experiment(self, failure_id: str, hypothesis_id: str, experiment_id: str, failure_type: str, parameters: Dict[str, Any] = None, environment: str = 'Sandbox AST v2.0', observations: str = '', diagnosis: str = '', confidence: float = 0.9, learned_constraint: str = '', future_recommendation: str = '') -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO failure_vault (failure_id, hypothesis_id, experiment_id, failure_type, parameters_json, environment, observations, diagnosis, confidence, learned_constraint, future_recommendation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (failure_id, hypothesis_id, experiment_id, failure_type, json.dumps(parameters or {}), environment, observations, diagnosis, confidence, learned_constraint, future_recommendation)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_failed_experiments(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM failure_vault ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        vault = []
        for r in rows:
            d = dict(r)
            d['parameters'] = json.loads(d.get('parameters_json') or '{}')
            vault.append(d)
        return vault

    def search_failure_vault(self, query: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        q = f"%{query}%"
        cursor.execute("SELECT * FROM failure_vault WHERE observations LIKE ? OR diagnosis LIKE ? OR learned_constraint LIKE ? ORDER BY id DESC LIMIT 10", (q, q, q))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    # --- Replication Engine ---
    def insert_replication_attempt(self, replication_id: str, paper_id: str, experiment_id: str, reported_result: str, reproduced_result: str, absolute_difference: float, relative_difference: float, uncertainty: float, parameter_match: float, dataset_match: float, method_match: float, execution_status: str, replication_status: str, failure_reason: str, multi_run_scores: List[float] = None, reproducibility_score: float = 90.0) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO replication_attempts (replication_id, paper_id, experiment_id, reported_result, reproduced_result, absolute_difference, relative_difference, uncertainty, parameter_match, dataset_match, method_match, execution_status, replication_status, failure_reason, multi_run_scores_json, reproducibility_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (replication_id, paper_id, experiment_id, reported_result, reproduced_result, absolute_difference, relative_difference, uncertainty, parameter_match, dataset_match, method_match, execution_status, replication_status, failure_reason, json.dumps(multi_run_scores or []), reproducibility_score)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_replication_attempts(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM replication_attempts ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        reps = []
        for r in rows:
            d = dict(r)
            d['multi_run_scores'] = json.loads(d.get('multi_run_scores_json') or '[]')
            reps.append(d)
        return reps

    # --- Counterfactual Lab ---
    def insert_counterfactual_experiment(self, counterfactual_id: str, hypothesis_id: str, varied_dimension: str, baseline_value: str, perturbed_value: str, robustness_score: float, is_fragile: bool, failure_point_identified: str = '', observations: str = '') -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO counterfactual_experiments (counterfactual_id, hypothesis_id, varied_dimension, baseline_value, perturbed_value, robustness_score, is_fragile, failure_point_identified, observations) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (counterfactual_id, hypothesis_id, varied_dimension, baseline_value, perturbed_value, robustness_score, 1 if is_fragile else 0, failure_point_identified, observations)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_counterfactual_experiments(self, hypothesis_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if hypothesis_id:
            cursor.execute("SELECT * FROM counterfactual_experiments WHERE hypothesis_id = ? ORDER BY id ASC", (hypothesis_id,))
        else:
            cursor.execute("SELECT * FROM counterfactual_experiments ORDER BY id DESC LIMIT 50")
        return [dict(r) for r in cursor.fetchall()]

    # --- Persistent Research Tree ---
    def insert_research_tree_node(self, node_id: str, parent_id: Optional[str], node_type: str, title: str, status: str = 'ACTIVE', confidence: float = 0.8, mission_id: str = '', data: Dict[str, Any] = None, children_ids: List[str] = None) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO research_tree_nodes (node_id, parent_id, node_type, title, status, confidence, mission_id, data_json, children_ids_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (node_id, parent_id, node_type, title, status, confidence, mission_id, json.dumps(data or {}), json.dumps(children_ids or []))
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_research_tree_nodes(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if mission_id:
            cursor.execute("SELECT * FROM research_tree_nodes WHERE mission_id = ? ORDER BY id ASC", (mission_id,))
        else:
            cursor.execute("SELECT * FROM research_tree_nodes ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        nodes = []
        for r in rows:
            d = dict(r)
            d['data'] = json.loads(d.get('data_json') or '{}')
            d['children_ids'] = json.loads(d.get('children_ids_json') or '[]')
            nodes.append(d)
        return nodes

    # --- Adversarial Tournament Records ---
    def insert_tournament_argument(self, argument_id: str, tournament_id: str, round_number: int, round_name: str, speaker_role: str, claim_text: str, attack_text: str, defense_text: str, attack_strength: float, defense_strength: float, unresolved_objection: str = '', evidence_refs: List[str] = None) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO tournament_arguments (argument_id, tournament_id, round_number, round_name, speaker_role, claim_text, attack_text, defense_text, attack_strength, defense_strength, unresolved_objection, evidence_refs_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (argument_id, tournament_id, round_number, round_name, speaker_role, claim_text, attack_text, defense_text, attack_strength, defense_strength, unresolved_objection, json.dumps(evidence_refs or []))
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_tournament_arguments(self, tournament_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tournament_arguments WHERE tournament_id = ? ORDER BY round_number ASC, id ASC", (tournament_id,))
        rows = cursor.fetchall()
        args = []
        for r in rows:
            d = dict(r)
            d['evidence_refs'] = json.loads(d.get('evidence_refs_json') or '[]')
            args.append(d)
        return args

    # --- Kill Chain Reports ---
    def insert_kill_chain_report(self, report_dict: Dict[str, Any]) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO kill_chain_reports (hypothesis_id, initial_score, literature_attack_score, contradiction_score, assumption_score, simulation_score, replication_score, statistical_score, final_survival_score, strongest_support, strongest_contradiction, critical_assumptions_json, failure_modes_json, recommended_next_action, disclaimer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    report_dict.get('hypothesis_id', ''),
                    report_dict.get('initial_score', 75.0),
                    report_dict.get('literature_attack_score', 70.0),
                    report_dict.get('contradiction_score', 65.0),
                    report_dict.get('assumption_score', 68.0),
                    report_dict.get('simulation_score', 80.0),
                    report_dict.get('replication_score', 78.0),
                    report_dict.get('statistical_score', 82.0),
                    report_dict.get('final_survival_score', 73.0),
                    report_dict.get('strongest_support', ''),
                    report_dict.get('strongest_contradiction', ''),
                    json.dumps(report_dict.get('critical_assumptions', [])),
                    json.dumps(report_dict.get('failure_modes', [])),
                    report_dict.get('recommended_next_action', ''),
                    report_dict.get('disclaimer', 'Empirical resilience score represents survival against simulated falsification; it does not constitute mathematical or physical proof.')
                )
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_kill_chain_report(self, hypothesis_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM kill_chain_reports WHERE hypothesis_id = ? ORDER BY id DESC LIMIT 1", (hypothesis_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['critical_assumptions'] = json.loads(d.get('critical_assumptions_json') or '[]')
                d['failure_modes'] = json.loads(d.get('failure_modes_json') or '[]')
                return d
            return None

    # --- Red Team Reports ---
    def insert_red_team_report(self, mission_id: str, literature_integrity: float, evidence_integrity: float, causal_validity: float, statistical_validity: float, reproducibility_rating: float, novelty_rating: float, overall_research_risk: str, findings: List[str], cascade_warnings: List[str]) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO red_team_reports (mission_id, literature_integrity, evidence_integrity, causal_validity, statistical_validity, reproducibility_rating, novelty_rating, overall_research_risk, findings_json, cascade_warnings_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (mission_id, literature_integrity, evidence_integrity, causal_validity, statistical_validity, reproducibility_rating, novelty_rating, overall_research_risk, json.dumps(findings), json.dumps(cascade_warnings))
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_red_team_reports(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            cursor = self.conn.cursor()
            if mission_id:
                cursor.execute("SELECT * FROM red_team_reports WHERE mission_id = ? ORDER BY id DESC", (mission_id,))
            else:
                cursor.execute("SELECT * FROM red_team_reports ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            reports = []
            for r in rows:
                d = dict(r)
                d['findings'] = json.loads(d.get('findings_json') or '[]')
                d['cascade_warnings'] = json.loads(d.get('cascade_warnings_json') or '[]')
                reports.append(d)
            return reports

    # --- Active Research Recommendations ---
    def insert_active_research_action(self, action_id: str, mission_id: str, action_type: str, target_hypothesis_id: str, title: str, expected_information_gain: float, estimated_cost_usd: Optional[float], estimated_duration_hours: Optional[float], risk_level: str, feasibility_score: float, hypothesis_discrimination_power: float, recommended_rank: int, reasoning: str) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO active_research_actions (action_id, mission_id, action_type, target_hypothesis_id, title, expected_information_gain, estimated_cost_usd, estimated_duration_hours, risk_level, feasibility_score, hypothesis_discrimination_power, recommended_rank, reasoning) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (action_id, mission_id, action_type, target_hypothesis_id, title, expected_information_gain, estimated_cost_usd, estimated_duration_hours, risk_level, feasibility_score, hypothesis_discrimination_power, recommended_rank, reasoning)
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_active_research_actions(self, mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            cursor = self.conn.cursor()
            if mission_id:
                cursor.execute("SELECT * FROM active_research_actions WHERE mission_id = ? ORDER BY recommended_rank ASC", (mission_id,))
            else:
                cursor.execute("SELECT * FROM active_research_actions ORDER BY id DESC LIMIT 20")
            return [dict(r) for r in cursor.fetchall()]

    # --- Benchmark Mode ---
    def insert_benchmark_run(self, run_id: str, task_name: str, mode: str, discovery_rate: float, evidence_accuracy: float, citation_accuracy: float, contradiction_recall: float, latency_seconds: float, compute_cost_usd: float, metrics: Dict[str, Any]) -> int:
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO benchmark_runs (run_id, task_name, mode, discovery_rate, evidence_accuracy, citation_accuracy, contradiction_recall, latency_seconds, compute_cost_usd, metrics_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, task_name, mode, discovery_rate, evidence_accuracy, citation_accuracy, contradiction_recall, latency_seconds, compute_cost_usd, json.dumps(metrics))
            )
            self._safe_commit()
            return cursor.lastrowid

    def get_benchmark_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM benchmark_runs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        runs = []
        for r in rows:
            d = dict(r)
            d['metrics'] = json.loads(d.get('metrics_json') or '{}')
            runs.append(d)
        return runs

    # --- Telemetry & Observability ---
    def insert_telemetry_log(self, mission_id: str, trace_id: str, agent_role: str, model_name: str = 'fast-router', prompt_tokens: int = 0, completion_tokens: int = 0, latency_seconds: float = 0.0, cost_usd: float = 0.0, status: str = 'SUCCESS') -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO telemetry_logs (mission_id, trace_id, agent_role, model_name, prompt_tokens, completion_tokens, latency_seconds, cost_usd, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (mission_id, trace_id, agent_role, model_name, prompt_tokens, completion_tokens, latency_seconds, cost_usd, status)
        )
        self._safe_commit()
        return cursor.lastrowid

    def get_telemetry_logs(self, mission_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if mission_id:
            cursor.execute("SELECT * FROM telemetry_logs WHERE mission_id = ? ORDER BY id ASC", (mission_id,))
        else:
            cursor.execute("SELECT * FROM telemetry_logs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]



