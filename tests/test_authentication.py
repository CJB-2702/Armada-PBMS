import pytest
from flask import Flask
from flask_login import current_user
from werkzeug.security import generate_password_hash
from app import create_app
from app.models.BaseModels.Users import User
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
        # Create test user with password
        user = User(
            username='testuser',
            email='test@example.com',
            is_admin=False,
            display_name='Test User',
            role='user',
            created_by=0
        )
        user.set_password('TestPass123')
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
        # Create admin user with password
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            display_name='Admin User',
            role='admin',
            created_by=0
        )
        admin.set_password('AdminPass123')
        db.session.add(admin)
        db.session.commit()
        
        # Login admin
        with client.session_transaction() as sess:
            sess['user_id'] = admin.row_id
            sess['_fresh'] = True
        
        return client

class TestUserModel:
    """Test cases for User model authentication methods"""
    
    def test_user_creation_with_password(self, app):
        """Test creating a user with password"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='TestPass123',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.password_hash is not None
            assert user.check_password('TestPass123')
            assert not user.check_password('wrongpassword')
    
    def test_password_validation(self, app):
        """Test password strength validation"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com', created_by=0)
            
            # Test empty password
            with pytest.raises(ValueError, match="Password cannot be empty"):
                user.set_password("")
            
            # Test short password
            with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
                user.set_password("short")
            
            # Test password without uppercase
            with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
                user.set_password("lowercase123")
            
            # Test password without lowercase
            with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
                user.set_password("UPPERCASE123")
            
            # Test password without digit
            with pytest.raises(ValueError, match="Password must contain at least one digit"):
                user.set_password("NoDigits")
            
            # Test valid password
            user.set_password("ValidPass123")
            assert user.password_hash is not None
            
            # Test admin user - no password validation
            admin = User(username='admin', email='admin@example.com', created_by=0)
            admin.set_password("short")  # Should work for admin
            assert admin.password_hash is not None
    
    def test_user_authentication(self, app):
        """Test user authentication method"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='TestPass123',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
            
            # Test successful authentication
            authenticated_user = User.authenticate('testuser', 'TestPass123')
            assert authenticated_user is not None
            assert authenticated_user.username == 'testuser'
            
            # Test failed authentication
            failed_user = User.authenticate('testuser', 'wrongpassword')
            assert failed_user is None
            
            # Test non-existent user
            non_existent = User.authenticate('nonexistent', 'password')
            assert non_existent is None
            
            # Test admin authentication - should work with any password
            admin = User(
                username='admin',
                email='admin@example.com',
                created_by=0
            )
            db.session.add(admin)
            db.session.commit()
            
            admin_auth = User.authenticate('admin', 'anypassword')
            assert admin_auth is not None
            assert admin_auth.username == 'admin'
    
    def test_user_can_login(self, app):
        """Test user login capability"""
        with app.app_context():
            # User with password can login
            user_with_password = User(
                username='testuser',
                email='test@example.com',
                password='TestPass123',
                created_by=0
            )
            assert user_with_password.can_login()
            
            # System user without password cannot login
            system_user = User(
                username='SYSTEM',
                email='system@null.null',
                is_admin=True,
                created_by=0
            )
            assert not system_user.can_login()
            
            # Admin user can always login
            admin_user = User(
                username='admin',
                email='admin@example.com',
                created_by=0
            )
            assert admin_user.can_login()
    
    def test_user_get_by_username(self, app):
        """Test getting user by username"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
            
            found_user = User.get_by_username('testuser')
            assert found_user is not None
            assert found_user.username == 'testuser'
            
            not_found = User.get_by_username('nonexistent')
            assert not_found is None
    
    def test_user_get_by_email(self, app):
        """Test getting user by email"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
            
            found_user = User.get_by_email('test@example.com')
            assert found_user is not None
            assert found_user.email == 'test@example.com'
            
            not_found = User.get_by_email('nonexistent@example.com')
            assert not_found is None

class TestAuthenticationRoutes:
    """Test cases for authentication routes"""
    
    def test_login_page(self, client):
        """Test login page is accessible"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign in to your Armada PBMS account' in response.data
    
    def test_login_success(self, client, app):
        """Test successful login"""
        with app.app_context():
            # Create user with password
            user = User(
                username='testuser',
                email='test@example.com',
                password='TestPass123',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
    
    def test_admin_auto_login(self, client, app):
        """Test admin auto-login without password"""
        with app.app_context():
            # Ensure admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    created_by=0
                )
                db.session.add(admin)
                db.session.commit()
        
        # Admin should be able to login without password
        response = client.post('/auth/login', data={
            'username': 'admin'
            # No password provided
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
    
    def test_admin_login_with_any_password(self, client, app):
        """Test admin login with any password"""
        with app.app_context():
            # Ensure admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    created_by=0
                )
                db.session.add(admin)
                db.session.commit()
        
        # Admin should be able to login with any password
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'anypassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
    
    def test_login_failure(self, client):
        """Test failed login"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_failure_non_admin(self, client):
        """Test failed login for non-admin users"""
        response = client.post('/auth/login', data={
            'username': 'testuser'
            # Missing password for non-admin user
        })
        
        assert response.status_code == 200
        assert b'Password is required for non-admin users' in response.data
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/auth/login', data={
            # Missing username
        })
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_logout(self, auth_client):
        """Test logout functionality"""
        response = auth_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out successfully' in response.data
    
    def test_register_page(self, client):
        """Test registration page is accessible"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data
    
    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'display_name': 'New User',
            'email': 'newuser@example.com',
            'password': 'NewPass123',
            'confirm_password': 'NewPass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
    
    def test_register_validation_errors(self, client):
        """Test registration validation errors"""
        # Test short password
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'display_name': 'New User',
            'email': 'newuser@example.com',
            'password': 'short',
            'confirm_password': 'short'
        })
        
        assert response.status_code == 200
        assert b'Password must be at least 8 characters long' in response.data
    
    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'display_name': 'New User',
            'email': 'newuser@example.com',
            'password': 'NewPass123',
            'confirm_password': 'DifferentPass123'
        })
        
        assert response.status_code == 200
        assert b'Passwords do not match' in response.data
    
    def test_register_duplicate_username(self, client, app):
        """Test registration with duplicate username"""
        with app.app_context():
            user = User(
                username='existinguser',
                email='existing@example.com',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/auth/register', data={
            'username': 'existinguser',
            'display_name': 'New User',
            'email': 'newuser@example.com',
            'password': 'NewPass123',
            'confirm_password': 'NewPass123'
        })
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    def test_profile_page_requires_auth(self, client):
        """Test that profile page requires authentication"""
        response = client.get('/auth/profile')
        assert response.status_code == 302  # Redirect to login
    
    def test_profile_page_with_auth(self, auth_client):
        """Test profile page with authentication"""
        response = auth_client.get('/auth/profile')
        assert response.status_code == 200
        assert b'User Profile' in response.data
    
    def test_profile_update(self, auth_client):
        """Test profile update functionality"""
        response = auth_client.post('/auth/profile', data={
            'display_name': 'Updated Name',
            'email': 'updated@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Profile updated successfully' in response.data
    
    def test_password_change(self, auth_client):
        """Test password change functionality"""
        response = auth_client.post('/auth/profile', data={
            'display_name': 'Test User',
            'email': 'test@example.com',
            'current_password': 'TestPass123',
            'new_password': 'NewPass123',
            'confirm_password': 'NewPass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Profile updated successfully' in response.data
    
    def test_password_change_wrong_current(self, auth_client):
        """Test password change with wrong current password"""
        response = auth_client.post('/auth/profile', data={
            'display_name': 'Test User',
            'email': 'test@example.com',
            'current_password': 'WrongPass123',
            'new_password': 'NewPass123',
            'confirm_password': 'NewPass123'
        })
        
        assert response.status_code == 200
        assert b'Current password is incorrect' in response.data
    
    def test_setup_admin_page(self, client):
        """Test admin setup page"""
        response = client.get('/auth/admin/setup-admin')
        assert response.status_code == 200
        assert b'Setup Admin Account' in response.data
    
    def test_setup_admin_success(self, client, app):
        """Test successful admin setup"""
        with app.app_context():
            # Ensure admin user exists without password
            admin = User.query.filter_by(username='admin').first()
            if admin:
                admin.password_hash = None
                db.session.commit()
        
        response = client.post('/auth/admin/setup-admin', data={
            'password': 'AdminPass123',
            'confirm_password': 'AdminPass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Admin password set successfully' in response.data
    
    def test_setup_admin_already_set(self, client, app):
        """Test admin setup when password already set"""
        with app.app_context():
            # Ensure admin user has password
            admin = User.query.filter_by(username='admin').first()
            if admin:
                admin.set_password('ExistingPass123')
                db.session.commit()
        
        response = client.get('/auth/admin/setup-admin')
        assert response.status_code == 302  # Redirect to login

class TestAuthenticationSecurity:
    """Test cases for authentication security features"""
    
    def test_login_redirects_authenticated_users(self, auth_client):
        """Test that authenticated users are redirected from login"""
        response = auth_client.get('/auth/login')
        assert response.status_code == 302  # Redirect to dashboard
    
    def test_register_redirects_authenticated_users(self, auth_client):
        """Test that authenticated users are redirected from register"""
        response = auth_client.get('/auth/register')
        assert response.status_code == 302  # Redirect to dashboard
    
    def test_protected_routes_require_auth(self, client):
        """Test that protected routes require authentication"""
        protected_routes = [
            '/auth/profile',
            '/auth/logout',
            '/dashboard',
            '/events/',
            '/users/'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302  # Redirect to login
    
    def test_admin_routes_require_admin(self, auth_client):
        """Test that admin routes require admin privileges"""
        # Regular user trying to access admin routes
        response = auth_client.get('/users/')
        assert response.status_code == 302  # Redirect to dashboard with error
    
    def test_password_hash_security(self, app):
        """Test that passwords are properly hashed"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='TestPass123',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != 'TestPass123'
            assert user.password_hash.startswith('pbkdf2:sha256:')
    
    def test_session_management(self, client, app):
        """Test session management"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='TestPass123',
                created_by=0
            )
            db.session.add(user)
            db.session.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        
        # Should be able to access protected route
        response = client.get('/auth/profile')
        assert response.status_code == 200
        
        # Logout
        client.get('/auth/logout')
        
        # Should not be able to access protected route
        response = client.get('/auth/profile')
        assert response.status_code == 302  # Redirect to login 