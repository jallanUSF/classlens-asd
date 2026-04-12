# UI Polish — Five Fixes for Judge-Facing Demo

**Date:** 2026-04-12
**Branch:** `nextjs-redesign`
**Driver:** Jeff
**Context:** Post browser-driven UI/UX audit. Live app runs, but three-column desktop layout content-starves the main column to ~380px on 1440 viewports, the Gemma 4 branding is buried, and three minor polish items remain.

## Goals

1. **Make the main column breathe on desktop** — judges on 1440 laptops see a cramped demo
2. **Surface Gemma 4 in the first second** — currently buried in chat panel
3. **Eliminate the one live-API wait on demo day** — Trajectory Report uncached
4. **Orient cold-start judges in 3 seconds** — `/` has no product explainer
5. **Fix one a11y issue** — level badges color-only

---

## Fix 1 + 2 (bundled — same code area): Collapsible chat panel + Gemma 4 branding move

**Agent B — frontend shell**

- Chat panel (`components/chat/*` + whatever renders it in layout) becomes **collapsed by default**. Add a toggle button (chat bubble icon in a fixed corner, or a tab-like pull-handle). Opens as a right-side Sheet when clicked.
- Persist state in `localStorage` under key `chat-panel-open` (default `false`).
- Move "Powered by Gemma 4" from the chat panel header to the **sidebar top** (next to the ClassLens logo), as a small badge. Something like `ClassLens — powered by Gemma 4`.
- On mobile, the existing FAB pattern stays — this change affects desktop only.

**Files:** components under `frontend/src/components/chat/`, `frontend/src/components/sidebar/`, and whatever layout component composes the three columns (likely `frontend/src/app/student/[id]/page.tsx` and/or `frontend/src/app/layout.tsx`). Agent will discover.

**Success criteria:** Main content column on 1440×900 is ≥650px wide. "Powered by Gemma 4" visible in sidebar header on every page. Chat still reachable in one click. `next build` clean.

## Fix 3: Precompute trajectory reports for demo students

**Agent A — backend**

- Mirror the pattern in `scripts/generate_podcast_cache.py`.
- New file: `scripts/generate_trajectory_cache.py` with CLI that takes `[student_id]` or defaults to `[maya_2026, jaylen_2026, amara_2026]` (match existing demo cohort).
- For each student, call the trajectory agent, write JSON to `data/precomputed/trajectory_{student_id}.json`.
- Trajectory router (`backend/routers/trajectory.py`) must prefer precomputed file when present (grep for existing pattern in `podcast.py` to match).
- Ship with all 3 caches generated via real Gemma 4.

**Success criteria:** `GET /api/students/maya_2026/trajectory` returns precomputed data in <500ms. Live-API path untouched (still works). Existing 165 tests pass.

## Fix 4: "About ClassLens" banner on `/`

**Agent C — landing page**

- Add a top-of-page banner card on `/` (before "Needs Attention" section) with one-sentence explainer: *"Photo of student work → structured IEP progress data. Powered by Gemma 4 with multimodal vision, function calling, and thinking mode."*
- Muted styling consistent with the rest of the design system. No CTA — just orientation.
- Do NOT add to student detail page.

**Files:** `frontend/src/app/page.tsx` only.

**Success criteria:** `/` loads with banner above the alert list. `next build` clean. No horizontal overflow at 1440×900.

## Fix 5: Level badge shape/icon alongside color

**Agent D — design system**

- Find the component that renders L1/L2/L3 pills (likely `frontend/src/components/ui/LevelBadge.tsx` or inline JSX — grep for `"L1"` / `"L2"` / `"L3"` or `asd_level`).
- Add a shape or icon alongside the color so it's distinguishable without color: L1 → circle icon (or dot), L2 → triangle, L3 → diamond. Use lucide-react icons the design system already imports.
- Keep text label "L1/L2/L3" for screen readers.
- Ensure consistency everywhere the badge renders (sidebar student list, student header, dashboard "Your Students" grid).

**Success criteria:** L1/L2/L3 badges visible in all three locations, each carrying both color AND shape. `next build` clean.

---

## Parallelism map

| Agent | Scope | Touches | Blocks |
|---|---|---|---|
| **A** | Backend trajectory precompute | `scripts/`, `data/precomputed/`, `backend/routers/trajectory.py` | None |
| **B** | Chat collapse + Gemma branding | `components/chat/`, `components/sidebar/`, layout | None |
| **C** | Landing page banner | `app/page.tsx` | None |
| **D** | Level badges | Wherever L1/L2/L3 renders | None |

File overlap check:
- Agent B touches sidebar header (logo area); Agent D may touch sidebar student-list rendering. Different regions — should not collide unless D decides to wrap the entire list component.
- No two agents touch `app/page.tsx` — only Agent C does.
- No two agents touch the chat panel — only Agent B.

If merge conflicts occur, resolve Agent B → C → D → A order (A is fully isolated).

---

## Verification plan

After all agents return:
1. `cd frontend && npx tsc --noEmit` — 0 errors
2. `cd frontend && npx next build` — clean
3. `python -m pytest tests/ -q` — 165 still passing
4. Manual spot-check at 1440×900: main column wider; "Powered by Gemma 4" in sidebar; banner on `/`; trajectory cached; level badges with shapes.
5. Commit as a single "UI polish pass" commit.
