import http.client
import json
from .config import auth0_config

async def get_m2m_token():
    """
    Get a machine-to-machine token from Auth0 using the recommended approach.
    
    Returns:
        str: The access token if successful
        
    Raises:
        Exception: If the token request fails
    """
    conn = http.client.HTTPSConnection(auth0_config.domain)
    
    payload = json.dumps({
        "client_id": auth0_config.client_id,
        "client_secret": auth0_config.client_secret,
        "audience": auth0_config.api_audience,
        "grant_type": "client_credentials"
    })
    
    headers = {
        'content-type': "application/json"
    }
    
    try:
        conn.request("POST", "/oauth/token", payload, headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        
        if response.status != 200:
            raise Exception(f"Failed to get token: {data.get('error_description', data)}")
        # Log the data
        print(f"Token data: {data}") 
        return data.get("access_token")
    except Exception as e:
        raise Exception(f"Token request failed: {str(e)}")
    finally:
        conn.close()
