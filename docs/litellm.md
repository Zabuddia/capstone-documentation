# LiteLLM

## Purpose

Run an OpenAI-compatible API on the Ubuntu VM so OpenWebUI and Cline can use an
Azure OpenAI deployment through a single endpoint.

---

## URL

- LiteLLM API: `http://10.55.55.1:4000`
- Model list endpoint: `http://10.55.55.1:4000/v1/models`

---

## Run Location

Ubuntu VM.

---

## Before You Start

- A model is deployed in [Azure AI Foundry](azure-ai-foundry.md#step-3-deploy-an-ai-model)
- The project endpoint and API key are available from
  [Azure AI Foundry](azure-ai-foundry.md#step-4-locate-endpoints-and-keys)
- [Docker](docker.md#docker) is installed on the VM
- [WireGuard](wireguard.md#wireguard) is in place so clients can reach
  `10.55.55.1`

---

## Context

LiteLLM gives the rest of the stack a single OpenAI-compatible endpoint. In the
example below, the Azure deployment is exposed as `gpt-4o`.

---

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

- `<deployment-name>` — the name you gave the deployment in Azure AI Foundry
  (e.g. `gpt-4o-virginia`). This is set in
  [Step 3 of Azure AI Foundry](azure-ai-foundry.md#step-3-deploy-an-ai-model).
- `<base-model-name>` — the underlying Azure OpenAI model name (e.g. `gpt-4o`).
  This is the **Model name** shown in
  [Step 4 of Azure AI Foundry](azure-ai-foundry.md#step-4-locate-endpoints-and-keys).

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

!!! note "Adding more deployments"
    If traffic later needs to be spread across multiple Azure deployments,
    additional entries can be added to `config.yaml` with the same
    `model_name`. LiteLLM can then route requests across deployments that
    expose the same underlying model.

!!! example "Increase effective TPM with two equivalent deployments"
    If two Azure deployments serve the same base model, both can be listed
    under the same LiteLLM alias. This is useful when each deployment has its
    own Tokens Per Minute quota and you want LiteLLM to spread requests across
    them.

    In this example, both Azure deployments map to the same LiteLLM model name
    `gpt-5.1`, so clients still call one model while LiteLLM can use either
    backend deployment:

        model_list:
          - model_name: gpt-5.1
            litellm_params:
              model: azure/gpt-5.1-virginia
              api_base: os.environ/AZURE_API_BASE_VIRGINIA
              api_key: os.environ/AZURE_LLM_API_KEY_VIRGINIA
              api_version: 2025-01-01-preview
              base_model: gpt-5.1

          - model_name: gpt-5.1
            litellm_params:
              model: azure/gpt-5.1-arizona
              api_base: os.environ/AZURE_API_BASE_ARIZONA
              api_key: os.environ/AZURE_LLM_API_KEY_ARIZONA
              api_version: 2025-01-01-preview
              base_model: gpt-5.1

        litellm_settings:
          drop_params: true
          rate_limiter: local

    Each Azure deployment keeps its own quota, so using multiple equivalent
    deployments can increase total available throughput while preserving a
    single model name for clients.

### Step 3: Run LiteLLM in Docker

```bash
cd ~/lite-llm
```

Both values come from
[Step 4 of Azure AI Foundry](azure-ai-foundry.md#step-4-locate-endpoints-and-keys):

- `AZURE_API_BASE` — the **Azure AI model inference endpoint**
- `AZURE_LLM_API_KEY` — the **Key**

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

If `config.yaml` references additional environment variables, add more `-e`
flags to the same `docker run` command. For example, the two-deployment
configuration above would also need:

```bash
-e AZURE_API_BASE_VIRGINIA="https://<virginia-endpoint>.openai.azure.us/" \
-e AZURE_LLM_API_KEY_VIRGINIA="<VIRGINIA_API_KEY>" \
-e AZURE_API_BASE_ARIZONA="https://<arizona-endpoint>.openai.azure.us/" \
-e AZURE_LLM_API_KEY_ARIZONA="<ARIZONA_API_KEY>" \
```

Those variable names must match the names used in `config.yaml`.

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

---

## What You Just Set Up

LiteLLM now provides a single OpenAI-compatible endpoint on the VM. OpenWebUI
and Cline can connect to that endpoint instead of talking directly to Azure
OpenAI.
