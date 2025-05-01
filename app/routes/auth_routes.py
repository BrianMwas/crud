from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth.token import get_m2m_token, login_user
from ..auth.verify import verify_token

class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str
    password: str

# Create a router for authentication endpoints
router = APIRouter(
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post("/login")
async def login(login_request: LoginRequest):
    """
    Login a user with username and password.

    This endpoint uses the Resource Owner Password flow to authenticate a user
    and get an access token from Auth0.
    """
    success, payload, token_or_error = await login_user(
        login_request.username,
        login_request.password
    )

    if not success:
        raise HTTPException(status_code=401, detail=token_or_error)

    return {
        "token": token_or_error,
        "user_id": payload.get("sub"),
        "permissions": payload.get("permissions", [])
    }

@router.get("/token")
async def get_token():
    """
    Get a machine-to-machine token from Auth0.
    """
    try:
        token = await get_m2m_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protected", dependencies=[Depends(verify_token)])
def protected_route():
    """A protected route that requires a valid Auth0 token."""
    return {"message": "This is a protected route"}
