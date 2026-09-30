from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class LLMValidationResult(BaseModel):
    status: str = Field(description="Must be one of: VALID, INVALID, DUPLICATE, NEEDS_REVIEW")
    confidence_score: float = Field(description="Model-reported confidence (0.0 to 1.0). Note: This is an uncalibrated score.")
    issues_found: List[str] = Field(description="List of identified issues")
    suggested_corrections: Dict[str, Any] = Field(description="Dictionary of suggested new values for specific fields")
    reasoning_summary: str = Field(description="Brief explanation of the decision")

class SystemValidationState(BaseModel):
    rule_flags: List[str] = []
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    llm_result: Optional[LLMValidationResult] = None
    final_classification: str = "PENDING"