# Stage 3.1: Workload Feasibility Assessment

**Date:** 2026-11-18  
**Based on:** Stage 3.1 Design Audit findings and corrected Stage 2.3 data

---

## 1. Corrected Workload Baseline

### 1.1 Verified Review Unit Counts (Corrected)

| Priority Band | Score Range | Review Units | % of Total |
|---------------|-------------|--------------|------------|
| Critical (80-100) | 25 | 0.3% |
| High (60-79) | 95 | 1.3% |
| Medium (40-59) | 1,599 | 22.3% |
| Standard (20-39) | 5,446 | 76.0% |
| Low (0-19) | 0 | 0.0% |
| **Total** | **7,165** | **100%** |

### 1.2 By Match Method

| Match Method | Units | % |
|--------------|-------|---|
| EXACT | 46 | 0.6% |
| SYNONYM | 21 | 0.3% |
| TOKEN_EQUIVALENT | 149 | 2.1% |
| TOKEN_SIMILARITY | 6,949 | 97.0% |
| **Total** | **7,165** | **100%** |

### 1.3 By Preparation State

| Prep State | Units | % |
|------------|-------|---|
| NOT_SPECIFIED | 5,413 | 75.5% |
| FRESH | 462 | 6.4% |
| POWDERED | 361 | 5.0% |
| DRIED | 268 | 3.7% |
| ROASTED | 90 | 1.3% |
| COOKED | 107 | 1.5% |
| SOAKED | 174 | 2.4% |
| RAW | 70 | 1.0% |
| GROUND | 82 | 1.1% |
| Others | 83 | 1.2% |

---

## 2. Corrected Workload Estimates

### 2.1 Time Per Unit (Realistic)

| Priority Band | Est. Time/Unit | Basis |
|---------------|----------------|-------|
| Critical | 8 min | EXACT + FRESH/RAW, quick verification |
| High | 10 min | EXACT + NOT_SPECIFIED, check prep evidence |
| Medium | 12 min | TOKEN_EQUIVALENT/SYNONYM, moderate evidence |
| Standard | 15 min | TOKEN_SIMILARITY, careful evidence eval |
| Low | 10 min | Most will be REJECTED/AMBIGUOUS, quick triage |

### 2.2 Total Effort (Single Review)

| Priority Band | Units | Time/Unit | Total Hours |
|---------------|-------|-----------|-------------|
| Critical | 25 | 8 min | 3.3 hrs |
| High | 95 | 10 min | 15.8 hrs |
| Medium | 1,599 | 12 min | 319.8 hrs |
| Standard | 5,446 | 15 min | 1,361.5 hrs |
| Low | 0 | — | 0 hrs |
| **Total** | **7,165** | **~11.5 min avg** | **~1,700 hrs** |

### 1.3 With Audit Overhead (2× Review)

| Component | Hours |
|-----------|-------|
| Primary review | 1,700 hrs |
| Second review (20% audit) | 340 hrs |
| Disagreement resolution | 50 hrs |
| Calibration/training | 40 hrs |
| **Total** | **~2,080 hrs** |

---

## 3. Team Capacity Scenarios

### 3.1 Scenario A: 8 Reviewers (Original Plan)

| Parameter | Value |
|-----------|-------|
| Reviewers | 8 |
| Effective hrs/day/reviewer | 3 hrs (after breaks, fatigue) |
| Days/week | 5 |
| Weekly capacity | 8 × 3 × 5 = 120 hrs |
| **Duration (primary only)** | 1,700 / 120 = **14.2 weeks** |
| **Duration (with audit)** | 2,080 / 120 = **17.3 weeks** |

### 3.2 Scenario B: 4 Reviewers (Realistic Minimum)

| Parameter | Value |
|-----------|-------|
| Reviewers | 4 |
| Effective hrs/day/reviewer | 2.5 hrs |
| Days/week | 5 |
| Weekly capacity | 4 × 2.5 × 5 = 50 hrs |
| **Duration (primary only)** | 1,700 / 50 = **34 weeks** |
| **Duration (with audit)** | 2,080 / 50 = **41.6 weeks** |

### 3.3 Scenario C: Single Reviewer (Fallback)

| Parameter | Value |
|-----------|-------|
| Reviewers | 1 |
| Effective hrs/day | 2 hrs |
| Days/week | 5 |
| Weekly capacity | 10 hrs |
| **Duration (primary only)** | 1,700 / 10 = **170 weeks (3.3 years)** |
| **Duration (with audit)** | 2,080 / 10 = **208 weeks (4 years)** |

### 3.3 Scenario D: 2 Reviewers (Minimum Viable)

| Parameter | Value |
|-----------|-------|
| Reviewers | 2 |
| Effective hrs/day | 2.5 hrs |
| Days/week | 5 |
| Weekly capacity | 25 hrs |
| **Duration (primary)** | 1,700 / 25 = **68 weeks (1.3 years)** |
| **Duration (with audit)** | 2,080 / 25 = **83 weeks (1.6 years)** |

---

## 4. Reviewer Requirements

### 4.1 Minimum Team Composition

| Role | Count | Specialization |
|-------|-------|----------------|
| Senior Reviewer (Lead) | 1 | Escalation, CONFLICT resolution, final sign-off |
| Domain Reviewers | 3–5 | Spices, Vegetables, Grains, Meat/Fish, Oils/Dairy |
| General Reviewers | 2–4 | Remaining categories |
| **Total** | **5–7** | Minimum viable team |

### 4.2 Skill Requirements

| Requirement | Justification |
|-------------|---------------|
| Food science/nutrition background | Species, prep-state, nutrient profile knowledge |
| IFCT 2017 familiarity | Table structure, food groups, codes |
| Indian cuisine knowledge | Hindi names, regional variants, preparations |
| Attention to detail | 50+ char rationale, evidence citation |
| Protocol adherence | 60s min review, no forced decisions |

---

## 5. Throughput Sensitivity Analysis

### 5.1 Units/Hour Sensitivity

| Units/Hour | Primary Review Hours | Weeks (8 reviewers) | Weeks (4 reviewers) |
|------------|---------------------|---------------------|---------------------|
| 20 u/hr (conservative) | 358 hrs | 15 weeks | 29 weeks |
| 30 u/hr (target) | 239 hrs | 10 weeks | 20 weeks |
| 40 u/hr (optimistic) | 179 hrs | 7.5 weeks | 15 weeks |

### 5.2 Break-even Analysis

| Reviewers | Weeks (30 u/hr) | Weeks (20 u/hr) | Risk |
|-----------|-----------------|-----------------|------|
| 8 | 10 weeks | 15 weeks | Low if all available |
| 6 | 13 weeks | 20 weeks | Medium |
| 4 | 20 weeks | 30 weeks | High |
| 2 | 40 weeks | 60 weeks | Critical |

---

## 6. Cost Estimation

### 6.1 Labor Cost (INR)

| Role | Hourly Rate (INR) | Hours | Cost |
|------|-------------------|-------|------|
| Senior Reviewer | 2,000 | 200 | 400,000 |
| Domain Reviewers (4) | 1,500 | 1,700 | 10,200,000 |
| General Reviewers (3) | 1,000 | 1,700 | 5,100,000 |
| QA Lead (audit) | 2,500 | 100 | 250,000 |
| **Total Labor** | | | **~15.95 Cr** |

### 6.2 Infrastructure (Annual)

| Item | Cost |
|------|------|
| Compute (review workbench) | 2,00,000 |
| Storage (Parquet + audit) | 50,000 |
| Backup/DR | 1,00,000 |
| **Total Infra** | **3,50,000** |

---

## 6. Risk-Adjusted Timeline

### 6.1 Probabilistic Timeline (Monte Carlo style)

| Percentile | 8 Reviewers | 4 Reviewers | 2 Reviewers |
|------------|-------------|-------------|-------------|
| P10 (optimistic) | 10 weeks | 20 weeks | 52 weeks |
| P50 (median) | 17 weeks | 34 weeks | 68 weeks |
| P90 (pessimistic) | 26 weeks | 52 weeks | 104 weeks |

**Recommendation:** Plan for **P90 with 4 reviewers = 52 weeks (1 year)** as baseline.

---

## 6. Go/No-Go Decision Matrix

| Condition | Go | No-Go |
|-----------|-----|-------|
| ≥ 4 committed reviewers | ✅ | ❌ |
| Design corrections complete | ✅ | ❌ |
| Workbench prototype tested | ✅ | ❌ |
| Calibration materials ready | ✅ | ❌ |
| QA sign-off on design | ✅ | ❌ |

**Current Status:** ❌ No-Go (design corrections incomplete, reviewers not confirmed)

---

## 7. Recommendation

### 7.1 Minimum Viable Path

1. **Confirm 4 committed reviewers** (minimum viable)
2. **Complete design corrections** (6–8 person-days)
3. **Build workbench prototype** (2 weeks)
4. **Run pilot** (50 units, 2 reviewers, 1 week)
5. **Calibrate throughput** → adjust timeline
4. **Full review launch**

### 7.2 If Only 2 Reviewers Available

- Extend timeline to **18–24 months**
- Defer Low/Ambiguous/Unmatched to Phase 3b
- Focus on Critical/High/Medium (1,720 units = 144 hrs → 6 weeks)

### 7.3 If No External Reviewers

- Internal team only: **Not feasible** for full scope
- Option: Automate Standard/Low tiers with ML, human-review only Critical/High/Medium
- Hybrid: ML pre-filter + human verification

---

## 8. Final Recommendation

**Verdict: CONDITIONAL GO — with 4+ confirmed reviewers and completed design corrections**

| Condition | Status |
|-----------|--------|
| Design corrections | ❌ Incomplete |
| Reviewer commitments | ❌ Unconfirmed |
| Workbench prototype | ❌ Not built |
| Calibration materials | ❌ Not ready |

**Action Required:** Complete design corrections (6–8 person-days) and secure ≥4 reviewer commitments before workbench development begins.

---

*End of Workload Feasibility Assessment*