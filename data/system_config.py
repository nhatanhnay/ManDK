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

# Cấu hình modules cho từng node/hộp/tủ
NODE_MODULE_CONFIG: Dict[str, List[ModuleConfig]] = {
    
    # === KHOANG ĐIỀU KHIỂN TẠI CHỖ 1 ===
    'ac_quy_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=48.0, default_current=10.0, default_power=480.0,
            min_voltage=42.0, max_voltage=54.0, max_current=15.0,
            description="Module sạc chính cho hệ thống ắc quy"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=24.0, default_current=2.0, default_power=48.0,
            description="Module điều khiển quá trình sạc ắc quy"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module giám sát điện áp từng cell"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module cân bằng điện áp giữa các cell"
        ),
        ModuleConfig(
            name="module_5",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            max_current=5.0,
            description="Module bảo vệ khỏi quá tải và ngắn mạch"
        )
    ],
    
    'phan_phoi_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=220.0, default_current=50.0, default_power=11000.0,
            min_voltage=200.0, max_voltage=240.0, max_current=80.0,
            description="Module phân phối điện chính"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=48.0, default_current=20.0, default_power=960.0,
            description="Module biến đổi điện áp DC"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.5, default_power=18.0,
            description="Module lọc nhiễu điện từ"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module giám sát công suất tiêu thụ"
        ),
        ModuleConfig(
            name="module_5",
            default_voltage=12.0, default_current=0.3, default_power=3.6,
            description="Module bảo vệ đấu ngược cực"
        ),
        ModuleConfig(
            name="module_6",
            default_voltage=24.0, default_current=5.0, default_power=120.0,
            description="Module ổn định điện áp đầu ra"
        )
    ],
    
    'bien_ap_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=380.0, default_current=100.0, default_power=38000.0,
            min_voltage=350.0, max_voltage=420.0, max_current=150.0,
            description="Module biến áp công suất chính"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=24.0, default_current=3.0, default_power=72.0,
            description="Module điều chỉnh điện áp tự động"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module bảo vệ biến áp khỏi quá tải"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            default_temperature=45.0, max_temperature=85.0,
            description="Module giám sát nhiệt độ biến áp"
        )
    ],
    
    'dan_dong_huong_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=48.0, default_current=15.0, default_power=720.0,
            max_current=25.0,
            description="Module điều khiển servo hướng"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module đọc vị trí góc hướng"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module điều khiển PID hướng"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module bảo vệ giới hạn góc hướng"
        )
    ],
    
    'dan_dong_tam_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=48.0, default_current=12.0, default_power=576.0,
            max_current=20.0,
            description="Module điều khiển servo tâm"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module đọc vị trí góc tâm"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module điều khiển PID tâm"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.6, default_power=7.2,
            description="Module cân bằng trọng lượng"
        )
    ],
    
    'dieu_khien_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=12.0, default_current=3.0, default_power=36.0,
            description="Module xử lý trung tâm"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=1.5, default_power=18.0,
            description="Module đầu vào/ra số"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module chuyển đổi analog-digital"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module giao tiếp CAN bus"
        ),
        ModuleConfig(
            name="module_5",
            default_voltage=12.0, default_current=0.3, default_power=3.6,
            description="Module lưu trữ dữ liệu"
        )
    ],
    
    'ban_dieu_khien_1': [
        ModuleConfig(
            name="module_1",
            default_voltage=24.0, default_current=2.0, default_power=48.0,
            description="Module màn hình giao diện người dùng"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module bàn phím điều khiển"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module đèn LED báo hiệu"
        )
    ],
    
    'hn11': [
        ModuleConfig(
            name="module_1",
            default_voltage=28.0, default_current=5.0, default_power=140.0,
            description="Module nguồn cấp cho HN11"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module giao tiếp với hệ thống HN11"
        )
    ],
    
    'hn12': [
        ModuleConfig(
            name="module_1",
            default_voltage=28.0, default_current=5.0, default_power=140.0,
            description="Module nguồn cấp cho HN12"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module giao tiếp với hệ thống HN12"
        )
    ],
    
    # === KHOANG ĐIỀU KHIỂN GIỮA ===
    'giao_tiep_hang_hai': [
        ModuleConfig(
            name="module_1",
            default_voltage=12.0, default_current=1.5, default_power=18.0,
            description="Module giao tiếp Ethernet với hệ thống hàng hải"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module giao tiếp RS485"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=2.0, default_power=24.0,
            description="Module định vị GPS và quán tính"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module la bàn điện tử"
        )
    ],
    
    'ban_dieu_khien_chinh': [
        ModuleConfig(
            name="module_1",
            default_voltage=24.0, default_current=4.0, default_power=96.0,
            description="Module màn hình điều khiển chính"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module bàn phím điều khiển chính"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module cần điều khiển"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.3, default_power=3.6,
            description="Module nút dừng khẩn cấp"
        )
    ],
    
    'bang_dien_chinh': [
        ModuleConfig(
            name="Module phân phối điện chính",
            default_voltage=440.0, default_current=200.0, default_power=88000.0,
            min_voltage=400.0, max_voltage=480.0, max_current=300.0,
            description="Module phân phối điện năng chính"
        ),
        ModuleConfig(
            name="Module UPS",
            default_voltage=220.0, default_current=50.0, default_power=11000.0,
            description="Module nguồn lưu điện UPS"
        ),
        ModuleConfig(
            name="Module đo lường điện",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module đo các thông số điện"
        ),
        ModuleConfig(
            name="Module bảo vệ chính",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module bảo vệ hệ thống điện chính"
        )
    ],
    
    # === KHOANG ĐIỀU KHIỂN TẠI CHỖ 2 (tương tự khoang 1) ===
    'ac_quy_2': [
        ModuleConfig(
            name="Module sạc chính 2",
            default_voltage=48.0, default_current=10.0, default_power=480.0,
            min_voltage=42.0, max_voltage=54.0, max_current=15.0,
            description="Module sạc chính cho hệ thống ắc quy 2"
        ),
        ModuleConfig(
            name="Module điều khiển sạc 2",
            default_voltage=24.0, default_current=2.0, default_power=48.0,
            description="Module điều khiển quá trình sạc ắc quy 2"
        ),
        ModuleConfig(
            name="Module giám sát điện áp 2",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module giám sát điện áp từng cell"
        ),
        ModuleConfig(
            name="Module cân bằng cell 2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module cân bằng điện áp giữa các cell"
        )
    ],
    
    'phan_phoi_2': [
        ModuleConfig(
            name="Module phân phối chính 2",
            default_voltage=220.0, default_current=50.0, default_power=11000.0,
            min_voltage=200.0, max_voltage=240.0, max_current=80.0,
            description="Module phân phối điện chính 2"
        ),
        ModuleConfig(
            name="Module biến đổi DC/DC 2",
            default_voltage=48.0, default_current=20.0, default_power=960.0,
            description="Module biến đổi điện áp DC 2"
        ),
        ModuleConfig(
            name="Module lọc nhiễu 2",
            default_voltage=12.0, default_current=1.5, default_power=18.0,
            description="Module lọc nhiễu điện từ 2"
        ),
        ModuleConfig(
            name="Module giám sát công suất 2",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module giám sát công suất tiêu thụ 2"
        )
    ],
    
    'bien_ap_2': [
        ModuleConfig(
            name="Module biến áp chính 2",
            default_voltage=380.0, default_current=100.0, default_power=38000.0,
            min_voltage=350.0, max_voltage=420.0, max_current=150.0,
            description="Module biến áp công suất chính 2"
        ),
        ModuleConfig(
            name="Module điều áp tự động 2",
            default_voltage=24.0, default_current=3.0, default_power=72.0,
            description="Module điều chỉnh điện áp tự động 2"
        ),
        ModuleConfig(
            name="Module bảo vệ quá tải 2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module bảo vệ biến áp khỏi quá tải 2"
        )
    ],
    
    'dan_dong_huong_2': [
        ModuleConfig(
            name="Module servo hướng 2",
            default_voltage=48.0, default_current=15.0, default_power=720.0,
            max_current=25.0,
            description="Module điều khiển servo hướng 2"
        ),
        ModuleConfig(
            name="Module encoder hướng 2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module đọc vị trí góc hướng 2"
        ),
        ModuleConfig(
            name="Module PID hướng 2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module điều khiển PID hướng 2"
        )
    ],
    
    'dan_dong_tam_2': [
        ModuleConfig(
            name="Module servo tâm 2",
            default_voltage=48.0, default_current=12.0, default_power=576.0,
            max_current=20.0,
            description="Module điều khiển servo tâm 2"
        ),
        ModuleConfig(
            name="Module encoder tâm 2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module đọc vị trí góc tâm 2"
        ),
        ModuleConfig(
            name="Module PID tâm 2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module điều khiển PID tâm 2"
        )
    ],
    
    'dieu_khien_2': [
        ModuleConfig(
            name="Module CPU chính 2",
            default_voltage=12.0, default_current=3.0, default_power=36.0,
            description="Module xử lý trung tâm 2"
        ),
        ModuleConfig(
            name="Module I/O số 2",
            default_voltage=12.0, default_current=1.5, default_power=18.0,
            description="Module đầu vào/ra số 2"
        ),
        ModuleConfig(
            name="Module ADC 2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description="Module chuyển đổi analog-digital 2"
        ),
        ModuleConfig(
            name="Module giao tiếp CAN 2",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module giao tiếp CAN bus 2"
        )
    ],
    
    'ban_dieu_khien_2': [
        ModuleConfig(
            name="Module màn hình HMI 2",
            default_voltage=24.0, default_current=2.0, default_power=48.0,
            description="Module màn hình giao diện người dùng 2"
        ),
        ModuleConfig(
            name="Module bàn phím 2",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module bàn phím điều khiển 2"
        ),
        ModuleConfig(
            name="Module LED báo trạng thái 2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module đèn LED báo hiệu 2"
        )
    ],
    
    'hn21': [
        ModuleConfig(
            name="Module nguồn HN21",
            default_voltage=28.0, default_current=5.0, default_power=140.0,
            description="Module nguồn cấp cho HN21"
        ),
        ModuleConfig(
            name="Module giao tiếp HN21",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module giao tiếp với hệ thống HN21"
        )
    ],
    
    'hn22': [
        ModuleConfig(
            name="Module nguồn HN22",
            default_voltage=28.0, default_current=5.0, default_power=140.0,
            description="Module nguồn cấp cho HN22"
        ),
        ModuleConfig(
            name="Module giao tiếp HN22",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module giao tiếp với hệ thống HN22"
        )
    ],
    
    # === CỘT NGẮM ===
    'hop_dien': [
        ModuleConfig(
            name="module_1",
            default_voltage=48.0, default_current=20.0, default_power=960.0,
            min_voltage=42.0, max_voltage=54.0, max_current=30.0,
            description="Module nguồn chính cho hộp điện"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=24.0, default_current=8.0, default_power=192.0,
            description="Module điều khiển các servo cột ngắm"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description="Module đọc vị trí cột ngắm"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5, default_power=6.0,
            description="Module cảm biến độ nghiêng tàu"
        ),
        ModuleConfig(
            name="module_5",
            default_voltage=12.0, default_current=2.0, default_power=24.0,
            description="Module bù trừ nghiêng tự động"
        ),
        ModuleConfig(
            name="module_6",
            default_voltage=12.0, default_current=0.3, default_power=3.6,
            description="Module bảo vệ giới hạn góc"
        )
    ],
    
    'hop_quang_dien_tu': [
        ModuleConfig(
            name="module_1",
            default_voltage=24.0, default_current=3.0, default_power=72.0,
            description="Module camera ảnh nhiệt"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=2.0, default_power=24.0,
            description="Module camera ánh sáng khả kiến"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=4.0, default_power=48.0,
            description="Module đo khoảng cách laser"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=5.0, default_power=60.0,
            description="Module xử lý hình ảnh AI"
        ),
        ModuleConfig(
            name="module_5",
            default_voltage=12.0, default_current=1.5, default_power=18.0,
            description="Module truyền dữ liệu video"
        ),
        ModuleConfig(
            name="module_6",
            default_voltage=24.0, default_current=6.0, default_power=144.0,
            description="Module ổn định hình ảnh"
        ),
        ModuleConfig(
            name="module_7",
            default_voltage=12.0, default_current=2.5, default_power=30.0,
            description="Module zoom và focus tự động"
        ),
        ModuleConfig(
            name="module_8",
            default_voltage=24.0, default_current=4.0, default_power=96.0,
            description="Module đèn LED chiếu sáng ban đêm"
        )
    ]
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