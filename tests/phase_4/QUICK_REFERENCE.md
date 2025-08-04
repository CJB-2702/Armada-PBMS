# Phase 4: Quick Reference Guide

## Overview
Phase 4 implements a basic web-based user interface with authentication for the Asset Management System.

## Quick Start

### 1. Build Phase 4
```bash
# Activate virtual environment
source venv/bin/activate

# Build Phase 4 (includes all previous phases)
python app.py --phase4 --build-only
```

### 2. Start the Application
```bash
# Start the web server
python app.py --phase4
```

### 3. Access the Application
- **URL**: http://localhost:5000
- **Username**: `admin`
- **Password**: `admin-password-change-me`

## Features

### Authentication
- ✅ Login/logout functionality
- ✅ Session management
- ✅ Protected routes
- ✅ Password hashing
- ✅ Secure redirects

### User Interface
- ✅ Home page with system overview
- ✅ Asset listing with pagination
- ✅ Individual asset details
- ✅ Basic filtering (location)
- ✅ Simple navigation

### Security
- ✅ Flask-Login integration
- ✅ Werkzeug password hashing
- ✅ Session-based authentication
- ✅ Protected route decorators

## File Structure

### New Files
```
app/
├── auth.py                    # Authentication blueprint
├── routes.py                  # Main application routes
├── templates/
│   ├── base.html             # Base template
│   ├── index.html            # Home page
│   ├── auth/
│   │   └── login.html        # Login form
│   └── assets/
│       ├── list.html         # Asset listing
│       └── view.html         # Individual asset view
```

### Modified Files
```
app/
├── __init__.py               # Added authentication setup
├── build.py                  # Added Phase 4 support
└── app.py                    # Added --phase4 argument
```

## Testing

### Manual Testing
1. Start server: `python app.py --phase4`
2. Open browser to http://localhost:5000
3. Login with admin credentials
4. Navigate through the interface
5. Test logout functionality

### Automated Testing
```bash
# Run the test script
python phase_4/test_phase4.py
```

## Default Credentials
- **Username**: `admin`
- **Password**: `admin-password-change-me`
- **Email**: `admin@assetmanagement.local`
- **Admin Rights**: Yes

## Navigation
- **Home**: System overview and recent assets
- **Assets**: List all assets with filtering
- **Asset Details**: View individual asset information
- **Logout**: End session and return to login

## Technical Details

### Authentication Flow
1. User visits protected page
2. Redirected to login if not authenticated
3. User enters credentials
4. Credentials validated against database
5. Session created and maintained
6. User redirected to originally requested page

### Security Features
- Password hashing using Werkzeug
- Session management with Flask-Login
- Protected routes requiring authentication
- Secure redirect handling
- CSRF protection (basic)

### User Interface Design
- Minimal HTML (no CSS/JavaScript)
- Simple forms and navigation
- Clear error messages
- Responsive design
- Works without JavaScript

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if virtual environment is activated
   - Ensure all dependencies are installed
   - Check if port 5000 is available

2. **Login fails**
   - Verify default credentials are correct
   - Check if database was built with Phase 4
   - Ensure admin user exists in database

3. **Pages not loading**
   - Check if server is running
   - Verify authentication is working
   - Check browser console for errors

4. **Database issues**
   - Rebuild database: `python app.py --phase4 --build-only`
   - Check database file exists
   - Verify all models are imported

### Debug Mode
The application runs in debug mode by default, which provides:
- Detailed error messages
- Auto-reload on code changes
- Debug console for errors

## Next Steps (Future Phases)
- CSS styling and modern UI
- JavaScript functionality
- Advanced search and filtering
- User management interface
- Role-based access control
- API endpoints
- Asset creation and editing forms
- Advanced reporting

## Support
For issues or questions:
1. Check the Phase 4 status file: `phase_4/PHASE4_STATUS.md`
2. Review the implementation plan: `context/phase4plan.md`
3. Check the test script: `phase_4/test_phase4.py` 