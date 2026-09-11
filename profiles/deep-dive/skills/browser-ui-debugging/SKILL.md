---
name: browser-ui-debugging
description: "Debug browser UI glitches: scrolling, layout, extensions."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [debugging, browser, chromium, ui, selenium]
---

# Browser UI Debugging

When you encounter UI glitches in a browser (scrolling issues, layout breaks, missing controls), follow this systematic approach.

## 1. Isolate the Environment

**Use a fresh browser profile** to rule out extensions, settings, or profile corruption.

```bash
# Chromium/Chrome with temporary user-data-dir
chromium --user-data-dir=$(mktemp -d) --no-first-run https://www.youtube.com

# For automated testing, launch via Selenium with temporary profile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
opts = Options()
opts.add_argument('--user-data-dir=' + tempfile.mkdtemp())
driver = webdriver.Chrome(options=opts)
```

## 2. Handle Remote Debugging Popups

Chrome 144+ shows "Allow remote debugging?" popup for each new CDP connection, blocking automation.

### Workarounds

- **Use `--remote-debugging-port=0`** (random port) to reduce conflicts (not a full fix).
- **Use Selenium/WebDriver** instead of raw CDP; Selenium manages its own session and avoids the popup when using a fresh profile.
- **Auto-click Allow** with tools like `yes-dev` or `computer-use-mcp`.
- **Use a dedicated profile** launched once, then connect repeatedly (may still trigger popups on reconnect).
- **For persistent automation**, consider a Chrome MV3 extension + native-messaging host (no popup).

## 3. Test Scrolling and Layout

Use JavaScript to query scroll positions, offsets, and layout.

```js
// Scroll height
window.document.body.scrollHeight
// Current scroll Y
window.scrollY
// Viewport height
window.innerHeight
// Element bounding rect
element.getBoundingClientRect()
```

Run via browser tool's `js()` or Selenium's `execute_script`.

## 4. Disable Extensions

If the issue disappears in a clean profile, re-enable extensions one by one to identify the culprit.

## 5. Check Chrome Flags

Visit `chrome://flags` and reset any experimental flags that might affect UI (e.g., smooth scrolling, overlay scrollbars).

## 6. Build a Tight Feedback Loop

Create a deterministic command that reproduces the UI glitch:

- A script that scrolls and checks for unexpected layout shifts.
- A screenshot comparison before/after an action.
- A console error check.

Run the loop repeatedly to verify fixes.

## 7. References

- Chrome remote debugging permissions: https://github.com/ChromeDevTools/chrome-devtools-mcp/issues/1794
- Selenium with temporary profile: https://www.selenium.dev/documentation/webdriver/browsers/chrome/
- yes-dev (auto-click Allow): https://github.com/dev-newb/yes-dev

---