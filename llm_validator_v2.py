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
    Mock Validator V2: Được cập nhật để xử lý các heuristic flags mới từ Rule Engine.
    Khi thay bằng Real LLM (OpenAI/Anthropic), prompt sẽ tự động bao quát các logic này.
    """
    def validate(self, record: dict, rule_flags: list) -> LLMValidationResult:
        if not rule_flags:
            return LLMValidationResult(
                status="VALID", confidence_score=0.95, issues_found=[],
                suggested_corrections={}, reasoning_summary="Data looks clean."
            )
        
        # FIX TC05: Lỗi ngày tháng mập mờ
        if "ambiguous_date_format" in rule_flags:
            return LLMValidationResult(
                status="NEEDS_REVIEW", confidence_score=0.85, issues_found=["Date format is non-standard"],
                suggested_corrections={"date_of_birth": "1990-01-01"}, 
                reasoning_summary="Attempted to standardize date format to YYYY-MM-DD. Needs human review."
            )
            
        # FIX TC06: Lỗi viết hoa/thường
        if "formatting_inconsistency" in rule_flags:
            return LLMValidationResult(
                status="NEEDS_REVIEW", confidence_score=0.92, issues_found=["Full name formatting is inconsistent (lowercase)"],
                suggested_corrections={"full_name": record.get("full_name", "").title()}, 
                reasoning_summary="Capitalized the first letter of each word in the name."
            )
            
        # FIX TC07: Lỗi đảo ngược cột
        if "semantic_mismatch" in rule_flags:
            return LLMValidationResult(
                status="NEEDS_REVIEW", confidence_score=0.89, issues_found=["Full name and Email fields appear swapped"],
                suggested_corrections={
                    "full_name": record.get("email"), 
                    "email": record.get("full_name")
                }, 
                reasoning_summary="Swapped the values of email and full_name based on content structure."
            )
            
        # FIX TC10: Lỗi logic năm sinh tương lai
        if "logical_error_future_date" in rule_flags:
            return LLMValidationResult(
                status="NEEDS_REVIEW", confidence_score=0.99, issues_found=["Date of birth is in the future (after 2026)"],
                suggested_corrections={}, # Không tự đoán bừa tuổi thật của họ
                reasoning_summary="Detected an impossible date of birth. System cannot autofix this; requires human validation."
            )
            
        # Default fallback cho các lỗi nghiêm trọng không thể cứu vãn (TC02, TC03, TC04, TC09)
        return LLMValidationResult(
            status="INVALID", confidence_score=0.99, issues_found=rule_flags,
            suggested_corrections={}, reasoning_summary="Critical rule failures detected. Cannot autofix."
        )