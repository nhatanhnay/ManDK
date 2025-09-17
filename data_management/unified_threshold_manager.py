"""
Unified threshold and configuration manager.
Manages both default and custom thresholds in a single JSON configuration file.
"""

import json
import os
from typing import Dict, Any, Optional

class UnifiedThresholdManager:
    """Manages module configurations and thresholds from unified JSON file."""

    def __init__(self):
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            'unified_module_config.json'
        )
        self.config_data = {}
        self.load_config()

    def load_config(self) -> bool:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                print(f"Loaded unified config from: {self.config_file}")
                return True
            else:
                print(f"Config file not found: {self.config_file}")
                return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save_config(self) -> bool:
        """Save configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            print(f"Saved unified config to: {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_effective_threshold(self, module_name: str, parameter_name: str) -> Dict[str, Any]:
        """
        Get the effective threshold for a parameter (custom overrides default).

        Args:
            module_name: Name of the module
            parameter_name: Name of the parameter

        Returns:
            Dictionary with min_normal, max_normal, unit
        """
        module_configs = self.config_data.get('module_configurations', {})

        if module_name not in module_configs:
            # Return fallback threshold
            return {"min_normal": 0.0, "max_normal": 100.0, "unit": ""}

        module_config = module_configs[module_name]

        # Check for custom threshold first
        custom_thresholds = module_config.get('custom_thresholds', {})
        if parameter_name in custom_thresholds:
            return custom_thresholds[parameter_name]

        # Fall back to default threshold
        default_thresholds = module_config.get('default_thresholds', {})
        if parameter_name in default_thresholds:
            return default_thresholds[parameter_name]

        # Ultimate fallback
        return {"min_normal": 0.0, "max_normal": 100.0, "unit": ""}

    def is_parameter_normal(self, module_name: str, parameter_name: str, value: float) -> bool:
        """
        Check if parameter value is within normal range.

        Args:
            module_name: Name of the module
            parameter_name: Name of the parameter
            value: Value to check

        Returns:
            True if normal, False if outside range
        """
        threshold = self.get_effective_threshold(module_name, parameter_name)
        return threshold["min_normal"] <= value <= threshold["max_normal"]

    def update_custom_threshold(self, module_name: str, parameter_name: str,
                              min_normal: Optional[float] = None,
                              max_normal: Optional[float] = None) -> bool:
        """
        Update custom threshold for a module parameter.

        Args:
            module_name: Name of the module
            parameter_name: Name of the parameter
            min_normal: New minimum threshold (optional)
            max_normal: New maximum threshold (optional)

        Returns:
            True if successful, False otherwise
        """
        module_configs = self.config_data.setdefault('module_configurations', {})

        if module_name not in module_configs:
            print(f"Module {module_name} not found in configuration")
            return False

        module_config = module_configs[module_name]
        custom_thresholds = module_config.setdefault('custom_thresholds', {})

        # Get current effective threshold as base
        current_threshold = self.get_effective_threshold(module_name, parameter_name)

        # Create or update custom threshold
        if parameter_name not in custom_thresholds:
            custom_thresholds[parameter_name] = current_threshold.copy()

        # Update values
        if min_normal is not None:
            custom_thresholds[parameter_name]['min_normal'] = min_normal
        if max_normal is not None:
            custom_thresholds[parameter_name]['max_normal'] = max_normal

        # Save configuration
        success = self.save_config()

        if success:
            # Refresh module statuses
            self._refresh_all_module_statuses()

        return success

    def reset_to_default(self, module_name: str, parameter_name: str) -> bool:
        """
        Reset a parameter threshold to default by removing custom override.

        Args:
            module_name: Name of the module
            parameter_name: Name of the parameter

        Returns:
            True if successful, False otherwise
        """
        module_configs = self.config_data.get('module_configurations', {})

        if module_name not in module_configs:
            return False

        custom_thresholds = module_configs[module_name].get('custom_thresholds', {})

        if parameter_name in custom_thresholds:
            del custom_thresholds[parameter_name]
            success = self.save_config()

            if success:
                self._refresh_all_module_statuses()

            return success

        return True  # Already at default

    def get_module_default_parameters(self, module_name: str) -> Dict[str, float]:
        """
        Get default parameter values for a module.

        Args:
            module_name: Name of the module

        Returns:
            Dictionary with default parameter values
        """
        module_configs = self.config_data.get('module_configurations', {})

        if module_name not in module_configs:
            return {
                'voltage': 12.0,
                'current': 2.0,
                'power': 24.0,
                'resistance': 50.0,
                'temperature': 35.0
            }

        return module_configs[module_name].get('default_parameters', {
            'voltage': 12.0,
            'current': 2.0,
            'power': 24.0,
            'resistance': 50.0,
            'temperature': 35.0
        })

    def get_node_module_list(self, node_id: str) -> list:
        """
        Get list of module names for a specific node.

        Args:
            node_id: ID of the node

        Returns:
            List of module names
        """
        node_configs = self.config_data.get('node_configurations', {})
        return node_configs.get(node_id, [])

    def get_module_description(self, module_name: str) -> str:
        """
        Get description for a module.

        Args:
            module_name: Name of the module

        Returns:
            Module description
        """
        module_configs = self.config_data.get('module_configurations', {})

        if module_name not in module_configs:
            return "Module chung"

        return module_configs[module_name].get('description', 'Module chung')

    def _refresh_all_module_statuses(self):
        """Refresh status of all modules after threshold change."""
        try:
            from .module_data_manager import module_manager
            from .node_data_manager import system_data_manager

            for node_modules in module_manager.modules.values():
                for module in node_modules.values():
                    # Force recheck status with new thresholds
                    module._check_status()

            # Also refresh node error statuses
            system_data_manager.refresh_all_node_error_statuses()

        except ImportError:
            pass  # module_manager not available

# Global instance
unified_threshold_manager = UnifiedThresholdManager()

# Backward compatibility functions
def get_threshold_for_parameter(module_name: str, parameter_name: str) -> Dict[str, Any]:
    """Backward compatibility function."""
    return unified_threshold_manager.get_effective_threshold(module_name, parameter_name)

def is_parameter_normal(module_name: str, parameter_name: str, value: float) -> bool:
    """Backward compatibility function."""
    return unified_threshold_manager.is_parameter_normal(module_name, parameter_name, value)

def update_module_threshold(node_id: str, module_name: str, parameter: str,
                          min_normal: Optional[float] = None,
                          max_normal: Optional[float] = None) -> Dict[str, Any]:
    """Backward compatibility function."""
    success = unified_threshold_manager.update_custom_threshold(
        module_name, parameter, min_normal, max_normal
    )

    if success:
        return unified_threshold_manager.get_effective_threshold(module_name, parameter)
    else:
        raise ValueError(f"Failed to update threshold for {module_name}/{parameter}")

def refresh_all_module_statuses():
    """Backward compatibility function."""
    unified_threshold_manager._refresh_all_module_statuses()