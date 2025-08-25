"""
Supply main routes for dashboard and overview
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.supply.part import Part
from app.models.supply.tool import Tool
from app.models.supply.part_demand import PartDemand
from app.logger import get_logger
from datetime import datetime

bp = Blueprint('supply_main', __name__)
logger = get_logger("asset_management.routes.supply.main")

@bp.route('/supply')
@login_required
def index():
    """Supply management dashboard with overview statistics"""
    logger.debug(f"User {current_user.username} accessing supply dashboard")
    
    # Get basic statistics
    total_parts = Part.query.count()
    total_tools = Tool.query.count()
    total_part_demands = PartDemand.query.count()
    
    # Get low stock parts
    low_stock_parts = Part.query.filter(Part.current_stock_level <= Part.minimum_stock_level).limit(5).all()
    
    # Get out of stock parts
    out_of_stock_parts = Part.query.filter(Part.current_stock_level <= 0).limit(5).all()
    
    # Get recent parts
    recent_parts = Part.query.order_by(Part.created_at.desc()).limit(5).all()
    
    # Get recent tools
    recent_tools = Tool.query.order_by(Tool.created_at.desc()).limit(5).all()
    
    # Get tools that need calibration
    tools_needing_calibration = Tool.query.filter(Tool.next_calibration_date <= datetime.utcnow().date()).limit(5).all()
    
    # Get parts by category
    parts_by_category = {}
    for part in Part.query.all():
        category = part.category or 'Uncategorized'
        if category not in parts_by_category:
            parts_by_category[category] = 0
        parts_by_category[category] += 1
    
    # Get tools by status
    tools_by_status = {}
    for tool in Tool.query.all():
        status = tool.status or 'Unknown'
        if status not in tools_by_status:
            tools_by_status[status] = 0
        tools_by_status[status] += 1
    
    return render_template('supply/index.html',
                         total_parts=total_parts,
                         total_tools=total_tools,
                         total_part_demands=total_part_demands,
                         low_stock_parts=low_stock_parts,
                         out_of_stock_parts=out_of_stock_parts,
                         recent_parts=recent_parts,
                         recent_tools=recent_tools,
                         tools_needing_calibration=tools_needing_calibration,
                         parts_by_category=parts_by_category,
                         tools_by_status=tools_by_status)
