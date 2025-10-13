from app.models.maintenance.base.action import Action
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app import db

class ActionFactory:
    """Factory for creating Actions from TemplateActionItems"""
    
    @staticmethod
    def create_from_template(template_action_item: TemplateActionItem, maintenance_action_set_id: int, user_id: int, **kwargs):
        """
        Create an Action from a TemplateActionItem
        
        Args:
            template_action_item: The template to create from
            maintenance_action_set_id: ID of the maintenance action set this action belongs to
            user_id: ID of the user creating the action
            **kwargs: Additional parameters for Action creation
        
        Returns:
            Action: The created action
        """
        # Set default values
        defaults = {
            'maintenance_action_set_id': maintenance_action_set_id,
            'template_action_item_id': template_action_item.id,
            'action_name': template_action_item.action_name,
            'description': template_action_item.description,
            'sequence_order': template_action_item.sequence_order,
            'estimated_duration': template_action_item.estimated_duration,
            'expected_billable_hours': template_action_item.expected_billable_hours,
            'safety_notes': template_action_item.safety_notes,
            'notes': template_action_item.notes,
            'created_by_id': user_id
        }
        
        # Merge with provided kwargs
        action_data = {**defaults, **kwargs}
        
        # Create the action
        action = Action(**action_data)
        db.session.add(action)
        db.session.flush()  # Get the ID
        
        return action
    
    @staticmethod
    def create_all_from_template_action_set(template_action_set: TemplateActionSet, maintenance_action_set_id: int, user_id: int):
        """
        Create all Actions from a TemplateActionSet
        
        Args:
            template_action_set: The template action set to create from
            maintenance_action_set_id: ID of the maintenance action set
            user_id: ID of the user creating the actions
        
        Returns:
            list[Action]: List of created actions
        """
        actions = []
        
        # Get template action items ordered by sequence
        template_action_items = TemplateActionItem.query.filter_by(
            template_action_set_id=template_action_set.id
        ).order_by(TemplateActionItem.sequence_order).all()
        
        for template_action_item in template_action_items:
            if template_action_item.is_required:
                action = ActionFactory.create_from_template(
                    template_action_item, maintenance_action_set_id, user_id
                )
                actions.append(action)
        
        return actions
    
    @staticmethod
    def create_with_part_demands_from_template(template_action_item: TemplateActionItem, maintenance_action_set_id: int, user_id: int, **kwargs):
        """
        Create an Action with its PartDemands from a TemplateActionItem
        
        Args:
            template_action_item: The template to create from
            maintenance_action_set_id: ID of the maintenance action set
            user_id: ID of the user creating the action
            **kwargs: Additional parameters for Action creation
        
        Returns:
            Action: The created action with part demands
        """
        # Create the action
        action = ActionFactory.create_from_template(
            template_action_item, maintenance_action_set_id, user_id, **kwargs
        )
        
        # Create part demands from template part demands
        from app.models.maintenance.factories.part_demand_factory import PartDemandFactory
        part_demands = PartDemandFactory.create_all_from_template_action_item(
            template_action_item, action.id, user_id
        )
        
        return action
