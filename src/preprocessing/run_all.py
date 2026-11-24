#!/usr/bin/env python3"
"""
Run all preprocessing pipelines.
Run: python -m src.preprocessing.run_all
"""

import subprocess
import sys
from pathlib import Path


def run_preprocessing(script_name: str) -> bool:
    """Run a preprocessing script and return success status."""
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
        "preprocess_recipes.py",
        "preprocess_indb.py"
    ]

    all_passed = True
    for script in scripts:
        passed = run_preprocessing(script)
        if not passed:
            print(f"\n❌ {script} FAILED")
            all_passed = False
        else:
            print(f"\n✅ {script} PASSED")

    print(f"\n{'='*60}")
    if all_passed:
        print("ALL PREPROCESSING COMPLETED ✅")
        sys.exit(0)
    else:
        print("SOME PREPROCESSING FAILED ❌")
        sys.exit(1)


if __name__ == "__main__":
    main()