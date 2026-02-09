from typing import List, Optional
from pydantic import BaseModel
import re

class CustomerProfile(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    party_size: Optional[int] = None
    date_time_preference: Optional[str] = None
    dietary_restrictions: List[str] = []
    occasion: Optional[str] = None
    special_requests: List[str] = []

def validate_customer_profile(profile: CustomerProfile) -> List[str]:
    errors = []

    if not profile.name or not profile.name.strip():
        errors.append("Name is required and cannot be empty.")

    if not validate_phone_number(profile.phone):
        errors.append("Phone number is required and must have 10 to 15 digits.")

    if not profile.party_size or profile.party_size < 1:
        errors.append("Party size is required and must be at least 1.")

    if profile.party_size and profile.party_size > 20:
        errors.append("Party size cannot exceed 20 people. Please call for large party reservations.")

    if not profile.date_time_preference or not profile.date_time_preference.strip():
        errors.append("Date and time preference is required.")

    return errors

def validate_phone_number(phone: Optional[str]) -> bool:
    if not phone:
        return False
    # Extract only digits
    digits_only = "".join(re.findall(r"\d", phone))
    # Check if the number has 10 to 15 digits
    return 10 <= len(digits_only) <= 15

def apply_defaults_to_profile(profile: CustomerProfile) -> CustomerProfile:
    updated_profile = profile.model_copy()

    if not updated_profile.party_size:
        updated_profile.party_size = 2

    if not updated_profile.occasion:
        updated_profile.occasion = "dinner"

    return updated_profile

def normalize_customer_profile(profile: CustomerProfile) -> CustomerProfile:
    return CustomerProfile(
        name=profile.name.strip() if profile.name else None,
        phone=str(format_phone(profile.phone)) if profile.phone else None,
        party_size=profile.party_size,
        date_time_preference=profile.date_time_preference.strip() if profile.date_time_preference else None,
        dietary_restrictions=[d.strip().lower() for d in (profile.dietary_restrictions or [])],
        occasion=profile.occasion.strip().lower() if profile.occasion else None,
        special_requests=[s.strip() for s in (profile.special_requests or [])]
    )

# format phone number to e164 format
def format_phone(phone: str, default_country_code: str = "+1") -> str:
    if not phone:
        return ""
    
    # Remove everything except digits
    digits = re.sub(r"[^\d]", "", phone)

    # Prepend country code if missing (assuming 10-digit US number)
    if len(digits) == 10:
        return default_country_code + digits
    elif digits.startswith("1") and len(digits) == 11:
        return "+" + digits
    elif digits.startswith("+") and len(digits) > 1:
        return digits
    else:
        return "+" + digits  # fallback for already full international
