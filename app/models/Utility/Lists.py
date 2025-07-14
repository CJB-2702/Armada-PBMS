from app.extensions import db
from app.models.BaseModels.ProtoClasses import GroupedLists, Types
from sqlalchemy import event, text
from app.utils.logger import get_logger

logger = get_logger()

#for refrence only GroupedLists is a child of Types and is found in ProtoClasses.py
"""
class GroupedLists(Types):
    __abstract__ = True
    UID = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __init__(self, group, value, description, created_by=0):
        uid = f"{group}_{value}"
        super().__init__(created_by)
        self.group = group
        self.value = value
        self.description = description
        self.UID = uid
"""

class GenericTypes(GroupedLists):
    __tablename__ = 'generic_types'


class Dropdowns(GroupedLists):
    __tablename__ = 'dropdowns'


@event.listens_for(Dropdowns, 'after_insert')
def check_dropdown_counts(target, connection, **kw):
    """Check if any dropdown groups have more than 20 items"""
    try:
        result = connection.execute(text("""
            SELECT "group", COUNT(*) as count 
            FROM dropdowns 
            GROUP BY "group"
            HAVING COUNT(*) > 20
        """))
        
        large_groups = result.fetchall()
        
        if large_groups:
            error_msg = (
                "ERROR: The following dropdown groups have more than 20 items:\n"
                + "\n".join([f"- {group}: {count} items" for group, count in large_groups])
                + "\n\nPlease contact your system administrator to:"
                + "\n1. Pull these dropdown values into their own dedicated tables"
                + "\n2. Update the data model to use the new tables instead of the generic dropdown table"
                + "\n\n Notify the development team to update the application code accordingly."
                + "\n Nobody is going to die if you don't do this, but it's a good idea to do it.Trust me."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    except Exception as e:
        logger.error(f"Error checking dropdown counts: {e}")
        raise