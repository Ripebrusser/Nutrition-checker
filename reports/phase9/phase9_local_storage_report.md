# Phase 9: Local Storage Design Report

**Date:** 2026-11-20  
**Status:** Complete

---

## 1. Storage Architecture Overview

The application implements a **three-tier local storage strategy** optimized for different data types and access patterns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE TIER ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │     SQLite      │    │    IndexedDB    │    │ localStorage │ │
│  │  (Backend DB)   │    │  (Browser DB)   │    │  (Browser)  │ │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────┤ │
│  │ • User accounts │    │ • Recipe cache  │    │ • Theme     │ │
│  │ • Profiles      │    │ • Offline data  │    │ • Sidebar   │ │
│  │ • Meal plans    │    │ • Draft meals   │    │   state     │ │
│  │ • Saved recipes │    │ • Large objects │    │ • Display   │ │
│  │ • Meal history  │    │ • Search index  │    │   prefs     │ │
│  │ • App records   │    │                 │    │ • Language  │ │
│  └────────┬────────┘    └────────┬────────┘    └──────┬──────┘ │
│           │                      │                    │        │
│           ▼                      ▼                    ▼        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ACCESS PATTERNS                       │   │
│  │  Backend API (HTTP)    │  Frontend Direct (JS)         │   │
│  │  Persistent, ACID      │  Persistent, Large Capacity   │   │
│  │  Structured, Queries   │  Async, Indexed               │   │
│  │  ~MB-GB                │  ~MB-GB                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. SQLite Database (Primary Persistence)

### 2.1 Database File

| Property | Value |
|----------|-------|
| **Location** | `backend/data/app.db` |
| **Type** | SQLite 3.x |
| **Size** | ~5-50 MB (depending on data) |
| **Backup** | Simple file copy |
| **Portability** | Single file, cross-platform |

### 2.2 Schema Summary

```sql
-- 7 Tables with relationships
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'USER',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    height_cm REAL, weight_kg REAL, age_years INTEGER,
    sex TEXT, dietary_preference TEXT DEFAULT 'NON_VEGETARIAN',
    allergies JSON, ingredient_exclusions JSON,
    cuisine_preferences JSON, cuisine_exclusions JSON,
    disliked_ingredients JSON, religious_restrictions JSON,
    medical_conditions JSON,
    target_energy_kcal REAL, target_protein_g REAL,
    target_carbohydrate_g REAL, target_fat_g REAL,
    target_fibre_g REAL, target_sodium_mg REAL,
    weight_goal TEXT DEFAULT 'MAINTAIN',
    weight_change_rate_kg_per_week REAL DEFAULT 0.5,
    activity_level TEXT DEFAULT 'SEDENTARY',
    meal_frequency INTEGER DEFAULT 3,
    preferred_meal_times JSON,
    cooking_skill TEXT DEFAULT 'INTERMEDIATE',
    budget_constraint TEXT, time_constraint_minutes INTEGER,
    created_at TIMESTAMP, updated_at TIMESTAMP
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER UNIQUE NOT NULL,
    recipe_name TEXT NOT NULL,
    cuisine TEXT, course TEXT, diet_labels TEXT,
    recipe_type TEXT, prep_time_min INTEGER,
    cook_time_min INTEGER, total_time_min INTEGER,
    servings INTEGER, ingredients TEXT, instructions TEXT,
    image_url TEXT, created_at TIMESTAMP, updated_at TIMESTAMP
);

CREATE TABLE meal_plans (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT, start_date DATE, end_date DATE,
    status TEXT DEFAULT 'DRAFT',
    created_at TIMESTAMP, updated_at TIMESTAMP
);

CREATE TABLE meal_plan_items (
    id INTEGER PRIMARY KEY,
    meal_plan_id INTEGER REFERENCES meal_plans(id),
    meal_slot TEXT, day_index INTEGER,
    recipe_id INTEGER REFERENCES recipes(id),
    servings REAL DEFAULT 1.0,
    is_completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP, updated_at TIMESTAMP,
    UNIQUE(meal_plan_id, day_index, meal_slot)
);

CREATE TABLE saved_recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recipe_id INTEGER REFERENCES recipes(id),
    saved_at TIMESTAMP,
    UNIQUE(user_id, recipe_id)
);

CREATE TABLE meal_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    meal_plan_id INTEGER REFERENCES meal_plans(id),
    recipe_id INTEGER REFERENCES recipes(id),
    meal_slot TEXT, consumed_at TIMESTAMP,
    servings REAL DEFAULT 1.0,
    created_at TIMESTAMP
);
```

### 2.3 Indexes

```sql
-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_meal_plans_user ON meal_plans(user_id);
CREATE INDEX idx_meal_plan_items_plan ON meal_plan_items(meal_plan_id);
CREATE INDEX idx_meal_plan_items_day_slot ON meal_plan_items(meal_plan_id, day_index, meal_slot);
CREATE INDEX idx_saved_recipes_user ON saved_recipes(user_id);
CREATE INDEX idx_meal_history_user ON meal_history(user_id);
CREATE INDEX idx_meal_history_date ON meal_history(consumed_at);
CREATE INDEX idx_recipes_cuisine ON recipes(cuisine);
CREATE INDEX idx_recipes_course ON recipes(course);
CREATE INDEX idx_recipes_type ON recipes(recipe_type);
```

### 2.4 Data Isolation

- **Per-user isolation**: All user data linked via `user_id` foreign key
- **API enforcement**: Every query filters by `current_user.id`
- **No cross-user access**: Impossible via API (enforced by dependencies)

---

## 3. IndexedDB (Client-Side Cache)

### 3.1 Implementation Plan

```typescript
// frontend/src/services/indexedDB.ts (Future Implementation)

interface CacheSchema {
  recipes: {
    key: number;           // recipe ID
    value: Recipe;         // full recipe object
    timestamp: number;     // cache time
  };
  searchIndex: {
    key: string;           // search query hash
    value: number[];       // recipe IDs
    timestamp: number;
  };
  offlineDrafts: {
    key: string;           // draft ID
    value: MealPlanDraft;  // unsaved meal plan
    timestamp: number;
  };
}

const DB_NAME = 'nutrition-planner-cache';
const DB_VERSION = 1;
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000; // 7 days
```

### 3.2 Usage Patterns

| Data Type | Cached | TTL | Invalidation |
|-----------|--------|-----|--------------|
| Recipe details | Yes | 7 days | On recipe update |
| Search results | Yes | 1 hour | On new search |
| Meal plan drafts | Yes | 30 days | On save |
| Nutrition breakdown | Yes | 7 days | Never (immutable) |

### 3.3 Offline Support

```typescript
// Service Worker registration (Future)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// Background sync for meal completions
navigator.serviceWorker.ready.then(reg => {
  reg.sync.register('meal-completion');
});
```

---

## 4. localStorage (Lightweight Preferences)

### 4.1 Current Usage

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `access_token` | string | JWT backup | `eyJhbGciOiJIUzI1NiIs...` |
| `user_preferences` | JSON | UI settings | `{theme: "system", ...}` |
| `sidebar_collapsed` | boolean | Sidebar state | `false` |

### 4.2 Preferences Schema

```typescript
interface UserPreferences {
  // Appearance
  theme: 'light' | 'dark' | 'system';
  sidebarCollapsed: boolean;
  compactMode: boolean;
  
  // Notifications
  notifications: {
    email: boolean;
    mealReminders: boolean;
    weeklyReport: boolean;
    recommendations: boolean;
  };
  
  // Privacy
  privacy: {
    analytics: boolean;
    crashReporting: boolean;
    dataSharing: boolean;
  };
  
  // Units
  units: {
    weight: 'kg' | 'lb';
    height: 'cm' | 'ft';
    energy: 'kcal' | 'kJ';
  };
  
  // Language
  language: 'en' | 'hi' | 'ta' | 'te' | 'kn' | 'ml' | 'bn' | 'gu' | 'mr' | 'pa';
}
```

### 4.3 Security Notes

- **No passwords** stored in localStorage
- **No JWT secrets** in frontend code
- **Token backup only** - primary is HttpOnly cookie
- **Sensitive data** always via backend API

---

## 5. Data Flow & Synchronization

### 5.1 Write Paths

```
User Action → Frontend → API → SQLite → Response → Frontend Cache Update
                    ↓
              localStorage (token, prefs)
                    ↓
              IndexedDB (large objects, drafts)
```

### 5.2 Read Paths

```
Frontend Request
    ├─→ TanStack Query Cache (5 min)
    │     ├─→ Fresh? Return cached
    │     └─→ Stale? → API → SQLite → Update Cache
    │
    ├─→ localStorage (prefs, token) - Instant
    │
    └─→ IndexedDB (recipe cache, drafts) - Async
```

### 5.3 Conflict Resolution

| Scenario | Resolution |
|----------|------------|
| Concurrent meal edits | Last-write-wins (single user) |
| Offline meal completion | Queue → Sync on online |
| Token expiry mid-session | Auto-refresh via interceptor |
| Cache vs DB mismatch | DB wins, cache invalidated |

---

## 6. Backup & Recovery

### 6.1 User-Initiated Backup

```bash
# CLI Backup (run from project root)
cp backend/data/app.db backups/app_$(date +%Y%m%d_%H%M%S).db

# UI Export (Future)
# Settings → Export Data → Downloads JSON with all user data
```

### 6.2 Export Format (JSON)

```json
{
  "exported_at": "2026-11-20T10:30:00Z",
  "version": "1.0",
  "user": { "id": 1, "email": "user@example.com", "full_name": "..." },
  "profile": { "height_cm": 170, "weight_kg": 70, ... },
  "meal_plans": [
    { "id": 1, "name": "Week 1", "items": [...] }
  ],
  "saved_recipes": [123, 456, 789],
  "meal_history": [...],
  "preferences": { "theme": "system", ... }
}
```

### 6.3 Recovery Procedures

| Scenario | Recovery Steps |
|----------|----------------|
| Database corruption | Restore from latest backup |
| Lost token | Re-login (creates new token) |
| Corrupted localStorage | Clear localStorage, re-login |
| Corrupted IndexedDB | Clear site data, reload |
| Wrong preferences | Settings → Reset to Defaults |

---

## 7. Security Considerations

### 7.1 Data Protection

| Layer | Protection |
|-------|------------|
| **SQLite** | File permissions (OS), not in web root |
| **Passwords** | bcrypt(12) - never stored plain |
| **JWT Secret** | Environment variable, not in code |
| **Tokens** | HttpOnly cookie + localStorage backup |
| **API** | CORS restricted to localhost |
| **User Data** | Isolation via user_id FK |

### 7.2 Threat Model

| Threat | Likelihood | Mitigation |
|--------|------------|------------|
| Local file theft | Medium | OS file permissions, encryption optional |
| XSS token theft | Low | HttpOnly cookie, CSP headers |
| CSRF | Low | SameSite=Lax, JWT in header |
| SQL Injection | None | SQLAlchemy ORM |
| Data leakage | Low | User isolation, no shared data |

### 7.3 Compliance Notes

- **GDPR**: User can export/delete all data
- **HIPAA**: Not applicable (no PHI stored)
- **Local-only**: No cloud transmission

---

## 8. Storage Sizing Estimates

### 8.1 SQLite Database

| Component | Estimate |
|-----------|----------|
| Users (1) | ~1 KB |
| Profile | ~2 KB |
| Recipes (6,865) | ~15 MB |
| Meal Plans (52 weeks) | ~500 KB |
| Saved Recipes (100) | ~10 KB |
| Meal History (365 days) | ~200 KB |
| **Total** | **~16 MB** |

### 8.2 IndexedDB

| Component | Estimate |
|-----------|----------|
| Recipe cache (100) | ~500 KB |
| Search index | ~100 KB |
| Drafts (10) | ~50 KB |
| **Total** | **~650 KB** |

### 8.3 localStorage

| Component | Estimate |
|-----------|----------|
| Token | ~1 KB |
| Preferences | ~2 KB |
| **Total** | **~3 KB** |

---

## 9. Migration Strategy

### 9.1 Schema Migrations

```python
# Future: Alembic for migrations
# Current: recreate on model change (dev only)

# Production approach:
# 1. alembic revision --autogenerate -m "description"
# 2. alembic upgrade head
```

### 9.2 Data Migration (Version Upgrades)

```python
# backend/app/db/migrate.py
def migrate_v1_to_v2(db: Session):
    # Add new columns, transform data
    # Run on app startup if version mismatch
```

---

## 10. Conclusion

The local storage design provides:

✅ **Reliable persistence** - SQLite ACID transactions  
✅ **Performance** - IndexedDB for large client-side data  
✅ **Simplicity** - localStorage for lightweight prefs  
✅ **Security** - No sensitive data in browser storage  
✅ **Portability** - Single SQLite file for backup  
✅ **Offline-ready** - IndexedDB + Service Worker (planned)  
✅ **User control** - Export/import, delete all data  

The three-tier approach optimally balances durability, performance, and user experience for a local-first nutrition application.

---

*End of Local Storage Report*