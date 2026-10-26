
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app.client import PortalError, portal_client
from app.client import PortalError, portal_client, get_transformers

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await portal_client.close()


app = FastAPI(
    title="Urja Meter API",
    description=(
        "A REST API that provides read-only access to meter data "
        "from the Urja Meter Ops portal."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "Urja Meter API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/meters")
async def get_meters(
    search: str = Query(
        default="",
        max_length=100,
        description="Optional meter ID or search text",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number, starting at 1",
    ),
):
    try:
        result = await portal_client.search_meters(
            query=search.strip(),
            page=page,
        )
        return result

    except PortalError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

@app.get("/api/v1/transformers")
async def list_transformers(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number, starting at 1",
    ),
):
    try:
        return await get_transformers(page=page)
    except PortalError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
