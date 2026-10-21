# Usability Improvements

Two front-end improvements and two backend/agent improvements, built on top of the working shop
from Problems 1–8. All four are live in the running app — see "Where to see it" under each one.

---

## Front end

### 1. Favorites ("save for later")

**What I added:** a heart toggle (♡ / ♥) on every product card — the Products grid, the "You
might also like" section, and the product detail page — plus a new `/favorites` page listing
everything saved, and a "Favorites" link in the nav bar once signed in. Favorites are stored per
account (a new `favorites` table, created automatically the first time the backend starts — it
wasn't in the original seed database) and reload with the shopper wherever they sign back in,
the same way chat history already does (Problem 8). Clicking the heart as a guest sends you to
the login page instead of silently doing nothing.

**Why it helps shoppers:** browsing and buying are different moods. Someone scrolling the
catalogue on a study break isn't ready to pick a size and check out, but they also don't want to
lose the hoodie they liked. A favorites list lets them keep browsing without that pressure, and
come back when they're actually ready to buy.

**Why it helps Campus Customs as a business:** a saved item is a shopper who almost converted.
Without a save option, "maybe later" usually means never coming back, or arriving through a
search engine for something else entirely and never rediscovering it. A favorites list turns that
into a concrete to-do the shopper set for themselves — and the chat agent can now help them act on
it directly (see "Agent can save and list favorites," below), so a passing interest during a chat
conversation doesn't require remembering a product name later.

**Where to see it:** click the heart on any product card or on a product's own page, then visit
Favorites in the nav bar (you'll need to be signed in — try the seed account,
`test@campuscustoms.yale.edu` / `password`, or create one).

### 2. "You might also like" (similar items)

**What I added:** a section at the bottom of every product's page showing 2–3 similar products,
each a full card (image, name, short description, price) that opens that product's own detail
page just like any other card. "Similar" means, in order: other products of roughly the same kind
(a hoodie page shows other hoodies, a t-shirt page shows other t-shirts), and if there aren't
enough of those, it fills in with products that share a color instead — exactly the "if there are
no other items, maybe just similar colors" fallback you suggested, so a page never comes up with
nothing.

One real wrinkle, and why "roughly the same kind" instead of an exact match: the catalogue's
`garment_type` field is inconsistent — "hoodie," "pullover hoodie," and "hooded pullover
sweatshirt" are all hoodies, but they're different strings (flagged back in
[output/harness.md](harness.md)'s Database section in Problem 2). Matching that field exactly
would often turn up nothing even when good matches exist. The similarity logic instead buckets
garment types by keyword (anything with "hoodie" or "hooded" counts as the same category, and so
on for crewnecks, t-shirts, quarter-zips, and fleece/jackets), so it actually reflects what a
shopper would consider "the same kind of item."

**Why it helps shoppers:** it's a second chance to find something that fits, right at the moment
they're already looking closely at one product — no need to go back and search again.

**Why it helps Campus Customs as a business:** more products seen per visit means more chances to
convert, and it's a standard, proven retail pattern ("customers also viewed...") for a reason — it
turns a single-item look into a small browsing session, which is exactly what the business wants
from a shopper who's already engaged enough to open a product page.

**Where to see it:** open any product's page and scroll to the bottom — try
`/products/baseball-left-chest-crewneck` to see it pull in other crewnecks.

---

## Backend / agent

You said you didn't have ideas for this half, so here's what I picked and why, tied to things
already built:

### 3. Agent can save and list favorites through conversation

**What I added:** two new tools, `add_favorite` and `list_favorites` (`backend/tools.py`),
registered on the agent alongside the existing three. A shopper can now say "save this for
later," "add the hoodie to my favorites," or "what have I saved?" mid-conversation, and Handsome
Dan does it — using `page_context` (Problem 8) to know which product "this" means, the same way
he already resolves "is this in stock?" The chat route passes the shopper's own account id into
`AgentDeps`, never anything typed in chat, so the agent can only ever touch that one shopper's
list. A guest gets a clear, in-character "you'll need an account" instead of a silent failure.

**Why it helps shoppers:** this directly extends the front-end favorites feature (#1) to the
chat — a shopper doesn't have to break their conversation, scroll back to a card, and click a
heart; saying "save that" is faster and keeps them in the flow of talking to the assistant, which
is the whole point of having a chat assistant in the first place.

**Why it helps the business:** the easier it is to act on interest in the moment, the more
interest actually gets captured instead of forgotten. A chat-driven save is also a strong signal
of real intent (a shopper who said something, not just hovered a cursor) — useful if Campus
Customs ever wants to look at what gets favorited most, or follow up with shoppers who saved
something but didn't buy.

**Where to see it:** open the chat, ask about a product (or view its page), then say "save this
for later." Follow up with "what have I favorited?" to see it listed back.

### 4. Search that doesn't dead-end

**What I added:** `search_products` (`backend/tools.py`) now tries a strict match first — every
word of the query has to show up somewhere on the product — and only if that comes back empty
does it retry with a looser match (any word matching), marking the result `exact_match: false`.
The agent's instructions tell it to be honest about which kind of result it's showing ("nothing
exact, but here's close") rather than presenting a loose guess as if it were precise.

**Why this, specifically:** it's a direct fix for a gap I flagged in Problem 2's database
analysis and ran into again while building "You might also like" (#2) — the catalogue's
`garment_type` and description text are inconsistent enough that a shopper's perfectly reasonable
phrasing ("a navy hoodie," "something for game day") can fail a strict match even when good
products exist. Before this change, a near-miss query just came back as "we don't have that,"
even when the catalogue clearly did.

**Why it helps shoppers:** fewer dead ends. Asking in your own words should work, not just the
exact words that happen to appear in a product's listing.

**Why it helps the business:** every "sorry, nothing found" is a shopper who might just leave.
Broadening the search instead of giving up on the first miss keeps more of those shoppers looking
at real products instead of bouncing off an empty result.

**Where to see it:** ask the chat for something specific enough to miss an exact match but close
enough to have real alternatives — for example "a green hoodie" (the catalogue has hoodies, just
not green ones) — and watch it offer the close alternatives instead of a flat "no."
