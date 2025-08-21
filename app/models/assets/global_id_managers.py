#!/usr/bin/env python3
"""
Global ID Manager for Asset Detail Tables
Manages shared row ID generation across all asset detail tables
"""

from app import db
from sqlalchemy import text
from contextlib import contextmanager
import threading

class AssetDetailIDManager:
    """
    Manages all_asset_detail_id sequence for AssetDetailVirtual tables
    Ensures unique IDs across all asset detail tables
    """
    
    _lock = threading.Lock()
    
    @classmethod
    def get_next_asset_detail_id(cls):
        """
        Get the next available asset detail ID
        Uses database counter table for thread safety
        """
        with cls._lock:
            # Update counter and get new value atomically
            db.session.execute(text("UPDATE asset_detail_id_counter SET current_value = current_value + 1"))
            result = db.session.execute(text("SELECT current_value FROM asset_detail_id_counter"))
            return result.scalar()
    
    @classmethod
    def create_sequence_if_not_exists(cls):
        """
        Create the asset detail sequence if it doesn't exist
        For SQLite, we'll use a simple counter table approach
        """
        try:
            # For SQLite, create a simple counter table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS asset_detail_id_counter (
                    id INTEGER PRIMARY KEY,
                    current_value INTEGER DEFAULT 0
                )
            """))
            
            # Initialize the counter if it doesn't exist
            result = db.session.execute(text("SELECT COUNT(*) FROM asset_detail_id_counter"))
            if result.scalar() == 0:
                db.session.execute(text("INSERT INTO asset_detail_id_counter (current_value) VALUES (0)"))
            
            db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def reset_sequence(cls, start_value=1):
        """
        Reset the asset detail sequence to a specific value
        Useful for testing or data migration
        """
        with cls._lock:
            db.session.execute(text(f"UPDATE asset_detail_id_counter SET current_value = {start_value - 1}"))
            db.session.commit()
    
    @classmethod
    def get_current_sequence_value(cls):
        """
        Get the current value of the asset detail sequence
        """
        result = db.session.execute(text("SELECT current_value FROM asset_detail_id_counter"))
        return result.scalar()
    
    @classmethod
    def get_sequence_info(cls):
        """
        Get information about the asset detail sequence
        """
        result = db.session.execute(text("SELECT current_value FROM asset_detail_id_counter"))
        current_value = result.scalar()
        return {'current_value': current_value}


class ModelDetailIDManager:
    """
    Manages all_model_detail_id sequence for ModelDetailVirtual tables
    Ensures unique IDs across all model detail tables
    """
    
    _lock = threading.Lock()
    
    @classmethod
    def get_next_model_detail_id(cls):
        """
        Get the next available model detail ID
        Uses database counter table for thread safety
        """
        with cls._lock:
            # Update counter and get new value atomically
            db.session.execute(text("UPDATE model_detail_id_counter SET current_value = current_value + 1"))
            result = db.session.execute(text("SELECT current_value FROM model_detail_id_counter"))
            return result.scalar()
    
    @classmethod
    def create_sequence_if_not_exists(cls):
        """
        Create the model detail sequence if it doesn't exist
        For SQLite, we'll use a simple counter table approach
        """
        try:
            # For SQLite, create a simple counter table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS model_detail_id_counter (
                    id INTEGER PRIMARY KEY,
                    current_value INTEGER DEFAULT 0
                )
            """))
            
            # Initialize the counter if it doesn't exist
            result = db.session.execute(text("SELECT COUNT(*) FROM model_detail_id_counter"))
            if result.scalar() == 0:
                db.session.execute(text("INSERT INTO model_detail_id_counter (current_value) VALUES (0)"))
            
            db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def reset_sequence(cls, start_value=1):
        """
        Reset the model detail sequence to a specific value
        Useful for testing or data migration
        """
        with cls._lock:
            db.session.execute(text(f"UPDATE model_detail_id_counter SET current_value = {start_value - 1}"))
            db.session.commit()
    
    @classmethod
    def get_current_sequence_value(cls):
        """
        Get the current value of the model detail sequence
        """
        result = db.session.execute(text("SELECT current_value FROM model_detail_id_counter"))
        return result.scalar()
    
    @classmethod
    def get_sequence_info(cls):
        """
        Get information about the model detail sequence
        """
        result = db.session.execute(text("SELECT current_value FROM model_detail_id_counter"))
        current_value = result.scalar()
        return {'current_value': current_value}
