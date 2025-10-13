#!/usr/bin/env python3
"""
MakeModel Factory
Factory class for creating MakeModel instances with proper detail table initialization
"""

from app.logger import get_logger
from app import db

logger = get_logger("asset_management.models.assets.factories")

class MakeModelFactory:
    """
    Factory class for creating MakeModel instances
    Ensures proper creation with detail table initialization
    """
    
    @classmethod
    def create_make_model(cls, created_by_id=None, commit=True, **kwargs):
        """
        Create a new MakeModel with proper initialization
        
        Args:
            created_by_id (int): ID of the user creating the make/model
            commit (bool): Whether to commit the transaction (default: True)
            **kwargs: MakeModel fields (make, model, year, asset_type_id, etc.)
            
        Returns:
            MakeModel: The created make/model instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        from app.models.core.make_model import MakeModel
        
        # Validate required fields
        if 'make' not in kwargs:
            raise ValueError("Make is required")
        if 'model' not in kwargs:
            raise ValueError("Model is required")
        
        # Check for duplicate make/model/year combination
        existing_model = MakeModel.query.filter_by(
            make=kwargs['make'],
            model=kwargs['model'],
            year=kwargs.get('year')
        ).first()
        
        if existing_model:
            raise ValueError(
                f"Make/Model/Year combination already exists: "
                f"{kwargs['make']} {kwargs['model']} {kwargs.get('year', 'N/A')}"
            )
        
        # Set audit fields if provided
        if created_by_id:
            kwargs['created_by_id'] = created_by_id
            kwargs['updated_by_id'] = created_by_id
        
        # Create the make/model instance
        make_model = MakeModel(**kwargs)
        
        logger.info(f"Creating make/model: {kwargs.get('make')} {kwargs.get('model')} {kwargs.get('year', '')}")
        
        # Add to session
        db.session.add(make_model)
        
        # Commit if requested
        if commit:
            db.session.commit()
            logger.info(f"Make/Model created successfully: {make_model.make} {make_model.model} (ID: {make_model.id})")
        else:
            # Flush to get the ID but don't commit
            db.session.flush()
            logger.info(f"Make/Model added to session: {make_model.make} {make_model.model} (ID: {make_model.id}, not committed)")
        
        # The after_insert event listener will automatically create detail table rows
        # This happens in MakeModel._after_insert() which calls make_model.create_detail_table_rows()
        
        return make_model
    
    @classmethod
    def create_make_model_from_dict(cls, make_model_data, created_by_id=None, commit=True, lookup_fields=None):
        """
        Create a make/model from a dictionary, with optional find_or_create behavior
        
        Args:
            make_model_data (dict): Make/Model data dictionary
            created_by_id (int): ID of the user creating the make/model
            commit (bool): Whether to commit the transaction
            lookup_fields (list): Fields to use for find_or_create (e.g., ['make', 'model', 'year'])
            
        Returns:
            tuple: (make_model, created) where created is True if make/model was created
        """
        from app.models.core.make_model import MakeModel
        
        # If lookup_fields provided, try to find existing make/model
        if lookup_fields:
            query_filters = {field: make_model_data.get(field) for field in lookup_fields if field in make_model_data}
            existing_model = MakeModel.query.filter_by(**query_filters).first()
            
            if existing_model:
                logger.info(f"Found existing make/model: {existing_model.make} {existing_model.model} (ID: {existing_model.id})")
                return existing_model, False
        
        # Create new make/model
        make_model = cls.create_make_model(created_by_id=created_by_id, commit=commit, **make_model_data)
        return make_model, True
    
    @classmethod
    def update_make_model(cls, make_model, updated_by_id=None, commit=True, **kwargs):
        """
        Update an existing make/model
        
        Args:
            make_model (MakeModel): The make/model to update
            updated_by_id (int): ID of the user updating the make/model
            commit (bool): Whether to commit the transaction
            **kwargs: Fields to update
            
        Returns:
            MakeModel: The updated make/model instance
        """
        from app.models.core.make_model import MakeModel
        
        # Check for duplicate make/model/year if any of those fields are being updated
        if any(key in kwargs for key in ['make', 'model', 'year']):
            make = kwargs.get('make', make_model.make)
            model = kwargs.get('model', make_model.model)
            year = kwargs.get('year', make_model.year)
            
            existing_model = MakeModel.query.filter_by(
                make=make,
                model=model,
                year=year
            ).first()
            
            if existing_model and existing_model.id != make_model.id:
                raise ValueError(
                    f"Make/Model/Year combination already exists: {make} {model} {year or 'N/A'}"
                )
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(make_model, key):
                setattr(make_model, key, value)
        
        # Set updated_by_id if provided
        if updated_by_id:
            make_model.updated_by_id = updated_by_id
        
        logger.info(f"Updating make/model: {make_model.make} {make_model.model} (ID: {make_model.id})")
        
        # Commit if requested
        if commit:
            db.session.commit()
            logger.info(f"Make/Model updated successfully: {make_model.make} {make_model.model} (ID: {make_model.id})")
        else:
            logger.info(f"Make/Model updates staged: {make_model.make} {make_model.model} (ID: {make_model.id}, not committed)")
        
        return make_model

