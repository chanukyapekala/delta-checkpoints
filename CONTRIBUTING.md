# Contributing to Delta Checkpoints

Thank you for your interest in contributing to Delta Checkpoints! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

We welcome contributions from the community! Here are the main ways you can contribute:

### 🐛 Reporting Bugs

- Use the [GitHub Issues](https://github.com/yourusername/delta-checkpoints/issues) page
- Include a clear description of the bug
- Provide steps to reproduce the issue
- Include your environment details (Python version, PySpark version, etc.)

### 💡 Suggesting Enhancements

- Use the [GitHub Issues](https://github.com/yourusername/delta-checkpoints/issues) page
- Describe the enhancement clearly
- Explain why this enhancement would be useful
- Provide examples if possible

### 🔧 Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   pytest
   ```
5. **Format your code**
   ```bash
   black .
   isort .
   ```
6. **Check code quality**
   ```bash
   flake8 delta_checkpoints tests
   mypy delta_checkpoints
   ```
7. **Commit your changes**
   ```bash
   git commit -m "Add feature: description of your changes"
   ```
8. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Create a Pull Request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.7+
- Git
- Poetry (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/delta-checkpoints.git
   cd delta-checkpoints
   ```

2. **Install dependencies**
   ```bash
   # Using Poetry (recommended)
   poetry install --with dev,test
   
   # Or using pip
   pip install -e ".[dev,test]"
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=delta_checkpoints

# Run specific test file
pytest tests/test_delta_checkpoint_source.py

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Place test files in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Use pytest fixtures for common setup
- Aim for good test coverage

### Example Test

```python
def test_new_feature():
    """Test the new feature functionality."""
    # Arrange
    expected_result = "expected"
    
    # Act
    result = some_function()
    
    # Assert
    assert result == expected_result
```

## 📝 Code Style

We use several tools to maintain code quality:

### Black (Code Formatting)
```bash
# Format code
black .

# Check formatting
black --check .
```

### isort (Import Sorting)
```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

### Flake8 (Linting)
```bash
# Run linter
flake8 delta_checkpoints tests
```

### MyPy (Type Checking)
```bash
# Run type checker
mypy delta_checkpoints
```

## 📋 Pull Request Guidelines

### Before Submitting

1. **Ensure all tests pass**
   ```bash
   pytest
   ```

2. **Run all quality checks**
   ```bash
   make check-all
   ```

3. **Update documentation** if needed

4. **Add tests** for new features

5. **Update version** if necessary

### Pull Request Template

Use this template when creating a pull request:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

## 🏷️ Versioning

We follow [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Updating Version

1. Update version in `pyproject.toml`
2. Update version in `delta_checkpoints/__init__.py`
3. Create a git tag
4. Update CHANGELOG.md

## 📚 Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Follow Google or NumPy docstring style
- Include type hints for function parameters and return values

### Example Docstring

```python
def read_checkpoint(spark: SparkSession, path: str) -> DataFrame:
    """Read checkpoint data from the specified path.
    
    Args:
        spark: SparkSession instance
        path: Path to the checkpoint directory
        
    Returns:
        DataFrame containing checkpoint information
        
    Raises:
        AnalysisException: If the checkpoint path does not exist
    """
    pass
```

## 🚀 Release Process

### For Maintainers

1. **Update version numbers**
2. **Update CHANGELOG.md**
3. **Create release branch**
4. **Run full test suite**
5. **Build package**
   ```bash
   poetry build
   ```
6. **Test package locally**
   ```bash
   pip install dist/delta_checkpoints-*.whl
   ```
7. **Publish to PyPI**
   ```bash
   poetry publish
   ```
8. **Create GitHub release**
9. **Merge to main**

## 🆘 Getting Help

If you need help with contributing:

- 📧 Email: your.email@example.com
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/delta-checkpoints/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/delta-checkpoints/issues)

## 📄 License

By contributing to Delta Checkpoints, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to Delta Checkpoints! 🎉 