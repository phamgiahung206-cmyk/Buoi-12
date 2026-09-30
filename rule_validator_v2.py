import re
from datetime import datetime
from config import REQUIRED_FIELDS

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{8,15}$")

def validate_rules(record: dict) -> list:
    flags = []
    
    # 1. Missing required fields
    for field in REQUIRED_FIELDS:
        if not record.get(field):
            flags.append(f"missing_{field}")
            
    # 2. Email format & Semantic Mismatch Heuristic (FIX TC07)
    email = record.get("email", "")
    full_name = record.get("full_name", "")
    
    if email and not EMAIL_REGEX.match(email):
        # Nếu cột email sai format, nhưng cột tên lại có dấu hiệu của email -> Khả năng cao bị nhập nhầm cột
        if "@" in full_name and "@" not in email:
            flags.append("semantic_mismatch")
        else:
            flags.append("invalid_email_format")
            
    # 3. Phone format
    phone = record.get("phone", "")
    if phone and not PHONE_REGEX.match(phone):
        flags.append("invalid_phone_format")
        
    # 4. Date format & Plausibility Check (FIX TC10)
    dob = record.get("date_of_birth", "")
    if dob:
        try:
            dt = datetime.strptime(dob, "%Y-%m-%d")
            # Kiểm tra logic thực tế: Năm hiện tại là 2026, khách hàng không thể sinh sau 2026
            if dt.year > 2026:
                flags.append("logical_error_future_date")
        except ValueError:
            flags.append("ambiguous_date_format")
            
    # 5. Formatting Heuristic (FIX TC06)
    # Kiểm tra xem tên có bị viết thường toàn bộ không
    if full_name and full_name.islower():
        flags.append("formatting_inconsistency")
            
    return flags