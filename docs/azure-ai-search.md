# Azure AI Search

## Purpose

Create the Azure AI Search service that stores the vectorized document chunks
used by the RAG workflow.

---

## URL

Service endpoint:  `https://<search-service-name>.search.azure.us`

---

## Run Location

Azure portal.

---

## Before You Start

- An Azure Government subscription with permission to create search resources
- A resource group in the target region
- A decision on the pricing tier needed for the project

---

## Context

The RAG website uploads content and embeddings to Azure AI Search, and the MCP
server later queries those indexes. The endpoint URL and admin API key from
this page are used again in later setup steps.

---

## Steps

### Step 1: Create the Azure AI Search service

1. In the Azure portal, search for **Azure AI Search**.
2. Select **+ Create**.
3. On the **Basics** tab:
    - Choose the correct subscription and resource group.
    - Enter a service name, such as `chris-rag-testing`.
    - Select the region, such as **USGov Virginia**.
    - Choose the pricing tier. For this project, **Free** or **Basic** are
      sufficient in most cases. Higher tiers (S, S2, S3, etc.) are available
      if needed.

    !!! note "Free tier limit"
        Azure only allows one Free tier search service per subscription. If you
        already have one, creating another will fail with an error — choose
        **Basic** instead.

4. Review the configuration and create the service.

### Step 2: Locate the endpoint and admin key

1. Open the Azure AI Search resource after deployment finishes.
2. Copy the **URL** shown on the overview page.
3. Open **Keys** in the left navigation.
4. Copy one of the **Admin keys**.

---

## What You Just Set Up

Azure AI Search is now available for the RAG workflow. The service endpoint and
admin key can be used by the RAG website to create indexes and by the MCP
server to expose those indexes as tools.
