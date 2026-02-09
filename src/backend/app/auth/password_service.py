"""
Password Service

TASK-008: Secure password hashing and validation.

Features:
- Argon2id hashing (winner of PHC)
- Password policy validation
- Strength scoring
"""
import re
from typing import List, Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from src.backend.config import settings


class PasswordService:
    """
    Secure password handling service.
    
    Uses Argon2id for hashing (recommended by OWASP).
    """

    def __init__(self):
        # Argon2id with secure defaults
        self._hasher = PasswordHasher(
            time_cost=2,  # iterations
            memory_cost=65536,  # 64 MB
            parallelism=1,
            hash_len=32,
            salt_len=16,
        )
        
        # Policy from settings
        self.min_length = settings.PASSWORD_MIN_LENGTH
        self.require_uppercase = settings.PASSWORD_REQUIRE_UPPERCASE
        self.require_number = settings.PASSWORD_REQUIRE_NUMBER
        self.require_special = settings.PASSWORD_REQUIRE_SPECIAL

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id.
        
        Args:
            password: Plain text password
            
        Returns:
            Argon2 hash string (includes algorithm params and salt)
        """
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored hash to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self._hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        """
        Check if a password hash needs to be rehashed.
        
        This is useful when updating hash parameters.
        
        Args:
            password_hash: Stored hash to check
            
        Returns:
            True if should rehash after successful verification
        """
        return self._hasher.check_needs_rehash(password_hash)

    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate a password against policy requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list of missing requirements)
        """
        missing = []
        
        if len(password) < self.min_length:
            missing.append(f"min_length_{self.min_length}")
        
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            missing.append("uppercase")
        
        if self.require_number and not re.search(r"\d", password):
            missing.append("number")
        
        if self.require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            missing.append("special_character")
        
        return len(missing) == 0, missing

    def calculate_strength(self, password: str) -> str:
        """
        Calculate password strength score.
        
        Returns:
            'weak', 'fair', 'strong', or 'very_strong'
        """
        score = 0
        
        # Length contribution
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        
        # Extra points for mixing multiple special chars
        if len(re.findall(r"[!@#$%^&*(),.?\":{}|<>]", password)) >= 2:
            score += 1
        
        # Common patterns penalty
        common_patterns = [
            r"(123|abc|qwerty|password|admin|letmein)",
            r"(.)\1{2,}",  # Repeated characters
        ]
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                score -= 1
        
        if score <= 2:
            return "weak"
        elif score <= 4:
            return "fair"
        elif score <= 6:
            return "strong"
        else:
            return "very_strong"

    def get_policy_description(self, lang: str = "en") -> dict:
        """
        Get password policy description for UI.
        
        Args:
            lang: Language code ('en' or 'ar')
            
        Returns:
            Policy requirements with translations
        """
        if lang == "ar":
            return {
                "min_length": f"الحد الأدنى {self.min_length} أحرف",
                "uppercase": "حرف كبير واحد على الأقل" if self.require_uppercase else None,
                "number": "رقم واحد على الأقل" if self.require_number else None,
                "special": "رمز خاص واحد على الأقل" if self.require_special else None,
            }
        else:
            return {
                "min_length": f"Minimum {self.min_length} characters",
                "uppercase": "At least one uppercase letter" if self.require_uppercase else None,
                "number": "At least one number" if self.require_number else None,
                "special": "At least one special character" if self.require_special else None,
            }


# Global service instance
password_service = PasswordService()
