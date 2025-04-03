"""
Storage systems for Tekton metrics.

This module provides storage mechanisms for metrics data
collected during system operation.
"""

import os
import json
import time
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricsStorage:
    """Base class for metrics storage."""
    
    def store_session(self, session_data):
        """Store a session's metrics data."""
        raise NotImplementedError("Subclasses must implement store_session")
    
    def get_session(self, session_id):
        """Retrieve a session by ID."""
        raise NotImplementedError("Subclasses must implement get_session")
    
    def get_sessions(self, filters=None, limit=100, offset=0):
        """Retrieve multiple sessions with optional filtering."""
        raise NotImplementedError("Subclasses must implement get_sessions")


class SQLiteMetricsStorage(MetricsStorage):
    """Stores metrics in a SQLite database."""
    
    def __init__(self, db_path="metrics.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create main tables
        tables = {
            "sessions": '''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    prompt TEXT,
                    config TEXT,
                    start_time REAL,
                    end_time REAL,
                    response TEXT,
                    performance TEXT,
                    spectral_metrics TEXT,
                    created_at REAL
                )
            ''',
            "component_activations": '''
                CREATE TABLE IF NOT EXISTS component_activations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    component_id TEXT,
                    activation_data TEXT,
                    timestamp REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            ''',
            "propagation_steps": '''
                CREATE TABLE IF NOT EXISTS propagation_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    source TEXT,
                    destination TEXT,
                    info_content REAL,
                    data TEXT,
                    timestamp REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            ''',
            "parameter_usage": '''
                CREATE TABLE IF NOT EXISTS parameter_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    component_id TEXT,
                    total_params INTEGER,
                    active_params INTEGER,
                    utilization REAL,
                    layer_data TEXT,
                    timestamp REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            '''
        }
        
        # Create tables
        for _, create_sql in tables.items():
            cursor.execute(create_sql)
        
        # Create indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)',
            'CREATE INDEX IF NOT EXISTS idx_component_activations_session ON component_activations(session_id)',
            'CREATE INDEX IF NOT EXISTS idx_propagation_steps_session ON propagation_steps(session_id)',
            'CREATE INDEX IF NOT EXISTS idx_parameter_usage_session ON parameter_usage(session_id)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
    
    def store_session(self, session_data):
        """Store a session's metrics data."""
        # Convert to dict if it's a SessionData object
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Store main session data
            cursor.execute(
                'INSERT INTO sessions (id, prompt, config, start_time, end_time, '
                'response, performance, spectral_metrics, created_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    data['id'],
                    data['prompt'],
                    json.dumps(data['config']),
                    data['start_time'],
                    data.get('end_time'),
                    data.get('response'),
                    json.dumps(data.get('performance', {})),
                    json.dumps(data.get('spectral_metrics', {})),
                    time.time()
                )
            )
            
            # Store component activations
            for component_id, activations in data.get('component_activations', {}).items():
                for activation in activations:
                    cursor.execute(
                        'INSERT INTO component_activations (session_id, component_id, '
                        'activation_data, timestamp) VALUES (?, ?, ?, ?)',
                        (
                            data['id'],
                            component_id,
                            json.dumps(activation),
                            activation.get('timestamp', 0)
                        )
                    )
            
            # Store propagation steps
            for step in data.get('propagation_path', []):
                cursor.execute(
                    'INSERT INTO propagation_steps (session_id, source, destination, '
                    'info_content, data, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        data['id'],
                        step['source'],
                        step['destination'],
                        step.get('info_content', 0),
                        json.dumps({k: v for k, v in step.items() 
                                 if k not in ['source', 'destination', 'info_content', 'timestamp']}),
                        step.get('timestamp', 0)
                    )
                )
            
            # Store parameter usage
            for component_id, usage in data.get('parameter_usage', {}).items():
                cursor.execute(
                    'INSERT INTO parameter_usage (session_id, component_id, total_params, '
                    'active_params, utilization, layer_data, timestamp) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (
                        data['id'],
                        component_id,
                        usage.get('total', 0),
                        usage.get('active', 0),
                        usage.get('utilization', 0),
                        json.dumps(usage.get('layers', {})),
                        usage.get('timestamp', 0)
                    )
                )
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing session data: {str(e)}")
            raise
        finally:
            conn.close()
    
    def get_session(self, session_id):
        """Retrieve a session by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get main session data
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
                
            session_data = dict(session_row)
            
            # Parse JSON fields
            for field in ['config', 'performance', 'spectral_metrics']:
                session_data[field] = json.loads(session_data[field])
            
            # Get component activations
            cursor.execute(
                'SELECT component_id, activation_data, timestamp FROM component_activations '
                'WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            activations = {}
            for row in cursor.fetchall():
                component_id = row['component_id']
                if component_id not in activations:
                    activations[component_id] = []
                
                activation_data = json.loads(row['activation_data'])
                activation_data['timestamp'] = row['timestamp']
                activations[component_id].append(activation_data)
            
            session_data['component_activations'] = activations
            
            # Get propagation steps
            cursor.execute(
                'SELECT source, destination, info_content, data, timestamp FROM propagation_steps '
                'WHERE session_id = ? ORDER BY timestamp', (session_id,)
            )
            
            propagation_path = []
            for row in cursor.fetchall():
                step = {
                    'source': row['source'],
                    'destination': row['destination'],
                    'info_content': row['info_content'],
                    'timestamp': row['timestamp']
                }
                
                # Add additional data if present
                step.update(json.loads(row['data']))
                propagation_path.append(step)
            
            session_data['propagation_path'] = propagation_path
            
            # Get parameter usage
            cursor.execute(
                'SELECT component_id, total_params, active_params, utilization, layer_data, timestamp '
                'FROM parameter_usage WHERE session_id = ?', (session_id,)
            )
            
            parameter_usage = {}
            for row in cursor.fetchall():
                parameter_usage[row['component_id']] = {
                    'total': row['total_params'],
                    'active': row['active_params'],
                    'utilization': row['utilization'],
                    'timestamp': row['timestamp'],
                    'layers': json.loads(row['layer_data'])
                }
            
            session_data['parameter_usage'] = parameter_usage
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error retrieving session data: {str(e)}")
            raise
        finally:
            conn.close()
    
    def get_sessions(self, filters=None, limit=100, offset=0):
        """Retrieve multiple sessions with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Build query based on filters
            query = "SELECT id FROM sessions"
            params = []
            
            if filters:
                conditions = []
                
                if 'start_time_min' in filters:
                    conditions.append("start_time >= ?")
                    params.append(filters['start_time_min'])
                
                if 'start_time_max' in filters:
                    conditions.append("start_time <= ?")
                    params.append(filters['start_time_max'])
                
                if 'prompt_like' in filters:
                    conditions.append("prompt LIKE ?")
                    params.append(f"%{filters['prompt_like']}%")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            session_ids = [row['id'] for row in cursor.fetchall()]
            
            # Get full data for each session
            sessions = []
            for session_id in session_ids:
                session_data = self.get_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving sessions: {str(e)}")
            raise
        finally:
            conn.close()
            
    def get_spectral_metrics(self, filters=None, limit=100):
        """Get spectral metrics for multiple sessions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Build query based on filters
            query = "SELECT id, start_time, spectral_metrics FROM sessions"
            params = []
            
            if filters:
                conditions = []
                for field, value in filters.items():
                    if field == 'start_time_min':
                        conditions.append("start_time >= ?")
                        params.append(value)
                    elif field == 'start_time_max':
                        conditions.append("start_time <= ?")
                        params.append(value)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY start_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [
                {
                    'id': row['id'],
                    'start_time': row['start_time'],
                    'metrics': json.loads(row['spectral_metrics'])
                }
                for row in cursor.fetchall()
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving spectral metrics: {str(e)}")
            raise
        finally:
            conn.close()


class JSONFileMetricsStorage(MetricsStorage):
    """Stores metrics in JSON files."""
    
    def __init__(self, directory="metrics"):
        """Initialize JSON file storage."""
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        
        # Create index file if it doesn't exist
        self.index_path = os.path.join(directory, "index.json")
        if not os.path.exists(self.index_path):
            with open(self.index_path, 'w') as f:
                json.dump({"sessions": {}}, f)
    
    def store_session(self, session_data):
        """Store a session's metrics data."""
        # Convert to dict if it's a SessionData object
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
            
        # Create session directory and write data
        session_id = data['id']
        session_dir = os.path.join(self.directory, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        with open(os.path.join(session_dir, "session.json"), 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update index
        try:
            with open(self.index_path, 'r') as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            index = {"sessions": {}}
        
        # Add to index with prompt truncation
        index["sessions"][session_id] = {
            "prompt": data['prompt'][:100] + "..." if len(data['prompt']) > 100 else data['prompt'],
            "start_time": data['start_time'],
            "end_time": data.get('end_time'),
            "file": f"{session_id}/session.json"
        }
        
        with open(self.index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_session(self, session_id):
        """Retrieve a session by ID."""
        session_file = os.path.join(self.directory, session_id, "session.json")
        
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None
    
    def get_sessions(self, filters=None, limit=100, offset=0):
        """Retrieve multiple sessions with optional filtering."""
        try:
            with open(self.index_path, 'r') as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
        # Get all sessions from index with ID added
        all_sessions = [
            {**session_info, "id": session_id}
            for session_id, session_info in index.get("sessions", {}).items()
        ]
        
        # Sort by start time (descending)
        all_sessions.sort(key=lambda x: x.get("start_time", 0), reverse=True)
        
        # Apply filters
        if filters:
            filtered_sessions = []
            for session in all_sessions:
                include = True
                
                if 'start_time_min' in filters and session.get('start_time', 0) < filters['start_time_min']:
                    include = False
                
                if 'start_time_max' in filters and session.get('start_time', 0) > filters['start_time_max']:
                    include = False
                
                if 'prompt_like' in filters and filters['prompt_like'] not in session.get('prompt', ''):
                    include = False
                
                if include:
                    filtered_sessions.append(session)
            
            all_sessions = filtered_sessions
        
        # Apply pagination and load full data
        return [
            self.get_session(session_info["id"])
            for session_info in all_sessions[offset:offset + limit]
            if self.get_session(session_info["id"])
        ]