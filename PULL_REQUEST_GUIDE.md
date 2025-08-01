# Pull Request Quick Reference Guide

## Creating a Pull Request

### 1. Ensure Phase is Stable
Before creating a pull request, ensure your phase is stable:
```bash
# Test the specific phase
python app.py --phase1 --build-only  # For Phase 1
python app.py --phase2 --build-only  # For Phase 2
python app.py --build-only           # For full system

# Run test suite
python test_phase_build.py
```

### 2. Create Feature Branch
```bash
# Create a new branch for your phase
git checkout -b phase1-stable  # or phase2-stable, etc.

# Make your changes and commit
git add .
git commit -m "Phase X Stable: [Description]"

# Push to remote
git push -u origin phase1-stable
```

### 3. Create Pull Request
1. Go to GitHub repository
2. Click "Compare & pull request" for your branch
3. Use the `PULL_REQUEST_TEMPLATE.md` template
4. Fill in all required information
5. Request reviews from team members

### 4. Pull Request Checklist
- [ ] Phase build test passes
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] No debugging code left in
- [ ] Error handling implemented
- [ ] Security considerations addressed

## Phase-Specific Requirements

### Phase 1 Pull Request
- **Branch**: `phase1-stable`
- **Test Command**: `python app.py --phase1 --build-only`
- **Required**: Core tables, system initialization, build system

### Phase 2 Pull Request
- **Branch**: `phase2-stable`
- **Test Command**: `python app.py --phase2 --build-only`
- **Required**: Detail tables, assignment system, Phase 1 dependency

### Phase 3 Pull Request
- **Branch**: `phase3-stable`
- **Test Command**: `python app.py --build-only`
- **Required**: Maintenance system, Phase 1+2 dependencies

### Phase 4 Pull Request
- **Branch**: `phase4-stable`
- **Test Command**: `python app.py --build-only`
- **Required**: Advanced features, all previous phase dependencies

## Common Issues and Solutions

### Build Failures
- Check database file permissions
- Ensure all dependencies are installed
- Verify model imports are correct
- Check for SQLAlchemy configuration issues

### Test Failures
- Run tests individually to isolate issues
- Check test data setup
- Verify database state
- Review error messages carefully

### Documentation Issues
- Update README.md with new features
- Include usage examples
- Document configuration changes
- Add screenshots for UI changes

## Review Process

### Self Review
1. Complete the PR template checklist
2. Test all functionality
3. Review code for style and quality
4. Ensure documentation is complete

### Code Review
1. Request review from team members
2. Address review comments
3. Make necessary changes
4. Re-test after changes

### Final Steps
1. Get approval from reviewers
2. Ensure CI/CD passes (if applicable)
3. Merge to main branch
4. Delete feature branch

## Best Practices

### Commit Messages
- Use descriptive commit messages
- Reference issue numbers
- Group related changes
- Use conventional commit format

### Branch Management
- Keep branches focused on single phases
- Delete branches after merge
- Use descriptive branch names
- Keep branches up to date with main

### Testing
- Test thoroughly before PR
- Include both positive and negative tests
- Test edge cases
- Verify error handling

### Documentation
- Update documentation with changes
- Include usage examples
- Document configuration options
- Add inline code comments 