from config import logger

def final_classification(rule_flags: list, is_dup: bool, llm_result) -> tuple:
    """
    Decides final status based on Rules, Duplication, and AI output.
    Rule: Never let AI override a hard duplicate or missing ID.
    """
    if "missing_customer_id" in rule_flags:
        return "INVALID", rule_flags
        
    if is_dup:
        return "DUPLICATE", ["Record is a suspected duplicate"]
        
    if llm_result:
        # AI decision is respected but constrained
        if llm_result.status == "NEEDS_REVIEW":
            return "NEEDS_REVIEW", llm_result.issues_found
        elif llm_result.status == "INVALID":
            return "INVALID", llm_result.issues_found
            
    if rule_flags:
         return "NEEDS_REVIEW", rule_flags # Fallback if rules failed but LLM didn't catch

    return "VALID", []