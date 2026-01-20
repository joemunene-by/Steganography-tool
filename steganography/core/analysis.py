"""
Image analysis and statistics utilities for steganography.
"""

import os
import numpy as np
from typing import Dict, List, Tuple, Optional
from PIL import Image
import math

from .image_utils import ImageValidator
from .exceptions import ImageValidationError


class ImageAnalyzer:
    """
    Provides detailed analysis and statistics for images used in steganography.
    """
    
    def __init__(self):
        self.validator = ImageValidator()
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Perform comprehensive analysis of an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        # Validate and load image
        image = self.validator.validate_image(image_path)
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        analysis = {
            'file_info': self._analyze_file(image_path),
            'image_properties': self._analyze_properties(image),
            'capacity_analysis': self._analyze_capacity(image),
            'statistical_analysis': self._analyze_statistics(img_array),
            'steganography_suitability': self._analyze_suitability(img_array)
        }
        
        return analysis
    
    def _analyze_file(self, image_path: str) -> Dict:
        """Analyze file properties."""
        stat = os.stat(image_path)
        
        return {
            'file_size': stat.st_size,
            'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
            'file_extension': os.path.splitext(image_path)[1].lower(),
            'last_modified': stat.st_mtime
        }
    
    def _analyze_properties(self, image: Image.Image) -> Dict:
        """Analyze image properties."""
        return {
            'dimensions': image.size,
            'width': image.size[0],
            'height': image.size[1],
            'total_pixels': image.size[0] * image.size[1],
            'mode': image.mode,
            'color_channels': len(image.getbands()),
            'has_transparency': 'transparency' in image.info or image.mode in ('RGBA', 'LA')
        }
    
    def _analyze_capacity(self, image: Image.Image) -> Dict:
        """Analyze steganography capacity."""
        width, height = image.size
        channels = len(image.getbands())
        
        # Calculate theoretical maximum
        total_bits = width * height * channels
        max_capacity_bytes = (total_bits - 32) // 8  # Reserve 32 bits for length header
        
        # Calculate practical capacity (90% of theoretical to be safe)
        practical_capacity = int(max_capacity_bytes * 0.9)
        
        return {
            'total_bits_available': total_bits,
            'max_capacity_bytes': max_capacity_bytes,
            'max_capacity_kb': round(max_capacity_bytes / 1024, 2),
            'practical_capacity_bytes': practical_capacity,
            'practical_capacity_kb': round(practical_capacity / 1024, 2),
            'bits_per_pixel': channels,
            'efficiency': round((32 / total_bits) * 100, 4)  # Header overhead percentage
        }
    
    def _analyze_statistics(self, img_array: np.ndarray) -> Dict:
        """Analyze statistical properties of the image."""
        stats = {}
        
        # Overall statistics
        stats['overall'] = {
            'mean': float(np.mean(img_array)),
            'std_dev': float(np.std(img_array)),
            'min': int(np.min(img_array)),
            'max': int(np.max(img_array)),
            'median': float(np.median(img_array))
        }
        
        # Channel-wise statistics
        if len(img_array.shape) == 3:  # Color image
            channel_names = ['Red', 'Green', 'Blue']
            if img_array.shape[2] == 4:
                channel_names = ['Red', 'Green', 'Blue', 'Alpha']
            
            stats['channels'] = {}
            for i, channel_name in enumerate(channel_names):
                if i < img_array.shape[2]:
                    channel_data = img_array[:, :, i]
                    stats['channels'][channel_name] = {
                        'mean': float(np.mean(channel_data)),
                        'std_dev': float(np.std(channel_data)),
                        'min': int(np.min(channel_data)),
                        'max': int(np.max(channel_data)),
                        'median': float(np.median(channel_data))
                    }
        
        # Histogram analysis
        stats['histogram'] = self._analyze_histogram(img_array)
        
        return stats
    
    def _analyze_histogram(self, img_array: np.ndarray) -> Dict:
        """Analyze histogram properties."""
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
        
        # Calculate histogram statistics
        non_zero_bins = np.count_nonzero(hist)
        entropy = self._calculate_entropy(hist)
        
        return {
            'bins_used': int(non_zero_bins),
            'bins_unused': int(256 - non_zero_bins),
            'entropy': float(entropy),
            'peak_frequency': int(np.max(hist)),
            'peak_value': int(np.argmax(hist))
        }
    
    def _calculate_entropy(self, histogram: np.ndarray) -> float:
        """Calculate entropy of histogram."""
        # Normalize histogram to get probabilities
        hist_normalized = histogram / np.sum(histogram)
        
        # Remove zero probabilities
        hist_normalized = hist_normalized[hist_normalized > 0]
        
        # Calculate entropy
        entropy = -np.sum(hist_normalized * np.log2(hist_normalized))
        
        return entropy
    
    def _analyze_suitability(self, img_array: np.ndarray) -> Dict:
        """Analyze suitability for steganography."""
        # LSB variance analysis
        lsb_variance = self._calculate_lsb_variance(img_array)
        
        # Noise estimation
        noise_level = self._estimate_noise_level(img_array)
        
        # Color diversity
        color_diversity = self._calculate_color_diversity(img_array)
        
        # Overall suitability score (0-100)
        suitability_score = self._calculate_suitability_score(
            lsb_variance, noise_level, color_diversity
        )
        
        return {
            'lsb_variance': float(lsb_variance),
            'noise_level': float(noise_level),
            'color_diversity': float(color_diversity),
            'suitability_score': round(suitability_score, 2),
            'recommendation': self._get_recommendation(suitability_score)
        }
    
    def _calculate_lsb_variance(self, img_array: np.ndarray) -> float:
        """Calculate variance of least significant bits."""
        lsb = img_array & 1  # Extract LSBs
        return float(np.var(lsb))
    
    def _estimate_noise_level(self, img_array: np.ndarray) -> float:
        """Estimate noise level in the image."""
        # Simple noise estimation using Laplacian operator
        if len(img_array.shape) == 3:
            # Convert to grayscale for noise estimation
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
        
        # Apply Laplacian kernel
        laplacian = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        
        # Simple convolution (edge effects ignored for simplicity)
        noise = 0
        count = 0
        
        for i in range(1, gray.shape[0] - 1):
            for j in range(1, gray.shape[1] - 1):
                region = gray[i-1:i+2, j-1:j+2]
                noise += abs(np.sum(region * laplacian))
                count += 1
        
        return noise / count if count > 0 else 0
    
    def _calculate_color_diversity(self, img_array: np.ndarray) -> float:
        """Calculate color diversity metric."""
        if len(img_array.shape) == 3:
            # For color images, count unique colors
            # Reshape and convert to tuples for counting
            pixels = img_array.reshape(-1, img_array.shape[2])
            unique_colors = len(np.unique(pixels, axis=0))
            total_pixels = len(pixels)
            return unique_colors / total_pixels
        else:
            # For grayscale, count unique intensity values
            unique_values = len(np.unique(img_array))
            return unique_values / 256.0
    
    def _calculate_suitability_score(self, lsb_variance: float, 
                                   noise_level: float, color_diversity: float) -> float:
        """Calculate overall suitability score."""
        # Normalize metrics to 0-1 range
        lsb_score = min(lsb_variance * 10, 1.0)  # Higher variance is better
        noise_score = min(noise_level / 50, 1.0)  # Higher noise is better
        diversity_score = color_diversity  # Already normalized
        
        # Weighted average
        weights = [0.3, 0.4, 0.3]  # Noise is most important
        score = (lsb_score * weights[0] + 
                noise_score * weights[1] + 
                diversity_score * weights[2])
        
        return score * 100  # Convert to 0-100 scale
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on suitability score."""
        if score >= 80:
            return "Excellent for steganography"
        elif score >= 60:
            return "Good for steganography"
        elif score >= 40:
            return "Acceptable for steganography"
        elif score >= 20:
            return "Poor for steganography"
        else:
            return "Not recommended for steganography"
    
    def compare_images(self, original_path: str, encoded_path: str) -> Dict:
        """
        Compare original and encoded images to analyze steganography impact.
        
        Args:
            original_path: Path to original image
            encoded_path: Path to encoded image
            
        Returns:
            Comparison analysis
        """
        # Load both images
        original = self.validator.validate_image(original_path)
        encoded = self.validator.validate_image(encoded_path)
        
        # Convert to arrays
        orig_array = np.array(original)
        enc_array = np.array(encoded)
        
        # Ensure same dimensions
        if orig_array.shape != enc_array.shape:
            raise ImageValidationError("Images have different dimensions")
        
        # Calculate differences
        diff = np.abs(orig_array.astype(float) - enc_array.astype(float))
        
        # PSNR calculation
        mse = np.mean(diff ** 2)
        if mse == 0:
            psnr = float('inf')
        else:
            max_pixel = 255.0
            psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
        
        # LSB analysis
        orig_lsb = orig_array & 1
        enc_lsb = enc_array & 1
        lsb_changes = np.sum(orig_lsb != enc_lsb)
        total_pixels = np.prod(orig_array.shape)
        
        return {
            'psnr': float(psnr),
            'mse': float(mse),
            'max_difference': float(np.max(diff)),
            'mean_difference': float(np.mean(diff)),
            'lsb_changes': int(lsb_changes),
            'lsb_change_percentage': round((lsb_changes / total_pixels) * 100, 4),
            'total_pixels': int(total_pixels),
            'quality_impact': self._assess_quality_impact(psnr)
        }
    
    def _assess_quality_impact(self, psnr: float) -> str:
        """Assess quality impact based on PSNR."""
        if psnr == float('inf'):
            return "No detectable changes"
        elif psnr >= 40:
            return "Minimal impact (excellent quality)"
        elif psnr >= 30:
            return "Low impact (good quality)"
        elif psnr >= 20:
            return "Moderate impact (fair quality)"
        else:
            return "High impact (poor quality)"
