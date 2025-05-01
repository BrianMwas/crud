from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(String, index=True)  # Auth0 user ID (sub claim)

class Document(Base):
    """
    Document model for testing permissions on a different model class.
    This model is used to test that M2M applications cannot access objects
    of model classes they don't have permissions for.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    owner_id = Column(String, index=True)  # Auth0 user ID (sub claim)