# -*- coding: utf-8 -*-
"""
Webhook Data Receiver (Jetson1)
================================
Nhận dữ liệu từ Jetson2 qua HTTP webhook thay vì CAN bus.
Jetson1 chạy Flask server để nhận dữ liệu từ Jetson2.
"""

from flask import Flask, request, jsonify
import threading
import struct
import ui.ui_config as config
import math
import numpy as np
import pandas as pd
import os
import serial
from typing import List
from communication.webhook_config import (
    JETSON1_HOST,
    JETSON1_PORT,
    ENDPOINT_DISTANCE,
    ENDPOINT_DIRECTION,
    ENDPOINT_CANNON_LEFT,
    ENDPOINT_CANNON_RIGHT,
    ENDPOINT_AMMO_STATUS,
    ENDPOINT_MODULE_DATA,
    SIDE_CODE_LEFT,
    SIDE_CODE_RIGHT,
    COMPASS_PORT,
    COMPASS_BAUDRATE,
    COMPASS_TIMEOUT
)

# Import các lớp từ targeting system (giữ nguyên)
class Point2D:
    """Lớp biểu diễn điểm trong không gian 2D."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance(self, other: 'Point2D') -> float:
        """Tính khoảng cách đến một điểm khác."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"


class Ship:
    def __init__(self, length: float = 30, width: float = 10):
        self.length = length
        self.width = width
        
        # Quang điện tử (điểm A) 
        self.optoelectronic = Point2D(width/4, 0)
        
        # Pháo B và C 
        self.cannon_1 = Point2D(-width/2, length/4)  # Pháo bên trái (B)
        self.cannon_2 = Point2D(width/2, length/4)   # Pháo bên phải (C)
    
    def get_optoelectronic(self) -> Point2D:
        """Trả về vị trí của quang điện tử."""
        return self.optoelectronic
    
    def get_cannons(self) -> List[tuple]:
        """Trả về vị trí của các khẩu pháo."""
        return [("cannon_1", self.cannon_1), ("cannon_2", self.cannon_2)]


class FiringTableInterpolator:
    """Nội suy bảng bắn để tìm góc tầm cho một khoảng cách."""
    
    def __init__(self, ranges: np.ndarray, angles: np.ndarray):
        if len(ranges) != len(angles):
            raise ValueError("Số lượng khoảng cách và góc tầm phải bằng nhau.")
        self.ranges = np.array(ranges)
        self.angles = np.array(angles)
        # Đảm bảo các khoảng cách được sắp xếp tăng dần
        sort_indices = np.argsort(self.ranges)
        self.ranges = self.ranges[sort_indices]
        self.angles = self.angles[sort_indices]

    def interpolate_angle(self, target_range: float) -> float:
        """Nội suy góc tầm cho một khoảng cách mục tiêu."""
        if target_range < self.ranges[0] or target_range > self.ranges[-1]:
            # Ngoại suy tuyến tính cho các giá trị ngoài cùng
            if target_range < self.ranges[0]:
                return np.interp(target_range, self.ranges[:2], self.angles[:2])
            else:
                return np.interp(target_range, self.ranges[-2:], self.angles[-2:])

        return np.interp(target_range, self.ranges, self.angles)


class TargetingSystem:
    """Hệ thống nhắm mục tiêu tính toán giải pháp bắn."""

    def __init__(self, ship: Ship, interpolator: FiringTableInterpolator):
        self.ship = ship
        self.interpolator = interpolator

    def calculate_target_position(self, distance_optoelectronic: float, azimuth_optoelectronic_deg: float) -> Point2D:
        """Tính toán vị trí mục tiêu dựa trên dữ liệu từ quang điện tử."""
        # Chuyển góc hướng từ độ sang radian
        azimuth_rad = math.radians(azimuth_optoelectronic_deg)
        
        # Vị trí quang điện tử
        A = self.ship.get_optoelectronic()
        
        # Tính toán vị trí mục tiêu T
        T_x = A.x + distance_optoelectronic * math.sin(azimuth_rad)
        T_y = A.y + distance_optoelectronic * math.cos(azimuth_rad)
        
        return Point2D(T_x, T_y)

    def calculate_firing_solution(self, target: Point2D) -> dict:
        """Tính toán giải pháp bắn cho cả hai khẩu pháo."""
        solutions = {}
        
        for cannon_name, cannon_pos in self.ship.get_cannons():
            # Khoảng cách từ pháo đến mục tiêu
            distance = cannon_pos.distance(target)
            
            # Góc tầm từ bảng bắn
            range_angle_deg = self.interpolator.interpolate_angle(distance)
            
            # Góc hướng (azimuth) từ pháo đến mục tiêu
            delta_x = target.x - cannon_pos.x
            delta_y = target.y - cannon_pos.y
            azimuth_rad = math.atan2(delta_x, delta_y)
            azimuth_deg = math.degrees(azimuth_rad)
            
            # Chuẩn hóa góc hướng về khoảng [0, 360)
            if azimuth_deg < 0:
                azimuth_deg += 360
            
            solutions[cannon_name] = {
                "distance": distance,
                "range_angle": range_angle_deg,
                "azimuth": azimuth_deg,
                "position": cannon_pos
            }
        
        return solutions


def load_firing_table_from_csv(csv_path: str = "table1.csv") -> tuple:
    """
    Đọc bảng bắn từ file CSV.
    
    Returns:
        Tuple chứa hai mảng (khoảng cách, góc tầm)
    """
    try:
        # Đọc file CSV
        df = pd.read_csv(csv_path)
        
        # Kiểm tra các cột cần thiết (X là khoảng cách, P là góc tầm)
        if 'X' not in df.columns or 'P' not in df.columns:
            raise ValueError("File CSV phải có cột 'X' và 'P'")
        
        # Chuyển đổi sang numpy array (X là range, P là angle)
        range_data = df['X'].values
        angle_data = df['P'].values
        
        print(f"✓ Đã đọc {len(range_data)} điểm dữ liệu từ {csv_path}")
        return range_data, angle_data
        
    except FileNotFoundError:
        print(f"⚠ Không tìm thấy file {csv_path}, sử dụng dữ liệu mặc định")
        # Bảng bắn mẫu
        default_ranges = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
        default_angles = np.array([5, 10, 15, 20, 25, 30, 35, 40, 42, 45])
        return default_ranges, default_angles
    except Exception as e:
        print(f"⚠ Lỗi đọc file CSV: {e}, sử dụng dữ liệu mặc định")
        # Bảng bắn mẫu
        default_ranges = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
        default_angles = np.array([5, 10, 15, 20, 25, 30, 35, 40, 42, 45])
        return default_ranges, default_angles


def extract_heading(data):
    """Trích xuất heading từ dữ liệu compass."""
    if data[0] == 0x68 and data[-1] == 0x16:
        heading_str = data[7:11]
        heading = float(heading_str)
        return heading
    return 0.0


def unpack_bits(byte_value, num_bits):
    """Giải nén bits từ byte."""
    return [(byte_value >> i) & 1 for i in range(num_bits)]


# Khởi tạo Flask app
app = Flask(__name__)

# Khởi tạo targeting system
ship = Ship()
range_data, angle_data = load_firing_table_from_csv()
interpolator = FiringTableInterpolator(range_data, angle_data)
targeting_system = TargetingSystem(ship, interpolator)


# =============================================================================
# Targeting Calculation Helper
# =============================================================================

def calculate_targeting_solution(distance, direction):
    """
    Tính toán giải pháp bắn dựa trên khoảng cách và hướng.
    Chỉ cập nhật khi ở chế độ tự động.
    """
    try:
        if distance <= 0 or direction < 0:
            return  # Skip nếu dữ liệu không hợp lệ
        
        # Tính toán vị trí mục tiêu
        target_position = targeting_system.calculate_target_position(distance, direction)
        
        # Tính toán giải pháp bắn
        solutions = targeting_system.calculate_firing_solution(target_position)
        
        # Chỉ cập nhật khoảng cách và hướng KHI Ở CHẾ ĐỘ TỰ ĐỘNG
        # Góc tầm sẽ được tính liên tục trong UI loop
        
        # Giàn trái - chỉ cập nhật khi ở chế độ tự động
        if config.DISTANCE_MODE_AUTO_L:
            config.DISTANCE_L = solutions["cannon_1"]["distance"]
        if config.DIRECTION_MODE_AUTO_L:
            config.AIM_DIRECTION_L = solutions["cannon_1"]["azimuth"]
        
        # Giàn phải - chỉ cập nhật khi ở chế độ tự động
        if config.DISTANCE_MODE_AUTO_R:
            config.DISTANCE_R = solutions["cannon_2"]["distance"]
        if config.DIRECTION_MODE_AUTO_R:
            config.AIM_DIRECTION_R = solutions["cannon_2"]["azimuth"]
        
        mode_l_dist = "AUTO" if config.DISTANCE_MODE_AUTO_L else "MANUAL"
        mode_r_dist = "AUTO" if config.DISTANCE_MODE_AUTO_R else "MANUAL"
        mode_l_dir = "AUTO" if config.DIRECTION_MODE_AUTO_L else "MANUAL"
        mode_r_dir = "AUTO" if config.DIRECTION_MODE_AUTO_R else "MANUAL"
        
        # Log thông tin tính toán targeting
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(
                f"Tính toán targeting - Trái: KC={config.DISTANCE_L:.1f}m ({mode_l_dist}), Hướng={config.AIM_DIRECTION_L:.1f}° ({mode_l_dir}) | "
                f"Phải: KC={config.DISTANCE_R:.1f}m ({mode_r_dist}), Hướng={config.AIM_DIRECTION_R:.1f}° ({mode_r_dir})",
                "INFO"
            )
        except:
            pass
            
    except Exception as e:
        error_msg = f"Lỗi tính toán targeting: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass


# =============================================================================
# Webhook Endpoints - Nhận dữ liệu từ Jetson Left/Right/3
# =============================================================================

@app.route('/api/target', methods=['POST'])
def receive_target_data():
    """Nhận dữ liệu mục tiêu (distance + direction) từ quang điện tử (Jetson3) và tính toán giải pháp bắn."""
    try:
        data = request.get_json()
        distance = data.get('distance', 0.0)
        direction = data.get('direction', 0.0)
        
        print(f"Webhook - Nhận mục tiêu: Khoảng cách={distance:.2f}m, Hướng={direction:.2f}°")
        
        # Log vào event log
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Nhận Webhook - Mục tiêu: KC={distance:.2f}m, Hướng={direction:.2f}°", "INFO")
        except:
            pass
        
        # Tính toán targeting solution và cập nhật config
        calculate_targeting_solution(distance, direction)
        
        return jsonify({
            "status": "success", 
            "distance": distance,
            "direction": direction,
            "solutions": {
                "left": {
                    "distance": config.DISTANCE_L,
                    "azimuth": config.AIM_DIRECTION_L
                },
                "right": {
                    "distance": config.DISTANCE_R,
                    "azimuth": config.AIM_DIRECTION_R
                }
            }
        }), 200
        
    except Exception as e:
        error_msg = f"Lỗi nhận dữ liệu mục tiêu: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route(ENDPOINT_CANNON_LEFT, methods=['POST'])
def receive_cannon_left():
    """Nhận góc hiện tại của pháo trái."""
    try:
        data = request.get_json()
        angle = data.get('angle', 0.0)
        direction = data.get('direction', 0.0)
        
        config.ANGLE_L = angle
        config.DIRECTION_L = direction
        print(f"Webhook - Pháo Trái: Góc={angle:.2f}°, Hướng={direction:.2f}°")
        
        # Log vào event log
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Nhận Webhook - Pháo Trái: Góc={angle:.2f}°, Hướng={direction:.2f}°", "INFO")
        except:
            pass
        
        return jsonify({"status": "success", "angle": angle, "direction": direction}), 200
        
    except Exception as e:
        error_msg = f"Lỗi nhận pháo trái: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route(ENDPOINT_CANNON_RIGHT, methods=['POST'])
def receive_cannon_right():
    """Nhận góc hiện tại của pháo phải."""
    try:
        data = request.get_json()
        angle = data.get('angle', 0.0)
        direction = data.get('direction', 0.0)
        
        config.ANGLE_R = angle
        config.DIRECTION_R = direction
        print(f"Webhook - Pháo Phải: Góc={angle:.2f}°, Hướng={direction:.2f}°")
        
        # Log vào event log
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Nhận Webhook - Pháo Phải: Góc={angle:.2f}°, Hướng={direction:.2f}°", "INFO")
        except:
            pass
        
        return jsonify({"status": "success", "angle": angle, "direction": direction}), 200
        
    except Exception as e:
        error_msg = f"Lỗi nhận pháo phải: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route(ENDPOINT_AMMO_STATUS, methods=['POST'])
def receive_ammo_status():
    """Nhận trạng thái đạn."""
    try:
        data = request.get_json()
        side_code = data.get('side_code')
        flags = data.get('flags', [])
        
        if side_code == SIDE_CODE_LEFT:
            config.AMMO_L = flags
            side_name = "Giàn Trái"
        elif side_code == SIDE_CODE_RIGHT:
            config.AMMO_R = flags
            side_name = "Giàn Phải"
        else:
            return jsonify({"status": "error", "message": "Invalid side_code"}), 400
        
        ammo_count = sum(flags)
        print(f"Webhook - {side_name}: Trạng thái đạn {ammo_count}/18 sẵn sàng")
        
        # Log vào event log
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Nhận Webhook - {side_name}: Trạng thái đạn {ammo_count}/18 sẵn sàng", "INFO")
        except:
            pass
        
        return jsonify({"status": "success", "side": side_name, "ammo_count": ammo_count}), 200
        
    except Exception as e:
        error_msg = f"Lỗi nhận trạng thái đạn: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route(ENDPOINT_MODULE_DATA, methods=['POST'])
def receive_module_data():
    """Nhận dữ liệu module (điện áp, dòng điện, công suất, nhiệt độ)."""
    try:
        data = request.get_json()
        node_id = data.get('node_id')
        module_index = data.get('module_index')
        voltage = data.get('voltage', 0.0)
        current = data.get('current', 0.0)
        power = data.get('power', 0.0)
        temperature = data.get('temperature', 0.0)
        
        # Cập nhật vào hệ thống
        from data_management.module_data_manager import update_module_data
        update_module_data(node_id, module_index, voltage, current, power, temperature)
        
        print(f"Webhook - Module [{node_id}][{module_index}]: V={voltage:.2f}V, I={current:.2f}A, P={power:.1f}W, T={temperature}°C")
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        error_msg = f"Lỗi nhận module data: {e}"
        print(error_msg)
        return jsonify({"status": "error", "message": str(e)}), 400


# =============================================================================
# Compass Reader (giữ nguyên như cũ)
# =============================================================================

def compass_reader():
    """Đọc dữ liệu từ compass qua Serial (giữ nguyên)."""
    try:
        Com_Compass = serial.Serial(COMPASS_PORT, COMPASS_BAUDRATE, timeout=COMPASS_TIMEOUT)
        print(f"✓ Compass reader đã khởi động trên {COMPASS_PORT}")
        
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Compass reader đã khởi động thành công trên {COMPASS_PORT}", "SUCCESS")
        except:
            pass
        
        while True:
            if Com_Compass.in_waiting >= 19:
                data_Compass = Com_Compass.read(19)
                data_CP = extract_heading(data_Compass)
                config.W_DIRECTION = data_CP
                print(f"Compass: {data_CP:.2f}°")
                
    except serial.SerialException as e:
        error_msg = f"Lỗi Compass: Không thể mở {COMPASS_PORT}. Compass reader sẽ không hoạt động. Chi tiết: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
    except Exception as e:
        error_msg = f"Lỗi không xác định trong compass reader: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
    finally:
        if 'Com_Compass' in locals():
            Com_Compass.close()
            print("Compass serial port đã được đóng")


# =============================================================================
# Main Run Function
# =============================================================================

def run():
    """
    Khởi động webhook receiver server và compass reader.
    Gọi hàm này trong thread để không block main UI.
    """
    # Start compass reader in separate thread
    compass_thread = threading.Thread(target=compass_reader, daemon=True)
    compass_thread.start()
    
    # Start Flask webhook server
    print(f"✓ Khởi động Webhook Receiver Server trên {JETSON1_HOST}:{JETSON1_PORT}")
    try:
        from ui.tabs.event_log_tab import LogTab
        LogTab.log(f"Webhook Receiver Server đã khởi động trên port {JETSON1_PORT}", "SUCCESS")
    except:
        pass
    
    # Run Flask (use_reloader=False để tránh conflict với PyQt)
    app.run(host=JETSON1_HOST, port=JETSON1_PORT, debug=False, use_reloader=False)
