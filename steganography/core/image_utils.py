"""
Image processing utilities for steganography operations.
"""

import os
from typing import Tuple
from PIL import Image, ImageOps
import numpy as np

from .exceptions import ImageValidationError


class ImageValidator:
    """Validates image files for steganography operations."""
    
    SUPPORTED_FORMATS = {'.png', '.bmp', '.tiff', '.jpg', '.jpeg'}
    MIN_SIZE = (64, 64)
    
    @classmethod
    def validate_image(cls, image_path: str) -> Image.Image:
        """
        Validate and load an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object
            
        Raises:
            ImageValidationError: If validation fails
        """
        if not os.path.exists(image_path):
            raise ImageValidationError(f"Image file not found: {image_path}")
        
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in cls.SUPPORTED_FORMATS:
            raise ImageValidationError(
                f"Unsupported image format: {file_ext}. "
                f"Supported formats: {', '.join(cls.SUPPORTED_FORMATS)}"
            )
        
        try:
            image = Image.open(image_path)
            image.load()  # Verify image data
            
            if image.size < cls.MIN_SIZE:
                raise ImageValidationError(
                    f"Image too small: {image.size}. "
                    f"Minimum size: {cls.MIN_SIZE}"
                )
            
            return image
        except Exception as e:
            raise ImageValidationError(f"Failed to load image: {str(e)}")
    
    @classmethod
    def calculate_capacity(cls, image: Image.Image) -> int:
        """
        Calculate maximum message capacity in bytes.
        
        Args:
            image: PIL Image object
            
        Returns:
            Maximum capacity in bytes
        """
        width, height = image.size
        channels = len(image.getbands())
        
        # Each pixel can store 3 bits (1 per channel) for LSB
        # Reserve space for message length header (32 bits)
        total_bits = (width * height * channels) - 32
        return total_bits // 8


class ImageProcessor:
    """Processes images for steganography operations."""
    
    @staticmethod
    def normalize_image(image: Image.Image) -> Image.Image:
        """
        Normalize image to RGB format if needed.
        
        Args:
            image: PIL Image object
            
        Returns:
            Normalized RGB Image
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    
    @staticmethod
    def image_to_array(image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to numpy array.
        
        Args:
            image: PIL Image object
            
        Returns:
            Numpy array representation
        """
        return np.array(image)
    
    @staticmethod
    def array_to_image(array: np.ndarray) -> Image.Image:
        """
        Convert numpy array to PIL Image.
        
        Args:
            array: Numpy array
            
        Returns:
            PIL Image object
        """
        return Image.fromarray(array.astype(np.uint8))
    
    @staticmethod
    def save_image(image: Image.Image, output_path: str) -> None:
        """
        Save image to file with optimal settings.
        
        Args:
            image: PIL Image object
            output_path: Output file path
            
        Raises:
            FileOperationError: If saving fails
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save with optimal settings based on format
            file_ext = os.path.splitext(output_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                image.save(output_path, 'JPEG', quality=95, optimize=True)
            elif file_ext == '.png':
                image.save(output_path, 'PNG', optimize=True)
            else:
                image.save(output_path)
        except Exception as e:
            from .exceptions import FileOperationError
            raise FileOperationError(f"Failed to save image: {str(e)}")
