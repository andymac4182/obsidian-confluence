# Contributing to EuroTempl

We deeply appreciate your interest in contributing to the EuroTempl project. This document provides comprehensive guidelines to help you contribute effectively while maintaining our high standards for code quality and project organization.

## Project Management and Documentation

We use Atlassian tools for project management and documentation:

- Project tracking: [EuroTempl JIRA](https://pygmalionrecords.atlassian.net/jira/software/projects/ET)
- Documentation: [EuroTempl Confluence](https://pygmalionrecords.atlassian.net/wiki/spaces/ET)

Before starting any work, please familiarize yourself with our documentation and current project status in these platforms.

## Development Workflow

### Getting Started

First, ensure you have read our README.md for system requirements and basic setup. After setting up your development environment, you should:

1. Review our architectural documentation in Confluence
2. Check current sprint goals and backlog in JIRA
3. Join our development channel on Slack for team communications

### Branch Strategy

We follow a trunk-based development approach with feature branches:

- Main branch: `main` (production-ready code)
- Development branch: `develop` (integration branch)
- Ticket branches: `ET-X-brief-description`

The JIRA ticket number (ET-X) must be included in the branch name for automatic tracking.

### Commit Guidelines

Each commit should:

1. Reference the JIRA ticket number in the commit message
2. Follow the conventional commits specification
3. Be focused and atomic

Example commit message:
```
feat(components): Implement parametric connector validation ET-123

- Add validation service for connector parameters
- Integrate with existing component management
- Update documentation

Resolves: ET-123
```

### Code Quality Standards

We maintain high code quality through:

1. Static Type Checking
   - Python: Use type hints and mypy
   - TypeScript: Strict mode enabled

2. Code Formatting
   - Python: Black formatter with line length 88
   - TypeScript/JavaScript: Prettier with provided config
   - SQL: pgFormatter

3. Linting
   - Python: flake8 with provided configuration
   - TypeScript: ESLint with provided config
   - CSS: stylelint

4. Testing Requirements
   - Unit tests required for all new features
   - Integration tests for API endpoints
   - End-to-end tests for critical paths
   - Minimum 80% code coverage

### Pull Request Process

1. Create a Pull Request from your feature branch to `develop`
2. Ensure the PR description includes:
   - JIRA ticket reference
   - Summary of changes
   - Testing methodology
   - Screenshots for UI changes
   - Migration steps if applicable

3. Request reviews from at least two team members
4. Address all review comments
5. Ensure CI/CD pipeline passes
6. Squash commits if requested by reviewers

## Documentation Requirements

### Code Documentation

- Python: Google-style docstrings
- TypeScript: JSDoc comments
- Inline comments for complex logic
- README files for each module

### Technical Documentation

Update relevant documentation in Confluence:
- Architecture changes
- New features
- API modifications
- Configuration changes

### Database Changes

For database modifications:
1. Create migration scripts
2. Document schema changes in Confluence
3. Update ERD diagrams
4. Provide rollback procedures

## Bug Reports and Feature Requests

1. Check existing JIRA tickets to avoid duplicates
2. Create a new ticket with:
   - Clear description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Screenshots or videos if applicable
   - Environment details

## Community and Communication

- Technical discussions: JIRA tickets or Confluence
- Quick questions: Slack development channel
- Code reviews: GitHub pull requests
- Sprint planning: JIRA boards
- Architecture decisions: Confluence

## Release Process

1. Create a release branch from `develop`
2. Update version numbers and CHANGELOG.md
3. Run full test suite
4. Create release notes in JIRA
5. Tag the release in Git
6. Merge to `main` after approval

## Questions and Support

For any questions about contributing:

1. Check existing documentation in Confluence
2. Ask in the Slack development channel
3. Contact the core development team
4. Create a JIRA ticket for broader discussions

Remember that every contribution, whether it's code, documentation, or bug reports, helps make EuroTempl better for everyone. Thank you for being part of our community!

## License

By contributing to EuroTempl, you agree that your contributions will be licensed under our proprietary license. See the LICENSE file for details.