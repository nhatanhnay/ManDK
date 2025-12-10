# -*- coding: utf-8 -*-
"""
CAN Sender - Jetson Left
=========================
Gửi lệnh phóng đạn xuống CAN bus.
Jetson Left nhận lệnh từ Jetson1 qua webhook, sau đó gửi xuống CAN.
"""

import can
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
CAN_ID_LAUNCH_COMMAND = 0x100

# Command constants
COMMAND_START = 0xAA
COMMAND_END = 0x55

# Global CAN bus
_can_bus = None


# =============================================================================
# CAN Bus Management
# =============================================================================
def get_can_bus():
    """Lấy hoặc tạo CAN bus instance."""
    global _can_bus
    if _can_bus is None:
        try:
            _can_bus = can.interface.Bus(
                channel=CAN_CHANNEL,
                bustype=CAN_BUSTYPE,
                bitrate=CAN_BITRATE
            )
            logger.info(f"Jetson LEFT: Đã kết nối CAN bus {CAN_CHANNEL}")
        except Exception as e:
            logger.error(f"Jetson LEFT: Lỗi kết nối CAN bus: {e}")
            raise
    return _can_bus


# =============================================================================
# CAN Sender Functions
# =============================================================================
def send_launch_command(idx, positions):
    """
    Gửi lệnh phóng đạn qua CAN bus.
    
    Args:
        idx: Index của message
        positions: List các vị trí đạn cần phóng (1-18)
    
    Returns:
        bool: True nếu thành công
    """
    try:
        # Chuyển đổi positions thành bit flags
        flags = [0] * 18
        for i in positions:
            if 1 <= i <= 18:
                flags[i - 1] = 1
        
        # Đóng gói thành 3 bytes
        flag1 = flags[:8][::-1]  # Reverse để đúng thứ tự bit
        flag2 = flags[8:16][::-1]
        flag3 = flags[16:][::-1]
        
        flag1 = ''.join(str(b) for b in flag1)
        flag2 = ''.join(str(b) for b in flag2)
        flag3 = ''.join(str(b) for b in flag3)
        
        flag1 = int(flag1, 2)
        flag2 = int(flag2, 2)
        flag3 = int(flag3, 2)
        
        # Tạo CAN message
        data_launch = [
            COMMAND_START,
            idx,
            flag1,
            flag2,
            flag3,
            COMMAND_END
        ]
        
        bus = get_can_bus()
        msg = can.Message(
            arbitration_id=CAN_ID_LAUNCH_COMMAND,
            data=data_launch,
            is_extended_id=False
        )
        
        bus.send(msg)
        logger.info(f"Jetson LEFT: Gửi lệnh phóng - idx={idx}, positions={positions}")
        logger.debug(f"CAN data: {' '.join([f'0x{b:02X}' for b in data_launch])}")
        
        time.sleep(0.001)  # Delay 1ms
        return True
        
    except OSError as e:
        if e.errno == 19:
            logger.error(f"Jetson LEFT: Không tìm thấy thiết bị CAN '{CAN_CHANNEL}'")
        else:
            logger.error(f"Jetson LEFT: Lỗi CAN OSError: {e}")
        return False
        
    except Exception as e:
        logger.error(f"Jetson LEFT: Lỗi gửi lệnh phóng: {e}")
        return False


# =============================================================================
# Test
# =============================================================================
if __name__ == '__main__':
    logger.info("Testing CAN sender for Jetson LEFT...")
    
    # Test gửi lệnh phóng vị trí 1, 2, 3
    result = send_launch_command(idx=1, positions=[1, 2, 3])
    if result:
        logger.info("✅ Test thành công!")
    else:
        logger.error("❌ Test thất bại!")
