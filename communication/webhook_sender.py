# -*- coding: utf-8 -*-
"""
Webhook Data Sender
===================
Gửi dữ liệu đến Jetson Left/Right qua HTTP webhook thay vì CAN bus.
"""

import requests
import time
from ui.tabs.event_log_tab import LogTab
from communication.webhook_config import (
    JETSON_LEFT_BASE_URL,
    JETSON_RIGHT_BASE_URL,
    ENDPOINT_LAUNCH_COMMAND,
    ENDPOINT_ANGLE_COMMAND,
    WEBHOOK_TIMEOUT,
    WEBHOOK_MAX_RETRIES,
    WEBHOOK_RETRY_DELAY,
    COMMAND_START,
    COMMAND_END,
    ANGLE_COMMAND_HEADER,
    get_base_url_for_side
)


def sender_ammo_status(idx, data, is_left=True):
    """
    Gửi lệnh phóng đạn qua webhook.
    
    Args:
        idx: Index của message
        data: List các vị trí cần set flag
        is_left: True nếu gửi cho pháo trái, False cho pháo phải
        
    Returns:
        bool: True nếu gửi thành công, False nếu có lỗi
    """
    try:
        # Lấy base URL dựa trên side
        base_url = get_base_url_for_side(is_left)
        side_name = "trái" if is_left else "phải"
        
        # Chuyển đổi data thành bit flags giống như CAN
        flags = [0] * 18
        for i in data:
            flags[i - 1] = 1
        
        flag1 = flags[:8][::-1]
        flag2 = flags[8:16][::-1]
        flag3 = flags[16:][::-1]
        
        flag1 = ''.join(str(b) for b in flag1)
        flag2 = ''.join(str(b) for b in flag2)
        flag3 = ''.join(str(b) for b in flag3)
        
        flag1 = int(flag1, 2)
        flag2 = int(flag2, 2)
        flag3 = int(flag3, 2)
        
        # Tạo payload JSON thay vì CAN message
        payload = {
            "idx": idx,
            "flag1": flag1,
            "flag2": flag2,
            "flag3": flag3,
            "positions": data  # Gửi cả danh sách vị trí để dễ debug
        }
        
        # Gửi HTTP POST request với retry logic
        url = f"{base_url}{ENDPOINT_LAUNCH_COMMAND}"
        
        for attempt in range(WEBHOOK_MAX_RETRIES):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=WEBHOOK_TIMEOUT
                )
                
                if response.status_code == 200:
                    success_msg = f"Gửi lệnh phóng pháo {side_name} thành công: idx={idx}, positions={data}"
                    print(success_msg)
                    try:
                        LogTab.log(success_msg, "SUCCESS")
                    except:
                        pass
                    return True
                else:
                    error_msg = f"Lỗi webhook pháo {side_name}: Server trả về status {response.status_code}"
                    print(error_msg)
                    if attempt == WEBHOOK_MAX_RETRIES - 1:
                        try:
                            LogTab.log(error_msg, "ERROR")
                        except:
                            pass
                        return False
                    
            except requests.exceptions.Timeout:
                error_msg = f"Timeout khi gửi webhook pháo {side_name} (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES})"
                print(error_msg)
                if attempt == WEBHOOK_MAX_RETRIES - 1:
                    try:
                        LogTab.log(error_msg, "ERROR")
                    except:
                        pass
                    return False
                    
            except requests.exceptions.ConnectionError:
                error_msg = f"Không thể kết nối đến pháo {side_name} tại {url} (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES})"
                print(error_msg)
                if attempt == WEBHOOK_MAX_RETRIES - 1:
                    try:
                        LogTab.log(error_msg, "ERROR")
                    except:
                        pass
                    return False
            
            # Đợi trước khi retry
            if attempt < WEBHOOK_MAX_RETRIES - 1:
                time.sleep(WEBHOOK_RETRY_DELAY)
        
        return False
        
    except Exception as e:
        error_msg = f"Lỗi không xác định khi gửi webhook: {e}"
        print(error_msg)
        try:
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return False


def sender_angle_direction(angle, direction, is_left=True):
    """
    Gửi dữ liệu góc và hướng qua webhook.
    
    Args:
        angle: Góc (int, đơn vị 0.1 độ)
        direction: Hướng (int, đơn vị 0.1 độ)
        is_left: True nếu gửi cho pháo trái, False cho pháo phải
        
    Returns:
        bool: True nếu gửi thành công, False nếu có lỗi
    """
    try:
        # Lấy base URL dựa trên side
        base_url = get_base_url_for_side(is_left)
        side_name = "trái" if is_left else "phải"
        
        # Tạo payload JSON
        payload = {
            "angle": angle,  # Đơn vị 0.1 độ
            "direction": direction,  # Đơn vị 0.1 độ
            "angle_degrees": angle / 10.0,  # Chuyển sang độ cho dễ đọc
            "direction_degrees": direction / 10.0
        }
        
        # Gửi HTTP POST request với retry logic
        url = f"{base_url}{ENDPOINT_ANGLE_COMMAND}"
        
        for attempt in range(WEBHOOK_MAX_RETRIES):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=WEBHOOK_TIMEOUT
                )
                
                if response.status_code == 200:
                    success_msg = f"Gửi góc pháo {side_name} thành công: Góc {angle/10:.1f}°, Hướng {direction/10:.1f}°"
                    print(success_msg)
                    try:
                        LogTab.log(success_msg, "INFO")
                    except:
                        pass
                    return True
                else:
                    error_msg = f"Lỗi webhook pháo {side_name}: Server trả về status {response.status_code}"
                    print(error_msg)
                    if attempt == WEBHOOK_MAX_RETRIES - 1:
                        try:
                            LogTab.log(error_msg, "ERROR")
                        except:
                            pass
                        return False
                    
            except requests.exceptions.Timeout:
                error_msg = f"Timeout khi gửi webhook pháo {side_name} (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES})"
                print(error_msg)
                if attempt == WEBHOOK_MAX_RETRIES - 1:
                    try:
                        LogTab.log(error_msg, "ERROR")
                    except:
                        pass
                    return False
                    
            except requests.exceptions.ConnectionError:
                error_msg = f"Không thể kết nối đến pháo {side_name} tại {url} (attempt {attempt + 1}/{WEBHOOK_MAX_RETRIES})"
                print(error_msg)
                if attempt == WEBHOOK_MAX_RETRIES - 1:
                    try:
                        LogTab.log(error_msg, "ERROR")
                    except:
                        pass
                    return False
            
            # Đợi trước khi retry
            if attempt < WEBHOOK_MAX_RETRIES - 1:
                time.sleep(WEBHOOK_RETRY_DELAY)
        
        return False
        
    except Exception as e:
        error_msg = f"Lỗi không xác định khi gửi webhook: {e}"
        print(error_msg)
        try:
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return False