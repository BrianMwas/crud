import jwt
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
jwks_cache = None

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
    # The user ID is usually stored in the 'sub' claim
    user_id = token_payload.get("sub")
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
    user_id = token_payload.get("sub")
    return db.query(Resource).filter(Resource.owner_id == user_id)
