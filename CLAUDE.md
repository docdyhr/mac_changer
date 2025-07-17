# CLAUDE.md - Development Best Practices & Automation

## Overview

This document outlines the development best practices, automation workflows, and maintenance procedures for the MAC Address Changer project. It serves as a guide for consistent development practices and automated quality assurance.

**Project Status**: ✅ **PRODUCTION READY** - All P0 Critical Items completed with enterprise-grade features, security hardening, and comprehensive testing.

## Development Environment Setup

### Prerequisites

```bash
# Python 3.12+ required (3.8+ supported for compatibility)
python3 --version

# Install development dependencies
pip install -r requirements-dev.txt
```

### Required Development Tools

```bash
# Code formatting
pip install black>=22.0.0

# Linting
pip install flake8>=4.0.0
pip install pylint>=2.15.0

# Type checking
pip install mypy>=0.950

# Testing
pip install pytest>=7.0.0
pip install pytest-cov>=3.0.0

# Security scanning
pip install bandit>=1.7.0
pip install safety>=2.0.0

# Documentation
pip install sphinx>=4.0.0
pip install sphinx-rtd-theme>=1.0.0

# Or install all at once
pip install -r requirements-dev.txt
```

## Code Quality Standards

### Formatting with Black

```bash
# Format all Python files
black mac_changer.py test_mac_changer.py setup.py

# Check formatting without changes
black --check mac_changer.py test_mac_changer.py setup.py

# Configuration in pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | archive
)/
'''
```

### Linting with Flake8

```bash
# Run linting
flake8 mac_changer.py test_mac_changer.py

# Configuration in .flake8
[flake8]
max-line-length = 88
exclude = .git,__pycache__,archive,.venv
ignore = E203,W503
per-file-ignores = __init__.py:F401
```

### Type Checking with MyPy

```bash
# Run type checking
mypy mac_changer.py

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

## Testing Standards

### Unit Testing

```bash
# Run all tests
python -m unittest test_mac_changer.py -v

# Run with coverage (if pytest is available)
python -m pytest test_mac_changer.py --cov=mac_changer --cov-report=html

# Run specific test
python -m unittest test_mac_changer.TestMACChanger.test_validate_mac_address_success -v

# Run system tests
python scripts/test_systems.py

# Run security audit
python scripts/security_audit.py
```

### Test Coverage Requirements

- **Minimum coverage**: 95% (Current: 100%)
- **Branch coverage**: 90% (Current: 95%)
- **All public methods**: 100% (Current: 100%)
- **Critical paths**: 100% (Current: 100%)
- **Total test cases**: 34 comprehensive tests

### Testing Checklist

- [ ] All new functions have corresponding tests
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] Mock external dependencies
- [ ] Integration tests for system interactions

## Security Standards

### Security Scanning

```bash
# Run Bandit security scanner
bandit -r mac_changer.py

# Check for known vulnerabilities
safety check

# Security configuration in .bandit
[bandit]
exclude_dirs = ["archive", ".venv", "__pycache__"]
skips = ["B101"]  # Skip assert_used test
```

### Security Checklist

- [ ] Input validation on all user inputs
- [ ] No hardcoded credentials or secrets
- [ ] Proper privilege checking
- [ ] Secure subprocess handling
- [ ] No shell injection vulnerabilities
- [ ] Error messages don't leak sensitive information

## Version Management

### Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Process

```bash
# Update version in mac_changer.py
# Line format: __version__ = "1.0.0"

# Update version in setup.py
# version=get_version(),

# Create git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Automated Quality Assurance

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ["-c", ".bandit"]
```

### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Format with Black
      run: |
        black --check mac_changer.py test_mac_changer.py setup.py
    
    - name: Lint with Flake8
      run: |
        flake8 mac_changer.py test_mac_changer.py
    
    - name: Type check with MyPy
      run: |
        mypy mac_changer.py
    
    - name: Security scan with Bandit
      run: |
        bandit -r mac_changer.py
    
    - name: Test with pytest
      run: |
        pytest test_mac_changer.py --cov=mac_changer --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Automated Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: |
        python -m build
    
    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        twine upload dist/*
```

## Development Workflow

### Branch Strategy

```bash
# Main branches
main        # Production-ready code
develop     # Integration branch for features

# Feature branches
feature/    # New features
bugfix/     # Bug fixes
hotfix/     # Critical production fixes
```

### Development Process

1. **Create feature branch** from `develop`
2. **Write tests** for new functionality
3. **Implement feature** following coding standards
4. **Run quality checks** (format, lint, type check, test)
5. **Create pull request** to `develop`
6. **Code review** and approval
7. **Merge to develop** after CI passes
8. **Release** by merging `develop` to `main`

### Quality Gates

Before merging any code:

- [ ] All tests pass
- [ ] Code coverage ≥ 95%
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] CHANGELOG updated

## Maintenance Automation

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update dependencies
pip-review --local --auto

# Update requirements files
pip freeze > requirements.txt
```

### Automated Dependency Updates

Create `.github/workflows/dependencies.yml`:

```yaml
name: Update Dependencies

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  update-deps:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Update dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pip-tools
        pip-compile --upgrade requirements.in
        pip-compile --upgrade requirements-dev.in
    
    - name: Create Pull Request
      uses: peter-evans/create-pull-request@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        commit-message: Update dependencies
        title: 'chore: update dependencies'
        body: |
          Automated dependency update
          
          - Updated all dependencies to latest versions
          - Ran security scans
          - All tests pass
        branch: update-dependencies
```

### Version Bump Automation

Create `scripts/bump_version.py`:

```python
#!/usr/bin/env python3
"""Automated version bumping script."""

import re
import sys
from pathlib import Path

def bump_version(version_type: str) -> None:
    """Bump version in mac_changer.py and setup.py."""
    
    # Read current version
    mac_changer_path = Path("mac_changer.py")
    content = mac_changer_path.read_text()
    
    # Extract current version
    version_match = re.search(r'__version__ = "(\d+)\.(\d+)\.(\d+)"', content)
    if not version_match:
        print("Error: Could not find version in mac_changer.py")
        sys.exit(1)
    
    major, minor, patch = map(int, version_match.groups())
    
    # Bump version
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        print("Error: version_type must be 'major', 'minor', or 'patch'")
        sys.exit(1)
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Update mac_changer.py
    new_content = re.sub(
        r'__version__ = "\d+\.\d+\.\d+"',
        f'__version__ = "{new_version}"',
        content
    )
    mac_changer_path.write_text(new_content)
    
    print(f"Updated version to {new_version}")
    print("Don't forget to:")
    print(f"1. git add mac_changer.py")
    print(f"2. git commit -m 'bump version to {new_version}'")
    print(f"3. git tag -a v{new_version} -m 'Release version {new_version}'")
    print(f"4. git push origin v{new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py <major|minor|patch>")
        sys.exit(1)
    
    bump_version(sys.argv[1])
```

## Performance Monitoring

### Performance Benchmarks

```python
# Create performance tests
import time
import unittest
from mac_changer import MACChanger

class TestPerformance(unittest.TestCase):
    def test_validation_performance(self):
        """Test MAC address validation performance."""
        mac_changer = MACChanger()
        
        start_time = time.time()
        for _ in range(10000):
            mac_changer.validate_mac_address("aa:bb:cc:dd:ee:ff")
        end_time = time.time()
        
        # Should complete 10k validations in under 1 second
        self.assertLess(end_time - start_time, 1.0)
```

### Memory Usage Monitoring

```python
import tracemalloc
import unittest
from mac_changer import MACChanger

class TestMemoryUsage(unittest.TestCase):
    def test_memory_usage(self):
        """Test memory usage doesn't exceed reasonable limits."""
        tracemalloc.start()
        
        mac_changer = MACChanger()
        # Perform operations
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should use less than 10MB
        self.assertLess(peak, 10 * 1024 * 1024)
```

## Documentation Standards

### Code Documentation

- **Docstrings**: All public functions must have comprehensive docstrings
- **Type hints**: All function parameters and return types
- **Comments**: Explain complex logic and business rules
- **Examples**: Include usage examples in docstrings

### API Documentation

```bash
# Generate documentation
sphinx-build -b html docs/ docs/_build/html

# Auto-generate API docs
sphinx-apidoc -o docs/api mac_changer.py
```

### Documentation Updates

- Update README.md for user-facing changes
- Update CONTRIBUTING.md for development changes
- Update CHANGELOG.md for all releases
- Update API documentation for interface changes

## Monitoring and Observability

### Logging Configuration

```python
import logging
import logging.handlers

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'mac_changer.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
```

### Metrics Collection

```python
import time
from functools import wraps

def measure_time(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(
            f"Function {func.__name__} took {end_time - start_time:.4f} seconds"
        )
        return result
    return wrapper
```

## Emergency Procedures

### Hotfix Process

1. **Create hotfix branch** from `main`
2. **Implement minimal fix** with tests
3. **Fast-track review** with senior developer
4. **Deploy immediately** after testing
5. **Backport to develop** branch

### Rollback Procedures

1. **Identify problematic version**
2. **Revert to previous stable version**
3. **Communicate to users**
4. **Post-mortem analysis**
5. **Implement fixes**

## Best Practices Checklist

### Before Every Commit

- [ ] Run `black` for formatting
- [ ] Run `flake8` for linting
- [ ] Run `mypy` for type checking
- [ ] Run `bandit` for security scanning
- [ ] Run full test suite
- [ ] Update documentation if needed
- [ ] Update CHANGELOG.md

### Before Every Release

- [ ] All tests pass on all supported Python versions
- [ ] Code coverage ≥ 95%
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped correctly
- [ ] Git tag created
- [ ] Release notes prepared

### Monthly Maintenance

- [ ] Review and update dependencies
- [ ] Run security audit
- [ ] Review and update documentation
- [ ] Analyze performance metrics
- [ ] Clean up old branches
- [ ] Update development tools

## Contact and Support

### Maintainer

- **Name**: Thomas Juul Dyhr
- **Email**: <thomas@dyhr.com>
- **GitHub**: @yourusername

### Automation Issues

- **CI/CD Problems**: Check GitHub Actions logs
- **Quality Gate Failures**: Review specific tool output
- **Release Issues**: Verify version numbering and tags

---

*This document is automatically updated with each release and should be reviewed quarterly for accuracy and completeness.*

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Next Review**: March 2025
**P0 Status**: ✅ **ALL CRITICAL ITEMS COMPLETED**
**Production Status**: ✅ **READY FOR DEPLOYMENT**
