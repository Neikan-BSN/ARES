"""Security utilities for ARES system.

Provides secure path handling, input validation, and other security hardening utilities.
"""

import hashlib
import logging
import os
import re
from pathlib import Path
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Base exception for security-related errors."""

    pass


class PathTraversalError(SecurityError):
    """Exception raised when path traversal is detected."""

    pass


class InputValidationError(SecurityError):
    """Exception raised when input validation fails."""

    pass


class SecurePathHandler:
    """Secure path handling to prevent directory traversal attacks."""

    # Dangerous path patterns that indicate potential traversal attempts
    DANGEROUS_PATTERNS = [
        r"\.\.[\\/]",  # ../ or ..\\
        r"[\\/]\.\.[\\/]",  # /../ or \..\\
        r"[\\/]\.\.$",  # /..
        r"^\.\.[\\/]",  # ../ at start
        r"%2e%2e",  # URL encoded ..
        r"\x2e\x2e",  # Hex encoded ..
        r"\\\\",  # UNC paths
        r"[\\/]etc[\\/]passwd",  # Common attack target
        r"[\\/]etc[\\/]shadow",  # Common attack target
        r"[\\/]proc[\\/]",  # Process filesystem
        r"[\\/]sys[\\/]",  # System filesystem
        r"%00",  # Null byte injection
        r"\x00",  # Null byte injection
    ]

    def __init__(self, allowed_base_paths: list[str | Path] | None = None):
        """
        Initialize secure path handler.

        Args:
            allowed_base_paths: List of allowed base paths. If None, uses current working directory.
        """
        if allowed_base_paths is None:
            self.allowed_base_paths = [Path.cwd()]
        else:
            self.allowed_base_paths = [Path(p).resolve() for p in allowed_base_paths]

    def validate_path(self, path: str | Path, allow_create: bool = False) -> Path:
        """
        Validate and sanitize a file path to prevent directory traversal.

        Args:
            path: Path to validate
            allow_create: Whether to allow non-existent paths

        Returns:
            Validated and resolved Path object

        Raises:
            PathTraversalError: If path contains dangerous patterns or is outside allowed paths
        """
        try:
            # Convert to string and normalize
            path_str = str(path)

            # URL decode if needed
            if "%" in path_str:
                path_str = unquote(path_str)

            # Check for dangerous patterns
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, path_str, re.IGNORECASE):
                    raise PathTraversalError(
                        f"Dangerous path pattern detected: {pattern}"
                    )

            # Convert to Path and resolve
            validated_path = Path(path_str).resolve()

            # Ensure path is within allowed base paths
            is_allowed = False
            for base_path in self.allowed_base_paths:
                try:
                    validated_path.relative_to(base_path)
                    is_allowed = True
                    break
                except ValueError:
                    continue

            if not is_allowed:
                raise PathTraversalError(
                    f"Path {validated_path} is not within allowed base paths"
                )

            # Check if path exists (unless creation is allowed)
            if not allow_create and not validated_path.exists():
                # For file paths, check if parent directory exists
                if validated_path.parent.exists():
                    # This is likely a file that will be created, which is okay
                    pass
                else:
                    raise PathTraversalError(
                        f"Path {validated_path} does not exist and parent directory is missing"
                    )

            return validated_path

        except (OSError, ValueError) as e:
            raise PathTraversalError(f"Invalid path: {e}") from e

    def secure_open(self, path: str | Path, mode: str = "r", **kwargs):
        """
        Securely open a file with path validation.

        Args:
            path: Path to file
            mode: File mode
            **kwargs: Additional arguments to pass to open()

        Returns:
            File handle

        Raises:
            PathTraversalError: If path validation fails
        """
        validated_path = self.validate_path(
            path, allow_create="w" in mode or "a" in mode
        )

        # Additional security: restrict certain modes
        if "x" in mode:  # Exclusive creation
            logger.warning(f"Exclusive creation mode used for {validated_path}")

        return open(validated_path, mode, **kwargs)


class InputValidator:
    """Input validation and sanitization utilities."""

    # Common dangerous input patterns
    DANGEROUS_INPUT_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"vbscript:",  # VBScript protocol
        r"data:",  # Data URLs (can be dangerous)
        r"\$\{.*\}",  # Template injection patterns
        r"\{\{.*\}\}",  # Template injection patterns
        r"<%.*%>",  # ASP/JSP patterns
        r"<\?.*\?>",  # PHP patterns
        r"exec\s*\(",  # Code execution
        r"eval\s*\(",  # Code evaluation
        r"system\s*\(",  # System calls
        r"__import__\s*\(",  # Python imports
        r"file:///",  # File protocol
        r"\\\\[a-zA-Z0-9]+\\",  # UNC paths
    ]

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to remove dangerous characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove control characters
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)

        # Ensure it's not empty and doesn't start with dots
        sanitized = sanitized.strip().lstrip(".")

        if not sanitized:
            sanitized = "unnamed_file"

        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[: 255 - len(ext)] + ext

        return sanitized

    @classmethod
    def validate_input(cls, input_data: str, max_length: int = 10000) -> str:
        """
        Validate and sanitize general input data.

        Args:
            input_data: Input string to validate
            max_length: Maximum allowed length

        Returns:
            Validated input string

        Raises:
            InputValidationError: If input contains dangerous patterns
        """
        if not isinstance(input_data, str):
            raise InputValidationError("Input must be a string")

        if len(input_data) > max_length:
            raise InputValidationError(
                f"Input exceeds maximum length of {max_length} characters"
            )

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_INPUT_PATTERNS:
            if re.search(pattern, input_data, re.IGNORECASE | re.DOTALL):
                logger.warning(f"Dangerous input pattern detected: {pattern}")
                raise InputValidationError("Input contains dangerous pattern")

        return input_data

    @staticmethod
    def secure_hash(data: str | bytes, algorithm: str = "sha256") -> str:
        """
        Generate a secure hash using a strong algorithm.

        Args:
            data: Data to hash
            algorithm: Hash algorithm (default: sha256)

        Returns:
            Hexadecimal hash string

        Raises:
            ValueError: If algorithm is not supported or is weak
        """
        # Prevent weak hash algorithms
        weak_algorithms = ["md5", "sha1"]
        if algorithm.lower() in weak_algorithms:
            logger.warning(
                f"Weak hash algorithm {algorithm} requested, using sha256 instead"
            )
            algorithm = "sha256"

        if isinstance(data, str):
            data = data.encode("utf-8")

        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data)
        return hash_obj.hexdigest()

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate a URL for basic security.

        Args:
            url: URL to validate

        Returns:
            True if URL appears safe
        """
        if not url or not isinstance(url, str):
            return False

        # Check for dangerous protocols
        dangerous_protocols = ["javascript:", "vbscript:", "data:", "file:"]
        url_lower = url.lower()

        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                return False

        # Must start with safe protocol
        safe_protocols = ["http://", "https://", "ftp://", "ftps://"]
        is_safe_protocol = any(
            url_lower.startswith(protocol) for protocol in safe_protocols
        )

        if not is_safe_protocol:
            return False

        # Basic format check
        if len(url) > 2048:  # URLs longer than 2048 are suspicious
            return False

        return True


# Global instances for convenient usage
default_path_handler = SecurePathHandler()
input_validator = InputValidator()


# Convenience functions
def secure_path(path: str | Path, allow_create: bool = False) -> Path:
    """Validate a path using the default path handler."""
    return default_path_handler.validate_path(path, allow_create)


def secure_open(path: str | Path, mode: str = "r", **kwargs):
    """Securely open a file using the default path handler."""
    return default_path_handler.secure_open(path, mode, **kwargs)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename using the input validator."""
    return input_validator.sanitize_filename(filename)


def validate_input(input_data: str, max_length: int = 10000) -> str:
    """Validate input using the input validator."""
    return input_validator.validate_input(input_data, max_length)


def secure_hash(data: str | bytes, algorithm: str = "sha256") -> str:
    """Generate a secure hash."""
    return input_validator.secure_hash(data, algorithm)


def validate_url(url: str) -> bool:
    """Validate a URL for basic security."""
    return input_validator.validate_url(url)
