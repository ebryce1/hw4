"""Tools the Campus Customs agent can call, plus the model it calls them with.

Prices and stock come only from these tools, never from the model's own memory — the agent's
instructions (prompts/prompt.md) tell it to call a tool before stating either.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import AgentDeps, ProductCard, ProductDetails, SizeStock, StockLookup

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"

DEFAULT_MODEL = "gpt6astra"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_SEARCH_RESULTS = 6


# --- model plumbing --------------------------------------------------------------------------


class AgentConfigError(RuntimeError):
    """The agent itself is misconfigured (e.g. no API key) — different from the model refusing
    one particular request, which the chat route handles separately and gracefully."""


def build_model() -> OpenAIResponsesModel:
    """Load the Portkey key from .env (checked at backend/, hw4/, and AI Foundations/) and build the model."""
    for base in (ROOT, *ROOT.parents):
        env_path = base / ".env"
        if env_path.is_file():
            load_dotenv(env_path)

    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise AgentConfigError(
            "PORTKEY_API_KEY is missing. Add it to a .env file in backend/, hw4/, or the AI Foundations folder."
        )
    model_name = os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("PORTKEY_BASE_URL", PORTKEY_BASE_URL),
        default_headers={"x-portkey-provider": "openai"},
    )
    return OpenAIResponsesModel(model_name=model_name, provider=OpenAIProvider(openai_client=client))


# --- database plumbing ------------------------------------------------------------------------


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sizes_for(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    sizes = [
        SizeStock(size=r["size"], quantity=r["quantity"], sold_out=r["quantity"] == 0) for r in rows
    ]
    sizes.sort(key=lambda s: SIZE_ORDER.index(s.size) if s.size in SIZE_ORDER else 99)
    return sizes


def shorten_description(text: str) -> str:
    """First sentence of a description, trimmed to fit a product card. Shared with main.py so a
    product looks the same whether its card came from the catalogue grid or the chat."""
    first = text.split(". ")[0].rstrip(".") + "."
    if len(first) <= 110:
        return first
    truncated = first[:107]
    cut = truncated.rfind(" ")  # back up to a whole word, not mid-word
    if cut > 60:  # only if that doesn't throw away most of the sentence
        truncated = truncated[:cut]
    return truncated.rstrip() + "..."


def _card(row: sqlite3.Row, sizes: list[SizeStock]) -> ProductCard:
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        price=row["price"],
        image_url=f"/images/{Path(row['image_file_path']).name}",
        in_stock=any(s.quantity > 0 for s in sizes),
        short_description=shorten_description(row["description"]),
    )


# --- agent tools -------------------------------------------------------------------------------


def search_products(ctx: RunContext[AgentDeps], query: str) -> dict:
    """Search the catalogue by name, garment type, description, color, or team/college tag.

    Returns up to 6 matches with product_id, name, price, and whether anything is in stock, under
    `results`. Call get_product_details for a product's full description and colors, or
    check_stock for a specific size's availability. Only product_id values that came from one of
    these three tools may be used in a reply.

    Usability note (Problem 9): the catalogue's garment_type field is inconsistent (e.g. "hoodie",
    "pullover hoodie", "hooded pullover sweatshirt" are all hoodies), so a strict match on every
    word in a query can come back empty for a perfectly reasonable request. If nothing matches
    every word, this tool automatically retries matching *any* word and sets `exact_match: false`
    on the broader results — say so honestly ("nothing exact, but here's close") rather than
    presenting a broadened result as if it were precisely what they asked for.
    """
    terms = [t for t in query.lower().split() if t]
    if not terms:
        return {"query": query, "exact_match": True, "results": []}

    with _get_db() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()

        def _find(require_all_terms: bool) -> list[ProductCard]:
            found: list[ProductCard] = []
            for row in rows:
                haystack = " ".join(
                    [
                        row["name"],
                        row["garment_type"],
                        row["description"],
                        " ".join(json.loads(row["colors"])),
                        " ".join(json.loads(row["search_tags"])),
                    ]
                ).lower()
                hits = [term in haystack for term in terms]
                if (all(hits) if require_all_terms else any(hits)):
                    found.append(_card(row, _sizes_for(conn, row["product_id"])))
                if len(found) >= MAX_SEARCH_RESULTS:
                    break
            return found

        matches = _find(require_all_terms=True)
        exact_match = True
        if not matches:
            matches = _find(require_all_terms=False)
            exact_match = False

    ctx.deps.returned_product_ids.extend(m.product_id for m in matches)
    return {
        "query": query,
        "exact_match": exact_match,
        "results": [m.model_dump() for m in matches],
    }


def get_product_details(ctx: RunContext[AgentDeps], product_id: str) -> dict:
    """Full details for one product: description, colors, price, and stock for every size.

    Call this whenever a shopper asks what a product is like, what it costs, or what colors it
    comes in. For a question about one specific size ("do you have this in L?", "how many XL
    left?"), prefer check_stock — it gives a ready-made sentence for that size.
    """
    with _get_db() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return {"error": f"No product with id {product_id!r}."}
        sizes = _sizes_for(conn, product_id)

    ctx.deps.returned_product_ids.append(product_id)
    details = ProductDetails(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        sizes=sizes,
        in_stock=any(s.quantity > 0 for s in sizes),
    )
    return details.model_dump()


def check_stock(ctx: RunContext[AgentDeps], product_id: str, size: str | None = None) -> dict:
    """Price and stock for one product, straight from the database — never guess either.

    Pass `size` (e.g. "M", "XL") when the shopper asked about one specific size; leave it out to
    see every size at once. The returned `note` is the exact sentence to say about stock — use it
    as-is rather than rephrasing the quantity, so a sold-out size is never reported as available.
    """
    with _get_db() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return {"error": f"No product with id {product_id!r}."}
        sizes = _sizes_for(conn, product_id)

    ctx.deps.returned_product_ids.append(product_id)

    matched: SizeStock | None = None
    resolved_size = size
    note: str
    if size:
        matched = next((s for s in sizes if s.size.lower() == size.strip().lower()), None)
        if matched is None:
            available = ", ".join(s.size for s in sizes) or "none"
            note = f"'{size}' isn't a size we carry for this product. Sizes offered: {available}."
            resolved_size = size
        else:
            resolved_size = matched.size
            if matched.sold_out:
                note = f"Size {matched.size} is sold out."
            elif matched.quantity <= 5:
                note = f"Only {matched.quantity} left in size {matched.size}."
            else:
                note = f"Size {matched.size} is in stock ({matched.quantity} available)."
    else:
        in_stock_sizes = [s.size for s in sizes if not s.sold_out]
        sold_out_sizes = [s.size for s in sizes if s.sold_out]
        if not in_stock_sizes:
            note = "Sold out in every size."
        elif not sold_out_sizes:
            note = "In stock in every size."
        else:
            note = f"In stock: {', '.join(in_stock_sizes)}. Sold out: {', '.join(sold_out_sizes)}."

    lookup = StockLookup(
        product_id=row["product_id"],
        name=row["name"],
        price=row["price"],
        sizes=sizes,
        in_stock=any(s.quantity > 0 for s in sizes),
        requested_size=resolved_size if (size and matched) else None,
        note=note,
    )
    return lookup.model_dump()


def add_favorite(ctx: RunContext[AgentDeps], product_id: str) -> dict:
    """Save a product to the shopper's favorites, so they can browse now and buy later without
    losing track of it (Problem 9). Call this when a shopper says to save, favorite, remember, or
    bookmark something — if they're mid-conversation about a product and say "save this" or
    "add this to my favorites" without naming it again, use the product_id already in view.

    Only works for a signed-in shopper — whether they're signed in comes from their account
    (AgentDeps.user_id), never from anything typed in chat. If `ok` is false because they're not
    signed in, tell them so and suggest they create an account.
    """
    if ctx.deps.user_id is None:
        return {"ok": False, "reason": "not signed in"}
    with _get_db() as conn:
        row = conn.execute(
            "SELECT name FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return {"ok": False, "reason": f"No product with id {product_id!r}."}
        conn.execute(
            "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)",
            (ctx.deps.user_id, product_id),
        )
        conn.commit()
    ctx.deps.returned_product_ids.append(product_id)
    return {"ok": True, "product_id": product_id, "name": row["name"]}


def list_favorites(ctx: RunContext[AgentDeps]) -> dict:
    """The shopper's saved favorites, most recently added first (Problem 9). Only works for a
    signed-in shopper (see add_favorite) — `ok: false` with an empty list otherwise.
    """
    if ctx.deps.user_id is None:
        return {"ok": False, "reason": "not signed in", "favorites": []}
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT product_id FROM favorites WHERE user_id = ? ORDER BY id DESC",
            (ctx.deps.user_id,),
        ).fetchall()
        cards: list[ProductCard] = []
        for r in rows:
            crow = conn.execute(
                "SELECT * FROM catalogue WHERE product_id = ?", (r["product_id"],)
            ).fetchone()
            if crow is not None:
                cards.append(_card(crow, _sizes_for(conn, crow["product_id"])))
    ctx.deps.returned_product_ids.extend(c.product_id for c in cards)
    return {"ok": True, "favorites": [c.model_dump() for c in cards]}
