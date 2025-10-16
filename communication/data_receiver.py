from random import random
import can
import struct
import ui.ui_config as config
from functools import reduce
from operator import or_
import can
import struct
import ui.ui_config as config
import math
import numpy as np
import pandas as pd
import os
from typing import List

# Thêm các lớp từ targeting system
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
        
        # Lấy vị trí của quang điện tử
        optoelectronic_pos = self.ship.get_optoelectronic()
        
        # Tính toán tọa độ x, y của mục tiêu
        target_x = optoelectronic_pos.x + distance_optoelectronic * math.sin(azimuth_rad)
        target_y = optoelectronic_pos.y + distance_optoelectronic * math.cos(azimuth_rad)
        
        return Point2D(target_x, target_y)

    def calculate_firing_solutions(self, target_position: Point2D) -> dict:
        """Tính toán giải pháp bắn cho từng khẩu pháo."""
        solutions = {}
        
        for cannon_name, cannon_pos in self.ship.get_cannons():
            # Tính khoảng cách từ pháo đến mục tiêu
            distance_to_target = cannon_pos.distance(target_position)
            
            # Tính góc hướng của mục tiêu so với pháo
            delta_x = target_position.x - cannon_pos.x
            delta_y = target_position.y - cannon_pos.y
            
            # Tính góc bằng atan2 để xử lý đúng các góc phần tư
            azimuth_rad = math.atan2(delta_x, delta_y)
            azimuth_deg = math.degrees(azimuth_rad)
            
            # Đảm bảo góc hướng nằm trong khoảng -180 đến 180 độ
            if azimuth_deg > 180:
                azimuth_deg -= 360
            elif azimuth_deg < -180:
                azimuth_deg += 360
            
            # Nội suy góc tầm từ bảng bắn
            elevation_angle_deg = self.interpolator.interpolate_angle(distance_to_target)
            
            # Chuyển đổi sang float tiêu chuẩn của Python
            solutions[f"{cannon_name}_distance"] = float(distance_to_target)
            solutions[f"{cannon_name}_azimuth"] = float(azimuth_deg)
            solutions[f"{cannon_name}_elevation"] = float(elevation_angle_deg)
            
        return solutions

def load_firing_table_from_csv(csv_path: str = "table1.csv"):
    """Đọc bảng bắn từ file CSV.
    
    Args:
        csv_path: Đường dẫn đến file CSV (mặc định: "table1.csv")
        
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
        
        print(f"Đã đọc {len(range_data)} điểm dữ liệu từ {csv_path}")
        return range_data, angle_data
        
    except FileNotFoundError:
        print(f"Không tìm thấy file {csv_path}, sử dụng dữ liệu mặc định")
    except Exception as e:
        print(f"Lỗi đọc file CSV: {e}, sử dụng dữ liệu mặc định")

def unpack_bits(n: int, width: int) -> List[bool]:
    return [bool((n>>i) & 1) for i in range(0, width)]

# Khởi tạo targeting system
ship = Ship()
range_data, angle_data = load_firing_table_from_csv()
interpolator = FiringTableInterpolator(range_data, angle_data)
targeting_system = TargetingSystem(ship, interpolator)

def run():
    distance, direction = 9000, 36
    distance = random.uniform(4000, 5000)  # Giả lập khoảng cách đến mục tiêu (m)
    
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
    print("Listening on can0...")
    try:
        for msg in bus:
            print(msg)
            if msg.arbitration_id == 0x100:
                if len(msg.data) == 4:
                    (distance,) = struct.unpack("<f", msg.data)
                    print(f"Received: ID=0x100, Distance: {distance:.2f} km")
                else:
                    print(f"Lỗi: ID=0x100, nhận {len(msg.data)} bytes, cần 4 bytes")
            if msg.arbitration_id == 0x102:
                if len(msg.data) == 4:
                    (direction,) = struct.unpack("<f", msg.data)
                    print(f"Received: ID=0x102, Direction: {direction:.2f}°")
                else:
                    print(f"Lỗi: ID=0x102, nhận {len(msg.data)} bytes, cần 4 bytes")
            
            target_position = targeting_system.calculate_target_position(distance, direction)
            
            # Tính toán giải pháp bắn
            solutions = targeting_system.calculate_firing_solutions(target_position)
            
            # Chỉ cập nhật khoảng cách và hướng từ CAN bus
            # Góc tầm sẽ được tính liên tục trong UI loop
            config.DISTANCE_L = solutions["cannon_1_distance"]
            config.DIRECTION_L = solutions["cannon_1_azimuth"]
            
            config.DISTANCE_R = solutions["cannon_2_distance"]
            config.DIRECTION_R = solutions["cannon_2_azimuth"]
            
            print(f"Updated config - L: dist={config.DISTANCE_L:.2f}, dir={config.DIRECTION_L:.2f}")
            print(f"Updated config - R: dist={config.DISTANCE_R:.2f}, dir={config.DIRECTION_R:.2f}")

            # Nhận góc hiện tại của pháo từ CAN bus (góc từ cảm biến)
            # TODO: Thay đổi arbitration_id theo hệ thống thực tế của bạn
            if msg.arbitration_id == 0x200:  # Góc pháo trái
                if len(msg.data) == 8:
                    angle, direction = struct.unpack("<ff", msg.data)
                    config.ANGLE_L = angle  # Góc hiện tại từ cảm biến
                    config.DIRECTION_L = direction  # Hướng hiện tại từ cảm biến
                    print(f"Received cannon_left - angle: {angle:.2f}°, direction: {direction:.2f}°")
            
            if msg.arbitration_id == 0x201:  # Góc pháo phải
                if len(msg.data) == 8:
                    angle, direction = struct.unpack("<ff", msg.data)
                    config.ANGLE_R = angle  # Góc hiện tại từ cảm biến
                    config.DIRECTION_R = direction  # Hướng hiện tại từ cảm biến
                    print(f"Received cannon_right - angle: {angle:.2f}°, direction: {direction:.2f}°")

            if msg.arbitration_id == 0x99:
                #if can't run change msg['data'] to msg.data
                data = msg.data
                print(data)
                
                flag1 = unpack_bits(data[2], 8)
                flag2 = unpack_bits(data[3], 8)
                flag3 = unpack_bits(data[4], 2)
                flags = flag1 + flag2 + flag3
                if data[1] == 0x31:
                    config.AMMO_L = flags
                elif data[1] == 0x32:
                    config.AMMO_R = flags
                else:
                    raise ValueError(f"Unknown side code: {data[1]:#x}")
                print(f"Ammo L: {config.AMMO_L}")
                print(f"Ammo R: {config.AMMO_R}")
                        
    except KeyboardInterrupt:
        print("Stopped receiving")
