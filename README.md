# urja-meter-api
# Urja Meter API

A read-only REST API built with **FastAPI** that provides programmatic access to meter search and distribution transformer data from the legacy Urja Meter Ops portal.

The project wraps the portal's existing HTTP endpoints and exposes a documented API with interactive Swagger documentation.

## Features

- **Meter search:** Search meters using a query and page number.
- **Transformer listing:** Retrieve distribution transformer records with pagination.
- **Portal authentication:** Sign in using credentials loaded from environment variables.
- **Session management:** Reuse an HTTP client to retain the portal's session cookies.
- **Input validation:** Validate page numbers and limit meter search query length.
- **Error handling:** Return appropriate API errors when upstream portal requests fail.
- **Interactive documentation:** Explore and test endpoints through Swagger UI.
- **OpenAPI specification:** Generate an `openapi.json` file from the FastAPI application.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| HTTPX | Asynchronous HTTP requests to the portal |
| python-dotenv | Load environment variables from `.env` |

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
├── requirements.txt
└── README.md
```

The local `.env` file and `.venv/` directory are intentionally excluded from version control.

## Prerequisites

- Python 3.11 or newer recommended
- Git
- Access to the Urja Meter Ops portal
- Valid portal credentials

The project has been developed and tested in a Python 3.14 virtual environment.

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-public-repository-url>
cd urja-meter-api
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Create a virtual environment

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

Create a local `.env` file in the project root. Use `.env.example` as a reference.

```dotenv
PORTAL_BASE_URL=https://urja-ops.flockenergy.tech
PORTAL_TIMEOUT_SECONDS=10
PORTAL_EMAIL=your_actual_email
PORTAL_PASSWORD=your_actual_password
```

Replace the credential placeholders with your authorized portal credentials.

**Security:** Never commit `.env`, credentials, session cookies, or tokens to GitHub. The repository should contain only `.env.example` with placeholder values.

### 5. Start the API server

```bash
uvicorn app.main:app --reload
```

The local API will be available at:

`http://127.0.0.1:8000`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Basic application health check |
| GET | `/api/v1/meters` | Search meter records |
| GET | `/api/v1/transformers` | Retrieve transformer records |

### 1. Health Check

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

This endpoint checks whether the API application is responding. It does not independently verify that the upstream portal is available.

### 2. Search Meters

**Request**

```http
GET /api/v1/meters?search=j100000&page=1
```

Parameters:

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

The response illustrates the observed upstream format. Actual results depend on the query and the current portal data.

### 3. List Distribution Transformers

**Request**

```http
GET /api/v1/transformers?page=1
```

Parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | Integer | `1` | Page number, starting at 1 |

The response preserves the upstream JSON structure, including `data`, `total`, `page`, and `pageSize`.

Observed transformer records contain fields such as:

- `code`
- `name`
- `feederCode`
- `capacityKva`

The first observed upstream page contained 20 records, with 40 total records reported at the time of inspection.

## Interactive API Documentation

Start the server, then visit:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI specification:** `http://127.0.0.1:8000/openapi.json`

The committed `openapi.json` file provides a portable specification of the API. Regenerate it after changing endpoints or their parameters.

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
     +---- Meter Search Endpoint
     |
     +---- Transformer Data Endpoint
```

The FastAPI layer validates incoming parameters and translates portal client errors into HTTP 502 responses. The portal client handles authentication and requests to the upstream endpoints.

## Design Decisions and Trade-offs

### 1. Read-only integration

The API exposes only read operations. It does not intentionally create, modify, or delete portal records.

### 2. Preserve the upstream response format

The API returns the portal's JSON data without introducing a new response schema. This reduces implementation complexity and preserves the fields and pagination metadata observed upstream.

**Trade-off:** Consumers remain dependent on the upstream response structure.

### 3. Environment-based configuration

The portal URL, timeout, email, and password are configured through environment variables instead of being hardcoded in source files.

**Trade-off:** The application requires valid configuration and authorized portal access to retrieve protected data.

### 4. Reusable asynchronous HTTP client

HTTPX is used to reuse the portal session and perform asynchronous requests.

**Trade-off:** Session expiration and concurrent requests require careful handling. More extensive authentication recovery tests would improve reliability.

### 5. Basic error handling

The API validates input parameters and reports upstream failures rather than exposing raw exception tracebacks to API consumers.

**Trade-off:** More detailed error classification, structured logging, and retry policies could be added in a future version.

## Protocol Documentation

`PROTOCOL.md` records the observed login flow, upstream endpoints, response fields, and known uncertainties.

It distinguishes verified observations from assumptions so future maintainers can understand how the integration was developed.

## Limitations and Future Improvements

- Add automated unit and integration tests using mocked portal responses.
- Validate upstream JSON responses using explicit schemas.
- Improve authentication recovery for expired or invalid sessions.
- Add structured logging and request correlation IDs.
- Introduce carefully bounded retries for transient upstream failures.
- Add CI checks for tests, formatting, and linting.
- Improve health checks to optionally report upstream connectivity.
- Add configuration validation and deployment instructions.
- Document and test pagination behavior across multiple pages.

These are potential improvements; they should not be considered implemented unless verified in the codebase.

## Assumptions

- The portal endpoints and response fields may change without notice.
- Page numbering starts at 1 for the exposed listing endpoints.
- Portal credentials are provided by the authorized user through environment configuration.
- Upstream response examples describe observed behavior and are not guaranteed to remain identical.
- The API is intended for read-only access.

## Disclaimer

This project was developed as an integration exercise around an existing portal. It is not an official product of Urja Meter Ops or Flock Energy. Access should be limited to authorized users, and all credentials must be handled securely.

