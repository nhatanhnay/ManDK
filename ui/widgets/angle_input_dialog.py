# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator


class AngleInputDialog(QDialog):
    """Dialog để nhập góc tầm và góc hướng."""
    
    def __init__(self, side="Trái", current_elevation=0, current_direction=0, parent=None):
        super().__init__(parent)
        self.side = side
        self.elevation_value = current_elevation
        self.direction_value = current_direction
        
        self.setWindowTitle(f"Nhập góc - Giàn {side}")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.setupUi()
        
    def setupUi(self):
        """Thiết lập giao diện dialog."""
        layout = QVBoxLayout()
        
        # Group box cho góc tầm
        elevation_group = QGroupBox("Góc tầm (độ)")
        elevation_layout = QHBoxLayout()
        
        self.elevation_label = QLabel("Góc tầm:")
        self.elevation_input = QLineEdit()
        self.elevation_input.setPlaceholderText("Nhập góc tầm (0-60)")
        self.elevation_input.setText(str(self.elevation_value))
        
        # Validator cho góc tầm (0-60 độ)
        elevation_validator = QDoubleValidator(0.0, 60.0, 1)
        elevation_validator.setNotation(QDoubleValidator.StandardNotation)
        self.elevation_input.setValidator(elevation_validator)
        
        elevation_layout.addWidget(self.elevation_label)
        elevation_layout.addWidget(self.elevation_input)
        elevation_group.setLayout(elevation_layout)
        
        # Group box cho góc hướng
        direction_group = QGroupBox("Góc hướng (độ)")
        direction_layout = QHBoxLayout()
        
        self.direction_label = QLabel("Góc hướng:")
        self.direction_input = QLineEdit()
        self.direction_input.setPlaceholderText("Nhập góc hướng (-180 đến 180)")
        self.direction_input.setText(str(self.direction_value))
        
        # Validator cho góc hướng (-180 đến 180 độ)
        direction_validator = QDoubleValidator(-180.0, 180.0, 1)
        direction_validator.setNotation(QDoubleValidator.StandardNotation)
        self.direction_input.setValidator(direction_validator)
        
        direction_layout.addWidget(self.direction_label)
        direction_layout.addWidget(self.direction_input)
        direction_group.setLayout(direction_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Xác nhận")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add all to main layout
        layout.addWidget(elevation_group)
        layout.addWidget(direction_group)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QGroupBox {
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:default {
                background-color: #28a745;
            }
            QPushButton:default:hover {
                background-color: #218838;
            }
        """)
        
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
