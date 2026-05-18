# Contributing to DB Security Testing

Thank you for your interest in contributing to this healthcare database security research project!

## Project Overview

This is a deliberately-vulnerable security research lab designed for educational purposes. It contains intentional security flaws to demonstrate SQL injection vulnerabilities and defense mechanisms.

## Code of Conduct

- Be respectful and constructive
- Focus on what is best for the security research community
- Remember this is an educational project

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/DB_Security_Testing`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Follow the installation guide in README.md
5. Run tests before committing

## Pull Request Guidelines

### For Security Fixes
- Clearly explain the vulnerability being fixed
- Include before/after examples when possible
- Reference the specific issue number
- Update relevant documentation

### For New Features
- Add tests for the new functionality
- Update API documentation if applicable
- Consider security implications
- Maintain the educational value of the project

### For Bug Fixes
- Describe the bug and reproduction steps
- Reference the issue being fixed
- Include regression tests

## Testing

The project includes several testing approaches:

### Security Testing
```bash
# Run comprehensive security comparison
python backend/attack_scenarios.py --mode compare

# Test vulnerable mode
python backend/attack_scenarios.py --mode vulnerable

# Test secure mode  
python backend/attack_scenarios.py --mode secure
```

### Code Quality
- Keep functions focused and single-purpose
- Add comments for complex security logic
- Follow existing code style
- Use meaningful variable names

## Security Research Guidelines

When working on security features:

1. **Intentional Vulnerabilities**
   - Keep vulnerable mode functional for education
   - Document intentionally insecure code paths
   - Ensure secure mode demonstrates proper defenses

2. **Security Fixes**
   - Test vulnerable mode still works
   - Verify secure mode blocks attacks
   - Document the security principle being demonstrated

3. **Sensitive Data**
   - Use realistic but fictitious patient data
   - No real PII should be committed
   - Follow healthcare data handling principles

## Documentation

### Documentation Standards
- Use clear, concise language
- Include code examples and use cases
- Update security impact analysis
- Add screenshots for complex features

### What Needs Documentation
- New API endpoints
- Security features and bypasses
- Configuration changes
- Breaking changes

## Issue Templates

### Security Issue Bug Report
```
**Severity**: (Critical/High/Medium/Low)
**Component**: (Frontend/Backend/Database/Infrastructure)
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
**Actual Behavior**:
**Environment**: (Docker/VM/Local)
```

### Feature Request
```
**Feature Description**:
**Security Impact**:
**Educational Value**:
**Proposed Implementation**:
**Alternatives Considered**:
```

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md for significant contributions
- Contributor section of README
- Security analysis documentation

## License

This project is for educational and research purposes. By contributing, you agree that your contributions will be licensed under the same terms as the project.

## Getting Help

- Review existing issues and PRs
- Check project documentation in LabDocumentation/
- Contact maintainers for complex security questions

Thank you for contributing to healthcare security education!