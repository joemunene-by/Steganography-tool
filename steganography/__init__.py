"""
Professional Steganography Tool

A high-end steganography solution for hiding and extracting messages
within digital images using LSB (Least Significant Bit) technique.
"""

__version__ = "1.0.0"
__author__ = "Joe Munene"
__email__ = "joemunene@gmail.com"
__description__ = "Professional steganography tool for digital images"

from .core import SteganoEncoder, SteganoDecoder, SteganographyError

__all__ = [
    "SteganoEncoder",
    "SteganoDecoder", 
    "SteganographyError",
    "__version__",
]
