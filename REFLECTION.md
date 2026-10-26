# Reflection — Urja Meter API

## 1. What assumptions did you make while building this project?

I assumed that the existing Urja Meter Ops portal could be accessed through its underlying HTTP endpoints and that these endpoints would provide a more reliable way to retrieve data than parsing the visible web pages wherever structured JSON was available.

During my investigation, I observed that meter search and transformer data were available through separate JSON endpoints. I used these observed endpoints as the upstream data sources and preserved their response structure to avoid unnecessary transformations.

I also assumed that portal credentials would be supplied by an authorized user through environment variables. I kept the implementation read-only and documented uncertainties rather than assuming that unverified endpoints or fields existed.

## 2. What was the most difficult part, and how did you get unstuck?

The most difficult part was understanding the legacy portal's authentication flow and discovering how its frontend retrieved data.

Initially, it was not enough to inspect the visible pages because some data was loaded through separate HTTP endpoints. I used the browser's developer tools to inspect network requests, response formats, and login behavior. I then tested the relevant endpoints and integrated the observed meter search and transformer data endpoints into the HTTPX client.

This helped me separate the portal communication logic from the FastAPI routes and expose the data through a simpler REST API.

## 3. If you had another day, what would you improve?

I would first investigate additional portal endpoints for individual meter details, consumption history, and relationships between meters, transformers, and feeders.

I would then add automated tests using mocked HTTP responses to cover successful requests, invalid parameters, upstream failures, pagination, and expired sessions. I would also improve authentication recovery, introduce explicit response schemas, and add structured logging.

Finally, I would consider caching or a network hierarchy endpoint if further investigation confirmed that the required data was available and those features would be useful to API consumers.

## 4. What mistake did you make while solving this assignment?

One lesson I learned was that the visible web page does not necessarily reveal the most direct way to access its data. Initially, I focused on the pages themselves, but inspecting the browser's network activity helped me identify the underlying JSON endpoint for transformer data.

I also learned that authentication behavior needs to be tested in the context of the full session, including the initial login page, form submission, cookies, and redirects. Testing individual requests in isolation can produce misleading results.

In a future project, I would spend more time on protocol discovery before implementing the adapter and would record verified observations as I go.

## 5. If you were reviewing your own submission, what would you criticise?

The current implementation provides a useful starting point, but its data coverage is limited to meter search and transformer listing. It does not yet expose individual meter details, consumption history, or a network hierarchy.

The API also preserves the upstream response format rather than defining a fully independent response contract. This keeps the initial implementation simple, but changes in the legacy portal could affect API consumers.

Additional automated tests, more comprehensive authentication recovery, explicit response schemas, and clearer classification of upstream errors would improve reliability. I would also verify pagination across multiple pages and test how the service behaves when the portal is unavailable or returns unexpected responses.

Overall, I prioritised a working read-only integration and documented the main observations, decisions, and limitations. My next step would be to expand verified data coverage and strengthen the tests before treating the service as production-ready.
