#!/usr/bin/env python3
"""
Scheduled Task Plan Virtual Base Class
Mixin class for all scheduled task plan models
"""

from datetime import datetime, timedelta
from app.models.core.user_created_base import UserCreatedBase

class ScheduledTaskPlanVirtual(UserCreatedBase):
    """
    Virtual mixin class for scheduled task plans
    Provides common functionality and interface for all scheduled task plan types
    """

    __abstract__ = True
    
    @property
    def has_meter_intervals(self):
        """Check if this plan has any meter-based intervals"""
        return any([
            getattr(self, 'interval_meter1', None),
            getattr(self, 'interval_meter2', None),
            getattr(self, 'interval_meter3', None),
            getattr(self, 'interval_meter4', None)
        ])
    
    @property
    def has_time_interval(self):
        """Check if this plan has a time-based interval"""
        return getattr(self, 'interval_days', None) is not None
    
    def get_meter_thresholds(self):
        """Get all meter thresholds for this plan"""
        thresholds = []
        for i in range(1, 5):
            meter_value = getattr(self, f'interval_meter{i}', None)
            if meter_value:
                thresholds.append((f'meter{i}', meter_value))
        return thresholds
    
    def get_next_maintenance_date(self, asset, from_date=None):
        """Calculate next maintenance date based on asset's current meter readings"""
        if not from_date:
            from_date = datetime.utcnow()
        
        # Check meter-based intervals
        if self.has_meter_intervals:
            # This would be implemented based on asset's current meter readings
            # and the intervals defined in this plan
            pass
        
        # Check time-based interval
        if self.has_time_interval:
            return from_date + timedelta(days=self.interval_days)
        
        return None
    
    @property
    def plan_type(self):
        """Get the type of this plan"""
        if hasattr(self, 'asset_id'):
            return 'asset_additional'
        elif hasattr(self, 'asset_type_id') and hasattr(self, 'make_model_id'):
            return 'generic'
        elif hasattr(self, 'asset_type_id'):
            return 'asset_type'
        elif hasattr(self, 'make_model_id'):
            return 'model_additional'
        else:
            return 'unknown'
    
    @property
    def target_name(self):
        """Get the name of the target (asset type, make/model, or asset)"""
        if hasattr(self, 'asset') and self.asset:
            return self.asset.name
        elif hasattr(self, 'asset_type') and self.asset_type:
            return self.asset_type.name
        elif hasattr(self, 'make_model') and self.make_model:
            return f"{self.make_model.make} {self.make_model.model}"
        else:
            return "Unknown"
    
    @property
    def target_description(self):
        """Get a description of what this plan applies to"""
        if self.plan_type == 'asset_additional':
            return f"Asset: {self.target_name}"
        elif self.plan_type == 'generic':
            if self.asset_type and self.make_model:
                return f"Asset Type: {self.asset_type.name}, Make/Model: {self.make_model.make} {self.make_model.model}"
            elif self.asset_type:
                return f"Asset Type: {self.asset_type.name}"
            elif self.make_model:
                return f"Make/Model: {self.make_model.make} {self.make_model.model}"
            else:
                return "Generic Plan"
        elif self.plan_type == 'asset_type':
            return f"Asset Type: {self.target_name}"
        elif self.plan_type == 'model_additional':
            return f"Make/Model: {self.target_name}"
        else:
            return "Unknown Target"
    
    def __repr__(self):
        """String representation of the scheduled task plan"""
        return f'<{self.__class__.__name__} {self.name} for {self.target_description}>'
