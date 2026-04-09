# Visual Studio Code (Cline)

## Purpose

Use Visual Studio Code with the Cline extension to connect to LiteLLM and the
MCP server from a local development workstation.

---

## Run Location

Local workstation.

---

## Before You Start

- [WireGuard](wireguard.md#wireguard) is connected on the local machine
- [LiteLLM](litellm.md#litellm) is running
- [MCP Server](mcp-server.md#mcp-server) is running if tool access is needed

---

## Context

Cline uses LiteLLM as an OpenAI-compatible provider and connects to the MCP
server over Streamable HTTP. The model name entered in Cline must match the
alias exposed by LiteLLM, such as `gpt-4o`.

---

## Steps

### Step 1: Install Visual Studio Code

1. Open `https://code.visualstudio.com/`.
2. Download the installer for the local operating system.
3. Install and launch Visual Studio Code.

### Step 2: Install the Cline extension

1. Open Visual Studio Code.
2. Open the **Extensions** view with `Ctrl+Shift+X`.
3. Search for **Cline**.
4. Install the extension.

### Step 3: Configure Cline to use LiteLLM

**If this is your first time installing Cline**, the setup wizard opens automatically:

1. On the "How will you use Cline?" screen, select **Bring my own API key** and click **Continue**.
2. On the "Configure your provider" screen, set:
    - **API Provider:** `OpenAI Compatible`
    - **Base URL:** `http://10.55.55.1:4000`
    - **OpenAI Compatible API Key:** `none` (a value is required — entering `none` avoids an error)
    - **Model ID:** the LiteLLM model alias, such as `gpt-4o`
3. Click **Continue**.

![Cline API](images/Cline%20API%20Config.png)

**If Cline is already installed**, open the settings directly:

1. Open the Cline panel.
2. Click the **Settings** icon in the top-right corner of the Cline panel. ![Cline settings icon](images/cline-settings.png)
3. Set the same fields: API Provider, Base URL, API Key (`none`), and Model ID.
4. Click **Done**.

### Step 4: Connect Cline to the MCP server

1. Open **MCP Servers** in the Cline panel. ![Cline MCP servers icon](images/cline-mcp.png)
2. Open **Remote Servers**.
3. Add a server with:
    - **Server Name:** any label, such as `Azure MCP`
    - **Server URL:** `http://10.55.55.1:8000/mcp`
    - **Transport Type:** `Streamable HTTP`
4. Save the server entry.

![Cline MCP Config](images/Cline%20MCP%20Config.png)

### Step 5: Confirm the connections

**Verify the model is connected:**

1. Open a new Cline chat.
2. Check the bottom bar of the Cline panel — the model name (e.g., `openai-compat:gpt-4o`) should appear there.
3. Type a short message and send it. If the model responds, LiteLLM is connected correctly.

**Verify the MCP server is connected:**

1. Open **MCP Servers** in the Cline panel. ![Cline MCP servers icon](images/cline-mcp.png)
2. Go to the **Configure** tab.
3. Find the MCP server entry (e.g., `Azure MCP`) and confirm it has a **green dot** on the right side, indicating it is connected and running.

---

## What You Just Set Up

Visual Studio Code and Cline are now connected to the private VM stack. Cline
can send model requests through LiteLLM and, when enabled, use the MCP tools
backed by Azure AI Search.
