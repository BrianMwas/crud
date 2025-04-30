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

def is_m2m_token(token):
    """Check if a token is an M2M token by looking for the 'gty' claim."""
    token_payload = decode_token(token)
    return "gty" in token_payload and token_payload["gty"] == "client-credentials"

def has_permission(token, permission):
    """Check if a token has a specific permission."""
    token_payload = decode_token(token)
    return permission in token_payload.get("permissions", [])

def test_resource_controller():
    """Test the resource controller functionality."""
    # Get a token
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Decode the token to check its claims
    token_payload = decode_token(token)
    is_m2m = "gty" in token_payload and token_payload["gty"] == "client-credentials"
    has_read_permission = "read:resources" in token_payload.get("permissions", []) if is_m2m else False

    print(f"\nToken type: {'M2M' if is_m2m else 'User'}")
    if is_m2m:
        print(f"Has 'read:resources' permission: {'Yes' if has_read_permission else 'No'}")

    # Create a resource
    resource_data = {"name": "Test Resource", "description": "A test resource"}

    print("\n1. Testing resource creation...")
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

    # Access the resource
    print("\n2. Testing resource retrieval by ID...")
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )

    if response.status_code == 200:
        if is_m2m:
            print("✅ M2M application with proper permissions can access the resource")
        else:
            print("✅ Owner can access their own resource")
        print(f"Resource details: {json.dumps(response.json(), indent=2)}")
    else:
        if is_m2m and not has_read_permission:
            print("✅ As expected, M2M application without proper permissions cannot access the resource")
        else:
            print(f"❌ Unexpected error: {response.text}")

    # List all resources
    print("\n3. Testing resource listing...")
    response = requests.get(
        f"{BASE_URL}/resources/",
        headers=headers
    )

    if response.status_code == 200:
        resources = response.json()
        if is_m2m and has_read_permission:
            print(f"✅ M2M application with proper permissions can see all resources (found {len(resources)})")
            if any(r["id"] == resource_id for r in resources):
                print("✅ The resource we just created is in the list")
            else:
                print("❌ The resource we just created is not in the list")
        elif not is_m2m:
            if any(r["id"] == resource_id for r in resources):
                print("✅ Resource appears in the list of user's resources")
                print(f"Found {len(resources)} resources")
            else:
                print("❌ Resource does not appear in the list of user's resources")
        else:
            print("❌ Unexpected: M2M application without proper permissions can see resources")
    else:
        print(f"❌ Failed to list resources: {response.text}")

    # Update the resource
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
            print(f"❌ Unexpected: M2M application can update resources: {response.status_code} - {response.text}")
    else:
        if response.status_code == 200:
            print("✅ Resource updated successfully")
            print(f"Updated resource: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Failed to update resource: {response.text}")

    # Delete the resource
    print("\n5. Testing resource deletion...")
    response = requests.delete(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )

    if is_m2m:
        if response.status_code == 403:
            print("✅ As expected, M2M applications cannot delete resources")
            print("Note: The resource will remain in the database")
        else:
            print(f"❌ Unexpected: M2M application can delete resources: {response.status_code} - {response.text}")
    else:
        if response.status_code == 204:
            print("✅ Resource deleted successfully")

            # Verify the resource is gone
            response = requests.get(
                f"{BASE_URL}/resources/{resource_id}",
                headers=headers
            )

            if response.status_code == 404:
                print("✅ Resource no longer exists")
            else:
                print(f"❌ Resource still exists: {response.text}")
        else:
            print(f"❌ Failed to delete resource: {response.text}")

    # Summary
    print("\nResource Controller Summary:")
    print("1. Resource owners can create, read, update, and delete their own resources")
    print("2. M2M applications with 'read:resources' permission can read all resources")
    print("3. M2M applications cannot update or delete resources")
    print("4. Other users or applications without proper permissions cannot access resources")

if __name__ == "__main__":
    test_resource_controller()
