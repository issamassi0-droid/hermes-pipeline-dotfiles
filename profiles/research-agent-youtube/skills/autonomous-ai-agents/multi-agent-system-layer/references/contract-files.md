# Contract Files — required contents

Minimal shape of each file in `~/.hermes/system/`. Keep them short; a contract nobody reads
is worse than none.

## registry.json

Single source of truth for the agent roster.

- `version`, `created`, `generated_by`, `install_root`, `system_root`
- `agents[]`: `name`, `handle`, `role`, `ministry`, `entrypoint` (bool), `tiers_served`,
 `upstream[]`, `downstream[]`, `produces[]`, `consumes[]`, `owns_files[]`, `can_dm[]`
- `pipeline`: one object per tier listing ordered stages and the agents serving them
- `invariants[]`: flat sentences. Each must name one agent as the sole authority for an act
 (who may open a mission, who may approve before an external write, who may escalate to a
 human). Invariants are what stop two agents both believing they own a step.

`can_dm` is the anti-fan-out control: an agent may only message agents on its own list, so
"message everyone just in case" is structurally impossible.

## protocol.md

- The envelope, fixed order, on its own lines before any payload:
 `[MISSION:…] [FROM:…] [TO:…] [STAGE:…] [URGENCY:…]` then `---PAYLOAD---` … `---END---`
- A table of payload types with sender and recipient for each (`handoff`, `blocker`,
 `revision_request`, `clarification_request`, `escalation`, feedback notice, registry notice)
- Reply semantics: the message tool is fire-and-forget. Say this plainly, because the natural
 assumption is a synchronous call and agents will otherwise wait on a reply that never comes.
- A message budget per mission (single digit to low double digit), after which communication
 routes through the orchestrator. Prevents the classic multi-agent failure: talking more
 than working.
- An escalation ladder with exactly one agent permitted to reach the human.

## ledger-schema.json

- `layout`: root path per mission + one filename per stage, each annotated with which agent
 writes it
- `ticket_schema`: required fields including mission id pattern, domain, stakes, complexity,
 output type, latency, budget hint, tier, temporal bounds, confidence threshold, and an
 `assumption` field so a non-asked clarifying question is recorded rather than lost
- `stage_entry_schema`: stage, agent, started/completed timestamps, status enum, confidence,
 tokens used, artifact path
- `coverage_schema`: the blind-spot matrix, tier-change events, totals, and a quality verdict
- `retention`: how many ledgers are kept and where older ones are archived

The `assumption` field is the one that keeps a system moving without nagging the user.

## routing.yaml

- `tiers`: for each tier — when to use it, pipeline stages, agents, token budget,
 verification floor, temporal bound, max skills per agent
- `escalate` / `deescalate`: the explicit signal that moves a request between tiers.
 De-escalation matters as much as escalation; without it every request ratchets upward.
- `stakes_floors`: for each stakes level — required verification, whether QA is mandatory,
 whether a human checkpoint exists. Make the floor a function of stakes, not of tier, or
 high-stakes requests get processed at low rigor.
- `latent_need_checks`: a short, bounded list (two or three) with an action per check. An
 unbounded "think about what they really want" step is where pipelines stall.
- `budget`: which stage dominates spend, what gets reserved first, and the hard-stop
 percentage at which the pipeline halts and reports instead of degrading the output.
- `compression`: the exact field set passed between consecutive stages. This is what keeps a
 long pipeline from re-sending raw material forward.

## quality-charter.md

Numbered articles so amendments can cite them. At minimum cover:

1. evidence labels, and that unlabeled claims may not leave an agent
2. the quality floor no tier may trade away for budget
3. independent verification (different model family) at high stakes
4. blind-spot coverage required at mission close, with uncovered spots explained
5. a minimum turnaround so verification cannot be rubber-stamped under deadline
6. rejection as a first-class output, with precision/recall as the verifier's metric
7. a convergence ceiling after which the failure is reclassified as a brief/evidence defect
8. a periodic review obligation with named metrics
9. who may amend the charter, and that the constitutional layer is out of scope

## evolution.md

- the loop: run → collect from ledgers → analyze → amend
- the analysis artifact and its fields (tier accuracy, verifier precision/recall, escalation
 accuracy, coverage completeness, token economy, proposed amendments)
- three risk classes with distinct approval paths: auto-apply after a cooling-off window,
 co-sign, and explicit user approval
- amendment rules for the per-agent SOULs, naming the single agent permitted to author them
- the rollback entry format and the command that restores a file to its before-hash
- an explicit "what does NOT evolve" list

## bootstrap.sh

Commands: `--status` (default), `--install`, `--restore`, `--rollback <id>`.

- `--status` verifies contracts exist, creates its directories, checks the CLI, counts
 profiles, and prints an agent table — one command the user can run to see the system.
- `--restore` must restore **both** the system layer and every SOUL, otherwise agents come
 back unwired.
- Keep `jq` optional with a hardcoded fallback table so status works on a bare machine.
