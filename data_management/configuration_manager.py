"""
API để quản lý cấu hình modules một cách dễ dàng.
Cung cấp các hàm tiện ích để thêm, sửa, xóa modules và thông số.
"""

import json
import os
from typing import Dict, List, Optional, Any
from .unified_threshold_manager import unified_threshold_manager

class ConfigManager:
    """Class quản lý cấu hình modules."""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "data/system_config_custom.json"
        self.custom_config = {}
        self.load_custom_config()
    
    def load_custom_config(self):
        """Tải cấu hình tùy chỉnh từ file JSON với error handling cải thiện."""
        if not os.path.exists(self.config_file):
            print(f"Info: Custom config file not found at {self.config_file}. Using defaults.")
            self.custom_config = {}
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.custom_config = json.load(f)
            print(f"Successfully loaded custom config from {self.config_file}")

        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file {self.config_file}: {e}")
            self.custom_config = {}

        except PermissionError:
            print(f"Error: Permission denied reading config file {self.config_file}")
            self.custom_config = {}

        except FileNotFoundError:
            print(f"Info: Config file {self.config_file} not found. Using defaults.")
            self.custom_config = {}

        except Exception as e:
            print(f"Unexpected error loading config file {self.config_file}: {e}")
            self.custom_config = {}
    
    def save_custom_config(self):
        """Lưu cấu hình tùy chỉnh ra file JSON với error handling cải thiện."""
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)

            # Write configuration file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_config, f, indent=2, ensure_ascii=False)

            print(f"Successfully saved custom config to {self.config_file}")
            return True

        except PermissionError:
            print(f"Error: Permission denied writing to {self.config_file}")
            return False

        except OSError as e:
            print(f"Error: OS error writing config file {self.config_file}: {e}")
            return False

        except Exception as e:
            print(f"Unexpected error saving config file {self.config_file}: {e}")
            return False
    
    def add_node(self, node_id: str, description: str = ""):
        """Thêm node mới."""
        if node_id not in self.custom_config:
            self.custom_config[node_id] = {
                'description': description,
                'modules': []
            }
            return True
        return False
    
    def remove_node(self, node_id: str):
        """Xóa node."""
        if node_id in self.custom_config:
            del self.custom_config[node_id]
            return True
        return False
    
    def add_module_to_node(self, node_id: str, module_config: Dict[str, Any]):
        """Thêm module vào node."""
        if node_id not in self.custom_config:
            self.add_node(node_id)
        
        # Validate module config
        required_fields = ['name', 'default_voltage', 'default_current', 'default_power']
        for field in required_fields:
            if field not in module_config:
                raise ValueError(f"Thiếu field bắt buộc: {field}")
        
        self.custom_config[node_id]['modules'].append(module_config)
        return True
    
    def remove_module_from_node(self, node_id: str, module_name: str):
        """Xóa module khỏi node."""
        if node_id in self.custom_config:
            modules = self.custom_config[node_id]['modules']
            for i, module in enumerate(modules):
                if module.get('name') == module_name:
                    del modules[i]
                    return True
        return False
    
    def update_module_parameter(self, node_id: str, module_name: str, parameter: str, value: Any):
        """Cập nhật thông số của module."""
        if node_id in self.custom_config:
            modules = self.custom_config[node_id]['modules']
            for module in modules:
                if module.get('name') == module_name:
                    module[parameter] = value
                    return True
        return False
    
    def get_effective_config(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lấy cấu hình hiệu lực (base + custom)."""
        effective_config = {}
        
        # Bắt đầu với cấu hình base từ unified system
        node_configs = unified_threshold_manager.config_data.get('node_configurations', {})
        for node_id, module_names in node_configs.items():
            effective_config[node_id] = module_names.copy()
        
        # Áp dụng custom config
        for node_id, node_data in self.custom_config.items():
            if node_id not in effective_config:
                effective_config[node_id] = []
            
            for module_data in node_data.get('modules', []):
                module_config = ModuleConfig(
                    name=module_data['name'],
                    default_voltage=module_data.get('default_voltage', 12.0),
                    default_current=module_data.get('default_current', 2.0),
                    default_power=module_data.get('default_power', 24.0),
                    default_resistance=module_data.get('default_resistance', 50.0),
                    default_temperature=module_data.get('default_temperature', 35.0),
                    min_voltage=module_data.get('min_voltage', 8.0),
                    max_voltage=module_data.get('max_voltage', 15.0),
                    max_current=module_data.get('max_current', 8.0),
                    max_temperature=module_data.get('max_temperature', 70.0),
                    # Add the new threshold fields
                    min_current=module_data.get('min_current', 0.5),
                    min_power=module_data.get('min_power', 1.0),
                    max_power=module_data.get('max_power', 50.0),
                    min_resistance=module_data.get('min_resistance', 10.0),
                    max_resistance=module_data.get('max_resistance', 100.0),
                    min_temperature=module_data.get('min_temperature', 0.0),
                    description=module_data.get('description', '')
                )
                effective_config[node_id].append(module_config)
        
        return effective_config

# Global instance
config_manager = ConfigManager()

# API Functions
def add_custom_node(node_id: str, description: str = ""):
    """Thêm node tùy chỉnh."""
    result = config_manager.add_node(node_id, description)
    if result:
        config_manager.save_custom_config()
    return result

def add_custom_module(node_id: str, name: str, voltage: float = 12.0, current: float = 2.0,
                     power: float = None, resistance: float = 50.0, temperature: float = 35.0,
                     min_voltage: float = 8.0, max_voltage: float = 15.0,
                     min_current: float = 0.5, max_current: float = 8.0,
                     min_power: float = 1.0, max_power: float = 50.0,
                     min_resistance: float = 10.0, max_resistance: float = 100.0,
                     min_temperature: float = 0.0, max_temperature: float = 70.0,
                     description: str = ""):
    """Thêm module tùy chỉnh vào node."""
    if power is None:
        power = voltage * current

    module_config = {
        'name': name,
        'default_voltage': voltage,
        'default_current': current,
        'default_power': power,
        'default_resistance': resistance,
        'default_temperature': temperature,
        'min_voltage': min_voltage,
        'max_voltage': max_voltage,
        'min_current': min_current,
        'max_current': max_current,
        'min_power': min_power,
        'max_power': max_power,
        'min_resistance': min_resistance,
        'max_resistance': max_resistance,
        'min_temperature': min_temperature,
        'max_temperature': max_temperature,
        'description': description
    }

    result = config_manager.add_module_to_node(node_id, module_config)
    if result:
        config_manager.save_custom_config()
    return result

def remove_custom_module(node_id: str, module_name: str):
    """Xóa module tùy chỉnh."""
    result = config_manager.remove_module_from_node(node_id, module_name)
    if result:
        config_manager.save_custom_config()
    return result

def update_module_parameter(node_id: str, module_name: str, parameter: str, value: Any):
    """Cập nhật thông số module."""
    result = config_manager.update_module_parameter(node_id, module_name, parameter, value)
    if result:
        config_manager.save_custom_config()
    return result

def get_node_config_summary(node_id: str) -> Dict[str, Any]:
    """Lấy tóm tắt cấu hình của node."""
    effective_config = config_manager.get_effective_config()
    
    if node_id not in effective_config:
        return {'error': 'Node không tồn tại'}
    
    modules = effective_config[node_id]
    total_power = sum(m.default_power for m in modules)
    voltage_range = (min(m.default_voltage for m in modules), max(m.default_voltage for m in modules)) if modules else (0, 0)
    
    return {
        'node_id': node_id,
        'module_count': len(modules),
        'total_power': total_power,
        'voltage_range': voltage_range,
        'modules': [
            {
                'name': m.name,
                'voltage': m.default_voltage,
                'current': m.default_current,
                'power': m.default_power,
                'description': m.description
            } for m in modules
        ]
    }

def backup_config(backup_file: str):
    """Sao lưu cấu hình hiện tại."""
    try:
        effective_config = config_manager.get_effective_config()
        
        # Chuyển đổi ModuleConfig objects thành dict
        serializable_config = {}
        for node_id, modules in effective_config.items():
            serializable_config[node_id] = []
            for module in modules:
                serializable_config[node_id].append({
                    'name': module.name,
                    'default_voltage': module.default_voltage,
                    'default_current': module.default_current,
                    'default_power': module.default_power,
                    'default_resistance': module.default_resistance,
                    'default_temperature': module.default_temperature,
                    'min_voltage': module.min_voltage,
                    'max_voltage': module.max_voltage,
                    'max_current': module.max_current,
                    'max_temperature': module.max_temperature,
                    'description': module.description
                })
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Lỗi backup: {e}")
        return False

def restore_config(backup_file: str):
    """Khôi phục cấu hình từ backup."""
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Chuyển đổi thành custom config format
        config_manager.custom_config = {}
        for node_id, modules in backup_data.items():
            node_configs = unified_threshold_manager.config_data.get('node_configurations', {})
            if node_id not in node_configs:  # Chỉ lưu nodes tùy chỉnh
                config_manager.custom_config[node_id] = {
                    'description': f'Node được khôi phục từ backup',
                    'modules': modules
                }
        
        config_manager.save_custom_config()
        return True
    except Exception as e:
        print(f"Lỗi khôi phục: {e}")
        return False

def validate_all_configs() -> Dict[str, Any]:
    """Kiểm tra tính hợp lệ của tất cả cấu hình."""
    effective_config = config_manager.get_effective_config()
    results = {}
    
    for node_id, modules in effective_config.items():
        issues = []
        
        for module in modules:
            # Kiểm tra logic thông số
            if module.default_voltage < module.min_voltage or module.default_voltage > module.max_voltage:
                issues.append(f'{module.name}: Điện áp mặc định ngoài phạm vi')
            
            if module.default_current > module.max_current:
                issues.append(f'{module.name}: Dòng điện mặc định vượt giới hạn')
            
            # Kiểm tra công suất có hợp lý không
            calculated_power = module.default_voltage * module.default_current
            power_error = abs(module.default_power - calculated_power) / calculated_power * 100
            if power_error > 15:  # Cho phép sai số 15%
                issues.append(f'{module.name}: Công suất không khớp với V*I (sai số {power_error:.1f}%)')
        
        results[node_id] = {
            'valid': len(issues) == 0,
            'module_count': len(modules),
            'issues': issues
        }
    
    return results

# Utility functions
def quick_add_power_module(node_id: str, name: str, voltage: float, current: float):
    """Nhanh chóng thêm module nguồn với thông số cơ bản."""
    return add_custom_module(
        node_id=node_id,
        name=name,
        voltage=voltage,
        current=current,
        power=voltage * current,
        description=f"Module nguồn {voltage}V/{current}A"
    )

def quick_add_control_module(node_id: str, name: str, description: str = ""):
    """Nhanh chóng thêm module điều khiển với thông số mặc định."""
    return add_custom_module(
        node_id=node_id,
        name=name,
        voltage=12.0,
        current=1.0,
        power=12.0,
        description=description or f"Module điều khiển {name}"
    )

def quick_add_sensor_module(node_id: str, name: str, description: str = ""):
    """Nhanh chóng thêm module cảm biến với thông số thấp."""
    return add_custom_module(
        node_id=node_id,
        name=name,
        voltage=12.0,
        current=0.5,
        power=6.0,
        description=description or f"Module cảm biến {name}"
    )

def change_config_module(node_id: str, module_name: str, parameter: str, value: Any):
    """Thay đổi thông số module nhanh chóng."""
    return update_module_parameter(node_id, module_name, parameter, value)


def get_node_id_from_index(node_index: int) -> Optional[str]:
    """
    Lấy node_id từ node index (dùng cho CAN bus mapping).
    
    Args:
        node_index: Index của node (0-255)
    
    Returns:
        node_id (str) hoặc None nếu không tìm thấy
    """
    try:
        # Load node index mapping from unified config
        node_index_mapping = unified_threshold_manager.config_data.get('node_index_mapping', {})
        
        # Search for node with matching index
        for node_id, node_info in node_index_mapping.items():
            if node_info.get('index') == node_index:
                return node_id
        
        return None
        
    except Exception as e:
        print(f"Error getting node_id from index {node_index}: {e}")
        return None


def get_node_index_from_id(node_id: str) -> Optional[int]:
    """
    Lấy node index từ node_id (dùng cho CAN bus mapping).
    
    Args:
        node_id: ID của node
    
    Returns:
        node_index (int) hoặc None nếu không tìm thấy
    """
    try:
        # Load node index mapping from unified config
        node_index_mapping = unified_threshold_manager.config_data.get('node_index_mapping', {})
        
        if node_id in node_index_mapping:
            return node_index_mapping[node_id].get('index')
        
        return None
        
    except Exception as e:
        print(f"Error getting index from node_id '{node_id}': {e}")
        return None


def get_node_can_id(node_id: str) -> Optional[str]:
    """
    Lấy CAN ID của node từ node_id.
    
    Args:
        node_id: ID của node
    
    Returns:
        CAN ID (str, ví dụ: "0x300") hoặc None nếu không tìm thấy
    """
    try:
        # Load node index mapping from unified config
        node_index_mapping = unified_threshold_manager.config_data.get('node_index_mapping', {})
        
        if node_id in node_index_mapping:
            return node_index_mapping[node_id].get('can_id')
        
        return None
        
    except Exception as e:
        print(f"Error getting CAN ID from node_id '{node_id}': {e}")
        return None


def get_all_node_mappings() -> Dict[str, Dict[str, Any]]:
    """
    Lấy tất cả node mappings (index, CAN ID, description).
    
    Returns:
        Dictionary với format: {node_id: {index, can_id, description}}
    """
    try:
        return unified_threshold_manager.config_data.get('node_index_mapping', {})
    except Exception as e:
        print(f"Error getting node mappings: {e}")
        return {}