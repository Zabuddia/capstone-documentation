# LiteLLM

## Purpose

Run an OpenAI-compatible API on the Ubuntu VM so OpenWebUI and Cline can use an
Azure OpenAI deployment through a single endpoint.

## URL

- LiteLLM API: `http://10.55.55.1:4000`
- Model list endpoint: `http://10.55.55.1:4000/v1/models`

## Run Location

Ubuntu VM.

## Before You Start

- A model is deployed in [Azure AI Foundry](azure-ai-foundry.md#step-3-deploy-an-ai-model)
- The project endpoint and API key are available from
  [Azure AI Foundry](azure-ai-foundry.md#step-4-locate-endpoints-and-keys)
- [Docker](docker.md#docker) is installed on the VM
- [WireGuard](wireguard.md#wireguard) is in place so clients can reach
  `10.55.55.1`

## Context

LiteLLM gives the rest of the stack a single OpenAI-compatible endpoint. In the
example below, the Azure deployment is exposed as `gpt-4o`. If traffic later
needs to be spread across multiple Azure deployments, additional entries can be
added to `config.yaml` with the same `model_name`.

## Steps

### Step 1: Create the LiteLLM configuration directory

```bash
mkdir -p ~/lite-llm
```

```bash
cd ~/lite-llm
```

### Step 2: Create `config.yaml`

```bash
nano ~/lite-llm/config.yaml
```

Paste the following configuration and replace the placeholders:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/<deployment-name>
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_LLM_API_KEY
      api_version: 2025-01-01-preview
      base_model: <base-model-name>

litellm_settings:
  drop_params: true
  rate_limiter: local
```

### Step 3: Run LiteLLM in Docker

```bash
cd ~/lite-llm
```

```bash
docker run -d \
  --name litellm \
  --restart unless-stopped \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -e AZURE_API_BASE="https://<azure-openai-endpoint>.openai.azure.us/" \
  -e AZURE_LLM_API_KEY="<AZURE_OPENAI_API_KEY>" \
  -p 10.55.55.1:4000:4000 \
  docker.litellm.ai/berriai/litellm:main-stable \
  --config /app/config.yaml
```

!!! note "No API key required"
    This example does not set a LiteLLM master key. Clients on WireGuard can
    connect without sending an API key. This is intentional for this setup
    since the endpoint is only reachable over the private VPN tunnel.

### Step 4: Validate the LiteLLM endpoint

```bash
curl -s http://10.55.55.1:4000/v1/models
```

```bash
docker logs -n 200 litellm
```

The model list should include the alias from `config.yaml`, such as `gpt-4o`.

### Step 5: Update the configuration later if needed

After editing `~/lite-llm/config.yaml`, restart the container:

```bash
docker restart litellm
```

If the Docker environment variables change, recreate the container:

```bash
docker rm -f litellm
```

Run the `docker run` command again after removing the container.

## What You Just Set Up

LiteLLM now provides a single OpenAI-compatible endpoint on the VM. OpenWebUI
and Cline can connect to that endpoint instead of talking directly to Azure
OpenAI.
