# User Info and Login Design Summary

## Overview

The user authentication system manages user accounts, credentials, and portal-specific settings. Core components include the `User` model for authentication, `PortalUserData` for user preferences/cache, and Flask-Login integration for session management. The system provides secure password hashing, role-based permissions, audit trails, and extensible user settings storage.

## User Model (`app/data/core/user_info/user.py`)

The `User` model extends Flask-Login's `UserMixin` and provides core authentication fields. It implements the `DataInsertionMixin` for standardized data creation workflows.

### Core Fields

- **Authentication**: `username` (String 80, unique, required), `email` (String 120, unique, required), `password_hash` (String 255, required)
- **Permissions**: `is_active` (Boolean, default True), `is_admin` (Boolean, default False), `is_system` (Boolean, default False)
- **Audit**: `created_at` (DateTime, auto-set on creation), `updated_at` (DateTime, auto-updated on modification)

### Password Management

Password security uses Werkzeug's PBKDF2-based hashing via `generate_password_hash()` and `check_password_hash()`. Passwords are never stored in plaintext. The model provides two methods:
- `set_password(password)`: Hashes and stores a new password
- `check_password(password)`: Verifies a password against the stored hash

### Authentication Integration

The `@login_manager.user_loader` decorator function enables Flask-Login to load users from session IDs. The `is_authenticated()` method returns the user's `is_active` status, allowing account disabling without deletion.

### Relationships

The User model maintains foreign key relationships (without backrefs to avoid circular dependencies) to track ownership and modifications:
- **Assets**: `created_assets`, `updated_assets`
- **Locations**: `created_locations`, `updated_locations`
- **Asset Types**: `created_asset_types`, `updated_asset_types`
- **Make/Models**: `created_make_models`, `updated_make_models`
- **Events**: `events` (user who created/owns the event)
- **Comments**: `created_comments`, `updated_comments`
- **Attachments**: `created_attachments`, `updated_attachments`

These relationships enable comprehensive audit trails showing who created or modified each entity in the system.

## Portal User Data (`app/data/core/user_info/portal_user_data.py`)

The `PortalUserData` model extends `UserCreatedBase` (which provides audit fields) and provides a one-to-one relationship with `User` to store user-specific portal configuration and performance-optimized cache data.

### Structure

The model uses a unique foreign key constraint (`user_id`) ensuring each user has at most one portal data record. Accessible via `user.portal_data` backref from the User model.

### Settings Fields (JSON)

User preferences that persist across sessions per module:
- `general_settings`: Application-wide preferences (theme, pagination, etc.)
- `core_settings`: Core module preferences
- `maintenance_settings`: Maintenance portal preferences
- Future: `inventory_settings`, `supply_settings`, etc.

Settings are stored as JSON dictionaries, allowing flexible schema evolution without migrations.

### Cache Fields (JSON)

Computed/aggregated data that can be regenerated for performance:
- `general_cache`: Application-wide cached data
- `core_cache`: Core module cached aggregations
- `maintenance_cache`: Maintenance portal cached data (e.g., top assets, recent events)
- Future: `inventory_cache`, `supply_cache`, etc.

Cache can be cleared and regenerated without losing user preferences. This separation allows settings to persist while cache can be invalidated during data updates.

## Login Flow (`app/auth.py`)

Authentication is handled through a Flask Blueprint named `auth` with routes for login and logout.

### Login Route (`/login`)

Handles both GET (display form) and POST (process credentials) requests:

1. **Authentication Check**: If user is already authenticated, redirects to main page
2. **Credential Validation**: Checks that both username and password are provided
3. **User Lookup**: Queries `User` model by username (case-sensitive)
4. **Password Verification**: Uses `check_password()` to verify against stored hash
5. **Active Status Check**: Ensures `is_active` flag is True
6. **Session Creation**: Calls Flask-Login's `login_user()` to create authenticated session
7. **Redirect Handling**: Supports `next` parameter for post-login navigation with security check against open redirects

Error cases flash appropriate messages and log warnings. Successful logins log info-level events and display welcome message.

### Logout Route (`/logout`)

Protected by `@login_required` decorator. Invalidates the Flask-Login session via `logout_user()`, logs the action, and redirects to login page.

### Flask-Login Configuration

The login manager is initialized in `app/__init__.py` with:
- `login_view = 'auth.login'`: Route to redirect unauthenticated users
- `login_message`: Flash message shown when login required
- `login_message_category`: CSS class for message styling

## Security Considerations

- Passwords are hashed using Werkzeug's secure PBKDF2 algorithm
- Login attempts are logged for security auditing
- Account deactivation via `is_active` flag provides non-destructive user management
- System users (`is_system`) can be flagged for automated accounts
- Open redirect prevention via URL parsing checks
- Session management handled securely by Flask-Login

