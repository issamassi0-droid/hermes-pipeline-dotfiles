#!/usr/bin/env python3
"""
Provider Health Monitor + Auto-Reconnect (v2)
Provider-agnostic: works with any OpenAI-compatible API endpoint.

Features:
  - Health checks with exponential backoff
  - Failover to backup providers on primary failure
  - No proxy restart — retry + switch, not restart
  - Configurable via env vars or ~/.hermes/providers.json

Usage:
    python3 provider_health.py --check              # single check
    python3 provider_health.py --daemon              # background watchdog
    python3 provider_health.py --list                # show current providers
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import urllib.request
import urllib.error

# --- Defaults ---
DEFAULT_PRIMARY = os.environ.get("HERMES_PROVIDER_URL", "http://localhost:3001/v1/models")
DEFAULT_API_KEY = os.environ.get("HERMES_FREELMAPI_KEY", "")
CONFIG_PATH = Path.home() / ".hermes" / "providers.json"
LOG_PATH = Path.home() / ".hermes" / "provider_health.log"

CHECK_INTERVAL = int(os.environ.get("HERMES_HEALTH_INTERVAL", "15"))
MAX_RETRIES = int(os.environ.get("HERMES_MAX_RETRIES", "3"))
BACKOFF_BASE = float(os.environ.get("HERMES_BACKOFF_BASE", "2.0"))
BACKOFF_MAX = float(os.environ.get("HERMES_BACKOFF_MAX", "60.0"))
FAILOVER_DELAY = int(os.environ.get("HERMES_FAILOVER_DELAY", "10"))


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


class Provider:
    """Represents a single LLM provider endpoint."""

    def __init__(self, name: str, url: str, api_key: str, priority: int = 0) -> None:
        self.name = name
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.priority = priority  # lower = higher priority
        self.failures = 0
        self.last_failure: float = 0.0
        self.circuit_open = False
        self.circuit_opened_at: float = 0.0

    @property
    def health_url(self) -> str:
        # If URL already ends with /models or /health, use as-is
        if self.url.endswith(("/models", "/health")):
            return self.url
        # Strip version suffix and add /models
        base = self.url.replace("/v1/models", "").rstrip("/")
        return f"{base}/models"

    def check(self, timeout: float = 10.0) -> tuple[bool, Optional[str]]:
        """Returns (healthy, error_message)."""
        if self.circuit_open:
            if time.monotonic() - self.circuit_opened_at > 60:
                self.circuit_open = False  # half-open retry
            else:
                return False, "circuit open"

        if not self.api_key:
            return False, "no API key"

        req = urllib.request.Request(self.health_url)
        req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    if self.failures > 0:
                        log(f"  {self.name}: recovered after {self.failures} failures")
                    self.failures = 0
                    self.circuit_open = False
                    return True, None
                return False, f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return False, "auth failed (401)"
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, f"unreachable ({e.reason})"
        except Exception as e:
            return False, str(e)

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure = time.monotonic()
        if self.failures >= 3:
            self.circuit_open = True
            self.circuit_opened_at = time.monotonic()


class ProviderManager:
    """Manages primary + failover providers."""

    def __init__(self, config: dict) -> None:
        self.providers: list[Provider] = []
        for p in config.get("providers", []):
            self.providers.append(Provider(
                name=p["name"],
                url=p["url"],
                api_key=p.get("api_key", ""),
                priority=p.get("priority", 99),
            ))
        self.providers.sort(key=lambda p: p.priority)
        self.active_idx = 0
        self.failover_count = 0

    @property
    def primary(self) -> Optional[Provider]:
        return self.providers[self.active_idx] if self.providers else None

    @property
    def active(self) -> Optional[Provider]:
        for i, p in enumerate(self.providers):
            if not p.circuit_open:
                return p
        return None  # all circuits open

    def failover(self) -> Optional[Provider]:
        """Switch to next available provider."""
        if self.active_idx >= len(self.providers) - 1:
            return None  # no backup
        self.active_idx += 1
        self.failover_count += 1
        p = self.active
        if p:
            log(f"FAILOVER → {p.name} (priority {p.priority})")
        return p

    def all_healthy(self) -> bool:
        return any(not p.circuit_open for p in self.providers)


def load_config() -> dict:
    """Load provider config from env, file, or defaults."""
    # 1. Try providers.json
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
            if data.get("providers"):
                return data
        except json.JSONDecodeError:
            pass

    # 2. Build from env vars (single provider)
    url = os.environ.get("HERMES_PROVIDER_URL", "")
    key = os.environ.get("HERMES_FREELMAPI_KEY", "")
    if url:
        return {"providers": [{"name": "env-primary", "url": url, "api_key": key, "priority": 0}]}

    # 3. Default: localhost FreeLLMAPI
    return {"providers": [{"name": "localhost", "url": "http://localhost:3001/v1/models", "api_key": "", "priority": 0}]}


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def cmd_check(manager: ProviderManager) -> int:
    """Single health check."""
    active = manager.active
    if not active:
        log("❌ All providers circuit-open")
        return 1

    healthy, err = active.check()
    if healthy:
        log(f"✅ {active.name} healthy")
        return 0

    log(f"❌ {active.name}: {err}")
    # Try failover
    backup = manager.failover()
    if backup:
        h, e = backup.check()
        if h:
            log(f"✅ Failover active: {backup.name}")
            return 0
        log(f"❌ Failover also down: {e}")
    return 1


def cmd_list(manager: ProviderManager) -> None:
    for p in manager.providers:
        status = "OPEN" if p.circuit_open else "closed"
        log(f"  {p.name} (pri={p.priority}) circuit={status} failures={p.failures}")


def daemon_loop(manager: ProviderManager) -> None:
    """Background watchdog: check, failover on failure, exponential backoff."""
    log(f"Daemon started — interval={CHECK_INTERVAL}s, providers={len(manager.providers)}")
    consecutive_failures = 0
    backoff = 1.0

    while True:
        active = manager.active
        if not active:
            log("All providers down — waiting before retry")
            time.sleep(FAILOVER_DELAY)
            continue

        healthy, err = active.check()
        if healthy:
            if consecutive_failures > 0:
                log(f"RECOVERED — {active.name} back online")
            consecutive_failures = 0
            backoff = 1.0
        else:
            consecutive_failures += 1
            active.record_failure()
            log(f"FAILURE {consecutive_failures}/{MAX_RETRIES}: {active.name} — {err}")

            if consecutive_failures >= MAX_RETRIES:
                log("Threshold reached — attempting failover")
                backup = manager.failover()
                if backup:
                    # Validate backup immediately
                    h, e = backup.check()
                    if h:
                        log(f"Failover validated: {backup.name} active")
                        consecutive_failures = 0
                        backoff = 1.0
                        continue
                    else:
                        log(f"Backup also down: {e}")
                else:
                    log("No backup providers available")

                # Reset to try primary again after delay (it may have recovered)
                manager.active_idx = 0
                consecutive_failures = 0
                backoff = min(backoff * BACKOFF_BASE, BACKOFF_MAX)

        # Adaptive sleep: back off when failing, normal when healthy
        sleep_time = backoff if not healthy else CHECK_INTERVAL
        time.sleep(sleep_time)


def main() -> int:
    parser = argparse.ArgumentParser(description="Provider Health Monitor")
    parser.add_argument("--daemon", action="store_true", help="Run as background watchdog")
    parser.add_argument("--check", action="store_true", help="Single health check")
    parser.add_argument("--list", action="store_true", help="List providers")
    parser.add_argument("--add", nargs=2, metavar=("NAME", "URL"), help="Add a provider")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL, help="Check interval (s)")
    args = parser.parse_args()

    config = load_config()
    manager = ProviderManager(config)

    if args.list:
        cmd_list(manager)
        return 0

    if args.add:
        name, url = args.add
        key = input("API key: ").strip()
        config["providers"].append({"name": name, "url": url, "api_key": key, "priority": len(config["providers"])})
        save_config(config)
        log(f"Added provider: {name} ({url})")
        return 0

    if args.daemon:
        daemon_loop(manager)
        return 0

    if args.check:
        return cmd_check(manager)

    # Default: single check
    return cmd_check(manager)


if __name__ == "__main__":
    sys.exit(main())