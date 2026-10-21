# Campus Customs

A Yale-themed campus merch storefront with an AI shop assistant — Handsome Dan, Yale's bulldog
mascot. React + Vite + TypeScript on the front end, FastAPI on the back end, with a PydanticAI
agent as the chatbot's brain.

Full write-ups of how the system works, what was built and why, are in [`output/`](output/):
[`harness.md`](output/harness.md) (database, auth, the agent, tools, safety, specs — the complete
technical reference), [`usability.md`](output/usability.md), [`design.md`](output/design.md), and
[`app_check.html`](output/app_check.html) (screenshots of the running app). Every prompt used to
build this is logged in [`AI_prompts.md`](AI_prompts.md).

## 1. Get the data pack

This repo does **not** include the product database or images — they're not ours to publish. You
need `campus_customs.db` and the `products/` image folder, placed like this:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/
```

## 2. Set up your API key

```bash
cp .env.example .env
```

Edit `.env` and fill in `PORTKEY_API_KEY` with your own Portkey key. This file stays local — it's
in `.gitignore` and is never committed.

## 3. Run the backend

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r ../requirements.txt
./.venv/bin/uvicorn main:app --reload --port 8000
```

Leave this running. It serves the API at `http://localhost:8000` and reads `data/` and `.env`
from the `hw4/` folder above it.

## 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL it prints (`http://localhost:5173`). The dev server proxies `/api/*` and `/images/*`
to the backend on port 8000, so both need to be running.

## 5. Try it

- Browse products, open one, favorite it, check "You might also like."
- Create an account, or log in as the seeded test account if you have its credentials.
- Open the chat in the bottom-right corner and ask Handsome Dan about merch, sizes, or stock.

## Project layout

```
hw4/
├── AI_prompts.md        # every prompt used to build this, by problem
├── requirements.txt      # backend Python dependencies
├── .env.example           # copy to .env and fill in your Portkey key
├── frontend/               # React + Vite + TypeScript app
├── backend/
│   ├── main.py             # FastAPI app — run with: uvicorn main:app --reload --port 8000
│   ├── agent.py             # the agent: entry point and wiring
│   ├── models.py             # Pydantic models (chat, products, audit trail)
│   ├── tools.py               # tools the agent can call
│   ├── audit.py                # the agent loop + append-only audit trail
│   ├── auth.py                  # password hashing/verification
│   └── prompts/
│       └── prompt.md             # the agent's system prompt (voice + safety rules)
└── output/
    ├── harness.md             # full technical writeup: how the whole system works
    ├── design.md                # the visual design pass and why
    ├── usability.md               # the usability-improvement features and why
    ├── app_check.html               # screenshots proving the app runs
    ├── app_check_images/              # screenshots linked from app_check.html
    └── audit_trail.json                # append-only log of every agent run
```

`backend/agent.py`, `backend/tools.py`, `backend/models.py`, and `backend/prompts/prompt.md` are
the agent itself. `data/` (the database and product images) stays local only — see step 1.
