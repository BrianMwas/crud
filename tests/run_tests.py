import asyncio
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_auth import main as test_auth
from tests.test_permissions import test_permission_system
from tests.test_resource_controller import test_resource_controller

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
    print("ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_tests())
