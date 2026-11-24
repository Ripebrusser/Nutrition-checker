"""
Ingredient Review Workbench - Streamlit Application

A web-based interface for reviewing and approving ingredient-to-IFCT mappings.
Implements Stage 3.5.2.2 enforced blind-review isolation for controlled pilot.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid
import os

# Page configuration
st.set_page_config(
    page_title="Ingredient Review Workbench",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Configuration ───

# File paths
CANDIDATES_PATH = "data/interim/phase3/stage2_3/ifct_match_candidates.parquet"
UNMATCHED_PATH = "data/interim/phase3/stage2_3/unmatched_ingredients.parquet"
IFCT_PATH = "data/interim/ifct_final_candidate/ifct_table1_candidate.parquet"
SYNONYM_PATH = "data/interim/phase2/ingredient_synonyms.csv"
HOUSEHOLD_PATH = "data/interim/phase2/household_measurements.csv"

# Separate persistence directories per reviewer role
DECISIONS_BASE_DIR = Path("data/interim/phase3/decisions")
DECISIONS_BASE_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_DECISIONS_DIR = DECISIONS_BASE_DIR / "primary"
AUDITOR_DECISIONS_DIR = DECISIONS_BASE_DIR / "auditor"
ADJUDICATION_DECISIONS_DIR = DECISIONS_BASE_DIR / "adjudication"
MERGED_DECISIONS_DIR = DECISIONS_BASE_DIR / "merged"

for d in [PRIMARY_DECISIONS_DIR, AUDITOR_DECISIONS_DIR, ADJUDICATION_DECISIONS_DIR, MERGED_DECISIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Reviewer configuration (in production, use environment variables or secure config)
REVIEWER_CONFIG = {
    "primary": {
        "role": "PRIMARY",
        "decisions_dir": PRIMARY_DECISIONS_DIR,
        "allowed_roles": ["PRIMARY"],
    },
    "auditor": {
        "role": "AUDITOR",
        "decisions_dir": AUDITOR_DECISIONS_DIR,
        "allowed_roles": ["AUDITOR"],
    },
    "adjudicator": {
        "role": "ADJUDICATOR",
        "decisions_dir": ADJUDICATION_DECISIONS_DIR,
        "allowed_roles": ["ADJUDICATOR"],
    }
}

# Submission state tracking
SUBMISSION_STATE_FILE = DECISIONS_BASE_DIR / "submission_states.parquet"

class SubmissionState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PRIMARY_SUBMITTED = "PRIMARY_SUBMITTED"
    AUDITOR_SUBMITTED = "AUDITOR_SUBMITTED"
    BOTH_SUBMITTED = "BOTH_SUBMITTED"
    READY_FOR_ADJUDICATION = "READY_FOR_ADJUDICATION"
    ADJUDICATED = "ADJUDICATED"

# Valid state transitions
VALID_TRANSITIONS = {
    SubmissionState.NOT_STARTED: [SubmissionState.PRIMARY_SUBMITTED, SubmissionState.AUDITOR_SUBMITTED],
    SubmissionState.PRIMARY_SUBMITTED: [SubmissionState.BOTH_SUBMITTED],
    SubmissionState.AUDITOR_SUBMITTED: [SubmissionState.BOTH_SUBMITTED],
    SubmissionState.BOTH_SUBMITTED: [SubmissionState.READY_FOR_ADJUDICATION],
    SubmissionState.READY_FOR_ADJUDICATION: [SubmissionState.ADJUDICATED],
    SubmissionState.ADJUDICATED: [],
}

# ─── Constants ───

class MatchMethod(str, Enum):
    EXACT = "EXACT"
    SYNONYM = "SYNONYM"
    TOKEN_EQUIVALENT = "TOKEN_EQUIVALENT"
    TOKEN_SIMILARITY = "TOKEN_SIMILARITY"
    FUZZY = "FUZZY"

class MappingDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AMBIGUOUS = "AMBIGUOUS"
    UNMATCHED = "UNMATCHED"
    NO_IFCT_EQUIVALENT = "NO_IFCT_EQUIVALENT"
    CONFLICT = "CONFLICT"

class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"

class PreparationState(str, Enum):
    RAW = "RAW"
    FRESH = "FRESH"
    DRIED = "DRIED"
    POWDERED = "POWDERED"
    GROUND = "GROUND"
    ROASTED = "ROASTED"
    FRIED = "FRIED"
    BOILED = "BOILED"
    COOKED = "COOKED"
    FERMENTED = "FERMENTED"
    SPROUTED = "SPROUTED"
    SOAKED = "SOAKED"
    BLANCHED = "BLANCHED"
    MARINATED = "MARINATED"
    NOT_SPECIFIED = "NOT_SPECIFIED"
    UNKNOWN = "UNKNOWN"

# ─── Data Classes ───

@dataclass
class ReviewDecision:
    """A reviewer's decision on a candidate mapping."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    review_unit_id: str = ""
    reviewer_id: str = ""
    reviewer_role: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    workflow_status: WorkflowStatus = WorkflowStatus.DRAFT
    mapping_decision: MappingDecision = MappingDecision.UNMATCHED
    previous_status: str = ""
    previous_decision: str = ""
    rationale: str = ""
    confidence: int = 3
    alternative_ifct_code: str = ""
    evidence_references: List[str] = field(default_factory=list)
    uncertainty_notes: str = ""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    duration_seconds: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_blind_review: bool = True
    
    def to_dict(self) -> dict:
        return {
            'decision_id': self.decision_id,
            'review_unit_id': self.review_unit_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_role': self.reviewer_role,
            'timestamp': self.timestamp,
            'workflow_status': self.workflow_status.value,
            'mapping_decision': self.mapping_decision.value,
            'previous_status': self.previous_status,
            'previous_decision': self.previous_decision,
            'rationale': self.rationale,
            'confidence': self.confidence,
            'alternative_ifct_code': self.alternative_ifct_code,
            'evidence_references': self.evidence_references,
            'uncertainty_notes': self.uncertainty_notes,
            'session_id': self.session_id,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_blind_review': self.is_blind_review,
        }

# ─── Session State Management ───

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'reviewer_id' not in st.session_state:
        st.session_state.reviewer_id = ""
    if 'reviewer_role' not in st.session_state:
        st.session_state.reviewer_role = ""
    if 'current_unit_idx' not in st.session_state:
        st.session_state.current_unit_idx = 0
    if 'review_units' not in st.session_state:
        st.session_state.review_units = None
    if 'filtered_units' not in st.session_state:
        st.session_state.filtered_units = None
    if 'current_decision' not in st.session_state:
        st.session_state.current_decision = None
    if 'decisions_df' not in st.session_state:
        st.session_state.decisions_df = None
    if 'show_candidate_details' not in st.session_state:
        st.session_state.show_candidate_details = True
    if 'filter_settings' not in st.session_state:
        st.session_state.filter_settings = {
            'priority': 'All',
            'ingredient': '',
            'prep_state': 'All',
            'ifct_group': 'All',
            'match_method': 'All',
            'confidence': 'All',
            'status': 'All'
        }
    if 'submission_states' not in st.session_state:
        st.session_state.submission_states = {}

# ─── Authentication & Role Enforcement ───

def load_reviewer_config() -> Dict:
    """Load reviewer configuration from environment or config file."""
    # In production, load from secure config file or environment variables
    # For pilot, we use a simple local config approach
    config = {}
    
    # Check for reviewer credentials in environment
    for role_key in ["primary", "auditor", "adjudicator"]:
        reviewer_id = os.environ.get(f"REVIEWER_{role_key.upper()}_ID", "")
        if reviewer_id:
            config[role_key] = {
                "role": role_key.upper(),
                "reviewer_id": reviewer_id,
                "decisions_dir": Path(f"data/interim/phase3/decisions/{role_key}"),
                "allowed_roles": [role_key.upper()],
            }
    
    # Fallback to local config file
    if not config:
        config_path = Path("config/reviewer_config.json")
        if config_path.exists():
            with open(config_path) as f:
                loaded = json.load(f)
                for role_key, cfg in loaded.items():
                    cfg["decisions_dir"] = Path(cfg["decisions_dir"])
                    config[role_key] = cfg
    
    # Default fallback for development (NOT for production)
    if not config:
        st.warning("⚠️ No reviewer configuration found. Using default development config.")
        config = {
            "primary": {"role": "PRIMARY", "reviewer_id": "primary_reviewer", "decisions_dir": PRIMARY_DECISIONS_DIR, "allowed_roles": ["PRIMARY"]},
            "auditor": {"role": "AUDITOR", "reviewer_id": "auditor_reviewer", "decisions_dir": AUDITOR_DECISIONS_DIR, "allowed_roles": ["AUDITOR"]},
            "adjudicator": {"role": "ADJUDICATOR", "reviewer_id": "adjudicator_reviewer", "decisions_dir": ADJUDICATION_DECISIONS_DIR, "allowed_roles": ["ADJUDICATOR"]},
        }
    
    return config

REVIEWER_CONFIG = load_reviewer_config()

def authenticate_reviewer(entered_id: str) -> Optional[Dict]:
    """Authenticate reviewer by ID against configured reviewers."""
    for role_key, cfg in REVIEWER_CONFIG.items():
        if cfg.get("reviewer_id") == entered_id:
            return {"role_key": role_key, **cfg}
    return None

def get_decisions_dir(role_key: str) -> Path:
    """Get the decisions directory for a role."""
    return REVIEWER_CONFIG[role_key]["decisions_dir"]

def get_decisions_file(role_key: str) -> Path:
    """Get the decisions file path for a role."""
    return get_decisions_dir(role_key) / "review_decisions.parquet"

def get_history_file(role_key: str) -> Path:
    """Get the history file path for a role."""
    return get_decisions_dir(role_key) / "review_decisions_history.parquet"

def load_submission_states() -> Dict:
    """Load submission states from file."""
    if SUBMISSION_STATE_FILE.exists():
        try:
            df = pd.read_parquet(SUBMISSION_STATE_FILE)
            return dict(zip(df['review_unit_id'], df['state']))
        except Exception:
            return {}
    return {}

def save_submission_states(states: Dict):
    """Save submission states to file."""
    try:
        df = pd.DataFrame([
            {"review_unit_id": k, "state": v.value if isinstance(v, SubmissionState) else v}
            for k, v in states.items()
        ])
        df.to_parquet(SUBMISSION_STATE_FILE, index=False)
    except Exception as e:
        st.error(f"Failed to save submission states: {e}")

def get_submission_state(review_unit_id: str) -> SubmissionState:
    """Get submission state for a review unit."""
    states = load_submission_states()
    state_str = states.get(review_unit_id, SubmissionState.NOT_STARTED.value)
    try:
        return SubmissionState(state_str)
    except ValueError:
        return SubmissionState.NOT_STARTED

def update_submission_state(review_unit_id: str, reviewer_role: str):
    """Update submission state after a reviewer submits."""
    current = get_submission_state(review_unit_id)
    role_key = reviewer_role.lower()
    
    if current == SubmissionState.NOT_STARTED:
        if role_key == "primary":
            new_state = SubmissionState.PRIMARY_SUBMITTED
        elif role_key == "auditor":
            new_state = SubmissionState.AUDITOR_SUBMITTED
        else:
            return
    elif current == SubmissionState.PRIMARY_SUBMITTED and role_key == "auditor":
        new_state = SubmissionState.BOTH_SUBMITTED
    elif current == SubmissionState.AUDITOR_SUBMITTED and role_key == "primary":
        new_state = SubmissionState.BOTH_SUBMITTED
    else:
        return
    
    states = load_submission_states()
    states[review_unit_id] = new_state.value
    save_submission_states(states)
    st.session_state.submission_states[review_unit_id] = new_state

def can_adjudicate(review_unit_id: str) -> bool:
    """Check if a unit is ready for adjudication."""
    state = get_submission_state(review_unit_id)
    return state in [SubmissionState.BOTH_SUBMITTED, SubmissionState.READY_FOR_ADJUDICATION]

def set_adjudication_ready(review_unit_id: str):
    """Mark unit as ready for adjudication."""
    states = load_submission_states()
    states[review_unit_id] = SubmissionState.READY_FOR_ADJUDICATION.value
    save_submission_states(states)

def set_adjudicated(review_unit_id: str):
    """Mark unit as adjudicated."""
    states = load_submission_states()
    states[review_unit_id] = SubmissionState.ADJUDICATED.value
    save_submission_states(states)

# ─── Decision Persistence (Role-Isolated) ───

def load_decisions(role_key: str) -> pd.DataFrame:
    """Load decisions for a specific reviewer role."""
    decisions_file = get_decisions_file(role_key)
    if decisions_file.exists():
        try:
            df = pd.read_parquet(decisions_file)
            return df
        except Exception as e:
            st.warning(f"Could not load decisions for {role_key}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def save_decisions(role_key: str, df: pd.DataFrame):
    """Save decisions for a specific reviewer role."""
    decisions_file = get_decisions_file(role_key)
    history_file = get_history_file(role_key)
    
    try:
        df.to_parquet(decisions_file, index=False)
        
        # Also save history
        if history_file.exists():
            hist = pd.read_parquet(history_file)
            hist = pd.concat([hist, df], ignore_index=True)
        else:
            hist = df.copy()
        hist.to_parquet(history_file, index=False)
    except Exception as e:
        st.error(f"Failed to save decisions for {role_key}: {e}")

def get_existing_decision(decisions_df: pd.DataFrame, review_unit_id: str, reviewer_id: str) -> Optional[pd.Series]:
    """Get existing decision for a review unit by this reviewer."""
    if decisions_df is not None and not decisions_df.empty:
        matches = decisions_df[
            (decisions_df['review_unit_id'] == review_unit_id) & 
            (decisions_df['reviewer_id'] == reviewer_id)
        ]
        if not matches.empty:
            return matches.iloc[-1]
    return None

def get_all_decisions_for_unit(review_unit_id: str) -> pd.DataFrame:
    """Get all decisions for a review unit across all roles (for adjudication)."""
    all_decisions = []
    for role_key in ["primary", "auditor", "adjudicator"]:
        df = load_decisions(role_key)
        if not df.empty:
            matches = df[df['review_unit_id'] == review_unit_id]
            if not matches.empty:
                all_decisions.append(matches)
    
    if all_decisions:
        return pd.concat(all_decisions, ignore_index=True).sort_values('timestamp')
    return pd.DataFrame()

# ─── Data Loading ───

@st.cache_data
def load_review_units() -> pd.DataFrame:
    """Load and prepare review units from Stage 2.3 output."""
    df = pd.read_parquet("data/interim/phase3/stage2_3/ifct_match_candidates.parquet")
    
    # Create review_unit_id if not present
    if 'review_unit_id' not in df.columns:
        df['review_unit_id'] = df.groupby(['primary_ingredient', 'preparation_state', 'ifct_food_code']).ngroup().apply(lambda x: f"RU_{x:06d}")
    
    # Ensure required columns exist
    required_cols = [
        'review_unit_id', 'recipe_id', 'primary_ingredient', 'preparation_state',
        'ifct_food_code', 'ifct_food_name', 'ifct_food_group', 'match_method',
        'similarity_score', 'provisional_confidence', 'requires_review',
        'match_method', 'evidence', 'acceptance_evidence', 'primary_ingredient',
        'original_ingredient', 'normalized_ingredient', 'recipe_id',
        'preparation_confidence', 'ambiguity_flags', 'extracted_aliases',
        'food_group_compat', 'prep_state_compat', 'taxonomy_category',
        'provisional_confidence', 'requires_review', 'acceptance_evidence'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            if col in ['evidence', 'acceptance_evidence']:
                df[col] = [{} for _ in range(len(df))]
            elif col in ['ambiguity_flags', 'extracted_aliases']:
                df[col] = [[] for _ in range(len(df))]
            else:
                df[col] = None
    
    # Ensure proper types
    df['similarity_score'] = pd.to_numeric(df['similarity_score'], errors='coerce').fillna(0.0)
    df['provisional_confidence'] = df['provisional_confidence'].fillna('LOW')
    df['requires_review'] = df['requires_review'].fillna(True)
    df['preparation_state'] = df['preparation_state'].fillna('NOT_SPECIFIED')
    
    # Ensure evidence columns are dicts
    for col in ['evidence', 'acceptance_evidence']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if isinstance(x, dict) else {})
    
    return df

@st.cache_data
def load_ifct_data() -> pd.DataFrame:
    """Load IFCT reference data."""
    df = pd.read_parquet("data/interim/ifct_final_candidate/ifct_table1_candidate.parquet")
    return df

@st.cache_data
def load_unmatched() -> pd.DataFrame:
    """Load unmatched ingredients."""
    return pd.read_parquet("data/interim/phase3/stage2_3/unmatched_ingredients.parquet")

# ─── Safeguard Functions ───

def check_auto_accept_eligibility(candidate: pd.Series) -> Tuple[bool, List[str]]:
    """Safeguard 1: Check if a candidate is eligible for auto-accept."""
    reasons = []
    
    prep_state = candidate.get('preparation_state', 'NOT_SPECIFIED')
    if prep_state == 'NOT_SPECIFIED':
        reasons.append("NOT_SPECIFIED preparation state cannot be auto-accepted")
    
    if candidate.get('match_method') != 'EXACT':
        reasons.append(f"Match method is {candidate.get('match_method')}, not EXACT")
    
    if candidate.get('similarity_score', 0) != 1.0:
        reasons.append(f"Similarity is {candidate.get('similarity_score')}, not 1.0")
    
    eligible = len(reasons) == 0
    return eligible, reasons

REQUIRED_EVIDENCE_FIELDS = [
    'ifct_food_code', 'ifct_food_name', 'ifct_food_group',
    'ifct_source_page', 'ifct_table_number',
    'match_method', 'similarity_score',
    'preparation_state', 'preparation_confidence',
    'prep_state_compat', 'extracted_aliases',
    'ambiguity_flags', 'species_verification',
    'edible_part_verification', 'prep_compatibility_evidence'
]

def validate_accepted_evidence(evidence_refs: List[str]) -> Tuple[bool, List[str]]:
    """Safeguard 4: Validate that ACCEPTED decision has all 15 mandatory evidence fields."""
    evidence_set = set(evidence_refs)
    missing = [f for f in REQUIRED_EVIDENCE_FIELDS if f not in evidence_set]
    return len(missing) == 0, missing

ALLOWED_WORKFLOW_TRANSITIONS = {
    WorkflowStatus.DRAFT: [WorkflowStatus.PENDING, WorkflowStatus.IN_REVIEW],
    WorkflowStatus.PENDING: [WorkflowStatus.IN_REVIEW, WorkflowStatus.ESCALATED],
    WorkflowStatus.IN_REVIEW: [WorkflowStatus.COMPLETED, WorkflowStatus.ESCALATED],
    WorkflowStatus.ESCALATED: [WorkflowStatus.IN_REVIEW, WorkflowStatus.COMPLETED],
    WorkflowStatus.COMPLETED: [WorkflowStatus.IN_REVIEW],
}

def validate_workflow_transition(current_status: str, new_status: str) -> Tuple[bool, str]:
    """Safeguard 3: Validate workflow status transition."""
    try:
        current = WorkflowStatus(current_status)
        new = WorkflowStatus(new_status)
    except ValueError:
        return False, f"Invalid workflow status: {current_status} -> {new_status}"
    
    if new in ALLOWED_WORKFLOW_TRANSITIONS.get(current, []):
        return True, ""
    
    return False, f"Transition from {current.value} to {new.value} not allowed"

# ─── UI Components ───

def render_login():
    """Render authentication screen."""
    st.title("🥗 Ingredient Review Workbench - Pilot Access")
    st.markdown("---")
    
    st.markdown("### Reviewer Authentication")
    st.caption("Enter your assigned reviewer ID to access your workspace.")
    
    with st.form("login_form"):
        reviewer_id = st.text_input("Reviewer ID", placeholder="Enter your reviewer ID")
        submitted = st.form_submit_button("Access Workspace", type="primary", use_container_width=True)
        
        if submitted:
            if not reviewer_id:
                st.error("Please enter your reviewer ID.")
                return
            
            auth = authenticate_reviewer(reviewer_id)
            if auth:
                st.session_state.authenticated = True
                st.session_state.reviewer_id = reviewer_id
                st.session_state.reviewer_role = auth["role"]
                st.session_state.role_key = auth.get("role_key", auth["role"].lower())
                st.session_state.decisions_df = load_decisions(auth["role_key"])
                st.success(f"✅ Authenticated as {auth['role']} ({reviewer_id})")
                st.rerun()
            else:
                st.error("❌ Invalid reviewer ID. Please check with the pilot coordinator.")
    
    st.markdown("---")
    st.caption("**Security Note:** This is a local single-user deployment. Role separation is enforced by the application logic but cannot protect against a local administrator with filesystem access. Reviewers must use separate physical machines or isolated browser sessions.")

def render_sidebar():
    """Render sidebar with navigation and filters (after authentication)."""
    st.sidebar.title("🥗 Review Workbench")
    
    # Reviewer info
    role_badges = {"PRIMARY": "🔵", "AUDITOR": "🟢", "ADJUDICATOR": "🟠"}
    badge = role_badges.get(st.session_state.reviewer_role, "")
    st.sidebar.success(f"{badge} **{st.session_state.reviewer_role}**\n{st.session_state.reviewer_id}")
    
    # Role is NOT selectable - enforced by authentication
    st.sidebar.markdown("---")
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Filters
    st.sidebar.subheader("Filters")
    
    priority_options = ['All', 'Critical', 'High', 'Medium', 'Standard', 'Low']
    priority = st.sidebar.selectbox(
        "Priority",
        priority_options,
        index=priority_options.index(st.session_state.filter_settings['priority'])
    )
    st.session_state.filter_settings['priority'] = priority
    
    ingredient = st.sidebar.text_input(
        "Ingredient Name",
        value=st.session_state.filter_settings['ingredient'],
        placeholder="Search ingredient..."
    )
    st.session_state.filter_settings['ingredient'] = ingredient
    
    prep_states = ['All', 'FRESH', 'RAW', 'NOT_SPECIFIED', 'POWDERED', 'DRIED', 
                   'ROASTED', 'FRIED', 'BOILED', 'COOKED', 'SOAKED', 'GROUND',
                   'SPROUTED', 'PICKLED', 'BLANCHED', 'MARINATED', 'FERMENTED', 'UNKNOWN']
    prep = st.sidebar.selectbox(
        "Preparation State",
        prep_states,
        index=prep_states.index(st.session_state.filter_settings['prep_state'])
    )
    st.session_state.filter_settings['prep_state'] = prep
    
    ifct_groups = ['All']
    ifct_group = st.sidebar.selectbox(
        "IFCT Food Group",
        ifct_groups,
        index=ifct_groups.index(st.session_state.filter_settings['ifct_group']) if st.session_state.filter_settings['ifct_group'] in ifct_groups else 0
    )
    st.session_state.filter_settings['ifct_group'] = ifct_group
    
    match_methods = ['All', 'EXACT', 'SYNONYM', 'TOKEN_EQUIVALENT', 'TOKEN_SIMILARITY', 'FUZZY']
    match_method = st.sidebar.selectbox(
        "Match Method",
        match_methods,
        index=match_methods.index(st.session_state.filter_settings['match_method'])
    )
    st.session_state.filter_settings['match_method'] = match_method
    
    confidences = ['All', 'HIGH', 'MEDIUM', 'LOW']
    confidence = st.sidebar.selectbox(
        "Confidence",
        confidences,
        index=confidences.index(st.session_state.filter_settings['confidence'])
    )
    st.session_state.filter_settings['confidence'] = confidence
    
    statuses = ['All', 'PENDING', 'IN_REVIEW', 'COMPLETED', 'ESCALATED', 'DRAFT']
    status = st.sidebar.selectbox(
        "Review Status",
        statuses,
        index=statuses.index(st.session_state.filter_settings['status'])
    )
    st.session_state.filter_settings['status'] = status
    
    st.sidebar.markdown("---")
    
    # Navigation
    st.sidebar.subheader("Navigation")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_unit_idx == 0, use_container_width=True):
            st.session_state.current_unit_idx = max(0, st.session_state.current_unit_idx - 1)
            st.rerun()
    with col2:
        if st.button("Next ➡️", disabled=st.session_state.current_unit_idx >= len(st.session_state.filtered_units) - 1, use_container_width=True):
            st.session_state.current_unit_idx = min(len(st.session_state.filtered_units) - 1, st.session_state.current_unit_idx + 1)
            st.rerun()
    
    if st.session_state.filtered_units is not None and len(st.session_state.filtered_units) > 0:
        unit_idx = st.sidebar.number_input(
            "Jump to unit #",
            min_value=1,
            max_value=len(st.session_state.filtered_units),
            value=st.session_state.current_unit_idx + 1,
            step=1
        )
        if st.sidebar.button("Go", use_container_width=True):
            st.session_state.current_unit_idx = unit_idx - 1
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Progress - only show current reviewer's progress
    total = len(st.session_state.filtered_units) if st.session_state.filtered_units is not None else 0
    completed = 0
    if st.session_state.decisions_df is not None and not st.session_state.decisions_df.empty:
        completed = st.session_state.decisions_df['review_unit_id'].nunique()
    
    st.sidebar.metric("My Progress", f"{completed}/{total}")
    if total > 0:
        st.sidebar.progress(completed / total)

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply current filter settings to the review units dataframe."""
    filtered = df.copy()
    
    fs = st.session_state.filter_settings
    
    if fs['priority'] != 'All':
        priority_ranges = {
            'Critical': (80, 100), 'High': (60, 79), 'Medium': (40, 59),
            'Standard': (20, 39), 'Low': (0, 19)
        }
        if fs['priority'] in priority_ranges:
            min_score, max_score = priority_ranges[fs['priority']]
            filtered = filtered[
                (filtered['priority_score'] >= min_score) & 
                (filtered['priority_score'] <= max_score)
            ]
    
    if fs['ingredient']:
        mask = filtered['primary_ingredient'].str.contains(fs['ingredient'], case=False, na=False)
        filtered = filtered[mask]
    
    if fs['prep_state'] != 'All':
        filtered = filtered[filtered['preparation_state'] == fs['prep_state']]
    
    if fs['ifct_group'] != 'All':
        filtered = filtered[filtered['ifct_food_group'] == fs['ifct_group']]
    
    if fs['match_method'] != 'All':
        filtered = filtered[filtered['match_method'] == fs['match_method']]
    
    if fs['confidence'] != 'All':
        filtered = filtered[filtered['provisional_confidence'] == fs['confidence']]
    
    if fs['status'] != 'All':
        filtered = filtered[filtered['workflow_status'] == fs['status']]
    
    return filtered

def render_candidate_comparison(candidate: pd.Series, ifct_df: pd.DataFrame):
    """Render the IFCT candidate comparison panel."""
    st.subheader("📊 IFCT Candidate Comparison")
    
    ifct_row = ifct_df[ifct_df['food_code'] == candidate['ifct_food_code']]
    if not ifct_row.empty:
        ifct_row = ifct_row.iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Source Ingredient**")
            st.write(f"**Primary:** {candidate['primary_ingredient']}")
            st.write(f"**Normalized:** {candidate.get('normalized_ingredient', 'N/A')}")
            st.write(f"**Original:** {candidate.get('original_ingredient', 'N/A')}")
            st.write(f"**Preparation:** {candidate.get('preparation_state', 'NOT_SPECIFIED')}")
            st.write(f"**Quantity:** {candidate.get('quantity', 'N/A')}")
            st.write(f"**Unit:** {candidate.get('unit', 'N/A')}")
        
        with col2:
            st.markdown("**IFCT Candidate**")
            st.write(f"**Code:** {ifct_row['food_code']}")
            st.write(f"**Name:** {ifct_row['food_name']}")
            st.write(f"**Group:** {ifct_row['food_group']}")
            
            st.markdown("**Nutrient Profile (per 100g edible portion)**")
            nutrient_cols = {
                'Protein': 'protein_g', 'Fat': 'fat_g', 'Moisture': 'moisture_g',
                'Ash': 'ash_g', 'Total Fibre': 'fibre_total_g',
                'Insoluble Fibre': 'fibre_insoluble_g', 'Soluble Fibre': 'fibre_soluble_g',
                'Available Carb': 'carb_available_g', 'Energy (kJ)': 'energy_kj'
            }
            
            for label, col in nutrient_cols.items():
                if col in ifct_row.index and pd.notna(ifct_row[col]):
                    val = ifct_row[col]
                    if isinstance(val, (int, float)):
                        st.write(f"**{label}:** {val} g")
                    else:
                        st.write(f"**{label}:** {val}")
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Match Method", candidate['match_method'])
        with col2:
            st.metric("Similarity", f"{candidate['similarity_score']:.3f}")
        with col3:
            st.metric("Confidence", candidate.get('provisional_confidence', 'N/A'))
        
        # Safeguard 1: Auto-accept eligibility display
        eligible, reasons = check_auto_accept_eligibility(candidate)
        if not eligible:
            st.warning("⚠️ Not eligible for auto-accept: " + "; ".join(reasons))

def render_review_interface(candidate: pd.Series, ifct_df: pd.DataFrame, existing_decision: Optional[pd.Series]):
    """Render the review decision interface with enforced isolation."""
    st.subheader("✍️ Review Decision")
    
    review_unit_id = candidate['review_unit_id']
    role_key = st.session_state.role_key
    
    # Check existing decision for this reviewer
    existing = existing_decision is not None
    if existing:
        st.info(f"ℹ️ You already submitted a decision: **{existing_decision['mapping_decision']}** (at {existing_decision['timestamp'][:19]})")
        if st.button("🔄 Overwrite Decision", type="secondary"):
            st.session_state.current_decision = None
            st.rerun()
        return
    
    # Check if already submitted by other reviewer (blind)
    other_role = "auditor" if role_key == "primary" else "primary"
    if role_key in ["primary", "auditor"]:
        other_decisions = load_decisions(other_role)
        if not other_decisions.empty:
            other_match = other_decisions[other_decisions['review_unit_id'] == review_unit_id]
            if not other_match.empty:
                st.info("🔒 **Blind Review Active**: The other reviewer has submitted their decision. Their decision and rationale are hidden from you.")
    
    # Adjudicator view - show all decisions
    if role_key == "adjudicator":
        all_decisions = get_all_decisions_for_unit(review_unit_id)
        if not all_decisions.empty:
            st.markdown("**All Submissions (for adjudication):**")
            for _, dec in all_decisions.iterrows():
                st.write(f"- **{dec['reviewer_role']}** ({dec['reviewer_id']}): {dec['mapping_decision']} — {dec['rationale'][:150]}...")
            st.divider()
    
    # Decision form
    with st.form(key=f"decision_form_{st.session_state.current_unit_idx}_{st.session_state.reviewer_id}"):
        st.markdown("**Decision**")
        decision = st.radio(
            "Mapping Decision",
            options=[d.value for d in MappingDecision],
            format_func=lambda x: x.value if hasattr(x, 'value') else x,
            horizontal=True,
            key=f"decision_{st.session_state.current_unit_idx}_{st.session_state.reviewer_id}"
        )
        
        decision_map = {d.value: d for d in MappingDecision}
        decision_enum = decision_map.get(decision, MappingDecision.UNMATCHED)
        
        col1, col2 = st.columns(2)
        with col1:
            confidence = st.slider(
                "Confidence (1-5)",
                min_value=1, max_value=5, value=3,
                help="Your confidence in this mapping decision"
            )
        with col2:
            alt_code = st.text_input(
                "Alternative IFCT Code (optional)",
                placeholder="e.g., G010",
                help="If you think a different IFCT code is more appropriate"
            )
        
        st.markdown("**Rationale** *(minimum 50 characters)*")
        rationale = st.text_area(
            "Reasoning for this decision",
            height=120,
            placeholder="Explain your reasoning, citing specific evidence fields...",
            key=f"rationale_{st.session_state.current_unit_idx}_{st.session_state.reviewer_id}"
        )
        
        evidence_refs = st.text_area(
            "Evidence References (comma-separated)",
            placeholder="e.g., ifct_food_code, ifct_food_name, ifct_food_group, ifct_source_page, ifct_table_number, match_method, similarity_score, preparation_state, preparation_confidence, prep_state_compat, extracted_aliases, ambiguity_flags, species_verification, edible_part_verification, prep_compatibility_evidence",
            help="Comma-separated list of evidence fields that support your decision. ACCEPTED requires all 15 fields.",
            key=f"evidence_{st.session_state.current_unit_idx}_{st.session_state.reviewer_id}"
        )
        
        uncertainty = st.text_area(
            "Uncertainty / Limitations (optional)",
            placeholder="Any caveats, uncertainties, or limitations in your assessment...",
            key=f"uncertainty_{st.session_state.current_unit_idx}_{st.session_state.reviewer_id}"
        )
        
        submitted = st.form_submit_button("💾 Submit Decision", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if len(rationale.strip()) < 50:
                st.error("❌ Rationale must be at least 50 characters.")
                return
            
            evidence_fields = [f.strip() for f in evidence_refs.split(',') if f.strip()]
            
            # Safeguard 4: ACCEPTED evidence enforcement
            if decision_enum == MappingDecision.ACCEPTED:
                valid, missing = validate_accepted_evidence(evidence_fields)
                if not valid:
                    st.error(f"❌ ACCEPTED decisions require all 15 evidence fields. Missing: {', '.join(missing)}")
                    return
            
            # Safeguard 1: NOT_SPECIFIED auto-accept prevention
            if not candidate.get('requires_review', True) and candidate.get('preparation_state') == 'NOT_SPECIFIED':
                st.error("❌ NOT_SPECIFIED preparation state cannot be auto-accepted. Manual review required.")
                return
            
            # Safeguard 2: CONFLICT decision support
            if decision_enum == MappingDecision.CONFLICT:
                if not alt_code.strip():
                    st.error("❌ CONFLICT decision requires an alternative IFCT code.")
                    return
                if len(rationale.strip()) < 100:
                    st.error("❌ CONFLICT decisions require detailed rationale (minimum 100 characters).")
                    return
            
            # Determine workflow status
            if decision_enum in [MappingDecision.AMBIGUOUS, MappingDecision.CONFLICT]:
                workflow_status = WorkflowStatus.ESCALATED
            else:
                workflow_status = WorkflowStatus.COMPLETED
            
            # Create decision
            decision_obj = ReviewDecision(
                review_unit_id=review_unit_id,
                reviewer_id=st.session_state.reviewer_id,
                reviewer_role=st.session_state.reviewer_role,
                workflow_status=workflow_status,
                mapping_decision=decision_enum,
                previous_status="",
                previous_decision="",
                rationale=rationale.strip(),
                confidence=confidence,
                alternative_ifct_code=alt_code.strip() if alt_code.strip() else "",
                evidence_references=evidence_fields,
                uncertainty_notes=uncertainty.strip(),
                session_id=str(uuid.uuid4()),
                is_blind_review=True,
            )
            
            # Save to role-isolated storage
            decision_dict = decision_obj.to_dict()
            existing_df = st.session_state.decisions_df
            
            if existing_df is not None and not existing_df.empty:
                existing_df = existing_df[
                    ~((existing_df['review_unit_id'] == review_unit_id) & 
                      (existing_df['reviewer_id'] == st.session_state.reviewer_id))
                ]
            decisions_df = pd.concat([existing_df, pd.DataFrame([decision_dict])], ignore_index=True)
            
            save_decisions(st.session_state.role_key, decisions_df)
            st.session_state.decisions_df = decisions_df
            st.session_state.current_decision = decision_dict
            
            # Update submission state
            update_submission_state(review_unit_id, st.session_state.reviewer_role)
            
            st.success("✅ Decision submitted!")
            st.rerun()

def render_navigation():
    """Render navigation controls."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_unit_idx == 0, use_container_width=True):
            st.session_state.current_unit_idx = max(0, st.session_state.current_unit_idx - 1)
            st.rerun()
    with col3:
        if st.button("Next ➡️", disabled=st.session_state.current_unit_idx >= len(st.session_state.filtered_units) - 1, use_container_width=True):
            st.session_state.current_unit_idx = min(len(st.session_state.filtered_units) - 1, st.session_state.current_unit_idx + 1)
            st.rerun()

# ─── Main Application ───

def compute_priority_score(row) -> float:
    """Compute priority score for a review unit."""
    score = 0.0
    
    method_scores = {
        'EXACT': 40, 'SYNONYM': 30, 'TOKEN_EQUIVALENT': 20,
        'TOKEN_SIMILARITY': 10, 'FUZZY': 5
    }
    score += method_scores.get(row.get('match_method', ''), 0)
    
    prep_scores = {
        'FRESH': 20, 'RAW': 20, 'NOT_SPECIFIED': 10,
        'DRIED': 5, 'POWDERED': 5, 'ROASTED': 0,
        'FRIED': 0, 'BOILED': 0, 'COOKED': 0,
        'FERMENTED': 0, 'SPROUTED': 5, 'SOAKED': 5,
        'GROUND': 0, 'BLANCHED': 5, 'MARINATED': 0,
        'PICKLED': 0, 'UNKNOWN': 0
    }
    score += prep_scores.get(row.get('preparation_state', ''), 0)
    
    score += row.get('similarity_score', 0) * 30
    
    candidate_count = row.get('candidate_count', 1)
    if candidate_count > 1:
        score -= min(20, candidate_count * 2)
    
    return min(100, max(0, score))

def main():
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login()
        return
    
    role_key = st.session_state.role_key
    
    # Load data
    if st.session_state.review_units is None:
        with st.spinner("Loading review units..."):
            st.session_state.review_units = load_review_units()
            st.session_state.review_units['priority_score'] = st.session_state.review_units.apply(compute_priority_score, axis=1)
            
            bins = [0, 19, 39, 59, 79, 100]
            labels = ['Low (0-19)', 'Standard (20-39)', 'Medium (40-59)', 'High (60-79)', 'Critical (80-100)']
            st.session_state.review_units['priority_band'] = pd.cut(
                st.session_state.review_units['priority_score'], bins=bins, labels=labels, right=True
            )
            st.session_state.review_units['priority_score'] = st.session_state.review_units.apply(compute_priority_score, axis=1)
    
    if st.session_state.decisions_df is None:
        st.session_state.decisions_df = load_decisions(role_key)
    
    if st.session_state.filtered_units is None:
        st.session_state.filtered_units = st.session_state.review_units.copy()
    
    # Load IFCT data
    ifct_df = load_ifct_data()
    
    # Sidebar
    render_sidebar()
    
    # Apply filters
    filtered = apply_filters(st.session_state.review_units)
    st.session_state.filtered_units = filtered
    
    # Main content
    if st.session_state.filtered_units is None or len(st.session_state.filtered_units) == 0:
        st.warning("No review units match the current filters.")
        return
    
    # Current unit
    idx = st.session_state.current_unit_idx
    if idx >= len(st.session_state.filtered_units):
        st.session_state.current_unit_idx = 0
        idx = 0
    
    candidate = st.session_state.filtered_units.iloc[idx]
    
    # Check existing decision for this reviewer
    review_unit_id = candidate['review_unit_id']
    existing_decision = get_existing_decision(st.session_state.decisions_df, review_unit_id, st.session_state.reviewer_id)
    
    # Load IFCT data
    ifct_df = load_ifct_data()
    
    # Layout
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        # Header
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("🥗 Ingredient Review Workbench")
        with col2:
            st.metric("Progress", f"{st.session_state.current_unit_idx + 1}/{len(st.session_state.filtered_units)}")
        
        role_badges = {"PRIMARY": "🔵", "AUDITOR": "🟢", "ADJUDICATOR": "🟠"}
        badge = role_badges.get(st.session_state.reviewer_role, "")
        st.caption(f"{badge} **{st.session_state.reviewer_role}** | {st.session_state.reviewer_id} | Unit {st.session_state.current_unit_idx + 1}/{len(st.session_state.filtered_units)}")
        
        st.divider()
        
        # Candidate comparison
        candidate = st.session_state.filtered_units.iloc[st.session_state.current_unit_idx]
        render_candidate_comparison(candidate, load_ifct_data())
        
        st.divider()
        
        # Review decision interface
        existing_decision = get_existing_decision(st.session_state.decisions_df, candidate['review_unit_id'], st.session_state.reviewer_id)
        render_review_interface(candidate, load_ifct_data(), existing_decision)
    
    with col_side:
        pass
    
    # Navigation at bottom
    st.divider()
    render_navigation()

# ─── Entry Point ───
if __name__ == "__main__":
    main()