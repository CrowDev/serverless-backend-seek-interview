# Task Management API

## Project Overview

This project is a serverless Task Management API built using AWS Lambda and MongoDB. The application allows users to create, retrieve, update, and delete tasks through RESTful endpoints.

## Architecture

- **Serverless Framework**: Infrastructure as code for AWS Lambda deployment
- **AWS Lambda**: Serverless compute service running the API functions
- **API Gateway**: HTTP API endpoints for accessing the Lambda functions
- **MongoDB**: NoSQL database for storing task data
- **Docker**: Container for Lambda function deployment via AWS ECR

## API Functionality

The API provides a complete task management system with the following endpoints:

### Endpoints

| Method | Endpoint          | Purpose                 |
| ------ | ----------------- | ----------------------- |
| GET    | /                 | Fetch all tasks         |
| POST   | /create           | Create a new task       |
| PUT    | /edit/{task_id}   | Update an existing task |
| DELETE | /delete/{task_id} | Remove a task           |

### Data Model

Each task in the system contains:

- **\_id**: Unique identifier (UUID)
- **title**: Task name
- **description**: Detailed task information
- **priority**: Importance level (low, medium, high)
- **status**: Current state (todo, in-progress, in-review, done, blocked)

## Implementation Details

### Error Handling

The API implements comprehensive error handling with appropriate HTTP status codes:

- 200/201: Successful operations
- 400: Invalid requests (validation errors)
- 404: Resource not found
- 500: Server errors

### MongoDB Integration

- Connection management with error handling
- Document-based storage for task data
- CRUD operations through MongoDB driver

### Security

- Environment variable management for sensitive configuration
- Input validation to prevent injection attacks
- Proper error responses that don't leak implementation details

## Project Structure

```
.
├── Dockerfile                # Container configuration
├── functions                 # Lambda function handlers
│   ├── delete                # Delete task endpoint
│   ├── get                   # Retrieve tasks endpoint
│   ├── post                  # Create task endpoint
│   └── put                   # Update task endpoint
├── requirements.txt          # Python dependencies
└── serverless.yml            # Service configuration
```

## Technical Approach

This project follows these principles:

1. **Microservices Architecture**: Each endpoint is a separate Lambda function
2. **Infrastructure as Code**: Complete deployment defined in serverless.yml
3. **Containerization**: Lambda functions packaged as Docker containers
4. **REST API Design**: Standard HTTP methods mapped to CRUD operations
5. **NoSQL Database**: Schemaless design for flexibility and scalability
