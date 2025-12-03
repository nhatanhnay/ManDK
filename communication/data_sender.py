import can
from ui.tabs.event_log_tab import LogTab

# Import CAN configuration
from communication.can_config import (
    CAN_CHANNEL, CAN_BUSTYPE, CAN_BITRATE,
    CAN_ID_LAUNCH_COMMAND, CAN_ID_ANGLE_LEFT, CAN_ID_ANGLE_RIGHT,
    COMMAND_START, COMMAND_END, ANGLE_COMMAND_HEADER,
    get_can_id_for_angle
)

def sender_ammo_status(idx, data):
    """
    Gửi dữ liệu qua CAN bus.
    
    Args:
        idx: Index của message
        data: List các vị trí cần set flag
        
    Raises:
        OSError: Khi CAN device không tồn tại
        Exception: Các lỗi khác khi gửi dữ liệu
    """
    try:
        flags = [0]*18
        for i in data:
            flags[i-1] = 1
        flag1 = flags[:8][::-1]
        flag2 = flags[8:16][::-1]
        flag3 = flags[16:][::-1]
        flag1  = ''.join(str(b) for b in flag1)
        flag2  = ''.join(str(b) for b in flag2)
        flag3  = ''.join(str(b) for b in flag3)
        flag1 = int(flag1, 2)
        flag2 = int(flag2, 2)
        flag3 = int(flag3, 2)
        data_launch = [
            COMMAND_START,
            idx,
            flag1,
            flag2,
            flag3,
            COMMAND_END
        ]
        # print(f'Sending data: {flag1:08b} {flag2:08b} {flag3:08b}')
        
        bus = can.interface.Bus(channel=CAN_CHANNEL, bustype=CAN_BUSTYPE, bitrate=CAN_BITRATE)
        msg_launch = can.Message(
            arbitration_id=CAN_ID_LAUNCH_COMMAND,
            data=data_launch,
            is_extended_id=False
        )
        print('CAN message sent successfully')
        bus.send(msg_launch)
        bus.shutdown()
        return True
        
    except OSError as e:
        if e.errno == 19:  # No such device
            error_msg = f"Lỗi CAN: Không tìm thấy thiết bị '{CAN_CHANNEL}'. Vui lòng kiểm tra kết nối CAN bus."
            print(error_msg)
            # Ghi log vào event log
            try:
                LogTab.log(error_msg, "ERROR")
            except:
                pass
        else:
            error_msg = f"Lỗi CAN OSError: {e}"
            print(error_msg)
            try:
                LogTab.log(error_msg, "ERROR")
            except:
                pass
        return False
        
    except Exception as e:
        error_msg = f"Lỗi không xác định khi gửi dữ liệu CAN: {e}"
        print(error_msg)
        try:
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return False
def sender_angle_direction(angle, direction, idx=CAN_ID_ANGLE_RIGHT):
    """
    Gửi dữ liệu góc và hướng qua CAN bus.
    
    Args:
        angle: Góc (int)
        direction: Hướng (int)
        idx: ID của giàn (CAN_ID_ANGLE_LEFT cho giàn trái, CAN_ID_ANGLE_RIGHT cho giàn phải). Mặc định là CAN_ID_ANGLE_RIGHT.
        
    Raises:
        OSError: Khi CAN device không tồn tại
        Exception: Các lỗi khác khi gửi dữ liệu
    """
    try:
        data_launch = [
            ANGLE_COMMAND_HEADER,
            angle & 0xFF,
            (angle >> 8) & 0xFF,
            direction & 0xFF,
            (direction >> 8) & 0xFF,
            COMMAND_END
        ]
        can_data = ' '.join([f'0x{byte:02X}' for byte in data_launch])
        
        bus = can.interface.Bus(channel=CAN_CHANNEL, bustype=CAN_BUSTYPE, bitrate=CAN_BITRATE)
        msg_launch = can.Message(
            arbitration_id=idx,
            data=data_launch,
            is_extended_id=False
        )
        message = f'Dữ liệu gửi góc: {angle/10:.1f}, hướng: {direction/10:.1f} tới ID: {hex(idx)}. Data: {can_data}'
        LogTab.log(message, "INFO")
        bus.send(msg_launch)
        bus.shutdown()
        return True
        
    except OSError as e:
        if e.errno == 19:  # No such device
            error_msg = f"Lỗi CAN: Không tìm thấy thiết bị '{CAN_CHANNEL}'. Vui lòng kiểm tra kết nối CAN bus. Dữ liệu gửi: ID {hex(idx)}, Góc {angle/10:.1f}, Hướng {direction/10:.1f}. Data {can_data}"
            # Ghi log vào event log
            try:
                LogTab.log(error_msg, "ERROR")
            except:
                pass
        else:
            error_msg = f"Lỗi CAN OSError: {e}"
            print(error_msg)
            try:
                LogTab.log(error_msg, "ERROR")
            except:
                pass
        return False
        
    except Exception as e:
        error_msg = f"Lỗi không xác định khi gửi dữ liệu CAN: {e}"
        print(error_msg)
        try:
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return False