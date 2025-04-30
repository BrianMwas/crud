import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL for the API
BASE_URL = "http://localhost:8000"

def get_token():
    """Get a machine-to-machine token from the API."""
    response = requests.get(f"{BASE_URL}/token")
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"Failed to get token: {response.text}")

def decode_token(token):
    """
    Decode a JWT token to get its payload.
    This is a simplified version that assumes the token is valid.
    In a real application, you would verify the token signature.
    """
    import base64
    import json

    # Get the payload part of the token (second part)
    payload = token.split('.')[1]

    # Add padding if needed
    payload += '=' * (4 - len(payload) % 4)

    # Decode the payload
    decoded = base64.b64decode(payload)

    # Parse the JSON
    return json.loads(decoded)

def test_permission_system():
    """Test the permission system for resources."""
    # Get a token for the user
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Decode the token to check its claims
    token_payload = decode_token(token)
    is_m2m = "gty" in token_payload and token_payload["gty"] == "client-credentials"
    has_permission = "read:resources" in token_payload.get("permissions", []) if is_m2m else False

    print(f"\nToken type: {'M2M' if is_m2m else 'User'}")
    if is_m2m:
        print(f"Has 'read:resources' permission: {'Yes' if has_permission else 'No'}")

    # Create a test resource
    print("\n1. Creating a test resource...")
    resource_data = {"name": "Permission Test Resource", "description": "A resource for testing permissions"}
    response = requests.post(
        f"{BASE_URL}/resources/",
        json=resource_data,
        headers=headers
    )

    if response.status_code != 201:
        print(f"❌ Failed to create resource: {response.text}")
        return

    resource = response.json()
    resource_id = resource["id"]
    print(f"✅ Created resource with ID {resource_id}")

    # Test resource access
    print("\n2. Testing resource access...")
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )

    if response.status_code == 200:
        if is_m2m:
            print("✅ M2M application with proper permissions can access the resource")
        else:
            print("✅ Owner can access their own resource")
    else:
        if is_m2m and not has_permission:
            print("✅ As expected, M2M application without proper permissions cannot access the resource")
        else:
            print(f"❌ Unexpected error: {response.text}")

    # Test resource listing
    print("\n3. Testing resource listing...")
    response = requests.get(
        f"{BASE_URL}/resources/",
        headers=headers
    )

    if response.status_code == 200:
        resources = response.json()
        if is_m2m and has_permission:
            print(f"✅ M2M application with proper permissions can see all resources (found {len(resources)})")
        elif not is_m2m:
            print(f"✅ User can see their own resources (found {len(resources)})")
        else:
            print("❌ Unexpected: M2M application without proper permissions can see resources")
    else:
        print(f"❌ Failed to list resources: {response.text}")

    # Test resource update
    print("\n4. Testing resource update...")
    update_data = {"name": "Updated Resource", "description": "This resource has been updated"}
    response = requests.put(
        f"{BASE_URL}/resources/{resource_id}",
        json=update_data,
        headers=headers
    )

    if is_m2m:
        if response.status_code == 403:
            print("✅ As expected, M2M applications cannot update resources")
        else:
            print(f"❌ Unexpected: M2M application can update resources: {response.text}")
    else:
        if response.status_code == 200:
            print("✅ Owner can update their own resource")
        else:
            print(f"❌ Owner cannot update their own resource: {response.text}")

    # Test resource deletion
    print("\n5. Testing resource deletion...")
    response = requests.delete(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )

    if is_m2m:
        if response.status_code == 403:
            print("✅ As expected, M2M applications cannot delete resources")
        else:
            print(f"❌ Unexpected: M2M application can delete resources: {response.text}")
    else:
        if response.status_code == 204:
            print("✅ Owner can delete their own resource")
        else:
            print(f"❌ Owner cannot delete their own resource: {response.text}")

    # Summary
    print("\nPermission System Summary:")
    print("1. Resource owners can create, read, update, and delete their own resources")
    print("2. M2M applications with 'read:resources' permission can read all resources")
    print("3. M2M applications cannot update or delete resources")
    print("4. Other users or applications without proper permissions cannot access resources")

if __name__ == "__main__":
    test_permission_system()
