"""End-to-end API smoke test for the Phase 9 backend.

Run against a live backend:
    cd backend
    venv\\Scripts\\python.exe smoke_test_phase9.py

Uses the API only (no direct DB access), so it verifies the real HTTP surface.
"""

import random
import string
import sys
import httpx

BASE = "http://127.0.0.1:8000"
PASS, FAIL = [], []


def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
        print(f"PASS  {name}")
    else:
        FAIL.append(f"{name} :: {detail}")
        print(f"FAIL  {name}  {detail}")


def main():
    suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    email = f"phase9_{suffix}@example.com"
    password = "Testing123!"

    with httpx.Client(base_url=BASE, timeout=180.0) as c:
        # --- auth ---
        r = c.post("/api/auth/register", json={"email": email, "password": password, "full_name": "Phase9 Tester"})
        check("POST /api/auth/register", r.status_code == 201, f"{r.status_code} {r.text[:200]}")
        token = r.json().get("access_token") if r.status_code == 201 else None
        if not token:
            print("\nCannot continue without a token.")
            return summarize()
        c.headers["Authorization"] = f"Bearer {token}"

        r = c.get("/api/auth/me")
        check("GET /api/auth/me", r.status_code == 200 and r.json().get("email") == email, f"{r.status_code}")

        # weak password must be rejected
        r = c.post("/api/auth/register", json={"email": f"weak{suffix}@example.com", "password": "weak", "full_name": "Weak"})
        check("register rejects weak password", r.status_code == 422, f"{r.status_code}")

        # --- profile ---
        payload = {
            "height_cm": 175, "weight_kg": 70, "age_years": 30, "sex": "MALE",
            "dietary_preference": "VEGETARIAN",
            "allergies": ["peanuts"], "ingredient_exclusions": [], "cuisine_preferences": ["South Indian"],
            "cuisine_exclusions": [], "disliked_ingredients": [], "religious_restrictions": [],
            "medical_conditions": [], "weight_goal": "MAINTAIN", "weight_change_rate_kg_per_week": 0.5,
            "activity_level": "MODERATELY_ACTIVE", "meal_frequency": 3, "preferred_meal_times": {},
            "cooking_skill": "INTERMEDIATE",
        }
        r = c.patch("/api/profile", json=payload)
        check("PATCH /api/profile", r.status_code == 200, f"{r.status_code} {r.text[:200]}")

        r = c.get("/api/profile")
        body = r.json() if r.status_code == 200 else {}
        check("GET /api/profile persists values", body.get("height_cm") == 175 and body.get("dietary_preference") == "VEGETARIAN", f"{r.status_code} {body}")

        # --- nutrition targets (real Phase 4 engine) ---
        r = c.get("/api/nutrition/targets")
        t = r.json() if r.status_code == 200 else {}
        check("GET /api/nutrition/targets", r.status_code == 200 and t.get("bmr_kcal", 0) > 1000, f"{r.status_code} {t}")
        if r.status_code == 200:
            print(f"      BMR={t.get('bmr_kcal')} TDEE={t.get('tdee_kcal')} target={t.get('target_energy_kcal')} "
                  f"protein={t.get('protein_g')}g carbs={t.get('carbohydrate_g')}g fat={t.get('fat_g')}g")
            check("targets include methodology", bool(t.get("calculation_method")), "")
            check("targets carry limitations", isinstance(t.get("limitations"), list) and len(t["limitations"]) > 0, "")

        # --- recipes ---
        r = c.get("/api/recipes", params={"query": "paneer", "per_page": 5})
        search = r.json() if r.status_code == 200 else {}
        check("GET /api/recipes search", r.status_code == 200 and len(search.get("recipes", [])) > 0, f"{r.status_code}")
        print(f"      'paneer' -> {search.get('total')} matches")

        recipe_id = search["recipes"][0]["id"] if search.get("recipes") else None
        r = c.get(f"/api/recipes/{recipe_id}") if recipe_id else None
        check("GET /api/recipes/{id}", bool(r) and r.status_code == 200 and len(r.json()["ingredients"]) > 0, f"{r.status_code if r else 'n/a'}")

        # dietary filter consistency: vegetarian only
        r = c.get("/api/recipes", params={"diet_labels": "Vegetarian", "per_page": 20})
        veg = r.json() if r.status_code == 200 else {}
        bad = [x["recipe_name"] for x in veg.get("recipes", []) if "vegetarian" not in (x.get("diet_labels") or "").lower()]
        check("diet label filter applied", r.status_code == 200 and not bad, f"non-matching: {bad[:3]}")

        # --- recommendations (Phase 4/5 engine) ---
        r = c.post("/api/recommendations", json={"k": 5, "diet_labels": ["Vegetarian"], "exclude_allergens": ["peanuts"]})
        rec = r.json() if r.status_code == 200 else {}
        recs = rec.get("recommendations", [])
        check("POST /api/recommendations", r.status_code == 200 and len(recs) > 0, f"{r.status_code} {r.text[:300]}")
        if recs:
            print(f"      top: {recs[0].get('recipe_id')} score={recs[0].get('score')}")
            check("recommendations expose component scores", isinstance(recs[0].get("component_scores"), dict), "")
            check("recommendation query_info present", isinstance(rec.get("query_info"), dict), "")

        # --- nutrition breakdown: must stay UNAVAILABLE, not fabricated ---
        r = c.get(f"/api/nutrition/breakdown/{recipe_id}") if recipe_id else None
        bd = r.json() if r and r.status_code == 200 else {}
        check("GET /api/nutrition/breakdown is honest", bool(r) and r.status_code == 200 and bd.get("completeness") == "UNAVAILABLE", f"{r.status_code if r else 'n/a'} {str(bd)[:200]}")

        # --- meal plan flow ---
        r = c.post("/api/meal-plans", json={"name": "Phase9 Plan", "start_date": "2026-11-16", "end_date": "2026-11-22"})
        plan = r.json() if r.status_code in (200, 201) else {}
        plan_id = plan.get("id")
        check("POST /api/meal-plans", r.status_code in (200, 201) and plan_id, f"{r.status_code} {r.text[:200]}")

        r = c.post(f"/api/meal-plans/{plan_id}/meals", json={"meal_slot": "LUNCH", "day_index": 0, "recipe_id": recipe_id, "servings": 1.0})
        item = r.json() if r.status_code in (200, 201) else {}
        item_id = item.get("id")
        check("POST meal into plan", r.status_code in (200, 201) and item_id, f"{r.status_code} {r.text[:200]}")

        r = c.get("/api/meal-plans/active")
        active = r.json() if r.status_code == 200 else {}
        check("GET /api/meal-plans/active", r.status_code == 200 and active.get("id") == plan_id, f"{r.status_code}")

        if item_id:
            r = c.post(f"/api/meal-plans/{plan_id}/meals/{item_id}/complete")
            check("complete meal", r.status_code == 200 and r.json().get("is_completed") is True, f"{r.status_code} {r.text[:200]}")
            completed_item_id = item_id

        r = c.get(f"/api/nutrition/meal-plan/{plan_id}")
        check("GET meal plan nutrition", r.status_code == 200, f"{r.status_code}")

        r = c.post(f"/api/meal-plans/{plan_id}/optimize")
        check("optimize reports 501 honestly", r.status_code == 501, f"{r.status_code} {r.text[:160]}")

        # --- saved recipes ---
        r = c.post("/api/saved-recipes", json={"recipe_id": recipe_id})
        check("save recipe", r.status_code in (200, 201), f"{r.status_code} {r.text[:160]}")

        r = c.get("/api/saved-recipes")
        saved = r.json() if r.status_code == 200 else []
        check("list saved recipes", r.status_code == 200 and len(saved) >= 1, f"{r.status_code}")

        r = c.get(f"/api/saved-recipes/{recipe_id}/check")
        check("saved-recipes check", r.status_code == 200 and r.json().get("saved") is True, f"{r.status_code} {r.text[:160]}")

        # --- history ---
        r = c.get("/api/history", params={"limit": 50})
        hist = r.json() if r.status_code == 200 else []
        check("GET /api/history", r.status_code == 200 and len(hist) >= 1, f"{r.status_code} {str(hist)[:160]}")

        # --- unsaved delete cleanup ---
        r = c.delete(f"/api/saved-recipes/{recipe_id}")
        check("unsave recipe", r.status_code in (200, 204), f"{r.status_code}")

    print(f"\nCreated test user: {email}")
    return summarize()


def summarize():
    print("\n" + "=" * 60)
    print(f"PASSED: {len(PASS)}   FAILED: {len(FAIL)}")
    for f in FAIL:
        print("  FAILED:", f)
    print("=" * 60)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
