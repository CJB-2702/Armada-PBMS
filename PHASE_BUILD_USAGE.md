# Phase Build Usage Guide

## Overview

The Asset Management System now supports phased builds, allowing you to build specific phases of the system based on your needs. This is useful for development, testing, and deployment scenarios.

## Build Phases

### Phase 1: Core Foundation
- **Phase 1A**: Core Foundation Tables (User, Asset, AssetType, MakeModel, etc.)
- **Phase 1B**: Core System Initialization (System user, admin user, initial data)

### Phase 2: Asset Detail Tables
- Asset detail table infrastructure
- Purchase information tables
- Vehicle registration tables
- Model detail tables
- Detail table sets and relationships

### Phase 3: Maintenance & Operations (Future)
- Maintenance event models
- Work order system
- Part tracking

### Phase 4: Advanced Features (Future)
- Advanced reporting
- Integration features
- Extended functionality

## Usage

### Command Line Options

#### Build Phase 1 Only
```bash
python app.py --phase1
```
This builds only the core foundation tables and system initialization.

#### Build Phase 1 and Phase 2
```bash
python app.py --phase2
```
This builds Phase 1 (core foundation) plus Phase 2 (asset detail tables).

#### Build All Phases (Default)
```bash
python app.py
```
This builds all available phases (currently Phase 1 and Phase 2).

#### Build Only (No Web Server)
```bash
python app.py --phase1 --build-only
python app.py --phase2 --build-only
python app.py --build-only
```
This builds the database and exits without starting the web server.

### Programmatic Usage

You can also use the build system programmatically:

```python
from app.build import build_database

# Build Phase 1 only
build_database(build_phase='phase1')

# Build Phase 1 and Phase 2
build_database(build_phase='phase2')

# Build all phases
build_database(build_phase='all')
```

## Build Flow

### Phase 1 Build Flow
1. **Phase 1A**: Create core database tables
   - User table
   - Asset table
   - AssetType table
   - MakeModel table
   - MajorLocation table
   - Event table

2. **Phase 1B**: Initialize system data
   - Create system user
   - Create admin user
   - Seed initial data
   - Verify table creation

### Phase 2 Build Flow
1. **Phase 1**: Complete Phase 1 build first
2. **Phase 2A**: Create asset detail table infrastructure
   - Detail table virtual templates
   - Asset detail base classes
   - Model detail base classes

3. **Phase 2B**: Create specific detail tables
   - Purchase information tables
   - Vehicle registration tables
   - Model detail tables
   - Detail table sets

4. **Phase 2C**: Initialize detail table data
   - Create sample detail table sets
   - Verify relationships
   - Test data integrity

## Testing

You can test the phase build functionality using the provided test script:

```bash
python test_phase_build.py
```

This will test all three build modes and report success or failure for each.

## Error Handling

The build system includes comprehensive error handling:

- **Phase Dependencies**: Each phase automatically includes its dependencies
- **Rollback**: If any phase fails, the build stops and reports the error
- **Verification**: Each phase includes verification steps to ensure proper creation
- **Logging**: Detailed logging of all build steps and results

## Development Workflow

### For Phase 1 Development
```bash
python app.py --phase1 --build-only
```

### For Phase 2 Development
```bash
python app.py --phase2 --build-only
```

### For Full System Testing
```bash
python app.py --build-only
```

### For Production Deployment
```bash
python app.py
```

## Notes

- **Dependencies**: Phase 2 automatically includes Phase 1, Phase 3 will include Phase 1 and 2, etc.
- **Database**: Each build phase can be run multiple times safely
- **Data**: Initial data is only created once per phase
- **Performance**: Phase 1 builds are faster than full builds
- **Testing**: Use `--build-only` for CI/CD pipelines and testing

## Future Enhancements

- **Phase 3**: Maintenance and operations tables
- **Phase 4**: Advanced features and integrations
- **Selective Builds**: Build specific components within phases
- **Migration Support**: Database migration between phases
- **Configuration**: Phase-specific configuration options 