# Cabinet-Office Multi-Agent System v1.6.0

> Multi-agent AI system — three-layer architecture

---

## Installation

```bash
# Clone the repository
git clone https://github.com/issamassi0-droid/hermes-pipeline-dotfiles.git
cd hermes-pipeline-dotfiles

# Run setup (pull + merge + verify)
bash setup.sh --import
```

---

## Usage

### Run a full mission

```bash
# Tier 2 — research + strategy + writing + verification + publishing
python3 system/cabinet-office.py run "Research AI multi-agent trends" --tier tier_2

# Tier 3 — full analysis with video
python3 system/cabinet-office.py run "Analyze user experiences with herdr" --tier tier_3

# Tier 1 — fast research
python3 system/cabinet-office.py run "What is ling-3.0-flash?" --tier tier_1
```

### System commands

```bash
# System status
python3 system/cabinet-office.py status

# Full health check
python3 system/cabinet-office.py health

# Quality assessment
python3 system/cabinet-office.py quality

# Deduplicate findings
python3 system/cabinet-office.py dedup findings.json

# Budget status
python3 system/cabinet-office.py budget

# Architect heartbeat
python3 system/cabinet-office.py heartbeat --check

# Validate output file
python3 system/cabinet-office.py validate output.json --agent writer --stage draft

# Check escalation trigger
python3 system/cabinet-office.py escalation high_factual_error

# Track human override
python3 system/cabinet-office.py override --mission m001 --reason "rejected draft"
```

---

## Tiers

| Tier | Use Case | Estimated Time |
|---|---|---|
| Tier 0 | Immediate decision (Architect only) | ~11 seconds |
| Tier 1 | Fast research and publish | ~44 seconds |
| Tier 2 | Research + strategy + verification | ~2 min 40 sec |
| Tier 3 | Full analysis with video and feedback | ~5 min 20 sec |

---

## Architecture

```
system/
├── registry.json                    # 11-agent registry
├── protocol.md                      # Communication protocol
├── routing.yaml                     # Routing rules
├── quality-charter.md               # Quality charter
├── ledger-schema.json               # Task ledger schema
├── evolution.md                     # Evolution loop
├── constitutional.md                # 7 constitutional principles
├── quality-metrics.md               # Quality metrics
├── escalation-criteria.md           # Escalation triggers
├── architect-failover.md            # Architect failover
├── system-health.md                 # Health dashboard
├── model-gateway.md + .sh           # Model gateway
├── model-registry.json              # Model registry
├── cabinet-office.py                # Unified CLI (12 commands)
├── bootstrap.sh                     # Boot/verify
└── scripts/
    ├── protocol-engine.py           # Protocol engine
    ├── context-budget.py            # Context budget calculator
    ├── architect-heartbeat.py       # Architect heartbeat
    ├── output-validator.py          # Output validator
    ├── dedup.py + dedup-v2.py       # Deduplication
    ├── quality-assessment-v2.py     # Quality assessment
    └── escalation-system-health.py  # Escalation + health
```

---

## The Eleven Agents

| Agent | Role |
|---|---|
| @architect | Sole orchestrator |
| @omni-researcher | Comprehensive research |
| @deep-dive | YouTube research |
| @strategist | Convert research to plan |
| @draft-writer | Write first draft |
| @editor-qa | Independent verification |
| @publisher | Publishing |
| @analytics | Performance measurement |
| @bot-maker | Create new agents |
| @omarchy | System management |
| @scout | Source monitoring |

---

## Metrics

| Metric | Value | Target |
|---|---|---|
| factual_error_rate | 0.0% | < 5% |
| source_verification_rate | 100% | > 90% |
| human_override_rate | 2 | < 20 |

> ⚠️ Current metrics are calculated on synthetic data — they need independent measurement.

---

## License

MIT — open source, no fees.
