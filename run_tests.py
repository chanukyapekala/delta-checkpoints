#!/usr/bin/env python3
"""
Test runner for Delta Checkpoints Data Source

This script runs all tests for the delta checkpoint data source.
Can be used as an alternative to running pytest directly.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run all tests using pytest."""
    # Check if we're in a Poetry environment
    try:
        # Try to run pytest through Poetry
        result = subprocess.run(
            ["poetry", "run", "pytest", "-v"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode
        
    except FileNotFoundError:
        print("Poetry not found. Please install Poetry or run tests manually:")
        print("  poetry install")
        print("  poetry run pytest")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_demo():
    """Run the demo script."""
    try:
        result = subprocess.run(
            ["poetry", "run", "python", "demo.py"],
            cwd=Path(__file__).parent
        )
        return result.returncode
    except FileNotFoundError:
        print("Poetry not found. Please install Poetry or run demo manually:")
        print("  poetry install")
        print("  poetry run python demo.py")
        return 1


def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "demo":
            exit_code = run_demo()
        elif command == "test" or command == "tests":
            exit_code = run_tests()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: test, demo")
            exit_code = 1
    else:
        # Default to running tests
        exit_code = run_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 