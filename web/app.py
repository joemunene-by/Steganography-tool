"""
Web Interface for Steganography Tool

A minimalist web UI for encoding and decoding messages in images.
"""

import os
import tempfile
import base64
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from io import BytesIO

# Add parent directory to path to import steganography modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steganography.core import SteganoEncoder, SteganoDecoder, SteganographyError
from steganography.core.crypto import SteganographyCrypto

app = Flask(__name__)
app.config['SECRET_KEY'] = 'steganography-web-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    """Encode a message into an image."""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'image' not in request.files:
                flash('No image file selected')
                return redirect(request.url)
            
            file = request.files['image']
            if file.filename == '':
                flash('No image file selected')
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, BMP, TIFF, WEBP')
                return redirect(request.url)
            
            # Get message
            message = request.form.get('message', '')
            password = request.form.get('password', '')
            
            if not message:
                flash('Message cannot be empty')
                return redirect(request.url)
            
            # Save uploaded image temporarily
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Create output path
            output_filename = f'encoded_{filename}'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Encode message
            encoder = SteganoEncoder()
            encoder.encode(input_path, message, output_path, password=password if password else None)
            
            # Clean up input file
            os.remove(input_path)
            
            # Send the encoded image
            return send_file(output_path, as_attachment=True, download_name=output_filename)
            
        except SteganographyError as e:
            flash(f'Steganography error: {str(e)}')
            return redirect(request.url)
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(request.url)
    
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    """Decode a message from an image."""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'image' not in request.files:
                flash('No image file selected')
                return redirect(request.url)
            
            file = request.files['image']
            if file.filename == '':
                flash('No image file selected')
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, BMP, TIFF, WEBP')
                return redirect(request.url)
            
            # Get password
            password = request.form.get('password', '')
            
            # Save uploaded image temporarily
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Decode message
            decoder = SteganoDecoder()
            message = decoder.decode(input_path, password=password if password else None)
            
            # Clean up input file
            os.remove(input_path)
            
            # Handle different message types
            if isinstance(message, str):
                if message.startswith('TEXT_FILE:'):
                    content = message[10:]
                    return render_template('decode.html', message=content, message_type='text_file')
                elif message.startswith('BINARY_FILE:'):
                    parts = message.split(':', 2)
                    filename = parts[1]
                    encoded_data = parts[2]
                    file_data = base64.b64decode(encoded_data)
                    
                    # Create a temporary file for download
                    temp_file = BytesIO(file_data)
                    return send_file(temp_file, as_attachment=True, download_name=filename)
                else:
                    return render_template('decode.html', message=message, message_type='text')
            else:
                # It's bytes
                temp_file = BytesIO(message)
                return send_file(temp_file, as_attachment=True, download_name='decoded_data.bin')
            
        except SteganographyError as e:
            flash(f'Steganography error: {str(e)}')
            return redirect(request.url)
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(request.url)
    
    return render_template('decode.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Analyze an image for steganography properties."""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'image' not in request.files:
                flash('No image file selected')
                return redirect(request.url)
            
            file = request.files['image']
            if file.filename == '':
                flash('No image file selected')
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, BMP, TIFF, WEBP')
                return redirect(request.url)
            
            # Save uploaded image temporarily
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Analyze image
            from steganography.core.analysis import ImageAnalyzer
            analyzer = ImageAnalyzer()
            analysis = analyzer.analyze_image(input_path)
            
            # Check for hidden message
            decoder = SteganoDecoder()
            has_message = decoder.has_message(input_path)
            
            # Calculate capacity
            encoder = SteganoEncoder()
            capacity = encoder.calculate_capacity(input_path)
            
            # Clean up input file
            os.remove(input_path)
            
            return render_template('analyze.html', 
                                 analysis=analysis, 
                                 has_message=has_message, 
                                 capacity=capacity)
            
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(request.url)
    
    return render_template('analyze.html')

@app.route('/tools')
def tools():
    """Tools and utilities page."""
    return render_template('tools.html')

@app.route('/generate-password')
def generate_password():
    """Generate a secure password."""
    try:
        password = SteganographyCrypto.generate_password(32)
        return render_template('tools.html', generated_password=password)
    except Exception as e:
        flash(f'Error generating password: {str(e)}')
        return redirect(url_for('tools'))

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
