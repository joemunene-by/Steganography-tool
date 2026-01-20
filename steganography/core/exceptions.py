"""
Custom exceptions for the steganography module.
"""


class SteganographyError(Exception):
    """Base exception for all steganography-related errors."""
    pass


class ImageValidationError(SteganographyError):
    """Raised when image validation fails."""
    pass


class MessageCapacityError(SteganographyError):
    """Raised when message exceeds image capacity."""
    pass


class EncodingError(SteganographyError):
    """Raised when encoding operation fails."""
    pass


class DecodingError(SteganographyError):
    """Raised when decoding operation fails."""
    pass


class FileOperationError(SteganographyError):
    """Raised when file operations fail."""
    pass
