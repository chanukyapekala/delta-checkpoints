# Publishing Guide for Delta Checkpoints

This guide explains how to publish the delta-checkpoints package to PyPI so that users can install it with `pip install delta-checkpoints`.

## 🚀 Quick Publishing

### Option 1: Automated Publishing (Recommended)

1. **Create a GitHub Release**
   - Go to your GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag version: `v0.1.0`
   - Title: `Release v0.1.0`
   - Description: Copy from CHANGELOG.md
   - Publish the release

2. **GitHub Actions will automatically publish to PyPI**

### Option 2: Manual Publishing

```bash
# Build and publish
make publish

# Or use the script directly
./scripts/publish.sh
```

## 📋 Prerequisites

### 1. PyPI Account

1. **Create a PyPI account** at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Create a Test PyPI account** at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)

### 2. API Tokens

1. **Generate PyPI API Token**:
   - Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - Create a new token with "Entire account" scope
   - Copy the token

2. **Generate Test PyPI API Token**:
   - Go to [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
   - Create a new token with "Entire account" scope
   - Copy the token

### 3. Configure Poetry

```bash
# Configure PyPI token
poetry config pypi-token.pypi YOUR_PYPI_TOKEN

# Configure Test PyPI token
poetry config pypi-token.testpypi YOUR_TEST_PYPI_TOKEN

# Add Test PyPI repository
poetry config repositories.testpypi https://test.pypi.org/legacy/
```

### 4. GitHub Secrets (for automated publishing)

Add these secrets to your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add `PYPI_API_TOKEN` with your PyPI API token

## 🔧 Publishing Process

### Step 1: Prepare for Release

```bash
# Update version (choose one)
make version-patch    # 0.1.0 → 0.1.1
make version-minor    # 0.1.0 → 0.2.0
make version-major    # 0.1.0 → 1.0.0

# Or manually
poetry version patch  # or minor/major
```

### Step 2: Update Documentation

1. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to the new version section
   - Update the release date

2. **Update README.md** if needed

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Prepare release v$(poetry version -s)"
   ```

### Step 3: Test Locally

```bash
# Run all checks
make check-all

# Build package
make build

# Test package locally
pip install dist/delta_checkpoints-*.whl
python -c "import delta_checkpoints; print('Success!')"
```

### Step 4: Publish

#### Test PyPI (Recommended for first-time publishers)

```bash
# Publish to Test PyPI
make publish-test

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ delta-checkpoints
```

#### Production PyPI

```bash
# Publish to PyPI
make publish

# Verify installation
pip install delta-checkpoints
```

## 🛠️ Publishing Script Options

The `scripts/publish.sh` script supports various options:

```bash
# Basic publishing (patch version to PyPI)
./scripts/publish.sh

# Publish to Test PyPI
./scripts/publish.sh --test-pypi

# Version bumping
./scripts/publish.sh --major
./scripts/publish.sh --minor
./scripts/publish.sh --patch

# Skip certain steps
./scripts/publish.sh --skip-tests
./scripts/publish.sh --skip-checks
./scripts/publish.sh --skip-local-test
./scripts/publish.sh --skip-push

# Show help
./scripts/publish.sh --help
```

## 📦 Package Structure

Your package will be published with this structure:

```
delta-checkpoints-0.1.0/
├── delta_checkpoints/
│   ├── __init__.py
│   ├── delta_checkpoint_source.py
│   └── spark_integration.py
├── examples/
│   └── usage_example.py
├── tests/
│   └── test_delta_checkpoint_source.py
├── README.md
├── LICENSE
├── CHANGELOG.md
└── pyproject.toml
```

## 🔍 Verification

After publishing, verify your package:

### 1. Check PyPI Listing

Visit: https://pypi.org/project/delta-checkpoints/

### 2. Test Installation

```bash
# Create a new virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the package
pip install delta-checkpoints

# Test basic functionality
python -c "
from pyspark.sql import SparkSession
import delta_checkpoints
print('Installation successful!')
"
```

### 3. Test with Spark

```bash
# Install PySpark
pip install pyspark

# Test the data source
python -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('test').getOrCreate()
print('Spark integration successful!')
"
```

## 🚨 Troubleshooting

### Common Issues

1. **"Package already exists"**
   - The version already exists on PyPI
   - Bump the version: `poetry version patch`

2. **"Authentication failed"**
   - Check your API token
   - Reconfigure: `poetry config pypi-token.pypi YOUR_TOKEN`

3. **"Package check failed"**
   - Run: `poetry run twine check dist/*`
   - Fix any issues in your package

4. **"Import error after installation"**
   - Check your `__init__.py` exports
   - Verify the package structure

### Debug Commands

```bash
# Check package contents
tar -tzf dist/delta_checkpoints-*.tar.gz

# Check wheel contents
unzip -l dist/delta_checkpoints-*.whl

# Validate package
poetry run twine check dist/*

# Test package locally
pip install --force-reinstall dist/delta_checkpoints-*.whl
```

## 📈 Post-Publishing

### 1. Monitor Usage

- Check PyPI download statistics
- Monitor GitHub repository activity
- Watch for issues and feedback

### 2. Update Documentation

- Update any external documentation
- Share on relevant forums/communities
- Consider writing a blog post

### 3. Plan Next Release

- Collect feedback and feature requests
- Plan the next version
- Update the roadmap

## 🔗 Useful Links

- [PyPI](https://pypi.org/) - Python Package Index
- [Test PyPI](https://test.pypi.org/) - Test Python Package Index
- [Poetry Documentation](https://python-poetry.org/docs/) - Poetry package manager
- [PyPA Packaging Guide](https://packaging.python.org/) - Python packaging guide
- [Semantic Versioning](https://semver.org/) - Version numbering guide

## 📞 Support

If you encounter issues during publishing:

- Check the [troubleshooting section](#-troubleshooting)
- Review the [Poetry documentation](https://python-poetry.org/docs/)
- Open an issue on GitHub
- Contact the maintainers

---

**Happy Publishing! 🎉** 