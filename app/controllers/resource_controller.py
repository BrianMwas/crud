from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Resource
from ..auth.verify import verify_token, has_model_permission
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
        # Get the user ID from the token
        user_id = token_payload.get("sub")
        
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
        # Check if this is an M2M token with appropriate permissions
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            permissions = token_payload.get("permissions", [])
            if "read:resources" in permissions:
                # M2M app with proper permissions can see all resources
                return db.query(Resource).all()
        
        # Regular users can only see their own resources
        user_id = token_payload.get("sub")
        return db.query(Resource).filter(Resource.owner_id == user_id).all()
    
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
        # Get the resource and check if the user is the owner
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        
        # Only the owner can update the resource
        user_id = token_payload.get("sub")
        if db_resource.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can update this resource"
            )
        
        # Update the resource
        db_resource.name = resource_update.name
        db_resource.description = resource_update.description
        db.commit()
        db.refresh(db_resource)
        return db_resource
    
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
        # Get the resource and check if the user is the owner
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        
        # Only the owner can delete the resource
        user_id = token_payload.get("sub")
        if db_resource.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete this resource"
            )
        
        # Delete the resource
        db.delete(db_resource)
        db.commit()
