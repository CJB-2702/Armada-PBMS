from app.data.maintenance.virtual_action_tool import VirtualActionTool
from app import db
from sqlalchemy.orm import relationship

class TemplateActionTool(VirtualActionTool):
    """
    Tools required for template actions
    Standalone copy - NO proto reference (allows template-specific customization)
    """
    __tablename__ = 'template_action_tools'
    
    # Parent reference - REQUIRED
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_actions.id'), nullable=False)
    
    # Template-specific fields
    is_required = db.Column(db.Boolean, default=True)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    template_action_item = relationship('TemplateActionItem', back_populates='template_action_tools')
    tool = relationship('Tool', foreign_keys='TemplateActionTool.tool_id', lazy='select')
    
    def __repr__(self):
        tool_name = self.tool.tool_name if self.tool else "Unknown"
        req_str = "Required" if self.is_required else "Optional"
        return f'<TemplateActionTool {self.id}: {tool_name} x{self.quantity_required} ({req_str})>'
