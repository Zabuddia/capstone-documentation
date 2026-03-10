# LiteLLM

## Purpose
Run an **OpenAI-compatible** API proxy on the Ubuntu VM so tools like **Cline** and **OpenWebUI** can call Azure Gov **GPT-4o** through a single endpoint.

**URL:** `http://10.55.55.1:4000`

**Auth:** Bearer token using `LITELLM_KEY`

**Config location:** `~/lite-llm/config.yaml` (mounted into the container)


## 1) Create `config.yaml`

On the Ubuntu VM:

```bash
mkdir -p ~/lite-llm
cd ~/lite-llm
nano config.yaml
```
Paste this config (two deployments exposed as one `gpt-4o`):

```yaml
model_list:
  - model_name: gpt-4o # can be anything you want
    litellm_params:
      model: azure/<name_given_to_model> # The name you gave to the model when it was deployed
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_LLM_API_KEY
      api_version: 2025-01-01-preview
      base_model: <Model_name> # from Model Name in Azure

  - model_name: gpt-4o
    litellm_params:
      model: azure/testGPT4o
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_LLM_API_KEY
      api_version: 2025-01-01-preview
      base_model: gpt-4o

litellm_settings:
  drop_params: true
  rate_limiter: local
```

1. Go to AI Hub
2. launch AI Foundry
3. Go into the projects
4. click into your deployed AI model

    * The `model_name: ` can be whatever you want it to be. This is the name that shows up in the applications that access it.
    * Replace name of `model: azure/<name_given_to_model>` with what you named the deployment of your AI model
    * Replace the `base_model: gpt-4o` with the name under "Model name" in Azure


Notes:

- `model_name: gpt-4o` appears twice → LiteLLM will serve **one** model name and route across the two Azure deployments. This allows the model to have an increased token rate

- `api_base`, `api_key`, and `master_key` come from environment variables you pass in via `docker run`.

## 2) Run LiteLLM in Docker

```bash
cd ~/lite-llm

docker run -d \
  --name litellm \
  --restart unless-stopped \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -e AZURE_API_BASE="https://aifoundry0436939217.openai.azure.us" \
  -e AZURE_LLM_API_KEY="PASTE_YOUR_AZURE_LLM_API_KEY_HERE" \
  -p 10.55.55.1:4000:4000 \
  docker.litellm.ai/berriai/litellm:main-stable \
  --config /app/config.yaml \
  --detailed_debug
```

* Note: See [part 4 of Azure AI Foundary instruction](azure-ai-foundry.md#step-4-locate-endpoints-and-keys) to find the endpoint url's and API keys

## 3) Verify it’s up

List models (should show `gpt-4o`):

```bash
curl -s http://10.55.55.1:4000/v1/models
```
Check logs if needed:

```bash
docker logs -n 200 litellm
```

## 4) Updating config

After editing `~/lite-llm/config.yaml`:

```bash
docker restart litellm
```
If you change any `-e ...` environment variables, recreate the container:

```bash
docker rm -f litellm
# rerun the docker run command
```

## 5) Using it from clients (Cline / OpenWebUI)

- **Base URL:** `http://10.55.55.1:4000`
- **API key:** `Leave blank`
- **Model:** `gpt-4o`

(You must be connected to WireGuard to reach `10.55.55.1`.)
