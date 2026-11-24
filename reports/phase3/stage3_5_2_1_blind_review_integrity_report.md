# Stage 3.5.2.1: Blind Review Integrity Report

**Date:** 2026-11-18  
**Objective:** Verify the actual blind-review implementation against security requirements

---

## Executive Summary

**The current implementation is a workflow convention (UI toggle), NOT enforced access isolation.** The blind-review mechanism relies on:
- A sidebar checkbox visible only to AUDITOR role
- Session-state dictionaries (`primary_decisions`) stored in browser memory
- UI conditional rendering to hide primary decisions
- Single shared parquet persistence for all reviewers

**No cryptographic, server-side, or process isolation exists.** A determined user can bypass blind review by:
- Changing role dropdown from AUDITOR to PRIMARY
- Disabling blind mode checkbox
- Accessing session state via browser dev tools
- Reading the shared parquet files directly

---

## Requirements vs Implementation

| Requirement | Implemented? | Mechanism | Assessment |
|-------------|--------------|-----------|------------|
| Auditor cannot see primary decisions before submission | ⚠️ Partial | UI hides via `blind_mode` checkbox | Bypassable via role change / dev tools |
| Primary cannot see auditor decisions before submission | ❌ No | Auditor decisions stored alongside primary; primary can see if not in blind mode | No enforcement |
| Hidden decisions not exposed via dashboard/filters/exports | ❌ No | Dashboard shows total decisions count; filters show all; export writes all | Exposed |
| Reviewer identity recorded | ✅ Yes | `reviewer_id` and `reviewer_role` fields on every decision | Satisfied |
| Both independent submissions preserved | ✅ Yes | Parallel storage in parquet (not replaced) | Satisfied |
| Adjudication only after independent submissions | ⚠️ Partial | Adjudicator sees all; no enforcement of sequence | Convention only |
| Unauthorized role changes cannot bypass | ❌ No | Role is a sidebar dropdown with no auth | Trivially bypassable |

---

## Detailed Code Inspection

### 1. Role Selection — No Authentication

**File:** `app/ingredient_review_app.py`, lines 389-395

```python
role_options = ["PRIMARY", "AUDITOR", "ADJUDICATOR"]
role = st.sidebar.selectbox(
    "Role",
    role_options,
    index=role_options.index(st.session_state.reviewer_role) if st.session_state.reviewer_role in role_options else 0
)
st.session_state.reviewer_role = role
```

**Issue:** Role is a simple dropdown. Any user can switch from AUDITOR → PRIMARY → ADJUDICATOR at any time. No password, token, or server-side authorization.

### 2. Blind Mode Toggle — User-Controlled

**File:** `app/ingredient_review_app.py`, lines 404-412

```python
if st.session_state.reviewer_role == "AUDITOR":
    blind_mode = st.sidebar.checkbox(
        "Blind Audit Mode",
        value=st.session_state.blind_mode,
        help="Hide primary reviewer decisions and rationales"
    )
    st.session_state.blind_mode = blind_mode
```

**Issue:** Blind mode is a checkbox the auditor can uncheck at any time. No enforced policy.

### 3. Primary Decision Storage — Browser Session State

**File:** `app/ingredient_review_app.py`, lines 199-200, 798-799

```python
# Session state init
if 'primary_decisions' not in st.session_state:
    st.session_state.primary_decisions = {}  # review_unit_id -> decision dict

# Store after PRIMARY saves
if st.session_state.reviewer_role == "PRIMARY" and not st.session_state.blind_mode:
    st.session_state.primary_decisions[review_unit_id] = decision_dict
```

**Issue:** Primary decisions stored in `st.session_state` — browser memory, accessible via dev tools. Not encrypted, not server-side.

### 4. Blind Mode Rendering — UI Conditional Only

**File:** `app/ingredient_review_app.py`, lines 648-654

```python
if st.session_state.blind_mode and st.session_state.reviewer_role == "AUDITOR":
    primary_decision = st.session_state.primary_decisions.get(review_unit_id)
    if primary_decision:
        st.info("🔒 Blind mode: Primary reviewer's decision and rationale are hidden")
    else:
        st.warning("⚠️ No primary decision recorded yet for this unit")
```

**Issue:** Only hides UI display. The primary decision data is still in session state and parquet. An auditor can:
- Uncheck blind mode checkbox
- Switch to PRIMARY role
- Inspect session state via browser console
- Read parquet file directly

### 5. Persistence — Shared Parquet File

**File:** `app/ingredient_review_app.py`, lines 780-791

```python
existing_df = st.session_state.decisions_df
if existing_df is not None and not existing_df.empty:
    if not (st.session_state.blind_mode and st.session_state.reviewer_role == "AUDITOR"):
        existing_df = existing_df[
            ~((existing_df['review_unit_id'] == review_unit_id) & 
              (existing_df['reviewer_id'] == st.session_state.reviewer_id))
        ]
decisions_df = pd.concat([existing_df, pd.DataFrame([decision_dict])], ignore_index=True)
save_decisions(decisions_df)
```

**Issue:** 
- Both primary and auditor decisions written to **same parquet file** (`review_decisions.parquet`)
- Auditor decisions append alongside primary (not replacing when blind mode on)
- Primary can see auditor decisions by reading parquet or via dashboard
- No isolation at storage layer

### 6. Dashboard Exposure

**File:** `app/ingredient_review_app.py`, lines 370-377 (sidebar progress)

```python
total = len(st.session_state.filtered_units) if st.session_state.filtered_units is not None else 0
completed = 0
if st.session_state.decisions_df is not None and not st.session_state.decisions_df.empty:
    completed = st.session_state.decisions_df['review_unit_id'].nunique()
st.sidebar.metric("Progress", f"{completed}/{total}")
```

**Issue:** Progress metric counts **all decisions** from all reviewers. Primary sees auditor's work counted.

### 7. Filter/Export Exposure

**File:** `app/ingredient_review_app.py`, lines 423-425 (status filter)

```python
statuses = ['All', 'PENDING', 'IN_REVIEW', 'COMPLETED', 'ESCALATED', 'DRAFT']
status = st.sidebar.selectbox("Review Status", statuses, ...)
```

**Issue:** Status filter shows decisions from all reviewers. Export functions would include all.

---

## Attack Vectors (Bypass Methods)

| Method | Difficulty | Result |
|--------|------------|--------|
| Change role dropdown to PRIMARY | Trivial (1 click) | See all primary decisions, disable blind mode |
| Uncheck blind mode checkbox | Trivial (1 click) | See primary decisions immediately |
| Browser dev tools → Application → Session Storage | Low (F12) | Read `primary_decisions` dict directly |
| Read `review_decisions.parquet` directly | Low (file system) | See all decisions from all reviewers |
| Switch to ADJUDICATOR role | Trivial (1 click) | See all decisions with rationale |
| Modify `st.session_state.blind_mode` via console | Low | `st.session_state.blind_mode = false` |

---

## What IS Working Correctly

| Feature | Implementation |
|---------|----------------|
| Reviewer identity recorded | `reviewer_id` + `reviewer_role` on every decision |
| Both submissions preserved | Auditor decisions append (not replace) in parquet when blind mode on |
| Adjudicator sees all | `get_all_decisions_for_unit()` returns all, shown for ADJUDICATOR role |
| `is_blind_review` flag recorded | Boolean field on decision record |
| `reviewer_role` recorded | PRIMARY/AUDITOR/ADJUDICATOR on every decision |
| Primary decisions stored for reference | `primary_decisions` session state dict |
| Blind mode UI indicator | Shows "🔒 Blind mode active" when enabled |

---

## Limitation Summary

| Aspect | Status | Comment |
|--------|--------|---------|
| **Access Control** | ❌ None | Role is UI dropdown, no auth |
| **Data Isolation** | ❌ None | Shared parquet, shared session state |
| **Blind Enforcement** | ❌ None | Checkbox toggle, user-controlled |
| **Audit Trail** | ✅ Complete | All decisions with role, blind flag, timestamps |
| **Parallel Submissions** | ✅ Preserved | Both stored in parquet |
| **Adjudication Support** | ✅ Available | ADJUDICATOR sees all |
| **Process Convention** | ⚠️ Documented | "Blind mode" checkbox + role selection |

---

## Accurate Classification

**The blind-review mechanism is a process convention documented in the UI, not an enforced security boundary.**

It supports the *intended workflow* when:
1. Reviewers are trustworthy and follow protocol
2. Roles are assigned and adhered to by convention
3. The checkbox is used as intended

It does **not** provide:
- Cryptographic isolation
- Server-enforced access control
- Tamper-proof audit of blindness
- Protection against malicious or careless reviewers

---

## Recommendation for Pilot

For a controlled 50-unit pilot with known, committed reviewers:

1. **Document the convention** — Pilot protocol explicitly states: "Auditor MUST keep blind mode enabled; role changes prohibited during review session"
2. **Physical separation** — Primary and Auditor review on different machines/sessions
3. **Post-hoc verification** — Compare `is_blind_review=True` decisions with `reviewer_role=AUDITOR` in parquet after pilot
4. **No automated enforcement** — Accept as documented limitation

**Do not claim** "enforced blind review" or "access isolation" in any formal report.

---

*End of Blind Review Integrity Report*