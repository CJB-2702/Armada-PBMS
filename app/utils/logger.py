import logging
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.extensions import db




class LogEntry(db.Model):
    __tablename__ = 'log_entry'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    module = db.Column(db.String(100))
    function = db.Column(db.String(100))
    line = db.Column(db.Integer)
    log_data = db.Column(db.Text)  # JSON string of additional data
    
    def __repr__(self):
        return f'<LogEntry {self.level} {self.timestamp}>'

class DatabaseHandler(logging.Handler):
    """Custom logging handler that writes to the database"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
    
    def emit(self, record):
        try:
            # Check if log_entry table exists
            try:
                log = LogEntry(
                    level=record.levelname,
                    message=record.getMessage(),
                    timestamp=datetime.utcnow(),
                    module=record.module,
                    function=record.funcName,
                    line=record.lineno,
                    log_data=json.dumps(record.__dict__) if hasattr(record, '__dict__') else None
                )
                self.db.session.add(log)
                self.db.session.commit()
            except Exception as e:
                # If table doesn't exist yet, just print to console
                print(f"[{record.levelname}] {record.getMessage()}")
                if hasattr(record, '__dict__'):
                    print(f"Extra data: {record.__dict__}")
        except Exception as e:
            self.handleError(record)

class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON"""
    
    def format(self, record):
        # Create base log record
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add log data if present
        if hasattr(record, 'log_data'):
            log_record['log_data'] = record.log_data
            
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

class LoggerFactory:
    """Factory class for creating and managing loggers"""
    
    _instance = None
    _loggers = {}
    _debug_override = True
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._loggers:
            self._loggers['std'] = self._setup_logger()
    
    def _check_db_connection(self):
        """Check if there is an active database connection
        
        Returns:
            bool: True if there is an active connection, False otherwise
        """
        if self._db is None:
            return False
            
        try:
            # Try to execute a simple query to check connection
            self._db.session.execute('SELECT 1')
            return True
        except Exception:
            return False
    
    def _setup_file_handler(self, logger, name, debug):
        """Setup file handler for logger
        
        Args:
            logger: Logger instance to add handler to
            name: Name of the logger
            debug: Whether debug logging is enabled
        """
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation (1KB max size)
        file_handler = RotatingFileHandler(
            log_dir / f'{name}.log',
            maxBytes=1024,  # 1KB
            backupCount=5
        )
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    
    def _setup_console_handler(self, logger, debug):
        """Setup console handler for logger
        
        Args:
            logger: Logger instance to add handler to
            debug: Whether debug logging is enabled
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
    
    def _setup_database_handler(self, logger, name, debug):
        """Setup database handler for logger
        
        Args:
            logger: Logger instance to add handler to
            name: Name of the logger
            debug: Whether debug logging is enabled
        """
        if self._check_db_connection():
            db_handler = DatabaseHandler(self._db)
            db_handler.setLevel(logging.DEBUG if debug else logging.INFO)
            logger.addHandler(db_handler)
            logger.debug(f"Database handler added to logger '{name}'")
        else:
            logger.debug(f"No active database connection for logger '{name}'")
    
    def _setup_logger(self, name='armada_pbms', debug=False):
        """Set up and configure the logger
        
        Args:
            name (str): Name of the logger
            debug (bool): Whether to enable debug logging
        """
        # Override debug if _debug_override is True
        if self._debug_override:
            debug = True
            
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Setup handlers
        self._setup_file_handler(logger, name, debug)
        self._setup_console_handler(logger, debug)
        self._setup_database_handler(logger, name, debug)
        
        return logger
    
    def connect_loggers_to_database(self, db):
        """Connect all active loggers to a database instance
        
        Args:
            db: SQLAlchemy database instance to connect to
        """
        self._db = db
        
        # Create the log table if it doesn't exist
        with db.engine.connect() as conn:
            if not db.engine.dialect.has_table(conn, LogEntry.__tablename__):
                LogEntry.__table__.create(db.engine)
        
        # Add database handler to all existing loggers
        for logger_name, logger in self._loggers.items():
            # Remove any existing database handlers
            for handler in logger.handlers[:]:
                if isinstance(handler, DatabaseHandler):
                    logger.removeHandler(handler)
            
            # Add new database handler
            self._setup_database_handler(logger, logger_name, self._debug_override)
    
    def get_logger(self, name='std', debug=False):
        """Get a logger instance by name
        
        Args:
            name (str): Name of the logger to get
            debug (bool): Whether to enable debug logging for new loggers
        """
        if name not in self._loggers:
            self._loggers[name] = self._setup_logger(name, debug)
        return self._loggers[name]

def init_logger(app):
    """Initialize the logger with the Flask application"""
    # Use the existing db instance from app.extensions
    from app.extensions import db
    logger_factory.connect_loggers_to_database(db)

# Create a singleton instance
logger_factory = LoggerFactory()

# Convenience function for getting loggers
def get_logger(name='std', debug=False):
    return logger_factory.get_logger(name, debug)
