# Azure API

## Purpose
It’s the set of HTTPS web endpoints your app stack calls inside **Microsoft Azure Government** to use cloud services like **Azure AI Search** (querying indexes) and **Azure AI Foundry / Azure OpenAI** (sending prompts to a deployed model like GPT-4o). These calls are made over the internet using standard REST APIs, authenticated with an API key or Azure identity, and return JSON responses your services (LiteLLM, MCP Server, RAG Website, OpenWebUI) use to produce answers.
