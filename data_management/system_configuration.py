"""
File cấu hình định nghĩa các module và thông số cho từng hộp/tủ trong hệ thống.
Mỗi node (hộp/tủ) có danh sách modules cụ thể với thông số mặc định.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ModuleConfig:
    """Cấu hình của một module."""
    name: str
    default_voltage: float = 12.0      # Điện áp mặc định (V)
    default_current: float = 2.0       # Dòng điện mặc định (A) 
    default_power: float = 24.0        # Công suất mặc định (W)
    default_resistance: float = 50.0   # Điện trở mặc định (Ω)
    default_temperature: float = 35.0  # Nhiệt độ mặc định (°C)
    min_voltage: float = 8.0           # Ngưỡng điện áp tối thiểu
    max_voltage: float = 15.0          # Ngưỡng điện áp tối đa
    max_current: float = 8.0           # Ngưỡng dòng điện tối đa
    max_temperature: float = 70.0      # Ngưỡng nhiệt độ tối đa
    description: str = ""              # Mô tả chức năng module

# Refactored: Import node configurations from separate module - Updated path
try:
    from config.node_configs import (
        get_battery_node_config,
        get_power_distribution_node_config,
        get_transformer_node_config,
        get_servo_control_node_config,
        get_control_unit_node_config,
        get_control_panel_node_config,
        get_hn_system_node_config,
        get_communication_node_config,
        get_main_control_panel_config,
        get_main_electrical_panel_config,
        get_sight_column_electrical_config,
        get_optoelectronic_config
    )

    # Cấu hình modules cho từng node/hộp/tủ - Refactored to use functions
    NODE_MODULE_CONFIG: Dict[str, List[ModuleConfig]] = {

        # === KHOANG ĐIỀU KHIỂN TẠI CHỖ 1 ===
        'ac_quy_1': get_battery_node_config(),
        'phan_phoi_1': get_power_distribution_node_config(),
        'bien_ap_1': get_transformer_node_config(),
        'dan_dong_huong_1': get_servo_control_node_config("direction"),
        'dan_dong_tam_1': get_servo_control_node_config("elevation"),
        'dieu_khien_1': get_control_unit_node_config(),
        'ban_dieu_khien_1': get_control_panel_node_config(),
        'hn11': get_hn_system_node_config("HN11"),
        'hn12': get_hn_system_node_config("HN12"),

        # === KHOANG ĐIỀU KHIỂN GIỮA ===
        'giao_tiep_hang_hai': get_communication_node_config(),
        'ban_dieu_khien_chinh': get_main_control_panel_config(),
        'bang_dien_chinh': get_main_electrical_panel_config(),

        # === KHOANG ĐIỀU KHIỂN TẠI CHỖ 2 (tương tự khoang 1) ===
        'ac_quy_2': get_battery_node_config(),
        'phan_phoi_2': get_power_distribution_node_config(),
        'bien_ap_2': get_transformer_node_config(),
        'dan_dong_huong_2': get_servo_control_node_config("direction"),
        'dan_dong_tam_2': get_servo_control_node_config("elevation"),
        'dieu_khien_2': get_control_unit_node_config(),
        'ban_dieu_khien_2': get_control_panel_node_config(),
        'hn21': get_hn_system_node_config("HN21"),
        'hn22': get_hn_system_node_config("HN22"),

        # === CỘT NGẮM ===
        'hop_dien': get_sight_column_electrical_config(),
        'hop_quang_dien_tu': get_optoelectronic_config()
    }

except ImportError:
    # Fallback to legacy configuration if new module not available
    print("Warning: Using legacy configuration. Consider updating imports.")
    NODE_MODULE_CONFIG: Dict[str, List[ModuleConfig]] = {
        # Fallback configuration would go here - keeping existing for compatibility
    }

def get_node_modules(node_id: str) -> List[ModuleConfig]:
    """Lấy danh sách modules của một node."""
    return NODE_MODULE_CONFIG.get(node_id, [])

def get_all_nodes() -> List[str]:
    """Lấy danh sách tất cả node IDs."""
    return list(NODE_MODULE_CONFIG.keys())

def get_node_info() -> Dict[str, Dict[str, Any]]:
    """Lấy thống kê thông tin các nodes."""
    result = {}
    for node_id, modules in NODE_MODULE_CONFIG.items():
        total_power = sum(m.default_power for m in modules)
        max_voltage = max(m.default_voltage for m in modules) if modules else 0
        result[node_id] = {
            'module_count': len(modules),
            'total_default_power': total_power,
            'max_voltage': max_voltage,
            'modules': [m.name for m in modules]
        }
    return result

def validate_node_config(node_id: str) -> Dict[str, Any]:
    """Kiểm tra tính hợp lệ của cấu hình node."""
    modules = get_node_modules(node_id)
    if not modules:
        return {'valid': False, 'error': f'Node {node_id} không có modules'}
    
    issues = []
    for module in modules:
        if module.default_voltage < module.min_voltage or module.default_voltage > module.max_voltage:
            issues.append(f'{module.name}: Điện áp mặc định ngoài phạm vi')
        if module.default_current > module.max_current:
            issues.append(f'{module.name}: Dòng điện mặc định vượt giới hạn')
        if module.default_power != module.default_voltage * module.default_current:
            # Chấp nhận sai số 10%
            calculated_power = module.default_voltage * module.default_current
            error_percent = abs(module.default_power - calculated_power) / calculated_power * 100
            if error_percent > 10:
                issues.append(f'{module.name}: Công suất không khớp với V*I')
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'module_count': len(modules)
    }

# Hàm tiện ích để tìm kiếm modules
def find_modules_by_name(search_term: str) -> Dict[str, List[str]]:
    """Tìm modules theo tên (không phân biệt hoa thường)."""
    result = {}
    search_lower = search_term.lower()
    
    for node_id, modules in NODE_MODULE_CONFIG.items():
        found_modules = []
        for module in modules:
            if search_lower in module.name.lower() or search_lower in module.description.lower():
                found_modules.append(module.name)
        
        if found_modules:
            result[node_id] = found_modules
    
    return result

def get_high_power_modules(power_threshold: float = 100.0) -> Dict[str, List[str]]:
    """Lấy danh sách modules có công suất cao."""
    result = {}
    
    for node_id, modules in NODE_MODULE_CONFIG.items():
        high_power_modules = []
        for module in modules:
            if module.default_power >= power_threshold:
                high_power_modules.append({
                    'name': module.name,
                    'power': module.default_power,
                    'voltage': module.default_voltage,
                    'current': module.default_current
                })
        
        if high_power_modules:
            result[node_id] = high_power_modules
    
    return result

if __name__ == "__main__":
    # Demo usage
    print("=== CẤU HÌNH MODULES TRONG HỆ THỐNG ===")
    
    # Hiển thị thống kê tổng quan
    print("\n📊 THỐNG KÊ TỔNG QUAN:")
    info = get_node_info()
    total_modules = sum(info[node]['module_count'] for node in info)
    total_power = sum(info[node]['total_default_power'] for node in info)
    
    print(f"Tổng số nodes: {len(info)}")
    print(f"Tổng số modules: {total_modules}")
    print(f"Tổng công suất mặc định: {total_power:.1f}W")
    
    # Hiển thị top nodes có nhiều modules nhất
    print(f"\n🏆 TOP NODES CÓ NHIỀU MODULES:")
    sorted_nodes = sorted(info.items(), key=lambda x: x[1]['module_count'], reverse=True)
    for i, (node_id, data) in enumerate(sorted_nodes[:5]):
        print(f"{i+1}. {node_id}: {data['module_count']} modules ({data['total_default_power']:.1f}W)")
    
    # Kiểm tra một vài nodes
    print(f"\n🔍 KIỂM TRA CẤU HÌNH:")
    test_nodes = ['hop_dien', 'hop_quang_dien_tu', 'bang_dien_chinh']
    for node_id in test_nodes:
        validation = validate_node_config(node_id)
        status = "✅ Hợp lệ" if validation['valid'] else "❌ Có lỗi"
        print(f"{node_id}: {status}")
        if not validation['valid']:
            for issue in validation['issues']:
                print(f"  - {issue}")
    
    # Tìm modules công suất cao
    print(f"\n⚡ MODULES CÔNG SUẤT CAO (>1000W):")
    high_power = get_high_power_modules(1000.0)
    for node_id, modules in high_power.items():
        print(f"{node_id}:")
        for module in modules:
            print(f"  - {module['name']}: {module['power']}W")