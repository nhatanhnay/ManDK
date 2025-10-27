# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QPainter, QColor


class AngleInputDialog(QWidget):
    """Widget overlay để nhập góc tầm và góc hướng - hiển thị trên tab thay vì window riêng."""
    
    # Signal để thông báo khi đóng dialog
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    
    def __init__(self, side="Trái", current_elevation=0, current_direction=0, parent=None):
        super().__init__(parent)
        self.side = side
        self.elevation_value = current_elevation
        self.direction_value = current_direction
        
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
        dialog_container.setMinimumWidth(500)
        dialog_container.setMaximumWidth(600)
        dialog_container.setMaximumHeight(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Group box cho góc tầm
        elevation_group = QGroupBox("Góc tầm (độ)")
        elevation_layout = QVBoxLayout()
        elevation_layout.setSpacing(8)
        
        self.elevation_input = QLineEdit()
        self.elevation_input.setPlaceholderText("Nhập góc tầm (0-60)")
        self.elevation_input.setText(str(self.elevation_value))
        
        # Validator cho góc tầm (0-60 độ)
        elevation_validator = QDoubleValidator(0.0, 60.0, 1)
        elevation_validator.setNotation(QDoubleValidator.StandardNotation)
        self.elevation_input.setValidator(elevation_validator)
        
        elevation_layout.addWidget(self.elevation_input)
        elevation_group.setLayout(elevation_layout)
        
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
        layout.addWidget(elevation_group)
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
                padding: 12px 15px;
                font-size: 18px;
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
        
    def accept(self):
        """Xử lý khi nhấn nút Xác nhận."""
        self.accepted.emit()
        self.hide()
    
    def reject(self):
        """Xử lý khi nhấn nút Hủy."""
        self.rejected.emit()
        self.hide()
        
    def get_values(self):
        """Lấy giá trị góc tầm và góc hướng đã nhập."""
        try:
            elevation = float(self.elevation_input.text()) if self.elevation_input.text() else self.elevation_value
            direction = float(self.direction_input.text()) if self.direction_input.text() else self.direction_value
            
            # Clamp values trong range hợp lệ
            elevation = max(0.0, min(60.0, elevation))
            direction = max(-180.0, min(180.0, direction))
            
            return elevation, direction
        except ValueError:
            # Trả về giá trị mặc định nếu parse lỗi
            return self.elevation_value, self.direction_value
