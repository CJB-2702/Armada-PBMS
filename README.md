# Armada PBMS - Application Goals and Design Choices

## Core Application Purpose
- Post and Event based Fleet management and maintenance tracking system
- Focus on preventive maintenance scheduling and event logging
- Asset lifecycle tracking and documentation
- Track part locations and installations on equipment
- Real-time status monitoring of fleet assets
- Historical data analysis for maintenance patterns

## Design Philosophy
see minimalist_styleguide.md


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
see datamodel.md and event_model.md

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
2. Data model cohesion



## Security Considerations
- SQL injection prevention
- Password hashing and security


## Documentation Requirements
- update datamodel.md and styleguide.md while working



## Implementation Roadmap

### Phase 1: Core Database Structure
1. **Base Models**
   - Implement core models (Asset, Event, User, Location)
   - Set up default data loading system
   - Create database migrations
   - Implement basic CRUD operations

2. **Minimalist UI Foundation**
   - Create base templates with native HTML
   - Implement HTMX for dynamic updates
   - Set up basic routing and views
   - Add minimal CSS for buttons and layout

3. **Basic Asset Management**
   - Asset creation form with native inputs
   - Asset list view with `<details>` for details
   - Basic asset search and filtering
   - Asset status updates via HTMX

4. **Event System Foundation**
   - Event creation with native form elements
   - Event feed using HTMX infinite scroll
   - Basic event filtering
   - Event status updates

### Phase 2: Enhanced Functionality
1. **Comments and Attachments**
   - Implement comment system using forms and HTMX
   - Add file upload with progress using HTMX
   - Create attachment preview using native `<dialog>`
   - Implement comment threading with `<details>`

2. **Event Type Specialization**
   - Create specialized event type forms
   - Implement event type validation
   - Add event type-specific views
   - Create event type templates

3. **Advanced Filtering**
   - Implement filter system using native `<select>`
   - Add date range filtering
   - Create filter combinations
   - Save filter preferences

4. **User Management**
   - User registration and login
   - Role-based access control
   - User preferences
   - Activity logging

### Phase 3: Polish and Optimization
1. **UI Refinement**
   - Optimize responsive design
   - Enhance accessibility
   - Add keyboard shortcuts
   - Implement error handling

2. **Performance Optimization**
   - Implement lazy loading
   - Optimize database queries
   - Add caching where needed
   - Minimize JavaScript usage

3. **Documentation**
   - Create user documentation
   - Add inline help using `<details>`
   - Document API endpoints
   - Create development guides

4. **Testing and Deployment**
   - Write unit tests
   - Perform integration testing
   - Set up CI/CD pipeline
   - Prepare deployment documentation






