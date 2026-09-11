---
name: freellmapi-config
description: "Configure Hermes agent to use FreeLLMAPI as LLM proxy."
version: 1.0.0
license: MIT
---

# FreeLLMAPI Configuration for Hermes Agent

Use when configuring the Hermes agent to use FreeLLMAPI as the LLM proxy.

## Why
FreeLLMAPI provides a unified OpenAI-compatible API gateway for multiple LLM providers, allowing the Hermes agent to switch between models seamlessly.

## Setup
1. Install FreeLLMAPI from GitHub (the npm package `freellmapi` is the CLI wrapper only and lags behind releases — npm shows v0.5.1 while GitHub releases are at v0.9.7+):
   ```bash
   npm install -g github:tashfeenahmed/freellmapi#<tag>
   ```
   Replace `<tag>` with the desired release (e.g., `v0.9.7`). Check latest: `curl -s 'https://api.github.com/repos/tashfeenahmed/freellmapi/releases/latest' | grep -o '"tag_name": *"[^"]*"' | head -1 | cut -d'"' -f4`
2. Run the one-click updater to always get the latest release:
   ```bash
   update-freellmapi            # latest tag
   update-freellmapi v0.9.6     # pin an older tag
   ```
   Script lives at `~/.local/bin/update-freellmapi` — fetches the latest GitHub release tag dynamically, cleans stale `@freellmapi/monorepo` symlinks from failed installs, then installs via `npm install -g github:tashfeenahmed/freellmapi#<tag>`, and verifies.
3. Obtain the unified API key from the FreeLLMAPI dashboard (or via the tray popover in the desktop app).
4. Set the Hermes agent's model API key:
   ```bash
   hermes config set model.api_key "<your-unified-api-key>"
   ```
   Alternatively, set the environment variable `HERMES_FREELMAPI_KEY` and the agent will read it automatically if the config uses `${HERMES_FREELMAPI_KEY}`.
5. Verify the configuration:
   ```bash
   hermes config get model.api_key
   ```

## Pitfalls
- Using an incorrect variable reference in the config (e.g., `${freellmapi-...}`) will cause authentication failures.
- Forgetting to set the environment variable if using variable substitution in the config.
- Using an expired or invalid API key from the FreeLLMAPI dashboard.

## Verification
After setting the key, test with a simple completion:
```bash
curl -s -X POST http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-unified-api-key>" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Say hello"}],"max_tokens":5}'
```

## References
- FreeLLMAPI documentation: https://github.com/tashfeenahmed/freellmapi
- Hermes agent configuration: https://hermes-agent.nousresearch.com/docs/configuration