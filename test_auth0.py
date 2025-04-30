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

async def main():
    print("Testing Auth0 machine-to-machine authentication...")
    
    # Get token
    print("\nGetting token from Auth0...")
    token_data = await get_token()
    
    if not token_data:
        print("Failed to get token. Please check your Auth0 credentials.")
        return
    
    print(f"Token received: {token_data.get('access_token')[:20]}...")
    
    # Test protected endpoint
    print("\nTesting protected endpoint...")
    await test_protected_endpoint(token_data.get("access_token"))

if __name__ == "__main__":
    asyncio.run(main())
