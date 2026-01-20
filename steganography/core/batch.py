"""
Batch processing utilities for steganography operations.
"""

import os
import glob
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .encoder import SteganoEncoder
from .decoder import SteganoDecoder
from .exceptions import SteganographyError


class BatchProcessor:
    """
    Handles batch processing of multiple steganography operations.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.encoder = SteganoEncoder()
        self.decoder = SteganoDecoder()
    
    def batch_encode(self, operations: List[Dict], progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Encode multiple messages in parallel.
        
        Args:
            operations: List of encoding operations, each containing:
                - input_path: Path to carrier image
                - message: Message to encode
                - output_path: Path to save encoded image
                - password: Optional encryption password
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of results with success/failure status
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_op = {
                executor.submit(
                    self._encode_single,
                    op['input_path'],
                    op['message'],
                    op['output_path'],
                    op.get('password')
                ): op for op in operations
            }
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_op)):
                op = future_to_op[future]
                try:
                    future.result()
                    result = {
                        'operation': op,
                        'status': 'success',
                        'error': None
                    }
                except Exception as e:
                    result = {
                        'operation': op,
                        'status': 'error',
                        'error': str(e)
                    }
                
                results.append(result)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(i + 1, len(operations), result)
        
        return results
    
    def batch_decode(self, operations: List[Dict], progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Decode multiple messages in parallel.
        
        Args:
            operations: List of decoding operations, each containing:
                - input_path: Path to encoded image
                - output_path: Optional path to save decoded message
                - password: Optional decryption password
                - output_as_bytes: Whether to return bytes instead of string
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of results with decoded messages or errors
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_op = {
                executor.submit(
                    self._decode_single,
                    op['input_path'],
                    op.get('output_as_bytes', False),
                    op.get('password')
                ): op for op in operations
            }
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_op)):
                op = future_to_op[future]
                try:
                    decoded_message = future.result()
                    
                    # Save to file if output path specified
                    if op.get('output_path'):
                        mode = 'wb' if op.get('output_as_bytes') else 'w'
                        with open(op['output_path'], mode) as f:
                            f.write(decoded_message)
                    
                    result = {
                        'operation': op,
                        'status': 'success',
                        'message': decoded_message,
                        'error': None
                    }
                except Exception as e:
                    result = {
                        'operation': op,
                        'status': 'error',
                        'message': None,
                        'error': str(e)
                    }
                
                results.append(result)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(i + 1, len(operations), result)
        
        return results
    
    def _encode_single(self, input_path: str, message: str, output_path: str, password: Optional[str] = None):
        """Encode a single message."""
        self.encoder.encode(input_path, message, output_path, password)
    
    def _decode_single(self, input_path: str, output_as_bytes: bool = False, password: Optional[str] = None):
        """Decode a single message."""
        return self.decoder.decode(input_path, output_as_bytes, password)
    
    @staticmethod
    def find_images(directory: str, pattern: str = "*") -> List[str]:
        """
        Find all image files in a directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern (default: all files)
            
        Returns:
            List of image file paths
        """
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff', '*.tif']
        image_files = []
        
        for ext in image_extensions:
            search_pattern = os.path.join(directory, pattern + ext)
            image_files.extend(glob.glob(search_pattern))
        
        return sorted(image_files)
    
    @staticmethod
    def create_batch_operations(input_dir: str, output_dir: str, message: str, 
                               password: Optional[str] = None) -> List[Dict]:
        """
        Create batch encoding operations for all images in a directory.
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory for output images
            message: Message to encode in all images
            password: Optional encryption password
            
        Returns:
            List of batch operations
        """
        operations = []
        image_files = BatchProcessor.find_images(input_dir)
        
        for input_path in image_files:
            # Create output path
            input_filename = os.path.basename(input_path)
            name, ext = os.path.splitext(input_filename)
            output_path = os.path.join(output_dir, f"{name}_encoded{ext}")
            
            operations.append({
                'input_path': input_path,
                'message': message,
                'output_path': output_path,
                'password': password
            })
        
        return operations
