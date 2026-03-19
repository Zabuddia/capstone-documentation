# ---------- Azure AI Search ----------
AZURE_SEARCH_ENDPOINT = "https://<search-service-name>.search.azure.us"
AZURE_SEARCH_API_VERSION = "2023-11-01"
AZURE_SEARCH_API_KEY = "<AZURE_AI_SEARCH_API_KEY>"

AZURE_SEARCH_DEFAULT_TOP_K = 5
SEARCH_TIMEOUT_SECONDS = 30

# ---------- Bindings ----------
BIND_HOST = "10.55.55.1"
MCP_PORT = 8000

ALLOWED_HOSTS = ["localhost:*", "127.0.0.1:*", f"{BIND_HOST}:*"]
ALLOWED_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*", f"http://{BIND_HOST}:*"]
