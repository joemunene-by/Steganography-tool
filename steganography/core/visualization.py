"""
Visualization utilities for steganography analysis and bit-level statistics.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Optional, Tuple
from PIL import Image
import io
import base64

from .image_utils import ImageValidator
from .exceptions import ImageValidationError


class SteganographyVisualizer:
    """
    Provides visualization capabilities for steganography analysis.
    """
    
    def __init__(self):
        self.validator = ImageValidator()
        plt.style.use('default')
    
    def visualize_lsb_distribution(self, image_path: str, save_path: Optional[str] = None) -> str:
        """
        Create a visualization of LSB distribution in the image.
        
        Args:
            image_path: Path to the image
            save_path: Optional path to save the plot
            
        Returns:
            Base64 encoded image of the plot
        """
        # Load and validate image
        image = self.validator.validate_image(image_path)
        img_array = np.array(image)
        
        # Extract LSBs
        lsb_array = img_array & 1
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('LSB Distribution Analysis', fontsize=16)
        
        # Overall LSB distribution
        axes[0, 0].hist(lsb_array.flatten(), bins=[-0.5, 0.5, 1.5], rwidth=0.8, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Overall LSB Distribution')
        axes[0, 0].set_xlabel('LSB Value')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_xticks([0, 1])
        
        # LSB heatmap
        if len(img_array.shape) == 3:
            # Color image - show average LSB
            lsb_avg = np.mean(lsb_array, axis=2)
        else:
            lsb_avg = lsb_array
        
        im = axes[0, 1].imshow(lsb_avg, cmap='gray', vmin=0, vmax=1)
        axes[0, 1].set_title('LSB Heatmap (Average)')
        axes[0, 1].axis('off')
        plt.colorbar(im, ax=axes[0, 1], fraction=0.046, pad=0.04)
        
        # Channel-wise LSB distribution
        if len(img_array.shape) == 3:
            channel_names = ['Red', 'Green', 'Blue']
            if img_array.shape[2] == 4:
                channel_names = ['Red', 'Green', 'Blue', 'Alpha']
            
            for i, channel_name in enumerate(channel_names[:3]):  # Show first 3 channels
                if i < img_array.shape[2]:
                    channel_lsb = lsb_array[:, :, i]
                    zeros = np.sum(channel_lsb == 0)
                    ones = np.sum(channel_lsb == 1)
                    total = zeros + ones
                    
                    axes[1, i].bar(['0', '1'], [zeros, ones], color=['lightcoral', 'lightblue'], edgecolor='black')
                    axes[1, i].set_title(f'{channel_name} Channel LSB')
                    axes[1, i].set_ylabel('Count')
                    axes[1, i].set_ylim(0, max(zeros, ones) * 1.1)
                    
                    # Add percentage labels
                    axes[1, i].text(0, zeros/2, f'{zeros/total*100:.1f}%', ha='center', va='center')
                    axes[1, i].text(1, ones/2, f'{ones/total*100:.1f}%', ha='center', va='center')
        else:
            # Grayscale image
            zeros = np.sum(lsb_array == 0)
            ones = np.sum(lsb_array == 1)
            total = zeros + ones
            
            axes[1, 0].bar(['0', '1'], [zeros, ones], color=['lightcoral', 'lightblue'], edgecolor='black')
            axes[1, 0].set_title('Grayscale LSB Distribution')
            axes[1, 0].set_ylabel('Count')
            axes[1, 0].set_ylim(0, max(zeros, ones) * 1.1)
            
            # Hide unused subplots
            axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        # Save or return as base64
        return self._save_or_encode_plot(fig, save_path)
    
    def visualize_bit_plane(self, image_path: str, bit_position: int = 0, save_path: Optional[str] = None) -> str:
        """
        Visualize a specific bit plane of the image.
        
        Args:
            image_path: Path to the image
            bit_position: Bit position (0=LSB, 7=MSB)
            save_path: Optional path to save the plot
            
        Returns:
            Base64 encoded image of the plot
        """
        # Load and validate image
        image = self.validator.validate_image(image_path)
        img_array = np.array(image)
        
        # Extract specific bit
        bit_plane = (img_array >> bit_position) & 1
        
        # Create figure
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f'Bit Plane {bit_position} Analysis', fontsize=16)
        
        # Original image
        axes[0].imshow(image)
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Bit plane visualization
        if len(img_array.shape) == 3:
            # Color image - show average bit plane
            bit_avg = np.mean(bit_plane, axis=2)
        else:
            bit_avg = bit_plane
        
        axes[1].imshow(bit_avg, cmap='gray', vmin=0, vmax=1)
        axes[1].set_title(f'Bit Plane {bit_position}')
        axes[1].axis('off')
        
        # Bit plane histogram
        axes[2].hist(bit_avg.flatten(), bins=[-0.5, 0.5, 1.5], rwidth=0.8, color='lightgreen', edgecolor='black')
        axes[2].set_title(f'Bit Plane {bit_position} Distribution')
        axes[2].set_xlabel('Bit Value')
        axes[2].set_ylabel('Frequency')
        axes[2].set_xticks([0, 1])
        
        plt.tight_layout()
        
        return self._save_or_encode_plot(fig, save_path)
    
    def visualize_entropy_analysis(self, image_path: str, window_size: int = 8, save_path: Optional[str] = None) -> str:
        """
        Create entropy map visualization.
        
        Args:
            image_path: Path to the image
            window_size: Size of sliding window for entropy calculation
            save_path: Optional path to save the plot
            
        Returns:
            Base64 encoded image of the plot
        """
        # Load and validate image
        image = self.validator.validate_image(image_path)
        img_array = np.array(image)
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array
        
        # Calculate local entropy
        entropy_map = self._calculate_local_entropy(gray, window_size)
        
        # Create figure
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Local Entropy Analysis', fontsize=16)
        
        # Original image
        axes[0].imshow(image)
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Entropy map
        im = axes[1].imshow(entropy_map, cmap='hot', vmin=0, vmax=8)
        axes[1].set_title(f'Local Entropy (Window: {window_size}x{window_size})')
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
        
        # Entropy histogram
        axes[2].hist(entropy_map.flatten(), bins=50, color='orange', edgecolor='black', alpha=0.7)
        axes[2].set_title('Entropy Distribution')
        axes[2].set_xlabel('Entropy Value')
        axes[2].set_ylabel('Frequency')
        axes[2].axvline(np.mean(entropy_map), color='red', linestyle='--', label=f'Mean: {np.mean(entropy_map):.2f}')
        axes[2].legend()
        
        plt.tight_layout()
        
        return self._save_or_encode_plot(fig, save_path)
    
    def visualize_steganography_impact(self, original_path: str, encoded_path: str, save_path: Optional[str] = None) -> str:
        """
        Visualize the impact of steganography on the image.
        
        Args:
            original_path: Path to original image
            encoded_path: Path to encoded image
            save_path: Optional path to save the plot
            
        Returns:
            Base64 encoded image of the plot
        """
        # Load and validate images
        original = self.validator.validate_image(original_path)
        encoded = self.validator.validate_image(encoded_path)
        
        orig_array = np.array(original)
        enc_array = np.array(encoded)
        
        # Ensure same dimensions
        if orig_array.shape != enc_array.shape:
            raise ImageValidationError("Images have different dimensions")
        
        # Calculate difference
        diff = np.abs(orig_array.astype(float) - enc_array.astype(float))
        
        # Create figure
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Steganography Impact Analysis', fontsize=16)
        
        # Original image
        axes[0, 0].imshow(original)
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')
        
        # Encoded image
        axes[0, 1].imshow(encoded)
        axes[0, 1].set_title('Encoded Image')
        axes[0, 1].axis('off')
        
        # Difference map
        if len(diff.shape) == 3:
            diff_avg = np.mean(diff, axis=2)
        else:
            diff_avg = diff
        
        im = axes[0, 2].imshow(diff_avg, cmap='hot', vmin=0, vmax=np.max(diff_avg))
        axes[0, 2].set_title('Difference Map')
        axes[0, 2].axis('off')
        plt.colorbar(im, ax=axes[0, 2], fraction=0.046, pad=0.04)
        
        # LSB changes
        orig_lsb = orig_array & 1
        enc_lsb = enc_array & 1
        lsb_changes = (orig_lsb != enc_lsb).astype(float)
        
        if len(lsb_changes.shape) == 3:
            lsb_changes_avg = np.mean(lsb_changes, axis=2)
        else:
            lsb_changes_avg = lsb_changes
        
        axes[1, 0].imshow(lsb_changes_avg, cmap='Reds', vmin=0, vmax=1)
        axes[1, 0].set_title('LSB Changes')
        axes[1, 0].axis('off')
        
        # Difference histogram
        axes[1, 1].hist(diff_avg.flatten(), bins=50, color='purple', edgecolor='black', alpha=0.7)
        axes[1, 1].set_title('Pixel Difference Distribution')
        axes[1, 1].set_xlabel('Difference Value')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].axvline(np.mean(diff_avg), color='red', linestyle='--', label=f'Mean: {np.mean(diff_avg):.3f}')
        axes[1, 1].legend()
        
        # Statistics
        psnr = self._calculate_psnr(orig_array, enc_array)
        lsb_change_count = np.sum(lsb_changes)
        total_pixels = np.prod(orig_array.shape)
        
        stats_text = f"""Statistics:
PSNR: {psnr:.2f} dB
Max Difference: {np.max(diff_avg):.1f}
Mean Difference: {np.mean(diff_avg):.3f}
LSB Changes: {lsb_change_count:,}
LSB Change %: {(lsb_change_count/total_pixels)*100:.4f}%
Total Pixels: {total_pixels:,}"""
        
        axes[1, 2].text(0.1, 0.5, stats_text, transform=axes[1, 2].transAxes, 
                        fontsize=10, verticalalignment='center', 
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        axes[1, 2].set_title('Impact Statistics')
        axes[1, 2].axis('off')
        
        plt.tight_layout()
        
        return self._save_or_encode_plot(fig, save_path)
    
    def _calculate_local_entropy(self, image: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate local entropy using sliding window."""
        height, width = image.shape
        entropy_map = np.zeros((height, width))
        
        # Pad image for edge handling
        pad = window_size // 2
        padded = np.pad(image, pad, mode='reflect')
        
        for i in range(height):
            for j in range(width):
                # Extract window
                window = padded[i:i+window_size, j:j+window_size]
                
                # Calculate histogram
                hist, _ = np.histogram(window, bins=256, range=(0, 256))
                
                # Calculate entropy
                hist_normalized = hist / np.sum(hist)
                hist_normalized = hist_normalized[hist_normalized > 0]
                entropy = -np.sum(hist_normalized * np.log2(hist_normalized))
                
                entropy_map[i, j] = entropy
        
        return entropy_map
    
    def _calculate_psnr(self, original: np.ndarray, encoded: np.ndarray) -> float:
        """Calculate Peak Signal-to-Noise Ratio."""
        mse = np.mean((original.astype(float) - encoded.astype(float)) ** 2)
        if mse == 0:
            return float('inf')
        
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
    
    def _save_or_encode_plot(self, fig, save_path: Optional[str] = None) -> str:
        """Save plot to file or encode as base64."""
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            return save_path
        else:
            # Encode as base64
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            return f"data:image/png;base64,{image_base64}"
    
    def generate_comprehensive_report(self, image_path: str, output_dir: str = "./steganography_report") -> Dict[str, str]:
        """
        Generate a comprehensive visualization report.
        
        Args:
            image_path: Path to the image
            output_dir: Directory to save report files
            
        Returns:
            Dictionary with paths to generated visualizations
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        report = {}
        
        # LSB distribution
        lsb_path = os.path.join(output_dir, "lsb_distribution.png")
        report['lsb_distribution'] = self.visualize_lsb_distribution(image_path, lsb_path)
        
        # Bit planes (LSB and MSB)
        for bit in [0, 7]:  # LSB and MSB
            bit_path = os.path.join(output_dir, f"bit_plane_{bit}.png")
            report[f'bit_plane_{bit}'] = self.visualize_bit_plane(image_path, bit, bit_path)
        
        # Entropy analysis
        entropy_path = os.path.join(output_dir, "entropy_analysis.png")
        report['entropy_analysis'] = self.visualize_entropy_analysis(image_path, save_path=entropy_path)
        
        return report
