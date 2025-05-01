# Auth0 Permission Tests Postman Collection

This Postman collection is designed to test the following permission scenarios:

1. **Scenario A**: Successful user access of an object they own (Object A)
2. **Scenario B**: Unsuccessful user access of an object they don't own (Object B)
3. **Scenario C**: Successful M2M access of both objects A and B (since they're of the same model class)
4. **Scenario D**: Unsuccessful M2M access of an object C belonging to a different model class

The collection uses two separate Auth0 applications:
- A web application for user authentication
- A machine-to-machine (M2M) application for API access

## Setup Instructions

1. Import the `Auth0_Permission_Tests.postman_collection.json` file into Postman
2. Import the `Auth0_API_Testing.postman_environment.json` environment file into Postman
3. Select the "Auth0 API Testing" environment in Postman
4. Update the `base_url` variable if your API is not running on `http://localhost:8000`

## Running the Tests

The collection is organized into four folders:

1. **Authentication**: Get tokens for User 1, User 2, and M2M
2. **Resource Creation**: Create test resources (Resource A, Resource B, Document C)
3. **Permission Tests**: Test the four permission scenarios
4. **Cleanup**: Delete the test resources

You can run the entire collection in sequence to test all scenarios, or run individual requests as needed.

### Test Flow

1. First, run the requests in the "Authentication" folder to get tokens
2. Then, run the requests in the "Resource Creation" folder to create test resources
3. Next, run the requests in the "Permission Tests" folder to test the permission scenarios
4. Finally, run the requests in the "Cleanup" folder to delete the test resources

## Expected Results

- **Scenario A**: User 1 can access Resource A (200 OK)
- **Scenario B**: User 1 cannot access Resource B (403 Forbidden)
- **Scenario C**: M2M can access both Resource A and Resource B (200 OK)
- **Scenario D**: M2M cannot access Document C (403 Forbidden)

## Troubleshooting

If you encounter issues:

1. Check that your API is running and accessible
2. Verify that your Auth0 configuration is correct
3. Make sure you have the correct permissions set up in Auth0
4. Check the API logs for any errors

## Notes

- The tests use environment variables to store tokens and resource IDs
- Each request includes test scripts to verify the expected response
- The collection is designed to be run in sequence, with each request depending on previous requests
