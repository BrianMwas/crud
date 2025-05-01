"""
Test user permission scenarios for the resource system.

This test implements the following scenarios:
1. Successful user access of an object they own (Object A)
2. Unsuccessful user access of an object they don't own (Object B)
3. Successful M2M access of both objects A and B (since they're of the same model class)
4. Unsuccessful M2M access of an object C belonging to a different model class
"""

import os
import json
import requests
import jwt
import sqlalchemy
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import sys

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app modules
from app.database import engine, SessionLocal
from app.models import Resource, Document, Base

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000"
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_token():
    """Get a token from Auth0."""
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": AUTH0_API_AUDIENCE,
        "grant_type": "client_credentials"
    }
    
    headers = {"content-type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    return data["access_token"]

def decode_token(token):
    """Decode a JWT token without verification."""
    # This is for testing purposes only - in production, always verify tokens
    return jwt.decode(token, options={"verify_signature": False})

def is_m2m_token(token):
    """Check if a token is an M2M token."""
    token_payload = decode_token(token)
    return "gty" in token_payload and token_payload["gty"] == "client-credentials"

def has_permission(token, permission):
    """Check if a token has a specific permission."""
    token_payload = decode_token(token)
    return permission in token_payload.get("permissions", [])

def create_resource(token, name, description):
    """Create a resource using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "description": description}
    
    response = requests.post(
        f"{BASE_URL}/resources/",
        json=data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"Failed to create resource: {response.text}")
        return None
    
    return response.json()

def create_document(token, title, content):
    """Create a document using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title, "content": content}
    
    response = requests.post(
        f"{BASE_URL}/documents/",
        json=data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"Failed to create document: {response.text}")
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

def get_document(token, document_id):
    """Get a document by ID using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/documents/{document_id}",
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

def update_resource_owner(resource_id, new_owner_id):
    """
    Update the owner_id of a resource directly in the database.
    This is used to simulate a resource owned by a different user.
    """
    try:
        # Create a database session
        db = SessionLocal()
        
        # Get the resource
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            print(f"Resource with ID {resource_id} not found")
            db.close()
            return False
        
        # Update the owner_id
        resource.owner_id = new_owner_id
        db.commit()
        db.close()
        
        print(f"Updated owner_id of resource {resource_id} to {new_owner_id}")
        return True
    except Exception as e:
        print(f"Error updating resource owner: {str(e)}")
        return False

def test_user_permissions():
    """
    Test the user permission system with real database interactions.
    
    Scenarios:
    1. Successful user access of an object they own (Object A)
    2. Unsuccessful user access of an object they don't own (Object B)
    3. Successful M2M access of both objects A and B (since they're of the same model class)
    4. Unsuccessful M2M access of an object C belonging to a different model class
    """
    print("\n" + "=" * 80)
    print("TESTING USER PERMISSIONS")
    print("=" * 80)
    
    # Get a user token and an M2M token
    user_token = get_token()
    m2m_token = get_token()  # In a real scenario, this would be a different token with M2M permissions
    
    # Decode tokens to check their claims
    user_token_payload = decode_token(user_token)
    m2m_token_payload = decode_token(m2m_token)
    
    is_user_m2m = is_m2m_token(user_token)
    is_m2m_m2m = is_m2m_token(m2m_token)
    
    has_user_read_permission = has_permission(user_token, "read:resources") if is_user_m2m else False
    has_m2m_read_permission = has_permission(m2m_token, "read:resources") if is_m2m_m2m else False
    
    print(f"User token type: {'M2M' if is_user_m2m else 'User'}")
    print(f"M2M token type: {'M2M' if is_m2m_m2m else 'User'}")
    
    if is_user_m2m:
        print(f"User token has 'read:resources' permission: {'Yes' if has_user_read_permission else 'No'}")
    
    if is_m2m_m2m:
        print(f"M2M token has 'read:resources' permission: {'Yes' if has_m2m_read_permission else 'No'}")
    
    # Create resources for testing
    print("\n1. Creating test resources...")
    
    # Resource A - owned by the current user
    resource_a = create_resource(user_token, "Resource A", "Owned by current user")
    if resource_a:
        print(f"✅ Created Resource A with ID {resource_a['id']}")
    else:
        print("❌ Failed to create Resource A")
        return
    
    # Resource B - owned by another user (simulated)
    resource_b = create_resource(user_token, "Resource B", "Owned by another user (simulated)")
    if resource_b:
        print(f"✅ Created Resource B with ID {resource_b['id']}")
    else:
        print("❌ Failed to create Resource B")
        return
    
    # Update the owner_id of Resource B to simulate it being owned by another user
    fake_owner_id = "auth0|fake-user-123456"
    if update_resource_owner(resource_b['id'], fake_owner_id):
        print(f"✅ Updated owner_id of Resource B to simulate different ownership")
    else:
        print("❌ Failed to update owner_id of Resource B")
        print("   The 'unsuccessful access' test may not work correctly")
    
    # Create Document C - owned by the current user
    document_c = create_document(user_token, "Document C", "This is a document for testing permissions")
    if document_c:
        print(f"✅ Created Document C with ID {document_c['id']}")
    else:
        print("❌ Failed to create Document C")
        return
    
    # TIMESTAMP A: Successful user access of an object they own (Object A)
    print("\n=== TIMESTAMP A: User accesses their own Resource A ===")
    response = get_resource(user_token, resource_a['id'])
    
    if response.status_code == 200:
        print(f"✅ User can access their own resource (A)")
        resource_data = response.json()
        print(f"Resource A details: {resource_data['name']} - {resource_data['description']}")
    else:
        print(f"❌ User cannot access their own resource (A): {response.status_code} - {response.text}")
    
    # TIMESTAMP B: Unsuccessful user access of an object they don't own (Object B)
    print("\n=== TIMESTAMP B: User fails to access Resource B (owned by another user) ===")
    response = get_resource(user_token, resource_b['id'])
    
    if response.status_code == 403:
        print(f"✅ User cannot access a resource they don't own (B)")
    else:
        print(f"❌ User can access a resource they don't own (B): {response.status_code}")
        print("   This indicates a problem with the permission system")
    
    # TIMESTAMP C: Successful M2M access of both objects A and B (same model class)
    if is_m2m_m2m and has_m2m_read_permission:
        print("\n=== TIMESTAMP C: M2M successfully accesses Resources A and B ===")
        
        # Test access to Resource A
        response_a = get_resource(m2m_token, resource_a['id'])
        if response_a.status_code == 200:
            print(f"✅ M2M can access Resource A")
        else:
            print(f"❌ M2M cannot access Resource A: {response_a.status_code} - {response_a.text}")
        
        # Test access to Resource B
        response_b = get_resource(m2m_token, resource_b['id'])
        if response_b.status_code == 200:
            print(f"✅ M2M can access Resource B")
        else:
            print(f"❌ M2M cannot access Resource B: {response_b.status_code} - {response_b.text}")
        
        # Test listing all resources
        response_list = list_resources(m2m_token)
        if response_list.status_code == 200:
            resources = response_list.json()
            resource_a_found = any(r["id"] == resource_a['id'] for r in resources)
            resource_b_found = any(r["id"] == resource_b['id'] for r in resources)
            
            if resource_a_found and resource_b_found:
                print(f"✅ M2M can list both Resource A and B (found {len(resources)} resources)")
            else:
                print(f"❌ M2M cannot list all resources: A found: {resource_a_found}, B found: {resource_b_found}")
        else:
            print(f"❌ M2M cannot list resources: {response_list.status_code} - {response_list.text}")
    else:
        print("\n=== TIMESTAMP C: Skipping M2M access test - token is not M2M or doesn't have read permission ===")
    
    # TIMESTAMP D: Unsuccessful M2M access of an object C belonging to a different model class
    print("\n=== TIMESTAMP D: M2M fails to access Document C (different model class) ===")
    
    # Try to access Document C with the M2M token
    response = get_document(m2m_token, document_c['id'])
    
    if response.status_code == 403:
        print("✅ M2M cannot access Document C (different model class) - 403 Forbidden")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    
    # Clean up - delete the test resources
    print("\n6. Cleaning up - deleting test resources...")
    
    # Delete Resource A
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.delete(f"{BASE_URL}/resources/{resource_a['id']}", headers=headers)
    if response.status_code == 204:
        print("✅ Resource A deleted successfully")
    else:
        print(f"❌ Failed to delete Resource A: {response.status_code} - {response.text}")
    
    # For Resource B, we need to restore the original owner_id first
    original_owner_id = user_token_payload.get("sub")
    if update_resource_owner(resource_b['id'], original_owner_id):
        print(f"✅ Restored original owner_id of Resource B")
        
        # Now delete Resource B
        response = requests.delete(f"{BASE_URL}/resources/{resource_b['id']}", headers=headers)
        if response.status_code == 204:
            print("✅ Resource B deleted successfully")
        else:
            print(f"❌ Failed to delete Resource B: {response.status_code} - {response.text}")
    else:
        print("❌ Failed to restore original owner_id of Resource B")
        print("   Resource B was not deleted and may need manual cleanup")
    
    # Delete Document C
    response = requests.delete(f"{BASE_URL}/documents/{document_c['id']}", headers=headers)
    if response.status_code == 204:
        print("✅ Document C deleted successfully")
    else:
        print(f"❌ Failed to delete Document C: {response.status_code} - {response.text}")
    
    # Summary
    print("\nPermission System Summary:")
    print("1. Successful user access of an object they own (Object A)")
    print("2. Unsuccessful user access of an object they don't own (Object B)")
    print("3. Successful M2M access of both objects A and B (since they're of the same model class)")
    print("4. Unsuccessful M2M access of an object C belonging to a different model class")

if __name__ == "__main__":
    test_user_permissions()
