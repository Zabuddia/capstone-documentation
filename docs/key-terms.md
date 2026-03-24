# Key Terms

A reference glossary for technical terms and acronyms used throughout this documentation.

---

## Core AI Concepts

### AI (Artificial Intelligence)
The simulation of human intelligence by computer systems. In this documentation, AI refers specifically to large language models capable of understanding and generating text.

### LLM (Large Language Model)
A type of AI model trained on large amounts of text data that can understand and generate human language. Examples include GPT-4o. LLMs power the chat and reasoning capabilities in this stack.

### RAG (Retrieval-Augmented Generation)
A technique that enhances an LLM's responses by first retrieving relevant documents from a knowledge base and providing them as context. Instead of relying solely on the model's training data, RAG allows the model to answer questions using your own documents.

### MCP (Model Context Protocol)
An open protocol that standardizes how AI models connect to external tools and data sources. MCP servers expose capabilities (like web search or file access) that an AI model can call during a conversation.

### MCPO (MCP OpenAPI Proxy)
A proxy that wraps MCP servers and exposes them as an OpenAPI-compatible HTTP endpoint. This allows tools like OpenWebUI to communicate with MCP servers over a standard REST interface.

### Embedding / Vector Embedding
A numerical representation of text as a list of numbers (a vector). Embeddings capture the semantic meaning of text so that similar content produces similar vectors. Azure AI Search stores these embeddings to enable similarity-based document retrieval.

### Chunking
The process of splitting large documents into smaller segments before generating embeddings. Chunking ensures that the pieces of text fed into the model are small enough to be processed effectively and retrieved accurately.

### Token / TPM (Tokens Per Minute)
A token is the basic unit of text that a language model processes — roughly equivalent to a word or word fragment. TPM (Tokens Per Minute) is a rate limit that controls how many tokens a model deployment can handle per minute.

### Inference
The process of running an AI model to generate a response. When you send a message to an LLM, the model performs inference to produce an output.

---

## Azure & Cloud Services

### Azure AI Foundry
Microsoft's cloud platform for hosting and deploying AI models. In this stack, Azure AI Foundry is used to deploy the LLM (GPT-4o) and the embedding model, providing API endpoints that the rest of the system calls.

### Azure AI Search
A cloud search service from Microsoft that stores vector embeddings and supports semantic similarity search. It acts as the knowledge base in the RAG pipeline — documents are indexed here and retrieved at query time.

### Azure Government
A version of Microsoft Azure designed for U.S. government agencies and contractors, hosted in separate datacenters with additional compliance controls. This documentation targets Azure Government deployments.

### API (Application Programming Interface)
A defined interface that allows one software system to communicate with another. In this stack, the LLM and search services are accessed via HTTP-based APIs.

### API Key
A secret string used to authenticate requests to an API. Components in this stack (LiteLLM, RAG website, MCP server) use API keys to prove they are authorized to call Azure AI Foundry and Azure AI Search.

### Resource Group
An Azure organizational container that holds related resources (VMs, search services, AI deployments) for a project. Resources in the same group share a lifecycle and can be managed together.

### VM (Virtual Machine)
A software-based computer that runs on physical hardware in a cloud datacenter. In this stack, an Ubuntu VM hosted on Azure runs Docker, LiteLLM, the RAG website, the MCP server, and OpenWebUI.

### Deployment
In the Azure AI Foundry context, a deployment is a named instance of a model (e.g., `gpt-4o`) that has been provisioned with a specific capacity and assigned an API endpoint.

---

## Networking & Security

### VPN (Virtual Private Network)
An encrypted network tunnel that connects two networks or devices securely over the internet. A VPN is used in this stack so that clients outside the Azure VM can access internal services privately.

### WireGuard
A modern, lightweight VPN protocol used in this stack to create a secure tunnel between client machines and the Azure VM. WireGuard is known for its simplicity and high performance.

### VNet (Virtual Network)
Azure's private network environment where resources like VMs are placed. The VM in this stack resides in a VNet, which controls what traffic can reach it.

### NSG (Network Security Group)
An Azure firewall that filters inbound and outbound traffic to resources in a VNet. NSG rules are configured to allow only the necessary ports (e.g., SSH, WireGuard) to reach the VM.

### NAT (Network Address Translation)
A technique that maps traffic from one IP address range to another. In the WireGuard setup, NAT allows VPN clients to route traffic through the VM to reach Azure services.

### NIC (Network Interface Card)
The virtual network adapter attached to the Azure VM. The NIC connects the VM to the VNet and is associated with the public IP address and NSG rules.

### Split Tunnel / Full Tunnel
Two VPN routing modes. In **split tunnel** mode, only traffic destined for the VPN network is routed through the VPN — other traffic goes directly to the internet. In **full tunnel** mode, all traffic is routed through the VPN.

### DNS (Domain Name System)
The system that translates human-readable domain names (e.g., `example.com`) into IP addresses. DNS settings in WireGuard determine how VPN clients resolve domain names.

### SSH (Secure Shell)
A cryptographic network protocol for securely connecting to a remote machine's command line. SSH is used to access and configure the Azure VM during setup.

---

## Infrastructure & Application Stack

### Docker / Container
Docker is a platform for packaging applications and their dependencies into self-contained units called **containers**. Containers run consistently across different environments. In this stack, Docker runs LiteLLM and OpenWebUI.

### Docker Compose
A tool for defining and running multi-container Docker applications using a single `docker-compose.yml` configuration file. Used in this stack to manage the LiteLLM and OpenWebUI containers together.

### systemd
The service manager for Linux systems. After setup, the RAG website and MCP server run as systemd services so they start automatically on boot and can be managed with `systemctl` commands.

### Flask
A lightweight Python web framework. The RAG website is built with Flask and serves the document upload and query interface on port 7000.

### OpenAPI
A standard specification format for describing REST APIs. The MCP server's tools are exposed via an OpenAPI-compatible endpoint so that clients like OpenWebUI can discover and call them.

### LiteLLM
An open-source proxy that provides a unified OpenAI-compatible API endpoint in front of various LLM backends. In this stack, LiteLLM connects to Azure AI Foundry and runs on port 4000, allowing other services to call the LLM through a single consistent interface.

### OpenWebUI
A web-based chat interface that connects to LLMs and MCP tools. It runs in a Docker container on port 3000 and provides the primary user-facing chat experience in this stack.

### Cline
A VS Code extension that adds an AI coding assistant to the editor. Cline connects to LiteLLM (for the LLM) and the MCP server (for tools), enabling AI-assisted development directly inside VS Code.
