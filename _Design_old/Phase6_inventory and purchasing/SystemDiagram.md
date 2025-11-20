# Phase 6: Inventory and Purchasing System - Visual Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE 6: PURCHASING & INVENTORY                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              MANAGER LAYER                               │
│                         (Business Logic & Factories)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ PurchaseOrder    │  │  PartArrival     │  │   Inventory      │     │
│  │    Manager       │  │    Manager       │  │    Manager       │     │
│  │                  │  │                  │  │                  │     │
│  │ • Create POs     │  │ • Receive Parts  │  │ • Track Moves    │     │
│  │ • Link Demands   │  │ • Inspect Parts  │  │ • Update Stock   │     │
│  │ • Track Status   │  │ • Update POs     │  │ • Issue Parts    │     │
│  │ • Events         │  │ • Trigger Inv    │  │ • Transfers      │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                           │
│         ┌──────────────────────────────────────────────┐                │
│         │         PartDemandManager                     │                │
│         │  (Extension for Purchasing Integration)      │                │
│         │                                               │                │
│         │  • Identify Unfulfilled Demands               │                │
│         │  • Purchase Recommendations                   │                │
│         │  • Check Inventory Availability               │                │
│         └──────────────────────────────────────────────┘                │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                  │
│                        (Database Models - CRUD Only)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  PURCHASING SYSTEM              RECEIVING SYSTEM        INVENTORY        │
│  ┌──────────────┐              ┌──────────────┐       ┌─────────────┐  │
│  │  Purchase    │◄─────────────│   Part       │       │  Inventory  │  │
│  │   Order      │              │   Arrival    │──────►│  Movement   │  │
│  │   Header     │              └──────────────┘       └─────────────┘  │
│  └──────────────┘                      │                      │          │
│         │                               │                      ▼          │
│         ▼                               ▼              ┌─────────────┐  │
│  ┌──────────────┐              ┌──────────────┐       │   Active    │  │
│  │  Purchase    │              │   Package    │       │  Inventory  │  │
│  │   Order      │              │   Header     │       └─────────────┘  │
│  │    Line      │              └──────────────┘                         │
│  └──────────────┘                                                        │
│         │                                                                 │
│         ▼                                                                 │
│  ┌──────────────┐                                                        │
│  │ PartDemand   │                                                        │
│  │ PO Line Link │                                                        │
│  └──────────────┘                                                        │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       INTEGRATION WITH OTHER PHASES                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  PHASE 5 (Maintenance)    PHASE 1 (Core)         PHASE 4 (Supply)       │
│  ┌──────────────┐         ┌──────────────┐      ┌──────────────┐       │
│  │  Maintenance │         │    Major     │      │     Part     │       │
│  │    Action    │         │   Location   │      └──────────────┘       │
│  └──────────────┘         └──────────────┘                              │
│         │                         │                      │               │
│         ▼                         ▼                      ▼               │
│  ┌──────────────┐         ┌──────────────┐      ┌──────────────┐       │
│  │     Part     │────────►│    Event     │◄─────│  Purchase    │       │
│  │    Demand    │         │              │      │    Order     │       │
│  └──────────────┘         └──────────────┘      └──────────────┘       │
│                                   │                                      │
│                                   ▼                                      │
│                            ┌──────────────┐                             │
│                            │   Comment    │                             │
│                            └──────────────┘                             │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Complete Data Flow Diagram

### 1. Purchase Order Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDER CREATION PROCESS                       │
└─────────────────────────────────────────────────────────────────────────┘

START: Maintenance Action needs parts
        │
        ▼
  ┌────────────┐
  │   Create   │
  │    Part    │ (Phase 5 - Maintenance)
  │   Demand   │
  └────────────┘
        │
        ▼
  ┌────────────┐
  │   Part     │
  │  Demand    │
  │  Manager   │ Checks inventory availability
  └────────────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  [In Stock?]       [Not Available]
        │                 │
        ▼                 ▼
  ┌────────────┐    ┌────────────┐
  │  Inventory │    │   Queue    │
  │   Manager  │    │    for     │
  │   Issues   │    │ Purchasing │
  │   Parts    │    └────────────┘
  └────────────┘          │
        │                 ▼
        │           ┌────────────┐
        │           │   Group    │
        │           │  Demands   │
        │           │  by Part   │
        │           └────────────┘
        │                 │
        │                 ▼
        │           ┌────────────┐
        │           │  Purchase  │
        │           │   Order    │ PurchaseOrderManager
        │           │  Manager   │ creates PO Header
        │           └────────────┘
        │                 │
        │                 ▼
        │           ┌────────────┐
        │           │   Create   │
        │           │ PO Lines   │ for each part
        │           └────────────┘
        │                 │
        │                 ▼
        │           ┌────────────┐
        │           │    Link    │
        │           │  Demands   │ to PO Lines
        │           │  to Lines  │
        │           └────────────┘
        │                 │
        │                 ▼
        │           ┌────────────┐
        │           │   Submit   │
        │           │     PO     │ Status: Draft → Submitted
        │           └────────────┘
        │                 │
        │                 ▼
        │           ┌────────────┐
        │           │   Create   │
        │           │   Event    │ for tracking
        │           └────────────┘
        │                 │
        ▼                 ▼
  [Demand Fulfilled] [Awaiting Arrival]
```

### 2. Part Receiving Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       PART RECEIVING PROCESS                             │
└─────────────────────────────────────────────────────────────────────────┘

START: Package arrives at location
        │
        ▼
  ┌────────────┐
  │   Create   │
  │  Package   │ Package tracking number
  │   Header   │ Received by user
  └────────────┘
        │
        ▼
  ┌────────────┐
  │    Part    │
  │  Arrival   │ PartArrivalManager
  │  Manager   │ receives parts against PO line
  └────────────┘
        │
        ▼
  ┌────────────┐
  │   Record   │
  │  Quantity  │ quantity_received
  │  Received  │ condition (Good/Damaged/Mixed)
  └────────────┘
        │
        ▼
  ┌────────────┐
  │  Inspect   │
  │   Parts    │ User inspects
  └────────────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  [Good Quality]    [Damaged/Reject]
        │                 │
        ▼                 ▼
  ┌────────────┐    ┌────────────┐
  │   Accept   │    │   Reject   │
  │   Parts    │    │   Parts    │
  │            │    │            │
  │ quantity_  │    │ quantity_  │
  │  accepted  │    │  rejected  │
  └────────────┘    └────────────┘
        │                 │
        ▼                 │
  ┌────────────┐          │
  │  Inventory │          │
  │  Movement  │          │
  │  (Arrival) │          │ (No inventory movement)
  └────────────┘          │
        │                 │
        ▼                 │
  ┌────────────┐          │
  │   Update   │          │
  │   Active   │          │
  │ Inventory  │          │
  └────────────┘          │
        │                 │
        ▼                 │
  ┌────────────┐          │
  │   Update   │◄─────────┘
  │  PO Line   │
  │ Received   │ quantity_received updated
  │  Quantity  │
  └────────────┘
        │
        ▼
  ┌────────────┐
  │   Check    │
  │  PO Line   │ All quantity received?
  │ Complete?  │
  └────────────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  [Complete]         [Partial]
        │                 │
        ▼                 ▼
  Status: Complete   Status: Partial
        │                 │
        ▼                 ▼
  ┌────────────┐    ┌────────────┐
  │   Check    │    │    Wait    │
  │  All PO    │    │    for     │
  │   Lines    │    │   More     │
  │ Complete?  │    │  Arrivals  │
  └────────────┘    └────────────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  [All Complete]    [Some Pending]
        │                 │
        ▼                 ▼
  PO Status:        PO Status:
  Complete          Partial
```

### 3. Inventory Movement and Issue Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INVENTORY MOVEMENT PROCESS                            │
└─────────────────────────────────────────────────────────────────────────┘

TRIGGER: Multiple events can trigger inventory movements

  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
  │   Parts    │   │   Issue    │   │   Manual   │   │  Transfer  │
  │  Arrived   │   │    to      │   │ Adjustment │   │  Between   │
  │            │   │Maintenance │   │            │   │ Locations  │
  └────────────┘   └────────────┘   └────────────┘   └────────────┘
        │                 │                 │                 │
        ▼                 ▼                 ▼                 ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │               INVENTORY MANAGER                                  │
  │                                                                   │
  │  • Validates movement                                            │
  │  • Creates InventoryMovement record                              │
  │  • Updates ActiveInventory                                       │
  │  • Creates Event for tracking                                    │
  └─────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌────────────┐
  │   Create   │
  │ Inventory  │ Records:
  │ Movement   │ • movement_type
  │   Record   │ • quantity (+/-)
  │            │ • location
  │            │ • reference
  └────────────┘
        │
        ▼
  ┌────────────┐
  │   Update   │
  │   Active   │ Updates:
  │ Inventory  │ • quantity_on_hand
  │            │ • last_movement_date
  │            │ • unit_cost_avg
  └────────────┘
        │
        ▼
  ┌────────────┐
  │   Check    │ Checks:
  │   Stock    │ • Below minimum?
  │   Levels   │ • Out of stock?
  └────────────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  [Low Stock]      [Adequate Stock]
        │                 │
        ▼                 │
  ┌────────────┐          │
  │   Trigger  │          │
  │  Purchase  │          │
  │  Alert     │          │
  └────────────┘          │
        │                 │
        └─────────┬───────┘
                  │
                  ▼
            [Movement Complete]
```

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ENTITY RELATIONSHIPS                                 │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌────────────────┐
                    │      Part      │
                    │   (Phase 4)    │
                    └────────────────┘
                            │
                            │ 1
                ┌───────────┼───────────┐
                │           │           │
              * │         * │         * │
        ┌───────▼────┐  ┌───▼──────┐  ┌▼──────────┐
        │ Purchase   │  │   Part   │  │  Active   │
        │  Order     │  │ Arrival  │  │ Inventory │
        │   Line     │  └──────────┘  └───────────┘
        └────────────┘       │              │
              │              │              │
            1 │            1 │            * │
              │          ┌───▼────────┐     │
              │          │  Package   │     │
              │          │  Header    │     │
              │          └────────────┘     │
              │                             │
            * │                             │
        ┌─────▼──────┐                      │
        │ Purchase   │                      │
        │  Order     │                      │
        │  Header    │                      │
        └────────────┘                      │
              │                             │
            1 │                             │
              │                             │
              │                      ┌──────▼─────────┐
              │                      │   Inventory    │
              │                      │   Movement     │
              │                      └────────────────┘
              │                             │
            1 │                           * │
        ┌─────▼──────┐              ┌──────▼─────────┐
        │   Event    │              │   Part Demand  │
        │  (Phase 1) │◄─────────────│   (Phase 5)    │
        └────────────┘          1   └────────────────┘
              │                             │
            * │                           * │
        ┌─────▼──────┐              ┌──────▼─────────┐
        │  Comment   │              │ PartDemand-    │
        │  (Phase 1) │              │ PurchaseOrder- │
        └────────────┘              │  Line (assoc)  │
                                    └────────────────┘
                                            │
                                          * │
                                    ┌───────▼────┐
                                    │ Purchase   │
                                    │  Order     │
                                    │   Line     │
                                    └────────────┘

┌────────────────────────────────────────────────────────────────┐
│ LEGEND:                                                         │
│   1   = One                                                     │
│   *   = Many                                                    │
│   ──►  = Relationship direction                                │
│   (assoc) = Association table (many-to-many junction)          │
└────────────────────────────────────────────────────────────────┘
```

## Status State Diagrams

### Purchase Order Header Status Flow

```
┌────────────────────────────────────────────────────────────────┐
│           PURCHASE ORDER HEADER STATUS STATES                   │
└────────────────────────────────────────────────────────────────┘

    [START]
       │
       ▼
  ┌─────────┐
  │  Draft  │───────────────────┐
  └─────────┘                   │
       │                        │
       │ Submit Order           │ Cancel
       ▼                        │
  ┌─────────┐                   │
  │Submitted│                   │
  └─────────┘                   │
       │                        │
       │ First Partial          │
       │ Arrival                │
       ▼                        │
  ┌─────────┐                   │
  │ Partial │                   │
  └─────────┘                   │
       │                        │
       │ All Lines              │
       │ Complete               │
       ▼                        │
  ┌─────────┐                   │
  │Complete │                   │
  └─────────┘                   │
                                │
                                ▼
                          ┌──────────┐
                          │Cancelled │
                          └──────────┘
```

### Part Arrival Status Flow

```
┌────────────────────────────────────────────────────────────────┐
│               PART ARRIVAL STATUS STATES                        │
└────────────────────────────────────────────────────────────────┘

    [Received into Package]
             │
             ▼
        ┌─────────┐
        │ Pending │
        └─────────┘
             │
             │ Inspection Performed
             ▼
        ┌──────────┐
        │Inspected │
        └──────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│Accepted │      │Rejected │
│         │      │         │
│(Creates │      │(No inv  │
│inv move)│      │movement)│
└─────────┘      └─────────┘
```

### Inventory Movement Types

```
┌────────────────────────────────────────────────────────────────┐
│             INVENTORY MOVEMENT TYPES                            │
└────────────────────────────────────────────────────────────────┘

              INVENTORY MOVEMENTS
                      │
        ┌─────────────┼──────────────┬──────────────┐
        │             │              │              │
        ▼             ▼              ▼              ▼
   ┌─────────┐  ┌─────────┐   ┌─────────┐   ┌──────────┐
   │ Arrival │  │  Issue  │   │Adjustment│  │ Transfer │
   │         │  │         │   │          │  │          │
   │ qty: +  │  │ qty: -  │   │ qty: +/- │  │ From: -  │
   │         │  │         │   │          │  │ To:   +  │
   └─────────┘  └─────────┘   └──────────┘  └──────────┘
        │             │              │              │
        │             │              │              │
    Refs:         Refs:          Refs:         Refs:
    PartArrival   PartDemand     Manual        Transfer
                                 entry         locations
        │             │              │              │
  Trace Chain:  Trace Chain:   Trace Chain:   Trace Chain:
  initial=A     initial=A      initial=A      initial=A
  previous=null previous=M1    previous=M1    previous=M1
        │             │              │              │
        └─────────────┴──────────────┴──────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │     Update     │
                   │     Active     │
                   │   Inventory    │
                   └────────────────┘

TRACEABILITY FIELDS ON EACH MOVEMENT:
┌──────────────────────────────────────────────────────────────┐
│ • part_arrival_id      → Links to triggering arrival (if any)│
│ • part_demand_id       → Links to fulfilling demand (if any) │
│ • initial_arrival_id   → ALWAYS points to original arrival   │
│ • previous_movement_id → Links to prior movement in chain    │
└──────────────────────────────────────────────────────────────┘
```

## Traceability Chain Visualization

```
┌─────────────────────────────────────────────────────────────────────────┐
│               COMPLETE TRACEABILITY CHAIN                                │
│     From Maintenance Need to Part Usage - Full History                  │
└─────────────────────────────────────────────────────────────────────────┘

MAINTENANCE                PURCHASING              RECEIVING
  (Phase 5)                 (Phase 6A)             (Phase 6B)
     │                          │                       │
     ▼                          ▼                       ▼
┌─────────┐               ┌─────────┐           ┌─────────┐
│Maint    │               │Purchase │           │Package  │
│Action   │               │Order    │           │Header   │
│         │               │Header   │           │         │
└─────────┘               └─────────┘           └─────────┘
     │                          │                       │
     │ Creates                  │ Contains              │ Contains
     ▼                          ▼                       ▼
┌─────────┐    Linked to   ┌─────────┐   Received as ┌─────────┐
│  Part   │───────────────►│Purchase │◄──────────────│  Part   │
│ Demand  │                │Order    │               │Arrival  │
│         │                │Line     │               │    [A]  │◄─┐
└─────────┘                └─────────┘               └─────────┘  │
     │                                                      │       │
     │                                                      │       │
     │                    INVENTORY                         │       │
     │                     (Phase 6C)                       │       │
     │                         │                            │       │
     │                         ▼                            │       │
     │                   ┌──────────┐                       │       │
     │                   │Inventory │◄──────────────────────┘       │
     │                   │Movement  │  part_arrival_id              │
     │                   │(Arrival) │  initial_arrival_id [A]◄──────┤
     │                   │   [M1]   │  previous_movement_id=null    │
     │                   └──────────┘                               │
     │                         │                                    │
     │                         │ Updates                            │
     │                         ▼                                    │
     │                   ┌──────────┐                               │
     │                   │  Active  │                               │
     │                   │Inventory │                               │
     │                   └──────────┘                               │
     │                         │                                    │
     │                         │ Transfer/Adjust                    │
     │                         ▼                                    │
     │                   ┌──────────┐                               │
     │                   │Inventory │                               │
     │                   │Movement  │  initial_arrival_id [A]◄──────┤
     │                   │(Transfer)│  previous_movement_id [M1]    │
     │                   │   [M2]   │                               │
     │                   └──────────┘                               │
     │                         │                                    │
     │                         │ Issues to                          │
     │                         ▼                                    │
     │                   ┌──────────┐                               │
     └──────────────────►│Inventory │                               │
       Fulfilled by      │Movement  │  initial_arrival_id [A]◄──────┘
                         │ (Issue)  │  previous_movement_id [M2]
                         │   [M3]   │  part_demand_id
                         └──────────┘

┌────────────────────────────────────────────────────────────────┐
│ ENHANCED TRACEABILITY - AT ANY POINT, YOU CAN TRACE:          │
│                                                                 │
│ • Part Demand ──► Which PO Line ──► Which PO                  │
│ • PO Line ──► Which Arrivals ──► Which Package                │
│ • Part Arrival ──► All Inventory Movements ──► Current Stock  │
│ • Inventory Issue ──► Which Part Demand ──► Which Maint Work  │
│                                                                 │
│ NEW TRACEABILITY CHAINS:                                       │
│ • Any Movement ──► initial_arrival_id ──► Original Purchase   │
│ • Any Movement ──► previous_movement_id ──► Movement History  │
│ • Full Chain: M3 → M2 → M1 → Part Arrival → PO Line → PO     │
│                                                                 │
│ EXAMPLE:                                                        │
│   Issue Movement [M3]:                                         │
│     - previous_movement_id → Transfer [M2]                     │
│     - M2.previous_movement_id → Arrival [M1]                   │
│     - M2.initial_arrival_id → Part Arrival [A]                 │
│     - Part Arrival [A] → PO Line → Purchase Order              │
│                                                                 │
│ COMPLETE BIDIRECTIONAL TRACEABILITY WITH MOVEMENT HISTORY!     │
└────────────────────────────────────────────────────────────────┘
```

## Manager vs Model Responsibility Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│           SEPARATION OF CONCERNS: MODELS vs MANAGERS                     │
└─────────────────────────────────────────────────────────────────────────┘

╔════════════════════════╦════════════════════╦═════════════════════════╗
║    FUNCTIONALITY       ║   MODEL (CRUD)     ║   MANAGER (Logic)       ║
╠════════════════════════╬════════════════════╬═════════════════════════╣
║ Database Schema        ║        ✓           ║                         ║
║ Field Definitions      ║        ✓           ║                         ║
║ Relationships          ║        ✓           ║                         ║
║ Basic Properties       ║        ✓           ║                         ║
║ to_dict() / from_dict()║        ✓           ║                         ║
╠════════════════════════╬════════════════════╬═════════════════════════╣
║ Create Complex Record  ║                    ║          ✓              ║
║ Business Validation    ║                    ║          ✓              ║
║ Status Transitions     ║                    ║          ✓              ║
║ Multi-Table Operations ║                    ║          ✓              ║
║ Calculations           ║                    ║          ✓              ║
║ Event Creation         ║                    ║          ✓              ║
║ Factory Methods        ║                    ║          ✓              ║
║ Complex Queries        ║                    ║          ✓              ║
╚════════════════════════╩════════════════════╩═════════════════════════╝

EXAMPLE: Creating a Purchase Order

MODEL RESPONSIBILITIES:
┌────────────────────────────────────────────────────────────────┐
│ PurchaseOrderHeader                                            │
│                                                                 │
│ class PurchaseOrderHeader(UserCreatedBase):                   │
│     po_number = db.Column(db.String, unique=True)             │
│     vendor_name = db.Column(db.String, nullable=False)        │
│     status = db.Column(db.String, default='Draft')            │
│     # ... more fields                                          │
│                                                                 │
│     @property                                                   │
│     def is_complete(self):                                     │
│         return self.status == 'Complete'                       │
│                                                                 │
│     def to_dict(self):                                         │
│         return {...}  # Simple dict conversion                │
└────────────────────────────────────────────────────────────────┘

MANAGER RESPONSIBILITIES:
┌────────────────────────────────────────────────────────────────┐
│ PurchaseOrderManager                                           │
│                                                                 │
│ class PurchaseOrderManager:                                    │
│                                                                 │
│     def create_from_part_demands(demands, vendor, user_id):   │
│         # 1. Validate demands                                  │
│         # 2. Group by part                                     │
│         # 3. Calculate quantities                              │
│         # 4. Create PO header                                  │
│         # 5. Create PO lines                                   │
│         # 6. Link to demands                                   │
│         # 7. Create event                                      │
│         # 8. Send notifications                                │
│         # 9. Return complete PO                                │
│                                                                 │
│     def submit_order(po_id, user_id):                          │
│         # 1. Validate can submit                               │
│         # 2. Update status                                     │
│         # 3. Lock lines                                        │
│         # 4. Create event                                      │
│         # 5. Notify vendor                                     │
│         # 6. Update part demand status                         │
└────────────────────────────────────────────────────────────────┘
```

## File Organization Visual

```
app/models/purchasing/
│
├── __init__.py
│   └─► Imports all models and managers for easy access
│
├── build.py
│   └─► Phase 6 database build and initialization
│
├── base/                          ◄─── DATA MODELS (CRUD ONLY)
│   ├── __init__.py
│   ├── purchase_order_header.py   ─► Database table definition
│   ├── purchase_order_line.py     ─► Database table definition
│   ├── part_demand_po_line.py     ─► Association table
│   ├── package_header.py          ─► Database table definition
│   ├── part_arrival.py            ─► Database table definition
│   ├── active_inventory.py        ─► Database table definition
│   └── inventory_movement.py      ─► Database table definition
│
├── managers/                      ◄─── BUSINESS LOGIC
│   ├── __init__.py
│   ├── purchase_order_manager.py  ─► PO creation, status, linking
│   ├── part_arrival_manager.py    ─► Receiving, inspection
│   ├── inventory_manager.py       ─► Movement tracking, updates
│   └── part_demand_manager.py     ─► Demand analysis, recommendations
│
└── utils/                         ◄─── HELPER FUNCTIONS
    ├── __init__.py
    ├── purchasing_helpers.py      ─► Utility functions
    └── inventory_helpers.py       ─► Stock calculations

USAGE PATTERN:
┌────────────────────────────────────────────────────────────────┐
│ Route/Controller                                               │
│                                                                 │
│   from app.models.purchasing.managers import (                │
│       PurchaseOrderManager,                                    │
│       InventoryManager                                         │
│   )                                                            │
│                                                                 │
│   @app.route('/purchase-order/create', methods=['POST'])      │
│   def create_po():                                             │
│       demands = request.form.getlist('demands')                │
│       vendor = request.form.get('vendor')                      │
│                                                                 │
│       # Call manager, not model directly                       │
│       po = PurchaseOrderManager.create_from_part_demands(     │
│           demands, vendor, current_user.id                     │
│       )                                                        │
│                                                                 │
│       return redirect(f'/purchase-order/{po.id}')             │
└────────────────────────────────────────────────────────────────┘
```

## Integration Points Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 6 INTEGRATION POINTS                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ WITH PHASE 1 (CORE):                                                 │
├──────────────────────────────────────────────────────────────────────┤
│ • MajorLocation   ──► Used for inventory tracking by location        │
│ • Event           ──► PO and arrivals create events                  │
│ • Comment         ──► Events support discussion                      │
│ • User            ──► All operations track user                      │
│ • UserCreatedBase ──► All models inherit audit trail                 │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ WITH PHASE 4 (SUPPLY):                                               │
├──────────────────────────────────────────────────────────────────────┤
│ • Part            ──► Referenced by PO lines, arrivals, inventory    │
│                       No changes to Part model needed                 │
│                       Just add relationships                          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ WITH PHASE 5 (MAINTENANCE):                                          │
├──────────────────────────────────────────────────────────────────────┤
│ • PartDemand      ──► Links to PurchaseOrderLine                     │
│                   ──► Links to InventoryMovement (Issue)             │
│                   ──► Manager checks inventory availability          │
│                   ──► Manager creates PO recommendations             │
│                                                                       │
│ • Action          ──► No direct integration                          │
│                   ──► Part demands are the link                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ FUTURE PHASES:                                                       │
├──────────────────────────────────────────────────────────────────────┤
│ • Phase 7 Planning ──► Pull inventory data for planning             │
│ • Phase 8 Vendors  ──► Link PO to Vendor table                      │
│ • Phase 9 Budgets  ──► Track PO costs against budgets               │
└──────────────────────────────────────────────────────────────────────┘
```

