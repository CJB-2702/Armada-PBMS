# Armada PBMS Tests

This directory contains tests for the Armada PBMS application.

## Test Structure

- `test_app_initialization.py` - Tests that verify the app initializes correctly and inserts all required data

## Running Tests

### Option 1: Using the test runner script
```bash
cd tests
python run_tests.py
```

### Option 2: Using pytest directly
```bash
# From the project root
pytest tests/ -v

# Or from the tests directory
pytest test_app_initialization.py -v
```

### Option 3: Using the Makefile (if available)
```bash
make test
```

## Test Coverage

The current tests cover:

1. **App Initialization**
   - App creation without errors
   - Database table creation
   - Required data insertion

2. **User Data**
   - SYSTEM user (row_id 0)
   - Admin user (row_id 1)
   - User count verification

3. **Asset Types**
   - Vehicle asset type insertion
   - Asset type count verification

4. **Statuses**
   - Required statuses (active, inactive, maintenance, retired)
   - Status count verification

5. **Locations**
   - SYSTEM location creation
   - Location count verification

6. **Events**
   - Event types insertion
   - Initial system events
   - Event count verification

7. **Vehicle-Specific Data**
   - Meter types from JSON file
   - Vehicle asset type
   - Vehicle tables creation
   - Config verification

## Test Database

Tests use a temporary SQLite database that is automatically created and cleaned up after each test. This ensures tests don't interfere with each other or with your development database.

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_*.py`
2. Use descriptive test method names
3. Include proper assertions with meaningful error messages
4. Use the `app` fixture for database access
5. Use the `client` fixture for HTTP request testing

## Dependencies

Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

Or install them individually:
```bash
pip install pytest pytest-cov pytest-flask
``` 