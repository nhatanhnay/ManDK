from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from .components.compass import AngleCompass
from .components.half_compass import HalfCircleWidget
from .components.numeric_data import NumericDataWidget
from .components.bullet_widget import BulletWidget
from .components.custom_message_box import CustomMessageBox
from .components.utils import ColoredSVGButton
import control_panel.config as config
from control_panel.sender import sender
import yaml
import random
import math
from .components.compass import resource_path
from scipy.interpolate import CubicSpline
import numpy as np

class GridBackgroundWidget(QtWidgets.QWidget):
    """Widget với grid background cho toàn bộ app với hiệu ứng dot nhấp nháy."""
    
    def __init__(self, parent=None, enable_animation=True):
        super().__init__(parent)
        self.enable_animation = enable_animation
        self.grid_spacing = 50
        self.dot_clusters = []
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        if self.enable_animation:
            self.animation_timer.start(50)  # Giảm xuống 50ms để animation mượt hơn
        self.time_offset = 0
        self._initialize_dot_clusters()
    
    def set_animation_enabled(self, enabled):
        """Bật/tắt hiệu ứng animation."""
        self.enable_animation = enabled
        if enabled:
            self.animation_timer.start(50)
        else:
            self.animation_timer.stop()
        self.update()  # Cập nhật để vẽ lại
        
    def _initialize_dot_clusters(self):
        """Khởi tạo hiệu ứng sóng từ trái trên xuống phải dưới."""
        # Không cần clusters nữa, chỉ cần thông số sóng
        self.wave_speed = 0.05  # Tăng tốc độ sóng chạy để rõ ràng hơn
        self.wave_frequency = 0.5  # Tăng tần số để tạo sự khác biệt rõ rệt giữa các dot
        
    def update_animation(self):
        """Cập nhật animation cho dot nhấp nháy."""
        if self.enable_animation:
            self.time_offset += 1
            self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Vẽ grid background với dot nhấp nháy."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.enable_animation:
            # Chỉ vẽ background đơn giản nếu animation bị tắt
            return
        
        # Vẽ lưới background với đường kẻ ngang và dọc màu xám trắng mỏng
        painter.setPen(QPen(QColor(220, 220, 220, 80), 0.5))
        
        # Vẽ các đường kẻ dọc
        for x in range(0, self.width(), self.grid_spacing):
            painter.drawLine(x, 0, x, self.height())
        
        # Vẽ các đường kẻ ngang
        for y in range(0, self.height(), self.grid_spacing):
            painter.drawLine(0, y, self.width(), y)
            
        # Vẽ các dot nhấp nháy tại giao điểm
        self._draw_blinking_dots(painter)
        
    def _draw_blinking_dots(self, painter):
        """Vẽ các dot nhấp nháy theo dạng sóng từ trái trên xuống phải dưới."""
        painter.setPen(Qt.NoPen)
        
        # Tính toán số lượng giao điểm
        cols = self.width() // self.grid_spacing + 1
        rows = self.height() // self.grid_spacing + 1
        
        # Tạo danh sách tất cả giao điểm hợp lệ (tránh viền)
        margin = 20
        for row in range(rows):
            for col in range(cols):
                x = col * self.grid_spacing
                y = row * self.grid_spacing
                
                # Kiểm tra nếu giao điểm nằm trong vùng hợp lệ
                if margin <= x <= self.width() - margin and margin <= y <= self.height() - margin:
                    # Tính toán khoảng cách diagonal từ góc trái trên (0,0)
                    # Sử dụng tổng col + row để tạo diagonal
                    diagonal_distance = col + row
                    
                    # Tạo sóng chạy theo thời gian với công thức rõ ràng hơn
                    wave_phase = self.time_offset * self.wave_speed - diagonal_distance * self.wave_frequency
                    
                    # Tính alpha dựa trên sóng sin với biên độ lớn hơn
                    alpha = int(80 + 175 * math.sin(wave_phase))  # Alpha từ 80 đến 255 để rõ ràng hơn
                    
                    # Đảm bảo alpha trong khoảng hợp lệ
                    alpha = max(0, min(255, alpha))
                    
                    # Màu dot: xanh lam nhạt với alpha theo sóng
                    color = QColor(100, 150, 255, alpha)
                    painter.setBrush(QBrush(color))
                    
                    # Vẽ dot nhỏ tại chính xác giao điểm
                    dot_size = 2.5
                    dot_rect = QRectF(
                        x - dot_size/2, 
                        y - dot_size/2,
                        dot_size, 
                        dot_size
                    )
                    painter.drawEllipse(dot_rect)
                        
    def resizeEvent(self, event):
        """Khởi tạo lại dot clusters khi resize."""
        super().resizeEvent(event)
        self._initialize_dot_clusters()

class LogTab(GridBackgroundWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data
        self.setupUi()

    def setupUi(self):
        # Create main layout for log display
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Add a label to indicate this is the log tab
        log_label = QtWidgets.QLabel("Nhật ký hệ thống")
        log_label.setStyleSheet("""
            QLabel {
                color: #F1F5F9;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                background: #19232D;
                border: 2px solid #10B981;
                border-radius: 8px;
                margin: 20px;
            }
        """)
        log_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(log_label)
        
        # Add placeholder for future log functionality
        placeholder_label = QtWidgets.QLabel("Tính năng nhật ký sẽ được phát triển trong tương lai")
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 14px;
                padding: 20px;
                text-align: center;
            }
        """)
        placeholder_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(placeholder_label)
