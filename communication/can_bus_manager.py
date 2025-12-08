# -*- coding: utf-8 -*-

import can
import threading
from communication.can_config import CAN_CHANNEL, CAN_BUSTYPE, CAN_BITRATE


class CANBusManager:
    """Singleton quản lý CAN bus instance duy nhất để tránh bus-off.
    
    Sử dụng singleton pattern để đảm bảo chỉ có 1 bus instance được tạo,
    tránh tình trạng tạo/đóng bus liên tục gây bus-off state.
    """
    
    _instance = None
    _lock = threading.Lock()
    _bus = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_bus(self):
        """Lấy CAN bus instance (tạo nếu chưa có).
        
        Returns:
            can.interface.Bus: CAN bus instance
            
        Raises:
            Exception: Nếu không thể khởi tạo CAN bus
        """
        if self._bus is None:
            with self._lock:
                if self._bus is None:
                    try:
                        self._bus = can.interface.Bus(
                            channel=CAN_CHANNEL,
                            bustype=CAN_BUSTYPE,
                            bitrate=CAN_BITRATE
                        )
                        print(f"✓ CAN bus manager khởi tạo thành công trên {CAN_CHANNEL} @ {CAN_BITRATE}bps")
                        
                        # Ghi log thành công
                        try:
                            from ui.tabs.event_log_tab import LogTab
                            LogTab.log(f"CAN bus manager khởi tạo thành công trên {CAN_CHANNEL} @ {CAN_BITRATE}bps", "SUCCESS")
                        except:
                            pass
                            
                    except Exception as e:
                        error_msg = f"Lỗi khởi tạo CAN bus: {e}"
                        print(error_msg)
                        
                        # Ghi log lỗi
                        try:
                            from ui.tabs.event_log_tab import LogTab
                            LogTab.log(error_msg, "ERROR")
                        except:
                            pass
                        raise
        return self._bus
    
    def is_connected(self):
        """Kiểm tra xem CAN bus đã được khởi tạo chưa.
        
        Returns:
            bool: True nếu bus đã được khởi tạo
        """
        return self._bus is not None
    
    def shutdown(self):
        """Đóng CAN bus (chỉ gọi khi thoát ứng dụng)."""
        if self._bus is not None:
            with self._lock:
                if self._bus is not None:
                    try:
                        self._bus.shutdown()
                        self._bus = None
                        print("CAN bus đã được đóng")
                        
                        # Ghi log
                        try:
                            from ui.tabs.event_log_tab import LogTab
                            LogTab.log("CAN bus đã được đóng", "INFO")
                        except:
                            pass
                    except Exception as e:
                        print(f"Lỗi khi đóng CAN bus: {e}")


# Tạo instance toàn cục
can_bus_manager = CANBusManager()
