# Phase 6: User Interface Report

**Date:** 2026-11-19  
**Status:** Implementation Complete

---

## 1. UI Framework & Design System

### 1.1 Technology Stack
| Component | Technology | Version |
|-----------|------------|---------|
| **Frontend Framework** | Streamlit | 1.67.0 |
| **Styling** | Custom CSS + Streamlit native | - |
| **Charts/Visualizations** | Plotly | 7.1.0 |
| **Icons** | Unicode emoji + Streamlit native | - |

### 1.2 Design Principles
| Principle | Implementation |
|-----------|----------------|
| **Clean & Minimal** | White space, clear typography, subtle shadows |
| **Consistent** | Reusable components, standardized colors |
| **Accessible** | High contrast, keyboard navigation, screen reader friendly |
| **Responsive** | Streamlit's built-in responsive layout |
| **Indian Context** | Cuisine names, ingredient names, meal terminology |

---

## 2. Page Structure & Navigation

### 2.1 Page Hierarchy
```
🏠 Home (Public)
├── 🔐 Login (Public)
├── 📝 Register (Public)
├── 📊 Dashboard (Auth)
├── 👤 Profile (Auth)
│   ├── 📋 Basic Info
│   ├── 🥗 Dietary Preferences
│   ├── 🎯 Nutrition Goals
│   └── 🔐 Security
├── 🎯 Nutrition Targets (Auth)
├── 🍲 Recipes (Auth)
│   └── 📋 Recipe Detail
├── ✨ Recommendations (Auth)
├── 📅 Meal Planner (Auth)
│   ├── 📅 Create Plan
│   ├── 📋 My Plans
│   └── 📊 Weekly View
├── 📋 Meal Plan Detail (Auth)
├── 🔬 Nutrition Breakdown (Auth)
├── ⚙️ Preferences (Auth)
└── 📜 History (Auth)
```

### 2.2 Navigation Components

| Component | Location | Behavior |
|-----------|----------|----------|
| **Sidebar** | Left panel | Collapsible, shows auth status, quick stats |
| **Top Navigation** | Page header | Page title, back button, quick actions |
| **Tab Navigation** | Within pages | Tabbed interfaces (Profile, Meal Plan Detail) |
| **Breadcrumbs** | Recipe Detail, Meal Plan Detail | Context awareness |

---

## 3. Page-by-Page UI Specification

### 3.1 Home Page (`/home`)
| Element | Description |
|---------|-------------|
| **Hero Section** | Title, tagline, CTA button |
| **Feature Grid** | 4 cards: Recipes, Nutrition, Meal Plans, Tracking |
| **How It Works** | 6-step numbered process |
| **Quick Stats** | 4 metrics: Recipes, Cuisines, Nutrients, IFCT Foods |
| **Footer** | Links, disclaimer about Gate C |

### 3.2 Login Page (`/login`)
| Component | Details |
|-----------|---------|
| **Form** | Email + Password fields |
| **Validation** | Real-time email format, password strength |
| **Error States** | Inline errors below fields |
| **Links** | "Forgot password" (placeholder), "Register" link |
| **Demo Notice** | Explains academic/demo nature |

### 3.3 Registration Page (`/register`)
| Section | Fields |
|---------|--------|
| **Personal** | First name, Last name, Email, Password, Confirm |
| **Quick Profile** | Height, Weight, Age, Sex |
| **Dietary** | Preference dropdown, Activity level |
| **Validation** | Real-time password strength meter |

### 3.4 Dashboard (`/dashboard`)
| Section | Components |
|---------|------------|
| **Welcome** | User name, quick stats (4 metrics) |
| **Today's Plan** | Meal slots with completion buttons |
| **Quick Actions** | 4 buttons: Browse, Recommend, Plan, Targets |
| **Recent Activity** | Saved recipes, completed meals |
| **Sidebar** | Progress, quick navigation |

### 3.5 Profile Page (`/profile`)
| Tab | Content |
|-----|---------|
| **Basic Info** | Height, Weight, Age, Sex (editable form) |
| **Dietary** | Preference, Allergies, Exclusions, Cuisines (tags input) |
| **Nutrition** | Weight goal, Macro targets, Meal frequency (editable) |
| **Security** | Change password, Delete account (confirmation) |
| **Summary** | Completion %, readiness status |

### 3.6 Nutrition Targets (`/nutrition_targets`)
| Tab | Content |
|-----|---------|
| **Your Targets** | Energy, Protein, Carbs, Fat, Fibre + method selector |
| **Meal Distribution** | Per-meal targets with visual bars |
| **Macro Breakdown** | Plotly pie chart + ICMR range validation |
| **Micronutrients** | Sodium, Potassium, Calcium, Iron, Zinc, Vitamins |

### 3.6 Recipes Page (`/recipes`)
| Component | Features |
|-----------|----------|
| **Sidebar Filters** | Cuisine, Course, Diet, Nutrition, Time, Sort |
| **Recipe Grid** | 2-column cards with image placeholder |
| **Recipe Card** | Name, cuisine, course, nutrition badge, macros preview |
| **Pagination** | 20 per page, prev/next, page jump |
| **Nutrition Badge** | Color-coded: Complete/Partial/Unavailable |

### 3.7 Recipe Detail (`/recipe_detail`)
| Tab | Content |
|-----|---------|
| **Ingredients & Instructions** | Lists + numbered steps, time, source link |
| **Nutrition** | Per-serving macros/micros, completeness bars, provenance |
| **Dietary** | Classification, non-veg items, Jain compliance |
| **Notes** | User notes textarea |
| **Actions** | Save, Add to Meal Plan, Similar recipes |

### 3.7 Recommendations (`/recommendations`)
| Section | Features |
|---------|----------|
| **Type Selector** | Similar Recipe / By Ingredients / Meal Slot / Diverse |
| **Input** | Recipe dropdown / Ingredient tags / Meal slot selector |
| **Filters** | Cuisine, Course, Diet, Time, Nutrition completeness |
| **Results** | Recipe cards with dietary badge, nutrition match score |
| **Explanation** | "Why this recipe?" with evidence segments |

### 3.8 Meal Planner (`/meal_planner`)
| Tab | Features |
|-----|----------|
| **Create Plan** | Start date, days, meals/day, auto-generate |
| **My Plans** | List with status, view/edit/complete actions |
| **Weekly View** | Expandable days, meal slots, drag-and-drop ready |

### 3.8 Meal Plan Detail
| Feature | Description |
|---------|-------------|
| **Day Tabs** | Mon-Sun expandable sections |
| **Meal Slots** | Badge + recipe name + complete/replace/remove |
| **Empty Slots** | "Add Recipe" button → redirects to recipes |
| **Summary** | Completion %, filled slots, unique recipes, cuisines |
| **Weekly Summary** | Macro totals, achievement %, notes |

### 3.9 Nutrition Breakdown
| Section | Content |
|---------|---------|
| **Coverage** | 4 metric cards: Complete/Partial/Unavailable/No Mapping |
| **Nutrient Table** | 9 nutrients with coverage % |
| **Edible Portion** | Coverage stats by category |
| **Weight Coverage** | 1.4% gram, 1.5% household, 98.5% unresolved |
| **Methodology** | Formula, steps, provenance, limitations |

### 3.8 Preferences
| Tab | Content |
|-----|---------|
| **Profile** | Basic info form |
| **Dietary** | Preferences, allergies, exclusions, cuisines |
| **Nutrition** | Goals, custom targets |
| **Security** | Password change, account deletion |

### 3.9 History
| Tab | Content |
|-----|---------|
| **Meal History** | Date filter, grouped by date, completion status |
| **Saved Recipes** | List with remove/view actions |
| **Analytics** | Stats cards, cuisine pie chart, completion trend chart |

---

## 4. Reusable Components

### 4.1 Form Components (`app/components/forms.py`)
| Component | Purpose |
|-----------|---------|
| `profile_form()` | Anthropometrics + lifestyle |
| `dietary_preferences_form()` | Tags input for allergies/exclusions/cuisines |
| `nutritional_goals_form()` | Weight goal + macro targets |
| `profile_form()` | Basic info form |
| `recipe_card()` | Recipe display card with nutrition |
| `nutrition_status_badge()` | Color-coded status badge |
| `nutrient_metric_card()` | Metric with target comparison |
| `dietary_compliance_badge()` | PASS/FAIL/UNVERIFIED badge |
| `meal_slot_badge()` | Icon + label for meal slots |
| `st_tags_input()` | Custom tags input with suggestions |

### 4.2 Custom Tag Input
```python
def st_tags_input(label, value, suggestions, disabled=False, key):
    # Session state for tag persistence
    # Selectbox with suggestions + text input
    # Add/remove buttons with rerun
    # Returns list of tags
```

---

## 5. Visual Design System

### 5.1 Color Palette
| Role | Hex | Usage |
|-------|-----|-------|
| **Primary** | `#1E88E5` | Primary buttons, links |
| **Success** | `#2E7D32` | Success messages, PASS badges |
| **Warning** | `#F57F17` | Warnings, UNVERIFIED badges |
| **Error** | `#C62828` | Errors, FAIL badges, delete |
| **Info** | `#0288D1` | Info messages, links |
| **Background** | `#FAFAFA` | Page background |
| **Surface** | `#FFFFFF` | Cards, containers |
| **Text Primary** | `#212121` | Primary text |
| **Text Secondary** | `#757575` | Secondary text, captions |

### 5.2 Status Badge Colors
| Status | Color | Hex |
|--------|-------|-----|
| COMPLETE | Green | `#2E7D32` |
| PARTIAL | Orange | `#F57F17` |
| UNAVAILABLE | Gray | `#757575` |
| NO_MAPPED_INGREDIENTS | Red | `#C62828` |

### 5.3 Nutrition Status Badges
| Status | Color |
|--------|-------|
| PASS | Green |
| FAIL | Red |
| UNVERIFIED | Orange |

### 5.3 Typography
| Element | Font | Size | Weight |
|---------|------|------|--------|
| Page Title | System UI | 2.5rem | 600 |
| Section Header | System UI | 1.5rem | 600 |
| Subsection | System UI | 1.25rem | 500 |
| Body Text | System UI | 1rem | 400 |
| Caption | System UI | 0.875rem | 400 |
| Metric Value | System UI | 2rem | 700 |
| Metric Label | System UI | 0.875rem | 500 |

### 5.4 Spacing Scale
| Size | Value |
|------|-------|
| xs | 0.25rem (4px) |
| sm | 0.5rem (8px) |
| md | 1rem (16px) |
| lg | 1.5rem (24px) |
| xl | 2rem (32px) |
| xxl | 3rem (48px) |

---

## 6. Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| **Desktop** (≥1024px) | Full sidebar, 2-col recipe grid, 5-col metrics |
| **Tablet** (768-1023px) | Collapsible sidebar, 1-col recipe grid, 3-col metrics |
| **Mobile** (<768px) | Hidden sidebar (hamburger), stacked layout, 2-col metrics |

---

## 7. Loading & Empty States

| State | Implementation |
|-------|----------------|
| **Page Load** | `st.spinner()` with descriptive text |
| **Data Fetch** | `st.spinner("Loading recipes...")` |
| **Empty Recipes** | Illustration + "No recipes match" + filter reset button |
| **No Meal Plan** | Illustration + "Create your first plan" CTA |
| **No Recommendations** | "No matches" + filter adjustment hints |
| **No Nutrition Data** | Clear "UNAVAILABLE" badge + explanation link |

---

## 8. Error Handling UI

| Error Type | Display |
|------------|---------|
| **Validation** | Inline red text below field |
| **Auth Failed** | Red alert banner at top |
| **Network Error** | Red banner + retry button |
| **Not Found** | 404 page with back link |
| **Server Error** | Generic message + "Contact support" |

---

## 9. Accessibility

| Feature | Implementation |
|----------|----------------|
| **Keyboard Navigation** | Tab order, focus visible |
| **Screen Readers** | Alt text, ARIA labels where possible |
| **Color Contrast** | WCAG AA compliant ratios |
| **Focus Indicators** | Visible outline on focus |
| **Form Labels** | Explicit `<label>` for all inputs |

---

## 10. Limitations

| Limitation | Impact |
|------------|--------|
| **Streamlit Limitations** | No custom HTML/JS, limited layout control |
| **No WebSocket** | No real-time updates without rerun |
| **Session State** | Resets on page refresh (by design) |
| **No Service Worker** | No offline support |
| **SEO** | Not applicable (authenticated app) |

---

*End of User Interface Report*