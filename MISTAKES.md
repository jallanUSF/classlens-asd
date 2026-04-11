# MISTAKES.md — ClassLens ASD

Per global CLAUDE.md: when a bug takes more than 3 passes to fix, log it here with what happened, the root cause, and a prevention rule. Never repeat a documented mistake.

---

## 1. `load_dotenv()` not called in FastAPI routers

**What happened:** After wiring the Gemma API to the chat endpoint, chat responses kept falling back to the mock response. The `.env` file was correct, `GemmaClient` worked from a standalone script, but the backend router never saw the env vars.

**Root cause:** `dotenv.load_dotenv()` was called in `core/gemma_client.py` at import time, but FastAPI imports `core.gemma_client` lazily inside the request handler. At router-module import time (when uvicorn boots), the env vars had never been loaded, and whatever read them first got stale/missing values.

**Prevention rule:** Every FastAPI router that reads env vars (directly or via a downstream import) must call `load_dotenv()` at the top of the module. Do NOT rely on transitive dotenv calls from deeper modules.

---

## 2. Precomputed JSON copy-paste bugs — wrong goal IDs and wrong student

**What happened:** Three existing precomputed cache files (`maya_math_worksheet.json`, `jaylen_task_checklist.json`, `sofia_writing_sample.json`) all contained the same `progress_note` and `thinking` body — a narrative about Maya's Communication Goal G1 and the fire drill. Jaylen's file also had the wrong goal ID on the match (G1 instead of G2). Sofia's file matched G1 instead of G3. These would render nonsense in the student UI.

**Root cause:** The precomputed cache was bootstrapped by copying a single Maya example and lightly editing the top-level fields. The deep fields (`progress_note`, `thinking`, `goal_id`) were never updated per student.

**Prevention rule:** When creating precomputed or golden-file fixtures, every file must reference its own student by name in the body — not just in the filename or top-level ID. Add a sanity check: grep the precomputed files for student names and fail the build if any file contains another student's name.

---

## 3. File-upload endpoint accepted client-supplied filename without sanitization

**What happened:** The `/api/capture` and `/api/documents/upload` endpoints wrote uploaded files to `data/documents/{student_id}/{date}_{work_type}_{image.filename}` using the raw `UploadFile.filename`. A malicious filename like `../../.env` or `../other_student/x.png` would have escaped the target directory. `student_id` was also unvalidated and would accept `../etc` as a Form field. No file size limit; no MIME/extension allowlist.

**Root cause:** The early scaffolding focused on "make upload work for the demo" and skipped validation. The happy path worked, so nobody noticed until a retroactive security pass.

**Prevention rule:** Any endpoint that accepts a filename from a client must: (a) strip path components with `Path(name).name`, (b) replace unsafe chars, (c) validate an extension allowlist, (d) enforce a byte limit, (e) validate any student_id / path segment against `^[A-Za-z0-9_-]+$`. The backend ships a `backend/upload_utils.py` helper — use it, never hand-roll. Covered by `tests/test_backend_security.py`.

---

## 4. "35/35 tests pass" meant nothing for the code that actually changed

**What happened:** After the Sprint 5 finalization session, the HANDOFF claimed "35/35 tests pass, full end-to-end working." A skeptical QA review showed every test used `MockGemmaClient`, and zero tests covered the FastAPI routers, upload validation, HTML sanitization, or the `load_dotenv` fix. The green number provided false confidence for a release decision.

**Root cause:** The test suite was designed for the Streamlit-era agents/pipeline, not the new FastAPI/Next.js backend. Tests never got ported when the backend was added.

**Prevention rule:** Before trusting a "tests pass" claim for release readiness, grep the test suite for imports of the code that actually changed this session. If the changed module isn't imported anywhere in `tests/`, the test count is irrelevant to that change. For backend routers specifically: every new router needs at least one test that hits `TestClient(app)` or a live cold-boot smoke script. The project now has `scripts/cold_boot_smoke.py` for the live path.

---

## 5. Next.js dev proxy silently drops long-running FastAPI calls; `TestClient`-based "feature smoke" lied about browser behavior

**What happened:** After shipping 5 judge-appeal features and seeing 71/71 pytest + 19/19 feature smoke green, a live Chrome QA walk-through showed that `/api/alerts/{id}/analyze`, `/api/documents/upload`, and `/api/materials/generate` all return **500 Internal Server Error** in the browser. Backend logs `200 OK`. Frontend dev log shows `Failed to proxy http://localhost:8001/... Error: socket hang up ECONNRESET`. The Turbopack dev server's internal proxy tears down the connection at ~30 seconds. Google AI Studio calls with function calling or thinking mode take 30-75s — always longer than the proxy window. Only `/api/chat/stream` worked, because SSE frames kept the socket warm with incremental data. Three of five shipped features were invisible in the browser for the entire QA session before the root cause was identified.

**Root cause:** Two compounding mistakes. **First:** both test suites (`pytest` + `scripts/feature_smoke.py`) call the backend via FastAPI `TestClient(app)`, which bypasses the Next.js dev proxy entirely. They prove the Python backend works, not that the Next.js→FastAPI wire holds. They were green while the browser was broken. This is the **next layer of mistake #4** — the fix in #4 added router tests via `TestClient`, which is necessary but not sufficient; `TestClient` is not a browser. **Second:** I wrote non-streaming endpoints for long-running Gemma calls. For a 40-second thinking-mode computation, a non-streaming HTTP endpoint is architecturally wrong — the client has no way to know the server is still working, and any proxy in the middle will guess wrong about whether the connection is stale.

**Prevention rule:** For any FastAPI endpoint that calls Gemma with function calling, thinking mode, or multimodal input — assume it will take 30-75s on Google AI Studio — **use `StreamingResponse` with SSE or incremental JSON chunks**. Never write a non-streaming handler for a call that can exceed 20 seconds. Second: before shipping a feature as "working," run it through a real browser end-to-end, not just a `TestClient`. Add a `scripts/browser_smoke.py` that drives the frontend with Playwright or chrome-devtools-mcp and hits each endpoint through the real proxy. The `feature_smoke.py` TestClient path is fine for functional correctness but must not be cited as evidence the UI works. Corollary: cold-boot-smoke via `curl` against port 8001 is also insufficient — it hits the backend directly, bypassing the proxy. A browser-path smoke must drive port 3000.
