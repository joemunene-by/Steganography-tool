"""
LSB Steganography Encoder Module

Implements Least Significant Bit encoding for hiding messages in digital images.
"""

import struct
from typing import Union
import numpy as np
from PIL import Image

from .image_utils import ImageValidator, ImageProcessor
from .exceptions import MessageCapacityError, EncodingError


class SteganoEncoder:
    """
    Encodes secret messages into digital images using LSB technique.
    """
    
    def __init__(self):
        self.validator = ImageValidator()
        self.processor = ImageProcessor()
    
    def encode(self, carrier_path: str, message: Union[str, bytes], 
               output_path: str) -> None:
        """
        Encode a message into an image using LSB steganography.
        
        Args:
            carrier_path: Path to the carrier image
            message: Message to hide (string or bytes)
            output_path: Path to save the encoded image
            
        Raises:
            EncodingError: If encoding fails
            MessageCapacityError: If message is too large
        """
        try:
            # Validate and load image
            image = self.validator.validate_image(carrier_path)
            image = self.processor.normalize_image(image)
            
            # Convert message to bytes if needed
            if isinstance(message, str):
                message_bytes = message.encode('utf-8')
            else:
                message_bytes = message
            
            # Check capacity
            max_capacity = self.validator.calculate_capacity(image)
            if len(message_bytes) > max_capacity:
                raise MessageCapacityError(
                    f"Message too large: {len(message_bytes)} bytes. "
                    f"Maximum capacity: {max_capacity} bytes"
                )
            
            # Convert to numpy array for manipulation
            img_array = self.processor.image_to_array(image)
            
            # Encode the message
            encoded_array = self._encode_message(img_array, message_bytes)
            
            # Convert back to PIL Image and save
            encoded_image = self.processor.array_to_image(encoded_array)
            self.processor.save_image(encoded_image, output_path)
            
        except Exception as e:
            if isinstance(e, (MessageCapacityError, EncodingError)):
                raise
            raise EncodingError(f"Failed to encode message: {str(e)}")
    
    def _encode_message(self, img_array: np.ndarray, message: bytes) -> np.ndarray:
        """
        Encode message bytes into image array using LSB technique.
        
        Args:
            img_array: Numpy array of image pixels
            message: Message bytes to encode
            
        Returns:
            Modified image array with encoded message
        """
        # Create a copy to avoid modifying the original
        encoded_array = img_array.copy()
        
        # Flatten the array for easier manipulation
        flat_array = encoded_array.flatten()
        
        # Add message length header (32 bits)
        message_length = len(message)
        length_bytes = struct.pack('>I', message_length)  # Big-endian unsigned int
        
        # Combine length header and message
        data_to_encode = length_bytes + message
        
        # Encode each bit of the data into the LSB of pixel values
        bit_index = 0
        for byte in data_to_encode:
            for bit_pos in range(8):
                if bit_index >= len(flat_array):
                    raise EncodingError("Insufficient pixel data for encoding")
                
                # Get the current bit
                bit = (byte >> bit_pos) & 1
                
                # Clear the LSB and set it to our bit
                flat_array[bit_index] = (flat_array[bit_index] & 0xFE) | bit
                
                bit_index += 1
        
        # Reshape back to original dimensions
        return flat_array.reshape(encoded_array.shape)
    
    def calculate_capacity(self, image_path: str) -> int:
        """
        Calculate the maximum message capacity for an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Maximum capacity in bytes
        """
        image = self.validator.validate_image(image_path)
        return self.validator.calculate_capacity(image)
