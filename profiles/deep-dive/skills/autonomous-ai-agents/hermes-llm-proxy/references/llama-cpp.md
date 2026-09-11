# Using llama.cpp Server with Hermes

This guide shows how to run a local llama.cpp server and configure Hermes to use it as a custom OpenAI-compatible endpoint.

## Prerequisites

- llama.cpp installed with `llama-server` binary (or `llama serve`).
- A GGUF model file (e.g., from Hugging Face).
- Hermes Agent installed.

## Steps

### 1. Locate your GGUF model

Find the exact path to your `.gguf` file, e.g.: `/home/user/.cache/huggingface/hub/models--username--model-name/snapshots/<hash>/model.gguf`

### 2. Start the llama.cpp server

```bash
llama-server \
  -m /path/to/model.gguf \
  --port 8080 \
  -c 8192 \
  -ngl 99
```

Adjust:
- `-c`: context size (default from model, e.g., 8192)
- `-ngl`: number of GPU layers to offload (set to 99 for full GPU if enough VRAM; adjust based on your GPU memory)
- `--host`: if needed to bind to a specific interface (default listens on 0.0.0.0)

### 3. Verify the server is running

```bash
curl -s http://localhost:8080/health
# Expected: {"status":"ok"}
```

### 4. Configure Hermes

#### Option A: Edit config.yaml directly

```yaml
model:
  provider: custom
  default: auto
  base_url: http://localhost:8080/v1
  api_key: sk-local

litellm:
  default_model: "openai/local-model"

context_length: 8192
```

#### Option B: Use Hermes CLI commands

```bash
hermes config set model.provider custom
hermes config set model.base_url http://localhost:8080/v1
hermes config set model.api_key sk-local
hermes config set litellm.default_model "openai/local-model"
hermes config set context_length 8192
```

### 5. Test the integration

```bash
hermes -z "Say hello in one sentence"
```

You should receive a response from the model.

## Notes

- The `api_key` value can be any string; the llama.cpp server does not validate it.
- If you change the model or server settings, restart the server.
- For multi-GPU setups, consult llama.cpp documentation for `--tensor-split` and `--split-mode`.

## Troubleshooting

- **Server not responding**: Ensure the server process is running and listening on the configured port (`ss -tlnp | grep :8080`).
- **Connection refused**: Double-check `base_url` and port.
- **Out of GPU memory**: Reduce `-ngl` or enable CPU offload.
- **Context length errors**: Ensure `context_length` in Hermes matches `-c` used for the server.

## Related

- Hermes custom provider documentation: `references/providers-and-models.md` (in hermes-agent skill)
- llama.cpp documentation: https://github.com/ggerganov/llama.cpp
