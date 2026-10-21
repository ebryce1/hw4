"""Campus Customs chat agent: entry point and wiring.

The agent is Handsome Dan (prompts/prompt.md sets his voice and the safety rules). It can call
search_products and get_product_details (tools.py) to look up real prices and stock, and must
produce an AgentReply (models.py): the reply text plus the product_ids to show as cards.

Problem 8: who the agent is talking to, and what they're looking at, both travel through
AgentDeps and get turned into extra instructions for this run by shopper_context() below — code
deciding what the model is told, the same "facts from code" principle the tools already follow.

Problem 12: every run goes through audit.run_chat_with_audit instead of a plain agent.run() call,
so each tool call and the run's outcome land in output/audit_trail.json. MAX_RETRIES (audit.py)
caps how many times a tool call or output validation can be retried in one run.
"""
from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent, RunContext

from audit import MAX_RETRIES, run_chat_with_audit
from models import AgentDeps, AgentReply, ChatTurn
from tools import (
    add_favorite,
    build_model,
    check_stock,
    get_product_details,
    list_favorites,
    search_products,
)

ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "prompt.md"

_agent: Agent[AgentDeps, AgentReply] | None = None


def get_agent() -> Agent[AgentDeps, AgentReply]:
    """Build the agent once and reuse it for every request (the model client is reusable)."""
    global _agent
    if _agent is None:
        agent = Agent(
            build_model(),
            deps_type=AgentDeps,
            output_type=AgentReply,
            instructions=PROMPT_PATH.read_text(),
            tools=[search_products, get_product_details, check_stock, add_favorite, list_favorites],
            retries=MAX_RETRIES,
        )

        @agent.instructions
        def shopper_context(ctx: RunContext[AgentDeps]) -> str:
            """Dynamic instructions: computed fresh from AgentDeps on every run and appended to
            prompts/prompt.md's static text. This is "code in the agent's context" — identity
            and page context are facts the program already knows before the model starts, so
            they're injected here rather than left for the model to ask about or guess."""
            d = ctx.deps
            lines: list[str] = []

            if d.customer_name or d.customer_email:
                who = d.customer_name or "a signed-in shopper"
                contact = f" ({d.customer_email})" if d.customer_email else ""
                lines.append(
                    f"This shopper is signed in as {who}{contact}. Greet them by first name "
                    "once near the start of the conversation; you don't need a tool to know "
                    "this, it's already confirmed. They can use add_favorite and list_favorites."
                )
            else:
                lines.append(
                    "This shopper is browsing as a guest (not signed in). Don't imply you know "
                    "their name or email. add_favorite and list_favorites will both decline for "
                    "them — if they ask to save something, tell them they'll need an account."
                )

            if d.viewing_product_id and d.viewing_product_name:
                lines.append(
                    f'They are currently on this exact product\'s page: "{d.viewing_product_name}" '
                    f"(product_id: {d.viewing_product_id}). If they say \"this\", \"it\", or don't "
                    "name a product, assume they mean this one — call get_product_details or "
                    "check_stock with this product_id directly instead of asking which product "
                    "they mean or running a search."
                )

            return "\n".join(lines)

        _agent = agent
    return _agent


def _format_history(history: list[ChatTurn]) -> str:
    if not history:
        return ""
    lines = [f"{turn.role}: {turn.content}" for turn in history]
    return "Conversation so far:\n" + "\n".join(lines) + "\n\n"


async def run_chat(
    message: str,
    history: list[ChatTurn],
    customer_name: str | None = None,
    customer_email: str | None = None,
    user_id: int | None = None,
    viewing_product_id: str | None = None,
    viewing_product_name: str | None = None,
) -> tuple[str, list[str]]:
    """Run one chat turn. Returns (reply_text, product_ids) — the route turns ids into product cards."""
    deps = AgentDeps(
        customer_name=customer_name,
        customer_email=customer_email,
        user_id=user_id,
        viewing_product_id=viewing_product_id,
        viewing_product_name=viewing_product_name,
    )
    prompt = f"{_format_history(history)}Shopper says: {message}"
    # inputs logged to the audit trail: user_id only (never name/email — see models.AuditEntry),
    # the shopper's own message, and what page they were on.
    audit_inputs = {
        "user_id": user_id,
        "message": message,
        "viewing_product_id": viewing_product_id,
    }
    result = await run_chat_with_audit(get_agent(), prompt, deps, audit_inputs)
    output = result.output
    # Only ids the tools actually returned may be shown, even if the model listed others.
    allowed = set(deps.returned_product_ids)
    product_ids = [pid for pid in dict.fromkeys(output.product_ids) if pid in allowed]
    return output.reply, product_ids
