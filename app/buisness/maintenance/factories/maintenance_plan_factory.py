from app.data.maintenance.base.maintenance_plan import MaintenancePlan
from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app import db
from datetime import datetime

class MaintenancePlanFactory:
    """Factory for creating MaintenancePlans and related operations"""
    
    @staticmethod
    def create_plan(name, description, asset_type_id, template_action_set_id, frequency_type, user_id, **kwargs):
        """
        Create a maintenance plan
        
        Args:
            name: Plan name
            description: Plan description
            asset_type_id: Asset type ID
            template_action_set_id: Template action set ID
            frequency_type: Frequency type (Time-based, Mileage-based, etc.)
            user_id: User creating the plan
            **kwargs: Additional parameters
        
        Returns:
            MaintenancePlan: The created maintenance plan
        """
        plan_data = {
            'name': name,
            'description': description,
            'asset_type_id': asset_type_id,
            'template_action_set_id': template_action_set_id,
            'frequency_type': frequency_type,
            'created_by_id': user_id,
            **kwargs
        }
        
        plan = MaintenancePlan(**plan_data)
        db.session.add(plan)
        db.session.flush()  # Get the ID
        
        return plan
    
    @staticmethod
    def create_from_template(template_action_set: TemplateActionSet, asset_type_id, frequency_type, user_id, **kwargs):
        """
        Create a maintenance plan from a template action set
        
        Args:
            template_action_set: The template to create from
            asset_type_id: Asset type ID
            frequency_type: Frequency type
            user_id: User creating the plan
            **kwargs: Additional parameters
        
        Returns:
            MaintenancePlan: The created maintenance plan
        """
        plan_data = {
            'name': f"{template_action_set.task_name} Plan",
            'description': f"Maintenance plan for {template_action_set.task_name}",
            'asset_type_id': asset_type_id,
            'template_action_set_id': template_action_set.id,
            'frequency_type': frequency_type,
            'created_by_id': user_id,
            **kwargs
        }
        
        plan = MaintenancePlan(**plan_data)
        db.session.add(plan)
        db.session.flush()  # Get the ID
        
        return plan
    
    @staticmethod
    def schedule_maintenance_from_plan(plan: MaintenancePlan, asset_id, scheduled_date=None, user_id=None):
        """
        Schedule maintenance from a plan - using delegation pattern
        
        Args:
            plan: The maintenance plan
            asset_id: Asset ID to maintain
            scheduled_date: Scheduled date (defaults to now)
            user_id: User scheduling the maintenance
        
        Returns:
            MaintenanceActionSet: The created maintenance action set
        """
        from app.buisness.maintenance.factories.maintenance_action_set_factory import MaintenanceActionSetFactory
        
        # Get template action set from plan
        template_action_set = plan.template_action_set
        
        # Create maintenance action set
        maintenance_action_set = MaintenanceActionSetFactory.create_from_template(
            template_action_set,
            asset_id=asset_id,
            maintenance_plan_id=plan.id,
            scheduled_date=scheduled_date or datetime.utcnow(),
            created_by_id=user_id
        )
        
        # Generate actions from template
        MaintenanceActionSetFactory.generate_actions_from_template_action_set(
            maintenance_action_set, template_action_set, user_id
        )
        
        return maintenance_action_set
    
    @staticmethod
    def calculate_next_maintenance_date(plan: MaintenancePlan, last_maintenance_date=None):
        """
        Calculate next maintenance date based on plan frequency
        
        Args:
            plan: The maintenance plan
            last_maintenance_date: Last maintenance date (defaults to now)
        
        Returns:
            datetime: Next maintenance date
        """
        if not last_maintenance_date:
            last_maintenance_date = datetime.utcnow()
        
        if plan.frequency_type == 'Time-based' and plan.delta_hours:
            # Calculate based on hours
            from datetime import timedelta
            return last_maintenance_date + timedelta(hours=plan.delta_hours)
        
        elif plan.frequency_type == 'Mileage-based':
            # This would require mileage tracking - placeholder for now
            return last_maintenance_date + timedelta(days=30)  # Default to 30 days
        
        else:
            # Default fallback
            return last_maintenance_date + timedelta(days=30)
    
    @staticmethod
    def get_eligible_assets(plan: MaintenancePlan):
        """
        Get assets eligible for this maintenance plan
        
        Args:
            plan: The maintenance plan
        
        Returns:
            Query: Query of eligible assets
        """
        from app.data.core.asset_info.asset import Asset
        
        query = Asset.query.filter_by(asset_type_id=plan.asset_type_id)
        
        # If plan is model-specific, filter by model
        if plan.model_id:
            query = query.filter_by(make_model_id=plan.model_id)
        
        return query
