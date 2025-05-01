from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Resource
from ..auth.verify import verify_token, has_model_permission, check_resource_permissions
from ..schemas.resource import ResourceCreate, ResourceResponse

class ResourceController:
    """
    Controller for handling Resource CRUD operations
    """

    @staticmethod
    def create_resource(
        resource: ResourceCreate,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> Resource:
        """
        Create a new resource. The current user will be set as the owner.

        Args:
            resource: The resource data
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            The created resource
        """
        from ..auth.verify import get_effective_user_id

        # Get the user ID from the token
        user_id = get_effective_user_id(token_payload)

        # Create the resource
        db_resource = Resource(
            name=resource.name,
            description=resource.description,
            owner_id=user_id
        )
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource

    @staticmethod
    def get_resources(
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> List[Resource]:
        """
        List all resources that the current user has access to.

        Args:
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            List of resources
        """
        # Use the check_resource_permissions function to get a query that returns
        # only the resources the user has permission to access
        query = check_resource_permissions(db, token_payload)
        return query.all()

    @staticmethod
    def get_resource_by_id(
        resource_id: int,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> Resource:
        """
        Get a specific resource by ID.
        Uses the has_model_permission function to check if the user has access.

        Args:
            resource_id: The ID of the resource
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            The resource if the user has permission

        Raises:
            HTTPException: If the user doesn't have permission or the resource doesn't exist
        """
        # This will raise an appropriate HTTP exception if the user doesn't have permission
        resource = has_model_permission(resource_id, db, token_payload)
        return resource

    @staticmethod
    def update_resource(
        resource_id: int,
        resource_update: ResourceCreate,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> Resource:
        """
        Update a specific resource.
        Only the owner can update the resource, not M2M applications.

        Args:
            resource_id: The ID of the resource to update
            resource_update: The updated resource data
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            The updated resource

        Raises:
            HTTPException: If the user doesn't have permission or the resource doesn't exist
        """
        # First check if the user has permission to access this resource
        resource = has_model_permission(resource_id, db, token_payload)

        # Only the owner can update the resource, not M2M applications
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="M2M applications cannot update resources"
            )

        # Update the resource
        resource.name = resource_update.name
        resource.description = resource_update.description
        db.commit()
        db.refresh(resource)
        return resource

    @staticmethod
    def delete_resource(
        resource_id: int,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> None:
        """
        Delete a specific resource.
        Only the owner can delete the resource, not M2M applications.

        Args:
            resource_id: The ID of the resource to delete
            db: Database session
            token_payload: The decoded JWT token payload

        Raises:
            HTTPException: If the user doesn't have permission or the resource doesn't exist
        """
        # First check if the user has permission to access this resource
        resource = has_model_permission(resource_id, db, token_payload)

        # Only the owner can delete the resource, not M2M applications
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="M2M applications cannot delete resources"
            )

        # Delete the resource
        db.delete(resource)
        db.commit()
