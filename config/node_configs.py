# -*- coding: utf-8 -*-
"""
Node configuration definitions - Split from large system_config.py for better maintainability.
Defines specific configurations for different node types.
"""

from typing import List
from data_management.system_configuration import ModuleConfig


def get_battery_node_config() -> List[ModuleConfig]:
    """Cấu hình cho các node ắc quy."""
    return [
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
    ]


def get_power_distribution_node_config() -> List[ModuleConfig]:
    """Cấu hình cho các node phân phối điện."""
    return [
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
    ]


def get_transformer_node_config() -> List[ModuleConfig]:
    """Cấu hình cho các node biến áp."""
    return [
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
    ]


def get_servo_control_node_config(servo_type: str) -> List[ModuleConfig]:
    """
    Cấu hình cho các node điều khiển servo.

    Args:
        servo_type: 'direction' hoặc 'elevation'
    """
    current_limit = 25.0 if servo_type == "direction" else 20.0
    base_current = 15.0 if servo_type == "direction" else 12.0

    return [
        ModuleConfig(
            name="module_1",
            default_voltage=48.0, default_current=base_current, default_power=720.0 if servo_type == "direction" else 576.0,
            max_current=current_limit,
            description=f"Module điều khiển servo {servo_type}"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=0.8, default_power=9.6,
            description=f"Module đọc vị trí góc {servo_type}"
        ),
        ModuleConfig(
            name="module_3",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description=f"Module điều khiển PID {servo_type}"
        ),
        ModuleConfig(
            name="module_4",
            default_voltage=12.0, default_current=0.5 if servo_type == "direction" else 0.6,
            default_power=6.0 if servo_type == "direction" else 7.2,
            description="Module bảo vệ giới hạn góc" if servo_type == "direction" else "Module cân bằng trọng lượng"
        )
    ]


def get_control_unit_node_config() -> List[ModuleConfig]:
    """Cấu hình cho các node điều khiển."""
    return [
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
    ]


def get_control_panel_node_config() -> List[ModuleConfig]:
    """Cấu hình cho các node bàn điều khiển."""
    return [
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
    ]


def get_hn_system_node_config(system_id: str) -> List[ModuleConfig]:
    """
    Cấu hình cho các hệ thống HN.

    Args:
        system_id: ID của hệ thống HN (ví dụ: "HN11", "HN12")
    """
    return [
        ModuleConfig(
            name="module_1",
            default_voltage=28.0, default_current=5.0, default_power=140.0,
            description=f"Module nguồn cấp cho {system_id}"
        ),
        ModuleConfig(
            name="module_2",
            default_voltage=12.0, default_current=1.0, default_power=12.0,
            description=f"Module giao tiếp với hệ thống {system_id}"
        )
    ]


def get_communication_node_config() -> List[ModuleConfig]:
    """Cấu hình cho node giao tiếp hàng hải."""
    return [
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
    ]


def get_main_control_panel_config() -> List[ModuleConfig]:
    """Cấu hình cho bàn điều khiển chính."""
    return [
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
    ]


def get_main_electrical_panel_config() -> List[ModuleConfig]:
    """Cấu hình cho bảng điện chính."""
    return [
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
    ]


def get_sight_column_electrical_config() -> List[ModuleConfig]:
    """Cấu hình cho hộp điện cột ngắm."""
    return [
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
    ]


def get_optoelectronic_config() -> List[ModuleConfig]:
    """Cấu hình cho hộp quang điện tử."""
    return [
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