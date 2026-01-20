# Professional Steganography Tool

A high-end, professional-grade steganography tool for hiding and extracting secret messages within digital images using the Least Significant Bit (LSB) technique.

## Overview

This steganography tool provides a robust, secure, and efficient solution for embedding confidential information within digital images without perceptible changes to the visual content. Built with professional software engineering principles, it offers comprehensive error handling, extensive validation, and a clean command-line interface.

## Features

- **LSB Steganography**: Advanced Least Significant Bit encoding for maximum capacity with minimal visual impact
- **Multiple Image Formats**: Support for PNG, BMP, TIFF, JPEG, and other common formats
- **Professional CLI**: Intuitive command-line interface with comprehensive help and examples
- **Robust Error Handling**: Comprehensive validation and error reporting
- **Unicode Support**: Full support for international characters and emojis
- **Capacity Analysis**: Built-in tools to calculate maximum message capacity
- **Message Detection**: Verify if an image contains hidden messages
- **Cross-Platform**: Compatible with Windows, macOS, and Linux
- **Extensive Testing**: Comprehensive test suite ensuring reliability

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Development Installation

For development and testing:

```bash
git clone https://github.com/joemunene-by/Steganography-tool.git
cd steganography-tool
pip install -r requirements.txt
pip install -e .
```

## Usage

### Command Line Interface

The tool provides four main operations: encode, decode, capacity, and check.

#### Encode a Message

Hide a text message within an image:

```bash
python -m steganography.cli.main encode -i carrier.png -m "Secret message" -o encoded.png
```

Hide a message from a file:

```bash
python -m steganography.cli.main encode -i carrier.png -f message.txt -o encoded.png
```

#### Decode a Message

Extract a hidden message from an image:

```bash
python -m steganography.cli.main decode -i encoded.png
```

Save decoded message to a file:

```bash
python -m steganography.cli.main decode -i encoded.png -o decoded.txt
```

#### Check Image Capacity

Calculate maximum message capacity:

```bash
python -m steganography.cli.main capacity -i carrier.png
```

#### Detect Hidden Messages

Check if an image contains a hidden message:

```bash
python -m steganography.cli.main check -i encoded.png
```

### Python API

#### Encoding Messages

```python
from steganography.core import SteganoEncoder

encoder = SteganoEncoder()

# Encode a string message
encoder.encode('carrier.png', 'Secret message', 'encoded.png')

# Encode bytes
encoder.encode('carrier.png', b'Binary data', 'encoded.png')
```

#### Decoding Messages

```python
from steganography.core import SteganoDecoder

decoder = SteganoDecoder()

# Decode as string
message = decoder.decode('encoded.png')

# Decode as bytes
message_bytes = decoder.decode('encoded.png', output_as_bytes=True)

# Check for hidden message
has_message = decoder.has_message('encoded.png')
```

#### Capacity Calculation

```python
from steganography.core import SteganoEncoder

encoder = SteganoEncoder()
capacity = encoder.calculate_capacity('carrier.png')
print(f"Maximum capacity: {capacity} bytes")
```

## Technical Architecture

### Core Components

- **SteganoEncoder**: Handles message encoding using LSB technique
- **SteganoDecoder**: Extracts hidden messages from images
- **ImageValidator**: Validates image files and calculates capacity
- **ImageProcessor**: Manages image format conversion and optimization
- **CLI Interface**: Professional command-line interface

### LSB Algorithm

The tool implements a sophisticated LSB steganography algorithm:

1. **Message Preparation**: Converts messages to bytes and adds length header
2. **Bit Embedding**: Modifies the least significant bit of each color channel
3. **Header Management**: Stores message length in first 32 bits for reliable extraction
4. **Error Detection**: Includes validation checks for message integrity

### Security Considerations

- Messages are encoded using UTF-8 for proper character handling
- Binary data is supported for maximum flexibility
- No encryption is applied (use external encryption for sensitive data)
- LSB changes are minimal to avoid statistical detection

## Performance Characteristics

### Capacity Calculation

Maximum message capacity is calculated as:

```
Capacity = (Width × Height × Channels - 32) ÷ 8 bytes
```

Where:
- Width, Height: Image dimensions in pixels
- Channels: Number of color channels (typically 3 for RGB)
- 32: Reserved bits for message length header

### Quality Impact

- LSB encoding results in minimal visual quality degradation
- Changes are limited to the least significant bit of each color channel
- Average quality loss: < 1% PSNR for typical images
- No visible artifacts to the human eye

## Supported Formats

### Input Formats
- PNG (recommended for lossless quality)
- BMP
- TIFF
- JPEG (with quality preservation)
- Most other PIL-supported formats

### Output Formats
- PNG (default, recommended)
- JPEG (with quality optimization)
- BMP
- TIFF

## Error Handling

The tool provides comprehensive error handling for:

- **File Operations**: Invalid paths, permission issues, disk space
- **Image Validation**: Unsupported formats, corrupted files, size limits
- **Message Capacity**: Oversized messages, capacity calculations
- **Encoding/Decoding**: Data integrity, format validation

Error messages are designed to be informative and actionable.

## Testing

### Run Test Suite

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=steganography

# Run specific test file
python -m pytest tests/test_encoder.py
```

### Test Coverage

The test suite includes:
- Unit tests for all core components
- Integration tests for complete workflows
- Edge case testing (empty messages, large files, corruption)
- Cross-platform compatibility tests
- Performance and quality validation

## Development

### Project Structure

```
steganography/
├── core/
│   ├── __init__.py
│   ├── encoder.py
│   ├── decoder.py
│   ├── image_utils.py
│   └── exceptions.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
└── tests/
    ├── __init__.py
    ├── test_encoder.py
    ├── test_decoder.py
    └── test_integration.py
```

### Code Standards

- **PEP 8 Compliance**: Consistent code formatting and style
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings for all public APIs
- **Error Handling**: Robust exception handling with custom error types
- **Testing**: Minimum 90% test coverage requirement

### Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with full test coverage
4. Ensure all tests pass
5. Submit a pull request with detailed description

## Security and Limitations

### Security Notes

- This tool provides steganography, not cryptography
- Messages are not encrypted by default
- Use external encryption for highly sensitive data
- LSB steganography can be detected with statistical analysis
- Consider the security implications of your use case

### Limitations

- Capacity limited by image dimensions
- JPEG compression may affect message integrity
- LSB encoding is vulnerable to statistical analysis
- Not suitable for highly sensitive communications without additional security measures

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues, questions, or contributions:

1. Check the existing documentation
2. Review the test suite for usage examples
3. Submit issues with detailed reproduction steps
4. Provide system information and error logs

## Version History

### Version 1.0.0
- Initial professional release
- LSB encoding/decoding implementation
- Comprehensive CLI interface
- Full test suite coverage
- Multi-platform support

---

**Disclaimer**: This tool is provided for educational and legitimate purposes only. Users are responsible for complying with applicable laws and regulations regarding steganography usage.
