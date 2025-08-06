# User Permission Data Model Design

## Overview
This document explores different approaches to implementing user permissions and access control in the Asset Management System. We'll examine various data model patterns, their trade-offs, and the specific database tables required for each approach.

## Permission System Requirements

### Core Requirements
1. **User Authentication**: Verify user identity
2. **Authorization**: Control what users can access and modify
3. **Role-Based Access**: Assign permissions based on user roles
4. **Resource-Level Permissions**: Control access to specific assets, locations, etc.
5. **Audit Trail**: Track permission changes and access attempts
6. **Flexibility**: Support future permission requirements
7. **Performance**: Efficient permission checking

### Business Requirements
- **Location-Based Access**: Users may only access assets in specific locations
- **Asset Type Restrictions**: Users may only work with certain asset types
- **Operation-Level Permissions**: Different permissions for create, read, update, delete
- **Temporary Permissions**: Time-limited access for contractors or temporary workers
- **Permission Inheritance**: Group permissions that apply to all members

## Permission Model Approaches

### Approach 1: Simple Role-Based (Current Implementation)

#### Overview
Basic boolean flags on the User model for different permission levels.

#### Database Tables
```sql
-- Enhanced User table (additions to existing)
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
ALTER TABLE users ADD COLUMN can_edit_assets BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN can_edit_events BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN can_manage_users BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN can_view_reports BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN can_export_data BOOLEAN DEFAULT FALSE;
```

#### Pros
- ✅ Simple to implement and understand
- ✅ Fast permission checking (direct field access)
- ✅ Minimal database overhead
- ✅ Easy to migrate from current system

#### Cons
- ❌ Limited flexibility
- ❌ No resource-level permissions
- ❌ Hard to add new permission types
- ❌ No permission inheritance
- ❌ Difficult to implement temporary permissions

#### Use Case
Best for small organizations with simple permission needs.

---

### Approach 2: Role-Based with Permission Matrix

#### Overview
Separate roles and permissions tables with a many-to-many relationship.

#### Database Tables
```sql
-- Roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id)
);

-- Permissions table
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- 'asset', 'event', 'user', 'location', etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id)
);

-- Role-Permission junction table
CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by_id INTEGER REFERENCES users(id),
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role junction table
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NULL, -- For temporary assignments
    PRIMARY KEY (user_id, role_id)
);
```

#### Sample Data
```sql
-- Insert default roles
INSERT INTO roles (name, description) VALUES
('admin', 'Full system access'),
('manager', 'Can manage assets and events'),
('operator', 'Can create events and comments'),
('viewer', 'Read-only access');

-- Insert permissions
INSERT INTO permissions (name, description, category) VALUES
('asset.create', 'Create new assets', 'asset'),
('asset.read', 'View assets', 'asset'),
('asset.update', 'Edit assets', 'asset'),
('asset.delete', 'Delete assets', 'asset'),
('event.create', 'Create events', 'event'),
('event.read', 'View events', 'event'),
('event.update', 'Edit events', 'event'),
('event.delete', 'Delete events', 'event'),
('user.manage', 'Manage users', 'user'),
('location.manage', 'Manage locations', 'location'),
('report.view', 'View reports', 'report'),
('data.export', 'Export data', 'data');

-- Assign permissions to roles
INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), -- admin
(2, 1), (2, 2), (2, 3), (2, 5), (2, 6), (2, 7), (2, 11), -- manager
(3, 2), (3, 5), (3, 6), (3, 7), -- operator
(4, 2), (4, 6); -- viewer
```

#### Pros
- ✅ Flexible permission system
- ✅ Easy to add new permissions
- ✅ Role inheritance
- ✅ Temporary role assignments
- ✅ Clear permission categories
- ✅ Audit trail for permission changes

#### Cons
- ❌ More complex to implement
- ❌ Slower permission checking (joins required)
- ❌ More database overhead
- ❌ Still no resource-level permissions

#### Use Case
Good for medium organizations with multiple user types and evolving permission needs.

---

### Approach 3: Resource-Based Permissions

#### Overview
Permissions tied to specific resources (assets, locations, etc.) with user-resource relationships.

#### Database Tables
```sql
-- Resource types table
CREATE TABLE resource_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- 'asset', 'location', 'asset_type', etc.
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User resource permissions table
CREATE TABLE user_resource_permissions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL, -- 'asset', 'location', etc.
    resource_id INTEGER NOT NULL, -- ID of the specific resource
    permission VARCHAR(50) NOT NULL, -- 'read', 'write', 'delete', 'admin'
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, resource_type, resource_id, permission)
);

-- Location-based access table
CREATE TABLE user_locations (
    user_id INTEGER REFERENCES users(id),
    location_id INTEGER REFERENCES major_locations(id),
    access_level VARCHAR(20) DEFAULT 'read', -- 'read', 'write', 'admin'
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NULL,
    PRIMARY KEY (user_id, location_id)
);

-- Asset type restrictions table
CREATE TABLE user_asset_type_restrictions (
    user_id INTEGER REFERENCES users(id),
    asset_type_id INTEGER REFERENCES asset_types(id),
    allowed_operations VARCHAR(100), -- 'read,write,delete' or 'read' only
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by_id INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id, asset_type_id)
);
```

#### Sample Data
```sql
-- Insert resource types
INSERT INTO resource_types (name, description) VALUES
('asset', 'Individual assets'),
('location', 'Major locations'),
('asset_type', 'Asset categories'),
('make_model', 'Make and model combinations');

-- Assign location access to users
INSERT INTO user_locations (user_id, location_id, access_level) VALUES
(2, 1, 'write'), -- User 2 can write to location 1
(3, 1, 'read'),  -- User 3 can only read location 1
(2, 2, 'admin'); -- User 2 has admin access to location 2

-- Assign asset type restrictions
INSERT INTO user_asset_type_restrictions (user_id, asset_type_id, allowed_operations) VALUES
(2, 1, 'read,write'), -- User 2 can read and write vehicle assets
(3, 1, 'read');       -- User 3 can only read vehicle assets
```

#### Pros
- ✅ Granular resource-level control
- ✅ Location-based access control
- ✅ Asset type restrictions
- ✅ Temporary permissions
- ✅ Very flexible

#### Cons
- ❌ Complex to implement and maintain
- ❌ Performance overhead for permission checking
- ❌ Difficult to manage at scale
- ❌ Complex UI for permission management

#### Use Case
Best for organizations with complex access requirements and resource-specific permissions.

---

### Approach 4: Hybrid Approach (Recommended)

#### Overview
Combine role-based permissions with resource-level restrictions for maximum flexibility.

#### Database Tables
```sql
-- Enhanced roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE, -- Cannot be deleted/modified
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id)
);

-- Enhanced permissions table
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- 'asset', 'event', 'user', 'location', 'system'
    resource_type VARCHAR(50) NULL, -- 'asset', 'location', 'asset_type', NULL for global
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id)
);

-- Role-permission assignments
CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by_id INTEGER REFERENCES users(id),
    PRIMARY KEY (role_id, permission_id)
);

-- User-role assignments
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (user_id, role_id)
);

-- Resource restrictions (overrides role permissions)
CREATE TABLE user_resource_restrictions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL, -- 'location', 'asset_type'
    resource_id INTEGER NOT NULL,
    restriction_type VARCHAR(20) NOT NULL, -- 'allow', 'deny', 'limit'
    restriction_value TEXT, -- JSON for complex restrictions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, resource_type, resource_id, restriction_type)
);

-- Permission audit log
CREATE TABLE permission_audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- 'login', 'access_denied', 'permission_granted', etc.
    resource_type VARCHAR(50) NULL,
    resource_id INTEGER NULL,
    permission_required VARCHAR(100) NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSON NULL
);
```

#### Sample Data
```sql
-- Insert system roles
INSERT INTO roles (name, description, is_system_role) VALUES
('system', 'System user for automated processes', TRUE),
('admin', 'Full system administrator', FALSE),
('manager', 'Asset and location manager', FALSE),
('operator', 'Event and comment operator', FALSE),
('viewer', 'Read-only access', FALSE);

-- Insert permissions
INSERT INTO permissions (name, description, category, resource_type) VALUES
-- Global permissions
('system.admin', 'Full system access', 'system', NULL),
('user.manage', 'Manage users and roles', 'user', NULL),
('report.view', 'View all reports', 'report', NULL),
('data.export', 'Export system data', 'data', NULL),

-- Asset permissions
('asset.create', 'Create assets', 'asset', 'asset'),
('asset.read', 'View assets', 'asset', 'asset'),
('asset.update', 'Edit assets', 'asset', 'asset'),
('asset.delete', 'Delete assets', 'asset', 'asset'),

-- Event permissions
('event.create', 'Create events', 'event', 'event'),
('event.read', 'View events', 'event', 'event'),
('event.update', 'Edit events', 'event', 'event'),
('event.delete', 'Delete events', 'event', 'event'),

-- Location permissions
('location.manage', 'Manage locations', 'location', 'location'),
('location.read', 'View location details', 'location', 'location');

-- Assign permissions to roles
INSERT INTO role_permissions (role_id, permission_id) VALUES
-- System role (all permissions)
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (1, 14),

-- Admin role
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12), (2, 13), (2, 14),

-- Manager role
(3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14),

-- Operator role
(4, 6), (4, 7), (4, 9), (4, 10), (4, 11), (4, 12),

-- Viewer role
(5, 6), (5, 10), (5, 13);

-- Add resource restrictions
INSERT INTO user_resource_restrictions (user_id, resource_type, resource_id, restriction_type, restriction_value) VALUES
(3, 'location', 1, 'allow', '{"operations": ["read", "write"]}'), -- User 3 can only work with location 1
(4, 'asset_type', 1, 'limit', '{"max_assets": 10}'); -- User 4 limited to 10 assets of type 1
```

#### Pros
- ✅ Maximum flexibility
- ✅ Role-based efficiency
- ✅ Resource-level control when needed
- ✅ Comprehensive audit trail
- ✅ Scalable design
- ✅ Supports complex business rules
- ✅ Easy to extend

#### Cons
- ❌ Most complex to implement
- ❌ Requires careful design
- ❌ More database overhead
- ❌ Complex permission checking logic

#### Use Case
Best for organizations with complex permission requirements that need both efficiency and flexibility.

---

## Implementation Recommendations

### Phase 1: Start with Enhanced Role-Based (Approach 2)
1. **Implement basic role-permission system**
2. **Add location-based restrictions**
3. **Create permission management interface**
4. **Add audit logging**

### Phase 2: Add Resource Restrictions (Approach 4)
1. **Add resource restriction tables**
2. **Implement complex permission checking**
3. **Enhance UI for resource management**
4. **Add temporary permission support**

### Migration Strategy
1. **Create new tables alongside existing user system**
2. **Migrate existing users to default roles**
3. **Gradually replace boolean flags with role system**
4. **Add resource restrictions as needed**

## Permission Checking Logic

### Basic Permission Check
```python
def has_permission(user, permission_name, resource_type=None, resource_id=None):
    """Check if user has specific permission"""
    # Check role-based permissions
    for role in user.roles:
        for permission in role.permissions:
            if permission.name == permission_name:
                # Check resource restrictions
                if resource_type and resource_id:
                    restriction = get_user_resource_restriction(user, resource_type, resource_id)
                    if restriction and restriction.restriction_type == 'deny':
                        return False
                return True
    return False
```

### Location-Based Asset Access
```python
def get_user_accessible_assets(user):
    """Get assets user can access based on location restrictions"""
    if user.has_permission('system.admin'):
        return Asset.query
    
    # Get user's allowed locations
    allowed_locations = get_user_allowed_locations(user)
    
    if not allowed_locations:
        return Asset.query.filter(Asset.id == 0)  # No access
    
    return Asset.query.filter(Asset.major_location_id.in_(allowed_locations))
```

## Security Considerations

### 1. **Permission Inheritance**
- System role should have all permissions
- Admin role inherits from system role
- Manager role inherits from admin role (with restrictions)

### 2. **Resource Isolation**
- Users should only see resources they have access to
- Database queries must filter by user permissions
- UI should hide unauthorized options

### 3. **Audit Trail**
- Log all permission changes
- Track access attempts (successful and failed)
- Monitor for suspicious activity

### 4. **Performance Optimization**
- Cache user permissions in session
- Use database indexes on permission tables
- Implement efficient permission checking algorithms

## Conclusion

The **Hybrid Approach (Approach 4)** provides the best balance of flexibility, performance, and maintainability. It supports:

- ✅ Simple role-based permissions for most users
- ✅ Resource-level restrictions when needed
- ✅ Comprehensive audit trail
- ✅ Scalable architecture
- ✅ Easy migration path
- ✅ Future extensibility

This approach can start simple and grow complex as your organization's needs evolve, making it the most future-proof solution. 