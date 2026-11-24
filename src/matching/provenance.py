"""Match Provenance - Tracking match decisions and evidence."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class ReviewDecision(Enum):
    """Manual review decision."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    SPLIT = "SPLIT"  # Split into multiple ingredients


@dataclass
class MatchProvenance:
    """Complete provenance trail for a match decision."""
    provenance_id: str
    match_id: str
    input_text: str
    normalized_text: str
    candidates_considered: int
    candidates_rejected: int
    selection_reason: str
    match_method: str
    similarity_breakdown: Dict
    review_trail: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_review_step(self, reviewer: str, decision: str, notes: str = ""):
        """Add a review step to the trail."""
        self.review_trail.append({
            'timestamp': datetime.now().isoformat(),
            'reviewer': reviewer,
            'decision': decision,
            'notes': notes
        })
    
    def to_dict(self) -> dict:
        return {
            'provenance_id': self.provenance_id,
            'match_id': self.match_id,
            'input_text': self.input_text,
            'normalized_text': self.normalized_text,
            'candidates_considered': self.candidates_considered,
            'candidates_rejected': self.candidates_rejected,
            'selection_reason': self.selection_reason,
            'match_method': self.match_method,
            'similarity_breakdown': self.similarity_breakdown,
            'review_trail': self.review_trail,
            'timestamp': self.timestamp
        }


@dataclass
class ManualReviewRecord:
    """Record of manual review decision."""
    review_id: str
    input_record_id: str
    candidate_ifct_codes: List[str]
    candidate_scores: List[float]
    reviewer_decision: str  # ACCEPT, REJECT, DEFER, SPLIT
    selected_ifct_code: Optional[str] = None
    reviewer_notes: str = ""
    review_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewer_id: str = ""


@dataclass
class ManualReviewRecord:
    """Record for manual review queue."""
    review_id: str
    input_record_id: str
    original_text: str
    normalized_text: str
    candidate_ifct_codes: List[str]
    candidate_scores: List[float]
    candidate_methods: List[str]
    reviewer_decision: str = "PENDING"  # PENDING, ACCEPT, REJECT, DEFER, SPLIT
    selected_ifct_code: Optional[str] = None
    reviewer_notes: str = ""
    review_timestamp: str = ""
    reviewer_id: str = ""
    
    def to_dict(self) -> dict:
        return {
            'review_id': self.review_id,
            'input_record_id': self.input_record_id,
            'original_text': self.original_text,
            'normalized_text': self.normalized_text,
            'candidate_ifct_codes': self.candidate_ifct_codes,
            'candidate_scores': self.candidate_scores,
            'candidate_methods': self.candidate_methods,
            'reviewer_decision': self.reviewer_decision,
            'selected_ifct_code': self.selected_ifct_code,
            'reviewer_notes': self.reviewer_notes,
            'review_timestamp': self.review_timestamp,
            'reviewer_id': self.reviewer_id
        }


class ProvenanceTracker:
    """Track provenance for all match decisions."""
    
    def __init__(self):
        self.provenance_records: Dict[str, any] = {}
        self.review_queue: List = []
        self.review_log: List = []
    
    def create_provenance(self, 
                          match_id: str,
                          input_text: str,
                          normalized_text: str,
                          candidates: List,
                          selection_reason: str,
                          match_method: str,
                          similarity_breakdown: Dict) -> str:
        """Create a provenance record for a match decision."""
        provenance_id = f"prov_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        provenance = {
            'provenance_id': provenance_id,
            'match_id': provenance_id,
            'input_text': self._truncate(text, 500) if len(text) > 500 else text,
            'normalized_text': normalized_text,
            'candidates_considered': len(candidates),
            'candidates_rejected': len(candidates) - 1 if candidates else 0,
            'selection_reason': selection_reason,
            'match_method': match_method,
            'similarity_breakdown': similarity_breakdown,
            'review_trail': [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.provenance_records[provenance_id] = provenance
        return provenance_id
    
    def add_review(self, provenance_id: str, reviewer: str, decision: str, notes: str = ""):
        """Add a review step to provenance."""
        if provenance_id in self.provenance_records:
            self.provenance_records[provenance_id]['review_trail'].append({
                'timestamp': datetime.now().isoformat(),
                'reviewer': reviewer,
                'decision': decision,
                'notes': notes
            })
    
    def add_to_review_queue(self, 
                           input_record_id: str,
                           original_text: str,
                           normalized_text: str,
                           candidates: List[Dict],
                           priority: str = "NORMAL"):
        """Add to manual review queue."""
        review_id = f"rev_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        review_record = {
            'review_id': review_id,
            'input_record_id': input_record_id,
            'original_text': original_text,
            'normalized_text': normalized_text,
            'candidate_ifct_codes': [c['ifct_food_code'] for c in candidates],
            'candidate_scores': [c.get('similarity_score', 0) for c in candidates],
            'candidate_methods': [c.get('match_method', '') for c in candidates],
            'reviewer_decision': 'PENDING',
            'selected_ifct_code': None,
            'reviewer_notes': '',
            'review_timestamp': datetime.now().isoformat(),
            'reviewer_id': '',
            'priority': priority
        }
        
        self.review_queue.append(review_record)
        return review_id
    
    def resolve_review(self, review_id: str, decision: str, 
                       selected_code: str = None, notes: str = "", reviewer: str = ""):
        """Resolve a manual review."""
        for record in self.review_queue:
            if record['review_id'] == review_id:
                record['reviewer_decision'] = decision
                record['selected_ifct_code'] = selected_code
                record['reviewer_notes'] = notes
                record['review_timestamp'] = datetime.now().isoformat()
                record['reviewer_id'] = reviewer
                break
    
    def get_review_queue(self, status: str = "PENDING") -> List:
        """Get pending reviews."""
        if status == "ALL":
            return self.review_queue
        return [r for r in self.review_queue if r['reviewer_decision'] == status]
    
    def get_provenance(self, provenance_id: str) -> Optional[dict]:
        return self.provenance_records.get(provenance_id)
    
    def export_provenance_log(self) -> List[Dict]:
        """Export all provenance records."""
        return list(self.provenance_records.values())
    
    def export_review_log(self) -> List[Dict]:
        """Export review log."""
        return self.review_log


# Global provenance tracker
provenance_tracker = ProvenanceTracker()