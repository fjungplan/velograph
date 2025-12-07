#!/usr/bin/env python3
"""Verify test infrastructure fix by running a subset of tests."""

import subprocess
import sys

def run_tests(test_path, description):
    """Run tests and return pass/fail count."""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Path: {test_path}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short", "-q"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Run test verification suite."""
    tests = [
        ("tests/test_health.py", "Health endpoint tests"),
        ("tests/test_dto.py", "Data transfer object tests"),
        ("tests/test_main.py", "Main app tests"),
        ("tests/test_auth_service.py", "Auth service tests"),
        ("tests/test_migrations.py", "Database migration tests"),
    ]
    
    results = {}
    for test_path, description in tests:
        try:
            results[description] = run_tests(test_path, description)
        except subprocess.TimeoutExpired:
            print(f"⏱️  TIMEOUT: {description}")
            results[description] = False
        except Exception as e:
            print(f"❌ ERROR: {description} - {e}")
            results[description] = False
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for description, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {description}")
    
    print(f"\nTotal: {passed}/{total} test modules passed\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
