import asyncio
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_auth import main as test_auth
from tests.test_permissions import test_permission_system
from tests.test_resource_controller import test_resource_controller
from tests.test_comprehensive_permissions import test_comprehensive_permissions
from tests.test_real_permissions import test_real_permissions
from tests.test_user_permissions import test_user_permissions
from tests.test_user_scoped_tokens import test_user_scoped_tokens
from tests.test_user_authentication import test_user_authentication

async def run_tests():
    """Run all tests in sequence."""
    print("=" * 80)
    print("RUNNING AUTH TESTS")
    print("=" * 80)
    await test_auth()

    print("\n" + "=" * 80)
    print("RUNNING PERMISSION TESTS")
    print("=" * 80)
    test_permission_system()

    print("\n" + "=" * 80)
    print("RUNNING RESOURCE CONTROLLER TESTS")
    print("=" * 80)
    test_resource_controller()

    print("\n" + "=" * 80)
    print("RUNNING COMPREHENSIVE PERMISSION TESTS")
    print("=" * 80)
    test_comprehensive_permissions()

    print("\n" + "=" * 80)
    print("RUNNING REAL PERMISSION TESTS")
    print("=" * 80)
    test_real_permissions()

    print("\n" + "=" * 80)
    print("RUNNING USER PERMISSION TESTS")
    print("=" * 80)
    test_user_permissions()

    print("\n" + "=" * 80)
    print("RUNNING USER-SCOPED TOKEN TESTS")
    print("=" * 80)
    test_user_scoped_tokens()

    print("\n" + "=" * 80)
    print("RUNNING USER AUTHENTICATION TESTS")
    print("=" * 80)
    await test_user_authentication()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_tests())
