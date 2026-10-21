# Design

What changed, and why it should help a shopper stick around and buy.

## Fonts

Headings: Georgia → **Playfair Display** (an elegant, high-contrast serif). Body: **Inter**. The
old system-font look read as a generic app, not a storefront — type is one of the first signals a
shopper reads for "is this worth trusting with a card."

## Color

Added a warm cream background in place of flat white/gray, and one gold accent (`--gold`) used
consistently on the primary CTA, hover states, and dividers. Navy-and-gold is Yale's own secondary
palette, so it reads as "collegiate retail" instead of "database frontend."

## Hierarchy & motion

- **Scroll-reveal**: product grids and page sections fade/rise into view as you scroll
  (`useScrollReveal.ts`) — a static page gets skimmed; one that reveals itself holds attention
  longer per section.
- **Card hover**: lift, deeper shadow, slight image zoom — the on-screen equivalent of picking an
  item up to look at it.
- **"Shop by style" tiles**: added icons, hover lift, and a gold underline sweep — four clear
  choices instead of four plain gray boxes.
- **Filter chip**: clicking a style tile now shows a "Filtered by: Hoodies ×" pill on Products, so
  the click visibly did something and there's a one-click way back.

## Product presentation

The "You might also like" section (Problem 9) does the heavy lifting here; this pass just gives
every card site-wide (grid, similar items, favorites, chat matches) the same hover treatment, so a
product behaves consistently no matter where a shopper finds it.

## Chat feel

Already built in Problems 5–9 — nothing new here by design.

## Real campus photos and the mascot

Five real photos from Wikimedia Commons — Harkness Tower, Sterling Memorial Library, Old Campus,
the Beinecke Library, a c. 1905 Woolsey Hall postcard — each under a Creative Commons or
public-domain license that explicitly permits reuse. Used as the Home/About heroes and in
alternating-side `SidePhoto` sections (the layout yalebulldogblue.com uses throughout its pages),
with every photographer credited in the footer's "Photo credits" disclosure, as CC BY/CC BY-SA
require. (A first pass used an illustrated skyline instead, over a licensing concern that doesn't
actually apply to properly-licensed photography — kept now only as a CSS fallback.)

No photoshopped alumni — putting real people, even historical ones, into fabricated images wearing
specific products reads as a fake endorsement, so the About page instead has three small
illustrated "engraved cameo" portraits (not photos, nobody shown wearing merchandise), captioned
with their real names and Yale class years: Eli Whitney, Nathan Hale, William H. Taft. Nathan Hale
stands in for John C. Calhoun, who was a prominent defender of slavery — a bad fit for storefront
decor even as a joke, and confirmed with you already.

A small illustrated bulldog (`BulldogMascot.tsx`) peeks up and winks from the bottom-left corner
of every page, with a quip on click. A consistent, in-character mascot makes the site feel like it
belongs to someone rather than being generated — a small trust signal.
