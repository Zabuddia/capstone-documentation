# MCP Server

## Purpose

Expose Azure AI Search as **MCP tools** so clients like **Cline**,
**OpenWebUI**, or other agents can query your Azure Search indexes
through a consistent tool interface.

This server exposes:

- **Native MCP Streamable HTTP (FastMCP):** `http://10.55.55.1:8000/mcp`
- **MCPO OpenAPI Proxy (for Open WebUI):** `http://10.55.55.1:8001`
- **MCPO Docs:** `http://10.55.55.1:8001/docs`

The MCP server remains clean and minimal. MCPO runs as a separate
service that bridges MCP → OpenAPI.


## Network / URLs

- **Bind IP (WireGuard):** `10.55.55.1`
- **MCP (Streamable HTTP):** `http://10.55.55.1:8000/mcp`
- **MCPO (OpenAPI Proxy):** `http://10.55.55.1:8001`
- **MCPO Docs:** `http://10.55.55.1:8001/docs`


## What tools it exposes

At startup, the MCP server calls Azure AI Search:

    GET /indexes

For each index found, it dynamically registers a tool:

    search_<index_name_sanitized>(query: str, top_k: int=...) -> str

Each tool:

- Searches its corresponding Azure AI Search index.
- Returns formatted text results.
- Defaults to `AZURE_SEARCH_DEFAULT_TOP_K` results.


## Files

### `requirements.txt`

```txt
fastmcp
httpx
uvicorn
mcpo
```

### `config.py`

```py
# ---------- Azure AI Search ----------
AZURE_SEARCH_ENDPOINT = "https://chris-rag-testing.search.azure.us"
AZURE_SEARCH_API_VERSION = "2023-11-01"
AZURE_SEARCH_API_KEY = "PASTE_YOUR_AZURE_SEARCH_API_KEY_HERE"

AZURE_SEARCH_DEFAULT_TOP_K = 5
SEARCH_TIMEOUT_SECONDS = 30

# ---------- Bindings ----------
BIND_HOST = "10.55.55.1"
MCP_PORT = 8000

ALLOWED_HOSTS = ["localhost:*", "127.0.0.1:*", f"{BIND_HOST}:*"]
ALLOWED_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*", f"http://{BIND_HOST}:*"]
```

### `server.py`

```py
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
```

## systemd Units

### MCP Service

`/etc/systemd/system/mcp-server.service`

```ini
[Unit]
Description=azure-search-mcp
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=byu_azure
WorkingDirectory=/home/byu_azure/mcp-server
ExecStart=/home/byu_azure/mcp-server/.venv/bin/python /home/byu_azure/mcp-server/server.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
```

### MCPO Service

`/etc/systemd/system/mcpo.service`

```ini
[Unit]
Description=mcpo (MCP-to-OpenAPI proxy)
Wants=network-online.target mcp-server.service
After=network-online.target mcp-server.service

[Service]
Type=simple
User=byu_azure
WorkingDirectory=/home/byu_azure/mcp-server

# Wait until MCP server is reachable (kills the startup race)
ExecStartPre=/usr/bin/bash -lc 'for i in {1..60}; do code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 1 http://10.55.55.1:8000/mcp || true)"; if [[ "$code" == "200" || "$code" == "202" || "$code" == "406" ]]; then exit 0; fi; sleep 1; done; echo "MCP not reachable (last HTTP $code)"; exit 1'

ExecStart=/home/byu_azure/mcp-server/.venv/bin/mcpo \
  --host 10.55.55.1 \
  --port 8001 \
  --server-type "streamable-http" \
  -- http://10.55.55.1:8000/mcp

Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

## Step-by-step: install & run on Ubuntu VM

### 1) Create project folder

```bash
mkdir -p ~/mcp-server
cd ~/mcp-server
```
Put the `config.py` and `server.py` in this folder.

### 2) Install OS packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 3) Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Production run (systemd)

```bash
sudo nano /etc/systemd/system/mcp-server.service
# Paste mcp-server.service

sudo nano /etc/systemd/system/mcpo.service
# Paste mcpo.service

sudo systemctl daemon-reload
sudo systemctl enable --now mcp-server
sudo systemctl enable --now mcpo
```
