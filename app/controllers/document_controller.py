from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Document
from ..auth.verify import verify_token
from ..schemas.document import DocumentCreate, DocumentResponse

class DocumentController:
    """
    Controller for handling Document CRUD operations
    """

    @staticmethod
    def create_document(
        document: DocumentCreate,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> Document:
        """
        Create a new document. The current user will be set as the owner.

        Args:
            document: The document data
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            The created document
        """
        # Get the user ID from the token
        user_id = token_payload.get("sub")

        # Create the document
        db_document = Document(
            title=document.title,
            content=document.content,
            owner_id=user_id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def get_documents(
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> List[Document]:
        """
        List all documents that the current user has access to.

        Args:
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            List of documents
        """
        # Check if this is an M2M token (client credentials flow)
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            # Check if the M2M app has the required permissions
            permissions = token_payload.get("permissions", [])
            
            if "read:documents" in permissions:
                return db.query(Document).all()
            else:
                # Return an empty list if the M2M app doesn't have the required permissions
                return []

        # Regular users can only see their own documents
        user_id = token_payload.get("sub")
        return db.query(Document).filter(Document.owner_id == user_id).all()

    @staticmethod
    def get_document_by_id(
        document_id: int,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> Document:
        """
        Get a specific document by ID.

        Args:
            document_id: The ID of the document
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            The document if the user has permission

        Raises:
            HTTPException: If the user doesn't have permission or the document doesn't exist
        """
        # Get the document instance
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check if this is an M2M token (client credentials flow)
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            # Verify if the M2M app has the required permissions
            permissions = token_payload.get("permissions", [])
            if "read:documents" in permissions:
                return document
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="M2M application doesn't have required permissions"
                )

        # Check if the user is the owner of the document
        user_id = token_payload.get("sub")
        if document.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )

        return document

    @staticmethod
    def update_document(
        document_id: int,
        document_update: DocumentCreate,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> Document:
        """
        Update a specific document.
        Only the owner can update the document, not M2M applications.

        Args:
            document_id: The ID of the document to update
            document_update: The updated document data
            db: Database session
            token_payload: The decoded JWT token payload

        Returns:
            The updated document

        Raises:
            HTTPException: If the user doesn't have permission or the document doesn't exist
        """
        # Get the document instance
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Only the owner can update the document, not M2M applications
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="M2M applications cannot update documents"
            )

        # Check if the user is the owner of the document
        user_id = token_payload.get("sub")
        if document.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this document"
            )

        # Update the document
        document.title = document_update.title
        document.content = document_update.content
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(
        document_id: int,
        db: Session = Depends(get_db),
        token_payload: dict = Depends(verify_token)
    ) -> None:
        """
        Delete a specific document.
        Only the owner can delete the document, not M2M applications.

        Args:
            document_id: The ID of the document to delete
            db: Database session
            token_payload: The decoded JWT token payload

        Raises:
            HTTPException: If the user doesn't have permission or the document doesn't exist
        """
        # Get the document instance
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Only the owner can delete the document, not M2M applications
        if "gty" in token_payload and token_payload["gty"] == "client-credentials":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="M2M applications cannot delete documents"
            )

        # Check if the user is the owner of the document
        user_id = token_payload.get("sub")
        if document.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this document"
            )

        # Delete the document
        db.delete(document)
        db.commit()
