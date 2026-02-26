## OpenWebUI

**Purpose:**
Provide a web UI for chatting with models through your **LiteLLM** server (OpenAI-compatible API), reachable over WireGuard on the Ubuntu VM.

**URL:** `http://10.55.55.1:3000`

**LLM API:** LiteLLM at `http://10.55.55.1:4000/v1`

**Data persistence:** Stored in the Docker volume `open-webui` (users, chats, settings)

---

### 1) Run OpenWebUI in Docker

Use this command:

```bash
docker run -d \
  --name open-webui \
  --restart unless-stopped \
  -p 10.55.55.1:3000:8080 \
  -e WEBUI_AUTH=True \
  -e OPENAI_API_BASE_URL="http://10.55.55.1:4000/v1" \
  -e OPENAI_API_KEY="sk-PASTE_YOUR_LITELLM_KEY_HERE" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

**What this is doing:**

- `-p 10.55.55.1:3000:8080`
  Binds OpenWebUI to the WireGuard IP only (private access over VPN).
  
- `WEBUI_AUTH=True`
  Turns on logins / user accounts.
  
- `OPENAI_API_BASE_URL="http://10.55.55.1:4000/v1"`
  Points OpenWebUI at LiteLLM (so the model list comes from LiteLLM’s `/v1/models`).
  
- `OPENAI_API_KEY="sk-..."`
  The Bearer token OpenWebUI uses to authenticate to LiteLLM (your `LITELLM_KEY`).
  
- `-v open-webui:/app/backend/data`
  Persists users, chats, and settings across container restarts/recreates.

---

### 2) First login creates the Admin account

After it starts:

1. Open: `http://10.55.55.1:3000`
2. On a fresh install, OpenWebUI will show a first-run flow (signup / create account).
3. **The first user account created becomes the Admin** (this is how you “bootstrap” admin access).

---

### 3) Creating additional accounts

After the Admin exists:

- Log in as the Admin
- Go to the **Admin Panel** (wording varies by version)
- Find **Users**
- Create additional users

Because you are using the persistent volume (`open-webui`), all accounts and settings remain even if you restart or recreate the container.

---

### 4) No-accounts mode

If you want a totally open instance (no logins), run with:

```bash
-e WEBUI_AUTH=False
```

**Important:** only do this if the service is restricted to a trusted network (you are binding to `10.55.55.1`, which is good).

---

### 5) Verify it’s up

```bash
curl -I http://10.55.55.1:3000
```

Logs:

```bash
docker logs -n 200 open-webui
```

---

### 6) Connect OpenWebUI to MCP tools

OpenWebUI tool/MCP integration can be configured from the UI, but the standard approach is:

1. Log in as **Admin**
2. Open the **Admin Panel** → **Settings** → **External Tools**
3. Add a new tool server with:
   - **Type:** `OpenAPI`
   - **OpenAPI Spec:** `URL: openapi.json` 
   - **URL:** `http://10.55.55.1:8001`
   - **Name:** `MCP Server`(or whatever you would like)

Once added, the MCP tools should become available to enable for chats.

---

### 7) Starting fresh (wipe users/chats/settings)

To completely reset OpenWebUI (delete all accounts + chats + settings):

```bash
docker rm -f open-webui 2>/dev/null || true
docker volume rm open-webui
```

Then rerun the “Run OpenWebUI in Docker” command above.
