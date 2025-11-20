from app.data.maintenance.base.part_demand import PartDemand
from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app import db

class PartDemandFactory:
    """Factory for creating PartDemands from TemplatePartDemands"""
    
    @staticmethod
    def create_from_template(template_part_demand: TemplatePartDemand, action_id: int, user_id: int, **kwargs):
        """
        Create a PartDemand from a TemplatePartDemand
        
        Args:
            template_part_demand: The template to create from
            action_id: ID of the action this part demand belongs to
            user_id: ID of the user creating the part demand
            **kwargs: Additional parameters for PartDemand creation
        
        Returns:
            PartDemand: The created part demand
        """
        # Set default values
        defaults = {
            'action_id': action_id,
            'part_id': template_part_demand.part_id,
            'quantity_required': template_part_demand.quantity_required,
            'notes': template_part_demand.notes,
            'sequence_order': template_part_demand.sequence_order,
            'created_by_id': user_id
        }
        
        # Merge with provided kwargs
        part_demand_data = {**defaults, **kwargs}
        
        # Create the part demand
        part_demand = PartDemand(**part_demand_data)
        db.session.add(part_demand)
        db.session.flush()  # Get the ID
        
        return part_demand
    
    @staticmethod
    def create_all_from_template_action_item(template_action_item: TemplateActionItem, action_id: int, user_id: int):
        """
        Create all PartDemands from a TemplateActionItem
        
        Args:
            template_action_item: The template action item to create from
            action_id: ID of the action
            user_id: ID of the user creating the part demands
        
        Returns:
            list[PartDemand]: List of created part demands
        """
        part_demands = []
        
        # Get template part demands ordered by sequence
        template_part_demands = template_action_item.template_part_demands.order_by(
            TemplatePartDemand.sequence_order
        )
        
        for template_part_demand in template_part_demands:
            part_demand = PartDemandFactory.create_from_template(
                template_part_demand, action_id, user_id
            )
            part_demands.append(part_demand)
        
        return part_demands
    
    @staticmethod
    def create_required_only_from_template_action_item(template_action_item: TemplateActionItem, action_id: int, user_id: int):
        """
        Create only required PartDemands from a TemplateActionItem
        
        Args:
            template_action_item: The template action item to create from
            action_id: ID of the action
            user_id: ID of the user creating the part demands
        
        Returns:
            list[PartDemand]: List of created part demands (required only)
        """
        part_demands = []
        
        # Get template part demands ordered by sequence
        template_part_demands = template_action_item.template_part_demands.order_by(
            TemplatePartDemand.sequence_order
        )
        
        for template_part_demand in template_part_demands:
            # Only create demands for required parts
            if template_part_demand.is_required:
                part_demand = PartDemandFactory.create_from_template(
                    template_part_demand, action_id, user_id
                )
                part_demands.append(part_demand)
        
        return part_demands
    
    @staticmethod
    def split_part_demand(original_demand, new_qty, new_status, user_id):
        """
        Split a part demand into two demands
        
        Args:
            original_demand: The original part demand to split
            new_qty: Quantity for the new part demand
            new_status: Status for the new part demand
            user_id: User performing the split
        
        Returns:
            PartDemand: The new part demand created from the split
        
        Raises:
            ValueError: If new_qty is not less than current qty or status is the same
        """
        # Validate inputs
        if new_qty >= original_demand.quantity_required:
            raise ValueError("New quantity must be less than current quantity")
        
        if new_status == original_demand.status:
            raise ValueError("New status must be different from current status")
        
        # Calculate remaining quantity for current demand
        remaining_qty = original_demand.quantity_required - new_qty
        
        # Find the maximum sequence order for this action
        max_sequence = db.session.query(db.func.max(PartDemand.sequence_order)).filter_by(
            action_id=original_demand.action_id
        ).scalar() or 0
        
        # Create new part demand with the split quantity and new status
        new_part_demand = PartDemand(
            action_id=original_demand.action_id,
            part_id=original_demand.part_id,
            quantity_required=new_qty,
            status=new_status,
            sequence_order=max_sequence + 1,  # Place at the end
            notes=f"Split from PartDemand {original_demand.id}",
            created_by_id=user_id,
            updated_by_id=user_id
        )
        
        # Add the new part demand to the session
        db.session.add(new_part_demand)
        db.session.flush()  # Get the ID for the comment
        
        # Adjust original part demand quantity
        original_demand._set_quantity_required(remaining_qty, user_id)
        
        # Add comments to track the split
        split_comment = f"Part demand split: {new_qty} units moved to new demand (ID: {new_part_demand.id}) with status '{new_status}', remaining: {remaining_qty} units"
        original_demand._add_comment_to_maintenance_event(user_id, split_comment)
        
        # Add comment to the new part demand
        new_part_demand._add_comment_to_maintenance_event(user_id, f"Created from split of PartDemand {original_demand.id}: {new_qty} units with status '{new_status}'")
        
        return new_part_demand
