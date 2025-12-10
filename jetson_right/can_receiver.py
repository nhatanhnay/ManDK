# -*- coding: utf-8 -*-
"""
CAN Receiver - Jetson Right
============================
Nhận trạng thái đạn từ CAN bus và cập nhật vào biến local.
Jetson Right sẽ gửi trạng thái này về Jetson1 qua webhook.
"""

import can
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CAN Configuration
# =============================================================================
CAN_CHANNEL = "can0"
CAN_BUSTYPE = "socketcan"
CAN_BITRATE = 500000

# CAN IDs
CAN_ID_AMMO_STATUS = 0x300
SIDE_CODE_RIGHT = 0x02

# Global variables để lưu trạng thái đạn
ammo_flags = [0] * 18  # 18 viên đạn
ammo_lock = threading.Lock()


# =============================================================================
# Utility Functions
# =============================================================================
def unpack_bits(byte_value, num_bits):
    """Chuyển byte thành list các bit."""
    bits = []
    for i in range(num_bits):
        bits.append((byte_value >> i) & 1)
    return bits


def get_ammo_status():
    """
    Lấy trạng thái đạn hiện tại.
    
    Returns:
        list: 18 giá trị 0/1 biểu diễn trạng thái đạn
    """
    with ammo_lock:
        return ammo_flags.copy()


# =============================================================================
# CAN Receiver Thread
# =============================================================================
def can_receiver_thread():
    """Thread nhận dữ liệu CAN liên tục."""
    global ammo_flags
    
    try:
        bus = can.interface.Bus(
            channel=CAN_CHANNEL,
            bustype=CAN_BUSTYPE,
            bitrate=CAN_BITRATE
        )
        logger.info(f"Jetson RIGHT: Đã kết nối CAN bus {CAN_CHANNEL}")
        
        while True:
            msg = bus.recv(timeout=1.0)
            if msg is None:
                continue
            
            # Chỉ xử lý message trạng thái đạn
            if msg.arbitration_id == CAN_ID_AMMO_STATUS:
                try:
                    data = msg.data
                    
                    # Kiểm tra side code
                    if data[1] != SIDE_CODE_RIGHT:
                        continue  # Bỏ qua nếu không phải pháo phải
                    
                    # Parse flags
                    flag1 = unpack_bits(data[2], 8)
                    flag2 = unpack_bits(data[3], 8)
                    flag3 = unpack_bits(data[4], 2)
                    flags = flag1 + flag2 + flag3
                    
                    # Cập nhật trạng thái
                    with ammo_lock:
                        ammo_flags = flags
                    
                    ammo_count = sum(flags)
                    logger.info(f"Jetson RIGHT: Nhận trạng thái đạn {ammo_count}/18 sẵn sàng")
                    
                except Exception as e:
                    logger.error(f"Jetson RIGHT: Lỗi xử lý CAN AMMO_STATUS: {e}")
    
    except Exception as e:
        logger.error(f"Jetson RIGHT: Lỗi CAN receiver: {e}")
    finally:
        try:
            bus.shutdown()
        except:
            pass


def start_can_receiver():
    """Khởi động CAN receiver thread."""
    thread = threading.Thread(target=can_receiver_thread, daemon=True)
    thread.start()
    logger.info("Jetson RIGHT: CAN receiver thread đã khởi động")
    return thread


# =============================================================================
# Test
# =============================================================================
if __name__ == '__main__':
    logger.info("Starting CAN receiver for Jetson RIGHT...")
    start_can_receiver()
    
    try:
        while True:
            status = get_ammo_status()
            count = sum(status)
            logger.info(f"Current ammo status: {count}/18 ready - {status}")
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Stopped")
