from app.models.maintenance.factories.maintenance_factory import MaintenanceFactory
from app.models.maintenance.utils.maintenance_helpers import MaintenanceHelpers
from app.models.maintenance.utils.template_helpers import TemplateHelpers
from app import db

class QuickActions:
    """Quick action functions for common maintenance operations"""
    
    @staticmethod
    def create_maintenance_from_template(template_action_set_id: int, asset_id: int, user_id: int, **kwargs):
        """
        Quick function to create a complete maintenance workflow from a template
        
        Args:
            template_action_set_id: ID of the template to use
            asset_id: ID of the asset to maintain
            user_id: ID of the user creating the maintenance
            **kwargs: Additional parameters (scheduled_date, priority, etc.)
        
        Returns:
            dict: Created maintenance objects
        """
        # Get the template
        template_action_set = db.session.get(TemplateActionSet, template_action_set_id)
        if not template_action_set:
            raise ValueError(f"Template with ID {template_action_set_id} not found")
        
        # Set required parameters
        params = {
            'asset_id': asset_id,
            'created_by_id': user_id,
            **kwargs
        }
        
        # Create the complete maintenance workflow
        result = MaintenanceFactory.create_complete_maintenance_from_template(
            template_action_set, **params
        )
        
        # Commit the transaction
        db.session.commit()
        
        return result
    
    @staticmethod
    def schedule_maintenance(template_action_set_id: int, asset_id: int, scheduled_date, user_id: int, **kwargs):
        """
        Schedule a maintenance event for a specific date
        
        Args:
            template_action_set_id: ID of the template to use
            asset_id: ID of the asset to maintain
            scheduled_date: When to perform the maintenance
            user_id: ID of the user scheduling the maintenance
            **kwargs: Additional parameters
        
        Returns:
            MaintenanceEvent: The scheduled maintenance event
        """
        params = {
            'asset_id': asset_id,
            'scheduled_date': scheduled_date,
            'created_by_id': user_id,
            **kwargs
        }
        
        result = QuickActions.create_maintenance_from_template(
            template_action_set_id, asset_id, user_id, **params
        )
        
        return result['maintenance_event']
    
    @staticmethod
    def get_template_preview(template_action_set_id: int):
        """
        Get a preview of what a template will create
        
        Args:
            template_action_set_id: ID of the template to preview
        
        Returns:
            dict: Preview information
        """
        template_action_set = db.session.get(TemplateActionSet, template_action_set_id)
        if not template_action_set:
            raise ValueError(f"Template with ID {template_action_set_id} not found")
        
        # Get template summary
        summary = TemplateHelpers.get_template_summary(template_action_set)
        
        # Get aggregated parts and tools
        parts = TemplateHelpers.get_template_parts_aggregated(template_action_set)
        tools = TemplateHelpers.get_template_tools_aggregated(template_action_set)
        
        # Validate template
        validation = TemplateHelpers.validate_template_completeness(template_action_set)
        
        return {
            'summary': summary,
            'parts': parts,
            'tools': tools,
            'validation': validation
        }
    
    @staticmethod
    def clone_and_schedule(template_action_set_id: int, new_name: str, asset_id: int, scheduled_date, user_id: int, **kwargs):
        """
        Clone a template and immediately schedule it
        
        Args:
            template_action_set_id: ID of the template to clone
            new_name: Name for the new template
            asset_id: ID of the asset to maintain
            scheduled_date: When to perform the maintenance
            user_id: ID of the user performing the operation
            **kwargs: Additional parameters
        
        Returns:
            dict: Both the cloned template and scheduled maintenance
        """
        # Get the original template
        original_template = db.session.get(TemplateActionSet, template_action_set_id)
        if not original_template:
            raise ValueError(f"Template with ID {template_action_set_id} not found")
        
        # Clone the template
        cloned_template = TemplateHelpers.clone_template(
            original_template, new_name, user_id
        )
        
        # Schedule maintenance with the cloned template
        scheduled_maintenance = QuickActions.schedule_maintenance(
            cloned_template.id, asset_id, scheduled_date, user_id, **kwargs
        )
        
        return {
            'cloned_template': cloned_template,
            'scheduled_maintenance': scheduled_maintenance
        }
