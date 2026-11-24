"""Complete Stage 2 Audit - Full Test Run"""

import subprocess

print("Running full test suite...")
result = subprocess.run(['py', '-m', 'pytest', 'tests/', '-v', '--tb=no'], 
                       capture_output=True, text=True, timeout=180)

output = result.stdout
lines = output.strip().split('\n')

passed = 0
failed = 0
skipped = 0
errors = 0

for l in lines:
    if 'PASSED' in l:
        passed += 1
    elif 'FAILED' in l:
        failed += 1
    elif 'SKIPPED' in l:
        skipped += 1
    elif 'ERROR' in l:
        errors += 1

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Skipped: {skipped}")
print(f"Errors: {errors}")
print(f"Total: {passed + failed + skipped + errors}")

# List all test names
print("\nAll tests:")
for l in lines:
    if any(x in l for x in ['PASSED', 'FAILED', 'SKIPPED', 'ERROR']):
        # Extract test name
        parts = l.strip().split(' ')
        for p in parts:
            if '::' in p or 'test_' in p:
                print(f"  {p}")
                break

# Also check for the summary line
for l in lines:
    if 'passed' in l and 'failed' in l:
        print(f"\nSummary: {l.strip()}")