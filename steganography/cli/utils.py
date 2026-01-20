"""
Utility functions for the CLI interface.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging if True
    """
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_paths(input_path: str, output_path: str = None) -> bool:
    """
    Validate input and output file paths.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file (optional)
        
    Returns:
        True if paths are valid, False otherwise
    """
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return False
    
    # Check if input file is readable
    if not os.access(input_path, os.R_OK):
        print(f"Error: Cannot read input file: {input_path}", file=sys.stderr)
        return False
    
    # Validate output path if provided
    if output_path:
        # Check if output directory exists and is writable
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                print(f"Error: Cannot create output directory: {e}", file=sys.stderr)
                return False
        
        if output_dir and not os.access(output_dir, os.W_OK):
            print(f"Error: Cannot write to output directory: {output_dir}", file=sys.stderr)
            return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f} {size_names[i]}"


def get_file_extension(file_path: str) -> str:
    """
    Get file extension from file path.
    
    Args:
        file_path: Path to file
        
    Returns:
        File extension (including dot)
    """
    return Path(file_path).suffix.lower()


def ensure_extension(file_path: str, default_ext: str) -> str:
    """
    Ensure file has the specified extension.
    
    Args:
        file_path: Original file path
        default_ext: Default extension to add (including dot)
        
    Returns:
        File path with ensured extension
    """
    current_ext = get_file_extension(file_path)
    if not current_ext:
        return file_path + default_ext
    return file_path
