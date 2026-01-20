"""
Command Line Interface for the Steganography Tool

Provides professional CLI for encoding and decoding messages in images.
"""

import argparse
import sys
import os
from pathlib import Path

from ..core import SteganoEncoder, SteganoDecoder, SteganographyError
from ..core.batch import BatchProcessor
from ..core.analysis import ImageAnalyzer
from ..core.crypto import SteganographyCrypto
from ..core.config import get_config, ConfigManager
from .utils import setup_logging, validate_paths, progress_bar


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='steganography',
        description='Professional Steganography Tool for hiding messages in digital images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  steganography encode -i image.png -m "Secret message" -o encoded.png
  steganography decode -i encoded.png
  steganography capacity -i image.png
  steganography check -i encoded.png
  steganography analyze -i image.png
  steganography batch-encode -d ./images -m "Secret" -o ./output
  steganography generate-password --length 32
        """
    )
    
    # Add verbosity option
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Add configuration option
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file'
    )
    
    # Add password option
    parser.add_argument(
        '-p', '--password',
        help='Password for encryption/decryption'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encode command
    encode_parser = subparsers.add_parser(
        'encode',
        help='Encode a message into an image'
    )
    encode_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the carrier image'
    )
    encode_parser.add_argument(
        '-m', '--message',
        help='Message to encode (use quotes for strings)'
    )
    encode_parser.add_argument(
        '-f', '--file',
        help='File containing the message to encode'
    )
    encode_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to save the encoded image'
    )
    
    # Decode command
    decode_parser = subparsers.add_parser(
        'decode',
        help='Decode a message from an image'
    )
    decode_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the encoded image'
    )
    decode_parser.add_argument(
        '-o', '--output',
        help='Path to save the decoded message (optional)'
    )
    decode_parser.add_argument(
        '--bytes',
        action='store_true',
        help='Output message as bytes instead of string'
    )
    
    # Capacity command
    capacity_parser = subparsers.add_parser(
        'capacity',
        help='Check the maximum message capacity of an image'
    )
    capacity_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the image'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check if an image contains a hidden message'
    )
    check_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the image'
    )
    
    return parser


def handle_encode(args) -> int:
    """Handle the encode command."""
    try:
        # Validate input arguments
        if not args.message and not args.file:
            print("Error: Either --message or --file must be specified", file=sys.stderr)
            return 1
        
        if args.message and args.file:
            print("Error: Cannot specify both --message and --file", file=sys.stderr)
            return 1
        
        # Get message content
        if args.message:
            message = args.message
        else:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    message = f.read()
            except Exception as e:
                print(f"Error reading message file: {e}", file=sys.stderr)
                return 1
        
        # Validate paths
        if not validate_paths(args.input, args.output):
            return 1
        
        # Perform encoding
        encoder = SteganoEncoder()
        encoder.encode(args.input, message, args.output)
        
        print(f"Successfully encoded message into {args.output}")
        return 0
        
    except SteganographyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_decode(args) -> int:
    """Handle the decode command."""
    try:
        # Validate input path
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        
        # Perform decoding
        decoder = SteganoDecoder()
        message = decoder.decode(args.input, output_as_bytes=args.bytes)
        
        # Output message
        if args.output:
            try:
                mode = 'wb' if args.bytes else 'w'
                with open(args.output, mode) as f:
                    f.write(message)
                print(f"Successfully decoded message to {args.output}")
            except Exception as e:
                print(f"Error writing output file: {e}", file=sys.stderr)
                return 1
        else:
            if args.bytes:
                print(f"Decoded message (bytes): {message}")
            else:
                print(f"Decoded message: {message}")
        
        return 0
        
    except SteganographyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_capacity(args) -> int:
    """Handle the capacity command."""
    try:
        # Validate input path
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        
        # Calculate capacity
        encoder = SteganoEncoder()
        capacity = encoder.calculate_capacity(args.input)
        
        print(f"Maximum message capacity: {capacity} bytes")
        print(f"Maximum message capacity: {capacity / 1024:.2f} KB")
        return 0
        
    except SteganographyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_check(args) -> int:
    """Handle the check command."""
    try:
        # Validate input path
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        
        # Check for message
        decoder = SteganoDecoder()
        has_message = decoder.has_message(args.input)
        
        if has_message:
            print("Hidden message detected in the image")
            return 0
        else:
            print("No hidden message detected in the image")
            return 1
        
    except SteganographyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle different commands
    if args.command == 'encode':
        return handle_encode(args)
    elif args.command == 'decode':
        return handle_decode(args)
    elif args.command == 'capacity':
        return handle_capacity(args)
    elif args.command == 'check':
        return handle_check(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
