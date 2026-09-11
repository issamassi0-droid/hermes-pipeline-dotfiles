#!/usr/bin/env python3
"""
Protocol Engine — Cabinet-Office System v1.0
Implements the inter-agent communication protocol:
- Envelope wrapping (MISSION/FROM/TO/STAGE/URGENCY)
- 10 payload types
- 12-message budget enforcement
- 8-turn group room limit
- Escalation ladder
"""
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
PROTOCOL_LOG = LEDGER_DIR / "protocol-messages.jsonl"
BUDGET_FILE = LEDGER_DIR / "message-budget.json"

# ── Protocol constants ────────────────────────────────────────────
MAX_MESSAGES_PER_MISSION = 12
MAX_GROUP_ROOM_TURNS = 8

VALID_PAYLOAD_TYPES = {
    "handoff", "blocker", "revision_request", "clarification_request",
    "video_request", "hypothesis_update", "escalation", "registry_notice",
    "proposal", "dedup"
}

VALID_STAGES = {
    "triage", "research", "video", "strategy", "draft",
    "verify", "publish", "analyze", "monitor"
}

VALID_URGENCY = {"low", "normal", "high", "blocker"}


class MessageBudget:
    """Tracks message budget per mission."""

    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self.count = 0
        self.messages = []

    def can_send(self) -> bool:
        return self.count < MAX_MESSAGES_PER_MISSION

    def record(self, sender: str, recipient: str, payload_type: str) -> dict:
        """Record a message and return budget status."""
        self.count += 1
        entry = {
            "index": self.count,
            "sender": sender,
            "recipient": recipient,
            "payload_type": payload_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "remaining": MAX_MESSAGES_PER_MISSION - self.count
        }
        self.messages.append(entry)

        # Log to file
        LEDGER_DIR.mkdir(parents=True, exist_ok=True)
        with open(PROTOCOL_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_status(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "messages_sent": self.count,
            "messages_remaining": MAX_MESSAGES_PER_MISSION - self.count,
            "budget_exhausted": self.count >= MAX_MESSAGES_PER_MISSION,
            "can_send": self.can_send()
        }


class Envelope:
    """Wraps an inter-agent message in the protocol envelope."""

    def __init__(
        self,
        mission_id: str,
        sender: str,
        recipient: str,
        stage: str,
        urgency: str = "normal",
        payload_type: str = "handoff",
        payload: dict = None
    ):
        # Validate inputs
        if payload_type not in VALID_PAYLOAD_TYPES:
            raise ValueError(f"Invalid payload type: {payload_type}. Valid: {VALID_PAYLOAD_TYPES}")
        if urgency not in VALID_URGENCY:
            raise ValueError(f"Invalid urgency: {urgency}. Valid: {VALID_URGENCY}")
        if stage not in VALID_STAGES:
            raise ValueError(f"Invalid stage: {stage}. Valid: {VALID_STAGES}")

        self.mission_id = mission_id
        self.sender = sender
        self.recipient = recipient
        self.stage = stage
        self.urgency = urgency
        self.payload_type = payload_type
        self.payload = payload or {}

    def wrap(self) -> str:
        """Wrap payload in envelope format."""
        header = (
            f"[MISSION:{self.mission_id}]\n"
            f"[FROM:{self.sender}]\n"
            f"[TO:{self.recipient}]\n"
            f"[STAGE:{self.stage}]\n"
            f"[URGENCY:{self.urgency}]\n"
            "---PAYLOAD---\n"
        )

        # Add payload type to payload
        payload_with_type = {"type": self.payload_type, **self.payload}
        payload_str = json.dumps(payload_with_type, indent=2)

        footer = "\n---END---"

        return header + payload_str + footer

    @staticmethod
    def unwrap(envelope_str: str) -> dict:
        """Parse an envelope string back to components."""
        lines = envelope_str.strip().split("\n")

        # Extract header fields
        fields = {}
        payload_start = None
        payload_end = None

        for i, line in enumerate(lines):
            if line.startswith("[MISSION:"):
                fields["mission_id"] = line.split(":")[1].rstrip("]")
            elif line.startswith("[FROM:"):
                fields["sender"] = line.split(":")[1].rstrip("]")
            elif line.startswith("[TO:"):
                fields["recipient"] = line.split(":")[1].rstrip("]")
            elif line.startswith("[STAGE:"):
                fields["stage"] = line.split(":")[1].rstrip("]")
            elif line.startswith("[URGENCY:"):
                fields["urgency"] = line.split(":")[1].rstrip("]")
            elif line == "---PAYLOAD---":
                payload_start = i + 1
            elif line == "---END---":
                payload_end = i

        if payload_start is None or payload_end is None:
            raise ValueError("Invalid envelope: missing payload markers")

        payload_str = "\n".join(lines[payload_start:payload_end])
        try:
            fields["payload"] = json.loads(payload_str)
        except:
            fields["payload"] = {"raw": payload_str}

        return fields

    def __str__(self):
        return self.wrap()


class ProtocolEngine:
    """Main engine that enforces protocol rules."""

    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self.budget = MessageBudget(mission_id)
        self.group_room_turns = 0

    def send(
        self,
        sender: str,
        recipient: str,
        stage: str,
        payload_type: str,
        payload: dict = None,
        urgency: str = "normal"
    ) -> dict:
        """
        Send a message through the protocol.
        Enforces: budget, envelope format, escalation rules.

        Returns: {"status": "...", "envelope": "...", "budget": {...}}
        """
        # Check budget
        if not self.budget.can_send():
            return {
                "status": "budget_exhausted",
                "error": f"Message budget ({MAX_MESSAGES_PER_MISSION}) exceeded for {self.mission_id}",
                "action": "route_through_architect",
                "budget": self.budget.get_status()
            }

        # Check escalation rules (only Architect escalates to human)
        if recipient == "human" and sender != "architect":
            return {
                "status": "escalation_violation",
                "error": f"Agent '{sender}' cannot escalate directly to human",
                "action": "route_through_architect",
                "escalation_ladder": f"{sender} → architect → human"
            }

        # Create envelope
        try:
            envelope = Envelope(
                mission_id=self.mission_id,
                sender=sender,
                recipient=recipient,
                stage=stage,
                urgency=urgency,
                payload_type=payload_type,
                payload=payload or {}
            )
        except ValueError as e:
            return {"status": "invalid_envelope", "error": str(e)}

        # Record in budget
        budget_entry = self.budget.record(sender, recipient, payload_type)

        return {
            "status": "sent",
            "envelope": envelope.wrap(),
            "budget": self.budget.get_status(),
            "message_index": budget_entry["index"]
        }

    def group_room_turn(self) -> dict:
        """Track a group room turn."""
        self.group_room_turns += 1
        if self.group_room_turns >= MAX_GROUP_ROOM_TURNS:
            return {
                "status": "group_room_limit",
                "turns": self.group_room_turns,
                "action": "pause_and_request_human"
            }
        return {
            "status": "continue",
            "turns": self.group_room_turns,
            "remaining": MAX_GROUP_ROOM_TURNS - self.group_room_turns
        }

    def get_status(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "message_budget": self.budget.get_status(),
            "group_room_turns": self.group_room_turns,
            "group_room_remaining": MAX_GROUP_ROOM_TURNS - self.group_room_turns
        }


# ── CLI interface ────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python protocol.py <command> [args]")
        print("Commands: send, unwrap, status, test")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "send":
        if len(sys.argv) < 7:
            print("Usage: python protocol.py send <mission> <sender> <recipient> <stage> <payload_type> [payload_json]")
            sys.exit(1)
        engine = ProtocolEngine(sys.argv[2])
        payload = json.loads(sys.argv[7]) if len(sys.argv) > 7 else {}
        result = engine.send(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], payload)
        print(json.dumps(result, indent=2))

    elif cmd == "unwrap":
        if len(sys.argv) < 3:
            print("Usage: python protocol.py unwrap '<envelope_string>'")
            sys.exit(1)
        envelope_str = sys.argv[2]
        parsed = Envelope.unwrap(envelope_str)
        print(json.dumps(parsed, indent=2))

    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: python protocol.py status <mission>")
            sys.exit(1)
        engine = ProtocolEngine(sys.argv[2])
        print(json.dumps(engine.get_status(), indent=2))

    elif cmd == "test":
        print("=== Protocol Engine Test ===\n")
        engine = ProtocolEngine("test-mission-001")

        # Test 1: Valid message
        print("[Test 1] Valid handoff message")
        result = engine.send(
            sender="omni-researcher",
            recipient="strategist",
            stage="research",
            payload_type="handoff",
            payload={
                "artifact_path": "/ledger/test-mission-001/research.json",
                "artifact_summary": "14 sources, 3 Tier-1",
                "confidence": 0.82
            }
        )
        print(f"  Status: {result['status']}")
        print(f"  Budget remaining: {result['budget']['messages_remaining']}")
        print()

        # Test 2: Envelope format
        print("[Test 2] Envelope format")
        if result['status'] == 'sent':
            print(result['envelope'][:200] + "...")
        print()

        # Test 3: Budget enforcement
        print("[Test 3] Budget enforcement (sending 12 messages)")
        engine3 = ProtocolEngine("test-budget")
        for i in range(12):
            r = engine3.send("agent1", "agent2", "research", "handoff", {"i": i})
            if r['status'] != 'sent':
                print(f"  Message {i+1}: {r['status']}")
                break
        else:
            print(f"  All 12 messages sent")
        # 13th should fail
        r = engine3.send("agent1", "agent2", "research", "handoff", {"i": 12})
        print(f"  Message 13: {r['status']}")
        print()

        # Test 4: Escalation violation
        print("[Test 4] Escalation violation (writer → human)")
        engine4 = ProtocolEngine("test-escalation")
        r = engine4.send("draft-writer", "human", "draft", "escalation", {"reason": "test"})
        print(f"  Status: {r['status']}")
        print(f"  Action: {r['action']}")
        print()

        # Test 5: Group room limit
        print("[Test 5] Group room turn limit")
        engine5 = ProtocolEngine("test-group")
        for i in range(8):
            r = engine5.group_room_turn()
            if r['status'] != 'continue':
                print(f"  Turn {i+1}: {r['status']}")
                break
        else:
            print(f"  All 8 turns completed")
        r = engine5.group_room_turn()
        print(f"  Turn 9: {r['status']}")
        print()

        # Test 6: Unwrap envelope
        print("[Test 6] Unwrap envelope")
        engine6 = ProtocolEngine("test-unwrap")
        sent = engine6.send(
            sender="editor-qa",
            recipient="draft-writer",
            stage="verify",
            payload_type="revision_request",
            payload={"cycle": 1, "unsupported_claims": ["c12"]}
        )
        if sent['status'] == 'sent':
            parsed = Envelope.unwrap(sent['envelope'])
            print(f"  Mission: {parsed.get('mission_id')}")
            print(f"  From: {parsed.get('sender')}")
            print(f"  To: {parsed.get('recipient')}")
            print(f"  Stage: {parsed.get('stage')}")
            print(f"  Payload type: {parsed.get('payload', {}).get('type')}")
        print()

        print("=== All tests complete ===")

    else:
        print(f"Unknown command: {cmd}")
