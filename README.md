# Indian Nutrition & Diet Planner

A personalized Indian meal recommendation system using health metrics and ingredient-level nutrition analysis. Built with React + FastAPI, running entirely locally on your machine.

## 🎯 Features

- **6,865+ Authentic Indian Recipes** - Curated from diverse regional cuisines
- **Science-Backed Nutrition** - ICMR 2020 RDA guidelines with Mifflin-St Jeor BMR calculations
- **Personalized Recommendations** - TF-IDF content-based + dietary constraint engine
- **Smart Meal Planning** - Weekly plans with variety controls and nutrition tracking
- **Dietary Safety** - Hard constraints for allergies, Jain, vegan, vegetarian, custom exclusions
- **Local-First** - SQLite database, no cloud dependencies, works offline

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   React + Vite  │────▶│    FastAPI      │
│   (Port 5173)   │     │   (Port 8000)   │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌─────────────┐ ┌──────────┐ ┌──────────┐
            │  Phase 3    │ │ Phase 4  │ │ Phase 5  │
            │ Nutrition   │ │Personal- │ │ Recomm-  │
            │ Engine      │ │ization   │ │endation  │
            └─────────────┘ └──────────┘ └──────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 ▼
                        ┌─────────────────┐
                        │   SQLite DB     │
                        │   (Local File)  │
                        └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git** (for cloning)

## 🚀 Quick Start

### Option 1: Automated (Windows)

```bash
# Clone and run
git clone <repository-url>
cd ML_proj
start_website.bat
```

### Option 2: Manual

#### Backend Setup

Run these from the **project root** (not from `backend/`): the API loads
`data/processed/recipes.parquet` with a relative path.

```bash
python -m venv backend/venv
backend\venv\Scripts\pip install -r backend/requirements.txt
backend\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
ML_proj/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── nutrition.py
│   │   │   ├── recipes.py
│   │   │   ├── recommendations.py
│   │   │   ├── meal_plans.py
│   │   │   ├── saved_recipes.py
│   │   │   ├── history.py
│   │   │   └── nutrition_breakdown.py
│   │   ├── services/       # Business logic (reuses Phase 3/4/5)
│   │   │   ├── recipe_service.py
│   │   │   ├── nutrition_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── meal_plan_service.py
│   │   ├── db/             # Database models & session
│   │   ├── auth/           # JWT + bcrypt authentication
│   │   └── core/           # Configuration
│   └── requirements.txt
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components (12 pages)
│   │   ├── contexts/       # React contexts (Auth)
│   │   ├── services/       # API client (Axios + TanStack Query)
│   │   ├── types/          # TypeScript types
│   │   └── hooks/          # Custom hooks
│   ├── package.json
│   └── vite.config.ts
├── src/                    # Original Python ML modules (Phase 1-6)
│   ├── nutrition/          # Phase 3.6 Nutrition Engine
│   ├── personalization/    # Phase 4 Personalization
│   ├── recommendation/     # Phase 5 Recommendations
│   └── ...
├── app/                    # Original Streamlit app
├── data/                   # Datasets (Parquet/CSV)
├── reports/                # Phase reports
└── start_website.bat       # Windows startup script
```

## 🔐 Authentication

- JWT tokens with HS256 signing
- Bcrypt password hashing (12 rounds)
- HttpOnly cookies for token storage
- Automatic token refresh

## 🗄️ Data Storage

| Data Type | Storage | Location |
|-----------|---------|----------|
| User accounts, profiles | SQLite | `backend/data/app.db` |
| Meal plans, history | SQLite | `backend/data/app.db` |
| Saved recipes | SQLite | `backend/data/app.db` |
| UI preferences | localStorage | Browser |
| Recipe cache | not implemented (no offline cache) | - |

### Backup Your Data

```bash
# Backup database
cp backend/data/app.db backup/app_$(date +%Y%m%d).db

# Export from UI: Settings → Export Data
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test

# Build verification
npm run build
```

## ⚠️ Known Limitations

| Limitation | Impact | Status |
|------------|--------|--------|
| **Zero approved IFCT mappings** | Nutrition analysis shows UNAVAILABLE for all recipes | Gate C pending |
| **1.4% gram weight coverage** | Most recipes lack resolved ingredient weights | Under review |
| **42% IFCT nutrient gaps** | Fibre/carb missing for 222/528 foods | Dataset limitation |
| **No collaborative filtering** | No user interaction data for CF | Future work |

**The application honestly displays UNAVAILABLE where nutrition cannot be calculated rather than fabricating values.**

## 📱 Pages

1. **Home** - Landing page with features
2. **Login/Register** - Authentication
3. **Dashboard** - Overview with today's meals, stats, quick actions
4. **Profile** - Complete profile editor with validation
5. **Nutrition Targets** - BMR, TDEE, macros, micronutrients with methodology
6. **Discover Recipes** - Search, filter, paginate 6,865+ recipes
7. **Recipe Detail** - Ingredients, instructions, nutrition (with unavailable states)
8. **Recommendations** - Personalized with filters and explanations
9. **Meal Planner** - Weekly grid with drag-drop, completion tracking
10. **Meal Plan Detail** - Full plan view with nutrition summary
11. **Nutrition Analysis** - Per-recipe breakdown with provenance
12. **Saved Recipes** - Personal cookbook with filters
13. **Meal History** - Consumption tracking with daily/weekly views
14. **Settings** - Theme, notifications, privacy, data management

## 🔧 Development

### Adding New API Endpoints

1. Create route in `backend/app/api/`
2. Add service logic in `backend/app/services/`
3. Register router in `backend/app/main.py`
4. Add TypeScript types in `frontend/src/types/index.ts`
5. Add API calls in `frontend/src/services/api.ts`
6. Create/update pages in `frontend/src/pages/`

### Reusing Existing Python Modules

The backend services directly import and use the existing Phase 3/4/5 modules:

```python
# In backend services
from personalization.nutrition_targets import NutritionTargetCalculator
from recommendation import ContentBasedRecipeRecommender
from personalization.meal_planner import MealPlanner
```

No JavaScript reimplementation of ML/nutrition logic.

## 📊 Dataset Sources

- **Recipes**: 6,865 Indian recipes with cuisine, course, diet labels
- **Ingredients**: 90,862 canonical ingredient records
- **IFCT 2017**: 528 food items with 9 nutrients per 100g edible portion
- **ICMR 2020**: Recommended Dietary Allowances for Indians

All datasets are frozen with SHA-256 hash verification.

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Must be 3.11+

# Reinstall dependencies
cd backend
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend build fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database errors
```bash
# Reset database (loses all data!)
rm backend/data/app.db
# Restart backend - will reinitialize
```

### CORS errors
- Ensure frontend runs on port 5173
- Check `CORS_ORIGINS` in `backend/app/core/config.py`

## 📄 License

This project is for educational/research purposes. See individual dataset licenses for data usage rights.

## 🙏 Acknowledgments

- ICMR 2020 Nutrient Requirements for Indians
- IFCT 2017 Indian Food Composition Tables
- Original Phase 1-6 implementation
- Open source libraries: FastAPI, React, Vite, Tailwind, Recharts, Lucide

## 📞 Support

For issues:
1. Check the troubleshooting section
2. Review backend logs in the terminal
3. Check browser console for frontend errors
4. Verify all prerequisites are installed

---

**Built with ❤️ for personalized Indian nutrition**