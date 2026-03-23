# MCP Server

## Purpose

Run the MCP service that exposes Azure AI Search indexes as tools for clients
such as Cline and OpenWebUI.

## URL

- MCP endpoint: `http://10.55.55.1:8000/mcp`
- MCPO OpenAPI proxy: `http://10.55.55.1:8001`
- MCPO docs: `http://10.55.55.1:8001/docs`

## Run Location

Local machine for downloading and uploading the starter bundle, Ubuntu VM for
installation and configuration, and a browser on a WireGuard-connected client
for viewing the OpenAPI docs.

## Before You Start

- [Azure AI Search](azure-ai-search.md#azure-ai-search) is created
- The [Ubuntu VM](ubuntu-virtual-machine.md#ubuntu-virtual-machine) is ready
- [WireGuard](wireguard.md#wireguard) is working
- The [RAG Website](rag-website.md#rag-website) has created at least one index

## Context

The starter bundle expands into `~/mcp-server`. It includes the Python service,
the MCPO bridge, and the two systemd units needed to run them at boot. After
extracting it, edit `config.py`, `deploy/mcp-server.service`, and
`deploy/mcpo.service`.

## Steps

### Step 1: Download the starter bundle

Download:

- [MCP Server starter bundle](downloads/mcp-server.tar.gz)

### Step 2: Upload the bundle to the Ubuntu VM

Run this command on the local machine:

```bash
scp -i /path/to/your-key.pem ~/Downloads/mcp-server.tar.gz <VM_USER_NAME>@<VM_PUBLIC_IP>:/home/<VM_USER_NAME>/
```

### Step 3: Extract the bundle on the Ubuntu VM

```bash
tar -xzf ~/mcp-server.tar.gz -C ~/
```

### Step 4: Edit the configuration files

Edit the Python configuration:

```bash
nano ~/mcp-server/config.py
```

Replace the placeholders for:

- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_API_KEY`

Edit the service files:

```bash
nano ~/mcp-server/deploy/mcp-server.service
```

```bash
nano ~/mcp-server/deploy/mcpo.service
```

Replace the placeholder for:

- `<VM_USER_NAME>`

### Step 5: Create the Python virtual environment and install dependencies

```bash
cd ~/mcp-server
```

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### Step 6: Install the systemd units

Copy the service files into systemd:

```bash
sudo cp ~/mcp-server/deploy/mcp-server.service /etc/systemd/system/mcp-server.service
```

```bash
sudo cp ~/mcp-server/deploy/mcpo.service /etc/systemd/system/mcpo.service
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

### Step 7: Start the services and enable them at boot

```bash
sudo systemctl enable --now mcp-server
```

```bash
sudo systemctl enable --now mcpo
```

### Step 8: Validate the services

```bash
sudo systemctl status mcp-server
```

```bash
sudo systemctl status mcpo
```

```bash
curl -i http://10.55.55.1:8000/mcp
```

```bash
curl -I http://10.55.55.1:8001/openapi.json
```

Open the docs from a client connected over WireGuard:

- `http://10.55.55.1:8001/docs`

## What You Just Set Up

The MCP service now exposes Azure AI Search indexes as callable tools, and the
MCPO bridge makes those tools available through an OpenAPI endpoint for
OpenWebUI.
