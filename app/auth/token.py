import http.client
import json
import base64
import httpx
from typing import Dict, Optional, Tuple
from .config import auth0_config

async def login_user(username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Login a user and get an access token from Auth0 using the Resource Owner Password flow.

    Args:
        username: User's email
        password: User's password

    Returns:
        Tuple containing:
        - Success flag (bool)
        - Token payload (Dict) if successful, None otherwise
        - Access token (str) if successful, error message otherwise
    """
    conn = httpx.AsyncClient()
    try:
        payload = {
                "client_id": auth0_config.web_client_id,
                "client_secret": auth0_config.web_client_secret,
                "username": username,
                "password": password,
                "grant_type": "password",
                "scope": "openid profile email",
                "audience": auth0_config.api_audience,
                "connection": "Username-Password-Authentication",
                "realm": "Username-Password-Authentication"
            }
            
        # Use web_client_domain as that's what you have in your config
        response = await conn.post(
            f"https://{auth0_config.web_client_domain}/oauth/token",
            json=payload
        )
        
        if response.status_code != 200:
            return False, None, f"Login failed: {response.text}"
            
        data = response.json()
        token = data.get("access_token")
        
        # Decode token to get payload (without verification)
        # Note: In production, you would verify this properly
        parts = token.split(".")
        if len(parts) != 3:
            return False, None, "Invalid token format"
            
        # Decode the payload (middle part)
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        decoded_bytes = base64.b64decode(padded)
        payload = json.loads(decoded_bytes.decode("utf-8"))
        
        return True, payload, token
        
    except Exception as e:
            return False, None, f"Login request failed: {str(e)}"
    finally:
        await conn.aclose()

async def get_m2m_token():
    """
    Get a machine-to-machine token from Auth0 using the recommended approach.

    Returns:
        str: The access token if successful

    Raises:
        Exception: If the token request fails
    """
    # Use the M2M application settings
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

        access_token = data.get("access_token")

        # Log the data (for debugging)
        print(f"Token data: {data}")
        return access_token
    except Exception as e:
        raise Exception(f"Token request failed: {str(e)}")
    finally:
        conn.close()
