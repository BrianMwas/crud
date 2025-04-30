# FastAPI Auth0 Machine-to-Machine Authentication

This project demonstrates how to implement machine-to-machine (M2M) authentication with Auth0 in a FastAPI application.

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

2. Test the Auth0 integration:
   ```
   python test_auth0.py
   ```

## API Endpoints

- `GET /`: Public endpoint
- `GET /health`: Public health check endpoint
- `GET /protected`: Protected endpoint that requires a valid Auth0 token
- `GET /token`: Endpoint to get a machine-to-machine token from Auth0

## Documentation

- FastAPI documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- FastAPI ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
