# Visual Studio Code (Cline)

## Purpose
Use Visual Studio Code with the Cline extension to interact with your LiteLLM server and MCP tools directly from your development environment.


## 1) Install Visual Studio Code

1. Go to: https://code.visualstudio.com
2. Download the installer for your operating system (Windows, macOS, or Linux).
3. Install and launch Visual Studio Code.


## 2) Install the Cline Extension

1. Open Visual Studio Code.
2. Click the **Extensions** icon on the left sidebar (or press `Ctrl+Shift+X`).
3. Search for **Cline**.
4. Click **Install**.


## 3) Configure Cline to Use LiteLLM

Open Cline settings and configure the following:

- **API Provider:** `OpenAI Compatible`
- **Base URL:**
  `http://10.55.55.1:4000`  
  (Replace with your LiteLLM server IP if different.)
- **OpenAI Compatible API Key:**
  Use the API key configured in your LiteLLM server.
- **Model ID:**
  Enter the model name exactly as defined in your LiteLLM configuration file.  
  (Example: `gpt-4o`, or whatever alias you configured in LiteLLM.)
Save the configuration.


## 4) Connect to the MCP Server

To allow Cline to use your MCP tools:

1. In Cline, click **MCP Servers**.
2. Go to **Remote Servers**.
3. Click **Add Server**.
4. Fill in:
   - **Server Name:** (Choose any name, e.g., `Azure MCP`)
   - **Server URL:** `http://10.55.55.1:8001/mcp`  
     (Replace with your MCP server IP if different.)
   - **Transport Type:** `Streamable HTTP`
5. Click **Add Server**.

Your MCP tools exposed by the MCP Server should now be available inside
Cline.


## Notes

- Ensure you are connected to WireGuard if accessing `10.55.55.1` over the VPN.
- Confirm LiteLLM is running on port `4000`.
- Confirm MCP Server is running on port `8000`.
