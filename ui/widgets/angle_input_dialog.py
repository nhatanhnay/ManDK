# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QPainter, QColor
import ui.ui_config as config


class AngleInputDialog(QWidget):
    """Widget overlay để nhập khoảng cách và góc hướng - hiển thị trên tab thay vì window riêng."""
    
    # Signal để thông báo khi đóng dialog
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    
    def __init__(self, side="Trái", current_distance=0, current_direction=0, is_left_side=True, parent=None):
        super().__init__(parent)
        self.side = side
        self.distance_value = current_distance
        self.direction_value = current_direction
        self.is_left_side = is_left_side  # True nếu giàn trái, False nếu giàn phải
        
        # Làm cho widget này hiển thị trên tất cả widget khác
        self.setWindowFlags(Qt.Widget)
        
        self.setupUi()
        
    def paintEvent(self, event):
        """Vẽ background semi-transparent cho overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ background mờ đục để làm nổi bật dialog
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
    
    def setupUi(self):
        """Thiết lập giao diện dialog."""
        # Layout chính chiếm toàn bộ widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container widget cho dialog box (sẽ được center)
        dialog_container = QWidget()
        dialog_container.setMinimumWidth(600)
        dialog_container.setMaximumWidth(700)
        dialog_container.setMaximumHeight(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Group box cho khoảng cách
        distance_group = QGroupBox("Khoảng cách (m)")
        distance_layout = QVBoxLayout()
        distance_layout.setSpacing(8)
        
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Nhập khoảng cách (0-20000)")
        self.distance_input.setText(str(self.distance_value))
        self.distance_input.setMinimumHeight(50)  # Tăng chiều cao ô nhập
        
        # Validator cho khoảng cách (0-20000 mét)
        distance_validator = QDoubleValidator(0.0, 20000.0, 1)
        distance_validator.setNotation(QDoubleValidator.StandardNotation)
        self.distance_input.setValidator(distance_validator)
        
        distance_layout.addWidget(self.distance_input)
        
        # Nút chuyển đổi chế độ Auto/Manual
        mode_button_layout = QHBoxLayout()
        mode_button_layout.setSpacing(15)
        
        self.mode_label = QLabel()
        self.mode_label.setMinimumHeight(40)  # Tăng chiều cao label
        self.mode_label.setMinimumWidth(180)  # Tăng chiều rộng label
        self.update_mode_label()
        mode_button_layout.addWidget(self.mode_label)
        
        self.toggle_mode_button = QPushButton()
        self.update_mode_button()
        self.toggle_mode_button.clicked.connect(self.toggle_distance_mode)
        self.toggle_mode_button.setMinimumWidth(180)  # Tăng chiều rộng tối thiểu
        self.toggle_mode_button.setMinimumHeight(40)  # Tăng chiều cao
        mode_button_layout.addWidget(self.toggle_mode_button)
        
        distance_layout.addLayout(mode_button_layout)
        distance_group.setLayout(distance_layout)
        
        # Group box cho góc hướng
        direction_group = QGroupBox("Góc hướng (độ)")
        direction_layout = QVBoxLayout()
        direction_layout.setSpacing(8)
        
        self.direction_input = QLineEdit()
        self.direction_input.setPlaceholderText("Nhập góc hướng (-180 đến 180)")
        self.direction_input.setText(str(self.direction_value))
        
        # Validator cho góc hướng (-180 đến 180 độ)
        direction_validator = QDoubleValidator(-180.0, 180.0, 1)
        direction_validator.setNotation(QDoubleValidator.StandardNotation)
        self.direction_input.setValidator(direction_validator)
        
        direction_layout.addWidget(self.direction_input)
        direction_group.setLayout(direction_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Xác nhận")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # Title label
        title_label = QLabel(f"Nhập góc - Giàn {self.side}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)
        
        # Add all to dialog container layout
        layout.addWidget(title_label)
        layout.addWidget(distance_group)
        layout.addWidget(direction_group)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        
        dialog_container.setLayout(layout)
        
        # Thêm container vào main layout và center nó
        main_layout.addStretch()
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(dialog_container)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Style - cải thiện để dễ nhìn hơn
        dialog_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 10px;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 13px;
                padding-top: 15px;
                padding-bottom: 10px;
                padding-left: 10px;
                padding-right: 10px;
                color: #cccccc;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #ffffff;
            }
            QLabel {
                color: #aaaaaa;
                font-size: 13px;
                font-weight: normal;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #f0f0f0;
                color: #000000;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 15px 20px;
                font-size: 22px;
                font-weight: bold;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 3px solid #0078d4;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 2px solid #888888;
                background-color: #fafafa;
            }
            QLineEdit:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
        """)
        
        # Style cho nút Xác nhận (màu xanh lá)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2eb84e;
            }
            QPushButton:pressed {
                background-color: #20873a;
            }
        """)
        
    def toggle_distance_mode(self):
        """Chuyển đổi giữa chế độ tự động và thủ công."""
        if self.is_left_side:
            config.DISTANCE_MODE_AUTO_L = not config.DISTANCE_MODE_AUTO_L
        else:
            config.DISTANCE_MODE_AUTO_R = not config.DISTANCE_MODE_AUTO_R
        
        self.update_mode_label()
        self.update_mode_button()
        
    def update_mode_label(self):
        """Cập nhật label hiển thị chế độ hiện tại."""
        is_auto = config.DISTANCE_MODE_AUTO_L if self.is_left_side else config.DISTANCE_MODE_AUTO_R
        mode_text = "Chế độ: <b>Tự động</b>" if is_auto else "Chế độ: <b>Thủ công</b>"
        self.mode_label.setText(mode_text)
        bg_color = "#004400" if is_auto else "#443300"
        border_color = "#00ff00" if is_auto else "#ffaa00"
        text_color = "#00ff00" if is_auto else "#ffaa00"
        self.mode_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: bold;
                padding: 10px 15px;
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 5px;
            }}
        """)
        
        # Vô hiệu hóa/kích hoạt ô nhập khoảng cách dựa trên chế độ
        self.distance_input.setEnabled(not is_auto)
        
    def update_mode_button(self):
        """Cập nhật text và style của nút chuyển chế độ."""
        is_auto = config.DISTANCE_MODE_AUTO_L if self.is_left_side else config.DISTANCE_MODE_AUTO_R
        button_text = "Chuyển sang Thủ công" if is_auto else "Chuyển sang Tự động"
        self.toggle_mode_button.setText(button_text)
        
        button_color = "#ff6600" if is_auto else "#00aa00"
        self.toggle_mode_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {button_color}dd;
            }}
            QPushButton:pressed {{
                background-color: {button_color}aa;
            }}
        """)
    
    def accept(self):
        """Xử lý khi nhấn nút Xác nhận."""
        self.accepted.emit()
        self.hide()
    
    def reject(self):
        """Xử lý khi nhấn nút Hủy."""
        self.rejected.emit()
        self.hide()
        
    def get_values(self):
        """Lấy giá trị khoảng cách và góc hướng đã nhập."""
        try:
            distance = float(self.distance_input.text()) if self.distance_input.text() else self.distance_value
            direction = float(self.direction_input.text()) if self.direction_input.text() else self.direction_value
            
            # Clamp values trong range hợp lệ
            distance = max(0.0, min(20000.0, distance))
            direction = max(-180.0, min(180.0, direction))
            
            return distance, direction
        except ValueError:
            # Trả về giá trị mặc định nếu parse lỗi
            return self.distance_value, self.direction_value
