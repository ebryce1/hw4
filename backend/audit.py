"""Append-only audit trail of every chat agent run (Problem 12), plus the loop/result limits that
keep one run from running away with time, tokens, or database rows.

output/audit_trail.json is never wiped: append_audit() always reads what's there, adds to it, and
writes the whole file back out with an atomic rename, so a crash mid-write can't corrupt or lose
earlier records, and restarting the backend never starts the file over.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic_ai import Agent, UsageLimits
from pydantic_ai.messages import RetryPromptPart, ToolCallPart, ToolReturnPart

from models import AgentDeps, AuditEntry, ToolCallRecord

ROOT = Path(__file__).resolve().parent
AUDIT_PATH = ROOT.parent / "output" / "audit_trail.json"  # hw4/output/, alongside harness.md
SUMMARY_CHARS = 300  # how much of a tool arg/result or the final reply gets kept in one record

# Loop limits for one chat turn. A normal turn is 1-3 tool calls (e.g. search_products, then
# get_product_details); this leaves headroom for a couple of validator retries without letting a
# confused run spiral into dozens of model requests on our dime.
MAX_AGENT_REQUESTS = 8
MAX_TOOL_CALLS = 8
MAX_RETRIES = 2  # per tool call / per output validation, passed to Agent(retries=...)

_write_lock = threading.Lock()  # serializes read-modify-write so two concurrent chats can't race


def _short(value) -> str:
    """Truncate anything to SUMMARY_CHARS for a compact, still-readable audit record."""
    if isinstance(value, str):
        text = value
    elif hasattr(value, "model_dump_json"):
        text = value.model_dump_json()
    else:
        text = json.dumps(value, default=str)
    return text if len(text) <= SUMMARY_CHARS else text[:SUMMARY_CHARS] + "..."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def append_audit(entry: AuditEntry) -> None:
    """Add one record to output/audit_trail.json without losing what's already there."""
    with _write_lock:
        rows: list = []
        if AUDIT_PATH.is_file() and AUDIT_PATH.read_text().strip():
            rows = json.loads(AUDIT_PATH.read_text())
        rows.append(entry.model_dump(mode="json"))
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = AUDIT_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rows, indent=2) + "\n")
        os.replace(tmp, AUDIT_PATH)  # atomic: readers never see a half-written file


async def run_chat_with_audit(agent: Agent[AgentDeps, object], prompt: str, deps: AgentDeps, inputs: dict):
    """Run the agent step by step (not a single agent.run() call) so every tool call and loop
    step can be recorded as it happens, then return the same AgentRunResult agent.run() would
    have given back. Writes run_start, one iteration record per loop step, and run_end.

    Raises whatever the agent run raises, after recording a run_end with stop_reason='error' —
    the caller (agent.py's run_chat) still decides how to respond to the shopper.
    """
    run_id = uuid4().hex[:12]
    append_audit(AuditEntry(timestamp=_now(), run_id=run_id, event="run_start", inputs=inputs))

    step = 0
    pending: AuditEntry | None = None
    pending_ids: list[str] = []  # tool_call_id for each record in pending.tool_calls, same order

    def flush() -> None:
        nonlocal pending
        if pending is not None:
            pending.timestamp = _now()
            append_audit(pending)
            pending = None

    try:
        limits = UsageLimits(request_limit=MAX_AGENT_REQUESTS, tool_calls_limit=MAX_TOOL_CALLS)
        async with agent.iter(prompt, deps=deps, usage_limits=limits) as run:
            async for node in run:
                if Agent.is_call_tools_node(node):
                    flush()
                    step += 1
                    resp = node.model_response
                    calls = [p for p in resp.parts if isinstance(p, ToolCallPart)]
                    pending_ids = [c.tool_call_id for c in calls]
                    pending = AuditEntry(
                        timestamp=_now(),
                        run_id=run_id,
                        event="iteration",
                        iteration=step,
                        model=resp.model_name,
                        tool_calls=[
                            ToolCallRecord(tool_name=c.tool_name, args=c.args_as_dict() or {})
                            for c in calls
                        ],
                        stop_reason=resp.finish_reason,
                    )
                elif Agent.is_model_request_node(node) and pending is not None:
                    # This request carries the previous step's tool results.
                    by_id: dict[str, tuple[str, str]] = {}
                    for part in node.request.parts:
                        if isinstance(part, ToolReturnPart):
                            by_id[part.tool_call_id] = ("ok", _short(part.content))
                        elif isinstance(part, RetryPromptPart) and part.tool_call_id:
                            by_id[part.tool_call_id] = ("retry", _short(part.content))
                    for rec, call_id in zip(pending.tool_calls, pending_ids):
                        if call_id in by_id:
                            rec.status, rec.result_summary = by_id[call_id]
                    flush()
            result = run.result
        if pending is not None:  # last step's tool call fed straight into the final answer
            for rec in pending.tool_calls:
                rec.status, rec.result_summary = "ok", "fed into final reply"
            flush()
        append_audit(
            AuditEntry(
                timestamp=_now(),
                run_id=run_id,
                event="run_end",
                stop_reason="completed",
                output_summary=_short(getattr(result.output, "reply", result.output)),
                tokens_in=result.usage.input_tokens,
                tokens_out=result.usage.output_tokens,
            )
        )
        return result
    except Exception as exc:
        flush()
        append_audit(
            AuditEntry(
                timestamp=_now(),
                run_id=run_id,
                event="run_end",
                stop_reason="error",
                error=_short(f"{type(exc).__name__}: {exc}"),
            )
        )
        raise
