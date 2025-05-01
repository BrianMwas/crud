from fastapi import FastAPI

from . import models, database
from .routes import base_routes, auth_routes, resource_routes, document_routes

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Auth0 M2M Demo",
    description="A demo of machine-to-machine authentication with Auth0",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Include routers
app.include_router(base_routes.router)
app.include_router(auth_routes.router)
app.include_router(resource_routes.router)
app.include_router(document_routes.router)