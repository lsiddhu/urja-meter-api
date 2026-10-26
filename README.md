# Urja Meter API

A read-only REST API built with **FastAPI** that provides programmatic access to meter search and distribution transformer data from the legacy Urja Meter Ops portal.

The service wraps observed portal HTTP endpoints behind a documented API, allowing other applications to retrieve data without interacting directly with the portal's web interface.

**Repository:** https://github.com/lsiddhu/urja-meter-api

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [API Endpoints](#api-endpoints)
- [Interactive Documentation](#interactive-documentation)
- [Architecture](#architecture)
- [Portal Protocol](#portal-protocol)
- [Assumptions](#assumptions)
- [Design Decisions and Trade-offs](#design-decisions-and-trade-offs)
- [Intentionally Skipped](#intentionally-skipped)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Reflection](#reflection)

## Features

- **Meter search:** Search for meters using query text and pagination.
- **Transformer listing:** Retrieve distribution transformer records with pagination.
- **Portal authentication:** Load login credentials from environment variables.
- **Session management:** Reuse an asynchronous HTTP client to retain portal session cookies.
- **Input validation:** Validate page numbers and limit meter search query length.
- **Error handling:** Translate portal client errors into HTTP 502 responses.
- **Interactive documentation:** Explore API endpoints using Swagger UI and ReDoc.
- **OpenAPI specification:** Provide a generated `openapi.json` document.
- **Protocol notes:** Document observed portal behavior, endpoints, and uncertainties.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application language |
| FastAPI | REST API framework and request validation |
| Uvicorn | ASGI application server |
| HTTPX | Asynchronous HTTP communication with the portal |
| python-dotenv | Load local environment configuration |

## Project Structure

```text
urja-meter-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── client.py
├── .env.example
├── .gitignore
├── openapi.json
├── PROTOCOL.md
├── README.md
└── requirements.txt
```

- `app/main.py` defines the public API routes and application configuration.
- `app/client.py` handles portal authentication and upstream HTTP requests.
- `app/__init__.py` marks `app` as a Python package.
- `.env.example` documents the required configuration variables using placeholders.
- `.gitignore` excludes local configuration, virtual environments, and generated development files.
- `requirements.txt` lists the Python dependencies.
- `PROTOCOL.md` documents the observed legacy portal behavior.
- `openapi.json` describes the API exposed by this project.

The local `.env` file and `.venv/` directory are intentionally excluded from version control.

## Installation and Setup

### Prerequisites

- Python 3.11 or newer recommended
- Git
- Authorized access to the Urja Meter Ops portal
- Valid portal credentials

The project has been developed and tested in a Python 3.14 virtual environment.

### 1. Clone the repository

```bash
git clone https://github.com/lsiddhu/urja-meter-api.git
cd urja-meter-api
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root using `.env.example` as a reference.

```dotenv
PORTAL_BASE_URL=https://urja-ops.flockenergy.tech
PORTAL_TIMEOUT_SECONDS=10
PORTAL_EMAIL=your_authorized_email
PORTAL_PASSWORD=your_authorized_password
```

Replace the placeholders with your authorized portal credentials.

**Security:** Never commit `.env`, passwords, session cookies, or tokens. Only placeholder values should appear in `.env.example`.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

The server must be running for the local API endpoints and interactive documentation to work.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Basic application health check |
| GET | `/api/v1/meters` | Search meter records |
| GET | `/api/v1/transformers` | Retrieve transformer records |

All implemented data endpoints are read-only.

### 1. Root endpoint

**Request**

```http
GET /
```

Returns a welcome message and links to the documentation and health endpoint.

### 2. Health check

**Request**

```http
GET /health
```

**Example response**

```json
{
  "status": "ok"
}
```

This endpoint confirms that the API application is responding. It does not independently verify upstream portal availability or authentication.

### 3. Search meters

**Request**

```http
GET /api/v1/meters?search=j100000&page=1
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `search` | String | Empty | Optional meter search text |
| `page` | Integer | `1` | Page number, starting at 1 |

**Example response**

```json
{
  "data": [
    {
      "meterId": "J100000",
      "serialNo": "SE33962",
      "make": "HPL",
      "phaseType": "single",
      "installationStatus": "Decommissioned",
      "dtCode": "DT-001"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20
}
```

This example reflects an observed portal response. Actual records and totals may differ as the upstream data changes.

### 4. List distribution transformers

**Request**

```http
GET /api/v1/transformers?page=1
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | Integer | `1` | Page number, starting at 1 |

The endpoint returns the upstream JSON response, including the `data`, `total`, `page`, and `pageSize` fields.

Observed transformer records contain fields such as:

- `code`
- `name`
- `feederCode`
- `capacityKva`

The first observed upstream page contained 20 records, with 40 total records reported at the time of inspection.

### Input validation and errors

The API validates incoming query parameters. For example, a page number less than 1 should produce an HTTP 422 validation response.

Portal client failures are translated into HTTP 502 responses by the API layer. Exact upstream error handling may depend on the failure type and should be tested further.

## Interactive Documentation

With the application running, visit:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Served OpenAPI specification:** http://127.0.0.1:8000/openapi.json

The repository also contains [`openapi.json`](./openapi.json), the generated specification for this API.

Regenerate the file after modifying API routes or their parameters:

```bash
python -c "import json; from app.main import app; open('openapi.json','w',encoding='utf-8').write(json.dumps(app.openapi(), indent=2))"
```

## Architecture

```text
API Consumer
     |
     v
FastAPI Application
     |
     +---- GET /api/v1/meters
     |
     +---- GET /api/v1/transformers
     |
     v
Portal Client (HTTPX)
     |
     +---- Authenticate using environment configuration
     |
     +---- Retain session cookies
     |
     v
Legacy Urja Meter Ops Portal
     |
     +---- Meter search endpoint
     |
     +---- Transformer data endpoint
```

The FastAPI layer validates public request parameters and converts portal client errors into API responses. The portal client manages the upstream session and performs HTTP requests to the observed data endpoints.

## Portal Protocol

The portal investigation and observed behavior are documented in [`PROTOCOL.md`](./PROTOCOL.md).

The documented observations include:

- The login flow using `GET /login` followed by a form-encoded `POST /login`.
- Meter search through `GET /portal/meters/search`.
- Transformer data retrieval through `GET /portal/dts`.
- The JSON fields and pagination metadata returned by the observed endpoints.
- The difference between the transformer HTML page and its separate data endpoint.

These notes describe observed behavior rather than a guarantee that the upstream implementation will remain unchanged.

## Assumptions

1. The portal's existing HTTP endpoints can be used as the upstream data source for the API.
2. The implemented listing endpoints use page numbers starting at 1.
3. Portal credentials are supplied through environment variables rather than hardcoded in source files.
4. Upstream response structures may change and are not guaranteed to remain stable.
5. The initial service focuses on read-only meter search and transformer listing.
6. The service is intended for authorized access and does not attempt to bypass the portal's authentication.

## Design Decisions and Trade-offs

### 1. FastAPI for the public API

FastAPI provides request validation, asynchronous route support, and automatic OpenAPI documentation with relatively little boilerplate.

**Trade-off:** The framework does not remove the need to handle upstream authentication, errors, or response changes.

### 2. Preserve the upstream response structure

The service returns the observed portal JSON structure rather than introducing a completely new response schema.

**Reason:** This keeps the initial implementation small and reduces unnecessary transformations.

**Trade-off:** Consumers remain coupled to upstream field names and pagination conventions. A future version could introduce stable response models.

### 3. Environment-based configuration

The portal URL, timeout, email, and password are supplied through environment variables.

**Reason:** This separates configuration from source code and avoids committing secrets.

**Trade-off:** The service needs valid local configuration and authorized portal access to retrieve protected data.

### 4. Reusable asynchronous HTTP client

HTTPX is used to retain session cookies and make asynchronous requests.

**Reason:** Reusing a client avoids creating a new session for every request.

**Trade-off:** Session expiration, concurrent requests, and upstream authentication changes need additional testing.

### 5. Basic upstream error handling

The client checks HTTP status codes and response content types before parsing JSON, and the API layer reports client failures as HTTP 502 responses.

**Reason:** This avoids returning unhandled upstream exceptions directly to consumers.

**Trade-off:** More precise error classification, structured logging, and carefully bounded retries would improve diagnostics and reliability.

## Intentionally Skipped

The initial implementation deliberately focuses on two verified data operations: meter search and transformer listing.

The following capabilities are not exposed by the current API:

- Meter detail endpoints beyond the observed search results.
- Recent consumption history or consumption analytics.
- A reconstructed network hierarchy connecting meters, transformers, feeders, and other network entities.
- A local indexing or cross-attribute query engine.
- Persistent caching or background synchronization.
- A separate frontend or dashboard.

These were left outside the initial scope to prioritize understanding the existing portal, implementing a small read-only integration, and documenting its behavior. Their availability and usefulness should be investigated before deciding how to implement them.

## Limitations and Future Improvements

With additional time, I would prioritize:

1. **Broader portal investigation:** Identify and verify additional meter detail, consumption, and network relationship endpoints.
2. **Automated tests:** Add unit tests with mocked HTTP responses and integration tests for pagination, authentication, and error handling.
3. **Response validation:** Define explicit schemas for meter and transformer responses.
4. **Authentication recovery:** Test expired sessions and improve recovery for redirects or authentication failures.
5. **Observability:** Add structured logging and request correlation identifiers without logging secrets.
6. **Robustness:** Add carefully bounded retries for appropriate transient upstream failures.
7. **Health checks:** Optionally distinguish application health from upstream portal availability.
8. **Data freshness:** Evaluate whether caching is useful and define a clear freshness policy before introducing it.
9. **CI and code quality:** Add automated tests, linting, and formatting checks.
10. **Useful extensions:** If the portal exposes the required data, consider a network hierarchy explorer or a consumption-focused interface.

These are proposed improvements, not features claimed to be implemented.

## Reflection

### What assumptions did you make?

I assumed that the portal's existing HTTP endpoints could provide the upstream data needed for a read-only API. I preserved the observed response structure to keep the initial implementation simple and documented uncertain behavior rather than treating it as guaranteed.

### Which part was the most difficult, and how did you get unstuck?

Understanding how the legacy portal authenticated requests and exposed its data was the most challenging part. I inspected browser network requests and response formats, then tested the relevant endpoints before integrating them into the API.

### If you had another day, what would you improve?

I would investigate additional meter detail, consumption, and network relationship endpoints, add automated tests, and improve session-expiration handling and upstream error reporting.

### What mistake did you make while solving this?

One challenge was initially treating the visible web page as the main source of data. Inspecting the underlying HTTP requests helped me identify the separate endpoint that returned transformer data. I would verify the data flow earlier in a similar investigation.

### If you were reviewing your own submission, what would you criticise?

The current API covers a limited set of read-only operations and largely preserves the upstream response format. Broader data coverage, explicit response schemas, automated tests, and more comprehensive authentication recovery would make it more robust and useful.

## Disclaimer

This project was developed as an engineering take-home exercise around an existing portal. It is not an official product of Urja Meter Ops or Flock Energy. Access should be limited to authorized users, and all credentials must be handled securely.
