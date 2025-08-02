#!/usr/bin/env python3
"""
Main build orchestrator for the Asset Management System
Handles phased building of models and data insertion
"""

from app import create_app, db
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_database(build_phase='all', data_phase='all'):
    """
    Main build orchestrator for the Asset Management System
    
    Args:
        build_phase (str): 'phase1', 'phase2', 'phase3', 'all', or 'none'
        data_phase (str): 'phase1', 'phase2', 'phase3', 'all', or 'none'
    """
    app = create_app()
    
    with app.app_context():
        logger.info(f"Starting database build - Build Phase: {build_phase}, Data Phase: {data_phase}")
        
        # Build models based on phase
        if build_phase != 'none':
            build_models(build_phase)
        
        # Insert data based on phase
        if data_phase != 'none':
            insert_data(data_phase)
        
        logger.info("Database build completed successfully")

def build_models(phase):
    """
    Build database models based on the specified phase
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', or 'all'
    """
    logger.info(f"Building models for phase: {phase}")
    
    if phase in ['phase1', 'phase2', 'phase3', 'all']:
        logger.info("Building Phase 1 models (Core Foundation)")
        from app.models.core.build import build_models as build_core_models
        build_core_models()
    
    if phase in ['phase2', 'phase3', 'all']:
        logger.info("Building Phase 2 models (Asset Details)")
        from app.models.assets.build import build_models as build_asset_models
        build_asset_models()
    
    if phase in ['phase3', 'all']:
        logger.info("Building Phase 3 models (Maintenance & Operations)")
        # Phase 3 builds on top of Phase 2, so Phase 2 models are already included
        pass
    
    # Create all tables
    db.create_all()
    logger.info("All database tables created")

def insert_data(phase):
    """
    Insert initial data based on the specified phase
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', or 'all'
    """
    logger.info(f"Inserting data for phase: {phase}")
    
    # Load build data
    build_data = load_build_data()
    
    if phase in ['phase1','phase2']:
        logger.info("Inserting Phase 1 data (Core Foundation)")
        from app.models.core.build import init_data
        init_data(build_data)
    
    if phase in ['phase2']:
        logger.info("Inserting Phase 2 data (Asset Details)")
        from app.models.assets.build import phase_2_init_data
        phase_2_init_data(build_data)
    
    if phase in ['phase3', 'all']:
        logger.info("Inserting Phase 3 data (Maintenance & Operations)")
        try:
            from app.models.core.asset import Asset
            from app.models.core.build import init_essential_data
            from app.models.assets.build import phase3_insert_data, phase3_update_data
            
            # Enable automatic detail insertion for Phase 3
            Asset.enable_automatic_detail_insertion()
            init_essential_data(build_data)
            phase3_insert_data(build_data)
            phase3_update_data(build_data)
        except ImportError as e:
            logger.error(f"Phase 3 failed to insert data: {e}")
            raise


def load_build_data():
    """
    Load build data from JSON file
    
    Returns:
        dict: Build data from JSON file
    """
    config_file = Path(__file__).parent / 'utils' / 'build_data.json'
    
    if not config_file.exists():
        raise FileNotFoundError(f"Build data file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        return json.load(f)

def build_models_only(phase):
    """
    Build only the models without inserting data
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', or 'all'
    """
    build_database(build_phase=phase, data_phase='none')

def insert_data_only(phase):
    """
    Insert only data without building models
    
    Args:
        phase (str): 'phase1', 'phase2', 'phase3', or 'all'
    """
    build_database(build_phase='none', data_phase=phase)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        build_phase = sys.argv[1]
        data_phase = sys.argv[2] if len(sys.argv) > 2 else build_phase
        build_database(build_phase=build_phase, data_phase=data_phase)
    else:
        build_database() 