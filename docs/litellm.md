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
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o-virginia-dzs
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_LLM_API_KEY
      api_version: 2025-01-01-preview
      base_model: gpt-4o
      tpm: 25000
      rpm: 100

  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o-virginia-s
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_LLM_API_KEY
      api_version: 2025-01-01-preview
      base_model: gpt-4o
      tpm: 40000
      rpm: 100

litellm_settings:
  drop_params: true
  rate_limiter: local

general_settings:
  master_key: os.environ/LITELLM_KEY
```
Notes:

- `model_name: gpt-4o` appears twice → LiteLLM will serve **one** model name and route across the two Azure deployments.

- `api_base`, `api_key`, and `master_key` come from environment variables you pass in via `docker run`.


## 2) Create a LiteLLM API key

```bash
echo "sk-$(openssl rand -hex 24)"
```

## 3) Run LiteLLM in Docker

```bash
cd ~/lite-llm

docker run -d \
  --name litellm \
  --restart unless-stopped \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -e AZURE_API_BASE="https://aifoundry0436939217.openai.azure.us" \
  -e AZURE_LLM_API_KEY_VIRGINIA="PASTE_YOUR_AZURE_LLM_API_KEY_HERE" \
  -e LITELLM_KEY="sk-PASTE_YOUR_LITELLM_KEY_HERE" \
  -p 10.55.55.1:4000:4000 \
  docker.litellm.ai/berriai/litellm:main-stable \
  --config /app/config.yaml \
  --detailed_debug
```

## 4) Verify it’s up

List models (should show `gpt-4o`):

```bash
curl -s \
  -H "Authorization: Bearer sk-PASTE_YOUR_LITELLM_KEY_HERE" \
  http://10.55.55.1:4000/v1/models
```
Check logs if needed:

```bash
docker logs -n 200 litellm
```

## 5) Updating config

After editing `~/lite-llm/config.yaml`:

```bash
docker restart litellm
```
If you change any `-e ...` environment variables, recreate the container:

```bash
docker rm -f litellm
# rerun the docker run command
```

## 6) Using it from clients (Cline / OpenWebUI)

- **Base URL:** `http://10.55.55.1:4000`
- **API key:** `LITELLM_KEY` (the `sk-...` value)
- **Model:** `gpt-4o`

(You must be connected to WireGuard to reach `10.55.55.1`.)
