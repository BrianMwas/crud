from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth.verify import verify_token
from ..controllers.resource_controller import ResourceController
from ..schemas.resource import ResourceCreate, ResourceResponse

# Create a router for resource endpoints
router = APIRouter(
    prefix="/resources",
    tags=["resources"],
    responses={404: {"description": "Resource not found"}}
)

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """
    Create a new resource. The current user will be set as the owner.
    """
    return ResourceController.create_resource(resource, db, token_payload)

@router.get("/", response_model=List[ResourceResponse])
def list_resources(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """List all resources that the current user has access to."""
    return ResourceController.get_resources(db, token_payload)

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """
    Get a specific resource by ID.
    Uses the has_model_permission function to check if the user has access.
    """
    return ResourceController.get_resource_by_id(resource_id, db, token_payload)

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_update: ResourceCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """
    Update a specific resource.
    Only the owner can update the resource, not M2M applications.
    """
    return ResourceController.update_resource(resource_id, resource_update, db, token_payload)

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """
    Delete a specific resource.
    Only the owner can delete the resource, not M2M applications.
    """
    ResourceController.delete_resource(resource_id, db, token_payload)
    return None
