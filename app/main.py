from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from . import models, database
from .auth.verify import verify_token
from .auth.token import get_m2m_token

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="FastAPI Auth0 M2M Demo",
    description="A demo of machine-to-machine authentication with Auth0",
    version="0.1.0"
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/protected", dependencies=[Depends(verify_token)])
def protected_route():
    """A protected route that requires a valid Auth0 token."""
    return {"message": "This is a protected route"}

@app.get("/token")
async def get_token():
    """Get a machine-to-machine token from Auth0."""
    try:
        token = await get_m2m_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))