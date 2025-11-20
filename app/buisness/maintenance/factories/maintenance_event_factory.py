from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app import db
from datetime import datetime

class MaintenanceActionSetFactory:
    """Factory for creating MaintenanceActionSet from TemplateActionSet"""
    
    @staticmethod
    def create_from_template(template_action_set: TemplateActionSet, **kwargs):
        """
        Create a MaintenanceActionSet from a TemplateActionSet
        
        Args:
            template_action_set: The template to create from
            **kwargs: Additional parameters for MaintenanceActionSet creation
                     (asset_id, scheduled_date, user_id, etc.)
        
        Returns:
            MaintenanceActionSet: The created maintenance action set
        """
        # Set default values
        defaults = {
            'template_action_set_id': template_action_set.id,
            'task_name': template_action_set.task_name,
            'description': template_action_set.description,
            'estimated_duration': template_action_set.estimated_duration,
            'staff_count': template_action_set.staff_count,
            'parts_cost': template_action_set.parts_cost,
            'labor_hours': template_action_set.labor_hours,
            'safety_review_required': template_action_set.safety_review_required,
            'revision': template_action_set.revision,
            'scheduled_date': kwargs.get('scheduled_date', datetime.utcnow())
        }
        
        # Merge with provided kwargs
        event_data = {**defaults, **kwargs}
        
        # Create the maintenance action set
        maintenance_action_set = MaintenanceActionSet(**event_data)
        db.session.add(maintenance_action_set)
        db.session.flush()  # Get the ID
        
        return maintenance_action_set
    
    @staticmethod
    def create_with_actions_from_template(template_action_set: TemplateActionSet, **kwargs):
        """
        Create a MaintenanceActionSet with all its Actions from a TemplateActionSet
        
        Args:
            template_action_set: The template to create from
            **kwargs: Additional parameters for MaintenanceActionSet creation
        
        Returns:
            MaintenanceActionSet: The created maintenance action set with actions
        """
        # Create the maintenance action set
        maintenance_action_set = MaintenanceActionSetFactory.create_from_template(
            template_action_set, **kwargs
        )
        
        # Create actions from template action items
        from app.buisness.maintenance.factories.action_factory import ActionFactory
        actions = ActionFactory.create_all_from_template_action_set(
            template_action_set, maintenance_action_set.id, kwargs.get('created_by_id')
        )
        
        return maintenance_action_set
    
    @staticmethod
    def copy_details_from_template_action_set(maintenance_action_set, template_action_set: TemplateActionSet, user_id=None):
        """Copy common details from template action set to maintenance action set"""
        maintenance_action_set.task_name = template_action_set.task_name
        maintenance_action_set.description = template_action_set.description
        maintenance_action_set.estimated_duration = template_action_set.estimated_duration
        maintenance_action_set.staff_count = template_action_set.staff_count
        maintenance_action_set.parts_cost = template_action_set.parts_cost
        maintenance_action_set.labor_hours = template_action_set.labor_hours
        maintenance_action_set.safety_review_required = template_action_set.safety_review_required
        maintenance_action_set.revision = template_action_set.revision
        
        if user_id:
            maintenance_action_set.add_comment_to_event(user_id, f"Details copied from template: {template_action_set.task_name}")
    
    @staticmethod
    def generate_actions_from_template_action_set(maintenance_action_set, template_action_set: TemplateActionSet, user_id):
        """Generate actions from template action set - using delegation pattern"""
        from app.buisness.maintenance.factories.action_factory import ActionFactory
        
        actions = ActionFactory.create_all_from_template_action_set(
            template_action_set, maintenance_action_set.id, user_id
        )
        
        if user_id:
            maintenance_action_set.add_comment_to_event(user_id, f"Generated {len(actions)} actions from template: {template_action_set.task_name}")
        
        return actions
