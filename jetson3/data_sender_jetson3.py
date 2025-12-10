# -*- coding: utf-8 -*-
"""
Jetson3 Data Sender (Quang Điện Tử)
====================================
Gửi dữ liệu khoảng cách và hướng từ Jetson3 (quang điện tử) về Jetson1 qua webhook.
"""

import requests
import time
import logging

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


# =============================================================================
# Sender Functions
# =============================================================================

def send_target_data(distance, direction):
    """
    Gửi dữ liệu mục tiêu (khoảng cách + hướng) từ quang điện tử về Jetson1.
    
    Args:
        distance: Khoảng cách (meters)
        direction: Hướng (degrees, 0-360)
    
    Returns:
        bool: True nếu gửi thành công
    """
    try:
        payload = {
            "distance": distance,
            "direction": direction
        }
        url = f"{JETSON1_BASE_URL}/api/target"
        
        for attempt in range(WEBHOOK_MAX_RETRIES):
            try:
                response = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT)
                if response.status_code == 200:
                    logger.info(f"Gửi mục tiêu thành công: KC={distance:.2f}m, Hướng={direction:.2f}°")
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
        logger.error(f"Lỗi gửi dữ liệu mục tiêu: {e}")
        return False
                    time.sleep(WEBHOOK_RETRY_DELAY)
        
        return False
        
    except Exception as e:
        logger.error(f"Lỗi gửi hướng: {e}")
        return False


# =============================================================================
# Test/Demo Functions
# =============================================================================

def test_send_optoelectronic_data():
    """Hàm test để gửi dữ liệu mẫu từ quang điện tử."""
    logger.info("=" * 60)
    logger.info("Test gửi dữ liệu từ Jetson3 (Quang điện tử) -> Jetson1")
    logger.info("=" * 60)
    
    # Test gửi khoảng cách và hướng
    distances = [1500.5, 2000.0, 1750.3, 1600.8]
    directions = [45.8, 90.0, 120.5, 75.2]
    
    for dist, direc in zip(distances, directions):
        logger.info(f"\nGửi: Distance={dist:.1f}m, Direction={direc:.1f}°")
        
        success = send_target_data(dist, direc)
        time.sleep(0.5)  # Delay giữa các lần gửi
        
        if success:
            logger.info("✅ Gửi thành công")
        else:
            logger.error("❌ Gửi thất bại")
    
    logger.info("\n" + "=" * 60)
    logger.info("Test hoàn tất!")
    logger.info("=" * 60)


def continuous_send_loop(read_sensors_func, frequency_hz=10):
    """
    Loop liên tục gửi dữ liệu từ cảm biến.
    
    Args:
        read_sensors_func: Hàm đọc cảm biến, return (distance, direction)
        frequency_hz: Tần suất gửi (Hz), mặc định 10 Hz
    """
    interval = 1.0 / frequency_hz
    
    logger.info(f"Bắt đầu gửi dữ liệu liên tục với tần suất {frequency_hz} Hz")
    logger.info("Nhấn Ctrl+C để dừng")
    
    try:
        while True:
            try:
                # Đọc từ cảm biến
                distance, direction = read_sensors_func()
                
                # Gửi về Jetson1 (cả 2 giá trị cùng lúc)
                send_target_data(distance, direction)
                
                logger.debug(f"Sent: Distance={distance:.1f}m, Direction={direction:.1f}°")
                
                # Đợi đến lần gửi tiếp theo
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Lỗi trong loop: {e}")
                time.sleep(1)  # Đợi 1s nếu có lỗi
                
    except KeyboardInterrupt:
        logger.info("\nĐã dừng gửi dữ liệu")


# =============================================================================
# Example Integration
# =============================================================================

def mock_read_optoelectronic():
    """
    Mock function để đọc từ quang điện tử.
    THAY THẾ hàm này bằng code đọc thực tế từ phần cứng.
    
    Returns:
        tuple: (distance, direction)
    """
    import random
    
    # Giả lập đọc khoảng cách (1000-3000m)
    distance = 1500 + random.uniform(-500, 500)
    
    # Giả lập đọc hướng (0-360°)
    direction = random.uniform(0, 360)
    
    return distance, direction


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'loop':
        # Chạy continuous loop với mock data
        logger.info("Chạy ở chế độ continuous loop (mock data)")
        continuous_send_loop(mock_read_optoelectronic, frequency_hz=5)
    else:
        # Chạy test một lần
        test_send_optoelectronic_data()
        
        logger.info("\nĐể chạy continuous loop, dùng: python3 data_sender_jetson3.py loop")
