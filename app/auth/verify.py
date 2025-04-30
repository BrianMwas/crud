import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt
from jose.exceptions import JWTError

from .config import auth0_config

# Set up the HTTP Bearer authentication scheme
security = HTTPBearer()

# Cache for the JWKS (JSON Web Key Set)
jwks_cache = None
jwks_client = None

async def get_jwks():
    """Get the JSON Web Key Set from Auth0."""
    global jwks_cache
    
    if jwks_cache is None:
        url = f"https://{auth0_config.domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            jwks_cache = response.json()
    
    return jwks_cache

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the JWT token from the Authorization header.
    
    Args:
        credentials: The HTTP Authorization credentials containing the token
        
    Returns:
        dict: The decoded token payload if valid
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the key that matches the key ID in the token header
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=auth0_config.algorithms,
            audience=auth0_config.api_audience,
            issuer=f"https://{auth0_config.domain}/"
        )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
