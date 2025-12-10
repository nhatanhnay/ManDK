# -*- coding: utf-8 -*-
"""
Webhook Configuration
=====================
File cấu hình cho hệ thống webhook, thay thế cho CAN bus.
Jetson1 sẽ gửi HTTP requests đến Jetson2 qua webhook.
"""

# =============================================================================
# Webhook Settings
# =============================================================================

# Jetson Left (Pháo trái) webhook server endpoint
JETSON_LEFT_HOST = "192.0.0.101"  # IP của Jetson Left
JETSON_LEFT_PORT = 5000
JETSON_LEFT_BASE_URL = f"http://{JETSON_LEFT_HOST}:{JETSON_LEFT_PORT}"

# Jetson Right (Pháo phải) webhook server endpoint
JETSON_RIGHT_HOST = "192.0.0.102"  # IP của Jetson Right
JETSON_RIGHT_PORT = 5000
JETSON_RIGHT_BASE_URL = f"http://{JETSON_RIGHT_HOST}:{JETSON_RIGHT_PORT}"

# Jetson3 (Quang điện tử) - Chỉ gửi, không nhận
JETSON3_HOST = "192.0.0.103"  # IP của Jetson3

# Timeout cho các HTTP requests (seconds)
WEBHOOK_TIMEOUT = 5

# Retry settings
WEBHOOK_MAX_RETRIES = 3
WEBHOOK_RETRY_DELAY = 1  # seconds


# =============================================================================
# Webhook Endpoints - Send (Jetson1 -> Jetson Left/Right)
# =============================================================================

# Endpoint gửi lệnh phóng đạn
ENDPOINT_LAUNCH_COMMAND = "/api/launch"

# Endpoint gửi lệnh góc và hướng cho pháo
ENDPOINT_ANGLE_COMMAND = "/api/angle"


# =============================================================================
# Webhook Endpoints - Receive (Jetson2 -> Jetson1)
# =============================================================================

# Jetson1 webhook server settings (để nhận dữ liệu từ Jetson2)
JETSON1_HOST = "0.0.0.0"  # Listen on all interfaces
JETSON1_PORT = 5001

# Endpoint nhận khoảng cách và hướng từ Quang điện tử
ENDPOINT_DISTANCE = "/api/distance"
ENDPOINT_DIRECTION = "/api/direction"

# Endpoint nhận góc hiện tại của pháo (từ cảm biến encoder)
ENDPOINT_CANNON_LEFT = "/api/cannon/left"
ENDPOINT_CANNON_RIGHT = "/api/cannon/right"

# Endpoint nhận trạng thái đạn
ENDPOINT_AMMO_STATUS = "/api/ammo/status"

# Endpoint nhận module data (điện áp, dòng điện, công suất, nhiệt độ)
ENDPOINT_MODULE_DATA = "/api/module/data"


# =============================================================================
# Data Format Constants
# =============================================================================

# Command constants
COMMAND_START = 0xAA
COMMAND_END = 0x55
ANGLE_COMMAND_HEADER = 0x01

# Side codes
SIDE_CODE_LEFT = 0x01
SIDE_CODE_RIGHT = 0x02


# =============================================================================
# Compass (La bàn) Settings
# =============================================================================

COMPASS_PORT = "/dev/ttyUSB0"     # Serial port cho la bàn
COMPASS_BAUDRATE = 4800           # Baudrate la bàn
COMPASS_TIMEOUT = 1               # Timeout (seconds)


# =============================================================================
# Helper Functions
# =============================================================================

def get_base_url_for_side(is_left: bool) -> str:
    """Lấy base URL của Jetson Left hoặc Right dựa trên giàn trái/phải."""
    return JETSON_LEFT_BASE_URL if is_left else JETSON_RIGHT_BASE_URL


def get_endpoint_for_angle() -> str:
    """Lấy endpoint để gửi góc/hướng."""
    return ENDPOINT_ANGLE_COMMAND


def get_side_code(is_left: bool) -> int:
    """Lấy mã nhận dạng giàn."""
    return SIDE_CODE_LEFT if is_left else SIDE_CODE_RIGHT
