# FastAPI Auth0 Machine-to-Machine Authentication with Resource Permissions

This project demonstrates how to implement machine-to-machine (M2M) authentication with Auth0 in a FastAPI application, along with a permission system that allows both resource owners and Auth0 M2M applications with specific permissions to access model instances.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on `.env.example` and fill in your Auth0 credentials

## Auth0 Setup

1. Create an Auth0 account if you don't have one already
2. Create a new API in Auth0:
   - Go to APIs in the Auth0 dashboard
   - Click "Create API"
   - Provide a name and identifier (this will be your API audience)
   - Select RS256 as the signing algorithm
3. Create a Machine-to-Machine application:
   - Go to Applications in the Auth0 dashboard
   - Click "Create Application"
   - Select "Machine to Machine Applications"
   - Choose the API you created in the previous step
   - Authorize the application to use the API

4. Update your `.env` file with the following values:
   - `AUTH0_DOMAIN`: Your Auth0 domain (e.g., `your-tenant.auth0.com`)
   - `AUTH0_API_AUDIENCE`: The identifier of your API
   - `AUTH0_CLIENT_ID`: The client ID of your M2M application
   - `AUTH0_CLIENT_SECRET`: The client secret of your M2M application

## Running the Application

1. Start the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

2. Test the API functionality:
   ```
   python -m tests.run_tests
   ```

   Or run individual tests:
   ```
   python -m tests.test_auth                    # Test authentication
   python -m tests.test_permissions             # Test basic permissions
   python -m tests.test_resource_controller     # Test CRUD operations
   python -m tests.test_comprehensive_permissions # Test comprehensive permission scenarios
   ```

   The comprehensive permission tests cover:
   - Successful user access of an object they own
   - Unsuccessful user access of an object they don't own
   - Successful M2M access of multiple objects of the same model class
   - Unsuccessful M2M access of objects from a different model class

## Project Structure

```
├── app/                     # Main application code
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── auth/                # Authentication related code
│   │   ├── __init__.py
│   │   ├── config.py        # Auth0 configuration
│   │   ├── token.py         # Token generation
│   │   └── verify.py        # Token verification and permissions
│   ├── controllers/         # Business logic
│   │   ├── __init__.py
│   │   └── resource_controller.py
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── auth_routes.py   # Authentication routes
│   │   ├── base_routes.py   # Basic routes
│   │   └── resource_routes.py # Resource CRUD routes
│   └── schemas/             # Pydantic models for request/response
│       ├── __init__.py
│       └── resource.py
├── tests/                   # Test files
│   ├── __init__.py
│   ├── run_tests.py         # Main test runner
│   ├── test_auth.py         # Authentication tests
│   ├── test_permissions.py  # Permission system tests
│   ├── test_resource_controller.py # Resource controller tests
│   └── test_comprehensive_permissions.py # Comprehensive permission scenarios
```

## API Endpoints

### Base Endpoints
- `GET /`: Welcome message
- `GET /health`: Health check endpoint

### Authentication Endpoints
- `GET /token`: Get a machine-to-machine token from Auth0
- `GET /protected`: Protected route that requires a valid Auth0 token

### Resource Endpoints
- `POST /resources/`: Create a new resource
- `GET /resources/`: List all resources the user has access to
- `GET /resources/{resource_id}`: Get a specific resource by ID
- `PUT /resources/{resource_id}`: Update a specific resource
- `DELETE /resources/{resource_id}`: Delete a specific resource

## Permission System

The API implements a comprehensive permission system that demonstrates machine-to-machine (M2M) authentication with Auth0:

### Resource Access Rules

1. **Resource Owners**:
   - Can create, read, update, and delete their own resources
   - Cannot access resources owned by other users

2. **M2M Applications**:
   - Can read all resources if they have the `read:resources` permission
   - Cannot update or delete any resources (even with permissions)
   - Authenticated using Auth0's client credentials flow

3. **Other Users**:
   - Cannot access resources they don't own

### Implementation Details

The permission system is implemented through two key functions:

1. **`has_model_permission`**:
   - Checks if a user has permission to access a specific resource
   - Used for single resource operations (get, update, delete)
   - Returns the resource if access is allowed, raises an HTTP exception otherwise

2. **`check_resource_permissions`**:
   - Returns a query that filters resources based on user permissions
   - Used for listing resources
   - M2M applications with proper permissions see all resources
   - Regular users only see their own resources



## Documentation

- FastAPI documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- FastAPI ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
