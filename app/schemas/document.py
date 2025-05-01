from pydantic import BaseModel
from typing import Optional

class DocumentBase(BaseModel):
    """Base schema for Document"""
    title: str
    content: Optional[str] = None

class DocumentCreate(DocumentBase):
    """Schema for creating a Document"""
    pass

class DocumentResponse(DocumentBase):
    """Schema for Document response"""
    id: int
    owner_id: str

    class Config:
        from_attributes = True
