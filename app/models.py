from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(String, index=True)  # Auth0 user ID (sub claim)