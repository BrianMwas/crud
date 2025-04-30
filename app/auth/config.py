import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Auth0Config(BaseModel):
    """Auth0 configuration settings."""
    domain: str = os.getenv("AUTH0_DOMAIN", "")
    api_audience: str = os.getenv("AUTH0_API_AUDIENCE", "")
    client_id: str = os.getenv("AUTH0_CLIENT_ID", "")
    client_secret: str = os.getenv("AUTH0_CLIENT_SECRET", "")
    algorithms: list[str] = ["RS256"]  # Auth0 uses RS256 by default

# Create a global instance of the config
auth0_config = Auth0Config()
