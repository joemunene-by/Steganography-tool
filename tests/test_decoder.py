"""
Test suite for the SteganoDecoder class.
"""

import unittest
import tempfile
import os
from PIL import Image

from steganography.core.encoder import SteganoEncoder
from steganography.core.decoder import SteganoDecoder
from steganography.core.exceptions import DecodingError


class TestSteganoDecoder(unittest.TestCase):
    """Test cases for SteganoDecoder functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = SteganoEncoder()
        self.decoder = SteganoDecoder()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.test_image_path = os.path.join(self.temp_dir, "test.png")
        self.create_test_image(self.test_image_path, 100, 100)
        
        self.encoded_image_path = os.path.join(self.temp_dir, "encoded.png")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path: str, width: int, height: int):
        """Create a test image for testing."""
        image = Image.new('RGB', (width, height), color='red')
        image.save(path)
    
    def test_decode_string_message(self):
        """Test decoding a string message."""
        original_message = "This is a test message"
        
        # Encode the message
        self.encoder.encode(self.test_image_path, original_message, self.encoded_image_path)
        
        # Decode the message
        decoded_message = self.decoder.decode(self.encoded_image_path)
        
        self.assertEqual(original_message, decoded_message)
    
    def test_decode_bytes_message(self):
        """Test decoding a bytes message."""
        original_message = b"This is a test message in bytes"
        
        # Encode the message
        self.encoder.encode(self.test_image_path, original_message, self.encoded_image_path)
        
        # Decode the message as bytes
        decoded_message = self.decoder.decode(self.encoded_image_path, output_as_bytes=True)
        
        self.assertEqual(original_message, decoded_message)
    
    def test_decode_empty_message(self):
        """Test decoding an empty message."""
        original_message = ""
        
        # Encode the message
        self.encoder.encode(self.test_image_path, original_message, self.encoded_image_path)
        
        # Decode the message
        decoded_message = self.decoder.decode(self.encoded_image_path)
        
        self.assertEqual(original_message, decoded_message)
    
    def test_decode_unicode_message(self):
        """Test decoding Unicode characters."""
        original_message = "Test message with unicode: 你好, 🌍, café"
        
        # Encode the message
        self.encoder.encode(self.test_image_path, original_message, self.encoded_image_path)
        
        # Decode the message
        decoded_message = self.decoder.decode(self.encoded_image_path)
        
        self.assertEqual(original_message, decoded_message)
    
    def test_decode_message_with_newlines(self):
        """Test decoding message with newlines and special characters."""
        original_message = "Line 1\nLine 2\tTabbed\nSpecial: !@#$%^&*()"
        
        # Encode the message
        self.encoder.encode(self.test_image_path, original_message, self.encoded_image_path)
        
        # Decode the message
        decoded_message = self.decoder.decode(self.encoded_image_path)
        
        self.assertEqual(original_message, decoded_message)
    
    def test_decode_no_message(self):
        """Test decoding from an image with no hidden message."""
        with self.assertRaises(DecodingError):
            self.decoder.decode(self.test_image_path)
    
    def test_decode_invalid_image_path(self):
        """Test decoding with invalid image path."""
        with self.assertRaises(DecodingError):
            self.decoder.decode("nonexistent.png")
    
    def test_has_message_true(self):
        """Test has_message with image containing hidden message."""
        original_message = "Test message"
        
        # Encode the message
        self.encoder.encode(self.test_image_path, original_message, self.encoded_image_path)
        
        # Check if message is detected
        self.assertTrue(self.decoder.has_message(self.encoded_image_path))
    
    def test_has_message_false(self):
        """Test has_message with image without hidden message."""
        self.assertFalse(self.decoder.has_message(self.test_image_path))
    
    def test_has_message_invalid_path(self):
        """Test has_message with invalid path."""
        self.assertFalse(self.decoder.has_message("nonexistent.png"))
    
    def test_decode_different_formats(self):
        """Test decoding from different image formats."""
        original_message = "Test message for different formats"
        
        formats = ['.png', '.bmp', '.jpg']
        
        for fmt in formats:
            # Create test image with specific format
            test_path = os.path.join(self.temp_dir, f"test{fmt}")
            encoded_path = os.path.join(self.temp_dir, f"encoded{fmt}")
            
            # Create image in the specific format
            img = Image.new('RGB', (50, 50), color='blue')
            img.save(test_path, format=fmt[1:].upper())
            
            # Encode and decode
            self.encoder.encode(test_path, original_message, encoded_path)
            decoded_message = self.decoder.decode(encoded_path)
            
            self.assertEqual(original_message, decoded_message)
    
    def test_decode_large_message(self):
        """Test decoding a large message."""
        # Create a larger image for this test
        large_image_path = os.path.join(self.temp_dir, "large.png")
        self.create_test_image(large_image_path, 500, 500)
        
        original_message = "A" * 1000  # 1000 character message
        
        # Encode the message
        self.encoder.encode(large_image_path, original_message, self.encoded_image_path)
        
        # Decode the message
        decoded_message = self.decoder.decode(self.encoded_image_path)
        
        self.assertEqual(original_message, decoded_message)
    
    def test_decode_corrupted_image(self):
        """Test decoding from a corrupted image."""
        # Create a corrupted image file
        corrupted_path = os.path.join(self.temp_dir, "corrupted.png")
        with open(corrupted_path, 'wb') as f:
            f.write(b"This is not a valid image file")
        
        with self.assertRaises(DecodingError):
            self.decoder.decode(corrupted_path)


if __name__ == '__main__':
    unittest.main()
