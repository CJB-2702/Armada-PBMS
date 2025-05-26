import json
import sqlite3
import os
from datetime import datetime
import logging
from pathlib import Path

class TestLogger:
    def __init__(self):
        # Setup file logging
        self.log_dir = Path("./instance/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self._get_new_log_file()
        
        # Setup SQLite database
        self.db_path = "./instance/test_logs.db"
        self._setup_database()
        
        # Initialize log counter
        self.log_count = 0

    def _get_new_log_file(self):
        """Create a new log file with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.log_dir / f"system_log_{timestamp}.json"

    def _setup_database(self):
        """Initialize SQLite database with log table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                log_level TEXT,
                message TEXT,
                context TEXT,
                source TEXT,
                stack_trace TEXT,
                user_row_id INTEGER,
                asset_row_id INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

    def _write_to_file(self, log_entry):
        """Write log entry to JSON file"""
        try:
            # Check if current file exists and is under 1KB
            if self.current_log_file.exists() and self.current_log_file.stat().st_size >= 1024:
                self.current_log_file = self._get_new_log_file()
            
            # Write log entry
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def _write_to_db(self, log_entry):
        """Write log entry to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs (
                    log_level, message, context, source, 
                    stack_trace, user_row_id, asset_row_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_entry['level'],
                log_entry['message'],
                json.dumps(log_entry['context']),
                log_entry['source'],
                log_entry.get('stack_trace'),
                log_entry.get('user_id'),
                log_entry.get('asset_id')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error writing to database: {e}")

    def log(self, level, message, source, context=None, user_id=None, asset_id=None, stack_trace=None):
        """Log an event to both file and database"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'context': context or {},
            'source': source,
            'user_id': user_id,
            'asset_id': asset_id,
            'stack_trace': stack_trace
        }
        
        self._write_to_file(log_entry)
        self._write_to_db(log_entry)
        self.log_count += 1

def main():
    # Create logger instance
    logger = TestLogger()
    
    # Test different log levels and scenarios
    logger.log(
        level="INFO",
        message="System initialization started",
        source="SystemInit",
        context={"version": "1.0.0"}
    )
    
    logger.log(
        level="WARNING",
        message="Missing configuration file",
        source="ConfigManager",
        context={"file": "config.json"},
        user_id=1
    )
    
    logger.log(
        level="ERROR",
        message="Failed to connect to database",
        source="DatabaseManager",
        context={"db_name": "main.db"},
        stack_trace="Traceback (most recent call last)..."
    )
    
    logger.log(
        level="DEBUG",
        message="Processing asset update",
        source="AssetManager",
        context={"asset_id": 123, "changes": ["status", "location"]},
        user_id=2,
        asset_id=123
    )
    
    logger.log(
        level="INFO",
        message="User login successful",
        source="AuthManager",
        context={"ip": "192.168.1.1"},
        user_id=1
    )
    
    print(f"Generated {logger.log_count} test logs")
    print(f"Log files stored in: {logger.log_dir}")
    print(f"Database stored at: {logger.db_path}")

if __name__ == "__main__":
    main() 