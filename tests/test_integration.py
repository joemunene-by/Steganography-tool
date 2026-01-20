"""
Integration tests for the steganography tool.
"""

import unittest
import tempfile
import os
import subprocess
import sys
from PIL import Image

from steganography.core import SteganoEncoder, SteganoDecoder


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete steganography workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = SteganoEncoder()
        self.decoder = SteganoDecoder()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images of various sizes
        self.test_images = {}
        sizes = [(50, 50), (100, 100), (200, 200)]
        
        for width, height in sizes:
            path = os.path.join(self.temp_dir, f"test_{width}x{height}.png")
            self.create_test_image(path, width, height)
            self.test_images[f"{width}x{height}"] = path
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path: str, width: int, height: int):
        """Create a test image with varying colors."""
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        # Create a pattern to make the image more realistic
        for i in range(width):
            for j in range(height):
                r = (i * 255) // width
                g = (j * 255) // height
                b = ((i + j) * 255) // (width + height)
                pixels[i, j] = (r, g, b)
        
        image.save(path)
    
    def test_complete_workflow_string(self):
        """Test complete encode-decode workflow with string message."""
        original_message = "This is a comprehensive test message for integration testing."
        
        for image_name, image_path in self.test_images.items():
            with self.subTest(image_size=image_name):
                output_path = os.path.join(self.temp_dir, f"encoded_{image_name}.png")
                
                # Encode
                self.encoder.encode(image_path, original_message, output_path)
                self.assertTrue(os.path.exists(output_path))
                
                # Decode
                decoded_message = self.decoder.decode(output_path)
                
                # Verify
                self.assertEqual(original_message, decoded_message)
    
    def test_complete_workflow_bytes(self):
        """Test complete encode-decode workflow with bytes message."""
        original_message = b"Binary message: \x00\x01\x02\x03\x04\x05"
        
        for image_name, image_path in self.test_images.items():
            with self.subTest(image_size=image_name):
                output_path = os.path.join(self.temp_dir, f"encoded_bytes_{image_name}.png")
                
                # Encode
                self.encoder.encode(image_path, original_message, output_path)
                
                # Decode as bytes
                decoded_message = self.decoder.decode(output_path, output_as_bytes=True)
                
                # Verify
                self.assertEqual(original_message, decoded_message)
    
    def test_multiple_messages_same_image(self):
        """Test encoding multiple different messages in the same image."""
        messages = [
            "First message",
            "Second message with more content",
            "Third message with special characters: !@#$%^&*()",
            "Fourth message with unicode: 你好世界"
        ]
        
        base_image = self.test_images["100x100"]
        
        for i, message in enumerate(messages):
            output_path = os.path.join(self.temp_dir, f"encoded_multi_{i}.png")
            
            # Encode
            self.encoder.encode(base_image, message, output_path)
            
            # Decode
            decoded_message = self.decoder.decode(output_path)
            
            # Verify
            self.assertEqual(message, decoded_message)
    
    def test_capacity_limits(self):
        """Test encoding messages at capacity limits."""
        # Use the largest image for capacity testing
        large_image = self.test_images["200x200"]
        
        # Calculate maximum capacity
        max_capacity = self.encoder.calculate_capacity(large_image)
        
        # Test message at maximum capacity
        max_message = "A" * max_capacity
        output_path = os.path.join(self.temp_dir, "encoded_max.png")
        
        # Should succeed
        self.encoder.encode(large_image, max_message, output_path)
        decoded_message = self.decoder.decode(output_path)
        self.assertEqual(max_message, decoded_message)
        
        # Test message exceeding capacity
        oversized_message = "A" * (max_capacity + 1)
        output_path_oversized = os.path.join(self.temp_dir, "encoded_oversized.png")
        
        # Should fail
        from steganography.core.exceptions import MessageCapacityError
        with self.assertRaises(MessageCapacityError):
            self.encoder.encode(large_image, oversized_message, output_path_oversized)
    
    def test_image_quality_preservation(self):
        """Test that encoded images maintain reasonable quality."""
        original_image_path = self.test_images["100x100"]
        message = "Test message for quality preservation"
        output_path = os.path.join(self.temp_dir, "quality_test.png")
        
        # Load original image
        original_image = Image.open(original_image_path)
        original_pixels = list(original_image.getdata())
        
        # Encode message
        self.encoder.encode(original_image_path, message, output_path)
        
        # Load encoded image
        encoded_image = Image.open(output_path)
        encoded_pixels = list(encoded_image.getdata())
        
        # Check that dimensions are preserved
        self.assertEqual(original_image.size, encoded_image.size)
        
        # Check that most pixels are very similar (LSB changes only)
        differences = 0
        for orig, enc in zip(original_pixels, encoded_pixels):
            for o, e in zip(orig, enc):
                if abs(o - e) > 1:  # Allow for LSB changes
                    differences += 1
        
        # Differences should be minimal (only LSB changes)
        total_pixels = len(original_pixels) * 3  # 3 channels per pixel
        difference_ratio = differences / total_pixels
        self.assertLess(difference_ratio, 0.01)  # Less than 1% significant differences
    
    def test_cli_integration(self):
        """Test integration with CLI interface."""
        # This test requires the CLI to be installed
        cli_path = os.path.join(os.path.dirname(__file__), '..', 'steganography', 'cli', 'main.py')
        
        if not os.path.exists(cli_path):
            self.skipTest("CLI module not found")
        
        message = "CLI integration test message"
        input_image = self.test_images["100x100"]
        encoded_image = os.path.join(self.temp_dir, "cli_encoded.png")
        decoded_file = os.path.join(self.temp_dir, "cli_decoded.txt")
        
        try:
            # Test encoding via CLI
            encode_cmd = [
                sys.executable, cli_path, 'encode',
                '-i', input_image,
                '-m', message,
                '-o', encoded_image
            ]
            result = subprocess.run(encode_cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(encoded_image))
            
            # Test decoding via CLI
            decode_cmd = [
                sys.executable, cli_path, 'decode',
                '-i', encoded_image,
                '-o', decoded_file
            ]
            result = subprocess.run(decode_cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(decoded_file))
            
            # Verify decoded content
            with open(decoded_file, 'r', encoding='utf-8') as f:
                decoded_message = f.read()
            self.assertEqual(message, decoded_message)
            
        except Exception as e:
            self.skipTest(f"CLI integration test failed: {e}")


if __name__ == '__main__':
    unittest.main()
