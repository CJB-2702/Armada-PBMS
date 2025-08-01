# Pull Request Template

## Overview
Brief description of what this PR accomplishes and why it's needed.

## Phase Information
- **Phase**: [Phase 1/2/3/4]
- **Phase Goal**: [Brief description of phase goal]
- **Status**: [Stable/In Progress/Experimental]

## Changes Made
- [ ] List major changes
- [ ] Include new features
- [ ] Note any breaking changes
- [ ] Document configuration changes

## Testing
- [ ] Phase 1 build tested: `python app.py --phase1 --build-only`
- [ ] Phase 2 build tested: `python app.py --phase2 --build-only` (if applicable)
- [ ] Full build tested: `python app.py --build-only`
- [ ] Web server starts correctly: `python app.py`
- [ ] All tests pass: `python test_phase_build.py`

## Database Changes
- [ ] New tables created
- [ ] Existing tables modified
- [ ] Data migrations included
- [ ] Sample data seeded

## Documentation
- [ ] README updated
- [ ] Phase documentation updated
- [ ] API documentation updated (if applicable)
- [ ] Usage examples provided

## Checklist
- [ ] Code follows project style guidelines
- [ ] All new code is documented
- [ ] No debugging code left in
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Security considerations addressed

## Screenshots (if applicable)
Add screenshots of UI changes or new features.

## Related Issues
Closes #[issue number]

## Notes
Any additional notes for reviewers or future reference. 