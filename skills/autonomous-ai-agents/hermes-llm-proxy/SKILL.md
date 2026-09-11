---
name: hermes-llm-proxy
description: "Configure local LLM API proxy for Hermes."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
---

# Hermes LLM Proxy Integration

This skill covers installing a local LLM API proxy server (such as FreeLLMAPI) and wiring it into Hermes Agent as a custom provider.

## When to Use

- You want to aggregate multiple free LLM provider keys behind a single unified API key.
- You want automatic failover and load balancing across providers.
- You want to keep API keys isolated from Hermes configuration (proxy handles rotation).

## Prerequisites

- Node.js 20–24 (FreeLLMAPI requirement; adjust for other proxies).
- Hermes Agent installed and configured.
- Access to provider API keys (e.g., Google Gemini, Groq, Mistral, etc.).
- **Preference**: Install the proxy in `~/.local/share/llm-proxy` for persistence (avoid `/tmp`).

## Installation Steps

### 1. Clone the Proxy Repository

```bash
# Choose installation directory (recommended: ~/.local/share/llm-proxy for persistence)
mkdir -p ~/.local/share/llm-proxy
cd ~/.local/share/llm-proxy
# Example for FreeLLMAPI:
git clone https://github.com/tashfeenahmed/freellmapi.git .
```

### 2. Install Dependencies and Build

```bash
npm install
npm run build -w server   # adjust if proxy uses different workspace
npm run build -w cli
```

### 3. Configure Environment

```bash
# Generate encryption key (32 bytes hex)
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Create .env
cat > .env <<EOF
ENCRYPTION_KEY=<64-char-hex-key>
PORT=3001   # or any free port
EOF
```

### 4. Set Up as a Systemd User Service (Optional but Recommended)

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/llm-proxy.service << 'EOF'
[Unit]
Description=LLM Proxy Server
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/.local/share/llm-proxy/server
ExecStart=/usr/bin/node dist/index.js
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now llm-proxy
systemctl --user status llm-proxy  # verify active
```

### 5. Create Admin Account

On first boot, the proxy logs a setup code. Retrieve it:

```bash
journalctl --user -u llm-proxy | grep "setup code"
```

Visit `http://localhost:3001` on the same machine, enter the code, email, and password to create the admin account.

**Alternative: Create admin account directly via API (no setup code needed when on same machine):**

```bash
curl -s -X POST http://localhost:3001/api/auth/setup \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@local","password":"SecurePass123!","name":"Admin"}'
```

This returns a JWT token; save it for the next step.

### 6. Add Provider API Keys

Obtain the unified API key from the proxy (stored in its SQLite DB):

```bash
UNIFIED_KEY=$(sqlite3 ~/.local/share/llm-proxy/server/data/freeapi.db "SELECT value FROM settings WHERE key='unified_api_key';")
echo "Unified API Key: $UNIFIED_KEY"
```

Then add provider keys via the proxy's API (requires admin token from step 5):

```bash
ADMIN_TOKEN=<token-from-setup>
curl -s -X POST http://localhost:3001/api/keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"name":"Google Gemini","platform":"google","key":"<GEMINI_API_KEY>","notes":""}'
```

Repeat for other providers as needed.

### 7. Configure Hermes to Use the Proxy

1. Export the unified API key to your shell environment (add to `~/.bashrc` or similar):

```bash
echo 'export HERMES_LLMPROXY_KEY="'$UNIFIED_KEY'"' >> ~/.bashrc
source ~/.bashrc
```

2. Edit Hermes configuration (`~/.hermes/config.yaml`):

   **Important:** The `custom_providers` block cannot be added via `hermes config set`; you must edit the file directly or use an overlay.

   First, update the `model` section to use the proxy:

```yaml
model:
  provider: custom
  default: auto              # let proxy choose best model
  base_url: http://localhost:3001/v1
  api_key: ${HERMES_LLMPROXY_KEY}
```

   Then, append the following to the end of the file (or insert under a `custom_providers:` key if it exists):

```yaml
custom_providers:
  - name: LLMProxy
    base_url: http://localhost:3001/v1
    key_env: HERMES_LLMPROXY_KEY
    model: auto
    models:
      auto: {}
      fusion: {}
    models_discovered: false
```

   **Note:** If you already have a `custom_providers` list, add the new entry under that list instead of duplicating the key.

### 8. Verify Integration

```bash
# Refresh Hermes model list (requires interactive terminal)
hermes model --refresh

# Test a simple request
hermes -z "Say hello in 5 words"
```

You should see a successful response routed through the proxy.

## Troubleshooting

- **Proxy not responding**: Check service status with `systemctl --user status llm-proxy` and view logs (`journalctl --user -u llm-proxy -f`).
- **Authentication errors**: Ensure the unified API key in Hermes matches the one in the proxy's database.
- **All models exhausted**: Verify that at least one provider API key has been added in the proxy's dashboard or via API.
- **Port already in use**: Change `PORT` in `.env` and update `base_url` in Hermes config accordingly.

## The Dashboard (Client)

The dashboard is a **separate Vite app** under `client/`, not part of the server process. Two ways to run it:

- **Built-in (persistent, no extra step):** `npm run build -w client` emits `client/dist/`, and the server serves it automatically at `http://localhost:3001/` (see `serveStaticAssets` in `server/src/app.ts`, default `true`). The systemd service from Step 4 serves the dashboard with no extra work — this is the permanent setup.
- **Dev server (ephemeral):** `npm run -w client` starts Vite on `localhost:5173` (or `PORT`), proxying `/api` and `/v1` to the server. It is **not persistent** — it dies when the terminal closes, and it is only needed while editing the dashboard UI. Do not rely on it for production access.

### First-run / login

The dashboard is gated behind an account. On first boot:

1. The server logs a one-time setup code (remote first-run only). Local/loopback setup ignores it.
2. Visit `http://localhost:3001/` → **Create account** (email + password, min 8 chars). Or create directly via API:

```bash
curl -s -X POST http://localhost:3001/api/auth/setup \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@local","password":"SecurePass123!","name":"Admin"}'
```

3. Subsequent visits show **Sign in** with the same email/password. The session token is stored in `localStorage` (`freellmapi_dashboard_token`).

### Verifying the dashboard actually renders

`curl` only proves the bytes are served — it cannot tell you whether the SPA boots. Verify with a real browser:

```bash
# Static checks (all should be 200):
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3001/
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3001/assets/index-*.js
curl -s http://localhost:3001/api/auth/status   # {"needsSetup":...,"authenticated":...}

# Render check — headless Chromium, confirm #root is populated:
chromium --headless --no-sandbox --disable-dev-shm-usage --dump-dom \
  --virtual-time-budget=3000 http://localhost:3001/ | grep -oE 'Sign in|Dashboard|Providers|API Keys'
```

A blank `#root` or a `NotFoundError` HTML body (instead of `index.html`) for non-API routes means the SPA fallback in `server/src/app.ts` is broken — see Troubleshooting.

## Updating the Proxy

```bash
cd ~/.local/share/llm-proxy
git pull
npm install
npm run build -w server
npm run build -w client   # rebuild the dashboard too
npm run build -w cli
systemctl --user restart llm-proxy
```

**Note:** rebuilding `client/` changes `client/dist/` and thus the dashboard the server serves. If you only touch server code, skip the client build. If the dashboard stops rendering after an update, the client build is the usual culprit.

## Using with llama.cpp server

You can also run a local `llama.cpp` server and configure Hermes to use it as a custom OpenAI-compatible endpoint. See `references/llama-cpp.md` for detailed steps.

## References

- FreeLLMAPI repository: https://github.com/tashfeenahmed/freellmapi
- Hermes custom provider documentation: https://hermes-agent.nousresearch.com/docs/references/providers-and-models.md
- llama.cpp server guide: references/llama-cpp.md

---
