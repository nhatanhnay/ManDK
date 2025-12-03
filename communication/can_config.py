# -*- coding: utf-8 -*-
"""
CAN Bus Configuration
=====================
File cấu hình cho CAN bus, bao gồm các CAN ID và bitrate.
Chỉnh sửa file này để thay đổi cấu hình CAN mà không cần sửa code.
"""

# =============================================================================
# CAN Bus Settings
# =============================================================================

# CAN channel (interface name)
CAN_CHANNEL = "can0"

# CAN bus type
CAN_BUSTYPE = "socketcan"

# CAN bitrate (bps)
CAN_BITRATE = 500000  # 500 kbps


# =============================================================================
# CAN IDs - Receive (Nhận dữ liệu)
# =============================================================================

# --- Khoảng cách và Hướng từ Quang điện tử ---
CAN_ID_DISTANCE = 0x100          # ID nhận khoảng cách (4 bytes, float)
CAN_ID_DIRECTION = 0x102         # ID nhận hướng (4 bytes, float)

# --- Góc hiện tại của Pháo (từ cảm biến encoder) ---
CAN_ID_CANNON_LEFT = 0x200       # ID nhận góc pháo trái (8 bytes: angle + direction)
CAN_ID_CANNON_RIGHT = 0x201      # ID nhận góc pháo phải (8 bytes: angle + direction)

# --- Trạng thái đạn ---
CAN_ID_AMMO_STATUS = 0x99        # ID nhận trạng thái ống phóng

# --- Module data (điện áp, dòng điện, công suất, nhiệt độ) ---
CAN_ID_MODULE_DATA_START = 0x300  # ID bắt đầu của module data
CAN_ID_MODULE_DATA_END = 0x32F    # ID kết thúc của module data


# =============================================================================
# CAN IDs - Send (Gửi dữ liệu)
# =============================================================================

# --- Lệnh phóng ---
CAN_ID_LAUNCH_COMMAND = 0x29      # ID gửi lệnh phóng

# --- Lệnh góc và hướng cho Pháo ---
CAN_ID_ANGLE_LEFT = 0x01A         # ID gửi góc/hướng cho giàn trái
CAN_ID_ANGLE_RIGHT = 0x01B        # ID gửi góc/hướng cho giàn phải


# =============================================================================
# CAN Data Format Constants
# =============================================================================

# --- Mã nhận dạng giàn trong gói tin ---
SIDE_CODE_LEFT = 0x31             # Mã giàn trái
SIDE_CODE_RIGHT = 0x32            # Mã giàn phải

# --- Mã lệnh ---
COMMAND_START = 0x31              # Byte bắt đầu lệnh phóng
COMMAND_END = 0x11                # Byte kết thúc lệnh

# --- Data header cho gói tin góc/hướng ---
ANGLE_COMMAND_HEADER = 0x11       # Byte header cho gói tin góc


# =============================================================================
# Compass (La bàn) Settings
# =============================================================================

COMPASS_PORT = "/dev/ttyUSB0"     # Serial port cho la bàn
COMPASS_BAUDRATE = 4800           # Baudrate la bàn
COMPASS_TIMEOUT = 1               # Timeout (seconds)


# =============================================================================
# Helper Functions
# =============================================================================

def is_module_data_id(can_id: int) -> bool:
    """Kiểm tra xem CAN ID có phải là module data không."""
    return CAN_ID_MODULE_DATA_START <= can_id <= CAN_ID_MODULE_DATA_END


def get_node_index_from_can_id(can_id: int) -> int:
    """Lấy node index từ CAN ID của module data."""
    if is_module_data_id(can_id):
        return can_id - CAN_ID_MODULE_DATA_START
    return -1


def get_can_id_for_angle(is_left: bool) -> int:
    """Lấy CAN ID để gửi góc/hướng dựa trên giàn trái/phải."""
    return CAN_ID_ANGLE_LEFT if is_left else CAN_ID_ANGLE_RIGHT


def get_side_code(is_left: bool) -> int:
    """Lấy mã nhận dạng giàn."""
    return SIDE_CODE_LEFT if is_left else SIDE_CODE_RIGHT
