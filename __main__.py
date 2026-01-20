"""
Main entry point for the steganography tool when run as a module.
"""

import sys
from steganography.cli.main import main

if __name__ == '__main__':
    sys.exit(main())
