import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")

async def get_token():
    """Get a machine-to-machine token from Auth0."""
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": AUTH0_API_AUDIENCE,
        "grant_type": "client_credentials"
    }
    
    headers = {"content-type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        return data

async def test_protected_endpoint(token):
    """Test the protected endpoint with the token."""
    url = "http://localhost:8000/protected"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

async def test_token_endpoint():
    """Test the token endpoint of our API."""
    url = "http://localhost:8000/token"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Token received: {data.get('token')[:20]}...")
            return data.get('token')
        else:
            print(f"Failed to get token: {response.text}")
            return None

async def main():
    print("Testing Auth0 authentication...")
    
    # Test 1: Get token directly from Auth0
    print("\n1. Getting token directly from Auth0...")
    token_data = await get_token()
    
    if not token_data:
        print("❌ Failed to get token from Auth0. Please check your Auth0 credentials.")
    else:
        print(f"✅ Token received from Auth0: {token_data.get('access_token')[:20]}...")
        
        # Test protected endpoint with Auth0 token
        print("\n2. Testing protected endpoint with Auth0 token...")
        await test_protected_endpoint(token_data.get("access_token"))
    
    # Test 2: Get token from our API
    print("\n3. Getting token from our API...")
    api_token = await test_token_endpoint()
    
    if api_token:
        # Test protected endpoint with API token
        print("\n4. Testing protected endpoint with API token...")
        await test_protected_endpoint(api_token)

if __name__ == "__main__":
    asyncio.run(main())
