"""
Research Memory Module.
Stores and retrieves previous missions, rejected/successful hypotheses, failed experiments, research gaps, and lessons learned.
Prevents repeatedly exploring known dead ends.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ResearchRecord:
    """Represents a discrete memory unit in research history."""
    id: str
    domain: str
    type: str # e.g., "mission", "hypothesis", "experiment", "lesson"
    status: str # e.g., "success", "failed", "rejected", "completed"
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

class ResearchMemory:
    """
    Manages long-term research memory to inform future investigations 
    and avoid repeating mistakes.
    """
    def __init__(self, db_manager):
        """
        Initialize the ResearchMemory.
        
        Args:
            db_manager: DBManager instance for SQLite operations.
        """
        self.db = db_manager
        self._init_tables()

    def _init_tables(self):
        """Initialize SQLite tables for research memory."""
        query = '''
            CREATE TABLE IF NOT EXISTS research_memory (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT
            )
        '''
        try:
            self.db.execute_update(query)
        except Exception as e:
            logger.error(f"Failed to initialize research memory table: {e}")

    def add_record(self, record: ResearchRecord):
        """Add a new research record to memory."""
        query = '''
            INSERT INTO research_memory (id, domain, type, status, description, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        meta_json = json.dumps(record.metadata)
        try:
            self.db.execute_update(
                query, 
                (record.id, record.domain, record.type, record.status, record.description, meta_json, record.created_at.isoformat())
            )
            logger.info(f"Added research record {record.id} of type {record.type}.")
        except Exception as e:
            logger.error(f"Failed to add research record: {e}")

    def get_records_by_type(self, record_type: str, domain: Optional[str] = None) -> List[ResearchRecord]:
        """Retrieve records of a specific type."""
        query = "SELECT * FROM research_memory WHERE type = ?"
        params = [record_type]
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        try:
            rows = self.db.execute_query(query, tuple(params))
            return self._parse_rows(rows)
        except Exception as e:
            logger.error(f"Failed to fetch records by type: {e}")
            return []

    def search_prior_research(self, query: str, domain: str) -> List[Dict[str, Any]]:
        """
        Search prior research to check if similar investigations were conducted.
        Warns the user if trying to explore known dead ends.
        
        Args:
            query: The search term or concept to look for.
            domain: The research domain to restrict the search to.
            
        Returns:
            List of matching records as dictionaries.
        """
        # A simple keyword search on description and metadata.
        # For a full implementation, this should use vector embeddings/semantic search via llm_engine.
        sql_query = '''
            SELECT * FROM research_memory 
            WHERE domain = ? AND (description LIKE ? OR metadata LIKE ?)
        '''
        search_term = f"%{query}%"
        try:
            rows = self.db.execute_query(sql_query, (domain, search_term, search_term))
            records = self._parse_rows(rows)
            
            results = []
            for record in records:
                # Add warnings for failed/rejected paths
                warning = False
                if record.status in ["failed", "rejected"]:
                    warning = True
                
                results.append({
                    "record_id": record.id,
                    "type": record.type,
                    "status": record.status,
                    "description": record.description,
                    "is_warning": warning,
                    "message": f"WARNING: Similar past {record.type} was {record.status}." if warning else f"Found prior {record.status} {record.type}."
                })
            return results
        except Exception as e:
            logger.error(f"Failed to search prior research: {e}")
            return []

    def _parse_rows(self, rows) -> List[ResearchRecord]:
        """Helper to parse database rows into ResearchRecord objects."""
        records = []
        if not rows:
            return records
        for row in rows:
            meta = json.loads(row['metadata']) if row['metadata'] else {}
            created = datetime.fromisoformat(row['created_at'])
            records.append(ResearchRecord(
                id=row['id'],
                domain=row['domain'],
                type=row['type'],
                status=row['status'],
                description=row['description'],
                metadata=meta,
                created_at=created
            ))
        return records
