# Armada PBMS (Post and Event Based Maintenance System)

A comprehensive fleet management and maintenance tracking system focused on preventive maintenance scheduling and event logging.

## Core Features

- Asset lifecycle tracking and documentation
- Preventive maintenance scheduling
- Event logging and tracking
- Parts inventory management
- Real-time status monitoring
- Historical data analysis
- File attachments for documentation
- Calendar integration

## Technology Stack

### Frontend
- Custom Fonts:
  - Lora: Logo/branding font
  - Fira Code: Monospace font for numbers/user input
  - Inclusive Sans: General content font
- CSS Grid/Flexbox for responsive layouts
- HTMX for dynamic content updates
- IBM Carbon-inspired design system

### Backend
- Flask framework
- SQLAlchemy ORM with SQLite
- Flask-Login for authentication
- Flask-WTF for form handling
- Flask-Mail for notifications
- File attachments stored in SQLite

## Project Structure

```
app/
├── models/          # Database models and business logic
├── routes/          # Route handlers
├── templates/       # HTML templates
├── static/         # Static files (CSS, JS, images)
└── utils/          # Utility functions
```

## Design Philosophy

- Clean, minimalist interface prioritizing readability
- Consistent visual language across components
- Minimal CSS and JavaScript usage
- HTMX-first approach for dynamic updates
- Web components for repeated elements
- Development-focused error handling

## Development Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python init_debug_db.py
   ```

4. Run the development server:
   ```bash
   python run.py
   ```

## Development Guidelines

### Models
- Contain all business logic
- Handle data validation
- Manage relationships
- Implement data operations

### Routes
- Keep routes thin and focused
- Handle HTTP requests/responses
- Delegate business logic to models
- Return appropriate responses

### Templates
- Use base template for common elements
- Keep templates focused on presentation
- Use includes for reusable components
- Follow consistent naming convention

### Static Files
- Organize by type (css, js, images)
- Minimize file sizes
- Use consistent naming
- Version control assets

### Utils
- Common helper functions
- Shared utilities
- Constants and configurations
- Custom extensions

## Security Considerations

- SQL injection prevention
- Password hashing and security
- File upload validation
- Input sanitization

## Development Priorities

1. Core functionality reliability
2. User experience optimization
3. Desktop responsiveness

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
