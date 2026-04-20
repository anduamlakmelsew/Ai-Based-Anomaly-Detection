import re
from typing import Dict, List, Tuple

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password strength according to security requirements:
    - Minimum 8 characters
    - Must contain letters (uppercase and lowercase)
    - Must contain numbers
    - Must contain special characters
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("At least 8 characters")
    
    # Check for uppercase letters
    if not re.search(r'[A-Z]', password):
        errors.append("One uppercase letter")
    
    # Check for lowercase letters
    if not re.search(r'[a-z]', password):
        errors.append("One lowercase letter")
    
    # Check for numbers
    if not re.search(r'\d', password):
        errors.append("One number")
    
    # Check for special characters
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
        errors.append("One special character")
    
    # Check for common weak patterns
    common_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'admin',
        r'letmein',
        r'welcome'
    ]
    
    password_lower = password.lower()
    for pattern in common_patterns:
        if re.search(pattern, password_lower):
            errors.append("Avoid common patterns")
            break
    
    return len(errors) == 0, errors

def get_password_strength_score(password: str) -> Dict[str, any]:
    """
    Calculate password strength score and provide feedback
    Returns a dictionary with score, level, and suggestions
    """
    score = 0
    suggestions = []
    
    # Length contribution (max 30 points)
    if len(password) >= 8:
        score += 20
        if len(password) >= 12:
            score += 10
    else:
        suggestions.append("Use at least 8 characters")
    
    # Character variety contribution (max 40 points)
    if re.search(r'[a-z]', password):
        score += 10
    else:
        suggestions.append("Add lowercase letters")
        
    if re.search(r'[A-Z]', password):
        score += 10
    else:
        suggestions.append("Add uppercase letters")
        
    if re.search(r'\d', password):
        score += 10
    else:
        suggestions.append("Add numbers")
        
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
        score += 10
    else:
        suggestions.append("Add special characters")
    
    # Complexity contribution (max 30 points)
    unique_chars = len(set(password))
    if unique_chars >= len(password) * 0.6:  # Good character variety
        score += 15
    elif unique_chars >= len(password) * 0.4:
        score += 10
    else:
        suggestions.append("Use more unique characters")
    
    # No common patterns (max 15 points)
    common_patterns = [r'123456', r'password', r'qwerty', r'admin', r'letmein']
    password_lower = password.lower()
    has_common_pattern = any(re.search(pattern, password_lower) for pattern in common_patterns)
    
    if not has_common_pattern:
        score += 15
    else:
        suggestions.append("Avoid common patterns")
    
    # Determine strength level
    if score >= 80:
        level = "VERY_STRONG"
    elif score >= 60:
        level = "STRONG"
    elif score >= 40:
        level = "MEDIUM"
    elif score >= 20:
        level = "WEAK"
    else:
        level = "VERY_WEAK"
    
    return {
        "score": score,
        "level": level,
        "suggestions": suggestions,
        "is_acceptable": score >= 40  # Minimum acceptable strength
    }
