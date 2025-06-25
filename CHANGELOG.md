# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Core delta checkpoint data source functionality
- Spark integration for format API support
- Comprehensive test suite
- Documentation and examples

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.0] - 2024-01-XX

### Added
- **Initial Release**: First public release of delta-checkpoints
- **Core Features**:
  - `DeltaCheckpointDataSource` class for reading checkpoint data
  - Support for reading offset, metadata, and commit information
  - Flexible parsing of JSON and key-value checkpoint files
  - Error handling for missing or corrupted checkpoint files
  - SQL support through DataFrame API
- **Spark Integration**:
  - `spark.read.format("delta-checkpoint").load()` syntax support
  - Automatic registration of data source with Spark
  - Convenience function `read_delta_checkpoint()`
- **Data Schema**:
  - Standardized schema with type, source, partition, offset, metadata, and timestamp fields
  - JSON serialization of metadata for easy querying
- **Documentation**:
  - Comprehensive README with usage examples
  - Contributing guidelines
  - API documentation
- **Testing**:
  - Complete test suite with pytest
  - Coverage reporting
  - Integration tests
- **Development Tools**:
  - Poetry for dependency management
  - Pre-commit hooks for code quality
  - Black, isort, flake8, and mypy configuration
  - Makefile for common development tasks

### Technical Details
- **Dependencies**: PySpark >= 3.0.0, py4j >= 0.10.9
- **Python Support**: 3.7, 3.8, 3.9, 3.10, 3.11
- **License**: Apache License 2.0
- **Platform**: Cross-platform (Linux, macOS, Windows)

---

## Version History

### Version 0.1.0
- **Release Date**: 2024-01-XX
- **Status**: Initial release
- **Key Features**: Core checkpoint reading functionality, Spark integration, comprehensive testing
- **Breaking Changes**: None (initial release)

---

## Contributing

To add entries to this changelog:

1. Add your changes under the `[Unreleased]` section
2. Use the appropriate category:
   - **Added** for new features
   - **Changed** for changes in existing functionality
   - **Deprecated** for soon-to-be removed features
   - **Removed** for now removed features
   - **Fixed** for any bug fixes
   - **Security** for security-related changes

3. When releasing:
   - Move `[Unreleased]` content to a new version section
   - Update the release date
   - Create a git tag for the version

## Links

- [PyPI Package](https://pypi.org/project/delta-checkpoints/)
- [GitHub Repository](https://github.com/yourusername/delta-checkpoints)
- [Documentation](https://github.com/yourusername/delta-checkpoints#readme) 