from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class TemplateActionTool(UserCreatedBase):
    __tablename__ = 'template_action_tools'
    
    # Foreign keys
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    
    # Template-specific fields
    is_required = db.Column(db.Boolean, default=True)
    quantity_required = db.Column(db.Integer, default=1)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem', backref='template_action_tools')
    tool = db.relationship('Tool')
    
    def __repr__(self):
        return f'<TemplateActionTool {self.tool.tool_name if self.tool else "Unknown Tool"}: {"Required" if self.is_required else "Optional"}>'
    
    @property
    def tool_name(self):
        """Get the tool name for convenience"""
        return self.tool.tool_name if self.tool else "Unknown Tool"
    
    @property
    def tool_status(self):
        """Get the tool status for convenience"""
        return self.tool.status if self.tool else "Unknown"
    
    def is_tool_available(self):
        """Check if the required tool is available"""
        if not self.tool:
            return False
        return self.tool.is_available
    
    def get_quantity_display(self):
        """Get quantity display string"""
        if self.quantity_required == 1:
            return "1"
        return f"{self.quantity_required}"
    
    def get_requirement_display(self):
        """Get requirement display string"""
        if self.is_required:
            return "Required"
        return "Optional"
