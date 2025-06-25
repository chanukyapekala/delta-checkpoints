#!/bin/bash

# Delta Checkpoints PyPI Publishing Script
# This script automates the process of publishing to PyPI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository. Please run this script from the project root."
        exit 1
    fi
}

# Function to check if there are uncommitted changes
check_clean_working_dir() {
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes. Please commit or stash them before publishing."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to get current version
get_current_version() {
    poetry version -s
}

# Function to update version
update_version() {
    local version_type=$1
    print_status "Updating version ($version_type)..."
    poetry version $version_type
    local new_version=$(get_current_version)
    print_success "Version updated to $new_version"
    
    # Update version in __init__.py
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" delta_checkpoints/__init__.py
    rm delta_checkpoints/__init__.py.bak
    print_success "Updated version in __init__.py"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    if ! poetry run pytest; then
        print_error "Tests failed. Please fix the issues before publishing."
        exit 1
    fi
    print_success "All tests passed!"
}

# Function to run quality checks
run_quality_checks() {
    print_status "Running quality checks..."
    
    # Check code formatting
    if ! poetry run black --check .; then
        print_error "Code formatting check failed. Run 'poetry run black .' to fix."
        exit 1
    fi
    
    # Check import sorting
    if ! poetry run isort --check-only .; then
        print_error "Import sorting check failed. Run 'poetry run isort .' to fix."
        exit 1
    fi
    
    # Check linting
    if ! poetry run flake8 delta_checkpoints tests; then
        print_error "Linting check failed. Please fix the issues."
        exit 1
    fi
    
    # Check types
    if ! poetry run mypy delta_checkpoints; then
        print_error "Type checking failed. Please fix the issues."
        exit 1
    fi
    
    print_success "All quality checks passed!"
}

# Function to build package
build_package() {
    print_status "Building package..."
    poetry build
    print_success "Package built successfully!"
}

# Function to check package
check_package() {
    print_status "Checking package..."
    if ! poetry run twine check dist/*; then
        print_error "Package check failed."
        exit 1
    fi
    print_success "Package check passed!"
}

# Function to test package locally
test_package_locally() {
    print_status "Testing package locally..."
    local package_file=$(ls dist/delta_checkpoints-*.whl | head -1)
    if [ -z "$package_file" ]; then
        print_error "No wheel file found in dist/"
        exit 1
    fi
    
    # Create temporary environment for testing
    python -m venv temp_test_env
    source temp_test_env/bin/activate
    
    # Install the package
    pip install "$package_file"
    
    # Test basic import
    python -c "import delta_checkpoints; print('Import successful')"
    
    # Clean up
    deactivate
    rm -rf temp_test_env
    
    print_success "Local package test passed!"
}

# Function to publish to PyPI
publish_to_pypi() {
    local test_pypi=$1
    local repository=""
    
    if [ "$test_pypi" = "true" ]; then
        print_status "Publishing to Test PyPI..."
        repository="--repository testpypi"
    else
        print_status "Publishing to PyPI..."
    fi
    
    if ! poetry publish $repository --build; then
        print_error "Publishing failed."
        exit 1
    fi
    
    if [ "$test_pypi" = "true" ]; then
        print_success "Published to Test PyPI successfully!"
        print_warning "You can test the package with: pip install --index-url https://test.pypi.org/simple/ delta-checkpoints"
    else
        print_success "Published to PyPI successfully!"
        print_success "You can install the package with: pip install delta-checkpoints"
    fi
}

# Function to create git tag
create_git_tag() {
    local version=$(get_current_version)
    print_status "Creating git tag v$version..."
    
    if git tag -l "v$version" | grep -q "v$version"; then
        print_warning "Tag v$version already exists. Skipping tag creation."
    else
        git tag "v$version"
        print_success "Git tag v$version created!"
    fi
}

# Function to push changes
push_changes() {
    print_status "Pushing changes to remote..."
    git add .
    git commit -m "Release version $(get_current_version)"
    git push origin main
    git push --tags
    print_success "Changes pushed to remote!"
}

# Main function
main() {
    print_status "Starting Delta Checkpoints publishing process..."
    
    # Check prerequisites
    if ! command_exists poetry; then
        print_error "Poetry is not installed. Please install Poetry first."
        exit 1
    fi
    
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check environment
    check_git_repo
    check_clean_working_dir
    
    # Parse arguments
    local version_type="patch"
    local test_pypi=false
    local skip_tests=false
    local skip_checks=false
    local skip_local_test=false
    local skip_push=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --major)
                version_type="major"
                shift
                ;;
            --minor)
                version_type="minor"
                shift
                ;;
            --patch)
                version_type="patch"
                shift
                ;;
            --test-pypi)
                test_pypi=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --skip-checks)
                skip_checks=true
                shift
                ;;
            --skip-local-test)
                skip_local_test=true
                shift
                ;;
            --skip-push)
                skip_push=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --major           Bump major version"
                echo "  --minor           Bump minor version (default)"
                echo "  --patch           Bump patch version"
                echo "  --test-pypi       Publish to Test PyPI instead of PyPI"
                echo "  --skip-tests      Skip running tests"
                echo "  --skip-checks     Skip quality checks"
                echo "  --skip-local-test Skip local package testing"
                echo "  --skip-push       Skip pushing to git"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Show current version
    local current_version=$(get_current_version)
    print_status "Current version: $current_version"
    
    # Confirm action
    if [ "$test_pypi" = "true" ]; then
        print_warning "This will publish to Test PyPI"
    else
        print_warning "This will publish to PyPI (production)"
    fi
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Publishing cancelled."
        exit 0
    fi
    
    # Run checks
    if [ "$skip_tests" != "true" ]; then
        run_tests
    fi
    
    if [ "$skip_checks" != "true" ]; then
        run_quality_checks
    fi
    
    # Update version
    update_version $version_type
    
    # Build and check package
    build_package
    check_package
    
    # Test package locally
    if [ "$skip_local_test" != "true" ]; then
        test_package_locally
    fi
    
    # Publish
    publish_to_pypi $test_pypi
    
    # Create git tag
    create_git_tag
    
    # Push changes
    if [ "$skip_push" != "true" ]; then
        push_changes
    fi
    
    print_success "Publishing process completed successfully!"
    
    if [ "$test_pypi" = "true" ]; then
        echo ""
        print_warning "Package published to Test PyPI."
        print_warning "Test with: pip install --index-url https://test.pypi.org/simple/ delta-checkpoints"
    else
        echo ""
        print_success "Package published to PyPI!"
        print_success "Install with: pip install delta-checkpoints"
    fi
}

# Run main function with all arguments
main "$@" 