# Mission Control Setup Skill

Bootstrap an AI agent squad from Mission Control with a single setup link.

---

## Metadata

| Field | Value |
|-------|-------|
| name | mission-control-setup |
| description | Bootstrap an AI agent squad from Mission Control |
| version | 1.0.0 |
| author | Mission Control |

---

## Trigger

Activate this skill when the user provides a Mission Control setup URL. Common patterns:

- "Setup my squad using this link: https://missioncontrol.ai/setup/..."
- "Bootstrap agents from https://missioncontrol.ai/api/setup/..."
- "Here's my Mission Control setup link: ..."
- User pastes a URL containing `/setup/` or `/api/setup/`

The setup URL format is:
```
https://missioncontrol.ai/api/setup/{squad_id}
```

The setup token should be sent via the `x-setup-token` header (not as a query parameter).

---

## Environment

No environment variables required. All configuration is fetched from the setup URL.

### Paths Used

| Path | Purpose |
|------|---------|
| `~/.openclaw/missions/{squad_id}/` | Squad-specific state and markers |
| `~/.openclaw/sessions/{agent_name}/` | Agent session directories |
| `~/.openclaw/skills/mission-control/` | Runtime skill installation |
| `~/.openclaw/cron/jobs.json` | Heartbeat cron job definitions |

---

## Setup Process

Follow these steps in order. Each step is idempotent - safe to re-run.

### Step 0: Check for Existing Setup

Before starting, check if this squad was already set up.

```bash
SQUAD_ID="<extracted_from_url>"
MARKER_FILE="$HOME/.openclaw/missions/$SQUAD_ID/setup-completed"

if [ -f "$MARKER_FILE" ]; then
 echo "Setup already completed for squad $SQUAD_ID"
 echo "Completed at: $(cat $MARKER_FILE)"
 # Ask user if they want to re-run
fi
```

**If marker exists**: Inform the user that setup was previously completed. Show the completion timestamp. Ask if they want to:
1. Skip setup entirely
2. Re-run setup (will update SOUL.md files and refresh configuration)

**If marker does not exist**: Proceed with setup.

---

### Step 1: Fetch Configuration

Parse the setup URL and fetch the squad configuration.

#### Extract URL Parameters

```bash
SETUP_URL="<full_url_from_user>"

# Extract squad_id from URL path
# URL format: https://missioncontrol.ai/api/setup/{squad_id}
# Token may be in URL query param (legacy) or provided separately
SQUAD_ID=$(echo "$SETUP_URL" | sed -n 's|.*/api/setup/\([^?]*\).*|\1|p')
TOKEN=$(echo "$SETUP_URL" | sed -n 's|.*token=\([^&]*\).*|\1|p')
```

#### Fetch Configuration

Send the token via the `x-setup-token` header (preferred over query parameter):

```bash
# Build the base URL (without query params)
BASE_URL="https://missioncontrol.ai/api/setup/$SQUAD_ID"

CONFIG_RESPONSE=$(curl -s -w "\n%{http_code}" \
 -H "x-setup-token: $TOKEN" \
 "$BASE_URL")
HTTP_CODE=$(echo "$CONFIG_RESPONSE" | tail -n1)
CONFIG_BODY=$(echo "$CONFIG_RESPONSE" | sed '$d')
```

#### Handle Errors

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Proceed to Step 2 |
| 401 | Invalid token | Tell user the token is invalid. They should generate a new setup link from Mission Control. |
| 403 | Token expired | Tell user the setup link has expired. They should generate a new one (links expire after 24 hours). |
| 404 | Squad not found | Tell user the squad ID is invalid or the squad was deleted. |
| 5xx | Server error | Tell user Mission Control is temporarily unavailable. Try again in a few minutes. |
| Network error | Connection failed | Check internet connection. Verify the URL is correct. |

**On success**, parse the JSON response:

```bash
# Expected response structure:
# {
# "squad": { "id": "uuid", "name": "My Squad" },
# "agents": [
# { "name": "Lead", "soul_md": "...", "role": "coordinator" },
# { "name": "Writer", "soul_md": "...", "role": "specialist" }
# ],
# "api_key": "mc_prefix_secret",
# "heartbeat_interval": 300,
# "heartbeat_stagger": 30,
# "dashboard_url": "https://missioncontrol.ai/dashboard/abc"
# }
```

Store the config for use in subsequent steps:
```bash
mkdir -p "$HOME/.openclaw/missions/$SQUAD_ID"
echo "$CONFIG_BODY" > "$HOME/.openclaw/missions/$SQUAD_ID/config.json"
```

---

### Step 2: Create Agent Sessions

Create a session for each agent defined in the configuration.

#### Using sessions_spawn Tool

For each agent in `config.agents`:

```
Use the sessions_spawn tool with:
- name: <agent.name>
- working_directory: $HOME/.openclaw/sessions/<agent.name>
```

#### Idempotency

- Check if session already exists before creating
- If session exists with the same name, skip creation (log that it was skipped)
- New sessions are created in stopped state

#### Example Output

```
Creating agent sessions...
 [+] Lead - created
 [=] Writer - already exists, skipped
 [+] Social - created

3 agents processed (2 created, 1 skipped)
```

---

### Step 3: Write SOUL.md Files

Write the SOUL.md file for each agent from the configuration.

#### Write Files

For each agent in `config.agents`:

```bash
AGENT_DIR="$HOME/.openclaw/sessions/${AGENT_NAME}"
mkdir -p "$AGENT_DIR"
echo "$AGENT_SOUL_MD" > "$AGENT_DIR/SOUL.md"
```

#### Important Notes

- **Always overwrite** existing SOUL.md files - this is expected behavior for configuration updates
- The `soul_md` content from the API is already complete and ready to write
- Create the agent directory if it doesn't exist

#### Example Output

```
Writing SOUL.md files...
 [+] Lead - wrote SOUL.md (1.2 KB)
 [+] Writer - wrote SOUL.md (0.9 KB)
 [+] Social - wrote SOUL.md (1.1 KB)

3 SOUL.md files written
```

---

### Step 4: Install Runtime Skill

Install the Mission Control runtime skill that agents will use for heartbeats and task management.

#### Create Skill Directory

```bash
SKILL_DIR="$HOME/.openclaw/skills/mission-control"
mkdir -p "$SKILL_DIR"
```

#### Write Runtime Skill

Write the runtime SKILL.md file that handles ongoing operations:

```bash
cat > "$SKILL_DIR/SKILL.md" << 'EOF'
# Mission Control Runtime Skill

Provides heartbeat and task management for Mission Control agents.

## Metadata

| Field | Value |
|-------|-------|
| name | mission-control |
| version | 1.0.0 |

## Commands

### heartbeat

Send a heartbeat to Mission Control. Run on a schedule via cron.

```bash
API_KEY="$MC_API_KEY"
AGENT_NAME="$MC_AGENT_NAME"

curl -X POST "https://missioncontrol.ai/api/agents/heartbeat" \
 -H "Authorization: Bearer $API_KEY" \
 -H "Content-Type: application/json" \
 -d "{\"agent\": \"$AGENT_NAME\", \"status\": \"active\"}"
```

### fetch-tasks

Check for new tasks assigned to this agent.

```bash
curl -s "https://missioncontrol.ai/api/agents/tasks" \
 -H "Authorization: Bearer $MC_API_KEY" \
 -H "X-Agent-Name: $MC_AGENT_NAME"
```

### complete-task

Mark a task as completed.

```bash
curl -X POST "https://missioncontrol.ai/api/tasks/$TASK_ID/complete" \
 -H "Authorization: Bearer $MC_API_KEY" \
 -H "Content-Type: application/json" \
 -d "{\"agent\": \"$MC_AGENT_NAME\", \"result\": \"$RESULT\"}"
```
EOF
```

#### Idempotency

- Overwrite existing skill files - this ensures agents get the latest version

---

### Step 5: Configure Heartbeat Crons

Set up staggered heartbeat cron jobs for each agent.

#### Calculate Stagger Offsets

Using `heartbeat_interval` and `heartbeat_stagger` from config:

```bash
# Example with 300s interval and 30s stagger for 3 agents:
# Lead: every 300s, offset 0s -> 0, 300, 600, ...
# Writer: every 300s, offset 30s -> 30, 330, 630, ...
# Social: every 300s, offset 60s -> 60, 360, 660, ...
```

#### Update jobs.json

```bash
CRON_FILE="$HOME/.openclaw/cron/jobs.json"
mkdir -p "$(dirname "$CRON_FILE")"

# Read existing jobs or create empty array
if [ -f "$CRON_FILE" ]; then
 EXISTING_JOBS=$(cat "$CRON_FILE")
else
 EXISTING_JOBS="[]"
fi
```

#### Job Format

Each cron job should have this structure:

```json
{
 "id": "{squad_id}-{agent_name}-heartbeat",
 "type": "heartbeat",
 "agent": "{agent_name}",
 "squad_id": "{squad_id}",
 "interval_seconds": 300,
 "offset_seconds": 0,
 "command": "mission-control heartbeat",
 "enabled": true
}
```

#### Upsert Logic

- Use composite ID: `{squad_id}-{agent_name}-heartbeat`
- If job with same ID exists, update it
- If job doesn't exist, add it
- Preserve other jobs in the file

#### Example Output

```
Configuring heartbeat crons...
 [+] Lead - every 5m, offset 0s
 [+] Writer - every 5m, offset 30s
 [+] Social - every 5m, offset 60s

Cron jobs written to ~/.openclaw/cron/jobs.json
```

---

### Step 6: Verify Setup

Test the API connection for each agent.

#### Test Each Agent

```bash
for AGENT_NAME in "${AGENTS[@]}"; do
 RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
 -X POST "https://missioncontrol.ai/api/agents/heartbeat" \
 -H "Authorization: Bearer $API_KEY" \
 -H "Content-Type: application/json" \
 -d "{\"agent\": \"$AGENT_NAME\", \"status\": \"setup_test\"}")

 if [ "$RESPONSE" = "200" ]; then
 echo "[OK] $AGENT_NAME - connected"
 else
 echo "[FAIL] $AGENT_NAME - HTTP $RESPONSE"
 fi
done
```

#### Handle Verification Failures

If any agent fails verification:

1. Report which agents failed and the error
2. Common causes:
 - Network connectivity issues
 - API key was revoked
 - Mission Control service is down
3. Setup is still considered complete - the issue is likely temporary
4. Suggest the user check the Mission Control dashboard

---

### Step 7: Mark Setup Complete

Write the completion marker file.

```bash
MARKER_FILE="$HOME/.openclaw/missions/$SQUAD_ID/setup-completed"
mkdir -p "$(dirname "$MARKER_FILE")"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$MARKER_FILE"
```

---

## Completion Report

After successful setup, display a summary:

```
========================================
Mission Control Setup Complete
========================================

Squad: My Content Squad
Squad ID: abc123-def456-...

Agents Created:
 - Lead (coordinator)
 - Writer (specialist)
 - Social (specialist)

Heartbeat Schedule:
 - Lead: every 5 minutes
 - Writer: every 5 minutes (offset +30s)
 - Social: every 5 minutes (offset +60s)

Files Created:
 - ~/.openclaw/sessions/Lead/SOUL.md
 - ~/.openclaw/sessions/Writer/SOUL.md
 - ~/.openclaw/sessions/Social/SOUL.md
 - ~/.openclaw/skills/mission-control/SKILL.md
 - ~/.openclaw/cron/jobs.json

Dashboard: https://missioncontrol.ai/dashboard/abc123

Next Steps:
 1. Start your agents using your agent management tool
 2. Check the dashboard to see agents come online
 3. Create your first task from the dashboard

========================================
```

---

## Error Scenarios

### Invalid Setup URL

```
Error: Invalid setup URL format

Expected format:
 https://missioncontrol.ai/api/setup/{squad_id}

The setup token should be provided via the x-setup-token header.
Legacy URLs with ?token= query parameter are still supported but deprecated.

Received:
 {user_provided_url}

Please copy the complete setup URL from Mission Control.
```

### Expired Token

```
Error: Setup link has expired

Setup links are valid for 24 hours. Please:
 1. Go to Mission Control dashboard
 2. Navigate to your squad settings
 3. Generate a new setup link
 4. Run setup again with the new link
```

### Network Error

```
Error: Could not connect to Mission Control

Please check:
 - Internet connection is working
 - Mission Control (missioncontrol.ai) is accessible
 - No firewall blocking outbound HTTPS

You can retry setup once the connection is restored.
```

### Partial Setup Failure

```
Warning: Setup completed with issues

Successful:
 - Configuration fetched
 - Agent sessions created
 - SOUL.md files written

Failed:
 - Heartbeat verification for "Social" (HTTP 500)

The setup is complete. The verification failure is likely temporary.
Check the Mission Control dashboard in a few minutes.
```

---

## Re-running Setup

When setup has already been completed and the user wants to re-run:

```
Previous setup detected for squad "My Content Squad"
Completed: 2024-01-15T10:30:00Z

What would you like to do?

1. Update configuration
 - Fetches latest config from Mission Control
 - Updates SOUL.md files
 - Updates cron jobs
 - Does NOT recreate existing sessions

2. Full reinstall
 - Removes existing sessions
 - Performs complete fresh setup
 - Warning: Any local agent state will be lost

3. Skip
 - Keep existing setup
 - No changes made
```

For option 1 (Update), run Steps 1, 3, 4, 5, 6, 7 (skip Step 2 session creation).

For option 2 (Full reinstall), remove existing state then run all steps:
```bash
rm -rf "$HOME/.openclaw/missions/$SQUAD_ID"
rm -rf "$HOME/.openclaw/sessions/Lead"
rm -rf "$HOME/.openclaw/sessions/Writer"
# ... for each agent
```

---

## Troubleshooting

### Sessions not starting

Check that the sessions were created:
```bash
ls -la ~/.openclaw/sessions/
```

Verify SOUL.md files exist and are non-empty:
```bash
cat ~/.openclaw/sessions/Lead/SOUL.md
```

### Heartbeats not sending

Check cron configuration:
```bash
cat ~/.openclaw/cron/jobs.json | jq .
```

Verify the API key is set correctly in the environment.

### API key issues

The API key from setup is stored in the config:
```bash
cat ~/.openclaw/missions/$SQUAD_ID/config.json | jq -r '.api_key'
```

Test the key manually:
```bash
curl -s "https://missioncontrol.ai/api/agents/status" \
 -H "Authorization: Bearer $API_KEY"
```
