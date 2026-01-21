"""
Steganography Core Module

This module provides the core functionality for steganographic operations
including encoding and decoding messages in digital images using LSB technique.
"""

from .encoder import SteganoEncoder
from .decoder import SteganoDecoder
from .exceptions import SteganographyError
from .crypto import SteganographyCrypto
from .batch import BatchProcessor
from .analysis import ImageAnalyzer
from .config import get_config, ConfigManager
from .visualization import SteganographyVisualizer

__version__ = "1.0.0"
__all__ = [
    "SteganoEncoder", 
    "SteganoDecoder", 
    "SteganographyError",
    "SteganographyCrypto",
    "BatchProcessor",
    "ImageAnalyzer",
    "SteganographyVisualizer",
    "get_config",
    "ConfigManager"
]
