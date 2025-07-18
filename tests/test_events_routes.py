import pytest
from flask import Flask
from flask_login import LoginManager
from app import create_app
from app.models.BaseModels.Event import Event, EventTypes
from app.models.BaseModels.Users import User
from app.models.BaseModels.Locations import MajorLocation
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def auth_client(app, client):
    """Create a test client with authentication"""
    with app.app_context():
        # Create test user
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
        
        # Login user
        with client.session_transaction() as sess:
            sess['user_id'] = user.row_id
            sess['_fresh'] = True
        
        return client

@pytest.fixture
def admin_client(app, client):
    """Create a test client with admin authentication"""
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            display_name='Admin User',
            role='admin',
            created_by=0
        )
        db.session.add(admin)
        db.session.commit()
        
        # Login admin
        with client.session_transaction() as sess:
            sess['user_id'] = admin.row_id
            sess['_fresh'] = True
        
        return client

@pytest.fixture
def sample_event_types(app):
    """Create sample event types"""
    with app.app_context():
        event_types = [
            EventTypes(value='System', description='System events', created_by=0),
            EventTypes(value='General', description='General events', created_by=0),
            EventTypes(value='Maintenance', description='Maintenance events', created_by=0)
        ]
        for event_type in event_types:
            db.session.add(event_type)
        db.session.commit()
        return event_types

@pytest.fixture
def sample_locations(app):
    """Create sample locations"""
    with app.app_context():
        locations = [
            MajorLocation(UID='SYSTEM', common_name='System Location', description='System location', status='active', created_by=0),
            MajorLocation(UID='LOC1', common_name='Location 1', description='Test location 1', status='active', created_by=0)
        ]
        for location in locations:
            db.session.add(location)
        db.session.commit()
        return locations

@pytest.fixture
def sample_events(app, sample_event_types, sample_locations):
    """Create sample events"""
    with app.app_context():
        events = [
            Event(
                title='Test Event 1',
                description='Test event description',
                event_type='System',
                status='completed',
                location_UID='SYSTEM',
                created_by=0
            ),
            Event(
                title='Test Event 2',
                description='Another test event',
                event_type='General',
                status='pending',
                location_UID='LOC1',
                created_by=0
            )
        ]
        for event in events:
            db.session.add(event)
        db.session.commit()
        return events

class TestEventsRoutes:
    """Test cases for events routes"""
    
    def test_index_requires_auth(self, client):
        """Test that events index requires authentication"""
        response = client.get('/events/')
        assert response.status_code == 302  # Redirect to login
    
    def test_index_with_auth(self, auth_client, sample_events):
        """Test events index with authentication"""
        response = auth_client.get('/events/')
        assert response.status_code == 200
        assert b'Test Event 1' in response.data
        assert b'Test Event 2' in response.data
    
    def test_view_event_requires_auth(self, client):
        """Test that viewing an event requires authentication"""
        response = client.get('/events/1')
        assert response.status_code == 302  # Redirect to login
    
    def test_view_event_with_auth(self, auth_client, sample_events):
        """Test viewing an event with authentication"""
        response = auth_client.get('/events/1')
        assert response.status_code == 200
        assert b'Test Event 1' in response.data
    
    def test_view_nonexistent_event(self, auth_client):
        """Test viewing a non-existent event"""
        response = auth_client.get('/events/999')
        assert response.status_code == 404
    
    def test_create_event_requires_auth(self, client):
        """Test that creating an event requires authentication"""
        response = client.get('/events/create')
        assert response.status_code == 302  # Redirect to login
    
    def test_create_event_form(self, auth_client, sample_event_types, sample_locations):
        """Test create event form display"""
        response = auth_client.get('/events/create')
        assert response.status_code == 200
        assert b'Create Event' in response.data
    
    def test_create_event_valid_data(self, auth_client, sample_event_types, sample_locations):
        """Test creating an event with valid data"""
        data = {
            'title': 'New Test Event',
            'description': 'New event description',
            'event_type': 'System',
            'status': 'pending',
            'location_UID': 'SYSTEM'
        }
        response = auth_client.post('/events/create', data=data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check if event was created
        with auth_client.application.app_context():
            event = Event.query.filter_by(title='New Test Event').first()
            assert event is not None
            assert event.description == 'New event description'
    
    def test_create_event_invalid_data(self, auth_client, sample_event_types, sample_locations):
        """Test creating an event with invalid data"""
        data = {
            'title': '',  # Empty title
            'description': 'Test description',
            'event_type': 'System',
            'status': 'pending',
            'location_UID': 'SYSTEM'
        }
        response = auth_client.post('/events/create', data=data)
        assert response.status_code == 200
        assert b'Title is required' in response.data
    
    def test_create_event_invalid_event_type(self, auth_client, sample_event_types, sample_locations):
        """Test creating an event with invalid event type"""
        data = {
            'title': 'Test Event',
            'description': 'Test description',
            'event_type': 'InvalidType',
            'status': 'pending',
            'location_UID': 'SYSTEM'
        }
        response = auth_client.post('/events/create', data=data)
        assert response.status_code == 200
        assert b'Invalid event type' in response.data
    
    def test_edit_event_requires_auth(self, client):
        """Test that editing an event requires authentication"""
        response = client.get('/events/1/edit')
        assert response.status_code == 302  # Redirect to login
    
    def test_edit_event_form(self, auth_client, sample_events):
        """Test edit event form display"""
        response = auth_client.get('/events/1/edit')
        assert response.status_code == 200
        assert b'Edit Event' in response.data
    
    def test_edit_event_valid_data(self, auth_client, sample_events):
        """Test editing an event with valid data"""
        data = {
            'title': 'Updated Event Title',
            'description': 'Updated description',
            'event_type': 'General',
            'status': 'completed',
            'location_UID': 'SYSTEM'
        }
        response = auth_client.post('/events/1/edit', data=data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check if event was updated
        with auth_client.application.app_context():
            event = Event.query.get(1)
            assert event.title == 'Updated Event Title'
            assert event.description == 'Updated description'
    
    def test_delete_event_requires_auth(self, client):
        """Test that deleting an event requires authentication"""
        response = client.post('/events/1/delete')
        assert response.status_code == 302  # Redirect to login
    
    def test_delete_event_success(self, auth_client, sample_events):
        """Test deleting an event successfully"""
        response = auth_client.post('/events/1/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Check if event was deleted
        with auth_client.application.app_context():
            event = Event.query.get(1)
            assert event is None
    
    def test_delete_event_nonexistent(self, auth_client):
        """Test deleting a non-existent event"""
        response = auth_client.post('/events/999/delete', follow_redirects=True)
        assert response.status_code == 404

class TestEventTypesRoutes:
    """Test cases for event types routes"""
    
    def test_event_types_index_requires_auth(self, client):
        """Test that event types index requires authentication"""
        response = client.get('/events/event-types')
        assert response.status_code == 302  # Redirect to login
    
    def test_event_types_index_with_auth(self, auth_client, sample_event_types):
        """Test event types index with authentication"""
        response = auth_client.get('/events/event-types')
        assert response.status_code == 200
        assert b'System' in response.data
        assert b'General' in response.data
    
    def test_create_event_type_requires_admin(self, auth_client):
        """Test that creating event types requires admin privileges"""
        response = auth_client.get('/events/event-types/create')
        assert response.status_code == 302  # Redirect with error
    
    def test_create_event_type_admin(self, admin_client):
        """Test creating event type as admin"""
        data = {
            'value': 'NewType',
            'description': 'New event type description'
        }
        response = admin_client.post('/events/event-types/create', data=data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check if event type was created
        with admin_client.application.app_context():
            event_type = EventTypes.query.filter_by(value='NewType').first()
            assert event_type is not None
            assert event_type.description == 'New event type description'
    
    def test_create_event_type_duplicate(self, admin_client, sample_event_types):
        """Test creating duplicate event type"""
        data = {
            'value': 'System',  # Already exists
            'description': 'Duplicate description'
        }
        response = admin_client.post('/events/event-types/create', data=data)
        assert response.status_code == 200
        assert b'already exists' in response.data
    
    def test_edit_event_type_requires_admin(self, auth_client, sample_event_types):
        """Test that editing event types requires admin privileges"""
        response = auth_client.get('/events/event-types/1/edit')
        assert response.status_code == 302  # Redirect with error
    
    def test_edit_event_type_admin(self, admin_client, sample_event_types):
        """Test editing event type as admin"""
        data = {
            'value': 'UpdatedType',
            'description': 'Updated description'
        }
        response = admin_client.post('/events/event-types/1/edit', data=data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check if event type was updated
        with admin_client.application.app_context():
            event_type = EventTypes.query.get(1)
            assert event_type.value == 'UpdatedType'
            assert event_type.description == 'Updated description'
    
    def test_delete_event_type_requires_admin(self, auth_client, sample_event_types):
        """Test that deleting event types requires admin privileges"""
        response = auth_client.post('/events/event-types/1/delete')
        assert response.status_code == 302  # Redirect with error
    
    def test_delete_event_type_admin(self, admin_client, sample_event_types):
        """Test deleting event type as admin"""
        response = admin_client.post('/events/event-types/1/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Check if event type was deleted
        with admin_client.application.app_context():
            event_type = EventTypes.query.get(1)
            assert event_type is None

class TestInputValidation:
    """Test cases for input validation"""
    
    def test_sanitize_input(self, auth_client):
        """Test input sanitization"""
        from app.routes.events import sanitize_input
        
        # Test basic sanitization
        assert sanitize_input('<script>alert("xss")</script>') == 'scriptalert(xss)/script'
        assert sanitize_input('  test  ') == 'test'
        assert sanitize_input('') == ''
        assert sanitize_input(None) is None
    
    def test_validate_event_data(self, auth_client):
        """Test event data validation"""
        from app.routes.events import validate_event_data
        
        # Test valid data
        errors = validate_event_data('Valid Title', 'Valid description', 'System', 'pending', 'SYSTEM')
        assert len(errors) == 0
        
        # Test invalid title
        errors = validate_event_data('', 'Valid description', 'System', 'pending', 'SYSTEM')
        assert 'Title is required' in errors
        
        # Test title too long
        long_title = 'A' * 256
        errors = validate_event_data(long_title, 'Valid description', 'System', 'pending', 'SYSTEM')
        assert 'Title must be less than 255 characters' in errors
        
        # Test invalid status
        errors = validate_event_data('Valid Title', 'Valid description', 'System', 'invalid_status', 'SYSTEM')
        assert 'Invalid status' in errors 