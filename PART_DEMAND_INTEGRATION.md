# Part Demand Integration - Maintenance Page

## ✅ Implementation Complete

Part demand information with inventory availability is now displayed on the maintenance do_maintenance page.

## Location

**URL**: `http://localhost:5000/maintenance/do_maintenance/<action_set_id>`

## What Was Added

### 1. Backend (Route) Changes
**File**: `app/routes/maintenance/main.py`

Added inventory availability checking for all part demands:

```python
# Phase 6: Get part demands with inventory availability
part_demand_info = []
try:
    from app.models.inventory.managers import PartDemandManager
    
    for action in actions:
        if hasattr(action, 'part_demands'):
            for demand in action.part_demands:
                # Check inventory availability
                availability = PartDemandManager.check_inventory_availability(demand.id)
                
                part_demand_info.append({
                    'demand': demand,
                    'action': action,
                    'availability': availability
                })
except ImportError:
    # Phase 6 not available yet
    logger.debug("Phase 6 inventory system not available")
    pass
```

**Key Features:**
- Imports Phase 6 PartDemandManager
- Checks inventory availability for each part demand
- Gracefully handles when Phase 6 is not available (ImportError)
- Passes `part_demand_info` to template

### 2. Frontend (Template) Changes
**File**: `app/templates/maintenance/do_maintenance.html`

Added new "Parts Required" card in sidebar (between Event Information and Comments sections).

**Displays:**
- Part name and part number
- Action the part is needed for
- Part demand status badge (Planned/Received/etc.)
- Required quantity with unit of measure

**Inventory Availability Indicators:**

1. **✅ Available at this location** (Green alert)
   - Shows total units available
   - Displays "Issue from Inventory" button (disabled - coming soon)

2. **ℹ️ Available at other location** (Blue alert)
   - Shows total units available
   - Indicates transfer needed

3. **⚠️ Need to purchase** (Yellow alert)
   - Shows current availability
   - Shows quantity shortage
   - Displays "Create Purchase Order" button (disabled - coming soon)

4. **❌ Out of stock** (Red alert)
   - Indicates purchase order required

**Additional Information:**
- Location details showing where inventory is available
- Current location vs other locations
- Quantity available at each location

**Action Buttons** (Prepared for future implementation):
- "Issue from Inventory" - For parts available locally
- "Create Purchase Order" - For parts needing purchase
- "View Inventory" - Link to inventory details

## Features

### ✅ Smart Availability Detection
- Checks if parts are available at the preferred location (where maintenance is being done)
- Checks if parts are available at other locations (requires transfer)
- Determines if parts need to be purchased
- Shows exact quantities available

### ✅ Visual Status Indicators
- Color-coded alerts (green, blue, yellow, red)
- Bootstrap icons for quick visual identification
- Status badges for part demands

### ✅ Location-Aware
- Understands the location context from the action
- Shows inventory at current location vs. other locations
- Helps plan logistics (transfer vs. direct issue)

### ✅ Graceful Degradation
- If Phase 6 inventory system is not available, page still works
- Shows "Inventory information not available" message
- No errors or broken functionality

## Example Display

When viewing a maintenance action set, the sidebar now shows:

```
┌─────────────────────────────────────┐
│ Parts Required (2)                  │
├─────────────────────────────────────┤
│ Engine Oil 5W-30 (OIL-001)          │
│ For: Add New Oil                    │
│ Required: 5.0 quarts                │
│                                     │
│ ✅ Available at this location       │
│    10 units in stock                │
│                                     │
│ [Issue from Inventory]              │
│ [View Inventory]                    │
│                                     │
│ 📍 Current location: 10 available   │
├─────────────────────────────────────┤
│ Oil Filter (FIL-001)                │
│ For: Replace Oil Filter             │
│ Required: 1.0 units                 │
│                                     │
│ ⚠️ Need to purchase                 │
│    Only 0 units available (need 1)  │
│                                     │
│ [Create Purchase Order]             │
│ [View Inventory]                    │
└─────────────────────────────────────┘
```

## Integration Points

### With Phase 5 (Maintenance)
- ✅ Reads part demands from maintenance actions
- ✅ Shows part demand status
- ✅ Links parts to specific actions

### With Phase 6 (Inventory)
- ✅ Uses `PartDemandManager.check_inventory_availability()`
- ✅ Gets inventory data from ActiveInventory
- ✅ Shows multi-location inventory
- ✅ Determines purchase needs

### With Phase 4 (Supply)
- ✅ Displays part information (name, number, UOM)
- ✅ Shows part details from Part model

## Future Enhancements (Ready to Implement)

### 1. Issue from Inventory (Button enabled)
When user clicks "Issue from Inventory":
- Create route to handle inventory issuance
- Call `InventoryManager.issue_to_demand()`
- Update part demand status to "Received"
- Create inventory movement record
- Update stock levels

### 2. Create Purchase Order (Button enabled)
When user clicks "Create Purchase Order":
- Redirect to purchase order creation page
- Pre-populate with this part demand
- Call `PurchaseOrderManager.create_from_part_demands()`
- Link PO to part demand

### 3. View Inventory (Button enabled)
When user clicks "View Inventory":
- Redirect to inventory detail page for this part
- Show complete inventory across all locations
- Show movement history
- Show traceability chain

### 4. Transfer Between Locations
For parts available at other locations:
- Add "Request Transfer" button
- Call `InventoryManager.transfer_between_locations()`
- Track transfer in progress

### 5. Real-time Updates
- HTMX integration for dynamic updates
- Auto-refresh when inventory changes
- Notifications when parts become available

## Data Flow

```
User visits /maintenance/do_maintenance/123
         ↓
Route gathers action set and actions
         ↓
For each action with part_demands:
    ↓
    PartDemandManager.check_inventory_availability(demand_id)
         ↓
    Returns availability dict with:
         - can_fulfill_from_preferred (bool)
         - can_fulfill_from_any (bool)
         - needs_purchase (bool)
         - total_available (float)
         - location_inventory (list)
         - other_locations (list)
         ↓
Template displays:
    - Part information
    - Availability status (color-coded)
    - Location details
    - Action buttons
```

## Files Modified

```
Modified:
  ✅ app/routes/maintenance/main.py
     - Added part demand inventory checking
     - Integrated PartDemandManager
     
  ✅ app/templates/maintenance/do_maintenance.html
     - Added "Parts Required" card in sidebar
     - Visual inventory status indicators
     - Action buttons for future features
```

## Testing

### Manual Test Steps:
1. Start the application:
   ```bash
   python app.py
   ```

2. Navigate to maintenance dashboard:
   ```
   http://localhost:5000/maintenance/
   ```

3. Click on an action set (or create one with part demands)

4. Go to "Do Maintenance" page

5. Check sidebar for "Parts Required" section

### Expected Behavior:
- ✅ Parts Required card appears if there are part demands
- ✅ Each part shows name, number, quantity needed
- ✅ Inventory availability is displayed with color coding
- ✅ Buttons are present (disabled) for future features
- ✅ No errors in browser console
- ✅ Page loads successfully

## Benefits

### For Maintenance Technicians:
- 👁️ **Visibility**: See immediately if parts are available
- ⚡ **Efficiency**: Know before starting if parts need to be ordered
- 📍 **Location Aware**: See where parts are located
- ✅ **Status Tracking**: See which parts have been received

### For Maintenance Planners:
- 📊 **Planning**: Identify parts shortages before scheduling
- 💰 **Cost Control**: Know when purchases are needed
- 🎯 **Prioritization**: Focus on jobs where parts are available
- 📈 **Metrics**: Track part availability issues

### For Inventory Managers:
- 🔗 **Integration**: Maintenance needs linked to inventory
- 📦 **Demand Visibility**: See what maintenance needs exist
- 🏪 **Stock Planning**: Plan inventory based on maintenance schedule
- 🔄 **Traceability**: Track parts from arrival to usage

## Status

| Feature | Status |
|---------|--------|
| Backend Integration | ✅ Complete |
| Frontend Display | ✅ Complete |
| Availability Checking | ✅ Complete |
| Visual Indicators | ✅ Complete |
| Location Awareness | ✅ Complete |
| Graceful Degradation | ✅ Complete |
| Issue from Inventory | ⏳ Button ready |
| Create Purchase Order | ⏳ Button ready |
| View Inventory | ⏳ Button ready |

---

**Ready for**: Implementing the action button functionality (issue, purchase, view)

**Works with**: Existing maintenance system and new Phase 6 inventory system

**No Breaking Changes**: Existing functionality remains unchanged

