import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from .config import auth0_config
from ..database import get_db
from ..models import Resource

# Set up the HTTP Bearer authentication scheme
security = HTTPBearer()

# Cache for the JWKS (JSON Web Key Set)
m2m_jwks_cache = None
web_jwks_cache = None

async def get_jwks(domain: str, is_web_app: bool = False):
    """
    Get the JSON Web Key Set from Auth0.

    Args:
        domain: The Auth0 domain to get the JWKS from
        is_web_app: Whether this is for the web application (True) or M2M application (False)

    Returns:
        The JWKS as a dictionary
    """
    global m2m_jwks_cache, web_jwks_cache

    # Use the appropriate cache based on the application type
    if is_web_app:
        if web_jwks_cache is None:
            url = f"https://{domain}/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                web_jwks_cache = response.json()
        return web_jwks_cache
    else:
        if m2m_jwks_cache is None:
            url = f"https://{domain}/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                m2m_jwks_cache = response.json()
        return m2m_jwks_cache

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the JWT token from the Authorization header.
    Handles tokens from both M2M and web applications.

    Args:
        credentials: The HTTP Authorization credentials containing the token

    Returns:
        dict: The decoded token payload if valid

    Raises:
        HTTPException: If the token is invalid or expired
    """
    token = credentials.credentials

    # Try to decode the token without verification to determine which Auth0 application issued it
    try:
        # Decode the token without verification to get the issuer
        unverified_payload = pyjwt.decode(token, options={"verify_signature": False})
        unverified_header = pyjwt.get_unverified_header(token)

        # Determine which Auth0 application issued the token based on the issuer
        issuer = unverified_payload.get("iss", "")

        # Check if this is a token from the web application
        is_web_app = auth0_config.web_client_domain in issuer

        # Get the appropriate domain and JWKS
        domain = auth0_config.web_client_domain if is_web_app else auth0_config.domain
        jwks = await get_jwks(domain, is_web_app)

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

        # Verify the token with the appropriate issuer
        payload = jwt.decode(
            token,
            key=rsa_key,
            algorithms=auth0_config.algorithms,
            audience=auth0_config.api_audience,
            issuer=f"https://{domain}/"
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_effective_user_id(token_payload: dict) -> str:
    """
    Get the effective user ID from the token payload.
    Uses the subject claim (sub) from the token.

    Args:
        token_payload: The decoded JWT token payload

    Returns:
        The effective user ID (subject claim)
    """
    # Use the subject claim as the user ID
    return token_payload.get("sub")

def has_model_permission(model_id: int, db: Session = Depends(get_db), token_payload: dict = Depends(verify_token)):
    """
    Checks if the current user has permission to access a specific resource.
    Allows access if:
    1. The user is the owner of the resource
    2. The request comes from an authorized M2M application with appropriate permissions

    Args:
        model_id: The ID of the resource to check permissions for
        db: Database session
        token_payload: The decoded JWT token payload

    Returns:
        The resource instance if the user has permission

    Raises:
        HTTPException: If the user doesn't have permission or the resource doesn't exist
    """
    # Get the resource instance
    resource = db.query(Resource).filter(Resource.id == model_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Check if this is an M2M token (client credentials flow)
    if "gty" in token_payload and token_payload["gty"] == "client-credentials":
        # Verify if the M2M app has the required permissions
        permissions = token_payload.get("permissions", [])
        if "read:resources" in permissions:
            return resource
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="M2M application doesn't have required permissions"
            )

    # Check if user is the owner
    # Get the effective user ID (either the scoped user or the subject claim)
    user_id = get_effective_user_id(token_payload)
    if resource.owner_id == user_id:
        return resource

    # If neither condition is met, deny access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this resource"
    )

def check_resource_permissions(db: Session, token_payload: dict):
    """
    Checks what resources the user has permission to access.
    This function is similar to has_model_permission but returns a query instead of a resource instance.
    It's used for listing resources rather than accessing a specific resource.

    Args:
        db: Database session
        token_payload: The decoded JWT token payload

    Returns:
        A query that will return only the resources the user has permission to access
    """

    # Check if this is an M2M token (client credentials flow)
    if "gty" in token_payload and token_payload["gty"] == "client-credentials":
        # Check if the M2M app has the required permissions
        permissions = token_payload.get("permissions", [])

        if "read:resources" in permissions:
            return db.query(Resource)
        else:
            # Return an empty query if the M2M app doesn't have the required permissions
            return db.query(Resource).filter(Resource.id == -1)  # This will return no results

    # Regular users can only see their own resources
    # Get the effective user ID (either the scoped user or the subject claim)
    user_id = get_effective_user_id(token_payload)
    return db.query(Resource).filter(Resource.owner_id == user_id)
