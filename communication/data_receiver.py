import random
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
import serial
import threading
from communication.can_bus_manager import can_bus_manager

# Import CAN configuration
from communication.can_config import (
    CAN_CHANNEL, CAN_BUSTYPE, CAN_BITRATE,
    CAN_ID_DISTANCE, CAN_ID_DIRECTION,
    CAN_ID_CANNON_LEFT, CAN_ID_CANNON_RIGHT,
    CAN_ID_AMMO_STATUS,
    CAN_ID_MODULE_DATA_START, CAN_ID_MODULE_DATA_END,
    SIDE_CODE_LEFT, SIDE_CODE_RIGHT,
    COMPASS_PORT, COMPASS_BAUDRATE, COMPASS_TIMEOUT,
    is_module_data_id
)

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

def extract_heading(binary_string: bytes) -> float:
    """Trích xuất giá trị hướng từ dữ liệu la bàn."""
    text = binary_string.decode(errors='ignore').strip()
    words = text.split(',')
    try:
        return float(words[1])
    except (ValueError, IndexError):
        print(f"Lỗi gói tin compass. Raw data: {binary_string}")
        return 0.0

def compass_reader_thread():
    """Thread đọc dữ liệu từ la bàn và cập nhật W_DIRECTION."""
    
    try:
        Com_Compass = serial.Serial(
            port=COMPASS_PORT, 
            timeout=COMPASS_TIMEOUT, 
            baudrate=COMPASS_BAUDRATE, 
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE, 
            stopbits=serial.STOPBITS_ONE
        )
        print(f"Compass reader đã khởi động thành công trên {COMPASS_PORT}")
        
        # Ghi log thành công
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

# Khởi tạo targeting system
ship = Ship()
range_data, angle_data = load_firing_table_from_csv()
interpolator = FiringTableInterpolator(range_data, angle_data)
targeting_system = TargetingSystem(ship, interpolator)

def parse_module_data_from_can(msg):
    """
    Parse CAN message để lấy thông số module.
    
    CAN Protocol:
    - CAN ID: CAN_ID_MODULE_DATA_START + node_index (0x300-0x32F)
    - Data format (8 bytes):
      [0]: Module index (0-255)
      [1-2]: Voltage (uint16, scale 0.01V → 0-655.35V)
      [3-4]: Current (uint16, scale 0.01A → 0-655.35A)
      [5-6]: Power (uint16, scale 0.1W → 0-6553.5W)
      [7]: Temperature (uint8, °C → 0-255°C)
    
    Returns:
        tuple: (node_id, module_index, voltage, current, power, temperature) hoặc None nếu invalid
    """
    try:
        # Check if CAN ID is in module data range
        if not is_module_data_id(msg.arbitration_id):
            return None
        
        # Check data length
        if len(msg.data) != 8:
            print(f"[CAN] Invalid module data length: {len(msg.data)} bytes (expected 8)")
            return None
        
        # Extract node index from CAN ID
        node_index = msg.arbitration_id - CAN_ID_MODULE_DATA_START
        
        # Parse data
        module_index = msg.data[0]
        voltage = struct.unpack(">H", msg.data[1:3])[0] * 0.01  # Big-endian uint16, scale 0.01
        current = struct.unpack(">H", msg.data[3:5])[0] * 0.01  # Big-endian uint16, scale 0.01
        power = struct.unpack(">H", msg.data[5:7])[0] * 0.1     # Big-endian uint16, scale 0.1
        temperature = msg.data[7]  # uint8
        
        # Get node_id from config
        from data_management.configuration_manager import get_node_id_from_index
        node_id = get_node_id_from_index(node_index)
        
        if node_id is None:
            print(f"[CAN] Unknown node index: {node_index}")
            return None
        
        return (node_id, module_index, voltage, current, power, temperature)
        
    except Exception as e:
        print(f"[CAN] Error parsing module data: {e}")
        return None


def update_module_from_can_message(node_id, module_index, voltage, current, power, temperature):
    """
    Cập nhật thông số module từ CAN message vào hệ thống.
    
    Args:
        node_id: ID của node (ví dụ: "bang_dien_chinh")
        module_index: Index của module trong node (0-based)
        voltage: Điện áp (V)
        current: Dòng điện (A)
        power: Công suất (W)
        temperature: Nhiệt độ (°C)
    """
    try:
        from data_management.module_data_manager import module_manager
        
        # Get all modules of the node
        node_modules = module_manager.get_node_modules(node_id)
        
        if not node_modules:
            print(f"[CAN] Node '{node_id}' has no modules")
            return False
        
        # Convert dict to list to access by index
        module_list = list(node_modules.values())
        
        if module_index >= len(module_list):
            print(f"[CAN] Module index {module_index} out of range for node '{node_id}' (has {len(module_list)} modules)")
            return False
        
        # Get the module at the specified index
        target_module = module_list[module_index]
        module_id = target_module.module_id
        
        # Update module parameters
        success = module_manager.update_module_parameters(
            node_id, 
            module_id,
            voltage=voltage,
            current=current,
            power=power,
            temperature=temperature
        )
        
        if success:
            print(f"[CAN] Updated {node_id}[{module_index}] {target_module.name}: V={voltage:.2f}V, I={current:.2f}A, P={power:.1f}W, T={temperature}°C")
        
        return success
        
    except Exception as e:
        print(f"[CAN] Error updating module: {e}")
        return False


def run():
    # Khởi động thread đọc la bàn
    compass_thread = threading.Thread(target=compass_reader_thread, daemon=True)
    compass_thread.start()
    
    try:
        # Sử dụng bus chung từ manager thay vì tạo mới
        bus = can_bus_manager.get_bus()
        print(f"Listening on {CAN_CHANNEL}...")
        # Ghi log thành công (đã log trong can_bus_manager)
    except OSError as e:
        if e.errno == 19:  # No such device
            error_msg = f"Lỗi CAN: Không tìm thấy thiết bị '{CAN_CHANNEL}'. CAN receiver sẽ không hoạt động."
            print(error_msg)
            # Ghi log vào event log
            try:
                from ui.tabs.event_log_tab import LogTab
                LogTab.log(error_msg, "ERROR")
            except:
                pass
        else:
            error_msg = f"Lỗi CAN OSError: {e}"
            print(error_msg)
            try:
                from ui.tabs.event_log_tab import LogTab
                LogTab.log(error_msg, "ERROR")
            except:
                pass
        return  # Thoát hàm nếu không thể khởi tạo CAN bus
    except Exception as e:
        error_msg = f"Lỗi không xác định khi khởi tạo CAN bus: {e}"
        print(error_msg)
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(error_msg, "ERROR")
        except:
            pass
        return
    
    # Khởi tạo biến distance và direction
    distance = 0.0
    direction = 0.0
    
    try:
        while True:
            msg = bus.recv(timeout=1.0)  # Timeout 1 giây
            if msg is None:
                continue
            
            # Parse module data (CAN ID 0x300-0x32F)
            module_data = parse_module_data_from_can(msg)
            if module_data:
                node_id, module_index, voltage, current, power, temperature = module_data
                success = update_module_from_can_message(node_id, module_index, voltage, current, power, temperature)
                # Log vào lịch sử
                try:
                    from ui.tabs.event_log_tab import LogTab
                    if success:
                        LogTab.log(f"Nhận CAN data - ID=0x{msg.arbitration_id:03X} ({node_id}[{module_index}]): V={voltage:.2f}V, I={current:.2f}A, P={power:.1f}W, T={temperature}°C", "INFO")
                    else:
                        LogTab.log(f"Lỗi cập nhật module từ CAN data - ID=0x{msg.arbitration_id:03X}: {node_id}[{module_index}]", "ERROR")
                except:
                    pass
                continue  # Skip other processing for module data messages
            
            if msg.arbitration_id == CAN_ID_DISTANCE:
                if len(msg.data) == 4:
                    (distance_tmp,) = struct.unpack("<f", msg.data)
                    if distance_tmp > 0:
                        distance = distance_tmp
                    print(f"Received: ID=0x{CAN_ID_DISTANCE:X}, Distance: {distance:.2f} km")
                    # Log vào lịch sử
                    try:
                        from ui.tabs.event_log_tab import LogTab
                        LogTab.log(f"Nhận CAN data - ID=0x{CAN_ID_DISTANCE:X}: Khoảng cách = {distance:.2f} km", "INFO")
                    except:
                        pass
                else:
                    print(f"Lỗi: ID=0x{CAN_ID_DISTANCE:X}, nhận {len(msg.data)} bytes, cần 4 bytes")
                    try:
                        from ui.tabs.event_log_tab import LogTab
                        LogTab.log(f"Lỗi CAN data - ID=0x{CAN_ID_DISTANCE:X}: nhận {len(msg.data)} bytes, cần 4 bytes", "ERROR")
                    except:
                        pass
            if msg.arbitration_id == CAN_ID_DIRECTION:
                if len(msg.data) == 4:
                    (direction,) = struct.unpack("<f", msg.data)
                    print(f"Received: ID=0x{CAN_ID_DIRECTION:X}, Direction: {direction:.2f}°")
                    # Log vào lịch sử
                    try:
                        from ui.tabs.event_log_tab import LogTab
                        LogTab.log(f"Nhận CAN data - ID=0x{CAN_ID_DIRECTION:X}: Hướng = {direction:.2f}°", "INFO")
                    except:
                        pass
                else:
                    print(f"Lỗi: ID=0x{CAN_ID_DIRECTION:X}, nhận {len(msg.data)} bytes, cần 4 bytes")
                    try:
                        from ui.tabs.event_log_tab import LogTab
                        LogTab.log(f"Lỗi CAN data - ID=0x{CAN_ID_DIRECTION:X}: nhận {len(msg.data)} bytes, cần 4 bytes", "ERROR")
                    except:
                        pass
            
            # Chỉ tính toán targeting khi nhận được CAN_ID_DISTANCE hoặc CAN_ID_DIRECTION
            # và ít nhất một bên đang ở chế độ tự động
            if msg.arbitration_id in [CAN_ID_DISTANCE, CAN_ID_DIRECTION]:
                target_position = targeting_system.calculate_target_position(distance, direction)
                
                # Tính toán giải pháp bắn
                solutions = targeting_system.calculate_firing_solutions(target_position)
                
                # Chỉ cập nhật khoảng cách và hướng từ CAN bus KHI Ở CHẾ ĐỘ TỰ ĐỘNG
                # Góc tầm sẽ được tính liên tục trong UI loop
                
                # Giàn trái - chỉ cập nhật khi ở chế độ tự động
                if config.DISTANCE_MODE_AUTO_L:
                    config.DISTANCE_L = solutions["cannon_1_distance"]
                if config.DIRECTION_MODE_AUTO_L:
                    config.AIM_DIRECTION_L = solutions["cannon_1_azimuth"]
                
                # Giàn phải - chỉ cập nhật khi ở chế độ tự động
                if config.DISTANCE_MODE_AUTO_R:
                    config.DISTANCE_R = solutions["cannon_2_distance"]
                if config.DIRECTION_MODE_AUTO_R:
                    config.AIM_DIRECTION_R = solutions["cannon_2_azimuth"]
                
                mode_l_dist = "AUTO" if config.DISTANCE_MODE_AUTO_L else "MANUAL"
                mode_r_dist = "AUTO" if config.DISTANCE_MODE_AUTO_R else "MANUAL"
                mode_l_dir = "AUTO" if config.DIRECTION_MODE_AUTO_L else "MANUAL"
                mode_r_dir = "AUTO" if config.DIRECTION_MODE_AUTO_R else "MANUAL"
                try:
                    from ui.tabs.event_log_tab import LogTab
                    LogTab.log(
                        f"Tính toán giải pháp bắn: Mục tiêu tại {target_position}, "
                        f"Giàn trái [Khoảng cách: {config.DISTANCE_L:.2f} km ({mode_l_dist}), Hướng: {config.AIM_DIRECTION_L:.2f}° ({mode_l_dir})], "
                        f"Giàn phải [Khoảng cách: {config.DISTANCE_R:.2f} km ({mode_r_dist}), Hướng: {config.AIM_DIRECTION_R:.2f}° ({mode_r_dir})]",
                        "INFO"
                    )
                except:
                    pass
            # Nhận góc hiện tại của pháo từ CAN bus (góc từ cảm biến)
            if msg.arbitration_id == CAN_ID_CANNON_LEFT:  # Góc pháo trái
                if len(msg.data) == 8:
                    angle, direction = struct.unpack("<ff", msg.data)
                    config.ANGLE_L = angle  # Góc hiện tại từ cảm biến
                    config.DIRECTION_L = direction  # Hướng hiện tại từ cảm biến
                    print(f"Received cannon_left - angle: {angle:.2f}°, direction: {direction:.2f}°")
                    # Log vào lịch sử
                    try:
                        from ui.tabs.event_log_tab import LogTab
                        LogTab.log(f"Nhận CAN data - ID=0x{CAN_ID_CANNON_LEFT:X} (Pháo trái): Góc tầm={angle:.2f}°, Hướng={direction:.2f}°", "INFO")
                    except:
                        pass
            
            if msg.arbitration_id == CAN_ID_CANNON_RIGHT:  # Góc pháo phải
                if len(msg.data) == 8:
                    angle, direction = struct.unpack("<ff", msg.data)
                    config.ANGLE_R = angle  # Góc hiện tại từ cảm biến
                    config.DIRECTION_R = direction  # Hướng hiện tại từ cảm biến
                    print(f"Received cannon_right - angle: {angle:.2f}°, direction: {direction:.2f}°")
                    # Log vào lịch sử
                    try:
                        from ui.tabs.event_log_tab import LogTab
                        LogTab.log(f"Nhận CAN data - ID=0x{CAN_ID_CANNON_RIGHT:X} (Pháo phải): Góc tầm={angle:.2f}°, Hướng={direction:.2f}°", "INFO")
                    except:
                        pass

            if msg.arbitration_id == CAN_ID_AMMO_STATUS:
                #if can't run change msg['data'] to msg.data
                data = msg.data
                print(data)
                
                flag1 = unpack_bits(data[2], 8)
                flag2 = unpack_bits(data[3], 8)
                flag3 = unpack_bits(data[4], 2)
                flags = flag1 + flag2 + flag3
                if data[1] == SIDE_CODE_LEFT:
                    config.AMMO_L = flags
                    side_name = "Giàn trái"
                elif data[1] == SIDE_CODE_RIGHT:
                    config.AMMO_R = flags
                    side_name = "Giàn phải"
                else:
                    raise ValueError(f"Unknown side code: {data[1]:#x}")
                print(f"Ammo L: {config.AMMO_L}")
                print(f"Ammo R: {config.AMMO_R}")
                # Log vào lịch sử
                try:
                    from ui.tabs.event_log_tab import LogTab
                    ammo_count = sum(flags)
                    LogTab.log(f"Nhận CAN data - ID=0x{CAN_ID_AMMO_STATUS:X} ({side_name}): Cập nhật trạng thái đạn ({ammo_count}/18 sẵn sàng)", "INFO")
                except:
                    pass
                        
    except KeyboardInterrupt:
        print("Stopped receiving")
    except Exception as e:
        print(f"Lỗi khi nhận dữ liệu CAN: {e}")
        try:
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Lỗi khi nhận dữ liệu CAN: {e}", "ERROR")
        except:
            pass
    # KHÔNG shutdown bus ở đây - bus được quản lý bởi can_bus_manager
