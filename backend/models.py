"""Pydantic models for the Campus Customs chat agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    """Stock for one size. `sold_out` is computed by code (quantity == 0), not left for the
    model to infer, so a sold-out size can never be reported as available by mistake."""

    size: str
    quantity: int
    sold_out: bool


class ProductCard(BaseModel):
    """A product match the agent sends to the page. This is the chat <-> site contract for
    Problem 7: the front end renders one of these exactly like a catalogue card — image, name,
    price, a short description, and whether it's in stock — whether it came from the product
    grid or from something a shopper asked the chatbot."""

    product_id: str
    name: str
    price: float
    image_url: str
    in_stock: bool
    short_description: str = Field(description="One short sentence, code-truncated from the full description.")


class ProductDetails(BaseModel):
    """Everything about one product: what get_product_details returns."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    sizes: list[SizeStock]
    in_stock: bool = Field(description="True if any size has quantity > 0.")


class StockLookup(BaseModel):
    """What check_stock returns: full per-size stock, plus a plain-language `note` the code
    writes (not the model) so the exact sold-out wording and the exact count are never left to
    the model to phrase or recall."""

    product_id: str
    name: str
    price: float
    sizes: list[SizeStock]
    in_stock: bool = Field(description="True if any size has quantity > 0.")
    requested_size: str | None = Field(
        default=None, description="The size asked about, if any (canonical code if it matched, e.g. 'XL')."
    )
    note: str = Field(description="Code-written summary, e.g. 'Size XL is sold out.' Say this, don't rephrase the number.")


class ChatTurn(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class PageContext(BaseModel):
    """What the shopper is looking at right now. The front end sends this with every message so
    "do you have this in pink?" can be resolved without the shopper having to name the product."""

    path: str = Field(description="Current route, e.g. '/products/basic-hoodie-big-yale'.")
    product_id: str | None = Field(
        default=None, description="Set when `path` is a single product's own page."
    )


class ChatRequest(BaseModel):
    """One message sent from the chat widget."""

    message: str = Field(min_length=1, max_length=2000)
    user_id: int | None = Field(default=None, description="Signed-in shopper, if any.")
    history: list[ChatTurn] = Field(
        default_factory=list, description="Prior turns this session, oldest first."
    )
    page_context: PageContext | None = Field(default=None)


class AgentReply(BaseModel):
    """Structured output the agent itself must produce."""

    reply: str = Field(description="Handsome Dan's reply to the shopper, in his voice.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id values (from search_products / get_product_details / check_stock results "
        "only) to show as cards on the page. For a category or style search, include every relevant match "
        "the tool returned, not just one — the site renders this whole list live. Empty if nothing matches.",
    )


class ChatResponse(BaseModel):
    """What the API sends back to the front end."""

    reply: str
    products: list[ProductCard]


class ChatHistoryEntry(BaseModel):
    """One saved turn, returned by GET /api/chat/history/{user_id} to reload a returning
    shopper's conversation. `products` is resolved fresh from the catalogue at load time (only
    the product_ids are actually stored), so reloaded cards always show today's price and stock,
    never a stale snapshot."""

    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)


class FavoriteRequest(BaseModel):
    """Body for POST /api/favorites."""

    user_id: int
    product_id: str


class ToolCallRecord(BaseModel):
    """One tool call made by the agent during a single chat turn (Problem 12). Part of an
    AuditEntry's `tool_calls` list — never written to the audit file by itself."""

    tool_name: str
    args: dict = Field(default_factory=dict, description="Arguments as the model sent them.")
    result_summary: str | None = Field(
        default=None, description="Short, truncated version of what the tool returned."
    )
    status: Literal["ok", "retry", "pending"] = Field(
        default="pending",
        description="'retry' if the tool call failed validation and the model was asked to try again.",
    )


class AuditEntry(BaseModel):
    """One record appended to output/audit_trail.json — every chat turn writes a run_start, one
    iteration per loop step, and a run_end, all sharing the same `run_id`. See
    output/harness.md's "Audit trail" section for the full field-by-field reasoning."""

    timestamp: str = Field(description="UTC time the record was written, ISO 8601.")
    run_id: str = Field(description="Groups every record from one chat turn's agent run.")
    event: Literal["run_start", "iteration", "run_end"]
    iteration: int | None = Field(default=None, description="Agent loop step number, starting at 1.")
    inputs: dict = Field(
        default_factory=dict,
        description="What started this run: user_id (an id only, never name/email), the shopper's "
        "message (truncated), and the page they were viewing. Written once, on run_start.",
    )
    model: str | None = None
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    stop_reason: str | None = Field(
        default=None,
        description="Why this step or run ended: a model finish_reason mid-run, or 'completed' / "
        "'error' / 'config_error' on run_end.",
    )
    tokens_in: int | None = None
    tokens_out: int | None = None
    output_summary: str | None = Field(default=None, description="On run_end: short version of the final reply.")
    error: str | None = Field(default=None, description="On a failed run_end: exception type and message.")


@dataclass
class AgentDeps:
    """Runtime state handed to the agent — its tools, and the dynamic instructions function in
    agent.py that tells the model who it's talking to and what they're looking at. None of this
    is sent to the model directly; it's code deciding what the model gets told, same principle as
    a tool result."""

    returned_product_ids: list[str] = field(default_factory=list)

    # Who's chatting (Problem 8). Both None for a guest.
    customer_name: str | None = None
    customer_email: str | None = None

    # The shopper's own id (Problem 9), so add_favorite/list_favorites act on their account. None
    # for a guest — those tools then decline rather than guess whose list to touch.
    user_id: int | None = None

    # What they're looking at (Problem 8): resolved from PageContext by main.py, so a bogus or
    # outdated product_id from the client can never reach the model as if it were real.
    viewing_product_id: str | None = None
    viewing_product_name: str | None = None
