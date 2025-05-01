import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Auth0Config(BaseModel):
    """Auth0 configuration settings."""
    api_audience: str = os.getenv("AUTH0_API_AUDIENCE", "")
    
    # Machine-to-Machine application settings
    domain: str = os.getenv("AUTH0_DOMAIN", "")
    client_id: str = os.getenv("AUTH0_CLIENT_ID", "")
    client_secret: str = os.getenv("AUTH0_CLIENT_SECRET", "")
    
    # Web application settings
    web_client_id: str = os.getenv("AUTH0_WEB_CLIENT_ID", "")
    web_client_secret: str = os.getenv("AUTH0_WEB_CLIENT_SECRET", "") 
    web_client_domain: str = os.getenv("AUTH0_WEB_CLIENT_DOMAIN", "") 
    algorithms: list[str] = ["RS256"]  # Auth0 uses RS256 by default

# Create a global instance of the config
auth0_config = Auth0Config()
