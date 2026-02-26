## LibreChat

This guide installs **LibreChat** on an Ubuntu virtual machine, wired to:

-   **LiteLLM** → `http://10.55.55.1:4000/v1`
-   **MCP Server** → `http://10.55.55.1:8000/mcp`
-   **LibreChat UI** → `http://10.55.55.1:3080`

---

### 1) Create Project Folder + Download Base Compose File

``` bash
mkdir -p ~/librechat && cd ~/librechat
curl -fsSL https://raw.githubusercontent.com/danny-avila/LibreChat/main/docker-compose.yml -o docker-compose.yml
```

---

### 2) Create `.env`

``` bash
nano .env
```

Paste and edit secrets:

``` env
HOST=0.0.0.0
PORT=3080

DOMAIN_CLIENT=http://10.55.55.1:3080
DOMAIN_SERVER=http://10.55.55.1:3080

LITELLM_KEY=sk-PASTE_YOUR_LITELLM_KEY_HERE

JWT_SECRET=REPLACE_WITH_RANDOM_STRING
JWT_REFRESH_SECRET=REPLACE_WITH_RANDOM_STRING

MEILI_MASTER_KEY=REPLACE_WITH_RANDOM_STRING

UID=1000
GID=1000

ALLOW_REGISTRATION=true
ALLOW_EMAIL_LOGIN=true
```

---

### 3) Create `docker-compose.override.yml`

``` bash
nano docker-compose.override.yml
```

Paste:

``` yaml
services:
  api:
    environment:
      - CONFIG_PATH=/app/librechat.yaml
    volumes:
      - ./librechat.yaml:/app/librechat.yaml:ro
```

---

### 4) Create `librechat.yaml`

``` bash
nano librechat.yaml
```

Paste:

``` yaml
version: 1.3.4

mcpSettings:
  allowedDomains:
    - "http://10.55.55.1:8000"

mcpServers:
  RAG_Website_MCP:
    type: http
    url: "http://10.55.55.1:8000/mcp"
    timeout: 60000

endpoints:
  custom:
    - name: "LiteLLM"
      apiKey: "${LITELLM_KEY}"
      baseURL: "http://10.55.55.1:4000/v1"
      models:
        default: ["gpt-4o"]
        fetch: true
      modelDisplayLabel: "LiteLLM"
```

---

### 8) Start LibreChat

From inside `~/librechat`:

``` bash
docker compose up -d
```

Check containers:

``` bash
docker compose ps
```

Check logs:

``` bash
docker logs -n 200 LibreChat
```

---

### 9) Access LibreChat

Open in your browser:

http://10.55.55.1:3080

If registration is enabled, create an account and log in.

---

### 10) Restart After Config Changes

``` bash
docker compose restart api
```

---

### 11) Update to Latest Version

``` bash
docker compose pull
docker compose up -d
```

---

### 12) Completely Reset (Wipe Data)

``` bash
docker compose down
rm -rf ./data-node ./meili_data_v1.35.1 ./uploads ./logs
docker compose up -d
```

---

LibreChat is now running cleanly with LiteLLM and your MCP server.
