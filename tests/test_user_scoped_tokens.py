"""
Test the user-scoped token functionality.

This test demonstrates how to:
1. Get a regular M2M token
2. Get a user-scoped token
3. Create resources on behalf of different users
4. Verify that users can only access their own resources
"""

import os
import json
import requests
import jwt
from dotenv import load_dotenv
import sys

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000"
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

def get_token(user_id=None):
    """Get a token from the API, optionally scoped to a specific user."""
    url = f"{BASE_URL}/token"
    if user_id:
        url += f"?user_id={user_id}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    return data["token"]

def get_user_scoped_token(user_id, m2m_token):
    """Get a token scoped to a specific user using an M2M token."""
    headers = {"Authorization": f"Bearer {m2m_token}"}
    
    response = requests.get(
        f"{BASE_URL}/user-scoped-token/{user_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    return data["token"]

def decode_token(token):
    """Decode a JWT token without verification."""
    # This is for testing purposes only - in production, always verify tokens
    return jwt.decode(token, options={"verify_signature": False})

def create_resource(token, name, description, owner_id=None):
    """Create a resource using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "description": description}
    
    url = f"{BASE_URL}/resources/"
    if owner_id:
        url += f"?owner_id={owner_id}"
    
    response = requests.post(
        url,
        json=data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"Failed to create resource: {response.text}")
        return None
    
    return response.json()

def get_resource(token, resource_id):
    """Get a resource by ID using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}",
        headers=headers
    )
    
    return response

def list_resources(token):
    """List all resources using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/resources/",
        headers=headers
    )
    
    return response

def test_user_scoped_tokens():
    """Test the user-scoped token functionality."""
    print("\n" + "=" * 80)
    print("TESTING USER-SCOPED TOKENS")
    print("=" * 80)
    
    # Get a regular M2M token
    print("\n1. Getting a regular M2M token...")
    m2m_token = get_token()
    if not m2m_token:
        print("❌ Failed to get M2M token")
        return
    
    m2m_payload = decode_token(m2m_token)
    print(f"✅ Got M2M token with subject: {m2m_payload.get('sub')}")
    
    # Define two user IDs
    user1_id = "auth0|user1"
    user2_id = "auth0|user2"
    
    # Get a token scoped to user1
    print(f"\n2. Getting a token scoped to user1 ({user1_id})...")
    user1_token = get_token(user1_id)
    if not user1_token:
        print("❌ Failed to get user1 token")
        return
    
    user1_payload = decode_token(user1_token)
    print(f"✅ Got token with scoped_user: {user1_payload.get('https://api.example.com/scoped_user')}")
    
    # Get a token scoped to user2
    print(f"\n3. Getting a token scoped to user2 ({user2_id})...")
    user2_token = get_user_scoped_token(user2_id, m2m_token)
    if not user2_token:
        print("❌ Failed to get user2 token")
        return
    
    user2_payload = decode_token(user2_token)
    print(f"✅ Got token with scoped_user: {user2_payload.get('https://api.example.com/scoped_user')}")
    
    # Create a resource owned by user1
    print("\n4. Creating a resource owned by user1...")
    resource1 = create_resource(user1_token, "User1's Resource", "This resource is owned by user1")
    if not resource1:
        print("❌ Failed to create resource for user1")
        return
    
    print(f"✅ Created resource with ID {resource1['id']} owned by {resource1['owner_id']}")
    
    # Create a resource owned by user2
    print("\n5. Creating a resource owned by user2...")
    resource2 = create_resource(user2_token, "User2's Resource", "This resource is owned by user2")
    if not resource2:
        print("❌ Failed to create resource for user2")
        return
    
    print(f"✅ Created resource with ID {resource2['id']} owned by {resource2['owner_id']}")
    
    # Create a resource for user2 using the M2M token
    print("\n6. Creating a resource for user2 using the M2M token...")
    resource3 = create_resource(m2m_token, "Resource for User2", "Created by M2M token", user2_id)
    if not resource3:
        print("❌ Failed to create resource for user2 using M2M token")
        return
    
    print(f"✅ Created resource with ID {resource3['id']} owned by {resource3['owner_id']}")
    
    # Test user1 access to their own resource
    print("\n7. Testing user1 access to their own resource...")
    response = get_resource(user1_token, resource1['id'])
    
    if response.status_code == 200:
        print("✅ User1 can access their own resource")
    else:
        print(f"❌ User1 cannot access their own resource: {response.status_code} - {response.text}")
    
    # Test user1 access to user2's resource
    print("\n8. Testing user1 access to user2's resource...")
    response = get_resource(user1_token, resource2['id'])
    
    if response.status_code == 403:
        print("✅ User1 cannot access user2's resource")
    else:
        print(f"❌ User1 can access user2's resource: {response.status_code} - {response.text}")
    
    # Test user2 access to the resource created for them by the M2M token
    print("\n9. Testing user2 access to the resource created for them by the M2M token...")
    response = get_resource(user2_token, resource3['id'])
    
    if response.status_code == 200:
        print("✅ User2 can access the resource created for them by the M2M token")
    else:
        print(f"❌ User2 cannot access the resource created for them: {response.status_code} - {response.text}")
    
    # Test M2M access to all resources
    print("\n10. Testing M2M access to all resources...")
    response = list_resources(m2m_token)
    
    if response.status_code == 200:
        resources = response.json()
        resource_ids = [r["id"] for r in resources]
        
        if resource1["id"] in resource_ids and resource2["id"] in resource_ids and resource3["id"] in resource_ids:
            print(f"✅ M2M token can access all resources (found {len(resources)} resources)")
        else:
            print("❌ M2M token cannot access all resources")
            if resource1["id"] not in resource_ids:
                print("  - Resource 1 is missing")
            if resource2["id"] not in resource_ids:
                print("  - Resource 2 is missing")
            if resource3["id"] not in resource_ids:
                print("  - Resource 3 is missing")
    else:
        print(f"❌ Failed to list resources: {response.text}")
    
    # Clean up - delete the test resources
    print("\n11. Cleaning up - deleting test resources...")
    
    # Delete resources using the M2M token (which has permission to delete any resource)
    headers = {"Authorization": f"Bearer {m2m_token}"}
    
    for resource_id in [resource1['id'], resource2['id'], resource3['id']]:
        response = requests.delete(f"{BASE_URL}/resources/{resource_id}", headers=headers)
        if response.status_code == 204:
            print(f"✅ Deleted resource {resource_id}")
        else:
            print(f"❌ Failed to delete resource {resource_id}: {response.status_code} - {response.text}")
    
    # Summary
    print("\nUser-Scoped Token Summary:")
    print("1. M2M tokens can be scoped to specific users")
    print("2. User-scoped tokens can create resources owned by the specified user")
    print("3. Users can only access resources they own")
    print("4. M2M tokens with proper permissions can access all resources")
    print("5. M2M tokens can create resources on behalf of specific users")

if __name__ == "__main__":
    test_user_scoped_tokens()
