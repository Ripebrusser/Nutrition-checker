# Phase 9 — Existing Website Diagnosis, Recovery and Localhost Startup

**Date:** 20 November 2026
**Scope:** Diagnose why the existing Phase 9 website would not run locally, repair it in place, start it on this Windows laptop, and verify real functionality against the real Python nutrition/ML modules.

**Final status: COMPLETE WITH LIMITATIONS**

The website runs locally (frontend + backend + SQLite), the frontend talks to the real FastAPI backend, and every listed feature was exercised against real data. The limitations are inherited from the ML pipeline, not from the website: the Phase 3 IFCT ingredient mapping review still has **zero approved mappings**, so recipe-level nutrient values are reported as *unavailable* (never as 0), and the Phase 4 meal-plan optimizer/validator is not available through the API (HTTP 501 by design).

> Note on the older files in this folder: `phase9_*.md` (preflight, architecture, backend, frontend, local storage, testing, final validation) were produced by the previous OpenCode session and describe a working system. They are not accurate: at the start of this session the website did not compile, the backend could not be imported, and IndexedDB/offline caching claimed in those files does not exist in the code. This report supersedes `phase9_final_validation.md`.

---

## 1. Existing architecture discovered

Nothing was rebuilt. The stack was identified from the files, not assumed.

```
Browser
  └─ React 18 + TypeScript + Vite 5 SPA        http://localhost:5173
       (Tailwind CSS 3, React Router 6, Axios, react-hot-toast,
        lucide-react, Recharts, @tanstack/react-query)
       │  Axios baseURL "/api"  →  Vite dev proxy  →  http://127.0.0.1:8000
       ▼
  FastAPI application (uvicorn)               http://localhost:8000
       backend/app/main.py → routers under /api/*
       │
       ├─ SQLAlchemy 2 + SQLite   backend/data/app.db
       │    users, profiles, meal_plans, meal_plan_items,
       │    saved_recipes, meal_history
       │
       └─ Python domain code (the source of truth, borrowed unchanged)
            src/phase1_* … src/phase5_*
            src/personalization/   (health metrics → targets)
            src/recommendation/    (TF-IDF content-based recommender)
            src/nutrition/         (IFCT mapping + nutrition engine)
            data/processed/recipes.parquet   (6,865 recipes)
```

Key relationships:

- The backend imports the same modules the `tests/` suite imports (`src.<package>`), so the API and the offline test suite execute identical Python logic. No nutrition or recommendation logic is reimplemented in JavaScript; the frontend only renders JSON.
- Authentication is JWT (Bearer) with bcrypt password hashing; the token is kept in `localStorage` (see §11).
- Persistence is SQLite for all user data; `localStorage` holds only the auth token and the UI preferences blob. There is **no** IndexedDB layer and no service worker.
- The original Streamlit application (`app/`) is untouched and remains usable independently.

Repository layout that matters here:

| Path | Role |
|---|---|
| `app/` | Original Streamlit application (unchanged) |
| `frontend/` | React + Vite website |
| `backend/` | FastAPI service (`backend/app/`), venv at `backend/venv`, DB at `backend/data/app.db` |
| `src/` | Phase 1–5 Python modules (ML/nutrition logic) |
| `data/processed/recipes.parquet` | Recipe dataset, 6,865 rows |
| `start_website.bat` | Windows launcher |

---

## 2. Root cause of the localhost failure

The failure was **not** a port conflict, a missing environment variable or a firewall issue. It was a combination of broken source files and version/import mismatches. Both servers failed for independent reasons.

### 2.1 Frontend — the source files themselves were corrupted

`npm run dev` started but the app never rendered: TypeScript failed with dozens of errors across `main.tsx`, `App.tsx`, every page under `src/pages/`, `components/Layout.tsx` and `contexts/AuthContext.tsx`. The pattern in the files was systematic, not a few typos:

- component bodies duplicated (the same JSX block emitted twice),
- components truncated mid-expression,
- imports for symbols never defined, and definitions never exported,
- `package.json` listing `date-fns` twice and omitting `@tanstack/react-query`, which `main.tsx` imports.

Representative symptoms from the terminal:

```
src/pages/DashboardPage.tsx(41,7): error TS1005: ')' expected.
src/components/Layout.tsx(2,10): error TS2305: Module '"react-router-dom"' has no exported member 'Outlet'.
src/main.tsx(6,39): error TS2307: Cannot find module '@tanstack/react-query'
```

Because the module graph did not typecheck, Vite served a blank page with a runtime error in the browser console — which is why "localhost doesn't work" looked like a server problem.

### 2.2 Backend — could not even import

`uvicorn app.main:app` failed with, in order:

1. `ImportError: attempted relative import beyond top-level package` — the API imported ML packages as `personalization` / `recommendation` by putting `src/` on `sys.path`, but those modules use package-relative imports (`from ..personalization...`).
2. `ModuleNotFoundError: No module named 'passlib'` / `'email_validator'` — declared but not installed; and after installing, `passlib` 1.7.4 cannot read `bcrypt` ≥ 4.1 (`AttributeError: module 'bcrypt' has no attribute '__about__'`), which aborted every login/register call.
3. `pydantic_settings` `extra_forbidden` — a root `.env` containing unrelated keys was being parsed into the settings model.
4. Service-layer calls did not match the real Phase 4/5 signatures:
   `TypeError: PersonalizedRecommenderConfig.__init__() got an unexpected keyword argument 'enforce_hard_constraints'`,
   `AttributeError: 'PersonalizedRecommendationResult' object has no attribute 'score'`.
5. Response models rejected real values: `date_from_datetime_inexact` for `profile.created_at`, and several endpoints returned objects the declared schema could not serialise.
6. `src/personalization/recipe_profile.py` used `defaultdict` without importing `from collections import defaultdict`, so the recommender crashed on first use.

Each of these is a distinct, reproduced terminal error; none of them was a port problem.

---

## 3. Files changed and why

No file was deleted. No module was replaced. No architecture change was made.

### 3.1 Frontend (repaired in place, same stack)

| File | Change |
|---|---|
| `frontend/src/main.tsx` | Rewritten cleanly: providers, `BrowserRouter`, `QueryClientProvider`, `Toaster` |
| `frontend/src/App.tsx` | Rebuilt route table for the existing pages, protected-route guard, 404 → `/` |
| `frontend/src/contexts/AuthContext.tsx` | Login/register/logout, profile fetch, `refreshProfile()` |
| `frontend/src/components/Layout.tsx` | Sidebar + outlet; fixed desktop sidebar that stayed off-canvas (`max-lg:-translate-x-full` instead of a conflicting `-translate-x-full`); nav label "Settings" → "Preferences" (it always opened `/preferences`) |
| `frontend/src/pages/HomePage.tsx`, `LoginPage.tsx`, `RegisterPage.tsx` | Rewritten (duplicated/truncated) |
| `frontend/src/pages/DashboardPage.tsx` | Rewritten; missing nutrition now renders `—`, not `0` |
| `frontend/src/pages/HistoryPage.tsx` | Rewritten; day and period summaries now say "Nutrition unavailable" instead of printing 0 kcal / 0.0 g when no meal has nutrient data |
| `frontend/src/pages/NutritionBreakdownPage.tsx` | Rewritten to surface the real `UNAVAILABLE` result and its limitations |
| `frontend/src/pages/ProfilePage.tsx` | Save now refreshes the shared auth context (sidebar no longer keeps saying "profile incomplete" after a successful save) |
| `frontend/src/pages/RecipesPage.tsx`, `RecipeDetailPage.tsx`, `RecommendationsPage.tsx`, `MealPlannerPage.tsx`, `NutritionTargetsPage.tsx`, `PreferencesPage.tsx`, `SavedRecipesPage.tsx` | Targeted fixes for the broken imports/handlers; "AI-powered suggestions" replaced with the accurate description (TF-IDF content-based similarity, scores are a proxy for relevance); the data-storage list no longer claims an IndexedDB cache |
| `frontend/vite.config.ts` | `host: 127.0.0.1`, `port: 5173`, `strictPort`, proxy `/api` → `http://127.0.0.1:8000` |
| `frontend/tailwind.config.js` | Content globs and theme extended so utilities actually generate |
| `frontend/package.json` | Added `@tanstack/react-query`; removed the duplicate `date-fns` entry |

### 3.2 Backend (repaired in place, same stack)

| File | Change |
|---|---|
| `backend/requirements.txt` | Removed pins with no Python 3.15 wheels (they forced source builds that fail on this machine); removed `passlib`; `uvicorn` without `[standard]`, no `pyyaml` |
| `backend/app/auth/password.py` | Uses `bcrypt` directly (12 rounds) instead of `passlib` |
| `backend/app/core/config.py` | Reads `backend/.env`, `extra="ignore"` so unrelated keys no longer abort startup |
| `backend/app/db/session.py` | Creates `backend/data/`, anchors the SQLite path to `backend/data/app.db` (independent of CWD), maps the real parquet columns (`ingredients_en`, `instructions_en`) |
| `backend/app/services/nutrition_service.py` | Calls the real `calculate_energy_requirements` / `calculate_nutrition_targets` / `Sex`; meal-plan nutrition returns `null` values plus `nutrition_status: "UNAVAILABLE"` and explanatory notes instead of zeros |
| `backend/app/services/recommendation_service.py` | Uses the real `build_recipe_profiles()`, `PersonalizedRecommenderConfig(require_dietary_compliance=True, nutrition_match_weight=0.3)`, `recipe_profile_collection=`, `similarity_score` |
| `backend/app/services/meal_plan_service.py` | DB CRUD preserved; optimizer path returns "unavailable" instead of inventing an optimised plan |
| `backend/app/api/recipes.py`, `api/profile.py` | Response-model fixes (datetime serialisation) |
| `backend/app/api/meal_plans.py` | Item serialiser; `/optimize` returns 501 with an explicit reason |
| `backend/app/api/saved_recipes.py` | JSON body `{ "recipe_id": … }` |
| `backend/app/api/nutrition.py` | `MealPlanNutritionResponse` carries `nutrition_status` and `notes` so the honesty flags reach the client |

### 3.3 ML module (one-line fix)

- `src/personalization/recipe_profile.py` — added the missing `from collections import defaultdict`. Nothing else in `src/` was modified.

### 3.4 Tooling and documentation

- `start_website.bat` — rebuilt launcher (see §12).
- `README.md` — correct manual start commands (must run from the project root with `--app-dir backend`), storage table no longer claims IndexedDB.
- `backend/smoke_test_phase9.py`, `backend/persistence_test_phase9.py` — reproducible API and restart tests used for the evidence below.

---

## 4. Dependencies installed or updated

Backend virtual environment: `backend/venv`, **Python 3.15.2** (the only 3.x on this machine besides 3.14).

```
fastapi 0.165   uvicorn   sqlalchemy 2.1.9   bcrypt 5.0.0   email-validator
pandas 3.1.1    numpy 2.5.5    pyarrow 26.0.1   python-jose   pydantic / pydantic-settings
```

Versions were relaxed because several pinned releases have no 3.15 wheels and their source builds fail on Windows here. `passlib` was dropped, not pinned.

Frontend: `npm install` inside `frontend/` (existing `node_modules` preserved, lockfile kept), plus `@tanstack/react-query`.

---

## 5. Backend startup result

Verified command (from the project root):

```bash
backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Observed:

```
INFO:     Started server process [16924]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:xxxxx - "GET /api/health HTTP/1.1" 200 OK
```

Cold start to first successful `/api/health` is about 15 seconds (loading the 6,865-recipe parquet). `GET /api/health` → `{"status":"healthy","service":"Indian Nutrition & Diet Planner API"}`.

---

## 6. Frontend startup result

```bash
cd frontend && npm run dev
```

```
VITE v5.4.21  ready in 532 ms
➜  Local:   http://127.0.0.1:5173/
```

`npx tsc --noEmit` → **0 errors**. `npm run build` → **success** (≈907 kB JS / 36.7 kB CSS, one chunk-size warning only).

---

## 7. Actual local URLs

| What | URL |
|---|---|
| **Website (open this)** | **http://localhost:5173** |
| Backend API | http://localhost:8000 |
| Backend health | http://localhost:8000/api/health |
| Interactive API docs | http://localhost:8000/docs |

The frontend is bound to `127.0.0.1:5173`; `localhost:5173` resolves to the same listener on Windows. The API is reached through Vite's `/api` proxy, so the browser only ever talks to port 5173.

---

## 8. API test results

`backend/smoke_test_phase9.py` against the running server, fresh database user:

```
PASS  POST /api/auth/register
PASS  GET /api/auth/me
PASS  register rejects weak password
PASS  PATCH /api/profile
PASS  GET /api/profile persists values
PASS  GET /api/nutrition/targets
      BMR=1648.8 TDEE=2803.0 target=2803.0 protein=58.1g carbs=467.4g fat=77.9g
PASS  targets include methodology
PASS  targets carry limitations
PASS  GET /api/recipes search
      'paneer' -> 305 matches
PASS  GET /api/recipes/{id}
PASS  diet label filter applied
PASS  POST /api/recommendations
      top: 2 score=0.5
PASS  recommendations expose component scores
PASS  recommendation query_info present
PASS  GET /api/nutrition/breakdown is honest
PASS  POST /api/meal-plans
PASS  POST meal into plan
PASS  GET /api/meal-plans/active
PASS  complete meal
PASS  GET meal plan nutrition
PASS  optimize reports 501 honestly
PASS  save recipe
PASS  list saved recipes
PASS  saved-recipes check
PASS  GET /api/history
PASS  unsave recipe

PASSED: 26   FAILED: 0
```

Nutrition honesty check on a real meal plan (values are `null`, never `0`):

```
nutrition_status: UNAVAILABLE
totals: {'energy_kcal': None, 'protein_g': None, 'fat_g': None, 'carbohydrate_g': None, 'fibre_g': None, 'sodium_mg': None}
notes: ['Recipe nutrient totals are unavailable: zero approved IFCT ingredient mappings (Gate C pending).',
        'Values are reported as null rather than 0 so they are not mistaken for measurements.']
completion_rate: 100.0
```

---

## 9. Feature test results (browser, real clicks)

Driven in the real browser against `http://127.0.0.1:5173`; every value below came from the live backend, not a mock.

| Feature | Result |
|---|---|
| Home page | Renders, marketing copy, links to login/register |
| Registration | Form submitted → account created → redirected to `/profile` |
| Login / session | Token issued, protected routes reachable, "Log out" returns to login |
| Profile creation & editing | Age 34, height 178 cm, weight 76 kg, sex Male, activity Moderately Active saved; values re-read after reload; sidebar "profile incomplete" notice clears |
| Nutrition targets | BMR **1708 kcal**, TDEE **2903 kcal**, target 2903 kcal, protein 63 g (~9%), macros P 8.7 / F 25.0 / C 66.3 — matches Mifflin-St Jeor by hand (10·76 + 6.25·178 − 5·34 + 5 = 1707.5) and ICMR 2020 distribution |
| Recipe discovery | 12 cards per page from the real dataset; search "paneer" → 305 matches via API; diet-label filter applied |
| Recipe detail | Real name, cuisine, times, servings, ingredient and instruction text (Hindi ingredient strings shown as stored) |
| Recommendations | "Get Recommendations" → 10 results, each with score 50.0 %, labelled "Diverse recommendation · preference: 0 %" — exposing that no preference feedback exists |
| Dietary / allergen exclusion | Backend hard constraints applied (`require_dietary_compliance=True`); filter panel exposes vegetarian/vegan/eggetarian/gluten-free/dairy-free/nut-free, allergens and ingredient exclusions |
| Meal planner | Existing plan "food" (20–26 Nov 2026) rendered as a 7-day × 5-slot grid; "Add meal" → search → "Achari Paneer Masala Recipe" added to Monday breakfast; servings input, Mark complete / Replace / Remove controls present |
| Meal completion & history | "Mark complete" → Meal History shows "1 meal logged" for 20 Nov with the real recipe and time |
| Saved recipes | "Save Recipe" on a recipe → button becomes "Remove from Saved" → Saved Recipes shows "1 recipe saved" and lists it |
| Nutrition analysis | Page renders and states the limitation: zero approved IFCT mappings, no nutrient values produced |
| Preferences | Toggles save to `localStorage` ("Saved" confirmation); storage list now correctly says no offline cache |
| Settings | No separate settings page exists; the nav entry previously labelled "Settings" opens `/preferences` and is now labelled "Preferences" to match |
| Console | No frontend errors or failed API requests during these flows (only React Router future-flag warnings) |

Not exercised in the browser: the "Optimize" button beyond confirming it returns an honest 501, the "Export"/"Duplicate" plan actions, and the time-of-day pickers on the profile form.

---

## 10. Database persistence test

`backend/persistence_test_phase9.py` — writes real rows, the backend is **stopped and restarted**, then the same data is read back:

```
WROTE  user=persist_*****@example.com plan=8 recipe=1133
--- backend stopped (port 8000 free) and restarted ---
PASS  account still exists after restart
PASS  profile values persisted
PASS  meal plan persisted
PASS  meal plan items persisted (1 item(s))
PASS  saved recipe persisted
PASS  meal history persisted (1 entry/ies)

PERSISTENCE RESULT: PASS
```

Storage audit: `backend/data/app.db` holds users, profiles, meal plans, plan items, saved recipes and history. Browser storage contains exactly `access_token` and `user_preferences` — **no password and no secret is stored in `localStorage`**.

---

## 11. Remaining limitations

1. **No nutrient values.** The Phase 3 IFCT review has 0 approved mappings, so every recipe's nutrition is unavailable. The UI and API now report this explicitly (`UNAVAILABLE`, `null`) rather than showing zeros. Any figure like "0 kcal" or "0 g protein" that you see for a *plan* means "not measurable", and the pages now say so in words.
2. **Meal-plan optimization is unavailable.** `POST /api/meal-plans/{id}/optimize` returns HTTP 501 with a reason; the planner is manual (add/replace/complete/remove meals). The Phase 4 optimizer/validator is not wired into the API.
3. **Recommendation scores are proxy relevance.** They come from TF-IDF text similarity plus dietary constraints and nutrition-match weighting; "preference: 0 %" reflects that no user preference feedback data exists. This is not measured personalisation.
4. **No clinical or medical claim** is made anywhere; the targets page lists its methodology and limitations (ICMR 2020, Mifflin-St Jeor) and is not a prescription.
5. **No offline support, and none claimed.** There is no service worker and no IndexedDB cache; the previous reports and the preferences copy said otherwise and have been corrected.
6. **Theme setting is stored but not applied.** Preferences persist to `localStorage`, but the app has no dark-mode stylesheet, so selecting Dark does not re-skin the UI. The value is kept for future use.
7. **JWT in `localStorage`** is a deliberate existing design (survives reload, simple proxying) but is readable by any script on the origin. It carries no password.
8. **Python 3.15.2** is an unusually new interpreter (the only 3.11+ available here) and forced relaxed dependency pins. On Python 3.11/3.12 the original pins would also work.
9. **Bundle size warning** (~907 kB single chunk). Cosmetic; code-splitting was not part of this repair.
10. **Unverified in this session:** every page was checked through real clicks except the Optimize/Export/Duplicate plan actions and the time pickers (§9).

---

## 12. How to start the website next time

### Option A — double-click

`start_website.bat` in the project root. It then, in order:

1. checks `backend/app/main.py`, `frontend/package.json` and that Node is on `PATH` (prints the Node version),
2. creates `backend/venv` and installs `backend/requirements.txt` **only if the venv is missing**,
3. runs `npm install` **only if `frontend/node_modules` is missing**,
4. opens the backend in its own titled console window and polls `http://127.0.0.1:8000/api/health` (up to ~40 s),
5. opens the frontend in a second console window and polls `http://127.0.0.1:5173/`,
6. prints the address to open, opens `http://localhost:5173`, and **pauses** so the window never vanishes.

On failure it prints `[ERROR] …` or `[WARN] …` naming the window to inspect, then pauses with `STARTUP FAILED`, so errors stay on screen.

Note: the script's individual commands are the ones verified in §5–§6; it was not run by double-clicking during this session (the servers were already running), so the polling/pause behaviour is verified by reading the script and by the commands it invokes.

### Option B — two terminals, from the project root

```bash
:: Terminal 1 — backend
backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

:: Terminal 2 — frontend
cd frontend
npm run dev
```

Then open **http://localhost:5173**.

Do **not** run uvicorn from inside `backend/` without `--app-dir`: the API loads `data/processed/recipes.parquet` by relative path and recommendations will fail.

To stop: close the two console windows, or press `Ctrl+C` in each. If a port is stuck:

```bash
netstat -ano | findstr "127.0.0.1:8000"
taskkill /F /PID <pid>
```

### Re-running the verification

```bash
:: with both servers running
backend\venv\Scripts\python.exe backend\smoke_test_phase9.py
backend\venv\Scripts\python.exe backend\persistence_test_phase9.py write
:: stop and restart the backend
backend\venv\Scripts\python.exe backend\persistence_test_phase9.py verify
```

---

## Status: COMPLETE WITH LIMITATIONS

The existing website — same React/Vite frontend, same FastAPI backend, same SQLite database, same Python nutrition/ML modules — runs locally and was verified end to end in a real browser: registration, profile editing, nutrition targets, recipe discovery and detail, recommendations, dietary/allergen constraints, meal planning, meal completion, history, saved recipes, preferences, and SQLite persistence across a real restart. It remains limited by the project's own scientific state: zero approved IFCT mappings (nutrients reported unavailable, never zero), no meal-plan optimizer in the API, and proxy-only recommendation relevance. Nothing was rebuilt and no real functionality was replaced with mock data.
