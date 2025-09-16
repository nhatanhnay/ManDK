# -*- coding: utf-8 -*-
"""
Common utilities module - Centralized functions used across the codebase.
Eliminates code duplication and provides consistent behavior.
"""

import os
import sys
import yaml
from typing import Dict, Any, Optional


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource file.

    Args:
        relative_path: Relative path to the resource

    Returns:
        Absolute path to the resource
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)

    # Running as normal Python script
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_button_colors() -> Dict[str, Any]:
    """
    Load button colors from config.yaml file.

    Returns:
        Dictionary containing button color configuration
    """
    config_path = resource_path('config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('ButtonColors', {})
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
        return {}
    except Exception as e:
        print(f"Error loading button colors: {e}")
        return {}


def load_config(config_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from config.yaml file.

    Args:
        config_key: Specific configuration section to load (optional)

    Returns:
        Configuration dictionary or specific section
    """
    config_path = resource_path('config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config_key:
            return config.get(config_key, {})
        return config

    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config: {e}")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def safe_file_operation(operation_func, *args, **kwargs):
    """
    Safely execute file operations with proper error handling.

    Args:
        operation_func: Function to execute
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (success: bool, result: Any, error: str)
    """
    try:
        result = operation_func(*args, **kwargs)
        return True, result, ""
    except FileNotFoundError as e:
        return False, None, f"File not found: {e}"
    except PermissionError as e:
        return False, None, f"Permission denied: {e}"
    except Exception as e:
        return False, None, f"Operation failed: {e}"


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path exists and is accessible.

    Args:
        file_path: Path to validate

    Returns:
        True if path is valid and accessible
    """
    try:
        return os.path.exists(file_path) and os.access(file_path, os.R_OK)
    except Exception:
        return False


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        return False