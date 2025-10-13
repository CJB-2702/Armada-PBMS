from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.part_demand import PartDemand
from app import db
from sqlalchemy import func

class MaintenanceHelpers:
    """Utility functions for maintenance operations"""
    
    @staticmethod
    def get_template_summary(template_action_set: TemplateActionSet):
        """
        Get a summary of a template action set including parts and tools
        
        Args:
            template_action_set: The template to summarize
        
        Returns:
            dict: Summary information
        """
        parts_summary = {}
        tools_summary = {}
        total_duration = 0
        
        for action_item in template_action_set.template_action_items:
            if action_item.is_required:
                total_duration += action_item.estimated_duration or 0
                
                # Collect parts
                for part_demand in action_item.template_part_demands:
                    part_name = part_demand.part.part_name if part_demand.part else "Unknown"
                    if part_name in parts_summary:
                        parts_summary[part_name] += part_demand.quantity_required
                    else:
                        parts_summary[part_name] = part_demand.quantity_required
                
                # Collect tools
                for tool_template in action_item.template_action_tools:
                    tool_name = tool_template.tool.tool_name if tool_template.tool else "Unknown"
                    if tool_name in tools_summary:
                        tools_summary[tool_name] = max(tools_summary[tool_name], tool_template.quantity_required)
                    else:
                        tools_summary[tool_name] = tool_template.quantity_required
        
        return {
            'template_name': template_action_set.task_name,
            'total_duration': total_duration,
            'parts_required': parts_summary,
            'tools_required': tools_summary,
            'action_count': len([ai for ai in template_action_set.template_action_items if ai.is_required])
        }
    
    @staticmethod
    def calculate_maintenance_cost(maintenance_action_set: MaintenanceActionSet):
        """
        Calculate the total cost of a maintenance action set
        
        Args:
            maintenance_action_set: The maintenance action set to calculate cost for
        
        Returns:
            dict: Cost breakdown
        """
        parts_cost = 0
        labor_cost = 0
        
        # Calculate parts cost
        for action in maintenance_action_set.actions:
            for part_demand in action.part_demands:
                if part_demand.part and part_demand.part.unit_cost:
                    parts_cost += part_demand.quantity_required * part_demand.part.unit_cost
        
        # Calculate labor cost (if billable_hours is available)
        for action in maintenance_action_set.actions:
            if action.billable_hours:
                # Assuming a standard labor rate - this should be configurable
                labor_rate = 50.0  # $50/hour default
                labor_cost += action.billable_hours * labor_rate
        
        return {
            'parts_cost': parts_cost,
            'labor_cost': labor_cost,
            'total_cost': parts_cost + labor_cost
        }
    
    @staticmethod
    def get_maintenance_status(maintenance_action_set: MaintenanceActionSet):
        """
        Get detailed status information for a maintenance action set
        
        Args:
            maintenance_action_set: The maintenance action set to check
        
        Returns:
            dict: Status information
        """
        total_actions = len(maintenance_action_set.actions)
        completed_actions = len([a for a in maintenance_action_set.actions if a.status == 'Completed'])
        in_progress_actions = len([a for a in maintenance_action_set.actions if a.status == 'In Progress'])
        not_started_actions = len([a for a in maintenance_action_set.actions if a.status == 'Not Started'])
        
        return {
            'maintenance_status': maintenance_action_set.status,
            'total_actions': total_actions,
            'completed_actions': completed_actions,
            'in_progress_actions': in_progress_actions,
            'not_started_actions': not_started_actions,
            'completion_percentage': (completed_actions / total_actions * 100) if total_actions > 0 else 0
        }
    
    @staticmethod
    def validate_maintenance_action_set(maintenance_action_set: MaintenanceActionSet):
        """
        Validate a maintenance action set for completeness
        
        Args:
            maintenance_action_set: The maintenance action set to validate
        
        Returns:
            dict: Validation results
        """
        issues = []
        warnings = []
        
        # Check if maintenance action set has actions
        if not maintenance_action_set.actions:
            issues.append("No actions found for maintenance action set")
        
        # Check if all required actions have part demands
        for action in maintenance_action_set.actions:
            if action.template_action_item:
                template_part_demands = action.template_action_item.template_part_demands
                required_parts = [pd for pd in template_part_demands if pd.is_required]
                
                if required_parts and not action.part_demands:
                    warnings.append(f"Action '{action.action_name}' has no part demands but template requires parts")
        
        # Check for missing required fields
        if not maintenance_action_set.asset_id:
            issues.append("No asset assigned to maintenance action set")
        
        if not maintenance_action_set.scheduled_date:
            warnings.append("No scheduled date set for maintenance action set")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
