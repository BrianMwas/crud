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

def test_permission_system():
    """Test the permission system for resources."""
    # Get a token for the user
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
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
    
    # Test owner access
    print("\n2. Testing owner access...")
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Owner can access their own resource")
    else:
        print(f"❌ Owner cannot access their own resource: {response.text}")
    
    # Simulate access with a different user (by modifying the token)
    # In a real scenario, you would use a different user's token
    print("\n3. Simulating access with a different user...")
    print("Note: This is a simulation. In a real scenario, you would use a different user's token.")
    print("✅ The owner would be able to access their resource")
    print("❌ Other users would get a 403 Forbidden error")
    
    # Simulate access with an M2M application
    print("\n4. Simulating access with an M2M application...")
    print("Note: This is a simulation. In a real scenario, you would use a token from an M2M application.")
    print("✅ M2M applications with 'read:resources' permission would be able to access the resource")
    print("❌ M2M applications without the required permission would get a 403 Forbidden error")
    
    # Clean up - delete the test resource
    print("\n5. Cleaning up - deleting the test resource...")
    response = requests.delete(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print("✅ Resource deleted successfully")
    else:
        print(f"❌ Failed to delete resource: {response.text}")

if __name__ == "__main__":
    test_permission_system()
