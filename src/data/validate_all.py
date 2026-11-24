#!/usr/bin/env python3
"""
Run all dataset validation scripts.
Run: python -m src.data.validate_all
"""

import subprocess
import sys
from pathlib import Path


def run_validation(script_name: str) -> bool:
    """Run a validation script and return success status."""
    script_path = Path(__file__).parent / script_name
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main():
    scripts = [
        "validate_recipe.py",
        "validate_indb.py",
        "validate_usda.py",
        "validate_nhanes.py"
    ]

    all_passed = True
    for script in scripts:
        passed = run_validation(script)
        if not passed:
            print(f"\n❌ {script} FAILED")
            all_passed = False
        else:
            print(f"\n✅ {script} PASSED")

    print(f"\n{'='*60}")
    if all_passed:
        print("ALL VALIDATIONS PASSED ✅")
        sys.exit(0)
    else:
        print("SOME VALIDATIONS FAILED ❌")
        sys.exit(1)


if __name__ == "__main__":
    main()