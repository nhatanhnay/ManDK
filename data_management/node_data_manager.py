"""
Module quản lý dữ liệu của các node trong hệ thống fire control.
Mỗi node có thông tin điện áp theo thời gian, thông báo lỗi và mã lỗi.
"""

import time
import random
from typing import Dict, List, Any
from datetime import datetime

class NodeData:
    """Class lưu trữ dữ liệu của một node."""
    
    def __init__(self, node_id: str, name: str):
        self.node_id = node_id
        self.name = name
        self.voltage_history: List[Dict[str, Any]] = []
        self.error_messages: List[str] = []
        self.error_codes: List[str] = []
        self.has_error = False
        self.last_update = time.time()
        
    def add_voltage_reading(self, voltage: float):
        """Thêm đọc số điện áp mới."""
        timestamp = datetime.now()
        self.voltage_history.append({
            'timestamp': timestamp,
            'voltage': voltage,
            'time_seconds': time.time()
        })
        
        # Giữ lại 100 readings gần nhất
        if len(self.voltage_history) > 100:
            self.voltage_history.pop(0)
            
        self.last_update = time.time()
        
    def add_error(self, error_code: str, error_message: str):
        """Thêm lỗi mới."""
        self.error_codes.append(error_code)
        self.error_messages.append(error_message)
        self.has_error = True
        
        # Giữ lại 50 lỗi gần nhất
        if len(self.error_codes) > 50:
            self.error_codes.pop(0)
            self.error_messages.pop(0)
            
    def clear_errors(self):
        """Xóa tất cả lỗi."""
        self.error_codes.clear()
        self.error_messages.clear()
        self.has_error = False

    def update_error_status_from_modules(self):
        """Cập nhật trạng thái lỗi của node dựa trên trạng thái của các module."""
        try:
            from .module_data_manager import module_manager

            # Lấy tất cả modules của node này
            node_modules = module_manager.get_node_modules(self.node_id)

            # Kiểm tra xem có module nào có lỗi không
            has_module_errors = False
            for module in node_modules.values():
                if module.status == "error" or module.error_messages:
                    has_module_errors = True
                    break

            # Cập nhật trạng thái lỗi node
            if has_module_errors:
                self.has_error = True
            elif not has_module_errors and not self.error_messages:
                # Clear lỗi nếu không có lỗi module và không có lỗi node riêng
                self.has_error = False

        except ImportError:
            # Không thể import module_manager
            pass
        
    def get_current_voltage(self) -> float:
        """Lấy điện áp hiện tại."""
        if self.voltage_history:
            return self.voltage_history[-1]['voltage']
        return 0.0
        
    def get_latest_error(self) -> tuple:
        """Lấy lỗi mới nhất."""
        if self.error_codes and self.error_messages:
            return self.error_codes[-1], self.error_messages[-1]
        return None, None

class SystemDataManager:
    """Class quản lý dữ liệu của toàn bộ hệ thống."""
    
    def __init__(self):
        self.nodes: Dict[str, NodeData] = {}
        self._initialize_nodes()
        
    def _initialize_nodes(self):
        """Khởi tạo tất cả các node trong hệ thống."""
        # Khoang điều khiển tại chỗ 1
        compartment1_nodes = [
            ('ac_quy_1', 'Tủ ác quy'),
            ('phan_phoi_1', 'Tủ phân phối\nbiến đổi'),
            ('bien_ap_1', 'Tủ biến áp'),
            ('dan_dong_huong_1', 'Hộp dẫn động\nkềnh hướng'),
            ('dan_dong_tam_1', 'Hộp dẫn động\nkềnh tâm'),
            ('dieu_khien_1', 'Tủ điều khiển\ntại chỗ 1'),
            ('ban_dieu_khien_1', 'Bàn điều\nkhiển tại chỗ'),
            ('hn11', 'HN11'),
            ('hn12', 'HN12')
        ]
        
        # Khoang điều khiển giữa
        compartment2_nodes = [
            ('giao_tiep_hang_hai', 'Khối giao tiếp\nhàng hải'),
            ('ban_dieu_khien_chinh', 'Bàn điều\nkhiển chính từ\nxa'),
            ('bang_dien_chinh', 'Bảng điện\nchính')
        ]
        
        # Khoang điều khiển tại chỗ 2
        compartment3_nodes = [
            ('ac_quy_2', 'Tủ ác quy'),
            ('phan_phoi_2', 'Tủ phân phối\nbiến đổi'),
            ('bien_ap_2', 'Tủ biến áp'),
            ('dan_dong_huong_2', 'Hộp dẫn động\nkềnh hướng'),
            ('dan_dong_tam_2', 'Hộp dẫn động\nkềnh tâm'),
            ('dieu_khien_2', 'Tủ điều khiển\ntại chỗ 2'),
            ('ban_dieu_khien_2', 'Bàn điều\nkhiển tại chỗ'),
            ('hn22', 'HN22'),
            ('hn21', 'HN21')
        ]
        
        # Cột ngắm
        sight_column_nodes = [
            ('hop_dien', 'Hộp điện'),
            ('hop_quang_dien_tu', 'Hộp quang\nđiện tử')
        ]
        
        # Tạo tất cả nodes
        all_nodes = compartment1_nodes + compartment2_nodes + compartment3_nodes + sight_column_nodes
        for node_id, name in all_nodes:
            self.nodes[node_id] = NodeData(node_id, name)
            
    def get_node(self, node_id: str) -> NodeData:
        """Lấy node theo ID."""
        return self.nodes.get(node_id)
        
    def get_all_nodes(self) -> Dict[str, NodeData]:
        """Lấy tất cả nodes."""
        return self.nodes
        
    def simulate_data(self):
        """
        Mô phỏng dữ liệu cho các node (chỉ cập nhật readings, không tự động tạo lỗi).
        Lỗi sẽ được xác định bởi threshold checking trong module system.
        """
        for node in self.nodes.values():
            # Mô phỏng điện áp (220V ± 10V) - chỉ cập nhật giá trị đo
            base_voltage = 220.0
            voltage = base_voltage + random.uniform(-10, 10)
            node.add_voltage_reading(voltage)

            # Không tự động tạo lỗi - để module threshold manager xử lý
            # Lỗi sẽ được tự động phát hiện dựa trên ngưỡng của từng module

    def refresh_all_node_error_statuses(self):
        """Làm mới trạng thái lỗi của tất cả các node dựa trên module status."""
        for node in self.nodes.values():
            node.update_error_status_from_modules()
                
    def get_node_by_name(self, name: str) -> NodeData:
        """Lấy node theo tên hiển thị."""
        for node in self.nodes.values():
            if node.name == name:
                return node
        return None

# Global instance
system_data_manager = SystemDataManager()
