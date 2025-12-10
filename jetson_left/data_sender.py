# -*- coding: utf-8 -*-
"""
Jetson Left Data Sender
========================
Gửi dữ liệu từ Jetson Left (Pháo trái) về Jetson1 qua webhook.
Module này gửi:
- Góc hiện tại của pháo trái (từ encoder)
- Trạng thái đạn pháo trái (từ CAN bus)
- Module data pháo trái (điện áp, dòng điện, công suất, nhiệt độ)
"""

import requests
import time
import logging
import can_receiver  # Import CAN receiver để đọc trạng thái đạn

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

# Jetson1 webhook endpoints
JETSON1_HOST = "192.0.0.100"  # IP của Jetson1
JETSON1_PORT = 5001
JETSON1_BASE_URL = f"http://{JETSON1_HOST}:{JETSON1_PORT}"

# Timeout và retry
WEBHOOK_TIMEOUT = 5
WEBHOOK_MAX_RETRIES = 3
WEBHOOK_RETRY_DELAY = 1

# Side code cho pháo trái
SIDE_CODE_LEFT = 0x01


# =============================================================================
# Sender Functions
# =============================================================================

def send_cannon_angle(angle, direction):
    """
    Gửi góc hiện tại của pháo TRÁI về Jetson1.
    
    Args:
        angle: Góc tầm (degrees)
        direction: Hướng (degrees)
    
    Returns:
        bool: True nếu gửi thành công
    """
    try:
        payload = {
            "angle": angle,
            "direction": direction
        }
        
        url = f"{JETSON1_BASE_URL}/api/cannon/left"
        
        for attempt in range(WEBHOOK_MAX_RETRIES):
            try:
                response = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT)
                if response.status_code == 200:
                    logger.info(f"Gửi góc pháo TRÁI thành công: Góc={angle:.2f}°, Hướng={direction:.2f}°")
                    return True
                else:
                    logger.warning(f"Lỗi: Server trả về status {response.status_code}")
                    if attempt == WEBHOOK_MAX_RETRIES - 1:
                        return False
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Lỗi kết nối (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES}): {e}")
                if attempt < WEBHOOK_MAX_RETRIES - 1:
                    time.sleep(WEBHOOK_RETRY_DELAY)
        
        return False
        
    except Exception as e:
        logger.error(f"Lỗi gửi góc pháo TRÁI: {e}")
        return False


def send_ammo_status(flags=None):
    """
    Gửi trạng thái đạn pháo TRÁI về Jetson1.
    Nếu không truyền flags, sẽ đọc từ CAN bus.
    
    Args:
        flags: List 18 giá trị 0/1 cho trạng thái đạn (optional)
    
    Returns:
        bool: True nếu gửi thành công
    """
    try:
        # Nếu không truyền flags, đọc từ CAN bus
        if flags is None:
            flags = can_receiver.get_ammo_status()
            logger.info(f"Jetson LEFT: Đọc trạng thái đạn từ CAN - {sum(flags)}/18 sẵn sàng")
        
        payload = {
            "side_code": SIDE_CODE_LEFT,
            "flags": flags
        }
        url = f"{JETSON1_BASE_URL}/api/ammo/status"
        
        for attempt in range(WEBHOOK_MAX_RETRIES):
            try:
                response = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT)
                if response.status_code == 200:
                    logger.info(f"Gửi trạng thái đạn pháo TRÁI thành công")
                    return True
                else:
                    logger.warning(f"Lỗi: Server trả về status {response.status_code}")
                    if attempt == WEBHOOK_MAX_RETRIES - 1:
                        return False
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Lỗi kết nối (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES}): {e}")
                if attempt < WEBHOOK_MAX_RETRIES - 1:
                    time.sleep(WEBHOOK_RETRY_DELAY)
        
        return False
        
    except Exception as e:
        logger.error(f"Lỗi gửi trạng thái đạn: {e}")
        return False


def send_module_data(node_id, module_index, voltage, current, power, temperature):
    """
    Gửi dữ liệu module pháo TRÁI về Jetson1.
    
    Args:
        node_id: ID của node
        module_index: Index của module
        voltage: Điện áp (V)
        current: Dòng điện (A)
        power: Công suất (W)
        temperature: Nhiệt độ (°C)
    
    Returns:
        bool: True nếu gửi thành công
    """
    try:
        payload = {
            "node_id": node_id,
            "module_index": module_index,
            "voltage": voltage,
            "current": current,
            "power": power,
            "temperature": temperature
        }
        url = f"{JETSON1_BASE_URL}/api/module/data"
        
        for attempt in range(WEBHOOK_MAX_RETRIES):
            try:
                response = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT)
                if response.status_code == 200:
                    logger.debug(f"Gửi module data LEFT [{node_id}][{module_index}] thành công")
                    return True
                else:
                    logger.warning(f"Lỗi: Server trả về status {response.status_code}")
                    if attempt == WEBHOOK_MAX_RETRIES - 1:
                        return False
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Lỗi kết nối (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES}): {e}")
                if attempt < WEBHOOK_MAX_RETRIES - 1:
                    time.sleep(WEBHOOK_RETRY_DELAY)
        
        return False
        
    except Exception as e:
        logger.error(f"Lỗi gửi module data: {e}")
        return False


# =============================================================================
# Test/Demo Functions
# =============================================================================

def test_send_left_data():
    """Hàm test để gửi dữ liệu mẫu từ pháo TRÁI."""
    logger.info("=" * 60)
    logger.info("Test gửi dữ liệu từ Jetson Left (Pháo trái) -> Jetson1")
    logger.info("=" * 60)
    
    # Khởi động CAN receiver
    logger.info("Khởi động CAN receiver...")
    can_receiver.start_can_receiver()
    time.sleep(2)  # Chờ CAN receiver khởi động
    
    # Test gửi góc pháo
    send_cannon_angle(35.2, 90.5)
    time.sleep(0.5)
    
    # Test gửi trạng thái đạn (sẽ đọc từ CAN)
    send_ammo_status()  # Không truyền flags -> đọc từ CAN
    time.sleep(0.5)
    
    # Test gửi module data
    send_module_data("bang_dien_trai", 0, 48.5, 10.2, 494.7, 35)
    
    logger.info("Test hoàn tất!")


if __name__ == '__main__':
    # Chạy test khi file được execute trực tiếp
    test_send_left_data()
