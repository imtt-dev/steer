from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
import uuid

# --- SHARED TYPES ---

class TeachingOption(BaseModel):
    """A proposed fix for a failure."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    recommended: bool = False
    logic_change: Optional[str] = None # The "Why?" tooltip

# --- LEGACY / INTERNAL TYPES (Needed for Verifiers) ---

class VerificationResult(BaseModel):
    """The result of a single deterministic check."""
    verifier_name: str
    passed: bool
    severity: str = "error"
    reason: Optional[str] = None
    # Allow verifiers to propose specific fixes
    suggested_fixes: List[TeachingOption] = Field(default_factory=list)


# --- V4.1 ARCHITECTURE TYPES (Needed for Dashboard) ---

class TraceStep(BaseModel):
    """Represents a single node in the visual timeline."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal['user', 'agent', 'tool', 'error', 'success']
    title: str
    content: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DiagnosticMetrics(BaseModel):
    """The scorecard (Health Metrics)."""
    faithfulness: Optional[int] = None
    relevance: Optional[int] = None
    context_precision: Optional[int] = None

class Incident(BaseModel):
    """
    The Master Schema. 
    This maps 1:1 to the 'Incident' type in the Next.js Dashboard.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:6].upper()}")
    title: str
    
    # NEW: Track which agent this belongs to
    agent_name: str = "default_agent"
    
    status: Literal['Active', 'Resolved'] = 'Active'
    
    # The "Badge" Logic
    detection_source: Literal['FAST_PATH', 'SLOW_PATH'] = 'FAST_PATH'
    detection_label: str # e.g. "Programmatic Verifier"
    
    severity: Literal['High', 'Medium', 'Low'] = 'Medium'
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    metrics: Optional[DiagnosticMetrics] = None
    
    # The Visuals
    trace: List[TraceStep] = Field(default_factory=list)
    teaching_options: List[TeachingOption] = Field(default_factory=list)
    
    # Raw Metadata (hidden from UI but useful for debug)
    raw_inputs: Dict[str, Any] = Field(default_factory=dict)
    raw_outputs: Optional[Any] = None