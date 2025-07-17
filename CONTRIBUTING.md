# Contributing to MAC Address Changer

Thank you for your interest in contributing to the MAC Address Changer project! This document provides guidelines and information for contributors.

**Project Status**: ✅ **PRODUCTION READY** - All P0 Critical Items completed with enterprise-grade features, security hardening, and comprehensive testing.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [Security Considerations](#security-considerations)
- [Development Roadmap](#development-roadmap)
- [License](#license)

## Getting Started

### Prerequisites

- Python 3.6 or higher
- `ifconfig` command (pre-installed on most Linux/macOS systems)
- Git for version control
- A Unix-like operating system (Linux or macOS)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/mac_changer.git
   cd mac_changer
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Development Dependencies** (optional)
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run Tests to Verify Setup**
   ```bash
   python3 -m unittest test_mac_changer.py -v
   python3 scripts/test_systems.py --system-info-only
   ```

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter standard)
- Use meaningful variable and function names
- Include comprehensive docstrings for all functions and classes

### Code Formatting

We recommend using the following tools:

- **Black** for code formatting:
  ```bash
  black mac_changer.py mac_changer_improved.py
  ```

- **flake8** for linting:
  ```bash
  flake8 mac_changer.py mac_changer_improved.py
  ```

- **mypy** for type checking:
  ```bash
  mypy mac_changer_improved.py
  ```

### Documentation Style

- Use clear, concise docstrings
- Include parameter types and return value descriptions
- Provide usage examples where appropriate
- Update README.md for significant changes

Example docstring format:
```python
def validate_mac_address(self, mac_addr: str) -> str:
    """Validate MAC address format.
    
    Args:
        mac_addr: MAC address string to validate
        
    Returns:
        Normalized MAC address (lowercase with colons)
        
    Raises:
        argparse.ArgumentTypeError: If MAC address format is invalid
        
    Example:
        >>> validator.validate_mac_address("AA:BB:CC:DD:EE:FF")
        "aa:bb:cc:dd:ee:ff"
    """
```

## Testing

### Running Tests

Run all tests:
```bash
python3 -m unittest discover -v
```

Run specific test files:
```bash
python3 -m unittest test.py -v
python3 -m unittest test_improved.py -v
```

Run with coverage (if pytest-cov is installed):
```bash
pytest --cov=mac_changer --cov-report=html
```

### Writing Tests

- Write tests for all new functionality
- Include both positive and negative test cases
- Test error handling and edge cases
- Mock external dependencies (subprocess calls, system functions)
- Follow the existing test structure and naming conventions
- Maintain 100% test coverage (current: 34 comprehensive test cases)
- Use the provided test infrastructure (test_mac_changer.py)

Test naming convention:
- `test_function_name_success` for successful cases
- `test_function_name_failure` for error cases
- `test_function_name_edge_case` for edge cases

**Quality Standards**:
- All tests must pass: `python3 -m unittest test_mac_changer.py -v`
- Security scan clean: `python3 scripts/security_audit.py`
- System compatibility: `python3 scripts/test_systems.py`

### Test Categories

1. **Unit Tests** - Test individual functions and methods (test_mac_changer.py)
2. **Integration Tests** - Test component interactions
3. **Validation Tests** - Test input validation and error handling
4. **System Tests** - Test system compatibility (scripts/test_systems.py)
5. **Security Tests** - Test security vulnerabilities (scripts/security_audit.py)
6. **Performance Tests** - Test performance benchmarks

## Submitting Changes

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following the style guidelines
   - Add or update tests as needed
   - Update documentation if necessary

3. **Test Your Changes**
   ```bash
   python3 -m unittest test_mac_changer.py -v
   python3 scripts/test_systems.py
   python3 scripts/security_audit.py
   python3 mac_changer.py --help
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new validation feature"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots or examples if applicable
   - Ensure all automated checks pass (CI/CD pipeline)
   - Include security impact assessment if applicable

### Commit Message Format

Use conventional commit format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

Examples:
```
feat: add support for random MAC generation
fix: handle interface not found error gracefully
docs: update installation instructions
test: add comprehensive validation tests
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Environment Information**
  - Operating system and version
  - Python version
  - Command that failed
  - Complete error message

- **Steps to Reproduce**
  - Exact commands used
  - Expected behavior
  - Actual behavior

- **Additional Context**
  - Network interface information
  - Relevant system logs
  - Screenshots if applicable

### Feature Requests

When requesting features:

- Describe the use case
- Explain the expected behavior
- Consider backward compatibility
- Provide implementation suggestions if possible

### Security Issues

For security-related issues:

- **DO NOT** create public issues
- Email security concerns to: thomas@dyhr.com
- Include detailed description and potential impact
- Allow time for assessment and fix before disclosure

## Security Considerations

### Code Review Focus Areas

- Input validation and sanitization
- Privilege escalation prevention
- Command injection vulnerabilities
- Error message information disclosure
- Dependency security

### Testing Security

- Test with malformed inputs
- Verify privilege checks work correctly
- Ensure error messages don't leak sensitive information
- Test command injection attack vectors

### Guidelines for Contributors

- Never hardcode credentials or sensitive data
- Validate all user inputs
- Use subprocess securely (avoid shell=True)
- Follow principle of least privilege
- Document security assumptions

## Development Workflow

### Recommended Development Cycle

1. **Plan** - Review existing issues and discuss approach
2. **Develop** - Implement changes with tests
3. **Test** - Run comprehensive test suite
4. **Review** - Self-review code for quality and security
5. **Submit** - Create pull request with clear description
6. **Iterate** - Address review feedback

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Backward compatibility maintained
- [ ] Error handling is appropriate

## Project Structure

```
mac_changer/
├── mac_changer.py              # Original implementation
├── mac_changer_improved.py     # Enhanced version with OOP design
├── test.py                     # Basic unit tests
├── test_improved.py            # Comprehensive test suite
├── private_changer_helper.py   # Development utilities
├── setup.py                    # Package installation script
├── requirements.txt            # Dependencies
├── README.md                   # Project documentation
├── CONTRIBUTING.md            # This file
├── LICENSE                    # MIT License
└── .gitignore                # Git ignore rules
```

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version number is incremented
- [ ] CHANGELOG is updated
- [ ] Security review completed
- [ ] Performance impact assessed

## Development Roadmap

### Current Priorities

See [TODO.md](TODO.md) for the complete prioritized list of development tasks, including:

- **Critical (P0)**: ✅ **COMPLETED** - Production readiness, security audits, system testing
- **High (P1)**: ✅ **COMPLETED** - CI/CD pipeline, automated testing, comprehensive logging
- **Medium (P2)**: Enhanced features, configuration support, user experience, Docker testing
- **Low (P3)**: Platform expansion, advanced features, enterprise integration

**Current Focus**: P2 Medium Priority items including Docker container testing and configuration file support.

### Planning Process

1. **Review TODO.md** for current priorities
2. **Check RECOMMENDATIONS.md** for strategic direction
3. **Follow CLAUDE.md** for development practices
4. **Review P0_IMPLEMENTATION_SUMMARY.md** for completed work
5. **Coordinate with maintainers** before starting major work

**Before Contributing**:
- Run `python3 scripts/test_systems.py` to verify system compatibility
- Review `BACKUP_PROCEDURES.md` if working on backup/restore features
- Check security implications with `python3 scripts/security_audit.py`

## Getting Help

### Resources

- **Documentation**: README.md
- **Development Tasks**: TODO.md
- **Strategic Planning**: RECOMMENDATIONS.md
- **Best Practices**: CLAUDE.md
- **Implementation Status**: P0_IMPLEMENTATION_SUMMARY.md
- **Backup Procedures**: BACKUP_PROCEDURES.md
- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions (if enabled)
- **Email**: thomas@dyhr.com

**Testing Resources**:
- `scripts/test_systems.py` - System compatibility testing
- `scripts/security_audit.py` - Security vulnerability scanning
- `scripts/backup_restore.py` - Backup and restore testing

### Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Follow the project's code of conduct

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for contributing to the MAC Address Changer project! Your contributions help make network administration tools better and more secure for everyone.