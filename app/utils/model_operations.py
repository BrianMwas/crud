"""
Utility functions for model operations.

This module provides functions for creating and accessing model instances
using the API endpoints.
"""

import httpx
from typing import Dict, Optional, Tuple, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"  # Change this to your actual API URL

async def create_model(token: str, model_class: str, name: str, description: str, owner_id: str = None) -> Tuple[bool, int, str]:
    """
    Create a new model instance
    
    Args:
        token: The access token
        model_class: The model class name (e.g., 'resources', 'documents')
        name: The name for the new instance
        description: The description for the new instance
        owner_id: Optional owner ID to create the resource on behalf of
        
    Returns:
        Tuple containing:
        - Success flag (bool)
        - Model ID (int) if successful, -1 otherwise
        - Message (str)
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "name": name,
            "description": description
        }
        
        url = f"{BASE_URL}/{model_class}/"
        if owner_id:
            url += f"?owner_id={owner_id}"
        
        try:
            response = await client.post(
                url,
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                return True, result.get("id", -1), "Created successfully"
            else:
                return False, -1, f"Failed to create: {response.text}"
        except Exception as e:
            return False, -1, f"Request failed: {str(e)}"

async def access_model(token: str, model_class: str, model_id: int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Attempt to access a model instance
    
    Args:
        token: The access token
        model_class: The model class name (e.g., 'resources', 'documents')
        model_id: The ID of the model to access
        
    Returns:
        Tuple containing:
        - Success flag (bool)
        - Model data (Dict) if successful, None otherwise
        - Message (str)
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = await client.get(
                f"{BASE_URL}/{model_class}/{model_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result, f"Successfully accessed {model_class}/{model_id}"
            else:
                return False, None, f"Failed to access {model_class}/{model_id}: {response.text}"
        except Exception as e:
            return False, None, f"Request failed: {str(e)}"

async def list_models(token: str, model_class: str) -> Tuple[bool, Optional[list], str]:
    """
    List all model instances the user has access to
    
    Args:
        token: The access token
        model_class: The model class name (e.g., 'resources', 'documents')
        
    Returns:
        Tuple containing:
        - Success flag (bool)
        - List of models (List) if successful, None otherwise
        - Message (str)
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = await client.get(
                f"{BASE_URL}/{model_class}/",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result, f"Successfully listed {model_class}"
            else:
                return False, None, f"Failed to list {model_class}: {response.text}"
        except Exception as e:
            return False, None, f"Request failed: {str(e)}"
