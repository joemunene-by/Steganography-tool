"""
Utility functions for the CLI interface.
"""

import logging
import os
import sys
from pathlib import Path
import time
from typing import Optional


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


def progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", 
                length: int = 50, fill: str = '█') -> None:
    """
    Display a progress bar in the console.
    
    Args:
        current: Current progress value
        total: Total value
        prefix: Prefix text
        suffix: Suffix text
        length: Bar length in characters
        fill: Fill character
    """
    if total == 0:
        return
    
    percent = 100 * (current / float(total))
    filled_length = int(length * current // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    
    print(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}', end='\r')
    
    # Print new line on completion
    if current == total:
        print()


class ProgressTracker:
    """Advanced progress tracker with time estimation."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the operation
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = self.start_time
    
    def update(self, increment: int = 1) -> None:
        """
        Update progress.
        
        Args:
            increment: Amount to increment progress
        """
        self.current += increment
        self.last_update = time.time()
        
        # Calculate estimated time remaining
        elapsed = self.last_update - self.start_time
        if self.current > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = f"ETA: {remaining:.1f}s"
        else:
            eta_str = "ETA: --"
        
        # Display progress
        progress_bar(
            self.current, self.total,
            prefix=f"{self.description}",
            suffix=f"{self.current}/{self.total} ({eta_str})"
        )
    
    def finish(self) -> None:
        """Mark progress as complete."""
        self.current = self.total
        elapsed = self.last_update - self.start_time
        progress_bar(
            self.current, self.total,
            prefix=f"{self.description}",
            suffix=f"Complete in {elapsed:.1f}s"
        )
        print()


def get_password(prompt: str = "Enter password: ") -> str:
    """
    Get password from user input securely.
    
    Args:
        prompt: Prompt to display
        
    Returns:
        Password string
    """
    try:
        import getpass
        return getpass.getpass(prompt)
    except ImportError:
        # Fallback for systems without getpass
        return input(prompt)


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask for user confirmation.
    
    Args:
        message: Confirmation message
        default: Default response if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    
    while True:
        response = input(message + suffix + ": ").lower().strip()
        
        if not response:
            return default
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'.")
