import re

def is_valid_first_name(name: str) -> tuple[bool, str]:
    """
    Validates a name allowing alphabets and spaces. Minimum 2 characters.
    Returns (True, "") if valid, else (False, "reason").
    """
    name = name.strip()
    if not name:
        return False, "First Name cannot be empty."
    if len(name) < 2:
        return False, "First Name must be at least 2 characters."
    if not re.fullmatch(r"[A-Za-z ]{2,}", name):
        return False, "First Name can contain only letters."
    return True, ""

def is_valid_last_name(name: str) -> tuple[bool, str]:
    """
    Validates a name allowing alphabets and spaces. Minimum 2 characters.
    Returns (True, "") if valid, else (False, "reason").
    """
    name = name.strip()
    if not name:
        return False, "Last Name cannot be empty."
    if len(name) < 2:
        return False, "Last Name must be at least 2 characters."
    if not re.fullmatch(r"[A-Za-z ]{2,}", name):
        return False, "Last Name can contain only letters."
    return True, ""

def is_valid_email(email: str) -> tuple[bool, str]:
    """
    Validates an email address.
    """
    email = email.strip()
    if not email:
        return False, "Email cannot be empty."
    if not re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", email):
        return False, "Invalid email format."
    return True, ""

def is_valid_phone(phone: str) -> tuple[bool, str]:
    """
    Validates a 10-digit phone number (no spaces, letters or special chars).
    """
    phone = phone.strip()
    if not phone:
        return False, "Phone number cannot be empty."
    if not re.fullmatch(r"\d{10}", phone):
        return False, "Phone number must be exactly 10 digits."
    return True, ""
