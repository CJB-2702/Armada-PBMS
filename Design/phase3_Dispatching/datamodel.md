## Dispatching Data Model (Design-Only)

This document defines the conceptual data model for the Dispatching domain. It is design-only and does not imply any implementation changes.

### Scope
- Requesting, reviewing, reserving, dispatching, returning assets
- Alternative resolutions: Contracted dispatch, Self-dispatch with Reimbursement
- Event and comment history, auditability, notifications

### Glossary
- Dispatch Request: A user's request to use an asset for a time window.
- Dispatch: The scheduled and executed allocation of a specific asset fulfilling a request.
- Event: Immutable audit trail entries capturing state changes and actions.
- Event-driven status: Status on the `Event` rows reflects lifecycle changes; no separate status-history table.
- Contracted Dispatch: Fulfillment via third party instead of internal asset.
- Reimbursement: Self-dispatch by employee with subsequent reimbursement.
- Check-out/In: Start and completion of an active dispatch.

### Entities

#### 1) DispatchRequest (Event detail record)
- id (PK)
- requester_id (FK → User)
- submitted_at (datetime, nullable until submission)
- desired_start (datetime)
- desired_end (datetime)
- num_people (int, nullable)
- names_freeform (text, nullable)
- asset_type_id (FK → AssetType)
- asset_subclass_text (string)
- dispatch_scope (enum: Onsite | Local | Regional | Interstate | Continental)
- estimated_meter_usage (decimal, nullable)
- major_location_id (FK → MajorLocation)
- activity_location (string)
- notes (text, nullable)
- status (enum: Draft | Submitted | UnderReview | Reserved | Dispatched | Completed | Rejected | Cancelled)
- resolution_type (enum: Internal | Contracted | Reimbursement, nullable until decision)
- created_at (datetime)
- updated_at (datetime)

Constraints:
- desired_end > desired_start
- submitted_at required when status ≥ Submitted

#### 2) Dispatch 
- id (PK)
- request_id (FK → DispatchRequest)
- asset_id (FK → Asset)
- assigned_by (FK → User)
- scheduled_start (datetime)
- scheduled_end (datetime)
- actual_start (datetime, nullable until check-out)
- actual_end (datetime, nullable until check-in)
- meter_start (decimal, nullable)
- meter_end (decimal, nullable)
- location_from_id (string)
- location_to_id (string)
- status (enum: Planned | Active | EditedPendingApproval | Completed | Cancelled)
- conflicts_resolved (bool, default false)
- created_at (datetime)
- updated_at (datetime)

Constraints:
- scheduled_end ≥ scheduled_start
- If meter_end set, meter_end ≥ meter_start

#### 3) ContractDetails (Optional – when resolution_type = Contracted)
- id (PK)
- request_id (FK → DispatchRequest)
- company_name (string)
- cost_currency (string, ISO)
- cost_amount (decimal)
- contract_reference (string, nullable)
- notes (text, nullable)
- created_at (datetime)

#### 4) ReimbursementDetails (Optional – when resolution_type = Reimbursement)
- id (PK)
- request_id (FK → DispatchRequest)
- from_account (string)
- to_account (string)
- amount (decimal)
- reason (text)
- policy_reference (string, nullable)
- created_at (datetime)

#### 5) Status changes
All lifecycle changes are recorded on `Event.status` with a descriptive `Event.description`. No separate status-history table is used.

#### 6) Event
- id (PK)
- event_type (string; fixed to "Dispatch" for this domain)
- description (text; human-readable summary of the action)
- status (string; one of: RequestCreated | RequestSubmitted | RequestReviewed | VehicleAssigned | Reserved | Dispatched | Returned | EditedRequested | EditApproved | EditRejected | Rejected | Cancelled | Contracted | Reimbursed | CommentAdded)
- user_id (FK → User, nullable)
- asset_id (FK → Asset, nullable)
- major_location_id (FK → MajorLocation, nullable)
- timestamp (datetime)

Notes:
- Events may be created without an `asset_id` (e.g., early request lifecycle). If `asset_id` is provided and `major_location_id` is not, the system auto-populates `major_location_id` from the asset.

#### 7) Comment
- Comments belong to `Event` (required `event_id`).
- Policy: every update that changes status or important fields generates a Comment summarizing the change (who, what, when, why).

#### 8) Attachment
- Files are stored as `Attachment` rows and linked to a Comment via `CommentAttachment` (virtual attachment reference).
- Attachments are not linked directly to Events; to attach files to an Event, create a Comment and attach files to that Comment.

### Enumerations
- DispatchRequest.status: Draft, Submitted, UnderReview, Reserved, Dispatched, Completed, Rejected, Cancelled
- Dispatch.status: Planned, Active, EditedPendingApproval, Completed, Cancelled
- resolution_type: Internal, Contracted, Reimbursement
- dispatch_scope: Onsite, Local, Regional, Interstate, Continental
- event_type: as listed above

### Relationships
- DispatchRequest (detail) 1—1 Event (the Request is represented as an Event detail record)
- Dispatch (detail) 1—1 Event (each significant action like Reserve/Dispatch may create its own Event detail record or reuse the primary Dispatch Event per design choice)
- DispatchRequest 1—0..1 Dispatch (Internal fulfillment path)
- DispatchRequest 1—0..1 ContractDetails (Contracted path)
- DispatchRequest 1—0..1 ReimbursementDetails (Self-dispatch path)
- Event 1—* Comment
- Comment 1—* CommentAttachment → Attachment

### State Transitions (Conceptual)

DispatchRequest:
- Draft → Submitted (Requester)
- Submitted → UnderReview (System/Dispatcher)
- UnderReview → Reserved (Dispatcher)
- Reserved → Dispatched (Dispatcher)
- Dispatched → Completed (Dispatcher/System on check-in)
- UnderReview → Rejected (Dispatcher)
- Any non-terminal → Cancelled (Requester/Dispatcher per policy)
- UnderReview → Contracted (Dispatcher) [resolution_type=Contracted]
- UnderReview → Reimbursement (Dispatcher) [resolution_type=Reimbursement]

Dispatch:
- Planned → Active (Check-out)
- Active → Completed (Check-in)
- Planned|Active → EditedPendingApproval (Requester change requiring approval)
- EditedPendingApproval → Planned|Active (Dispatcher approves)
- EditedPendingApproval → unchanged (Dispatcher rejects)
- Planned|Active → Cancelled (Dispatcher)

### Validation Rules
- Date coherence: end ≥ start on all schedules and actuals
- Overlap prevention: a single asset cannot have overlapping Planned/Active windows
- Meter monotonicity: meter_end ≥ meter_start
- Required fields per transition: e.g., ContractDetails required for Contracted; ReimbursementDetails required for Reimbursement
- Authorization gates: role-based per transition

### Derived Data and Projections
- Current status per entity derived from latest relevant Event.status
- Utilization metrics by Asset/AssetType based on Dispatch actuals
- SLA metrics from Event timestamps (e.g., time from Submitted to Reserved)

### Open Questions
- Approval thresholds for contracted/reimbursement (amount-based?)
- Lead time buffers or blackout windows per AssetType
- Multi-capacity assets supported or strictly capacity=1?


