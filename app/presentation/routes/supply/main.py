"""
Supply routes
"""

from flask import Blueprint, render_template
from flask_login import login_required
from app.data.supply_items.part import Part
from app.data.supply_items.tool import Tool
from app.data.supply_items.issuable_tool import IssuableTool
from app.logger import get_logger
from app import db

from .parts import bp as parts_bp
from .tools import bp as tools_bp

logger = get_logger("asset_management.routes.supply.main")

# Create main supply blueprint
supply_bp = Blueprint('supply', __name__, url_prefix='/supply')

# ROUTE_TYPE: WORK_PORTAL (Complex GET)
# This route coordinates multiple domain operations for dashboard statistics.
# Rationale: Aggregates statistics from multiple sources for dashboard view.
@supply_bp.route('/')
@login_required
def index():
    """Supply management dashboard with statistics and alerts"""
    logger.debug("Accessing supply management dashboard")
    
    # Get basic statistics
    total_parts = Part.query.count()
    total_tools = Tool.query.count()
    
    # Get low stock parts (stock level <= minimum stock level)
    low_stock_parts = Part.query.filter(
        Part.current_stock_level <= Part.minimum_stock_level,
        Part.current_stock_level > 0
    ).limit(10).all()
    
    # Get out of stock parts (stock level <= 0)
    out_of_stock_parts = Part.query.filter(
        Part.current_stock_level <= 0
    ).limit(10).all()
    
    # Get tools needing calibration (next_calibration_date is in the past or due soon)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    tools_needing_calibration = IssuableTool.query.filter(
        IssuableTool.next_calibration_date.isnot(None),
        IssuableTool.next_calibration_date <= today + timedelta(days=30)
    ).limit(10).all()
    
    # Get recent parts (last 10 created)
    recent_parts = Part.query.order_by(Part.created_at.desc()).limit(10).all()
    
    # Get recent tools (last 10 created)
    recent_tools = Tool.query.order_by(Tool.created_at.desc()).limit(10).all()
    
    # Get recent issuable tools (last 10 created)
    recent_issuable_tools = IssuableTool.query.order_by(IssuableTool.created_at.desc()).limit(10).all()
    
    # Get parts by category
    from sqlalchemy import func
    parts_by_category = dict(
        db.session.query(Part.category, func.count(Part.id))
        .group_by(Part.category)
        .all()
    )
    
    # Get tools by status (from IssuableTool)
    tools_by_status = dict(
        db.session.query(IssuableTool.status, func.count(IssuableTool.id))
        .group_by(IssuableTool.status)
        .all()
    )
    
    logger.info(f"Supply dashboard - Parts: {total_parts}, Tools: {total_tools}, Low stock: {len(low_stock_parts)}")
    
    return render_template('supply/index.html',
                         total_parts=total_parts,
                         total_tools=total_tools,
                         total_part_demands=0,  # Part demands moved to maintenance module
                         low_stock_parts=low_stock_parts,
                         out_of_stock_parts=out_of_stock_parts,
                         tools_needing_calibration=tools_needing_calibration,
                         recent_parts=recent_parts,
                         recent_tools=recent_tools,
                         recent_issuable_tools=recent_issuable_tools,
                         parts_by_category=parts_by_category,
                         tools_by_status=tools_by_status)

# Register sub-blueprints
supply_bp.register_blueprint(parts_bp, url_prefix='/parts')
supply_bp.register_blueprint(tools_bp, url_prefix='/tools')

