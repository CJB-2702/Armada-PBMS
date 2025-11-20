from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
from app import db

class TemplateHelpers:
    """Utility functions for template operations"""
    
    @staticmethod
    def get_template_parts_aggregated(template_action_set: TemplateActionSet):
        """
        Get aggregated parts requirements from a template action set
        
        Args:
            template_action_set: The template to analyze
        
        Returns:
            dict: Aggregated parts with quantities
        """
        parts_aggregated = {}
        
        for action_item in template_action_set.template_action_items:
            if action_item.is_required:
                for part_demand in action_item.template_part_demands:
                    part_id = part_demand.part_id
                    part_name = part_demand.part.part_name if part_demand.part else "Unknown"
                    
                    if part_id in parts_aggregated:
                        parts_aggregated[part_id]['quantity'] += part_demand.quantity_required
                    else:
                        parts_aggregated[part_id] = {
                            'part_name': part_name,
                            'quantity': part_demand.quantity_required,
                            'is_required': part_demand.is_required,
                            'notes': part_demand.notes
                        }
        
        return parts_aggregated
    
    @staticmethod
    def get_template_tools_aggregated(template_action_set: TemplateActionSet):
        """
        Get aggregated tools requirements from a template action set
        
        Args:
            template_action_set: The template to analyze
        
        Returns:
            dict: Aggregated tools with quantities
        """
        tools_aggregated = {}
        
        for action_item in template_action_set.template_action_items:
            if action_item.is_required:
                for tool_template in action_item.template_action_tools:
                    tool_id = tool_template.tool_id
                    tool_name = tool_template.tool.tool_name if tool_template.tool else "Unknown"
                    
                    if tool_id in tools_aggregated:
                        # For tools, take the maximum quantity (tools are reusable)
                        tools_aggregated[tool_id]['quantity'] = max(
                            tools_aggregated[tool_id]['quantity'], 
                            tool_template.quantity_required
                        )
                    else:
                        tools_aggregated[tool_id] = {
                            'tool_name': tool_name,
                            'quantity': tool_template.quantity_required,
                            'is_required': tool_template.is_required,
                            'notes': tool_template.notes
                        }
        
        return tools_aggregated
    
    @staticmethod
    def validate_template_completeness(template_action_set: TemplateActionSet):
        """
        Validate that a template is complete and ready for use
        
        Args:
            template_action_set: The template to validate
        
        Returns:
            dict: Validation results
        """
        issues = []
        warnings = []
        
        # Check if template has action items
        if not template_action_set.template_action_items:
            issues.append("Template has no action items")
        
        # Check each action item
        for action_item in template_action_set.template_action_items:
            if not action_item.action_name:
                issues.append(f"Action item {action_item.id} has no name")
            
            if not action_item.description:
                warnings.append(f"Action item '{action_item.action_name}' has no description")
            
            if not action_item.estimated_duration:
                warnings.append(f"Action item '{action_item.action_name}' has no estimated duration")
        
        # Check for required parts
        has_required_parts = False
        for action_item in template_action_set.template_action_items:
            for part_demand in action_item.template_part_demands:
                if part_demand.is_required:
                    has_required_parts = True
                    break
        
        if not has_required_parts:
            warnings.append("Template has no required parts defined")
        
        return {
            'is_complete': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    @staticmethod
    def clone_template(template_action_set: TemplateActionSet, new_name: str, user_id: int):
        """
        Clone a template action set with a new name
        
        Args:
            template_action_set: The template to clone
            new_name: Name for the new template
            user_id: ID of the user creating the clone
        
        Returns:
            TemplateActionSet: The cloned template
        """
        # Create new template action set
        new_template = TemplateActionSet(
            task_name=new_name,
            description=template_action_set.description,
            estimated_duration=template_action_set.estimated_duration,
            staff_count=template_action_set.staff_count,
            parts_cost=template_action_set.parts_cost,
            labor_hours=template_action_set.labor_hours,
            safety_review_required=template_action_set.safety_review_required,
            revision=template_action_set.revision,
            created_by_id=user_id
        )
        
        db.session.add(new_template)
        db.session.flush()  # Get the ID
        
        # Clone action items
        for action_item in template_action_set.template_action_items:
            new_action_item = TemplateActionItem(
                template_action_set_id=new_template.id,
                action_name=action_item.action_name,
                description=action_item.description,
                sequence_order=action_item.sequence_order,
                estimated_duration=action_item.estimated_duration,
                expected_billable_hours=action_item.expected_billable_hours,
                safety_notes=action_item.safety_notes,
                notes=action_item.notes,
                is_required=action_item.is_required,
                minimum_staff_count=action_item.minimum_staff_count,
                instructions=action_item.instructions,
                instructions_type=action_item.instructions_type,
                required_skills=action_item.required_skills,
                created_by_id=user_id
            )
            
            db.session.add(new_action_item)
            db.session.flush()  # Get the ID
            
            # Clone part demands
            for part_demand in action_item.template_part_demands:
                new_part_demand = TemplatePartDemand(
                    template_action_item_id=new_action_item.id,
                    part_id=part_demand.part_id,
                    quantity_required=part_demand.quantity_required,
                    notes=part_demand.notes,
                    is_optional=part_demand.is_optional,
                    sequence_order=part_demand.sequence_order,
                    created_by_id=user_id
                )
                
                db.session.add(new_part_demand)
        
        return new_template
