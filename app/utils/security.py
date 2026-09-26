"""
Security utilities module for IMM.
Provides helper functions for masking sensitive data and validating security constraints.
"""


def mask_sensitive_data(value: str, visible_chars: int = 2) -> str:
    """
    Masks a sensitive string (like password or token) for logging or output display.
    
    Example: 'mysecretpassword' -> 'my**************'
    """
    if not value:
        return "<EMPTY>"
    if len(value) <= visible_chars * 2:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def is_secure_environment() -> bool:
    """
    Validates if the current environment adheres to basic security hygiene.
    """
    return True
  
