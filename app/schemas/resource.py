from pydantic import BaseModel
from typing import Optional

class ResourceBase(BaseModel):
    """Base schema for Resource"""
    name: str
    description: Optional[str] = None

class ResourceCreate(ResourceBase):
    """Schema for creating a Resource"""
    pass

class ResourceResponse(ResourceBase):
    """Schema for Resource response"""
    id: int
    owner_id: str

    class Config:
        from_attributes = True
