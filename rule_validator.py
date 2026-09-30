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
            
    # 2. Email format
    email = record.get("email", "")
    if email and not EMAIL_REGEX.match(email):
        flags.append("invalid_email_format")
        
    # 3. Phone format
    phone = record.get("phone", "")
    if phone and not PHONE_REGEX.match(phone):
        flags.append("invalid_phone_format")
        
    # 4. Date format (Strict parsing try)
    dob = record.get("date_of_birth", "")
    if dob:
        try:
            # Try standard ISO first
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            flags.append("ambiguous_date_format")
            
    return flags