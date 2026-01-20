"""
Encryption utilities for enhanced steganography security.
"""

import base64
import hashlib
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from .exceptions import SteganographyError


class EncryptionError(SteganographyError):
    """Raised when encryption/decryption operations fail."""
    pass


class SteganographyCrypto:
    """
    Provides encryption and decryption capabilities for steganographic messages.
    Uses AES-256-CBC for secure encryption.
    """
    
    def __init__(self, password: str):
        """
        Initialize crypto with password.
        
        Args:
            password: Password for encryption/decryption
        """
        if not password:
            raise EncryptionError("Password cannot be empty")
        
        self.password = password.encode('utf-8')
        self.key_length = 32  # AES-256
        self.iv_length = 16   # AES block size
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            salt: Salt for key derivation
            
        Returns:
            Derived key
        """
        return hashlib.pbkdf2_hmac('sha256', self.password, salt, 100000)
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using AES-256-CBC.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data with salt and IV prepended
        """
        try:
            # Generate random salt and IV
            salt = os.urandom(16)
            iv = os.urandom(self.iv_length)
            
            # Derive key
            key = self._derive_key(salt)
            
            # Apply PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Encrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Return salt + iv + encrypted_data
            return salt + iv + encrypted_data
            
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using AES-256-CBC.
        
        Args:
            encrypted_data: Data to decrypt (with salt and IV prepended)
            
        Returns:
            Decrypted data
        """
        try:
            # Extract salt, IV, and encrypted data
            salt = encrypted_data[:16]
            iv = encrypted_data[16:16 + self.iv_length]
            ciphertext = encrypted_data[16 + self.iv_length:]
            
            # Derive key
            key = self._derive_key(salt)
            
            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove PKCS7 padding
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data
            
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def encrypt_message(self, message: str) -> str:
        """
        Encrypt a string message and return base64 encoded result.
        
        Args:
            message: Message to encrypt
            
        Returns:
            Base64 encoded encrypted message
        """
        message_bytes = message.encode('utf-8')
        encrypted_bytes = self.encrypt(message_bytes)
        return base64.b64encode(encrypted_bytes).decode('ascii')
    
    def decrypt_message(self, encrypted_message: str) -> str:
        """
        Decrypt a base64 encoded encrypted message.
        
        Args:
            encrypted_message: Base64 encoded encrypted message
            
        Returns:
            Decrypted message as string
        """
        encrypted_bytes = base64.b64decode(encrypted_message.encode('ascii'))
        decrypted_bytes = self.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    
    @staticmethod
    def generate_password(length: int = 32) -> str:
        """
        Generate a cryptographically secure random password.
        
        Args:
            length: Length of password to generate
            
        Returns:
            Random password string
        """
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
        return ''.join(os.urandom(1)[0] % len(alphabet) for _ in range(length))
