"""
Test suite for the SteganoEncoder class.
"""

import unittest
import tempfile
import os
from PIL import Image
import numpy as np

from steganography.core.encoder import SteganoEncoder
from steganography.core.exceptions import (
    ImageValidationError, 
    MessageCapacityError, 
    EncodingError
)


class TestSteganoEncoder(unittest.TestCase):
    """Test cases for SteganoEncoder functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = SteganoEncoder()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.test_image_path = os.path.join(self.temp_dir, "test.png")
        self.create_test_image(self.test_image_path, 100, 100)
        
        self.small_image_path = os.path.join(self.temp_dir, "small.png")
        self.create_test_image(self.small_image_path, 10, 10)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path: str, width: int, height: int):
        """Create a test image for testing."""
        image = Image.new('RGB', (width, height), color='red')
        image.save(path)
    
    def test_encode_string_message(self):
        """Test encoding a string message."""
        message = "This is a test message"
        output_path = os.path.join(self.temp_dir, "encoded.png")
        
        # Should not raise any exception
        self.encoder.encode(self.test_image_path, message, output_path)
        
        # Verify output file exists
        self.assertTrue(os.path.exists(output_path))
        
        # Verify it's a valid image
        with Image.open(output_path) as img:
            self.assertEqual(img.size, (100, 100))
    
    def test_encode_bytes_message(self):
        """Test encoding a bytes message."""
        message = b"This is a test message in bytes"
        output_path = os.path.join(self.temp_dir, "encoded_bytes.png")
        
        self.encoder.encode(self.test_image_path, message, output_path)
        
        self.assertTrue(os.path.exists(output_path))
    
    def test_encode_empty_message(self):
        """Test encoding an empty message."""
        message = ""
        output_path = os.path.join(self.temp_dir, "encoded_empty.png")
        
        self.encoder.encode(self.test_image_path, message, output_path)
        self.assertTrue(os.path.exists(output_path))
    
    def test_encode_large_message(self):
        """Test encoding a message that exceeds capacity."""
        # Create a very large message
        message = "A" * 10000  # Much larger than small image capacity
        output_path = os.path.join(self.temp_dir, "encoded_large.png")
        
        with self.assertRaises(MessageCapacityError):
            self.encoder.encode(self.small_image_path, message, output_path)
    
    def test_encode_invalid_image_path(self):
        """Test encoding with invalid image path."""
        message = "Test message"
        output_path = os.path.join(self.temp_dir, "output.png")
        
        with self.assertRaises(ImageValidationError):
            self.encoder.encode("nonexistent.png", message, output_path)
    
    def test_encode_invalid_output_path(self):
        """Test encoding with invalid output path."""
        message = "Test message"
        # Try to write to a directory that doesn't exist
        output_path = "/nonexistent/directory/output.png"
        
        with self.assertRaises(EncodingError):
            self.encoder.encode(self.test_image_path, message, output_path)
    
    def test_calculate_capacity(self):
        """Test capacity calculation."""
        capacity = self.encoder.calculate_capacity(self.test_image_path)
        
        # For a 100x100 RGB image: 100*100*3 = 30000 pixels
        # Capacity = (30000 - 32) // 8 = 3746 bytes
        expected_capacity = (100 * 100 * 3 - 32) // 8
        self.assertEqual(capacity, expected_capacity)
    
    def test_calculate_capacity_invalid_path(self):
        """Test capacity calculation with invalid path."""
        with self.assertRaises(ImageValidationError):
            self.encoder.calculate_capacity("nonexistent.png")
    
    def test_encode_different_formats(self):
        """Test encoding with different image formats."""
        message = "Test message"
        
        formats = ['.png', '.bmp', '.jpg']
        
        for fmt in formats:
            # Create test image with specific format
            test_path = os.path.join(self.temp_dir, f"test{fmt}")
            output_path = os.path.join(self.temp_dir, f"encoded{fmt}")
            
            # Create image in the specific format
            img = Image.new('RGB', (50, 50), color='blue')
            img.save(test_path, format=fmt[1:].upper())
            
            # Test encoding
            self.encoder.encode(test_path, message, output_path)
            self.assertTrue(os.path.exists(output_path))
    
    def test_encode_unicode_message(self):
        """Test encoding Unicode characters."""
        message = "Test message with unicode: 你好, 🌍, café"
        output_path = os.path.join(self.temp_dir, "encoded_unicode.png")
        
        self.encoder.encode(self.test_image_path, message, output_path)
        self.assertTrue(os.path.exists(output_path))
    
    def test_encode_message_with_newlines(self):
        """Test encoding message with newlines and special characters."""
        message = "Line 1\nLine 2\tTabbed\nSpecial: !@#$%^&*()"
        output_path = os.path.join(self.temp_dir, "encoded_special.png")
        
        self.encoder.encode(self.test_image_path, message, output_path)
        self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    unittest.main()
