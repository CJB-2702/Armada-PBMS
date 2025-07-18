import pytest
from flask import Flask
from app import create_app
from app.models.BaseModels.Users import User
from app.extensions import db


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context"""
    with app.app_context():
        yield app


class TestAdminLogin:
    """Test cases for admin login functionality"""

    def test_admin_login_without_password(self, client, app_context):
        """Test that admin can login without providing a password"""
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
        
        # Test admin login without password
        response = client.post('/auth/login', data={
            'username': 'admin'
            # No password provided
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'dashboard' in response.data.lower() or b'welcome' in response.data.lower()

    def test_admin_login_with_any_password(self, client, app_context):
        """Test that admin can login with any password"""
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
        
        # Test admin login with any password
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'anypassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'dashboard' in response.data.lower() or b'welcome' in response.data.lower()

    def test_admin_login_with_empty_password(self, client, app_context):
        """Test that admin can login with empty password"""
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
        
        # Test admin login with empty password
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'dashboard' in response.data.lower() or b'welcome' in response.data.lower()

    def test_admin_login_with_whitespace_password(self, client, app_context):
        """Test that admin can login with whitespace-only password"""
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
        
        # Test admin login with whitespace password
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': '   '
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'dashboard' in response.data.lower() or b'welcome' in response.data.lower()

    def test_admin_login_page_accessible(self, client):
        """Test that login page is accessible"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign in to your Armada PBMS account' in response.data

    def test_admin_login_redirects_authenticated_user(self, client, app_context):
        """Test that authenticated admin is redirected from login page"""
        # First login as admin
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
        
        # Login
        client.post('/auth/login', data={'username': 'admin'})
        
        # Try to access login page again
        response = client.get('/auth/login')
        assert response.status_code == 302  # Should redirect

    def test_admin_can_access_protected_routes(self, client, app_context):
        """Test that admin can access protected routes after login"""
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
        
        # Login as admin
        client.post('/auth/login', data={'username': 'admin'})
        
        # Test access to protected routes
        protected_routes = [
            '/dashboard',
            '/assets/',
            '/events/',
            '/locations/',
            '/users/'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 200, f"Failed to access {route}"

    def test_admin_logout(self, client, app_context):
        """Test that admin can logout successfully"""
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
        
        # Login as admin
        client.post('/auth/login', data={'username': 'admin'})
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out successfully' in response.data.lower()
        
        # Verify can't access protected routes after logout
        response = client.get('/dashboard')
        assert response.status_code == 302  # Should redirect to login 