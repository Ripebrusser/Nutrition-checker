"""SQLite persistence test across a backend restart.

Phase 1 writes data through the API and saves the credentials/plan id to a
small JSON file. Phase 2 (run after restarting the backend) logs in again and
verifies the same data is still there.

    conda/venv python persistence_test_phase9.py write
    # restart the backend
    venv python persistence_test_phase9.py verify
"""

import json
import random
import string
import sys
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
STATE = Path(__file__).resolve().parent / ".persistence_state.json"


def write_state():
    suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    email = f"persist_{suffix}@example.com"
    password = "Persist123!"

    with httpx.Client(base_url=BASE, timeout=180.0) as c:
        r = c.post("/api/auth/register", json={"email": email, "password": password, "full_name": "Persistence Check"})
        r.raise_for_status()
        token = r.json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"

        c.patch("/api/profile", json={
            "height_cm": 181, "weight_kg": 82, "age_years": 41, "sex": "MALE",
            "dietary_preference": "EGGETARIAN", "allergies": ["sesame"],
            "activity_level": "VERY_ACTIVE", "weight_goal": "LOSE",
            "weight_change_rate_kg_per_week": 0.25, "meal_frequency": 4,
        }).raise_for_status()

        plan = c.post("/api/meal-plans", json={
            "name": "Persistence Plan", "start_date": "2026-11-16", "end_date": "2026-11-22",
        }).json()

        recipe = c.get("/api/recipes", params={"per_page": 1}).json()["recipes"][0]
        item = c.post(f"/api/meal-plans/{plan['id']}/meals", json={
            "meal_slot": "BREAKFAST", "day_index": 1, "recipe_id": recipe["id"], "servings": 1.0,
        }).json()
        c.post(f"/api/meal-plans/{plan['id']}/meals/{item['id']}/complete").raise_for_status()
        c.post("/api/saved-recipes", json={"recipe_id": recipe["id"]}).raise_for_status()

    STATE.write_text(json.dumps({
        "email": email, "password": password, "plan_id": plan["id"],
        "recipe_id": recipe["id"], "height_cm": 181,
    }), encoding="utf-8")
    print(f"WROTE  user={email} plan={plan['id']} recipe={recipe['id']}")
    print(f"State saved to {STATE}")


def verify_state():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    failures = []

    with httpx.Client(base_url=BASE, timeout=180.0) as c:
        r = c.post("/api/auth/login", json={"email": state["email"], "password": state["password"]})
        if r.status_code != 200:
            print(f"FAIL  login after restart: {r.status_code} {r.text[:200]}")
            return 1
        print("PASS  account still exists after restart")
        c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"

        profile = c.get("/api/profile").json()
        if profile.get("height_cm") == 181 and profile.get("dietary_preference") == "EGGETARIAN":
            print("PASS  profile values persisted")
        else:
            failures.append(f"profile mismatch: {profile}")
            print("FAIL  profile values did not persist")

        plans = c.get("/api/meal-plans").json()
        if any(p["id"] == state["plan_id"] for p in plans):
            print("PASS  meal plan persisted")
        else:
            failures.append("meal plan missing")
            print("FAIL  meal plan missing after restart")

        plan = c.get(f"/api/meal-plans/{state['plan_id']}").json()
        if plan.get("items"):
            print(f"PASS  meal plan items persisted ({len(plan['items'])} item(s))")
        else:
            failures.append("meal items missing")
            print("FAIL  meal plan items missing")

        saved = c.get("/api/saved-recipes").json()
        if any(s["recipe_id"] == state["recipe_id"] for s in saved):
            print("PASS  saved recipe persisted")
        else:
            failures.append("saved recipe missing")
            print("FAIL  saved recipe missing")

        history = c.get("/api/history", params={"limit": 50}).json()
        if history:
            print(f"PASS  meal history persisted ({len(history)} entr(y/ies))")
        else:
            failures.append("meal history empty")
            print("FAIL  meal history empty after restart")

    print("\n" + "=" * 60)
    print("PERSISTENCE RESULT:", "PASS" if not failures else f"FAIL ({len(failures)})")
    print("=" * 60)
    return 0 if not failures else 1


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "write"
    sys.exit(write_state() or 0 if action == "write" else verify_state())
