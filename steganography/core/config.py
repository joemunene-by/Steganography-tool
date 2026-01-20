"""
Configuration management for steganography tool.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SteganographyConfig:
    """Configuration class for steganography settings."""
    
    # Encoding settings
    default_quality: int = 95
    default_format: str = "PNG"
    use_compression: bool = True
    
    # Batch processing
    max_workers: int = 4
    chunk_size: int = 1024
    
    # Security settings
    default_encryption: bool = False
    password_length: int = 32
    
    # Analysis settings
    enable_analysis: bool = True
    detailed_statistics: bool = False
    
    # Output settings
    verbose: bool = False
    show_progress: bool = True
    output_directory: str = "./output"
    
    # File handling
    backup_originals: bool = False
    overwrite_existing: bool = False
    
    # Performance settings
    memory_limit_mb: int = 512
    cache_images: bool = True


class ConfigManager:
    """
    Manages configuration loading, saving, and validation.
    """
    
    DEFAULT_CONFIG_PATHS = [
        "./steganography.json",
        "./steganography.yaml",
        "~/.steganography/config.json",
        "~/.steganography/config.yaml"
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config = SteganographyConfig()
        
        if config_path:
            self.load_config(config_path)
        else:
            self.load_default_config()
    
    def load_default_config(self):
        """Load configuration from default locations."""
        for path in self.DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    self.load_config(expanded_path)
                    break
                except Exception:
                    continue
    
    def load_config(self, config_path: str):
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        file_ext = os.path.splitext(config_path)[1].lower()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if file_ext in ['.json']:
                    data = json.load(f)
                elif file_ext in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported configuration format: {file_ext}")
            
            # Update configuration with loaded data
            self._update_config(data)
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {str(e)}")
    
    def save_config(self, config_path: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            config_path: Path to save configuration (optional)
        """
        if config_path is None:
            config_path = self.config_path or "./steganography.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        file_ext = os.path.splitext(config_path)[1].lower()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if file_ext in ['.json']:
                    json.dump(asdict(self.config), f, indent=2)
                elif file_ext in ['.yaml', '.yml']:
                    yaml.dump(asdict(self.config), f, default_flow_style=False)
                else:
                    raise ValueError(f"Unsupported configuration format: {file_ext}")
                    
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {str(e)}")
    
    def _update_config(self, data: Dict[str, Any]):
        """Update configuration with data from file."""
        for key, value in data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")
    
    def validate_config(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Validate quality setting
            if not 0 <= self.config.default_quality <= 100:
                raise ValueError("Quality must be between 0 and 100")
            
            # Validate max_workers
            if self.config.max_workers < 1:
                raise ValueError("Max workers must be at least 1")
            
            # Validate password length
            if self.config.password_length < 8:
                raise ValueError("Password length must be at least 8")
            
            # Validate memory limit
            if self.config.memory_limit_mb < 64:
                raise ValueError("Memory limit must be at least 64 MB")
            
            # Validate output directory
            if self.config.output_directory:
                # Try to create directory if it doesn't exist
                os.makedirs(os.path.expanduser(self.config.output_directory), exist_ok=True)
            
            return True
            
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {str(e)}")
    
    def create_sample_config(self, config_path: str):
        """
        Create a sample configuration file.
        
        Args:
            config_path: Path where to create the sample configuration
        """
        sample_config = SteganographyConfig()
        
        # Create temporary config manager to save sample
        temp_manager = ConfigManager()
        temp_manager.config = sample_config
        temp_manager.save_config(config_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self.config)
    
    def from_dict(self, data: Dict[str, Any]):
        """Load configuration from dictionary."""
        self._update_config(data)
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(asdict(self.config), indent=2)


# Global configuration instance
_global_config = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global configuration instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration manager instance
    """
    global _global_config
    
    if _global_config is None or config_path is not None:
        _global_config = ConfigManager(config_path)
    
    return _global_config


def reset_config():
    """Reset global configuration instance."""
    global _global_config
    _global_config = None
