import json
from abc import ABC, abstractmethod
from schemas import LLMValidationResult
from config import logger

class BaseLLMValidator(ABC):
    @abstractmethod
    def validate(self, record: dict, rule_flags: list) -> LLMValidationResult:
        pass

class MockLLMValidator(BaseLLMValidator):
    """
    Mock Validator for testing/reproducibility without spending API credits.
    Simulates LLM behavior based on rule flags.
    """
    def validate(self, record: dict, rule_flags: list) -> LLMValidationResult:
        if not rule_flags:
            return LLMValidationResult(
                status="VALID",
                confidence_score=0.95,
                issues_found=[],
                suggested_corrections={},
                reasoning_summary="Data looks clean."
            )
        
        # Simulate AI fixing an ambiguous date
        if "ambiguous_date_format" in rule_flags:
            return LLMValidationResult(
                status="NEEDS_REVIEW",
                confidence_score=0.85, # Model-reported score
                issues_found=["Date format is non-standard"],
                suggested_corrections={"date_of_birth": "1990-01-01"}, # Mock suggestion
                reasoning_summary="Attempted to standardize date format to YYYY-MM-DD. Needs human review."
            )
            
        return LLMValidationResult(
            status="INVALID",
            confidence_score=0.99,
            issues_found=rule_flags,
            suggested_corrections={},
            reasoning_summary="Critical rule failures detected. Cannot autofix."
        )

# Future: class OpenAILLMValidator(BaseLLMValidator): ...