import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from app.models.BaseModels import insert_initial_data, load_json_data, validate_data_structure
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'test_data': [
                {'id': 1, 'name': 'Test 1', 'value': 100},
                {'id': 2, 'name': 'Test 2', 'value': 200}
            ]
        }, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)

class TestLoadJsonData:
    """Test cases for load_json_data function"""
    
    def test_load_json_data_success(self, temp_json_file):
        """Test successful JSON file loading"""
        data = load_json_data(os.path.basename(temp_json_file))
        assert 'test_data' in data
        assert len(data['test_data']) == 2
        assert data['test_data'][0]['name'] == 'Test 1'
    
    def test_load_json_data_file_not_found(self):
        """Test loading non-existent JSON file"""
        with pytest.raises(FileNotFoundError):
            load_json_data('nonexistent.json')
    
    def test_load_json_data_invalid_json(self):
        """Test loading invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_json_data(os.path.basename(temp_file))
        finally:
            os.unlink(temp_file)

class TestValidateDataStructure:
    """Test cases for validate_data_structure function"""
    
    def test_validate_data_structure_valid(self):
        """Test validation with valid data structure"""
        data = [
            {'id': 1, 'name': 'Test 1', 'value': 100},
            {'id': 2, 'name': 'Test 2', 'value': 200}
        ]
        required_fields = ['id', 'name', 'value']
        
        # Should not raise any exception
        validate_data_structure(data, required_fields, 'Test Data')
    
    def test_validate_data_structure_not_list(self):
        """Test validation with non-list data"""
        data = {'id': 1, 'name': 'Test'}
        required_fields = ['id', 'name']
        
        with pytest.raises(ValueError, match='Test Data data must be a list'):
            validate_data_structure(data, required_fields, 'Test Data')
    
    def test_validate_data_structure_item_not_dict(self):
        """Test validation with non-dict items"""
        data = [{'id': 1, 'name': 'Test'}, 'not a dict']
        required_fields = ['id', 'name']
        
        with pytest.raises(ValueError, match='Test Data item 1 must be a dictionary'):
            validate_data_structure(data, required_fields, 'Test Data')
    
    def test_validate_data_structure_missing_field(self):
        """Test validation with missing required fields"""
        data = [
            {'id': 1, 'name': 'Test 1'},
            {'id': 2, 'name': 'Test 2', 'value': 200}
        ]
        required_fields = ['id', 'name', 'value']
        
        with pytest.raises(ValueError, match='Test Data item 0 missing required field: value'):
            validate_data_structure(data, required_fields, 'Test Data')

class TestInsertInitialData:
    """Test cases for insert_initial_data function"""
    
    @patch('app.models.BaseModels.load_json_data')
    def test_insert_initial_data_success(self, mock_load_json, app):
        """Test successful initial data insertion"""
        # Mock JSON data
        mock_load_json.side_effect = [
            {'required_statuses': [
                {'row_id': 0, 'name': 'active', 'description': 'Active status', 'created_by': 0},
                {'row_id': 1, 'name': 'inactive', 'description': 'Inactive status', 'created_by': 0}
            ]},
            {'initial_events': [
                {'row_id': 0, 'title': 'Test Event', 'description': 'Test', 'event_type': 'System', 'status': 'Completed', 'location_UID': 'SYSTEM', 'created_by': 0}
            ]}
        ]
        
        # Mock required data from models
        with patch('app.models.BaseModels.required_users') as mock_users, \
             patch('app.models.BaseModels.required_asset_types') as mock_asset_types, \
             patch('app.models.BaseModels.required_system_locations') as mock_locations, \
             patch('app.models.BaseModels.required_event_types') as mock_event_types:
            
            mock_users.__iter__ = lambda x: iter([
                {'row_id': 0, 'username': 'SYSTEM', 'email': 'system@null.null', 'is_admin': True, 'display_name': 'System', 'role': 'admin', 'created_by': 0},
                {'row_id': 1, 'username': 'admin', 'email': 'admin@null.com', 'is_admin': True, 'display_name': 'Admin', 'role': 'admin', 'created_by': 0}
            ])
            mock_asset_types.__iter__ = lambda x: iter([
                {'row_id': 0, 'name': 'System', 'description': 'System assets', 'created_by': 0},
                {'row_id': 1, 'name': 'General', 'description': 'General assets', 'created_by': 0}
            ])
            mock_locations.__iter__ = lambda x: iter([
                {'row_id': 0, 'UID': 'SYSTEM', 'common_name': 'System Location', 'description': 'System location', 'status': 'active', 'created_by': 0}
            ])
            mock_event_types.__iter__ = lambda x: iter([
                {'row_id': 0, 'name': 'System', 'description': 'System events', 'created_by': 0},
                {'row_id': 1, 'name': 'General', 'description': 'General events', 'created_by': 0}
            ])
            
            # Should not raise any exception
            insert_initial_data(app)
    
    @patch('app.models.BaseModels.load_json_data')
    def test_insert_initial_data_json_error(self, mock_load_json, app):
        """Test initial data insertion with JSON loading error"""
        mock_load_json.side_effect = FileNotFoundError("JSON file not found")
        
        with pytest.raises(FileNotFoundError):
            insert_initial_data(app)
    
    @patch('app.models.BaseModels.load_json_data')
    def test_insert_initial_data_validation_error(self, mock_load_json, app):
        """Test initial data insertion with validation error"""
        # Mock JSON data with invalid structure
        mock_load_json.side_effect = [
            {'required_statuses': 'not a list'},  # Invalid structure
            {'initial_events': []}
        ]
        
        # Mock required data from models
        with patch('app.models.BaseModels.required_users') as mock_users, \
             patch('app.models.BaseModels.required_asset_types') as mock_asset_types, \
             patch('app.models.BaseModels.required_system_locations') as mock_locations, \
             patch('app.models.BaseModels.required_event_types') as mock_event_types:
            
            mock_users.__iter__ = lambda x: iter([])
            mock_asset_types.__iter__ = lambda x: iter([])
            mock_locations.__iter__ = lambda x: iter([])
            mock_event_types.__iter__ = lambda x: iter([])
            
            with pytest.raises(ValueError, match='Statuses data must be a list'):
                insert_initial_data(app)
    
    @patch('app.models.BaseModels.load_json_data')
    def test_insert_initial_data_database_error(self, mock_load_json, app):
        """Test initial data insertion with database error"""
        # Mock JSON data
        mock_load_json.side_effect = [
            {'required_statuses': [
                {'row_id': 0, 'name': 'active', 'description': 'Active status', 'created_by': 0}
            ]},
            {'initial_events': []}
        ]
        
        # Mock required data from models
        with patch('app.models.BaseModels.required_users') as mock_users, \
             patch('app.models.BaseModels.required_asset_types') as mock_asset_types, \
             patch('app.models.BaseModels.required_system_locations') as mock_locations, \
             patch('app.models.BaseModels.required_event_types') as mock_event_types:
            
            mock_users.__iter__ = lambda x: iter([
                {'row_id': 0, 'username': 'SYSTEM', 'email': 'system@null.null', 'is_admin': True, 'display_name': 'System', 'role': 'admin', 'created_by': 0}
            ])
            mock_asset_types.__iter__ = lambda x: iter([])
            mock_locations.__iter__ = lambda x: iter([])
            mock_event_types.__iter__ = lambda x: iter([])
            
            # Mock database error
            with patch.object(db.session, 'execute', side_effect=Exception("Database error")):
                with pytest.raises(Exception, match="Database error"):
                    insert_initial_data(app)
    
    @patch('app.models.BaseModels.load_json_data')
    def test_insert_initial_data_transaction_rollback(self, mock_load_json, app):
        """Test that transaction is rolled back on error"""
        # Mock JSON data
        mock_load_json.side_effect = [
            {'required_statuses': [
                {'row_id': 0, 'name': 'active', 'description': 'Active status', 'created_by': 0}
            ]},
            {'initial_events': []}
        ]
        
        # Mock required data from models
        with patch('app.models.BaseModels.required_users') as mock_users, \
             patch('app.models.BaseModels.required_asset_types') as mock_asset_types, \
             patch('app.models.BaseModels.required_system_locations') as mock_locations, \
             patch('app.models.BaseModels.required_event_types') as mock_event_types:
            
            mock_users.__iter__ = lambda x: iter([
                {'row_id': 0, 'username': 'SYSTEM', 'email': 'system@null.null', 'is_admin': True, 'display_name': 'System', 'role': 'admin', 'created_by': 0}
            ])
            mock_asset_types.__iter__ = lambda x: iter([])
            mock_locations.__iter__ = lambda x: iter([])
            mock_event_types.__iter__ = lambda x: iter([])
            
            # Mock database error after some successful inserts
            call_count = 0
            def mock_execute(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count > 2:  # Fail after 2 successful inserts
                    raise Exception("Database error")
                return MagicMock()
            
            with patch.object(db.session, 'execute', side_effect=mock_execute), \
                 patch.object(db.session, 'rollback') as mock_rollback:
                
                with pytest.raises(Exception, match="Database error"):
                    insert_initial_data(app)
                
                # Verify rollback was called
                mock_rollback.assert_called_once()

class TestDataVerification:
    """Test cases for data verification"""
    
    def test_verify_data_inserted_success(self, app):
        """Test successful data verification"""
        from app.models.BaseModels.verify_data_inserted
        from app.models.BaseModels.Users import User
        
        # Create test user
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                is_admin=False,
                display_name='Test User',
                role='user',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
            
            # Verify data was inserted
            result = verify_data_inserted(User, 1, "Test Users")
            assert result is True
    
    def test_verify_data_inserted_failure(self, app):
        """Test data verification failure"""
        from app.models.BaseModels.verify_data_inserted
        from app.models.BaseModels.Users import User
        
        with app.app_context():
            # Verify data was not inserted (expecting 1, but 0 exist)
            result = verify_data_inserted(User, 1, "Test Users")
            assert result is False 