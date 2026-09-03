# Emergency Intelligence - API Contract

## Overview
This document defines the REST API contract for the Emergency Intelligence backend system. The API follows REST conventions and uses JSON for data exchange.

## Base URL
```
http://127.0.0.1:8000
```

## API Endpoints

### Incidents
#### Create Incident
- **Method**: POST
- **Path**: `/incidents`
- **Purpose**: Create a new incident
- **Request JSON**:
```json
{
  "type": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "severity": "string",
  "priority": "string",
  "description": "string",
  "status": "string"
}
```
- **Response JSON**:
```json
{
  "id": "integer",
  "type": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "severity": "string",
  "priority": "string",
  "description": "string",
  "status": "string",
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 201 Created, 400 Bad Request

#### List Incidents
- **Method**: GET
- **Path**: `/incidents`
- **Purpose**: Retrieve all incidents
- **Request JSON**: None
- **Response JSON**:
```json
[
  {
    "id": "integer",
    "type": "string",
    "location": {
      "latitude": "number",
      "longitude": "number"
    },
    "severity": "string",
    "priority": "string",
    "description": "string",
    "status": "string",
    "timestamp": "string (ISO 8601)"
  }
]
```
- **HTTP Status Codes**: 200 OK

#### Get Incident
- **Method**: GET
- **Path**: `/incidents/{id}`
- **Purpose**: Retrieve a specific incident
- **Request JSON**: None
- **Response JSON**:
```json
{
  "id": "integer",
  "type": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "severity": "string",
  "priority": "string",
  "description": "string",
  "status": "string",
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 200 OK, 404 Not Found

#### Update Incident
- **Method**: PUT
- **Path**: `/incidents/{id}`
- **Purpose**: Update an existing incident
- **Request JSON**:
```json
{
  "type": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "severity": "string",
  "priority": "string",
  "description": "string",
  "status": "string"
}
```
- **Response JSON**:
```json
{
  "id": "integer",
  "type": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "severity": "string",
  "priority": "string",
  "description": "string",
  "status": "string",
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 200 OK, 404 Not Found

### Alerts
#### Create Alert
- **Method**: POST
- **Path**: `/alerts`
- **Purpose**: Create a new alert
- **Request JSON**:
```json
{
  "incident_id": "integer",
  "type": "string",
  "description": "string",
  "timestamp": "string (ISO 8601)"
}
```
- **Response JSON**:
```json
{
  "id": "integer",
  "incident_id": "integer",
  "type": "string",
  "description": "string",
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 201 Created, 400 Bad Request

#### List Alerts
- **Method**: GET
- **Path**: `/alerts`
- **Purpose**: Retrieve all alerts
- **Request JSON**: None
- **Response JSON**:
```json
[
  {
    "id": "integer",
    "incident_id": "integer",
    "type": "string",
    "description": "string",
    "timestamp": "string (ISO 8601)"
  }
]
```
- **HTTP Status Codes**: 200 OK

### Assets
#### Create Asset
- **Method**: POST
- **Path**: `/assets`
- **Purpose**: Create a new asset
- **Request JSON**:
```json
{
  "type": "string",
  "name": "string",
  "status": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  }
}
```
- **Response JSON**:
```json
{
  "id": "integer",
  "type": "string",
  "name": "string",
  "status": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 201 Created, 400 Bad Request

#### List Assets
- **Method**: GET
- **Path**: `/assets`
- **Purpose**: Retrieve all assets
- **Request JSON**: None
- **Response JSON**:
```json
[
  {
    "id": "integer",
    "type": "string",
    "name": "string",
    "status": "string",
    "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 200 OK

### Missions
#### Create Mission
- **Method**: POST
- **Path**: `/missions`
- **Purpose**: Create a new mission
- **Request JSON**:
```json
{
  "incident_id": "integer",
  "asset_id": "integer",
  "status": "string",
  "description": "string"
}
```
- **Response JSON**:
```json
{
  "id": "integer",
  "incident_id": "integer",
  "asset_id": "integer",
  "status": "string",
  "description": "string",
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 201 Created, 400 Bad Request

#### List Missions
- **Method**: GET
- **Path**: `/missions`
- **Purpose**: Retrieve all missions
- **Request JSON**: None
- **Response JSON**:
```json
[
  {
    "id": "integer",
    "incident_id": "integer",
    "asset_id": "integer",
    "status": "string",
    "description": "string",
    "timestamp": "string (ISO 8601)"
  }
]
```
- **HTTP Status Codes**: 200 OK

### Persons
#### Create Person
- **Method**: POST
- **Path**: `/persons`
- **Purpose**: Create a new person
- **Request JSON**:
```json
{
  "incident_id": "integer",
  "name": "string",
  "status": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  }
}
```
- **Response JSON**:
```json
{
  "id": "integer",
  "incident_id": "integer",
  "name": "string",
  "status": "string",
  "location": {
    "latitude": "number",
    "longitude": "number"
  },
  "timestamp": "string (ISO 8601)"
}
```
- **HTTP Status Codes**: 201 Created, 400 Bad Request

#### List Persons
- **Method**: GET
- **Path**: `/persons`
- **Purpose**: Retrieve all persons
- **Request JSON**: None
- **Response JSON**:
```json
[
  {
    "id": "integer",
    "incident_id": "integer",
    "name": "string",
    "status": "string",
    "location": {
      "latitude": "number",
      "longitude": "number"
    },
    "timestamp": "string (ISO 8601)"
  }
]
```
- **HTTP Status Codes**: 200 OK