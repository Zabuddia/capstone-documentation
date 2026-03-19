import asyncio
import logging
import os
import re
from typing import Dict, List, Optional, Set

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

import config

logger = logging.getLogger("azure-search-mcp")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def _as_list(v) -> List[str]:
    if isinstance(v, list):
        items = v
    else:
        items = str(v).split(",")
    return [x.strip() for x in items if x and str(x).strip()]


mcp = FastMCP(
    name="azure-search-mcp",
    json_response=False,
    stateless_http=False,
    transport_security=TransportSecuritySettings(
        allowed_hosts=_as_list(config.ALLOWED_HOSTS),
        allowed_origins=_as_list(config.ALLOWED_ORIGINS),
    ),
)


class AzureSearchClient:
    def _endpoint(self) -> str:
        return str(config.AZURE_SEARCH_ENDPOINT).rstrip("/")

    def _headers(self) -> Dict[str, str]:
        return {"api-key": config.AZURE_SEARCH_API_KEY}

    async def fetch_indexes(self) -> List[str]:
        url = f"{self._endpoint()}/indexes?api-version={config.AZURE_SEARCH_API_VERSION}"
        async with httpx.AsyncClient(timeout=config.SEARCH_TIMEOUT_SECONDS) as client:
            r = await client.get(url, headers=self._headers())
            r.raise_for_status()
            data = r.json()
            return [
                x["name"]
                for x in data.get("value", [])
                if isinstance(x, dict) and "name" in x
            ]

    async def search(self, index_name: str, query: str, top_k: int) -> Dict:
        url = (
            f"{self._endpoint()}/indexes/{index_name}/docs/search"
            f"?api-version={config.AZURE_SEARCH_API_VERSION}"
        )
        headers = {**self._headers(), "Content-Type": "application/json"}
        payload = {"search": query, "top": max(1, min(int(top_k), 50))}
        async with httpx.AsyncClient(timeout=config.SEARCH_TIMEOUT_SECONDS) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()


azure = AzureSearchClient()


def format_results(data: Dict, top_k: int) -> str:
    hits = data.get("value", [])
    if not hits:
        return "No results found."

    out: List[str] = []
    for i, doc in enumerate(hits[:top_k], start=1):
        score = doc.get("@search.score")
        text = doc.get("content") or doc.get("chunk") or doc.get("text") or ""
        snippet = text[:800] + ("…" if len(text) > 800 else "")
        out.append(f"Result {i} (score={score}):\n{snippet}")

    return "\n\n---\n\n".join(out)


_registered: set[str] = set()


def _tool_name_for_index(index_name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", index_name).strip("_").lower()
    return f"search_{base or 'index'}"


def _register_index_tool(index_name: str) -> None:
    tool_name = _tool_name_for_index(index_name)
    if tool_name in _registered:
        return

    async def _search_tool(query: str, top_k: Optional[int] = None) -> str:
        k = int(top_k) if top_k is not None else int(config.AZURE_SEARCH_DEFAULT_TOP_K)
        try:
            data = await azure.search(index_name=index_name, query=query, top_k=k)
            return format_results(data, k)
        except Exception as e:
            return f"Azure Search error (index={index_name}): {e}"

    _search_tool.__name__ = tool_name
    _search_tool.__doc__ = f"Search Azure AI Search index '{index_name}'."

    mcp.tool()(_search_tool)
    _registered.add(tool_name)
    logger.info("Registered MCP tool %s for index %s", tool_name, index_name)


async def _startup_register_tools() -> Set[str]:
    names = await azure.fetch_indexes()
    for idx in names:
        _register_index_tool(idx)
    return set(names)


async def main() -> None:
    try:
        await _startup_register_tools()
    except Exception as e:
        logger.warning("Startup index fetch failed: %s", e)

    app = mcp.streamable_http_app()

    cfg = uvicorn.Config(
        app,
        host=str(config.BIND_HOST),
        port=int(config.MCP_PORT),
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )
    server = uvicorn.Server(cfg)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
