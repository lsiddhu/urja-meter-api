
import os
import asyncio

import httpx
from dotenv import load_dotenv

load_dotenv()

PORTAL_BASE_URL = os.getenv(
    "PORTAL_BASE_URL",
    "https://urja-ops.flockenergy.tech",
).rstrip("/")

PORTAL_TIMEOUT = float(os.getenv("PORTAL_TIMEOUT_SECONDS", "10"))
PORTAL_EMAIL = os.getenv("PORTAL_EMAIL")
PORTAL_PASSWORD = os.getenv("PORTAL_PASSWORD")


class PortalError(Exception):
    """Raised when the upstream portal request fails."""


class PortalClient:
    def __init__(self):
        # Reuse one session so login cookies persist.
        self._client = httpx.AsyncClient(
            base_url=PORTAL_BASE_URL,
            timeout=PORTAL_TIMEOUT,
            follow_redirects=False,
        )
        self._login_lock = asyncio.Lock()
        self._authenticated = False

    async def login(self) -> None:
        """Log in to the portal and retain its session cookies."""
        if not PORTAL_EMAIL or not PORTAL_PASSWORD:
            raise PortalError(
                "Portal credentials are missing from environment variables."
            )

        try:
            # Load the login page first.
            page_response = await self._client.get("/login")
            page_response.raise_for_status()

            # Submit the login form using the same HTTP session.
            response = await self._client.post(
                "/login",
                data={
                    "email": PORTAL_EMAIL,
                    "password": PORTAL_PASSWORD,
                },
                headers={
                    "Origin": PORTAL_BASE_URL,
                    "Referer": f"{PORTAL_BASE_URL}/login",
                },
            )

            # The portal may redirect to /meters after login.
            if response.status_code == 303:
                location = response.headers.get("location", "")
                if location.rstrip("/").endswith("/meters"):
                    self._authenticated = True
                    return

                raise PortalError(
                    "Portal login redirected to an unexpected location."
                )

            response.raise_for_status()
            self._authenticated = True

        except httpx.HTTPStatusError as exc:
            raise PortalError(
                f"Portal login failed with HTTP "
                f"{exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise PortalError(
                f"Portal login request failed: {type(exc).__name__}"
            ) from exc

    async def search_meters(
        self,
        query: str = "",
        page: int = 1,
    ) -> dict:
        if page < 1:
            raise PortalError("Page must be 1 or greater")

        # Authenticate only when needed.
        if not self._authenticated:
            async with self._login_lock:
                if not self._authenticated:
                    await self.login()

        try:
            response = await self._client.get(
                "/portal/meters/search",
                params={"q": query, "page": page},
            )

            # If the session expired, log in again and retry once.
            if response.status_code == 401:
                async with self._login_lock:
                    self._authenticated = False
                    await self.login()

                response = await self._client.get(
                    "/portal/meters/search",
                    params={"q": query, "page": page},
                )

            response.raise_for_status()

            if "application/json" not in response.headers.get(
                "content-type", ""
            ):
                raise PortalError(
                    "Meter search returned non-JSON data."
                )

            result = response.json()

            if not isinstance(result, dict):
                raise PortalError(
                    "Unexpected meter-search response format."
                )

            return result

        except httpx.HTTPStatusError as exc:
            raise PortalError(
                f"Meter search failed with HTTP "
                f"{exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise PortalError(
                f"Meter search request failed: {type(exc).__name__}"
            ) from exc

    async def get_transformers(self, page: int = 1) -> dict:
        if page < 1:
            raise PortalError("Page must be 1 or greater")

        # Ensure we have an authenticated session.
        if not self._authenticated:
            async with self._login_lock:
                if not self._authenticated:
                    await self.login()

        try:
            response = await self._client.get(
                "/portal/dts",
                params={"page": page},
            )

            # Re-authenticate and retry once if the session expired.
            if response.status_code == 401:
                async with self._login_lock:
                    self._authenticated = False
                    await self.login()

                response = await self._client.get(
                    "/portal/dts",
                    params={"page": page},
                )

            response.raise_for_status()

            if "application/json" not in response.headers.get(
                "content-type", ""
            ):
                raise PortalError(
                    "Transformer listing returned non-JSON data."
                )

            result = response.json()

            if not isinstance(result, dict):
                raise PortalError(
                    "Unexpected transformer response format."
                )

            return result

        except httpx.HTTPStatusError as exc:
            raise PortalError(
                f"Transformer request failed with HTTP "
                f"{exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise PortalError(
                f"Transformer request failed: {type(exc).__name__}"
            ) from exc

    async def close(self) -> None:
        await self._client.aclose()


portal_client = PortalClient()


async def search_meters(query: str = "", page: int = 1) -> dict:
    return await portal_client.search_meters(query, page)
async def get_transformers(page: int = 1) -> dict:
    return await portal_client.get_transformers(page)