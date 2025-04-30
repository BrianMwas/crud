from fastapi import APIRouter, Depends, HTTPException
from ..auth.token import get_m2m_token
from ..auth.verify import verify_token

# Create a router for authentication endpoints
router = APIRouter(
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.get("/token")
async def get_token():
    """Get a machine-to-machine token from Auth0."""
    try:
        token = await get_m2m_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protected", dependencies=[Depends(verify_token)])
def protected_route():
    """A protected route that requires a valid Auth0 token."""
    return {"message": "This is a protected route"}
