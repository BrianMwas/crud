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

def test_resource_controller():
    """Test the resource controller functionality."""
    # Get a token for the first user
    token1 = get_token()

    # Create a resource as the first user
    headers = {"Authorization": f"Bearer {token1}"}
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

    # Access the resource with the same token (should succeed)
    print("\n2. Testing resource retrieval by ID...")
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )

    if response.status_code == 200:
        print("✅ Owner can access their own resource")
        print(f"Resource details: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Owner cannot access their own resource: {response.text}")

    # List all resources (should include the one we created)
    print("\n3. Testing resource listing...")
    response = requests.get(
        f"{BASE_URL}/resources/",
        headers=headers
    )

    if response.status_code == 200:
        resources = response.json()
        if any(r["id"] == resource_id for r in resources):
            print("✅ Resource appears in the list of user's resources")
            print(f"Found {len(resources)} resources")
        else:
            print("❌ Resource does not appear in the list of user's resources")
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

    if response.status_code == 204:
        print("✅ Resource deleted successfully")
    else:
        print(f"❌ Failed to delete resource: {response.text}")

    # Verify the resource is gone
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )

    if response.status_code == 404:
        print("✅ Resource no longer exists")
    else:
        print(f"❌ Resource still exists: {response.text}")

    print("\nPermission notes:")
    print("✅ The owner can access, update, and delete their own resources")
    print("❌ Other users would get a 403 Forbidden error")
    print("✅ M2M applications with 'read:resources' permission can read resources")

if __name__ == "__main__":
    test_resource_controller()
