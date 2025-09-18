#!/usr/bin/env python3
"""Test runner script for the flash card app."""

import sys
import subprocess
from pathlib import Path


def run_tests(test_type="all", verbose=True):
    """Run tests with specified type and verbosity."""

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if verbose:
        cmd.append("-v")

    # Add test type specific options
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "ui":
        cmd.extend(["-m", "ui"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        print(f"Unknown test type: {test_type}")
        print("Available types: all, unit, integration, ui")
        return False

    # Add coverage if available
    try:
        import coverage

        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    except ImportError:
        print("Coverage not available. Install with: pip install coverage")

    # Run tests
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"

    success = run_tests(test_type)

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
