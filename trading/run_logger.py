"""
Run logging system for tracking scanner executions
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger('trading.run_logger')

class RunLogger:
    """Handles logging of scanner runs to SQLite database"""
    
    def __init__(self, db_path: str = "trading/data/run_logs.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the run logs database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                candidates_count INTEGER DEFAULT 0,
                symbols_scanned INTEGER DEFAULT 0,
                duration_seconds REAL DEFAULT 0,
                output_files TEXT,
                error_message TEXT,
                parameters TEXT,
                run_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_run(self, 
                status: str, 
                run_id: str = None,
                candidates_count: int = 0, 
                symbols_scanned: int = 0,
                duration_seconds: float = 0, 
                output_files: List[str] = None, 
                error_message: str = None, 
                parameters: Dict = None) -> int:
        """Log a scanner run to the database
        
        Args:
            status: SUCCESS, FAILED, or ERROR
            run_id: Unique run identifier
            candidates_count: Number of candidates found
            symbols_scanned: Number of symbols processed
            duration_seconds: Execution time
            output_files: List of generated files
            error_message: Error details if any
            parameters: Run parameters
            
        Returns:
            Log entry ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO run_logs 
            (timestamp, status, run_id, candidates_count, symbols_scanned, 
             duration_seconds, output_files, error_message, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            status,
            run_id,
            candidates_count,
            symbols_scanned,
            duration_seconds,
            json.dumps(output_files or []),
            error_message,
            json.dumps(parameters or {})
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Logged {status} run {run_id}: {candidates_count} candidates, {duration_seconds:.2f}s")
        return log_id
    
    def get_recent_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent run logs
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of run log dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, status, run_id, candidates_count, 
                   symbols_scanned, duration_seconds, output_files, 
                   error_message, parameters
            FROM run_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        runs = []
        for row in rows:
            run_dict = dict(zip(columns, row))
            
            # Parse JSON fields
            try:
                run_dict['output_files'] = json.loads(run_dict['output_files'] or '[]')
            except:
                run_dict['output_files'] = []
                
            try:
                run_dict['parameters'] = json.loads(run_dict['parameters'] or '{}')
            except:
                run_dict['parameters'] = {}
                
            runs.append(run_dict)
        
        return runs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get run statistics
        
        Returns:
            Dictionary with run statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total runs
        cursor.execute("SELECT COUNT(*) FROM run_logs")
        total_runs = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("SELECT COUNT(*) FROM run_logs WHERE status = 'SUCCESS'")
        successful_runs = cursor.fetchone()[0]
        
        # Average duration
        cursor.execute("SELECT AVG(duration_seconds) FROM run_logs WHERE status = 'SUCCESS'")
        avg_duration = cursor.fetchone()[0] or 0
        
        # Total candidates found
        cursor.execute("SELECT SUM(candidates_count) FROM run_logs WHERE status = 'SUCCESS'")
        total_candidates = cursor.fetchone()[0] or 0
        
        # Recent activity (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM run_logs 
            WHERE datetime(timestamp) > datetime('now', '-1 day')
        ''')
        recent_runs = cursor.fetchone()[0]
        
        conn.close()
        
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        return {
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'success_rate': success_rate,
            'avg_duration_seconds': avg_duration,
            'total_candidates_found': total_candidates,
            'recent_runs_24h': recent_runs
        }

# Global instance
run_logger = RunLogger()