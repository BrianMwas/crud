import httpx
from .config import auth0_config

async def get_m2m_token():
    """
    Get a machine-to-machine token from Auth0.
    
    This function requests a token from Auth0 using client credentials flow,
    which is ideal for machine-to-machine (M2M) applications.
    
    Returns:
        str: The access token if successful
        
    Raises:
        Exception: If the token request fails
    """
    url = f"https://{auth0_config.domain}/oauth/token"
    
    payload = {
        "client_id": auth0_config.client_id,
        "client_secret": auth0_config.client_secret,
        "audience": auth0_config.api_audience,
        "grant_type": "client_credentials"
    }
    
    headers = {"content-type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get token: {response.text}")
        
        return response.json().get("access_token")
