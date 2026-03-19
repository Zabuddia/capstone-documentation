# RAG Website

## Purpose

Run the Flask application that manages Azure AI Search indexes, uploads PDFs,
and scrapes websites for RAG content.

## URL

`http://10.55.55.1:7000`

## Run Location

Local machine for downloading and uploading the starter bundle, Ubuntu VM for
installation and configuration, and a browser on a WireGuard-connected client
for validation.

## Before You Start

- [Azure AI Search](azure-ai-search.md#azure-ai-search) is created
- A text embedding model is deployed in
  [Azure AI Foundry](azure-ai-foundry.md#step-3-deploy-an-ai-model)
- The [Ubuntu VM](ubuntu-virtual-machine.md#ubuntu-virtual-machine) is ready
- Python 3 and virtual environment support are installed on the VM

## Context

The starter bundle expands into `~/rag-website`. It includes the application
code, templates, configuration files, and a systemd unit file. After
extracting it, edit `config/config.yaml` and `deploy/rag-website.service` to
match the environment.

## Steps

### Step 1: Download the starter bundle

Download:

- [RAG Website starter bundle](downloads/rag-website.tar.gz)

### Step 2: Upload the bundle to the Ubuntu VM

Run this command on the local machine:

```bash
scp -i /path/to/your-key.pem ~/Downloads/rag-website.tar.gz <VM_USER_NAME>@<VM_PUBLIC_IP>:/home/<VM_USER_NAME>/
```

### Step 3: Extract the bundle on the Ubuntu VM

```bash
tar -xzf ~/rag-website.tar.gz -C ~/
```

### Step 4: Edit the configuration files

Edit the application configuration:

```bash
nano ~/rag-website/config/config.yaml
```

Replace the placeholder values for:

- The Azure AI Search endpoint
- The Azure OpenAI endpoint
- The embedding deployment name

Edit the systemd unit file:

```bash
nano ~/rag-website/deploy/rag-website.service
```

Replace the placeholders for:

- `<VM_USER_NAME>`
- `<AZURE_AI_SEARCH_API_KEY>`
- `<AZURE_OPENAI_API_KEY>`

### Step 5: Create the Python virtual environment and install dependencies

```bash
cd ~/rag-website
```

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### Step 6: Install the systemd unit

Copy the service file into systemd:

```bash
sudo cp ~/rag-website/deploy/rag-website.service /etc/systemd/system/rag-website.service
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

### Step 7: Start the service and enable it at boot

```bash
sudo systemctl enable --now rag-website
```

### Step 8: Validate the website

```bash
sudo systemctl status rag-website
```

```bash
sudo journalctl -u rag-website -n 100 --no-pager
```

```bash
curl -I http://10.55.55.1:7000
```

Open the site from a client connected over WireGuard:

- `http://10.55.55.1:7000`

## What You Just Set Up

The RAG website is now running on the VM and can create, update, and delete
Azure AI Search indexes. It also provides the main interface for uploading
documents and web content into the RAG pipeline.
