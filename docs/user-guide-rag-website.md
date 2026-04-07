# RAG Website User Guide

## Overview

The RAG Website is a centralized interface for managing the knowledge bases that power your AI solutions. By uploading documents or scraping web pages, you create **indexes** — isolated collections of content that the AI can search through when answering questions. This guide covers every step of creating, editing, and managing indexes through the Index Manager.

---

## Prerequisites

- Documents you want to upload are ready (PDF, plain text, or source code files)
- WireGuard is connected on your local machine

---

## Key Concepts

### What is an Index?

An index is an isolated knowledge base stored in Azure AI Search. Think of it as a dedicated "brain" for a specific topic or project. Each index is independent — the AI only searches the index you point it at, so keeping indexes focused on a single subject improves answer quality.

### What are Embeddings and Vector Dimensions?

When a document is added to an index, the system converts each chunk of text into a list of numbers called an **embedding**. An embedding captures the meaning of that text in a way a computer can compare and search — two chunks about similar topics will have embeddings that are numerically close to each other.

**Vector Dimensions** controls how many numbers are in each embedding. The default is **3072**, which matches the output size of the embedding model in use. You should not change this value unless you are switching to a different embedding model that produces a different output size, as a mismatch will break the index.

### What is Chunk Size?

Before a document is indexed, it is split into smaller segments called chunks. **Chunk Size** controls the maximum number of tokens (roughly, word-pieces) in each segment.

- **Smaller chunks** (e.g., 512) give more precise retrieval — the AI gets a tighter, more focused passage — but may lose surrounding context.
- **Larger chunks** (e.g., 1024–2048) preserve more context around each passage but may include irrelevant content in the retrieved segment.

A chunk size of **512–1024** is a reasonable starting point for most documentation. If your documents have dense, self-contained sections (e.g., API reference pages), lean toward smaller chunks. If they rely heavily on context across paragraphs (e.g., narrative procedures), lean larger.

---

## The Index Manager Dashboard

The Index Manager is the landing page at `http://10.55.55.1:7000`. It lists every index currently available.

| Column | Description |
|---|---|
| **Index Name** | Unique identifier for the index in Azure AI Search. Click the name to open its edit page. |
| **Description** | A summary of the index's purpose. |
| **Documents** | Total number of processed document chunks in the index. |
| **Status** | Current state — **Active** means the index is reachable and ready to query. |
| **Created** | Timestamp of when the index was first created. |
| **Actions** | **Edit** to add content or update the description. **Delete** to permanently remove the index and all its data. |

Use the **Search** bar at the top right to filter indexes by name.

!!! warning
    There is no way to view the individual files that have been added to an index — only the total document count is shown. Keep a separate record of what you have uploaded to each index if you need to track this.

---

## Creating a New Index

Click **+ Create Index** on the dashboard to open the creation form.

### Step 1: Configure the Index

Fill in the following fields:

- **Index Name** — A unique identifier. Use lowercase letters, numbers, and hyphens (e.g., `project-docs`). This name is used by the MCP server to reference the index as a tool.
- **Vector Dimensions** — Leave this at the default **3072** unless you are using a different embedding model.
- **Chunk Size** — Select from the dropdown. If unsure, start with **512** and adjust based on the quality of responses you get.
- **Description** — A short summary of the index's contents and purpose. This is for your own reference only — the AI model does not see this description when querying the index.

### Step 2: Add Content

You can add content via file upload, a URL, or both at the same time.

**Upload Files**

Click **Choose Files** and select one or more files from your computer. Supported types include:

- PDF documents
- Plain text files (`.txt`)
- Source code files (read as plain text)

!!! warning
    The index will accept all file types, but files with non-text content (e.g., images, binary files) will not produce meaningful results. Only upload files whose text content you want the AI to search.

!!! warning
    The index does not prevent duplicate uploads. If you upload the same file twice, its content will be added to the index twice, which can cause the AI to return redundant results. Keep track of what you have already added.

**Upload URL**

Paste a URL into the **Upload URL** field and click **Create Index**. The site will scrape the page, find all links on that domain, and show you a **Select Links to Scrape** page. Check the boxes next to the pages you want to add to the index, then click **Add Selected to Index**.

### Step 3: Submit

Click **Create Index**. The system will process and embed your documents into Azure AI Search. Larger uploads take more time — the index will show as **Active** on the dashboard once indexing is complete.

---

## Editing an Existing Index

Click **Edit** next to any index on the dashboard to open the Edit Index page.

### Read-Only Information

These fields reflect the current state of the index and cannot be changed:

- **Created At** — When the index was first created.
- **Status** — Whether the index is currently active.
- **Number of Documents** — Total chunk count across all uploaded files.

### Updating the Index

- **Description** — Edit the text field to update the description for your own reference.
- **Add Files to Index** — Drag and drop files onto the upload area, or click **Choose Files** to browse. New files are added to the existing index without removing previously indexed content.
- **Add a Website URL to Scrape** — Enter a URL to scrape additional web pages into the index. This follows the same link-selection flow as during creation.

Click **Update Index & Add Files** to save changes and trigger ingestion for any new content.

---

## Using an Index with the AI

Indexes are exposed to the AI assistant as tools via the MCP server. To use an index during a conversation:

1. Connect your AI assistant (Cline or OpenWebUI) to the MCP server (see the CLine and OpenWebUI user guides).
2. In your AI assistant (Cline or OpenWebUI), the available indexes will appear as selectable tools.
3. Ask a question — the AI will automatically query the relevant index and cite the passages it found.

!!! note
    The AI does not have access to the index description. Give your indexes clear, consistent names so you can identify the right one when selecting tools.

---

## Tips

- Keep each index focused on a single topic or project. Mixed-content indexes produce lower-quality answers.
- After adding new documents, allow a moment for indexing to complete before querying.
- Chunk size affects retrieval quality more than most other settings. If answers are missing context, try re-creating the index with a larger chunk size.
