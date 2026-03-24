# OpenWebUI

## Purpose

Run the web chat interface that connects to LiteLLM and can optionally use MCP
tools during a conversation.

## URL

`http://10.55.55.1:3000`

## Run Location

Ubuntu VM for Docker commands and a browser on a WireGuard-connected client for
the web interface.

## Before You Start

- [Docker](docker.md#docker) is installed on the VM
- [LiteLLM](litellm.md#litellm) is running
- [WireGuard](wireguard.md#wireguard) is working
- [MCP Server](mcp-server.md#mcp-server) is optional but recommended if tool
  access is needed

## Context

OpenWebUI stores users, chats, and settings in a Docker volume named
`open-webui`. The first account created becomes the admin account. When the MCP
tool server is enabled for a chat, those tools become available to the model in
that conversation, but the model is not forced to use them.

## Steps

### Step 1: Start OpenWebUI in Docker

```bash
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  -p 10.55.55.1:3000:8080 \
  -e WEBUI_AUTH=True \
  -e OPENAI_API_BASE_URL="http://10.55.55.1:4000/v1" \
  -e OPENAI_API_KEY="dummy" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

### Step 2: Create the first admin account

!!! note "First account is the admin"
    The first account created on a fresh OpenWebUI instance automatically
    becomes the admin. All accounts created after that are regular users.
    Complete this step before sharing the URL with anyone else.

1. Open `http://10.55.55.1:3000` from a client connected over WireGuard.
2. Complete the first-run signup flow.
3. Use that first account as the OpenWebUI admin account.

### Step 3: Create additional user accounts

After the admin account exists, additional users can be created through the admin panel:

1. Sign in as the admin.
2. Open **Admin Panel**.
3. Go to **Users**.
4. Create additional accounts as needed.

All accounts and settings persist in the `open-webui` Docker volume, so they survive container restarts and recreations.

### Step 3a: Optional — run without accounts

If you want an open instance with no login requirement, stop and remove the current container:

```bash
docker rm -f open-webui
```

Then re-run with `WEBUI_AUTH=False`:

```bash
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  -p 10.55.55.1:3000:8080 \
  -e WEBUI_AUTH=False \
  -e OPENAI_API_BASE_URL="http://10.55.55.1:4000/v1" \
  -e OPENAI_API_KEY="dummy" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

!!! note "No-auth mode"
    In no-auth mode anyone who can reach `http://10.55.55.1:3000` over WireGuard
    can use the instance without signing in. This is only appropriate if all
    WireGuard clients are trusted.

### Step 4: Validate the container

```bash
curl -I http://10.55.55.1:3000
```

```bash
docker logs -n 200 open-webui
```

### Step 4: Connect OpenWebUI to the MCP tools

1. Sign in as an admin.
2. Open **Admin Panel**.
3. Go to **Settings** -> **Integrations** -> **Manage Tool Servers**.
4. Add a connection with:
    - Type: `OpenAPI`
    - URL: `http://10.55.55.1:8001`
    - OpenAPI spec: `openapi.json`
    - Name: `MCP Server`

### Step 5: Reset the instance later if needed

!!! note "This deletes all data"
    These commands permanently remove all chats, users, and settings stored
    in the OpenWebUI volume. This cannot be undone.

To remove the container and all persisted OpenWebUI data:

```bash
docker rm -f open-webui
```

```bash
docker volume rm open-webui
```

Run the `docker run` command again after removing the container.

## What You Just Set Up

OpenWebUI is now available on the private VM address and connected to LiteLLM.
If the MCP tool server was added, chats can also call the search tools exposed
by the MCP server.
