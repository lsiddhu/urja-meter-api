
# Urja Meter Ops — Observed Portal Protocol

## 1. Purpose

This document records the read-only HTTP behavior observed while
integrating with the Urja Meter Ops portal.

Base URL: `https://urja-ops.flockenergy.tech`

Only behavior observed during normal portal use is documented.
Unverified endpoints and assumptions are identified explicitly.

## 2. Authentication

- The login page is available at `GET /login`.
- Login is submitted using `POST /login`.
- The observed login form uses form-encoded fields named `email`
  and `password`.
- A successful browser login redirects to `/meters` with HTTP 303.
- The API client loads `/login` before submitting credentials.
- A single reusable HTTP client is used to retain session cookies.
- Credentials are loaded from environment variables and must not be
  hardcoded or committed.

Authentication expiration and failure behavior should be verified
through additional tests.

## 3. Meter Search

### Request

- Method: `GET`
- Path: `/portal/meters/search`
- Query parameters:
  - `q`: search text
  - `page`: page number

Example:

`GET /portal/meters/search?q=j100000&page=1`

### Observed response

The endpoint returns JSON with these top-level fields:

- `data`: array of meter records
- `total`: total number of matching records
- `page`: current page
- `pageSize`: page size

Observed meter record fields:

- `meterId`
- `serialNo`
- `make`
- `phaseType`
- `installationStatus`
- `dtCode`

The observed example returned meter `J100000`, serial number
`SE33962`, make `HPL`, phase `single`, status `Decommissioned`,
and distribution transformer `DT-001`.

## 4. Distribution Transformers

### Request

- Method: `GET`
- Path: `/portal/dts`
- Query parameter:
  - `page`: page number

Example:

`GET /portal/dts?page=1`

### Observed response

The endpoint returns JSON with these top-level fields:

- `data`: array of transformer records
- `total`: total number of records
- `page`: current page
- `pageSize`: page size

Observed transformer record fields:

- `code`
- `name`
- `feederCode`
- `capacityKva`

The observed first page contained 20 records and reported a total
of 40 transformers.

## 5. Web Pages Versus Data Endpoints

- `GET /meters` serves the meter interface.
- `GET /transformers` serves the transformer interface.
- `GET /portal/meters/search` returns meter-search JSON.
- `GET /portal/dts` returns transformer-list JSON.

The HTML response for `/transformers` contained the table structure
but no transformer rows in its initial HTML. The separate
`/portal/dts` endpoint supplied the transformer data.

## 6. Error Handling and Unknowns

The API client applies a request timeout and checks HTTP status codes.
It checks the response content type before parsing JSON.

The following behaviors have not yet been comprehensively verified:

- Exact error response bodies for invalid requests
- Whether all portal endpoints use the same authentication rules
- Rate limits and pagination limits
- Session expiration timing
- Additional meter detail or transformer detail endpoints

These items should be treated as unknown rather than assumed.

## 7. Safety and Constraints

- The integration is read-only.
- No write operations are intentionally exposed by this API.
- Credentials, session cookies, and tokens must not be included in
  source control or public documentation.
- This document describes observed behavior, not a guarantee of
  permanent upstream compatibility.
