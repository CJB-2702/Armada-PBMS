# Build System Quick Reference

## Quick Commands

### Build Models Only
```bash
# Phase 1 models only
python -c "from app.build import build_database; build_database(build_phase='phase1', data_phase='none')"

# Phase 1 + Phase 2 models
python -c "from app.build import build_database; build_database(build_phase='phase2', data_phase='none')"

# All models
python -c "from app.build import build_database; build_database(build_phase='all', data_phase='none')"
```

### Insert Data Only
```bash
# Phase 1 data only
python -c "from app.build import build_database; build_database(build_phase='none', data_phase='phase1')"

# Phase 1 + Phase 2 data
python -c "from app.build import build_database; build_database(build_phase='none', data_phase='phase2')"

# All data
python -c "from app.build import build_database; build_database(build_phase='none', data_phase='all')"
```

### Complete Builds
```bash
# Phase 1 complete (models + data)
python -c "from app.build import build_database; build_database(build_phase='phase1', data_phase='phase1')"

# Phase 2 complete (models + data)
python -c "from app.build import build_database; build_database(build_phase='phase2', data_phase='phase2')"

# Everything
python -c "from app.build import build_database; build_database(build_phase='all', data_phase='all')"
```

### Convenience Functions
```bash
# Build models only
python -c "from app.build import build_models_only; build_models_only('phase1')"
python -c "from app.build import build_models_only; build_models_only('phase2')"
python -c "from app.build import build_models_only; build_models_only('all')"

# Insert data only
python -c "from app.build import insert_data_only; insert_data_only('phase1')"
python -c "from app.build import insert_data_only; insert_data_only('phase2')"
python -c "from app.build import insert_data_only; insert_data_only('all')"
```

## Phase Summary

| Phase | Models | Data | Description |
|-------|--------|------|-------------|
| 1A | ✅ | ❌ | Core Foundation Tables |
| 1B | ❌ | ✅ | Core System Initialization |
| 2A | ✅ | ❌ | Asset Detail Tables |
| 2B | ❌ | ✅ | Asset Detail Data |

## Verification Commands

### Check Tables
```python
from app.models.build import verify_all_tables
verify_all_tables()
```

### Show Summary
```python
from app.models.build import show_build_summary
show_build_summary()
```

### Test Phase 2
```bash
python phase_2/test_phase2.py
```

## Common Workflows

### Development Workflow
1. **Build Phase 1 models**: `build_phase='phase1', data_phase='none'`
2. **Add core data**: `build_phase='none', data_phase='phase1'`
3. **Build Phase 2 models**: `build_phase='phase2', data_phase='none'`
4. **Add detail data**: `build_phase='none', data_phase='phase2'`
5. **Test**: `python phase_2/test_phase2.py`

### Testing Workflow
1. **Build models only**: `build_phase='phase2', data_phase='none'`
2. **Test schema**: Verify tables exist
3. **Add test data**: `build_phase='none', data_phase='phase2'`
4. **Run tests**: `python phase_2/test_phase2.py`

### Production Workflow
1. **Build all models**: `build_phase='all', data_phase='none'`
2. **Verify schema**: `verify_all_tables()`
3. **Add production data**: `build_phase='none', data_phase='all'`
4. **Final verification**: `show_build_summary()`

## Error Recovery

### If Model Build Fails
```bash
# Check what tables exist
python -c "from app import db; inspector = db.inspect(db.engine); print(inspector.get_table_names())"

# Rebuild from scratch
python -c "from app.build import build_database; build_database(build_phase='phase1', data_phase='none')"
```

### If Data Insertion Fails
```bash
# Check if required data exists
python -c "from app.models.core.user import User; print(User.query.all())"

# Reinsert data only
python -c "from app.build import build_database; build_database(build_phase='none', data_phase='phase1')"
```

## Build Parameters Reference

### build_phase Options
- `'none'`: Skip model building
- `'phase1'`: Core Foundation Tables only
- `'phase2'`: Core + Asset Detail Tables
- `'all'`: All phases (default)

### data_phase Options
- `'none'`: Skip data insertion
- `'phase1'`: Core System Initialization only
- `'phase2'`: Core + Asset Detail Data
- `'all'`: All phases (default) 