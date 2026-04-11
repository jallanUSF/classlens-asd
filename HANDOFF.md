# HANDOFF.md — Session Handoff

**Date:** 2026-04-11 (overnight — QA fix queue sprint, 8 of 12 findings resolved)
**Branch:** `nextjs-redesign`
**Status:** SHIPPED. All critical + high findings from last night's QA report resolved. Demo should now be browser-safe (needs live verification next session). 71/71 pytest + clean Next build. Release gate still closed per Jeff's standing instruction — no video/deploy/submission work touched.

## TL;DR cold start (post-fix state)

1. `git pull origin nextjs-redesign` — top commit is the QA fix queue sprint
2. `pip install -r requirements.txt` + `cd frontend && npm install` (no new deps this session)
3. `.env` already has `MODEL_PROVIDER=google` + `GOOGLE_AI_STUDIO_KEY=...`
4. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001`
5. Terminal 2: `cd frontend && npm run dev`
6. **First thing to do next session:** run the live browser QA plan in `todo.md` to confirm the 4 previously-500 endpoints work end-to-end in Chrome (chat already verified — don't re-test that). TestClient + typecheck + build all green, but per MISTAKE #5 that's not the same as a browser.

## What shipped this session

All 8 findings from the "fastest → biggest" queue in the previous HANDOFF landed:

| # | Finding | Fix location |
|---|---|---|
| 7 | Dashboard AbortController regression | `frontend/src/app/page.tsx` — added `ac.signal.aborted` guard before setState |
| 11 | Spanish letter placeholder signature | `prompts/templates.py` + `agents/material_forge.py` — `teacher_name` threaded with "use this exact name" instruction, default `Ms. Rodriguez` |
| 6 | IEP extraction dup pages 1+2 | `agents/iep_extractor.py::_merge_pages` — dedupe by normalized description prefix, not goal_id |
| 3 | Alert label classifier collapsed 3 outcomes | `backend/routers/alerts.py::_classify_goal` — emits `declining / plateau_below / plateau_at_target` with matching titles/details/actions |
| 2 | Alert ids non-deterministic → 404 on analyze | `backend/routers/alerts.py::_stable_alert_id` — sha256 of `{student}_{goal}_{label}` |
| 8 | Alert `severity` always null | Rolled into the classifier refactor (`high/medium/low`) |
| 4 | `first_then` renderer missing | `frontend/src/components/materials/FirstThenView.tsx` NEW — FIRST/arrow/THEN/teacher-notes cards with react-markdown |
| 5 | Chat SSE whitespace concat bug | `backend/routers/chat.py::_sanitize_stream_chunk` — strips tags without `.strip()`, preserves inter-chunk spaces |
| 1 | **Next.js proxy kills long Gemma calls** | `backend/routers/_sse.py::run_streaming_job` NEW — runs blocking Gemma in `asyncio.to_thread` with 4s heartbeats; new streaming endpoints `/analyze/stream`, `/upload/stream`, `/generate/stream`; frontend consumers via `frontend/src/lib/sseJob.ts::consumeSseJob<T>` NEW |

Non-streaming originals retained for TestClient smokes.

## 4 findings deferred (low impact)
- Finding 9 — chat send button doesn't react to programmatic `fill` (automation only)
- Finding 10 — `/sw.js` 404 on every load (console noise)
- Finding 12 — bilingual letters are independent generations, not translations of the approved EN letter (still good content, just less student-specific color)
- (Finding 11 was LOW but was wedge-able in 10 minutes so it shipped)

## Verification done
- `python -m pytest tests/ -q` → 71/71 pass
- `cd frontend && npx tsc --noEmit` → clean
- `cd frontend && npx next build` → compiles in 17.3s, TS checks pass, 5 pages generated
- Python sanity: `_classify_goal` on Amara G2 (45/42/40, target 70) → `declining`; Maya G1 (80/80/80, target 80) → `plateau_at_target`; improving 30→60 no alert; stable ids match across calls
- Python sanity: `_merge_pages` with duplicate goals across pages 1+2 → 3 unique goals, 3 accommodations, 3 interests (was 5/4/4 in old code)

## Verification NOT done (MUST DO next session)
Per MISTAKE #5: TestClient + typecheck + build are not a browser. The 4 endpoints that were 500ing in last night's QA need to be re-driven through real Chrome:
1. Dashboard → alert card → Why? → watch heartbeat → thinking trace unfolds
2. Add Student → upload `data/sample_iep/amara_iep_2025.pdf` → watch heartbeat → extraction card with 3 goals
3. MaterialViewer on Maya parent letter → ES → watch heartbeat → letter rewrites with `Ms. Rodriguez` signature
4. MaterialViewer on Maya first_then draft → renders FIRST/THEN cards, not raw markdown

Use `browse` or `chrome-devtools-mcp`. Expected new behavior: instead of a 40s silent spinner then 500, you should see an immediate "Thinking…" / "Extracting…" / "Generating…" message that holds the socket warm, then the result lands at ~30-75s.

## Docs that reference the old 12-finding state
- `docs/qa-reports/qa-report-classlens-2026-04-11.md` — still accurate as the *pre-fix* snapshot. Do not rewrite; add a new QA report after the browser verification pass instead.
- `todo.md` — updated this session to mark 8 items checked and park the 4 deferred items.
- `MISTAKES.md` — no new entry needed; MISTAKE #5 already covers the "TestClient ≠ browser" lesson.

---

## Previous session (very-late-night 2026-04-11) — Live browser QA pass

### ⚠️ STOP — read this before the next code change

**The demo is not browser-safe right now.** The Gemma-4 backend produces outstanding clinical content, but the Next.js dev proxy drops every non-streaming long-running Gemma call at ~30s with `socket hang up / ECONNRESET`. Backend logs `200 OK`; browser gets `500`. Impact:

| Endpoint | Browser | Backend | Impact |
|---|---|---|---|
| `POST /api/chat/stream` | ✅ 200 | ✅ 200 | Works — SSE keeps socket warm |
| `POST /api/alerts/{id}/analyze` | ❌ 500 | ✅ 200 | Feature #3 "Why?" dead in browser |
| `POST /api/documents/upload` | ❌ 500 | ✅ 200 | Feature #1 IEP extraction dead in browser |
| `POST /api/materials/generate` | ❌ 500 | ✅ 200 | Feature #4 + #5 + Sprint 4 dead in browser |

**The fix and the feature upgrade are the same fix:** stream every Gemma endpoint like `/api/chat/stream` does. That converts "40s spinner → response" into "reasoning unfolds live" which is the actual sales pitch for thinking mode. See `docs/qa-reports/qa-report-classlens-2026-04-11.md` for the full finding list and prioritized fix queue.

Do NOT record the demo video until the proxy/streaming issue is resolved. Do NOT claim the features work end-to-end in the writeup until browser-path fixes land. The backend tests pass; the browser tests don't.

## TL;DR cold start (post-QA state)

1. `git pull origin nextjs-redesign` — latest commit is the QA-docs bundle on top of `6cad487`
2. Read `docs/qa-reports/qa-report-classlens-2026-04-11.md` **first** — 12 findings with repro steps, screenshots in `.gstack/qa-reports/screenshots/` (local, gitignored)
3. `pip install -r requirements.txt` + `cd frontend && npm install` (no new deps this session)
4. `.env` already has `MODEL_PROVIDER=google` + `GOOGLE_AI_STUDIO_KEY=...`
5. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001`
6. Terminal 2: `cd frontend && npm run dev`
7. http://localhost:3000 — dashboard works, student pages work, cached materials work, chat stream works. Why? buttons, material generation, and IEP upload all return browser-side 500 until the proxy bug is fixed.
8. Tests still 71/71 pytest + 19/19 feature smoke (both run against the backend directly via TestClient, so they bypass the proxy and say everything's fine — do not trust them for browser-path claims).

## Session log (very-late-night 2026-04-11) — Live browser QA pass

**Trigger:** Jeff directed a full Chrome-driven UI test from a special ed teacher's perspective. Used chrome-devtools-mcp to drive a real Chrome browser through the 25-step plan a QA planner agent produced, evaluating both functionality and content quality "as a teacher."

**Phases executed:**
1. Dashboard + student navigation — ✅ clean
2. "Why?" thinking trace on alerts — **broken in browser** (500), excellent on backend
3. Chat SSE streaming — ✅ works, content is exceptional, whitespace bugs
4. IEP PDF extraction — **broken in browser** (500), works on backend with a dedup bug
5. All 7 material types — cached ones render fine, new generation 500s
6. Bilingual parent comms — backend works, ES is warm/native, UI toggle 500s
7. Work capture + final sweep — sweep only (work upload hits the same proxy bug)

**Report and evidence:**
- `docs/qa-reports/qa-report-classlens-2026-04-11.md` — **66/100 health score, 12 findings, prioritized fix queue** (committed)
- `.gstack/qa-reports/screenshots/*.png` — 7 screenshots of key states (local-only, gitignored)
- `.gstack/qa-reports/*.json` — evidence blobs: Maya G1 thinking trace, Amara G2 thinking trace, Amara IEP extraction, Maya ES parent letter (local-only, gitignored — regenerate with the commands in the report if needed)

### The 12 findings at a glance
| # | Sev | Category | One-liner |
|---|---|---|---|
| 1 | CRITICAL | Proxy | Next.js dev proxy kills 3/4 Gemma endpoints — only SSE survives |
| 2 | CRITICAL | State | Alert ids non-deterministic across `/api/alerts` fetches → 404 on analyze |
| 3 | HIGH | Content | All alerts labeled "plateaued" regardless of decline/target-met/plateau |
| 4 | HIGH | UI | `first_then` material has no frontend renderer — raw Markdown dumped |
| 5 | MEDIUM | UI | Chat SSE whitespace loss (`to40%`, `investedin`, `Notepad"with`) |
| 6 | MEDIUM | Content | IEP extraction duplicates every field (6 goals = 3 twice from page merge) |
| 7 | LOW | Perf | Dashboard AbortController regression — double-fetches in Strict Mode |
| 8 | MEDIUM | Schema | Alert `severity` field always `null` |
| 9 | LOW | UX | Chat send button stays disabled after programmatic input fill |
| 10 | LOW | Perf | `/sw.js` 404 every page load |
| 11 | LOW | Content | Spanish letter has `[Nombre del Maestro/a]` placeholder; EN has real name |
| 12 | LOW | Content | Bilingual = independent generations, ES drops student-specific signals |

### Content quality — teacher verdict
**Every piece of generated content is exceptional.** Highlights captured in the report:
- Amara G2 thinking trace names the "intervention resistance phenomenon" and distinguishes "losing ability to speak vs losing will to engage" — BCBA supervisor framing
- Amara MHA chat response proposes three interventions with cross-goal awareness (G2 social intervention ties back to G1 inference struggles)
- Maya first_then board weaves Jurassic World + deep purple + counting + proprioceptive sensory input into one coherent card (content 10/10, renderer 0/10)
- Maya EN parent letter says "raptor greeting at home — Maya practiced greeting peers like Blue greets her pack"
- Maya ES parent letter uses culturally-native phrasing ("Querida familia de Maya" / "Con cariño") with specific data

The model choice (Google AI Studio Gemma 4 31B) is **absolutely vindicated**. The content is the strongest part of the product. The wire layer is the weakest.

### Prioritized fix queue (~5 hours total to browser-safe)
1. Render a `FirstThenView.tsx` component (~30 min) — Finding 4
2. Fix alert label classifier to emit `declining | plateau_below | plateau_at_target | improving` (~20 min) — Finding 3
3. Stabilize alert ids by hashing `{student_id}_{goal_id}_{week}` (~20 min) — Finding 2
4. Dedupe IEP extraction merge in `agents/iep_extractor.py` (~15 min) — Finding 6
5. Fix chat whitespace concat in `frontend/src/hooks/useChat.ts` (~30 min) — Finding 5
6. Restore dashboard AbortController in `app/page.tsx` (~10 min) — Finding 7
7. Thread teacher name into the ES prompt template (~10 min) — Finding 11
8. **The big one:** stream `/api/alerts/analyze`, `/api/documents/upload`, `/api/materials/generate` like `/api/chat/stream` does (~2-3h) — Finding 1. Fixes the demo blocker AND upgrades the demo surface (reasoning unfolds live instead of 40s spinner).

### What the demo video can safely show today
1. Dashboard load — clean, correct counts
2. Student navigation — Maya/Amara/Jaylen all load fine
3. Chat asking Gemma about Amara's G2 — MHA-themed interventions stream live (but warn about or fix Finding 5 whitespace first)
4. Viewing cached approved materials (tracking sheet, parent letter EN)
5. G3 count-based target display (`≤1/day`)

### What the demo video cannot safely show today
1. Clicking "Why?" on any alert (500)
2. Uploading an IEP PDF in Add Student (500)
3. Generating a new material of any type (500)
4. Live bilingual toggle on a parent letter (500 — fires materials/generate)
5. Viewing a `first_then` board even from cache (renderer missing)

### Working-tree cleanup done this session
- Reverted `data/alerts/active_alerts.json` (backend write during testing, not a real change)
- Deleted `data/materials/maya_2026/parent_comm_G1_2026-04-11.json` (my ES-test artifact, not approved content)
- Moved the QA report from `.gstack/qa-reports/` (gitignored) to `docs/qa-reports/` (tracked)
- Screenshots + evidence JSONs remain in `.gstack/qa-reports/` local-only

---

## Previous session (late-evening 2026-04-11) — Judge-Appeal Feature Sprint
**Status at that point:** SHIPPED. 5 features + provider flip committed as `6cad487` and pushed to origin. 71/71 pytest + 19/19 live feature smoke + clean Next.js build. Release gate still closed per Jeff's instructions — no video/deploy/submission work touched.

## TL;DR cold start (post-commit state)

1. `git pull origin nextjs-redesign` — latest commit is `6cad487` ("Ship 5 judge-appeal features + flip to Google AI Studio")
2. `pip install -r requirements.txt` (new dep: `pymupdf` for IEP extraction PDF→PNG rendering) + `cd frontend && npm install`
3. Copy `.env.example` → `.env`. Canonical provider is now **Google AI Studio**: set `MODEL_PROVIDER=google` + `GOOGLE_AI_STUDIO_KEY=...`. OpenRouter and Ollama are fallback-only — see CLAUDE.md "Model:" section for the architectural trade-offs.
4. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001` (8001 is canonical)
5. Terminal 2: `cd frontend && npm run dev`
6. http://localhost:3000 — dashboard loads, 7 students, 5 alerts, all 5 new features live.
7. Tests: `python -m pytest tests/ -q` (71/71) · `python scripts/feature_smoke.py` (19/19 live against real Gemma 4 31B) · `python scripts/cold_boot_smoke.py` (original live smoke, needs live backend) · `python scripts/provider_ab.py` (if revisiting the provider decision)

## What to know in 60 seconds

- **Five judge-appeal features shipped this session.** All lying docstrings fixed (chat.py claimed streaming, documents.py claimed extraction — both now true).
- **Provider is Google AI Studio.** Only provider with working native function calling AND thinking mode. OpenRouter 404s on tool use. Ollama has no thinking code path in `gemma_client.py`. Dev machine is GPU-less so Ollama CPU inference is 10× slower than Google anyway — ~30 min for the 4-feature smoke vs Google's ~3 min.
- **Thinking trace is the demo centerpiece.** Click "Why?" on any alert card → `/api/alerts/{id}/analyze` runs ProgressAnalyst → UI reveals ~4,000-5,000 chars of Gemma's reasoning in a collapsible panel. Architecturally invisible on any other provider.
- **IEP extraction works end-to-end.** Drop a PDF in Add Student → pymupdf renders pages → Gemma multimodal + function calling extracts `{student_name, grade, asd_level, iep_goals[], accommodations[]}` → UI shows an "Extracted from IEP" card.
- **Chat streams live via SSE.** `fetch` + `ReadableStream` + `TextDecoder` consumer (not EventSource — needed POST with body).
- **Bilingual parent comms.** Language toggle (EN/ES/VI/ZH) in MaterialViewer, only appears for parent_comm material type.
- **First-Then board.** Was orphaned, now reachable — brings total output types to 7.

## Key files added this commit (for archaeology)

- `agents/iep_extractor.py` — IEP multimodal extraction agent, follows the `vision_reader.py` pattern
- `scripts/feature_smoke.py` — 19-assertion live smoke test for the 5 features via TestClient
- `scripts/provider_ab.py` — 3-way provider comparison (run with any provider loaded)
- `scripts/ollama_e4b_solo.py` — one-off clean-room Ollama test (reference)
- Modified: `backend/routers/chat.py` (+/stream endpoint), `backend/routers/alerts.py` (+/analyze), `backend/routers/documents.py` (real extraction), `backend/routers/materials.py` (first_then + language), `core/gemma_client.py` (generate_stream), `agents/material_forge.py` (language param), `prompts/templates.py` (IEP extraction prompts + language field), `schemas/tools.py` (EXTRACT_IEP_CONTENT tool)
- Frontend modified: `frontend/src/hooks/useChat.ts` (SSE consumer), `frontend/src/components/student/AlertBanner.tsx` ("Why?" button + thinking panel), `frontend/src/components/materials/MaterialViewer.tsx` (language toggle), `frontend/src/components/materials/ParentLetterView.tsx` (lang attribute), `frontend/src/app/student/new/page.tsx` (IEP extraction consumer)

## What's still unstaged in the working tree

- `.claude/` — local Claude Code tooling, not committed (add to .gitignore if it bothers you)
- `RESEARCH-BRIEF.md` — 1-page project brief Jeff asked for to pass to another LLM for research evaluation. Intentionally uncommitted since it's a transient artifact. Delete it when you're done with it, or commit it if you want to preserve the snapshot.

## What's NOT in this commit

- Release/deploy/video/submission work — release gate explicitly still closed per Jeff's standing instruction. No Sprint 6 work until he says the project is done.
- Ollama thinking-mode support — `_ollama_generate_with_thinking` would need a `<thinking>...</thinking>` tag protocol and parser. ~50 lines, worth ~1 hour, worth doing only if you later move the demo to a GPU-equipped machine and want thinking mode visible on the local path too.
- Pydantic v1 → v2 validator migration — the 13 deprecation warnings in pytest are pre-existing and will become errors when pydantic v3 drops. Separate cleanup task.

---

---

## Provider decision (2026-04-11 late-late evening)

After shipping the 5 judge-appeal features, ran a 3-way A/B comparing OpenRouter (`google/gemma-3-27b-it`), Google AI Studio (`gemma-4-31b-it`), and local Ollama (`gemma4:e4b`, `gemma4:26b`). Scripts: `scripts/provider_ab.py` (3-way run) and `scripts/ollama_e4b_solo.py` (clean-room Ollama with zero contention).

**Decision: `MODEL_PROVIDER=google`** — flipped in `.env` this session, CLAUDE.md tech-stack section rewritten to match.

Why:
- **Only provider with working native function calling.** OpenRouter's `google/gemma-3-27b-it` returns 404 "No endpoints that support tool use" and forces every tool-based agent (VisionReader, IEPMapper, MaterialForge, IEPExtractor) onto the `_parse_fallback` text-JSON path. Google's native `types.Tool(function_declarations=[...])` with `AUTO` mode works out of the box.
- **Only provider with working thinking mode.** Google returned a **6,191-char reasoning chain** on the Amara G2 alert analysis; both OpenRouter and both Ollama variants returned `thinking=0` because `gemma_client.py::generate_with_thinking` has no non-Google code path (it falls through to `_openai_generate`). The "Why?" button on `AlertBanner.tsx` is architecturally dependent on Google until/unless we add a `<thinking>` tag protocol for the OpenAI-compat backends.
- **Branding truth.** CLAUDE.md was claiming "Google Gemma 4" while actually serving Gemma 3 27B via OpenRouter. Now it's actually Gemma 4 31B (real model, not a proxy relabel). For a "Gemma 4 Good Hackathon" submission this matters — judges who read code will see the model ID match the branding.
- **Speed, even with latency.** Google ran the full 4-feature smoke in ~3 minutes. OpenRouter ran it in ~3-5 minutes. Ollama e4b ran it in ~30 minutes solo (43 minutes under contention). Per-call latency on Google is 30-75s per structured call, which is acceptable for a teacher-in-the-loop workflow.
- **Cost.** Google AI Studio free tier (15 RPM / 1,500 req/day) is more than enough for dev + a recorded demo + a few judge sessions.

Why not Ollama (on this machine):
- Dev machine is Windows Server 2022 headless, no GPU (wmic reports only Microsoft Remote Display Adapter + Microsoft Basic Display Adapter). Ollama runs everything on CPU: `gemma4:e4b` at ~5 tok/s, `gemma4:26b` at ~1-2 tok/s.
- Solo (zero contention) measurements on e4b: chat TTFB 80s, IEP extraction **761s (12.7 min)**, alert analysis **558s (9.3 min)**, Spanish letter **451s (7.5 min)**. Total ~30 min for 4 features. Not viable for a live demo.
- Ollama e4b IEP extraction quality matched Google (3 goals, demographics populated) — the model is fine, the hardware isn't.
- Ollama 26b extracted **more** content (10 goals vs Google's 3, 18 accommodations vs 6) but lost on Spanish quality (704 chars vs 1993) and still had zero thinking.
- On a GPU-equipped demo machine, Ollama 26b becomes viable again and the equation flips (real Gemma 4 branding + free + offline + FERPA-friendly narrative). Code is ready to support that: set `MODEL_PROVIDER=ollama` and `OLLAMA_MODEL=gemma4:26b`.

Remaining architectural gap worth tracking: Ollama thinking-mode support is a ~50-line follow-up (prompt-based `<thinking>...</thinking>` tag protocol parsed in `_ollama_generate_with_thinking`). Not needed for Google path but useful if you later move to GPU box.

---

---

## This session (late evening 2026-04-11) — Judge-Appeal Feature Sprint

**Trigger:** Jeff asked what features remained untested / under-demonstrated that would strengthen the Gemma 4 hackathon submission outside of video work. Audit surfaced two docstring lies (chat.py claiming streaming, documents.py claiming IEP extraction) and three invisible Gemma capabilities (thinking mode, multilingual, long-context PDF). Jeff ordered: "Fix that nonsense right now. Then execute 1-5."

**Approach:** Phase A inline (shared infra + tiny fix), Phase B four parallel subagents (one per feature), Phase C live smoke. Single session.

### Features shipped

**#1 — Real IEP PDF auto-extraction** (`backend/routers/documents.py`, `agents/iep_extractor.py` NEW, `schemas/tools.py` +EXTRACT_IEP_CONTENT, `prompts/templates.py` +IEP_EXTRACTOR_*, `frontend/src/app/student/new/page.tsx`, `requirements.txt` +pymupdf)
- The endpoint no longer lies. Uploads render PDF pages 1-2 to PIL images via pymupdf at 2x zoom, call Gemma multimodal with function calling against EXTRACT_IEP_CONTENT tool, merge per-page results, return structured `extraction: {student_name?, grade?, asd_level?, communication_level?, interests, iep_goals[], accommodations[]}`.
- Frontend reads the extraction response and renders an "Extracted from IEP" card below the Profile Preview in the Add Student flow. Auto-fills name/grade/level into the preview state.
- Degrades gracefully: if pymupdf fails to import, the model call errors, or rendering fails, returns `extraction: {iep_goals: [], accommodations: [], notes: "..."}` so the upload flow never breaks.

**#2 — Chat SSE streaming** (`backend/routers/chat.py`, `frontend/src/hooks/useChat.ts`)
- Added `POST /api/chat/stream` returning `StreamingResponse` with `text/event-stream`, SSE frames `data: {"delta": "..."}\n\n` followed by `{"done": true}`. Per-chunk HTML sanitization. Mock fallback preserved for no-key dev.
- Frontend `sendMessage` rewritten to use `fetch` + `ReadableStream` + `TextDecoder` (NOT EventSource — POST with body). Characters appear live; loading indicator yields on first chunk. History ref updated once after stream completes.
- Module and handler docstrings rewritten to match reality.
- Old `/api/chat` endpoint retained for backwards compat.

**#3 — Thinking-trace UI for alerts** (`backend/routers/alerts.py`, `frontend/src/components/student/AlertBanner.tsx`)
- New `POST /api/alerts/{alert_id}/analyze`. Regenerates alerts from live student data to resolve id → `{student_id, goal_id}`, instantiates `ProgressAnalyst` via `_get_progress_analyst()` (follows materials.py `_get_forge` pattern), calls `analyst.analyze(student_id, goal_id)` which drives `generate_with_thinking`, sanitizes output, returns `{alert_id, goal_id, student_id, thinking, output}`.
- AlertBanner now has a "Why?" button (Brain icon) alongside "Generate Materials" and "Ask Assistant". Click reveals a collapsible panel showing pulsing loader → "Gemma's reasoning" (italic/muted, only if non-empty) → "Analysis" (body text). Retry on error. Results cached per alert id in component state.

**#4 — First-Then board** (`backend/routers/materials.py`)
- Added `"first_then"` to the `material_type` enum and routed it to `forge.generate_first_then(student_id, goal_id)` (the MaterialForge method already existed and was orphaned). Now the demo has all 7 output types reachable from the UI, matching CLAUDE.md's claim.

**#5 — Bilingual parent communications** (`agents/material_forge.py`, `prompts/templates.py`, `backend/routers/materials.py`, `frontend/src/components/materials/MaterialViewer.tsx`, `frontend/src/components/materials/ParentLetterView.tsx`)
- `language: str = "en"` threaded through: `GenerateRequest` → `forge.generate_parent_comm(student_id, goal_id, language=...)` → prompt template's new `{language_name}` field → stored on material record.
- Prompt template has an explicit "Write the ENTIRE letter in {language_name}. Greetings, highlights, try-at-home, closing — everything. Use culturally natural phrasing…" instruction block.
- MaterialViewer shows a 4-button language toggle (EN / ES / VI / ZH) ONLY when material_type === "parent_comm". Selecting a language re-calls the generate endpoint and swaps `liveMaterial` state in place. Active button has filled variant + aria-pressed.
- ParentLetterView accepts optional `language` prop, sets `lang={language}` on the root div for screen readers, explicit `dir="ltr"` for future RTL safety.

### Infrastructure added

- `core/gemma_client.py` — new `generate_stream()` method with `_google_generate_stream` (via `generate_content_stream`) and `_openai_generate_stream` (via `stream=True`) implementations. `Iterator[str]` of text chunks. Used by `/api/chat/stream`.
- `scripts/feature_smoke.py` — NEW. Live smoke test for all 5 features via FastAPI TestClient against real Gemma. 19 assertions covering streaming, alert analysis, bilingual Spanish markers, IEP extraction, first-then. Parallels `scripts/cold_boot_smoke.py` but runs in-process.

### Verification

- `python -m pytest tests/ -q` → **71/71 passed** (13 pre-existing Pydantic v1-validator deprecation warnings, unrelated)
- `cd frontend && npx next build` → **compiled successfully**, TypeScript clean, all 5 routes generated
- `python scripts/feature_smoke.py` → **19/19 passed** against live OpenRouter Gemma
  - SSE: 51 delta frames, 197 accumulated chars, terminal done frame received
  - Thinking trace: output 571 chars, thinking empty (expected on OpenRouter)
  - Bilingual Spanish: 5 language markers detected, letter preview starts with `"estimados padres de maya,"`
  - IEP extraction: 0 goals, 7 accommodations from `amara_iep_2025.pdf`
  - First-Then: 1398 char content body

### IMPORTANT finding surfaced by smoke run

OpenRouter's `google/gemma-3-27b-it` returns **404 for tool use** — every function-calling agent in the project (VisionReader, IEPMapper, MaterialForge, IEPExtractor) is hitting the `_parse_fallback` text-JSON path instead of real function calling. This has been the situation since OpenRouter was wired up — not a new regression. The fallback works, but:
- IEP extraction degrades to accommodations-only on some PDFs because the text-parse can't reconstruct nested goal arrays as reliably as native function calling.
- Thinking mode is empty on OpenRouter because the provider doesn't expose reasoning chains (documented behavior in `gemma_client.py::generate_with_thinking`).

**Fix available without code change:** set `MODEL_PROVIDER=google` in `.env` (the `GOOGLE_AI_STUDIO_KEY` is already set). Google AI Studio supports real function calling AND non-empty thinking traces. Every tool-based agent will light up with richer structured output, and the "Why?" button on alerts will actually show Gemma's thinking. This is a 1-line config change that would materially improve the demo fidelity on #1 and #3.

Recommend Jeff test both providers on the same PDF to decide which to ship.

### What Jeff should manually verify

1. `MODEL_PROVIDER=google` experiment — restart backend, re-hit `/api/documents/upload` with a mock IEP PDF, confirm goals populate. Then `/api/alerts/{id}/analyze` and confirm thinking is non-empty.
2. Browser visual confirmation of #2 (chat streaming) and #3 (AlertBanner "Why?" button) — TestClient proved the wire protocol but not the animation.
3. Browser visual confirmation of #5 language toggle — open a parent letter in MaterialViewer, click ES, confirm the letter body swaps to Spanish in place.
4. Browser visual confirmation of #1 Add Student flow — drop a mock IEP PDF, see the "Extracted from IEP" card populate.

### Changes are unstaged

Nothing committed. Review and commit when ready. Suggest one bundled commit because all 5 features + the gemma_client streaming infra form a coherent "no more lying code" milestone.

---

## Previous session (evening 2026-04-11)

---

## What happened this session (evening 2026-04-11)

**Scope:** Sarah needed help reviewing the synthetic data before video recording. Built a dev-aid bundle she can review and mark up.

**Created:** `sarah_review_bundle/` (gitignored — not a shipped feature)
- `README.md` — index + 5 specific feedback questions for Sarah
- `student_dockets/` — 7 markdown dockets (one per student: profile snapshot, interests, sensory profile, IEP goals with current status, teacher observations, strategies working/not working, open questions)
- `sample_outputs/` — 12 realistic samples covering all 7 Material Forge output types:
  - Lesson plan (Maya G2), tracking sheet (Ethan G1), social story (Jaylen fire drill), visual schedule (Marcus bathroom routine), first-then board (Maya math)
  - Parent emails: Amara G1 celebration + Amara G2 concern (same student, same day), Marcus big-slide milestone
  - Admin reports: Sofia monthly (positive case) + Ethan monthly (plateau w/ OT recommendation)
  - Progress Analyst alert (Amara G2 regression with thinking trace)
  - Full pipeline output (Maya math worksheet: vision → IEP mapper → progress analyst end-to-end)

**How to share with Sarah:** zip `sarah_review_bundle/`, email or drop in Drive. Self-contained Markdown.

**Code/test changes:** None. Only `.gitignore` was updated to exclude `sarah_review_bundle/`.

**Next session pickup:** Either (a) wait for Sarah's feedback on the bundle before making prompt-template adjustments, or (b) start Sprint 6 groundwork (video script timing, deploy target) while waiting. Release gate still blocks Sprint 6 proper.

---

## Previous session (afternoon 2026-04-11)

Created 9 new sample work artifacts + matching precomputed JSONs to cover the 4 previously-empty students (Amara, Ethan, Lily, Marcus) and top up Sofia. Every artifact is goal-mapped to the student's actual IEP with a realistic progress analysis narrative.

**New artifacts:**
- `amara_inference_probe` → G1 reading comprehension, 70% target met (MHA character mapping strategy)
- `amara_social_tracker` → G2 social regression, 30% **ALERT** (5 consecutive declines, below baseline)
- `ethan_spontaneous_speech` → G1 SLP tally, 70% target met (weather + number-7 motivators)
- `ethan_handwriting_probe` → G2 OT probe, 45% **ALERT** (4-session plateau, intervention saturation)
- `lily_conversation_log` → G1 pragmatic language, 80% target met (internalized body-clue checklist)
- `lily_coping_strategy` → G3 self-regulation, 70% (5/5 intensity wall identified)
- `marcus_aac_request_log` → G1 AAC, 80% (multimodal verbal+AAC emerging)
- `marcus_playground_log` → G3 adapted PE, 80% (big slide + crowd tolerance)
- `sofia_peer_conversation_tally` → G1 social, 90% (group project anchor, credit-sharing)

**Two alert scenarios** deliberately baked in so Progress Analyst has realistic failure-mode data for demo:
- Amara G2: **declining** trend, 5 consecutive weekly drops, intervention actively rejected by student
- Ethan G2: **plateau** trend, 4 consecutive sessions at 45%, specific OT recommendation (vibrating pen + bursts)

**Code changes:**
- `scripts/generate_sample_work.py` — added 9 generator functions, Windows font fallback (`_load_font` helper trying Arial / Segoe UI / DejaVu / PIL default), fixed Linux-hardcoded `main()` path to use `Path(__file__)` resolution, added `--extended` flag for regenerating just the new artifacts, added `_draw_table` helper
- 9 new PNGs in `data/sample_work/` (~80-100KB each, cleanly rendered Arial)
- 9 new JSONs in `data/precomputed/` following canonical schema from `jaylen_pecs_log.json` (transcription + goal_mapping + analyses with thinking narrative)

**Verification:**
- `python -m pytest tests/ -q` — **71/71 pass** (no regressions)
- Pipeline cache-hit test — all 9 artifacts resolve via `_load_precomputed`, goal mappings propagate, alert flags surface correctly
- Spot-checked 2 PNGs visually (amara_inference_probe, ethan_handwriting_probe) — fonts, colors, layout all clean
- Every new JSON validated: parses, `image_path` resolves, `goal_id` references the student's actual IEP goal

---

## Earlier sessions (2026-04-11)
Morning: Path B hardening + live browser QA fixes. Afternoon: 9 new synthetic artifacts + precomputed JSONs to cover all 7 students. Release gate re-open for Jeff.

---

## TL;DR for a cold start

1. Clone, `pip install -r requirements.txt`, `cd frontend && npm install`.
2. Copy `.env.example` → `.env`, set `MODEL_PROVIDER=openrouter` + `OPENROUTER_API_KEY=...`.
3. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001` — **8001 is canonical**, don't use 8000 (ulana.main squats it on the dev machine).
4. Terminal 2: `cd frontend && npm run dev` — frontend auto-proxies `/api/*` to 8001.
5. Open http://localhost:3000 — dashboard, 7 students, real Gemma via OpenRouter, all 11 sample PNGs cache-hit the pipeline.
6. Tests: `python -m pytest tests/ -q` (71 green) and `python scripts/cold_boot_smoke.py` (8/8 green against a live backend).

Everything below is context for *why* things are the way they are.

---

## What happened this session (2026-04-11)

Three phases in one sitting:

### Phase 1 — Path B hardening (commits `d46c898`, `d700d7c`)
Project Manager + QA Manager sub-agents reviewed Sprints 1–5 and flagged that "35/35 tests pass" was all-mock — zero coverage on the FastAPI routers, the `load_dotenv` fix, image upload, or the real OpenRouter API path. Chose Path B (one hardening week) before Sprint 6.

- **Precomputed cache gap closed** — 3 new artifacts + 3 mis-mapped existing ones fixed (Maya copy-paste bugs, wrong goal_ids).
- **Security pass** — new `backend/upload_utils.py`: filename sanitize, path-traversal blocks on student IDs, 10 MB cap, extension allowlist. Capture + documents routers rewritten to use it. CORS tightened (opt-in regex, explicit method/header lists). Production→test coupling (`MockGemmaClient` import) removed from the happy path.
- **HTML sanitization** — `_sanitize_model_text` now drops `<script>`/`<style>` blocks with bodies and strips any tag with attributes. Old regex only caught 7 hard-coded tag names.
- **Port 8001 canonicalized** — frontend `next.config.ts` default, CLAUDE.md tech stack rewritten for Next.js + FastAPI reality, HANDOFF + todo updated.
- **Synthetic test content** — sub-agent generated 4 new work artifacts (Maya + Jaylen), 4 matching precomputed JSONs, 2 mock IEP PDFs, extended `scripts/generate_sample_work.py` + new `scripts/generate_sample_ieps.py`.
- **Test coverage** — `tests/test_backend_security.py` added 32 unit tests (upload validation + sanitization). Total 67/67.
- **Live cold-boot smoke** — `scripts/cold_boot_smoke.py` runs real HTTP against a fresh uvicorn: health, students, **real OpenRouter chat round-trip**, capture happy path (new cache entry), 3 validation rejections. 8/8 green.
- **MISTAKES.md seeded** — 4 lessons from Sprints 1–5 per global CLAUDE.md mandate.

### Phase 2 — Live browser QA (Chrome DevTools MCP)
Started real backend + frontend, drove Chrome through the actual UI. Logged everything the user would do: dashboard load → student page → real chat (Gemma via OpenRouter returned Maya-specific response referencing "Blue the raptor" and correctly identifying the 75% G2 plateau) → upload `maya_reading_comprehension.png` → full pipeline result rendered as a chat action card → navigate to Jaylen → upload `jaylen_turn_taking_tally.png` → Gordon/Percy transcription + G3 match. Zero console errors, zero failed network requests. Screenshots in `data/documents/qa_screenshots/` (gitignored).

Surfaced 3 bugs, two real fixes and one product decision.

### Phase 3 — Bug fixes (commit `<hash>` — this session's commit)

1. **G3 count-based goal display** — Maya's G3 "reduce outbursts to 1 or fewer per day" was rendering as `Target: 1%` which is meaningless. Backend now annotates goals with `target_unit`, `target_value`, `target_display`. Count-based goals (`target ≤ 10` + description contains one of "fewer/reduce/outburst/incident/per day") render as `≤1/day` with the progress bar normalized to 100. Percentage goals unchanged. New unit tests in `test_backend_security.py::TestAnnotateGoalTarget`.

2. **React Strict Mode double-fetch** — every `useEffect` data-loader was firing twice in dev. Added `AbortController` to 5 call sites: `app/page.tsx`, `app/student/[id]/page.tsx`, `components/sidebar/StudentSidebar.tsx`, `components/student/RecentWork.tsx`, `components/student/MaterialsLibrary.tsx`. Verified in browser: first fetch now shows `ERR_ABORTED`, only the second reaches the backend. Half the network traffic in dev, correct production behavior guaranteed.

3. **Chat history not scoped to student** — switching from Maya to Jaylen kept Maya's conversation in the chat panel. `ChatProvider.setActiveStudent` now tracks the previous ID in a `useRef` and calls `clearHistory()` outside the setState updater before setting the new ID. Using the ref (instead of an updater callback) avoids Strict Mode double-invoking the side effect. Verified in browser: Maya's chat cleanly resets to welcome + "Now looking at Jaylen" when switching.

Also caught along the way:
- Latent bug in student page's context message: used stale `alerts.length` state instead of the just-loaded value, always showing "How can I help?" instead of the real alert count. Now uses local `studentAlerts` — verified rendering "2 alert(s) need attention" for Maya, "1 alert(s)" for Jaylen.
- `data/documents/` added to `.gitignore` (runtime upload state + QA screenshots — should never be committed).

---

## Current state

### What works end-to-end
- Dashboard loads with 7 students, 5 alerts, sessions counter
- Student navigation, chat (real OpenRouter Gemma 3 27B), work image upload → pipeline → structured chat action card
- 11 sample PNGs all precomputed — demo never waits on live API for capture
- 2 mock IEP PDFs for `/api/documents/upload` testing
- All 3 browser QA bugs fixed, zero console errors, zero failed network requests
- Backend + frontend boot cleanly on 8001/3000

### Test state (all green)
- `python -m pytest tests/ -q` — **71/71 pass** (was 35 at session start, added 32 security + 4 goal-annotation)
- `cd frontend && npx next build` — **0 errors** with Next 16.2.2 + Turbopack
- `python scripts/cold_boot_smoke.py` — **8/8 live checks** against real backend + real OpenRouter
- Browser QA (Chrome DevTools MCP) — **0 console errors, 0 failed requests** across the full user path on both Maya and Jaylen

### What's still open
- **Sarah's content** — still Sarah's job, in progress. Synthetic test content covers development/QA; Sarah's real content drives Sprint 6 video + profile validation.
- **Deploy target decision** — local + OpenRouter for testing; Streamlit/Kaggle submission form factor deferred until release gate opens. CLAUDE.md has been updated to reflect the Next.js + FastAPI active stack and the Streamlit dormant stack.
- **"Release ready" definition** — still needs Jeff's explicit criterion (demo-ready vs. production-ready).

---

## Release gate — still re-open for Jeff

**Path B hardening + browser QA both complete. Evidence for release readiness:**

Strong:
- Real unit tests on real code paths (71/71)
- Live cold-boot smoke proves real API round-trip (not just manual)
- Browser QA with Chrome DevTools walked through the golden path successfully
- All 3 browser-QA findings fixed and re-verified
- Security hardening on both upload endpoints + CORS
- Precomputed cache covers every sample artifact (no live-API fallthrough during demo)
- MISTAKES.md + CLAUDE.md aligned with reality
- Port 8001 baked in everywhere that matters

Remaining Jeff-only decisions:
1. Sarah's real student profiles/video segments ready?
2. What specific evidence would move you from "awaiting approval" to "approved"?
3. Once approved, Sprint 6 scope: deploy → video → writeup → Kaggle notebook → submit with buffer before 2026-05-18.

---

## Key file changes this session

| File | What changed |
|------|-------------|
| `backend/upload_utils.py` | NEW — shared upload validation (phase 1) |
| `backend/routers/capture.py` | Rewritten with upload_utils; removed test import from happy path |
| `backend/routers/documents.py` | Rewritten with upload_utils |
| `backend/routers/chat.py` | `_sanitize_model_text` helper; comprehensive HTML stripping |
| `backend/routers/students.py` | `_annotate_goal_target` helper; adds target_display/target_unit/target_value to each goal |
| `backend/main.py` | CORS tightened |
| `frontend/next.config.ts` | Default `API_URL` → `http://localhost:8001` |
| `frontend/.env.local.example` | NEW — documents the override |
| `frontend/src/app/page.tsx` | AbortController for dashboard fetches |
| `frontend/src/app/student/[id]/page.tsx` | AbortController; uses local studentAlerts for context msg |
| `frontend/src/components/sidebar/StudentSidebar.tsx` | AbortController |
| `frontend/src/components/student/RecentWork.tsx` | AbortController |
| `frontend/src/components/student/MaterialsLibrary.tsx` | AbortController |
| `frontend/src/components/student/GoalCard.tsx` | Renders `target_display` when present |
| `frontend/src/context/ChatContext.tsx` | Uses `useRef` to track previous student; clears chat on student switch |
| `data/precomputed/*.json` | 4 new, 3 Maya copy-paste bugs fixed |
| `data/sample_work/*.png` | 4 new synthetic artifacts |
| `data/sample_iep/*.pdf` | 2 new mock IEP PDFs |
| `scripts/generate_sample_work.py` | Extended with 4 new worksheet layouts |
| `scripts/generate_sample_ieps.py` | NEW — reportlab-based IEP PDF generator |
| `scripts/cold_boot_smoke.py` | NEW + expanded to 8/8 checks |
| `tests/test_backend_security.py` | NEW + 32+4 unit tests |
| `MISTAKES.md` | NEW — 4 seeded lessons |
| `CLAUDE.md` | Tech stack rewritten for Next.js + FastAPI reality |
| `HANDOFF.md` | This file |
| `todo.md` | Path B closed |
| `.gitignore` | Added `data/documents/` |

---

## Agent files for next session

`~/.claude/agents/project-manager.md` and `~/.claude/agents/qa-manager.md` are in place. They weren't hot-loaded this session (new agent files register on next restart), so this session used `general-purpose` with inlined personas. Next session they'll be directly invokable via `subagent_type: "project-manager"` and `subagent_type: "qa-manager"`.

---

## Commits on `nextjs-redesign` this session

```
<latest>  Fix G3 target display, AbortController, scope chat to student
d700d7c   Canonicalize port 8001 + expand synthetic test content
d46c898   Path B hardening: security, coverage, cache completion
783d355   Sprint 5 finalization: real Gemma API + image upload pipeline
```

All pushed to origin.
