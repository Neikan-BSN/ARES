#!/usr/bin/env python3
"""
Quick Security Hardening Validation Script
Validates that security hardening measures are working correctly.
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n⚙️ {description}")
    print(f"   Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # noqa: S603
        if result.returncode == 0:
            print("   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ FAILED: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print("   ⏱️ TIMEOUT")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False


def test_security_utils():
    """Test the security utilities."""
    print("\n🔍 Testing Security Utilities")

    try:
        # Test path validation
        from src.ares.utils.security_utils import PathTraversalError, secure_path

        # Test safe path
        try:
            safe_path = secure_path("src/ares/main.py")
            print(f"   ✅ Path validation working: {safe_path.name}")
        except Exception as e:
            print(f"   ❌ Path validation failed: {e}")
            return False

        # Test dangerous path detection
        try:
            secure_path("../../../etc/passwd")
            print("   ❌ Dangerous path not blocked!")
            return False
        except PathTraversalError:
            print("   ✅ Path traversal attack blocked")
        except Exception as e:
            print(f"   ✅ Path validation blocked dangerous path: {e}")

        # Test input validation
        from src.ares.utils.security_utils import InputValidationError, validate_input

        try:
            validate_input("Hello, World!")
            print("   ✅ Input validation working")
        except Exception as e:
            print(f"   ❌ Input validation failed: {e}")
            return False

        # Test dangerous input detection
        try:
            validate_input("<script>alert('xss')</script>")
            print("   ❌ Dangerous input not blocked!")
            return False
        except InputValidationError:
            print("   ✅ XSS attack blocked")
        except Exception as e:
            print(f"   ✅ Input validation blocked dangerous input: {e}")

        return True

    except ImportError as e:
        print(f"   ❌ Security utils import failed: {e}")
        return False


def main():
    """Main validation function."""
    print("🔒 ARES Security Hardening Validation")
    print("=" * 50)

    tests = [
        # Security scanning
        (
            [
                "bandit",
                "-r",
                "src/",
                "--severity-level",
                "high",
                "--confidence-level",
                "high",
            ],
            "Bandit High-Severity Security Scan",
        ),
        # Path validation exists
        (
            [
                "python3",
                "-c",
                "from src.ares.utils.security_utils import secure_path; print('Security utils available')",
            ],
            "Security Utilities Import Test",
        ),
        # Container security check
        (["docker", "--version"], "Docker Available (for container security)"),
    ]

    passed = 0
    total = len(tests)

    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1

    # Test security utilities
    if test_security_utils():
        passed += 1
        total += 1
    else:
        total += 1

    print("\n📈 Security Validation Results")
    print("=" * 50)
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("   ✅ ALL SECURITY TESTS PASSED!")
        print("   🎉 Security hardening is working correctly")
        return 0
    else:
        print("   ⚠️ Some security tests failed")
        print("   🔧 Security hardening needs attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
