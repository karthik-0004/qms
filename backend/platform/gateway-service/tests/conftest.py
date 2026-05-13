"""Gateway Service — Shared test fixtures.

The gateway is a stateless reverse-proxy; it does not ship an application database module.
Integration-style fixtures (AsyncClient + create_app) can be added here when needed.
"""

pytest_plugins = ("pytest_asyncio",)
