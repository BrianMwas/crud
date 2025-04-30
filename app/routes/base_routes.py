from fastapi import APIRouter

# Create a router for basic endpoints
router = APIRouter(
    tags=["base"]
)

@router.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the FastAPI Auth0 M2M Demo API"}

@router.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy"}
