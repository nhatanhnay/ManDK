"""
Module quản lý dữ liệu chi tiết của các module trong từng node.
Mỗi node có thể có nhiều module, mỗi module có các thông số: điện áp, dòng điện, công suất, điện trở.
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class ModuleParameters:
    """Class lưu trữ các thông số của một module."""
    voltage: float = 0.0        # Điện áp (V)
    current: float = 0.0        # Dòng điện (A)
    power: float = 0.0          # Công suất (W)
    resistance: float = 0.0     # Điện trở (Ω)
    temperature: float = 0.0    # Nhiệt độ (°C) - thêm thông số này
    
    def to_dict(self) -> Dict[str, float]:
        """Chuyển đổi thành dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'ModuleParameters':
        """Tạo từ dictionary."""
        return cls(**data)

class ModuleData:
    """Class lưu trữ dữ liệu của một module."""
    
    def __init__(self, module_id: str, name: str, node_id: str):
        self.module_id = module_id
        self.name = name
        self.node_id = node_id
        self.parameters = ModuleParameters()
        self.parameter_history: List[Dict[str, Any]] = []
        self.status = "normal"  # normal, warning, error
        self.error_messages: List[str] = []
        self.last_update = time.time()
        
        # Ngưỡng validation (sẽ được set từ config)
        self.min_voltage = 8.0
        self.max_voltage = 15.0
        self.max_current = 8.0
        self.max_temperature = 70.0
        self.description = ""
        
    def update_parameters(self, **kwargs):
        """Cập nhật các thông số của module."""
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
        
        # Lưu vào lịch sử
        self.parameter_history.append({
            'timestamp': datetime.now().isoformat(),
            'time_seconds': time.time(),
            'parameters': self.parameters.to_dict()
        })
        
        # Giữ lại 1000 records gần nhất
        if len(self.parameter_history) > 1000:
            self.parameter_history.pop(0)
            
        self.last_update = time.time()
        self._check_status()
        
    def _check_status(self):
        """Kiểm tra trạng thái module dựa trên thông số và ngưỡng từ config."""
        self.clear_errors()  # Xóa lỗi cũ trước
        
        # Kiểm tra điện áp
        if self.parameters.voltage < self.min_voltage:
            self.status = "error"
            self.add_error(f"Điện áp thấp ({self.parameters.voltage:.1f}V < {self.min_voltage}V)")
        elif self.parameters.voltage > self.max_voltage:
            self.status = "error" 
            self.add_error(f"Điện áp cao ({self.parameters.voltage:.1f}V > {self.max_voltage}V)")
        
        # Kiểm tra dòng điện
        elif self.parameters.current > self.max_current:
            if self.parameters.current > self.max_current * 1.2:  # Vượt 20% -> error
                self.status = "error"
                self.add_error(f"Dòng điện quá cao ({self.parameters.current:.1f}A > {self.max_current}A)")
            else:  # Vượt nhưng <20% -> warning
                self.status = "warning"
                self.add_error(f"Dòng điện cao ({self.parameters.current:.1f}A)")
        
        # Kiểm tra nhiệt độ
        elif self.parameters.temperature > self.max_temperature:
            if self.parameters.temperature > self.max_temperature * 1.1:  # Vượt 10% -> error
                self.status = "error"
                self.add_error(f"Quá nhiệt ({self.parameters.temperature:.1f}°C > {self.max_temperature}°C)")
            else:  # Vượt nhưng <10% -> warning
                self.status = "warning"
                self.add_error(f"Nhiệt độ cao ({self.parameters.temperature:.1f}°C)")
        
        # Nếu không có lỗi gì
        else:
            self.status = "normal"
    
    def add_error(self, message: str):
        """Thêm thông báo lỗi."""
        if message not in self.error_messages:
            self.error_messages.append(message)
            
    def clear_errors(self):
        """Xóa tất cả lỗi."""
        self.error_messages.clear()
        
    def get_latest_parameters(self) -> ModuleParameters:
        """Lấy thông số mới nhất."""
        return self.parameters
        
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary để lưu/tải."""
        return {
            'module_id': self.module_id,
            'name': self.name,
            'node_id': self.node_id,
            'parameters': self.parameters.to_dict(),
            'status': self.status,
            'error_messages': self.error_messages,
            'last_update': self.last_update
        }

class ModuleManager:
    """Class quản lý tất cả modules trong hệ thống."""
    
    def __init__(self):
        self.modules: Dict[str, Dict[str, ModuleData]] = {}  # {node_id: {module_id: ModuleData}}
        self._initialize_default_modules()
        
    def _initialize_default_modules(self):
        """Khởi tạo các module từ cấu hình system_config.py."""
        from .system_configuration import NODE_MODULE_CONFIG
        
        for node_id, module_configs in NODE_MODULE_CONFIG.items():
            self.modules[node_id] = {}
            
            for i, module_config in enumerate(module_configs, 1):
                module_id = f"{node_id}_module_{i:02d}"
                module = ModuleData(module_id, module_config.name, node_id)
                
                # Khởi tạo thông số từ cấu hình
                module.update_parameters(
                    voltage=module_config.default_voltage,
                    current=module_config.default_current,
                    power=module_config.default_power,
                    resistance=module_config.default_resistance,
                    temperature=module_config.default_temperature
                )
                
                # Lưu thông tin ngưỡng để validation
                module.min_voltage = module_config.min_voltage
                module.max_voltage = module_config.max_voltage
                module.max_current = module_config.max_current
                module.max_temperature = module_config.max_temperature
                module.description = module_config.description
                
                self.modules[node_id][module_id] = module
                
    def get_node_modules(self, node_id: str) -> Dict[str, ModuleData]:
        """Lấy tất cả modules của một node."""
        return self.modules.get(node_id, {})
        
    def get_module(self, node_id: str, module_id: str) -> Optional[ModuleData]:
        """Lấy một module cụ thể."""
        return self.modules.get(node_id, {}).get(module_id)
        
    def update_module_parameters(self, node_id: str, module_id: str, **parameters):
        """Cập nhật thông số module từ CAN/API."""
        if node_id in self.modules and module_id in self.modules[node_id]:
            self.modules[node_id][module_id].update_parameters(**parameters)
            return True
        return False
        
    def update_all_modules_from_can_data(self, can_data: Dict[str, Any]):
        """Cập nhật modules từ dữ liệu CAN bus."""
        # Format CAN data: {node_id: {module_id: {parameter: value}}}
        for node_id, node_data in can_data.items():
            if isinstance(node_data, dict):
                for module_id, module_params in node_data.items():
                    if isinstance(module_params, dict):
                        self.update_module_parameters(node_id, module_id, **module_params)
                        
    def simulate_realtime_data(self):
        """Mô phỏng dữ liệu thời gian thực cho tất cả modules."""
        import random
        current_time = int(time.time())
        
        for node_id, node_modules in self.modules.items():
            for module_id, module in node_modules.items():
                # Tạo biến động nhỏ dựa trên thời gian
                random.seed(hash(f"{module_id}_{current_time}"))
                
                # Biến động nhỏ quanh giá trị hiện tại
                voltage_delta = random.uniform(-0.5, 0.5)
                current_delta = random.uniform(-0.2, 0.2)
                power_delta = random.uniform(-1, 1)
                resistance_delta = random.uniform(-2, 2)
                temp_delta = random.uniform(-1, 1)
                
                new_voltage = max(0, module.parameters.voltage + voltage_delta)
                new_current = max(0, module.parameters.current + current_delta)
                new_power = max(0, module.parameters.power + power_delta)
                new_resistance = max(0, module.parameters.resistance + resistance_delta)
                new_temp = max(0, module.parameters.temperature + temp_delta)
                
                module.update_parameters(
                    voltage=new_voltage,
                    current=new_current,
                    power=new_power,
                    resistance=new_resistance,
                    temperature=new_temp
                )
                
    def get_modules_by_status(self, status: str) -> List[ModuleData]:
        """Lấy tất cả modules theo trạng thái."""
        result = []
        for node_modules in self.modules.values():
            for module in node_modules.values():
                if module.status == status:
                    result.append(module)
        return result
        
    def export_to_file(self, filepath: str):
        """Xuất dữ liệu ra file JSON."""
        data = {}
        for node_id, node_modules in self.modules.items():
            data[node_id] = {}
            for module_id, module in node_modules.items():
                data[node_id][module_id] = module.to_dict()
                
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def import_from_file(self, filepath: str):
        """Nhập dữ liệu từ file JSON với error handling cải thiện."""
        if not os.path.exists(filepath):
            print(f"Error: Import file not found: {filepath}")
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_count = 0
            for node_id, node_modules in data.items():
                if node_id not in self.modules:
                    self.modules[node_id] = {}

                for module_id, module_data in node_modules.items():
                    try:
                        module = ModuleData(
                            module_data['module_id'],
                            module_data['name'],
                            module_data['node_id']
                        )
                        module.parameters = ModuleParameters.from_dict(module_data['parameters'])
                        module.status = module_data['status']
                        module.error_messages = module_data['error_messages']
                        module.last_update = module_data['last_update']

                        self.modules[node_id][module_id] = module
                        imported_count += 1

                    except KeyError as e:
                        print(f"Warning: Missing field in module data {module_id}: {e}")
                    except Exception as e:
                        print(f"Warning: Error importing module {module_id}: {e}")

            print(f"Successfully imported {imported_count} modules from {filepath}")
            return True

        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in import file {filepath}: {e}")
            return False

        except PermissionError:
            print(f"Error: Permission denied reading import file {filepath}")
            return False

        except Exception as e:
            print(f"Unexpected error importing data from {filepath}: {e}")
            return False

# Global instance
module_manager = ModuleManager()

# API Functions để sử dụng từ external systems
def update_module_from_can(node_id: str, module_id: str, can_message: bytes):
    """
    Cập nhật module từ CAN message.
    
    Args:
        node_id: ID của node
        module_id: ID của module  
        can_message: Raw CAN message bytes
    """
    # Parse CAN message (implement theo protocol của bạn)
    # Ví dụ format CAN message: [voltage_bytes, current_bytes, power_bytes, resistance_bytes]
    try:
        if len(can_message) >= 16:  # 4 parameters x 4 bytes each
            voltage = int.from_bytes(can_message[0:4], 'big') / 100.0
            current = int.from_bytes(can_message[4:8], 'big') / 100.0  
            power = int.from_bytes(can_message[8:12], 'big') / 100.0
            resistance = int.from_bytes(can_message[12:16], 'big') / 100.0
            
            module_manager.update_module_parameters(
                node_id, module_id,
                voltage=voltage,
                current=current,
                power=power,
                resistance=resistance
            )
            return True
    except Exception as e:
        print(f"Lỗi parse CAN message: {e}")
    
    return False

def update_module_from_api(node_id: str, module_id: str, api_data: Dict[str, float]):
    """
    Cập nhật module từ API data.
    
    Args:
        node_id: ID của node
        module_id: ID của module
        api_data: Dictionary chứa các thông số {'voltage': 12.5, 'current': 2.3, ...}
    """
    return module_manager.update_module_parameters(node_id, module_id, **api_data)

def get_all_module_data() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Lấy tất cả dữ liệu module để hiển thị."""
    result = {}
    for node_id, node_modules in module_manager.modules.items():
        result[node_id] = {}
        for module_id, module in node_modules.items():
            result[node_id][module_id] = {
                'name': module.name,
                'parameters': module.parameters.to_dict(),
                'status': module.status,
                'errors': module.error_messages,
                'last_update': module.last_update
            }
    return result