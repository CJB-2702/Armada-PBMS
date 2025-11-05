## Dispatching Design (Design-Only)

This document describes the intended behavior, workflows, and UX for the Dispatching domain. It is design-only and does not change any application code.

### Objectives
- Allow users to request dispatches with minimal friction and clear guidance.
- Provide dispatchers with a powerful queue and resource calendar to select the best option.
- Support alternative fulfillment paths: contracted dispatch and self-dispatch with reimbursement.
- Ensure strong auditability via events, status history, and comments.
- Enable reporting on utilization, SLAs, and outcomes.

### Roles and Permissions
- Requester: create/edit drafts, submit requests, cancel before review; receive notifications.
- Dispatcher: triage queue, filter/search, reserve/dispatch/reject, approve/decline edits, set resolution types; override conflicts with reason.
- Fleet Manager: view dashboards, approve high-cost contracts/reimbursements per policy, adjust policies.

Authorization overview (policy-level):
- Transitions are gated by role; overrides require reasons; high-cost financial actions may require Fleet Manager approval.

### Key Concepts
- Dispatch Request: user-submitted demand including dates, scope, asset type, and notes.
- Dispatch: assignment of a specific asset over a time window, leading to check-out/in.
- Event: immutable log of actions and changes; source for audits and SLAs.
- Status History: structured timeline of status transitions for quick queries.
- Resolution Types: Internal (asset dispatched), Contracted, Reimbursement.

### Event Detail Architecture (EventDetailVirtual)
- Pattern: Request/Dispatch/Contract/Reimbursement are represented as Event detail records built on the `EventDetailVirtual` base.
- Core fields per detail record:
  - `event_id` (required): links the detail to its parent `Event`.
  - `all_details_id` (required): global sequence for all event detail tables (enables unified reporting across different detail types).
  - `asset_id` (optional): may be null for pre-assignment lifecycle events (e.g., request submitted).
- Creation mechanics:
  - Each detail class implements `create_event()`; when constructing a detail without an explicit `event_id`, it creates an `Event` via `Event.add_event(event_type="Dispatch", description=..., user_id=..., asset_id=optional)`.
  - If an `asset_id` is provided and `major_location_id` is omitted, `Event.__init__` auto-populates `major_location_id` from the asset.
- Status handling:
  - Lifecycle changes are reflected on `Event.status` (e.g., Reserved, Dispatched, Returned). No separate status-history table.
  - Human-readable rationale is placed in `Event.description`; structured diffs can be included in associated Comments.
- Comments & attachments:
  - Comments attach to the `Event` (`comment.event_id` is required).
  - Attachments are linked to Comments via `CommentAttachment`; to attach files to an Event, attach them to a Comment.


### Lifecycle & Status Model

Dispatch Request statuses
- Draft → Submitted → Under Review → Reserved → Dispatched → Completed
- Alternate endings: Rejected, Cancelled
- Alternate paths from Under Review: Contracted, Reimbursement

Dispatch statuses
- Planned → Active → Completed
- Edits: Planned|Active → Edited Pending Approval → Planned|Active
- Alternate ending: Cancelled

Transition rules (conceptual)
- Who can act: Requester (draft/submit/cancel); Dispatcher (review/reserve/dispatch/reject/cancel/approve edits); Fleet Manager (approve large $)
- Required data per transition: e.g., Contract details, Reimbursement details when chosen; reasons on reject/cancel/override

### Request Creation Flow (Requester)
- Form fields: desired start/end, number of people, names freeform (optional), asset type, asset subclass (controlled list with Other), dispatch scope (Onsite/Local/Regional/Interstate/Continental), estimated meter usage (optional), major location, notes.
- UX: progressive disclosure, validation prior to submit, save as draft, email confirmation upon submission.
- Accessibility: keyboard-first, clear error messages, labels and descriptions.

Implementation pattern (design-only):
- Construct a Request detail record (Event detail) without an explicit `event_id`; its `create_event()` will create the parent `Event` (no `asset_id` yet), set `event_type="Dispatch"`, populate `Event.status=RequestSubmitted`, and store the user's intent in the detail fields.
- Immediately add a Comment on the new Event summarizing the request.

### Dispatcher Console (Queue + Calendar)
- Layout: left 1/3 queue; right 2/3 resource calendar.
- Queue features: filters by location, model, equipment id, status; quick search; sort by urgency/date.
- On select: expand request details; highlight requested date range on calendar; lift available assets to top.
- Maintenance integration: show last maintenance event title/date and any blackout windows.
- Actions:
  - Reserve: hold an asset for the requested window; notify requester.
  - Reject: capture reason; notify requester.
  - Contract: open contract form (company, cost, reference, attachments); set resolution type; notify requester (pending approvals if required).
  - Reimbursement: open reimbursement form (accounts, amount, reason, receipt attachments); set resolution type; notify requester (pending approvals if required).
  - Dispatch: finalize assignment and move to Planned (or Active at check-out); notify requester.

### Resource Timeline (Gantt) Integration
- Library: vis-timeline (BSD-3, part of vis.js). Rationale: free, robust time range visualization with grouping, large-item performance, drag/resize.
- Data model for timeline (design-only):
  - Groups (assets):
    - id: asset id (int)
    - content: asset label (e.g., name, equipment id)
    - className: CSS class by asset type/status
  - Items (ranges):
    - id: event/detail id (int)
    - group: asset id
    - start: ISO datetime
    - end: ISO datetime
    - type: 'range'
    - className: 'dispatch-reserved' | 'dispatch-active' | 'maintenance' | 'blackout'
    - title: hover tooltip (requester, scope, location, last maintenance)
    - editable: { updateTime: role-based; override requires reason }
- Backend endpoints (JSON; windowed by date range):
  - GET /api/dispatching/assets?type=&location=&q=
  - GET /api/dispatching/timeline?start=ISO&end=ISO&assetType=&location=
    - returns { groups: [...], items: [...] }
- Interactions:
  - Select item → open detail drawer (request details, conflicts, maintenance info).
  - Drag/resize (dispatcher only) → propose edit; on drop, create EditedRequested event; approval flow updates detail and adds Comment.
  - Zoom, pan; filter by location, asset type, model, status.
- Styling/legend:
  - Reserved (info), Active (primary), Maintenance (warning), Blackout (muted/disabled). Legend present above the timeline.
- Performance:
  - Request only visible window; enable clustering; debounce filters; paginate groups for large fleets.
- Accessibility:
  - Keyboard selection and focus ring; high-contrast classes; ARIA labels on items.
- Auditability:
  - All timeline edits create Events with status and auto-generated Comments summarizing changes; attachments via Comment when applicable.

Event detail pattern per action (design-only):
- Reserve: create or update a Dispatch detail record (with `asset_id`), set `Event.status=Reserved`, and add a Comment summarizing selected asset/time window and any conflicts resolved.
- Reject: create an Event with `status=Rejected`, add Comment with required reason.
- Contract/Reimbursement: create detail records for ContractDetails/ReimbursementDetails linked to a new Event or the primary Request Event; set `Event.status` accordingly and add a Comment with financial summary; attach documents via Comment.
- Dispatch: create/update Dispatch detail with scheduled window and `asset_id`; set `Event.status=Dispatched` (or `Planned` if you prefer pre-check-out), and add a Comment.

### Edit and Change Management
- Edits that shorten the window (start later or end earlier): auto-apply with notification to dispatcher.
- Edits that expand the window (start earlier or end later): create an Edit Request requiring dispatcher approval.
- Diff view: show old vs new dates/scope; preserve comments; approval generates Event and StatusHistory entry.

Event detail alignment (design-only):
- Auto-apply (shorten window): create an Event with `status=EditApproved` and a Comment describing the delta; update the existing Dispatch detail accordingly.
- Expand window (requires approval): create an Event with `status=EditedRequested` and a Comment containing the requested change; on approval, another Event with `status=EditApproved` and an updated Dispatch detail; on rejection, `status=EditRejected` with Comment.

### Check-out / Check-in
- Check-out (start): capture actual_start, meter_start, verify asset availability; confirm operator.
- Check-in (return): capture actual_end, meter_end; compute usage delta; allow incident report (damage, breakdown, late return).
- Maintenance hooks: if meter delta or incident warrants, generate maintenance reminders or events.

Event detail alignment (design-only):
- Check-out: update Dispatch detail `actual_start` and `meter_start`; create Event with `status=Dispatched` (or `Active`) and add a Comment (operator, meter snapshot).
- Check-in: update Dispatch detail `actual_end` and `meter_end`; create Event with `status=Returned` (or `Completed`) and add a Comment including usage delta; attach any check-in photos via Comment.

### Scheduling Rules
- Availability: avoid overlapping reservations/dispatches for the same asset.
- Buffers: optional pre/post buffers per AssetType; configurable.
- Overrides: dispatcher may override conflicts with required reason and audit event.
- Calendar views: by asset type, by asset, by location; show maintenance blocks and holidays/blackouts.

### Contracted and Reimbursement Flows
- Contracted: decision criteria documented; require company, currency, amount, and reference; upload contract documents; approval tiers for high-cost contracts.
- Reimbursement: allowed scenarios, policy references, GL coding, required receipts, caps and rates; approval tiers for high amounts.

### Notifications & SLAs
- Triggers
  - Request submitted, reserved, dispatched, edited (requested/approved/rejected), rejected, cancelled, contracted, reimbursed, returned.
- SLAs
  - Target time from Submitted → Under Review
  - Target time from Under Review → Reserved/Decision
  - Escalation rules for items exceeding targets.

### Reporting & Metrics
- Utilization: by asset and asset type; time in Reserved/Active; on-time return rate.
- Throughput: counts by status, rejection reasons, contracted vs internal ratio.
- Meter analytics: average delta per dispatch; thresholds exceeded.
- SLA dashboards: time-to-first-touch, time-to-decision, aging in queue.

### Comments & Attachments
- Comments: threaded comments on Requests and Dispatches; mention users; notify participants.
- Attachments: receipts, contracts, check-in photos; typed with content type and stored path.

### Error Handling & Edge Cases
- Late returns and no-shows; requester withdrawal after reservation; asset becomes unavailable due to urgent maintenance; breakdown mid-dispatch → incident workflow to Maintenance.
- Idempotency: repeated action submissions should not duplicate events.

### Open Questions
- Approval thresholds and roles for large financial decisions.
- Multi-capacity assets support and how to represent capacity.
- Standard buffer policies per asset type/location.

### Diagram References
- See `Dispatch Model.canvas` for high-level nodes: Dispatch Request, Event, Comments, Contracted Dispatch, Dispatch Reimbursement, Check-in/out. Future work: state and sequence diagrams per workflow.


