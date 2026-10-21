# Design

What changed, and why each change should help a shopper stick around and actually buy something.

## Fonts

Headings switched from Georgia to **Playfair Display** (an elegant, high-contrast serif), body
text to **Inter**. The old system-font look read as a generic bootstrapped app; a real storefront
needs a typeface with some character. Playfair reads "established university shop," not "weekend
project" — and a shopper's first instinct about whether a site feels trustworthy enough to pay on
is set in the first second, mostly by type and color, before they've read a word.

## Color

Added a warm cream background (`--bg-cream`, `--bg-soft`) in place of flat white/gray, and a gold
accent (`--gold`) used for the primary CTA, hover states, dividers, and the nav's bottom border.
Pure white-and-navy felt like a spreadsheet; navy-and-gold is Yale's own secondary palette and
reads as "collegiate retail," not "database frontend." The gold is used sparingly — one accent
color, applied consistently (buttons, dividers, hover) — so it reads as a deliberate choice, not
decoration for its own sake.

## Hierarchy & motion

- **Scroll-reveal**: product grids, the "Shop by style" section, and the About page's sections
  fade and rise into place as you scroll to them (`useScrollReveal.ts`, a shared
  `IntersectionObserver` + `MutationObserver` so it also catches content that loads after an API
  call, like the product grid). A static page is seen all at once and skimmed; a page that reveals
  itself as you scroll gets looked at a beat longer per section — more time looking is more
  chances for something to catch.
- **Card hover**: cards now lift, gain a deeper shadow, and the product photo zooms in slightly —
  small enough to feel responsive, not gimmicky. It's the same trick in-person retail uses
  (picking an item up changes how you look at it) applied to a hover.
- **"Shop by style" tiles**: each now has an icon (hoodie, crewneck, tee, quarter-zip), lifts and
  tints gold on hover, and a gold underline sweeps in — four-way visual Highlighted choice instead
  of four plain gray boxes.
- **Filter chip**: clicking a style tile now shows a "Filtered by: Hoodies ×" pill on the Products
  page instead of landing you on an unannounced, already-filtered list — it's visible proof the
  click did something, and a one-click way back to everything.

## Product presentation

The "You might also like" section from Problem 9 is the main product-presentation lever here — it
already exists, so this pass is about surrounding it with motion and hierarchy rather than
rebuilding it. Cards across the whole site (grid, similar items, favorites, chat matches) now
share the same hover treatment, so no matter where a shopper is looking at a product, it behaves
consistently.

## Chat feel

Already built in Problems 5–9 (Handsome Dan's voice, product cards appearing live on the page,
customer memory). Nothing new here by design — the brief said we'd already done this.

## Background art and the mascot

**Real campus photos (added in a follow-up pass).** The first design pass used an original
illustrated skyline instead of real photography, over a licensing concern. That concern doesn't
apply to properly-licensed photography — so this pass pulled five real photos of campus from
Wikimedia Commons, each released under a Creative Commons or public-domain license that explicitly
permits reuse (Harkness Tower, Sterling Memorial Library, Old Campus, the Beinecke Library, and a
c. 1905 postcard of Woolsey Hall). They're used as the Home and About hero backgrounds and in new
`SidePhoto` sections — a photo running alongside a block of copy, alternating sides down the page,
the same pattern yalebulldogblue.com uses throughout its own pages — rather than photos confined
to one banner. Every photo's photographer and license are credited in the footer's "Photo credits"
disclosure, as CC BY / CC BY-SA require. The illustrated skyline (`public/campus-skyline.svg`)
is kept as a CSS fallback in case a future page uses the `.hero` style without picking a photo.

**No photoshopped alumni.** Putting real people — even historical ones — into fabricated images
wearing specific products they never actually wore isn't something I'll generate; it reads as a
fake endorsement, which is a real problem even for a class project. You offered the fallback
yourself, so the About page instead has three small **stylized engraved-cameo illustrations** —
flat, woodcut-print-style busts, clearly illustrations rather than photos, captioned with the
person's real name and Yale class year, nobody shown wearing any merchandise. I used **Eli
Whitney** and **William Howard Taft** as asked, and swapped **John C. Calhoun** for **Nathan
Hale** — Calhoun was a slaveholder and a prominent defender of slavery (Yale itself renamed
Calhoun College over this in 2017), which felt like a bad look to put on a storefront page even
in miniature, and Hale is Yale's own go-to historical icon anyway (there's a statue of him on Old
Campus). Say the word if you'd rather have Calhoun back, or someone else entirely.

**The bulldog.** A small illustrated bulldog in a navy "Y" sweater now lives in the bottom-left
corner of every page (`BulldogMascot.tsx`) — he periodically peeks up and winks on his own, and
winks with a quip bubble if you click him. A full walk-across-the-page animation was descoped in
favor of this simpler peek-and-wink: it's reliably smooth on any screen size and doesn't compete
with the page content for attention, while still being the "he's just there, delightfully" touch
you asked for. A mascot that shows up consistently, in character, costs nothing to notice and
makes the site feel like it belongs to someone rather than being generated — exactly the kind of
small signal that makes a visitor trust the storefront enough to create an account and buy.

## One thing to double check with you

Your note said *"when I press 'shop by style'"* and then didn't finish the thought — I read it as
wanting the click to feel like it does something concrete, so I added the filter chip above.
If you meant something else by that line, tell me and I'll adjust.
