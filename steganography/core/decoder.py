"""
LSB Steganography Decoder Module

Implements Least Significant Bit decoding for extracting hidden messages from digital images.
"""

import struct
from typing import Union, Optional
import numpy as np
from PIL import Image

from .image_utils import ImageValidator, ImageProcessor
from .exceptions import DecodingError
from .crypto import SteganographyCrypto, EncryptionError


class SteganoDecoder:
    """
    Decodes secret messages from digital images using LSB technique.
    """
    
    def __init__(self):
        self.validator = ImageValidator()
        self.processor = ImageProcessor()
    
    def decode(self, encoded_path: str, output_as_bytes: bool = False, 
               password: Optional[str] = None) -> Union[str, bytes]:
        """
        Decode a hidden message from an image.
        
        Args:
            encoded_path: Path to the encoded image
            output_as_bytes: If True, return bytes; otherwise return string
            password: Optional password for decryption
            
        Returns:
            Decoded message as string or bytes
            
        Raises:
            DecodingError: If decoding fails
        """
        try:
            # Validate and load image
            image = self.validator.validate_image(encoded_path)
            image = self.processor.normalize_image(image)
            
            # Convert to numpy array
            img_array = self.processor.image_to_array(image)
            
            # Decode the message
            message_bytes = self._decode_message(img_array)
            
            # Check if message is encrypted
            is_encrypted = message_bytes.startswith(b'ENCRYPTED:')
            if is_encrypted:
                if not password:
                    raise DecodingError("Message is encrypted but no password provided")
                
                try:
                    # Remove encryption marker and decrypt
                    encrypted_data = message_bytes[10:]  # Remove 'ENCRYPTED:' prefix
                    crypto = SteganographyCrypto(password)
                    message_bytes = crypto.decrypt(encrypted_data)
                except EncryptionError as e:
                    raise DecodingError(f"Decryption failed: {str(e)}")
            
            # Return in requested format
            if output_as_bytes:
                return message_bytes
            else:
                try:
                    return message_bytes.decode('utf-8')
                except UnicodeDecodeError as e:
                    raise DecodingError(f"Failed to decode message as UTF-8: {str(e)}")
                    
        except Exception as e:
            if isinstance(e, DecodingError):
                raise
            raise DecodingError(f"Failed to decode message: {str(e)}")
    
    def _decode_message(self, img_array: np.ndarray) -> bytes:
        """
        Decode message bytes from image array using LSB technique.
        
        Args:
            img_array: Numpy array of image pixels
            
        Returns:
            Decoded message bytes
        """
        # Flatten the array for easier manipulation
        flat_array = img_array.flatten()
        
        # Extract the message length header (first 32 bits)
        length_bytes = self._extract_bytes(flat_array, 0, 4)
        message_length = struct.unpack('>I', length_bytes)[0]
        
        # Validate message length
        if message_length <= 0:
            raise DecodingError("Invalid message length: 0 or negative")
        
        # Check if we have enough data
        max_possible_length = (len(flat_array) - 32) // 8
        if message_length > max_possible_length:
            raise DecodingError(
                f"Message length ({message_length}) exceeds maximum possible "
                f"length ({max_possible_length})"
            )
        
        # Extract the actual message
        message_bytes = self._extract_bytes(flat_array, 32, message_length)
        
        return message_bytes
    
    def _extract_bytes(self, flat_array: np.ndarray, start_bit: int, 
                      num_bytes: int) -> bytes:
        """
        Extract a specific number of bytes from the LSB of pixel values.
        
        Args:
            flat_array: Flattened image array
            start_bit: Starting bit position
            num_bytes: Number of bytes to extract
            
        Returns:
            Extracted bytes
        """
        result = bytearray()
        
        for byte_index in range(num_bytes):
            byte_value = 0
            for bit_pos in range(8):
                bit_index = start_bit + (byte_index * 8) + bit_pos
                
                if bit_index >= len(flat_array):
                    raise DecodingError("Insufficient pixel data for decoding")
                
                # Extract the LSB
                bit = flat_array[bit_index] & 1
                byte_value |= (bit << bit_pos)
            
            result.append(byte_value)
        
        return bytes(result)
    
    def has_message(self, encoded_path: str) -> bool:
        """
        Check if an image contains a hidden message.
        
        Args:
            encoded_path: Path to the image file
            
        Returns:
            True if a message is detected, False otherwise
        """
        try:
            # Validate and load image
            image = self.validator.validate_image(encoded_path)
            image = self.processor.normalize_image(image)
            
            # Convert to numpy array
            img_array = self.processor.image_to_array(image)
            flat_array = img_array.flatten()
            
            # Try to extract message length
            if len(flat_array) < 32:
                return False
            
            length_bytes = self._extract_bytes(flat_array, 0, 4)
            message_length = struct.unpack('>I', length_bytes)[0]
            
            # Check if message length is reasonable
            max_possible_length = (len(flat_array) - 32) // 8
            return 0 < message_length <= max_possible_length
            
        except Exception:
            return False
