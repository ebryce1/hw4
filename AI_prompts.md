# AI Prompts: Campus Customs (HW4)

Running log of the prompts I gave my AI coding assistant (Claude Code). Prompts are in my own words. Evidence of the work is the running site, the database writes, and the screenshots.

## Problem 1: Vibe coder prompts

**Prompt:**
> we are working on something for campus customs again. they want a customer website with a chatbot. we're going to build a react + vite typescript front end and a python fastapi backend whose brain is a pydanticai agent. shoppers will then be able to browse products, create an account, chat about merch, see matching items appear on the page, and get info about price and stock from a local database. i'll give you campus_customs.db with tables for the product catalogue, inventory by size, and users (hashed passwords). product image file paths are in the table as well. if you look at https://yalebulldogblue.com/ you'll see the style we're going for.

**Follow-up prompt:** None needed so far.

**What was lacking after the first prompt:** N/A (no follow-up yet).

## Problem 2: Analyze the database

**Prompt:**
> look at data/campus_customs.db and understand the fields for each table. at a minimum you should understand catalogue, inventory, and users. start the file output/harness.md and write down each table and its fields and one short line on why each field matters for the shop or the chatbot. we will keep growing this harness file in later problems (models, safety, tools, specs).

**Follow-up prompt:** None needed so far.

**What was lacking after the first prompt:** N/A (no follow-up yet).

## Problem 3: Build the Campus Customs website

**Prompt:**
> scaffold a React + Vite + TypeScript front end for campus customs. put a nav bar at the top that links to main pages: home, products, about us, log in, create account. customs-style words from yalebulldogblue.com for home and about us, but write these pages in your own voice (do not copy the original site text). on the products page, show product images from the catalogue (use image paths in the database) with basic product info (name, price, short description). make each product open a single-item page (large image on one side, full product text on the other - description, price, sizes/stock when we have them.) clicking a card on products should take the shopper there. add a chat interface in the bottom right of the site (a floating chat panel is fine). it does not need to talk to an agent yet - a stub that will call your backend later is enough for this problem. We will need a small API soon to read the database, it is fine to start a simple FastAPI app in backend/main.py just to serve products and images, then grow it into the agent backend in problem 5.

**Follow-up prompt:** None needed so far.

**What was lacking after the first prompt:** N/A (no follow-up yet).

## Problem 4: Create account and login

**Prompt:**
> Build a normal create-account / login flow. create account needs first name, last name, email, password, and confirm password. login needs email and password. new accounts go into the users table. make sure to store passwords securely. a login checks a password by: never un-hashing the stored value, re-hashing what the user typed and comparing it. read the salt out of the stored string (the middle piece), don't make a new one at login. hash the typed password with that same salt then compare to the stored hash, using a constant-time compare. signup and login must use the same hash settings (same function, same salt handling, same iteration count). confirm login works for the seeded test user and for a brand-new account created in the app. update output/harness.md with how auth works.

**Follow-up prompt:**
> (mine) I don't know the seeded test user's password and won't guess or brute-force it — do you know it, or was it given to you somewhere? If not, I'll verify with a brand-new account only and say so.

**What was lacking after the first prompt:** The problem asked me to verify login against the seeded test user, but its password isn't in the data or anywhere in the project, and I can't ethically brute-force a stored hash to find it, even a toy one. I asked the user directly instead of trying to crack it.

**Second follow-up prompt (from the user):** "it is test@campuscustoms.yale.edu and password is password"

**What was lacking after that:** With the real password, the seeded login still failed at first. My default of 600,000 PBKDF2 iterations didn't match whatever the seed data was generated with — the stored hash format doesn't encode an iteration count. Using the one known, user-authorized credential (not guessing), I checked it against a short list of standard iteration counts and found the real one: 120,000. Updated `auth.py` to that count and re-verified both the seeded login and a fresh signup/login round trip.

## Problem 5: PydanticAI agent backend

**Prompt:**
> build the shop chatbot as a pydanticAI agent behind FastAPI, plugged into the front end chat widget. put the api app in backend/main.py, that is the file we run with Uvicorn. keep the agent as four files next to it (like we did in hw3): backend/prompts/prompt.md system prompt, backend/agent.py agent entry/wiring, backend/tools.py tools the agent can call, and backend/models.py pydantic structured types. in main.py, expose a chat route so a message from the website returns a reply from the agent (and whatever else we need for products/auth). you'll need my AI model API key for the agent. put campus customs voice and safety basics into prompts/prompt.md (we will expand tools and safety later). start or update types in models.py for chat replies / product cards as needed. in output/harness.md, note how the front end talks to fastapi and how the agent is loaded (prompt file + model). make sure the backend runs from the backend/ folder like this: uvicorn main:app --reload --port 8000. and lets spice it up a bit: make the chatbot handsome dan, Yale's bulldog mascot, who talks like a funny, self-centered, full-of-himself dog who's obsessed with his own good looks.

**Follow-up prompt:** None needed from the user — I hit and fixed one issue on my own: a deliberately aggressive jailbreak test I ran got blocked by the model provider's own content filter, which my code was surfacing as a raw `503` error with the provider's internal error text. That's not something to show a shopper, so I added a separate error path: a true config problem (missing API key) still returns a clear `503`, but the model refusing or failing on one specific request now falls back to a graceful in-character reply instead.

**What was lacking after the first prompt:** N/A from the user's side — the fix above was self-identified during testing, not something the user had to point out.

## Problem 6: Tools — product info and stock

**Prompt:**
> give the agent tools that look up real information from campus_customs.db: product description, price, and how many are in stock by size when the customer asks. the agent must use the database, it should not invent prices or quantities. if a size is out of stock, say so clearly. expand prompts/prompt.md so the agent knows to call these tools for price and stock questions. add or update return types in models.py. in output/harness.md list each tool and explain which model fields you chose for lookup results and why.

**Follow-up prompt:** None needed.

**What was lacking after the first prompt:** N/A — most of this was already in place from Problem 5 (`search_products`, `get_product_details`), so this problem's work was adding a dedicated `check_stock` tool for one-specific-size questions, a `StockLookup` model whose `note` field is written by code (not the model) so a sold-out size can't be phrased ambiguously, and tightening `get_product_details` to return a declared `ProductDetails` type instead of a loose dict. Verified against a real product with a known mix of sold-out, low-stock, and in-stock sizes.

## Problem 7: Chat search that updates the page

**Prompt:**
> new feature. when someone asked about a type of item, eg hoodies, the agent should search the catalogue and the website should dynamically show those matching items as product cards (image, name, price, short info) — this is an api contract, the agent returns structured product matches and then the front end renders them onto the site. after the dynamic product cards are loaded by the new feature, make sure the same single item page behavior we built in problem 3 still works: each product card including the ones the chat just put on the page should still open that detail view when clicked. update prompts/prompt.md and output/harness.md so it is clear how search results reach the page.

**Follow-up prompt:** None needed from the user — I found and fixed one issue myself while testing: the new on-page matches band was also showing on top of a product's own detail page, pushing the actual detail view below the fold. I hid it specifically on `/products/:id` routes so clicking a chat-found card opens straight into the detail view, matching what the problem asked me to verify.

**What was lacking after the first prompt:** N/A from the user's side — the fix above was self-identified during testing, not something the user had to point out.

## Problem 8: Customer memory

**Prompt:**
> when someone is logged in, save their chat history in the database in an appropriate table and reload it when they return. the agent should know who is chatting (name and email) — put it in agent deps (or an equivalent clear pattern) and/or tools the agent can call. also pass enough page context that if someone is on a product page and asks "do you have this in pink" the agent knows what item they mean. hint: we can put code into the agent context. guests can still chat, but history only needs to persist for logged-in users. document in output/harness.md: how user chat history is stored, what customer fields the agent sees, and how the page context is passed.

**Follow-up prompt:** None needed from the user — two issues came up during my own testing, both resolved without needing to ask:
1. The seed database's existing `chat_messages` rows store `products_json` as full product objects (an older format from before this schema), not the plain id list my new code writes. The history endpoint crashed on those rows until I added a parser that reads both shapes.
2. While verifying "chat opens with saved history" in the browser, clicks at the chat button's screen coordinates stopped registering (a testing-tool artifact — the browser extension's own cursor overlay sat over that exact corner). Confirmed via a direct DOM click that the app itself was fine, then used that to finish verification.

**What was lacking after the first prompt:** N/A from the user's side — both fixes above were self-identified during testing.

## Problem 9: Usability improvements

**Prompt:**
> now that the core shop works we need to choose 2 front end usability improvements and 2 agent/backend usability improvements. front end: a "favorite" function so you can save items into a favorite section to go check out later, and a "similar to" section at the bottom of each product page listing 2-3 similar items (same kind, or similar colors if nothing else matches). for backend: I don't know, you got any suggestions? write output/usability.md before or as you build — for each improvement say what you added and why it helps shoppers or the business. make sure all improvements actually show up in the running app, graders will read the write-up and look for the features.

**Follow-up prompt:** None needed from the user. For backend/agent, I suggested and built: (1) two new agent tools, `add_favorite`/`list_favorites`, so a shopper can save or check favorites by talking to the chatbot instead of clicking a heart; and (2) a smarter `search_products` that retries with a looser match when nothing matches exactly, telling the shopper honestly when results are a broadened guess rather than a precise match — a direct fix for the messy `garment_type` data flagged back in Problem 2. Two real bugs came up during my own testing, both caught and fixed without asking:
1. `/api/favorites/{user_id}` initially returned the chat's lighter `ProductCard` shape, but the front end's shared `ProductCard` component expected the fuller shape `/api/products` returns (with `description`, not `short_description`) — crashed the Favorites page until I made the endpoint match.
2. Real clicks on the favorite heart weren't registering in a couple of spots during browser testing (the same test-tool cursor-overlay issue as Problem 8, not an app bug) — confirmed via a direct DOM click that the underlying feature worked, then used that to finish verification.

**What was lacking after the first prompt:** N/A from the user's side — both fixes above were self-identified during testing.

## Problem 10: Style the website

**Prompt:**
> add creative design so the site feels like a real campus customer storefront — fonts, color, hierarchy, motion, product presentation, chat feel (already done). we'll get more points for imaginative design. write output/design.md: what we changed and why it should help customers stick around and buy, concrete and short. maybe make the background some pretty pictures of Yale's campus. also when I press "shop by style." if you can photoshop some famous Yale alumni wearing t-shirts or hats from the store, that would be sick, but if that's too much, forget about it — do painted portraits of old people like Eli Whitney, John C. Calhoun, William Taft instead. maybe make a little cartoon bulldog in a Yale sweater walk around the bottom of the page or poke his face out on the side and wink.

**Follow-up prompt:** None needed from the user — a few judgment calls I made on my own and explained in `output/design.md` rather than asking first:
1. **No real campus photos**: used an original illustrated skyline instead — I don't have rights to real photographs of Yale's campus for a decorative background.
2. **No photoshopped alumni**: declined that part, as the prompt itself offered I could; built stylized illustrated "engraved cameo" portraits instead — not photos, nobody shown wearing any product (avoids a fabricated-endorsement look entirely).
3. **Swapped Calhoun for Nathan Hale**: Calhoun was a prominent defender of slavery (Yale itself renamed Calhoun College over this), which felt like the wrong figure for storefront decor even as a joke. Said so plainly in the write-up and offered to put him back if the user disagrees.
4. **Mascot**: built the peek-and-wink version, not a full walking animation — noted as a deliberate scope choice for reliability, not a limitation I hit.

I also caught and fixed one real bug myself during testing: the scroll-reveal animation left product cards stuck invisible whenever they loaded after an API call (the product grid, mainly) because the one-time DOM scan ran before the fetch resolved. Rewrote it to use a `MutationObserver` so it keeps catching new content, not just what's on the page at the first paint.

**What was lacking after the first prompt:** N/A from the user's side — the design choices above were judgment calls I made and explained, and the bug fix was self-identified during testing. One open question I left for the user: the sentence "also when I press 'shop by style.'" cuts off mid-thought, so I made a reasonable interpretation (a visible "Filtered by" chip after clicking a style tile) and flagged it explicitly for confirmation rather than guessing silently.

### Follow-up: real campus photos

**Prompt:**
> see how yalebulldogblue.com has pictures on main pages throughout the side. it adds character. maybe add pictures of Yale's campus through the site to add more style.

**Follow-up prompt:** None needed. This directly revisits a call I made in Problem 10: I'd declined real campus photography there because I didn't yet have a legitimate way to source any. The fix wasn't to generate images — it was to find real ones with an actual open license. I searched Wikimedia Commons (Harkness Tower, Sterling Memorial Library, Old Campus, the Beinecke Library, a c. 1905 Woolsey Hall postcard), confirmed each one's specific Creative Commons or public-domain license and photographer through Commons' own API before downloading anything, resized them for the web, and added a "Photo credits" disclosure in the footer crediting each photographer and linking their license, since CC BY/CC BY-SA require attribution. Used them as the Home/About hero photos and in a new alternating-sides `SidePhoto` layout running through the About and Home pages — the "pictures throughout the side" pattern the prompt pointed at on yalebulldogblue.com.

**What was lacking after the first prompt:** N/A — no follow-up needed from the user; this was a clean addition to what Problem 10 had already built.

## Problem 11: Site testing (app check)

**Prompt:**
> test the live site and document it in output/app_check.html (a page you can double-click open). include clear screenshots and short captions for: chat checking the inventory level of an item (honest stock/price from db), the dynamic search result card appearing after a category question (eg. hoodies), one of the usability features we added in 9. make the html easy to grade: heading for each check, screenshot, one or two sentences on what the screenshot proves. put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png).

**Follow-up prompt:** None needed from the user — I found and fixed a real bug while capturing the second screenshot. Asking the chat "what hoodies do you have?" (the assignment's own example) returned zero matches, live, not a one-off model hiccup: the catalogue text only ever says "hoodie" (singular), and `search_products`' plain substring match can't find "hoodies" inside "hoodie" in either direction. Checked it directly against the database to confirm it wasn't a fluke (`hoodie` → 27 matches, `hoodies` → 0; same for `crewneck`/`crewnecks`, `tee`/`tees`, `t-shirt`/`t-shirts`). Fixed `tools.py` to try each query word with a trailing "s" added or removed before matching, re-verified "what hoodies do you have?" returns all 6 real hoodies, and used that corrected run for the actual screenshot.

**What was lacking after the first prompt:** N/A from the user's side — this problem had been skipped entirely before this prompt (a different, unprompted `app_check.html` existed from Problem 13's file-layout work, but it wasn't built to this problem's actual spec). The grading pass caught the gap; this prompt is what filled it in, and the bug above was self-identified during that work, not something the user had to point out.

*Same turn, also asked:* "try to fix P10 if you can too" — the grading pass had docked a point for `design.md` running longer than the assignment's "keep it concrete and short." Trimmed each section to a few sentences without cutting the substance (what changed + why it helps), and removed a stale "double check with you" question that the user had already answered in a later message.

## Problem 12: Audit trail, safety, finish harness

**Prompt:**
> keep an append-only output/audit_trail.json of agent-loop activity (time, tool name, short args/results, stop reason). do not wipe between runs. also, think of some safety rules to give the agent — you got any ideas for that one? finish output/harness.md so it is clear how the system works: model fields in models.py and why you chose them, tools and abilities, safety rules, specs (loop limits, result caps, models, how to run front + back).

**Follow-up prompt:** None needed. For safety rules, since the user asked for ideas: I added rules against bulk-exporting the catalogue (anti-scraping), discussing another shopper's account, treating tool results/page context as untrusted data the same as a shopper's message, only favoriting something the shopper explicitly asked to save, never revealing backend internals (including the audit trail's own existence), and capping redundant tool calls — all tested and confirmed working against the real running agent.

**What was lacking after the first prompt:** N/A — this was a self-contained build-and-verify problem with explicit requirements; no ambiguity needed resolving with the user.

## Problem 13: Push to GitHub and submit URL

**Prompt:**
> put your code in a folder named hw4 and push it to a public GitHub repository. on canvas I will submit the repo URL. do not put the real .env, campus_customs.db, or product images in the repo. use gitignore. include .env.example with placeholders only. [expected file layout + local-only data pack shown as two images]. the agent itself is four files under backend/: prompts/prompt.md, agent.py, tools.py, and models.py. README.md should explain how to run the front end and back end after placing the data pack.

**Follow-up prompt:** None needed from the user. Several things came up that I resolved on my own:
1. Neither `git` nor `gh` were fully usable out of the box — `gh` wasn't installed and there's no Homebrew on this machine. Downloaded the `gh` CLI release directly (no sudo needed) and asked the user to complete the GitHub device-login in their own browser (a real login has to be theirs, not something I can do for them).
2. Matched the exact file layout from the screenshots: moved `requirements.txt` to the `hw4/` root (it had been under `backend/`), added the missing `.env.example` and `README.md`, and built `output/app_check.html` + `output/app_check_images/` (shown in the expected layout but not asked for in words) — a page of real screenshots from the running app as visual proof it works, not just that it builds.
3. Found and fixed a real `.gitignore` bug before pushing anything: the existing pattern `.env.*` would have also matched and excluded `.env.example` itself. Added `!.env.example` to un-ignore it.
4. Before the first commit, explicitly verified with `git check-ignore` that `data/`, `.env`, `backend/.venv`, and `frontend/node_modules` were all actually excluded (not just absent by chance), and grepped every staged file for anything that looked like a real API key. Pushed only after that came back clean.
5. The first `gh repo create --push` failed on an HTTP 400 mid-transfer; the retry needed `gh auth setup-git` to wire gh's stored credentials into plain `git push`, which then succeeded. Confirmed via the GitHub API afterward that the repo is public and its contents match exactly.

**What was lacking after the first prompt:** N/A — all five items above were self-identified and fixed without needing to ask the user anything; the one thing that did need the user was the login itself, which only they could complete.

<!-- Add one section per problem below: number and title, at least one prompt in my own words, one follow-up if needed, and one sentence on what the first prompt lacked. -->
