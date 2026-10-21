"""Campus Customs API. Run from backend/: uvicorn main:app --reload --port 8000

Problem 3: read-only endpoints that serve the catalogue, stock, and product images.
Problem 4: account creation and login against the users table.
Problem 5: /api/chat, backed by the Handsome Dan agent (agent.py, tools.py, prompts/prompt.md).
Problem 9: favorites (table created at startup — not in the original seed db) and similar items.
See output/usability.md for what these are and why.
"""

import json
import logging
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, field_validator

from agent import run_chat
from auth import hash_password, verify_password
from models import ChatHistoryEntry, ChatRequest, ChatResponse, FavoriteRequest, ProductCard
from tools import AgentConfigError, shorten_description

FALLBACK_REPLY = (
    "Even a dog with this jawline hits the occasional snag. Give me a second and try that again?"
)
MAX_HISTORY_MESSAGES = 40  # last ~20 exchanges, enough to feel continuous without reloading forever

logger = logging.getLogger("campus_customs")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
IMAGES_DIR = DATA_DIR / "products"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema() -> None:
    """`favorites` isn't in the original seed database — create it on startup if it's missing,
    so a fresh checkout of this project needs no manual migration step."""
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE (user_id, product_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES catalogue(product_id)
            )
            """
        )
        conn.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ensure_schema()
    yield


app = FastAPI(title="Campus Customs API", lifespan=lifespan)


def product_from_row(row: sqlite3.Row) -> dict:
    """Shape a catalogue row for the front end (parse JSON text, build image URL)."""
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "price": row["price"],
        "image_url": f"/images/{Path(row['image_file_path']).name}",
    }


@app.get("/api/products")
def list_products() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            ORDER BY c.name
            """
        ).fetchall()
    return [{**product_from_row(r), "in_stock": r["total_stock"] > 0} for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        stock = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()
    sizes = sorted(
        ({"size": s["size"], "quantity": s["quantity"]} for s in stock),
        key=lambda s: SIZE_ORDER.index(s["size"]) if s["size"] in SIZE_ORDER else 99,
    )
    return {
        **product_from_row(row),
        "sizes": sizes,
        "in_stock": any(s["quantity"] > 0 for s in sizes),
    }


# Garment types most alike, so "similar items" pulls from the same shelf rather than just
# "anything with a shared word." Keyed on substring keywords because the catalogue's own
# garment_type text is inconsistent (see output/harness.md's Database section) — e.g. "hoodie",
# "pullover hoodie," and "hooded pullover sweatshirt" should all bucket together.
_CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("hoodie", ["hoodie", "hooded"]),
    ("crewneck", ["crewneck", "raglan", "mockneck"]),
    ("t-shirt", ["t-shirt", "tshirt", "tee"]),
    ("quarter-zip", ["quarter-zip", "quarter zip", "1/4 zip"]),
    ("fleece/jacket", ["fleece", "jacket", "full-zip"]),
]


def _category_for(garment_type: str) -> str:
    text = garment_type.lower()
    for category, keywords in _CATEGORY_KEYWORDS:
        if any(k in text for k in keywords):
            return category
    return "other"


@app.get("/api/products/{product_id}/similar")
def similar_products(product_id: str, limit: int = 3) -> list[dict]:
    """Up to `limit` products like this one — same kind of garment first (Problem 9: usability.md
    "Similar items"); if too few of those exist, fill in with anything sharing a color, so even an
    unusual product still gets suggestions rather than none."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")

        this_category = _category_for(row["garment_type"])
        this_colors = set(json.loads(row["colors"]))

        others = conn.execute(
            "SELECT * FROM catalogue WHERE product_id != ?", (product_id,)
        ).fetchall()

        same_category = [o for o in others if _category_for(o["garment_type"]) == this_category]
        picked: list[sqlite3.Row] = same_category[:limit]

        if len(picked) < limit:
            picked_ids = {p["product_id"] for p in picked}
            same_color = [
                o
                for o in others
                if o["product_id"] not in picked_ids and this_colors & set(json.loads(o["colors"]))
            ]
            picked += same_color[: limit - len(picked)]

        cards = [
            {
                **product_from_row(p),
                "in_stock": any(
                    s["quantity"] > 0 for s in _sizes_for(conn, p["product_id"])
                ),
            }
            for p in picked
        ]
    return cards


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Required")
        return v

    @field_validator("password")
    @classmethod
    def min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def public_user(row: sqlite3.Row) -> dict:
    """User fields safe to send to the front end. Never includes password_hash."""
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": row["name"],
        "email": row["email"],
    }


@app.post("/api/signup", status_code=201)
def signup(body: SignupRequest) -> dict:
    if body.password != body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    email = body.email.lower()
    name = f"{body.first_name} {body.last_name}"
    password_hash = hash_password(body.password)

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing is not None:
            raise HTTPException(status_code=409, detail="An account with that email already exists")

        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, password_hash, body.first_name, body.last_name),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return public_user(row)


@app.post("/api/login")
def login(body: LoginRequest) -> dict:
    email = body.email.lower()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    # Same "invalid email or password" message either way, so a login attempt
    # can't be used to probe which emails have accounts.
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return public_user(row)


@app.get("/api/favorites/{user_id}")
def list_favorites_endpoint(user_id: int) -> list[dict]:
    """Problem 9: a shopper's saved-for-later list, most recently added first. Shaped exactly
    like /api/products (not the lighter chat ProductCard) so the front end's one ProductCard
    component renders a favorite the same way everywhere, no matter which page it came from.

    Like the chat history endpoint, this trusts whatever user_id it's given — see that
    endpoint's docstring for the same known limitation (no session token in this app yet)."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.* FROM favorites f
            JOIN catalogue c ON c.product_id = f.product_id
            WHERE f.user_id = ?
            ORDER BY f.id DESC
            """,
            (user_id,),
        ).fetchall()
        return [
            {**product_from_row(r), "in_stock": any(s["quantity"] > 0 for s in _sizes_for(conn, r["product_id"]))}
            for r in rows
        ]


@app.post("/api/favorites", status_code=201)
def add_favorite_endpoint(body: FavoriteRequest) -> dict:
    with get_db() as conn:
        exists = conn.execute(
            "SELECT 1 FROM catalogue WHERE product_id = ?", (body.product_id,)
        ).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Product not found")
        conn.execute(
            "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)",
            (body.user_id, body.product_id),
        )
        conn.commit()
    return {"ok": True}


@app.delete("/api/favorites/{user_id}/{product_id}")
def remove_favorite_endpoint(user_id: int, product_id: str) -> dict:
    with get_db() as conn:
        conn.execute(
            "DELETE FROM favorites WHERE user_id = ? AND product_id = ?", (user_id, product_id)
        )
        conn.commit()
    return {"ok": True}


def _sizes_for(conn: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    return sorted(
        ({"size": r["size"], "quantity": r["quantity"]} for r in rows),
        key=lambda s: SIZE_ORDER.index(s["size"]) if s["size"] in SIZE_ORDER else 99,
    )


def _cards_for(product_ids: list[str]) -> list[ProductCard]:
    """Load full ProductCards for ids the agent's tools actually returned, in that order."""
    if not product_ids:
        return []
    with get_db() as conn:
        placeholders = ",".join("?" for _ in product_ids)
        rows = conn.execute(
            f"SELECT * FROM catalogue WHERE product_id IN ({placeholders})", product_ids
        ).fetchall()
        by_id = {
            r["product_id"]: ProductCard(
                product_id=r["product_id"],
                name=r["name"],
                price=r["price"],
                image_url=f"/images/{Path(r['image_file_path']).name}",
                in_stock=any(s["quantity"] > 0 for s in _sizes_for(conn, r["product_id"])),
                short_description=shorten_description(r["description"]),
            )
            for r in rows
        }
    return [by_id[pid] for pid in product_ids if pid in by_id]


def _product_ids_from_json(raw: str | None) -> list[str]:
    """Parse a chat_messages.products_json value into product_ids. Handles both the format this
    app writes (a plain list of id strings) and the seed data's own format (a list of full
    product objects, each with its own "product_id" key) — the seed rows predate this schema."""
    if not raw:
        return []
    parsed = json.loads(raw)
    ids: list[str] = []
    for item in parsed:
        if isinstance(item, str):
            ids.append(item)
        elif isinstance(item, dict) and "product_id" in item:
            ids.append(item["product_id"])
    return ids


def _save_chat_message(user_id: int, role: str, content: str, product_ids: list[str] | None) -> None:
    """Persist one turn for a signed-in shopper (Problem 8). Only product_ids are stored, not a
    full snapshot — reloaded cards are re-resolved against the live catalogue, so they always
    show today's price and stock, never what it was when the message was sent."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, json.dumps(product_ids) if product_ids else None),
        )
        conn.commit()


@app.get("/api/chat/history/{user_id}")
def chat_history(user_id: int) -> list[ChatHistoryEntry]:
    """What the chat widget loads on return for a signed-in shopper (Problem 8): their last
    MAX_HISTORY_MESSAGES turns, oldest first, with each turn's product cards rebuilt fresh.

    Known limitation: like the rest of this app's auth (Problem 4), there is no session token —
    whoever can send a user_id can read that user_id's history. Fine for a class project, not
    for a real deployment; a real version would check a signed session instead of a bare id.
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, MAX_HISTORY_MESSAGES),
        ).fetchall()
    rows = list(reversed(rows))  # query grabs the most recent N; put them back in time order
    return [
        ChatHistoryEntry(
            role=r["role"],
            content=r["content"],
            products=_cards_for(_product_ids_from_json(r["products_json"])),
        )
        for r in rows
    ]


@app.post("/api/chat")
async def chat(body: ChatRequest) -> ChatResponse:
    """The chat <-> site contract (Problem 7): `products` is structured data (ProductCard —
    image_url, name, price, short_description, in_stock), not text. The front end renders it as
    real product cards on the page, the same way it renders /api/products results.

    Problem 8: who's chatting (name/email) and what they're looking at (page_context) are
    resolved here, from the database and the catalogue — never taken as-is from the client — and
    handed to the agent as AgentDeps. For a signed-in shopper, both sides of the turn are saved
    to chat_messages; a guest's conversation is never written to the database.
    """
    customer_name = customer_email = None
    if body.user_id is not None:
        with get_db() as conn:
            row = conn.execute(
                "SELECT first_name, last_name, email FROM users WHERE id = ?", (body.user_id,)
            ).fetchone()
        if row is not None:
            customer_name = f"{row['first_name']} {row['last_name']}".strip() or None
            customer_email = row["email"]

    # Resolve the viewed product server-side so the agent is only ever told about a real product,
    # never whatever a client happened to claim.
    viewing_product_id = body.page_context.product_id if body.page_context else None
    viewing_product_name = None
    if viewing_product_id:
        with get_db() as conn:
            prow = conn.execute(
                "SELECT name FROM catalogue WHERE product_id = ?", (viewing_product_id,)
            ).fetchone()
        viewing_product_name = prow["name"] if prow else None
        if viewing_product_name is None:
            viewing_product_id = None

    if body.user_id is not None:
        _save_chat_message(body.user_id, "user", body.message, None)

    try:
        reply, product_ids = await run_chat(
            body.message,
            body.history,
            customer_name=customer_name,
            customer_email=customer_email,
            user_id=body.user_id,
            viewing_product_id=viewing_product_id,
            viewing_product_name=viewing_product_name,
        )
    except AgentConfigError as exc:
        # The agent itself isn't set up (e.g. no PORTKEY_API_KEY) — a real outage, worth a clear error.
        logger.error("Chat agent misconfigured: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        # The model/provider rejected or failed on this one request (e.g. an upstream content
        # filter catching an injection attempt, a timeout). Don't show the shopper a raw error or
        # a stack trace — degrade to an in-character reply and keep the chat usable.
        logger.exception("Chat agent failed on one request")
        reply, product_ids = FALLBACK_REPLY, []

    if body.user_id is not None:
        _save_chat_message(body.user_id, "assistant", reply, product_ids)

    return ChatResponse(reply=reply, products=_cards_for(product_ids))


app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
