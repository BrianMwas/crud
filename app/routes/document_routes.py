from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth.verify import verify_token
from ..controllers.document_controller import DocumentController
from ..schemas.document import DocumentCreate, DocumentResponse

# Create a router for document endpoints
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Document not found"}}
)

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: DocumentCreate, 
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Create a new document. The current user will be set as the owner."""
    return DocumentController.create_document(document, db, token_payload)

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """List all documents that the current user has access to."""
    return DocumentController.get_documents(db, token_payload)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Get a specific document by ID."""
    return DocumentController.get_document_by_id(document_id, db, token_payload)

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document: DocumentCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Update a specific document."""
    return DocumentController.update_document(document_id, document, db, token_payload)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Delete a specific document."""
    DocumentController.delete_document(document_id, db, token_payload)
    return None
