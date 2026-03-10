# Azure AI Search

## Purpose
Provides the **vector search index** that stores and retrieves document chunks for RAG. The RAG website uploads embeddings here, and queries are sent through the Azure AI Search API.

**Endpoint:** `https://chris-rag-testing.search.azure.us`

## Create Azure AI Search Service

1. Search for **Azure AI Search**
2. Click **+ Create**
3. Basic Tab:

    * Select a Resource Group
    * Enter a name: e.g. `chris-rag-testing`
    * Location: (US) USGov Virginia
    * Pricing Tier - Free will allow up to 3 indexes, but Basic will give you 15
    
4. Select **Review + create**
5. Networking -Endpoint connectivity: Public
6. Click **Review + create**
7. Click **Create**
