from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.factories.maintenance_action_set_factory import MaintenanceActionSetFactory
from app.models.maintenance.factories.action_factory import ActionFactory
from app.models.maintenance.factories.part_demand_factory import PartDemandFactory
from app import db

class MaintenanceFactory:
    """Main factory for creating complete maintenance workflows from templates"""
    
    @staticmethod
    def create_complete_maintenance_from_template(template_action_set: TemplateActionSet, **kwargs):
        """
        Create a complete maintenance workflow from a TemplateActionSet
        
        This includes:
        - MaintenanceActionSet
        - All Actions from TemplateActionItems
        - All PartDemands from TemplatePartDemands
        
        Args:
            template_action_set: The template to create from
            **kwargs: Additional parameters for creation
                     (asset_id, scheduled_date, user_id, etc.)
        
        Returns:
            dict: Dictionary containing created objects
                {
                    'maintenance_action_set': MaintenanceActionSet,
                    'actions': list[Action],
                    'part_demands': list[PartDemand]
                }
        """
        # Create the maintenance action set
        maintenance_action_set = MaintenanceActionSetFactory.create_from_template(
            template_action_set, **kwargs
        )
        
        # Create all actions with their part demands
        actions = []
        all_part_demands = []
        
        template_action_items = template_action_set.template_action_items.order_by(
            'sequence_order'
        )
        
        for template_action_item in template_action_items:
            if template_action_item.is_required:
                # Create action
                action = ActionFactory.create_from_template(
                    template_action_item, 
                    maintenance_action_set.id, 
                    kwargs.get('created_by_id')
                )
                actions.append(action)
                
                # Create part demands for this action
                part_demands = PartDemandFactory.create_all_from_template_action_item(
                    template_action_item, 
                    action.id, 
                    kwargs.get('created_by_id')
                )
                all_part_demands.extend(part_demands)
        
        return {
            'maintenance_action_set': maintenance_action_set,
            'actions': actions,
            'part_demands': all_part_demands
        }
    
    @staticmethod
    def create_maintenance_action_set_only(template_action_set: TemplateActionSet, **kwargs):
        """
        Create only a MaintenanceActionSet from a TemplateActionSet (no actions)
        
        Args:
            template_action_set: The template to create from
            **kwargs: Additional parameters for creation
        
        Returns:
            MaintenanceActionSet: The created maintenance action set
        """
        return MaintenanceActionSetFactory.create_from_template(template_action_set, **kwargs)
    
    @staticmethod
    def add_actions_to_maintenance_action_set(maintenance_action_set, template_action_set: TemplateActionSet, user_id: int):
        """
        Add actions to an existing maintenance action set from a template
        
        Args:
            maintenance_action_set: The existing maintenance action set
            template_action_set: The template to create actions from
            user_id: ID of the user creating the actions
        
        Returns:
            list[Action]: List of created actions
        """
        return ActionFactory.create_all_from_template_action_set(
            template_action_set, maintenance_action_set.id, user_id
        )
