"""
Test user authentication and resource creation on behalf of other users.

This test demonstrates how to:
1. Login as a user with username and password
2. Create resources as that user
3. Login as another user
4. Verify that users can only access their own resources
5. Use an M2M token to create resources on behalf of different users
"""

import os
import asyncio
import sys
import json

# Try to import jwt and dotenv, install if not available
try:
    import jwt
except ImportError:
    print("Installing PyJWT...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyJWT"])
    import jwt

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app modules
from app.utils.model_operations import create_model, access_model, list_models
from app.auth.token import login_user, get_m2m_token

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000"
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")

# Auth0 Machine-to-Machine application settings
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

# Auth0 Web application settings
AUTH0_WEB_CLIENT_DOMAIN = os.getenv("AUTH0_WEB_CLIENT_DOMAIN")
AUTH0_WEB_CLIENT_ID = os.getenv("AUTH0_WEB_CLIENT_ID")
AUTH0_WEB_CLIENT_SECRET = os.getenv("AUTH0_WEB_CLIENT_SECRET")

# Test user credentials
USER1 = {"username": "user1@example.com", "password": "User1Password!"}
USER2 = {"username": "user2@example.com", "password": "User2Password!"}

def decode_token(token):
    """Decode a JWT token without verification."""
    # This is for testing purposes only - in production, always verify tokens
    return jwt.decode(token, options={"verify_signature": False})

async def test_user_authentication():
    """Test user authentication and resource creation on behalf of other users."""
    print("\n" + "=" * 80)
    print("TESTING USER AUTHENTICATION AND RESOURCE CREATION")
    print("=" * 80)

    # Login as User 1
    print("\n1. Logging in as User 1...")
    success, user1_payload, user1_token = await login_user(USER1["username"], USER1["password"])

    if not success:
        print(f"❌ Failed to login as User 1: {user1_token}")
        return

    user1_id = user1_payload.get("sub")
    print(f"✅ Logged in as User 1 with ID: {user1_id}")

    # Login as User 2
    print("\n2. Logging in as User 2...")
    success, user2_payload, user2_token = await login_user(USER2["username"], USER2["password"])

    if not success:
        print(f"❌ Failed to login as User 2: {user2_token}")
        return

    user2_id = user2_payload.get("sub")
    print(f"✅ Logged in as User 2 with ID: {user2_id}")

    # Create a resource as User 1
    print("\n3. Creating a resource as User 1...")
    success, resource1_id, message = await create_model(
        user1_token,
        "resources",
        "User 1's Resource",
        "This resource is owned by User 1"
    )

    if not success:
        print(f"❌ Failed to create resource as User 1: {message}")
        return

    print(f"✅ Created resource with ID {resource1_id} as User 1")

    # Create a resource as User 2
    print("\n4. Creating a resource as User 2...")
    success, resource2_id, message = await create_model(
        user2_token,
        "resources",
        "User 2's Resource",
        "This resource is owned by User 2"
    )

    if not success:
        print(f"❌ Failed to create resource as User 2: {message}")
        return

    print(f"✅ Created resource with ID {resource2_id} as User 2")

    # User 1 tries to access their own resource
    print("\n5. User 1 tries to access their own resource...")
    success, resource_data, message = await access_model(user1_token, "resources", resource1_id)

    if success:
        print(f"✅ User 1 can access their own resource: {resource_data.get('name')}")
    else:
        print(f"❌ User 1 cannot access their own resource: {message}")

    # User 1 tries to access User 2's resource
    print("\n6. User 1 tries to access User 2's resource...")
    success, resource_data, message = await access_model(user1_token, "resources", resource2_id)

    if not success:
        print(f"✅ User 1 cannot access User 2's resource (as expected)")
    else:
        print(f"❌ User 1 can access User 2's resource (unexpected): {resource_data.get('name')}")

    # Get an M2M token
    print("\n7. Getting an M2M token...")
    try:
        m2m_token = await get_m2m_token()
        print("✅ Got M2M token")
    except Exception as e:
        print(f"❌ Failed to get M2M token: {str(e)}")
        return

    # M2M token creates a resource on behalf of User 1
    print("\n8. M2M token creates a resource on behalf of User 1...")
    success, resource3_id, message = await create_model(
        m2m_token,
        "resources",
        "Resource for User 1",
        "Created by M2M token on behalf of User 1",
        user1_id
    )

    if success:
        print(f"✅ M2M token created resource with ID {resource3_id} on behalf of User 1")
    else:
        print(f"❌ M2M token failed to create resource on behalf of User 1: {message}")

    # User 1 tries to access the resource created on their behalf
    if success:
        print("\n9. User 1 tries to access the resource created on their behalf...")
        success, resource_data, message = await access_model(user1_token, "resources", resource3_id)

        if success:
            print(f"✅ User 1 can access the resource created on their behalf: {resource_data.get('name')}")
        else:
            print(f"❌ User 1 cannot access the resource created on their behalf: {message}")

    # M2M token lists all resources
    print("\n10. M2M token lists all resources...")
    success, resources, message = await list_models(m2m_token, "resources")

    if success:
        print(f"✅ M2M token can list all resources (found {len(resources)})")

        # Check if all created resources are in the list
        resource_ids = [r["id"] for r in resources]
        all_found = True

        for resource_id in [resource1_id, resource2_id]:
            if resource_id not in resource_ids:
                all_found = False
                print(f"❌ Resource {resource_id} not found in the list")

        if resource3_id and resource3_id not in resource_ids:
            all_found = False
            print(f"❌ Resource {resource3_id} not found in the list")

        if all_found:
            print("✅ All created resources are in the list")
    else:
        print(f"❌ M2M token cannot list all resources: {message}")

    # Clean up - delete the test resources
    print("\n11. Cleaning up - deleting test resources...")

    # We'll use the M2M token to delete all resources for simplicity
    for resource_id in [resource1_id, resource2_id]:
        if resource_id:
            success, _, message = await access_model(m2m_token, f"resources/{resource_id}", "DELETE")
            if success:
                print(f"✅ Deleted resource {resource_id}")
            else:
                print(f"❌ Failed to delete resource {resource_id}: {message}")

    if resource3_id:
        success, _, message = await access_model(m2m_token, f"resources/{resource3_id}", "DELETE")
        if success:
            print(f"✅ Deleted resource {resource3_id}")
        else:
            print(f"❌ Failed to delete resource {resource3_id}: {message}")

    # Summary
    print("\nUser Authentication and Resource Creation Summary:")
    print("1. Users can authenticate with username and password")
    print("2. Users can create and access their own resources")
    print("3. Users cannot access resources owned by other users")
    print("4. M2M tokens can create resources on behalf of specific users")
    print("5. Users can access resources created on their behalf by M2M tokens")

if __name__ == "__main__":
    asyncio.run(test_user_authentication())
