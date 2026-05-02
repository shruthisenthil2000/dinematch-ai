# Google Stitch prompt — Next.js restaurant recommendation UI

Copy everything inside the block below and paste it into **Google Stitch** (or similar UI / mockup generators) to produce screens or visual references for the frontend. The implementation target is **Next.js** (TypeScript, responsive, accessible).

---

## Prompt (copy from here)

```
Design a complete, production-style UI kit and key screens for a web app called “DineMatch” (working title): an AI-assisted restaurant recommendation experience inspired by Zomato, but with a neutral brand (no third-party logos).

TARGET STACK (for engineers implementing from your designs):
- Next.js (App Router), TypeScript
- Styling: Tailwind CSS or CSS Modules (pick one visually consistent system)
- Data: the client calls a JSON API that accepts user preferences and returns ranked restaurants with AI-written rationales

USER INPUTS (must appear clearly in the form UI):
- Location (text, required) — city or neighborhood (e.g. Bangalore, Bellandur)
- Budget band (required) — single select: low | medium | high
- Cuisines (optional) — multi-select or comma-separated chips; empty means “any cuisine”
- Minimum rating (required) — number 0–5, step 0.1
- Optional constraints (optional) — textarea, e.g. family-friendly, outdoor seating, “around ₹2000 for two”
- Advanced / power user (collapsible section): “Top N” (default 5), “Candidate cap” (default 25), “Use live LLM” toggle (on = call model; off = deterministic fallback)

PRIMARY USER FLOW:
1) Home: short hero (“Find restaurants that fit your taste and budget”) + preference form + primary CTA “Get recommendations” + secondary “Try demo” (prefills realistic Indian city + budget + rating).
2) Loading: full-width subtle progress — skeleton cards or pulse placeholders; disabled CTA; non-blocking message “Finding matches…”
3) Results: 
   - Optional top “Comparative summary” panel (1–2 sentences comparing top picks)
   - Responsive grid of recommendation CARDS. Each card shows: rank badge, restaurant name, cuisine line, star rating + numeric rating, estimated cost line, 2–4 line AI rationale in readable body text, small muted chip or caption with opaque “Restaurant ID” for grounding (developer-facing but visible in MVP)
   - Subtle footer strip: “Candidates considered: N · Latency · Outcome” (muted typography; feels diagnostic, not marketing)
4) Empty state: friendly illustration or icon, headline “No matches yet”, body copy suggesting to lower min rating, widen budget, or clear cuisine filters; single CTA “Edit preferences”
5) Error state: inline alert for validation errors (field-level if possible); global alert for network / server errors with retry

VISUAL LANGUAGE:
- Light mode first; calm slate/blue accent; plenty of whitespace; rounded corners (10–12px), soft borders, subtle shadows on cards
- Typography: modern sans (e.g. Inter-like); clear hierarchy (H1 → body → meta)
- Mobile-first; show how the layout adapts at tablet and desktop
- Accessibility: focus states on inputs and buttons, sufficient contrast, tap targets ≥ 44px on mobile

DELIVERABLES FROM STITCH:
- High-fidelity mockups for the five states above (Home+form, Loading, Results, Empty, Error)
- Optional: a compact component sheet (buttons, inputs, cards, alerts, chips) for a Next.js design handoff
- Annotate one screen with brief notes: “POST JSON body: { preferences: { location, budget, cuisines[], min_rating, optional_constraints? }, cap, top_n, use_llm }” and “Response: recommendations[] with rank, name, cuisine, rating, estimated_cost, ai_rationale, restaurant_id”
```

---

## After Stitch: wiring to this repo

- Preference fields match `schemas/user-preferences.schema.json`.
- Backend contract for recommendations is documented in [`src/phase5/README.md`](../src/phase5/README.md) (`POST /api/recommend`).
- The current reference UI lives under [`src/phase6/`](../src/phase6/README.md) (Flask + HTML); a Next.js app would replace Phase 6’s presentation layer while keeping the same API shapes.
