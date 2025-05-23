# Armada PBMS - Application Goals and Design Choices

## Core Application Purpose
- Post and Event based Fleet management and maintenance tracking system
- Focus on preventive maintenance scheduling and event logging
- Asset lifecycle tracking and documentation
- Track part locations and installations on equipment
- Real-time status monitoring of fleet assets
- Historical data analysis for maintenance patterns

## Design Philosophy
- Clean, minimalist interface prioritizing readability and efficiency
- Consistent visual language across all components
- Minimize all css and javascript whenever possible
- Prioritize using HTMX whenever possible
- Webcomponents for most frequently repeated items
- Minimize all exeption handling, allow things to break during development to debug



## Technology Stack
### Frontend
- Custom font selection:
  - Lora: Logo/branding font for elegance and page Headers
  - Fira Code: Monospace font for anything with numbers or written by users
  - Inclusive Sans: General Content Font for interactive buttons and ui controls
- CSS Grid/Flexbox for responsive layouts
- HTMX for dynamic content updates


## Visual language
- Primary Inspiration from IBM Carbon
- Square blocky components
- Components broken into sections by power of two
- cool blue and grey, dark and light mode considerations

### Backend
- Flask framework for lightweight, modular backend
- SQLAlchemy ORM for database interactions with sqlite
- Flask-Login for user authentication
- File attachments and photos stored inside of the squlite database
- Flask-WTF for form handling
- Flask-Mail for email notifications
- Pathlib for file and directory tracking and editing whenever possible

#### Application Structure
```
app/
├── models/          # Database models and business logic
├── routes/          # Route handlers, minimal logic
├── templates/       # HTML templates
├── static/         # Static files (CSS, JS, images)
└── utils/          # Utility functions and helpers
```

#### Code Organization Guidelines
1. Models
   - Contain all business logic
   - Handle data validation
   - Manage relationships
   - Implement data operations

2. Routes
   - Keep routes thin and focused
   - Handle HTTP requests/responses
   - Delegate business logic to models
   - Delegate Html formatting to models
   - Return appropriate responses

3. Templates
   - Use base template for common elements
   - Keep templates focused on presentation
   - Use includes for reusable components
   - Follow consistent naming convention

4. Static Files
   - Organize by type (css, js, images)
   - Minimize file sizes
   - Use consistent naming
   - Version control assets

5. Utils
   - Common helper functions
   - Shared utilities
   - Constants and configurations
   - Custom extensions

### Database Schema
- Users and Authentication
- Assets and Equipment
- Maintenance Records
- Parts Inventory
- Parts Assigments
- Work Orders
- Event Logs
- File Attachments
- Locations

## Key Features
- Event logging and tracking
- Maintenance scheduling
- Asset management
- Parts inventory
- Dispatch coordination
- Report generation
- User authentication and authorization
- File attachments for documentation
- Calendar integration


## Development Priorities
1. Core functionality reliability
2. User experience optimization
3. Desktop responsiveness


## Security Considerations
- SQL injection prevention
- Password hashing and security


## Documentation Requirements
- UI style document
- Database schema documentation


## Implementation Roadmap

### Phase 1: Core Database Structure

#### User Management
```sql
-- Users Table (Simplified for initial development)
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    display_name TEXT,
    role TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default users
INSERT INTO users (user_id, username, display_name, role) VALUES
    (1, 'admin', 'System Administrator', 'admin'),
    (2, 'tech1', 'Technician One', 'technician'),
    (3, 'tech2', 'Technician Two', 'technician'),
    (4, 'supervisor', 'Maintenance Supervisor', 'supervisor'),
    (5, 'viewer', 'Read Only User', 'viewer');
```

#### Development Approach
1. Default Admin User
   - All initial development will use the admin user (user_id: 1)
   - No authentication required during development
   - All actions will be attributed to the admin user
   - User management and security features will be implemented later

2. User References
   - All `created_by` and `uploaded_by` fields will default to admin user_id (1)
   - User permissions and role-based access will be implemented in a later phase
   - User interface will show admin as the default user

#### Asset Management
```sql
-- Base Asset Table
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY,
    common_name TEXT,
    asset_type TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asset Details Table
CREATE TABLE asset_details (
    asset_id INTEGER PRIMARY KEY REFERENCES assets(asset_id),
    make TEXT,
    model TEXT,
    equipment_identifier TEXT,
    year_manufactured INTEGER,
    date_delivered DATE,
    location_id INTEGER REFERENCES locations(location_id),
    meter1_reading DECIMAL,
    meter1_type TEXT,
    fuel_type TEXT,
    weight DECIMAL,
    registration_category TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Asset Purchase Information
CREATE TABLE asset_purchases (
    purchase_id INTEGER PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(asset_id),
    purchase_date DATE,
    price DECIMAL,
    buyer_name TEXT,
    seller_name TEXT,
    purchase_address TEXT,
    delivery_date DATE,
    attachment_ids JSON,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Asset Relationships and Groupings
CREATE TABLE generic_lists (
    row_id INTEGER PRIMARY KEY,
    grouping_name TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

#### Location Management
```sql
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    unique_name TEXT,
    common_name TEXT,
    description TEXT,
    country TEXT,
    state TEXT,
    city TEXT,
    street TEXT,
    building_number TEXT,
    room TEXT,
    x DECIMAL,
    y DECIMAL,
    z DECIMAL,
    bin TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Event and Post System
```sql
-- Events/Posts Table
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES events(event_id),
    asset_id INTEGER REFERENCES assets(asset_id),
    created_by INTEGER REFERENCES users(user_id),
    event_type TEXT,
    title TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Comments Table
CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY,
    event_id INTEGER REFERENCES events(event_id),
    created_by INTEGER REFERENCES users(user_id),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Attachments Table
CREATE TABLE attachments (
    attachment_id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    parent_type TEXT,
    filename TEXT,
    filetype TEXT,
    bytecontent BLOB,
    uploaded_by INTEGER REFERENCES users(user_id),
    access_rules TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);
```

#### Maintenance Actions
```sql
CREATE TABLE maintenance_actions (
    action_id INTEGER PRIMARY KEY,
    action_class TEXT,
    short_name TEXT,
    full_name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Phase 2: Basic UI Implementation
1. Asset Management Interface
   - Asset creation form (as admin)
   - Asset listing with infinite scroll
   - Asset detail view
   - Location assignment interface

2. Event System Interface
   - Event creation form (as admin)
   - Event feed with infinite scroll
   - Comment system (as admin)
   - Attachment upload interface (as admin)

3. Location Management Interface
   - Location creation form
   - Location listing
   - Location detail view

### Phase 3: Maintenance System
1. Maintenance Action Implementation
   - Maintenance action creation interface
   - Work order generation
   - Troubleshooting workflow
   - Maintenance history view

2. Maintenance Scheduling
   - Calendar integration
   - Recurring maintenance setup
   - Maintenance notifications

### Phase 4: UI Enhancement
1. HTMX Integration
   - Replace vanilla JS with HTMX for dynamic updates
   - Implement infinite scroll with HTMX
   - Add real-time updates for events

2. Web Components
   - Create reusable components for:
     - Asset cards
     - Event cards
     - Comment sections
     - Attachment viewers
     - Location selectors


### Phase 5: Add Part inventory managment
    - achieve above goals first then continue to develop


### Development Guidelines
1. Database
   - Use SQLite for development
   - Allow all fields to be nullable for initial development
   - Initialize database with:
     ```sql
     -- Create tables in order of dependencies
     -- Insert default users
     -- Create initial asset types
     -- Create initial locations
     ```

2. UI/UX
   - Follow IBM Carbon design principles
   - Use power-of-two spacing
   - Maintain consistent component hierarchy
   - Avoid rounded corners and components


3. HTMX Patterns
   - Use `hx-get` for loading content
   - Use `hx-post` for form submissions
   - Use `hx-trigger="load"` for initial content
   - Use `hx-swap="outerHTML"` for updates
   - Use `hx-indicator` for loading states
   - Use `hx-target` for specific updates

4. Error Handling
   - Show errors inline where they occur
   - Use toast notifications for system messages
   - Log all errors to console during development
   - Return proper HTTP status codes

### First Milestone Goals
1. Database Setup
   - All tables created and working
   - Default users inserted
   - Basic indexes in place

2. Basic Asset Management
   - Create a new asset
   - View asset list
   - View asset details
   - Assign asset to location

3. Basic Event System
   - Create a new event
   - View event list
   - Add comments to events
   - Attach files to events

4. Basic Location Management
   - Create a new location
   - View location list
   - View location details
   - Assign assets to locations

### Implementation Checklist
- [ ] Database schema implemented
- [ ] Default users created
- [ ] Basic asset CRUD operations
- [ ] Basic event CRUD operations
- [ ] Basic location CRUD operations
- [ ] HTMX integration for dynamic updates
- [ ] Basic error handling
- [ ] Basic UI components
- [ ] Basic navigation
- [ ] Basic forms
- [ ] Basic lists
- [ ] Basic details views

### Next Steps After First Milestone
1. Enhance UI with HTMX
2. Add maintenance features
3. Add part inventory
4. Add reporting
5. Add user management
6. Add security features



