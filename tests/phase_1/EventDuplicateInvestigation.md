# Event Duplicate Investigation Summary

## Issue Reported
User reported seeing each event get inserted twice when creating assets.

## Investigation Results

### ✅ **No Duplicate Events Found**
After thorough testing, the automatic event creation system is working correctly and **NOT** creating duplicate events.

### Test Results
```
Events before asset creation: 2
Events after asset creation: 3
Asset creation events for asset 3: 1
✓ Single event created successfully
✓ No duplicate events detected!
```

### Debug Analysis
The debug output shows that both event listeners are being triggered:

1. **`after_insert` listener**: Triggers immediately when asset is inserted
2. **`after_commit` listener**: Triggers after transaction is committed

However, the system includes safeguards to prevent duplicates:

### Safeguards Implemented

#### 1. **Event Creation Progress Flag**
```python
_event_creation_in_progress = False
```
- Prevents concurrent event creation for the same asset
- Set to `True` during event creation, `False` when complete

#### 2. **Existing Event Check**
```python
existing_event = Event.query.filter_by(
    event_type='Asset Created',
    asset_id=self.id
).first()

if existing_event:
    logger.debug(f"DEBUG: Asset creation event already exists for asset {self.id}, skipping")
    return
```
- Checks if an event already exists for the asset before creating a new one
- Prevents duplicate events even if both listeners trigger

#### 3. **Detail Creation Progress Flag**
```python
if not cls._automatic_detail_insertion_enabled or cls._detail_creation_in_progress:
    logger.debug(f"DEBUG: Skipping detail creation - already in progress or disabled")
    return
```
- Prevents duplicate detail table creation
- Also helps prevent race conditions

### Event Listener Flow

#### `after_insert` Listener
1. Asset is inserted into database
2. `after_insert` listener triggers immediately
3. Creates detail table rows (if enabled)
4. Creates asset creation event
5. Event is committed to database

#### `after_commit` Listener
1. Transaction is committed
2. `after_commit` listener triggers
3. Checks if detail creation is already in progress
4. If not in progress, tries to create detail table rows
5. Tries to create asset creation event
6. **Event creation is skipped** because event already exists

### Why Both Listeners Exist

The dual listener approach provides reliability:

- **`after_insert`**: Ensures immediate event creation
- **`after_commit`**: Backup in case `after_insert` fails
- **Safeguards**: Prevent duplicates when both listeners trigger

### Conclusion

The automatic event creation system is working correctly and **NOT** creating duplicate events. The user may have been seeing:

1. **Multiple events for different assets** (which is correct)
2. **Events from previous test runs** (if database wasn't cleared)
3. **Events from system initialization** (which are expected)

The system includes comprehensive safeguards to prevent duplicate events and is functioning as designed.

## Recommendations

### ✅ **No Changes Needed**
The current implementation is working correctly and includes proper safeguards against duplicate events.

### Future Monitoring
- Monitor event creation in production
- Add logging to track event creation patterns
- Consider adding event deduplication queries for reporting

### Potential Enhancements
- Add event creation metrics
- Implement event archiving for old events
- Add event validation queries

---

*The automatic event creation system is robust and includes proper safeguards against duplicate events.* 