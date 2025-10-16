from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QWidget, QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
import ui.ui_config as config


class BinaryValidator(QIntValidator):
    """Validator chỉ chấp nhận giá trị 0 hoặc 1."""
    
    def __init__(self, parent=None):
        super().__init__(0, 1, parent)
    
    def validate(self, input_str, pos):
        # Chỉ chấp nhận chuỗi rỗng, "0" hoặc "1"
        if input_str == "":
            return (QIntValidator.Intermediate, input_str, pos)
        if input_str in ["0", "1"]:
            return (QIntValidator.Acceptable, input_str, pos)
        return (QIntValidator.Invalid, input_str, pos)


class CapsuleInput(QWidget):
    """Widget hình viên thuốc với 3 phần: label - input - đơn vị."""

    def __init__(self, label_text, default_value="0", unit_text="", parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.unit_text = unit_text

        # Tạo layout chính
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container cho viên thuốc
        capsule = QWidget()
        capsule.setFixedHeight(50)
        capsule_layout = QHBoxLayout(capsule)
        capsule_layout.setContentsMargins(0, 0, 0, 0)
        capsule_layout.setSpacing(0)

        # Label bên trái
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setFixedHeight(50)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #525252;
                color: #F1F5F9;
                font-size: 14px;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-left: 20px;
                border-top-left-radius: 25px;
                border-bottom-left-radius: 25px;
            }
        """)
        self.label.setMinimumWidth(180)
        capsule_layout.addWidget(self.label)

        # Đường phân cách giữa label và input
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFixedWidth(1)
        separator1.setStyleSheet("background-color: #F1F5F9;")
        capsule_layout.addWidget(separator1)

        # Input ở giữa
        self.input_field = QLineEdit(default_value)
        self.input_field.setValidator(QDoubleValidator())
        self.input_field.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Căn phải
        self.input_field.setFixedHeight(50)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #525252;
                color: #F1F5F9;
                border: none;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-right: 10px;
            }
            QLineEdit:focus {
                background-color: #626262;
            }
            QLineEdit:disabled {
                background-color: #3a3a3a;
                color: #808080;
            }
        """)
        self.input_field.setFixedWidth(100)  # Tăng lên 100px
        capsule_layout.addWidget(self.input_field)

        # Đường phân cách giữa input và đơn vị
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFixedWidth(1)
        separator2.setStyleSheet("background-color: #F1F5F9;")
        capsule_layout.addWidget(separator2)

        # Đơn vị bên phải
        self.unit_label = QLabel(unit_text)
        self.unit_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Căn phải
        self.unit_label.setFixedHeight(50)
        self.unit_label.setStyleSheet("""
            QLabel {
                background-color: #525252;
                color: #F1F5F9;
                font-size: 14px;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-right: 15px;
                border-top-right-radius: 25px;
                border-bottom-right-radius: 25px;
            }
        """)
        self.unit_label.setFixedWidth(100)  # Tăng lên 100px
        capsule_layout.addWidget(self.unit_label)

        layout.addWidget(capsule)

    def text(self):
        """Lấy text từ input field."""
        return self.input_field.text()

    def setText(self, text):
        """Set text cho input field."""
        self.input_field.setText(text)

    def setEnabled(self, enabled):
        """Enable/disable input field."""
        self.input_field.setEnabled(enabled)
        super().setEnabled(enabled)

    @property
    def textChanged(self):
        """Signal khi text thay đổi."""
        return self.input_field.textChanged


class RoundedLineEdit(QLineEdit):
    """Custom QLineEdit với bo góc và style đẹp."""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F1F5F9;
                border: 1.5px solid #475569;
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 1.5px solid #3B82F6;
                background-color: #1E293B;
            }
            QLineEdit:disabled {
                background-color: #1E293B;
                color: #64748B;
                border: 1.5px solid #334155;
            }
        """)
        self.setMinimumHeight(36)


class ToggleSwitch(QWidget):
    """Toggle switch tự động/thủ công."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_auto = True  # True = Tự động, False = Thủ công
        self.setFixedSize(110, 40)  # Tăng width từ 100 lên 110
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
        from PyQt5.QtCore import QRectF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Vẽ nền toggle
        if self.is_auto:
            bg_color = QColor(16, 185, 129)  # Xanh lá khi bật (tự động)
        else:
            bg_color = QColor(71, 85, 105)  # Xám khi tắt (thủ công)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, 110, 40, 20, 20)

        # Vẽ nút tròn
        circle_x = 75 if self.is_auto else 5  # 75 = 110 - 30 - 5
        painter.setBrush(QBrush(QColor(241, 245, 249)))  # Trắng
        painter.drawEllipse(circle_x, 5, 30, 30)

        # Vẽ chữ
        painter.setPen(QPen(QColor(241, 245, 249)))
        font = QFont("Tahoma", 9, QFont.Bold)
        painter.setFont(font)

        from PyQt5.QtCore import QRect
        if self.is_auto:
            # Text bên trái khi nút ở bên phải
            text_rect = QRect(10, 0, 60, 40)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "Tự động")
        else:
            # Text bên phải khi nút ở bên trái
            text_rect = QRect(40, 0, 65, 40)
            painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, "Thủ công")

    def mousePressEvent(self, event):
        self.is_auto = not self.is_auto
        self.update()
        # Gọi callback nếu có
        if hasattr(self, 'on_toggle'):
            self.on_toggle(self.is_auto)


class BallisticCalculatorWidget(QWidget):
    """Widget tính toán lượng sửa bắn hiển thị inline trong giao diện."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set object name để áp dụng stylesheet riêng
        self.setObjectName("ballistic_calculator_main")

        # Giá trị tiêu chuẩn
        self.standard_temp = 15.9
        self.standard_pressure = 750
        self.standard_charge_temp = 15

        # Lấy góc hiện tại từ config
        self.current_elevation_left = config.ANGLE_L
        self.current_direction_left = config.DIRECTION_L
        self.current_elevation_right = config.ANGLE_R
        self.current_direction_right = config.DIRECTION_R

        self.setup_ui()
        self.apply_styles()
        self.connect_signals()
        self.update_angle_display()

    def setup_ui(self):
        """Thiết lập giao diện."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Phần bên trái - Input fields
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # Đường phân cách dọc
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedWidth(2)
        separator.setStyleSheet("background-color: #FFFFFF;")
        main_layout.addWidget(separator)

        # Phần bên phải
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

    def create_left_panel(self):
        """Tạo panel bên trái với các input fields."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        # Title
        title = QLabel("Nhập thông số")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(title)

        # Input fields
        self.wind_speed_inputs = []
        self.wind_dir_inputs = []

        # Gió dọc dàn đạo
        label_text = "Gió dọc đạn đạo thấp"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi theo hướng đạn ở độ cao thấp (âm: xuôi chiều, dương: ngược chiều)")
        layout.addWidget(capsule)
        self.wind_speed_inputs.append(capsule)

        label_text = "Gió dọc đạn đạo cao"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi theo hướng đạn ở độ cao lớn (âm: xuôi chiều, dương: ngược chiều)")
        layout.addWidget(capsule)
        self.wind_speed_inputs.append(capsule)

        # Gió ngang đạn đạo
        label_text = "Gió ngang đạn đạo thấp"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi vuông góc với hướng đạn ở độ cao thấp (dương: phải, âm: trái)")
        layout.addWidget(capsule)
        self.wind_dir_inputs.append(capsule)

        # Gió ngang đạn đạo cao
        label_text = "Gió ngang đạn đạo cao"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi vuông góc với hướng đạn ở độ cao lớn (dương: phải, âm: trái)")
        layout.addWidget(capsule)
        self.wind_dir_inputs.append(capsule)

        # Mật độ không khí
        self.air_density_input = self.create_input_row("Áp suất không khí", str(self.standard_pressure), "mmHg", 
                                                        note_text="Áp suất khí quyển tại vị trí bắn")
        layout.addWidget(self.air_density_input)

        # Nhiệt độ không khí
        self.air_temp_input = self.create_input_row("Nhiệt độ không khí", str(self.standard_temp), "°C",
                                                     note_text="Nhiệt độ môi trường không khí ngoài trời")
        layout.addWidget(self.air_temp_input)

        # Nhiệt độ liều phóng
        self.charge_temp_input = self.create_input_row("Nhiệt độ liều phóng", str(self.standard_charge_temp), "°C",
                                                        note_text="Nhiệt độ của thuốc phóng trong đạn (tiêu chuẩn: 15°C)")
        layout.addWidget(self.charge_temp_input)

        # Thuốc phóng kacn-14 (chỉ nhận 0 hoặc 1)
        self.kacn_input = self.create_input_row("Thuốc phóng kacn-14", "0", "", binary_mode=True,
                                                 note_text="Loại thuốc phóng: 0 = thường, 1 = kacn-14")
        layout.addWidget(self.kacn_input)

        # Góc tạ mục tiêu
        self.target_angle_input = self.create_input_row("Góc tà mục tiêu", "0", "",
                                                         note_text="Góc chênh của mục tiêu (dương: mục tiêu cao hơn, âm: mục tiêu thấp hơn)")
        layout.addWidget(self.target_angle_input)

        layout.addStretch()

        return panel

    def create_right_panel(self):
        """Tạo panel bên phải với switch và bảng."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)

        # Title với toggle switch
        header = QHBoxLayout()
        title = QLabel("Chế độ tính toán")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
        header.addWidget(title)
        header.addStretch()

        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.on_toggle = self.on_mode_changed
        header.addWidget(self.toggle_switch)
        layout.addLayout(header)

        # Input fields cho mode thủ công
        self.manual_panel = QWidget()
        manual_layout = QVBoxLayout(self.manual_panel)
        manual_layout.setSpacing(12)

        self.manual_elevation_left_input = self.create_input_row("Thay đổi góc tầm trái", "0", "ly giác")
        manual_layout.addWidget(self.manual_elevation_left_input)
        self.manual_elevation_right_input = self.create_input_row("Thay đổi góc tầm phải", "0", "ly giác")
        manual_layout.addWidget(self.manual_elevation_right_input)

        self.manual_direction_left_input = self.create_input_row("Thay đổi góc hướng trái", "0", "ly giác")
        manual_layout.addWidget(self.manual_direction_left_input)
        self.manual_direction_right_input = self.create_input_row("Thay đổi góc hướng phải", "0", "ly giác")
        manual_layout.addWidget(self.manual_direction_right_input)

        # Disable mặc định khi ở chế độ tự động
        self.manual_elevation_left_input.setEnabled(False)
        self.manual_elevation_right_input.setEnabled(False)
        self.manual_direction_left_input.setEnabled(False)
        self.manual_direction_right_input.setEnabled(False)


        layout.addWidget(self.manual_panel)

        # Bảng hiển thị góc tầm và góc hướng
        table_title = QLabel("Góc trước và sau khi áp dụng")
        table_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9; margin-top: 10px;")
        layout.addWidget(table_title)

        table = self.create_angle_table()
        layout.addWidget(table)

        # Đường phân cách
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #475569;")
        layout.addWidget(separator)

        # Giá trị tiêu chuẩn
        standard_title = QLabel("Giá trị tiêu chuẩn")
        standard_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(standard_title)

        standard = self.create_standard_values()
        layout.addWidget(standard)

        # Nút OK và Cancel
        buttons = self.create_buttons()
        layout.addLayout(buttons)

        return panel

    def create_input_row(self, label_text, default_value, unit, binary_mode=False, note_text=""):
        """Tạo một widget input hình viên thuốc với ghi chú.
        
        Args:
            label_text: Text hiển thị bên trái
            default_value: Giá trị mặc định
            unit: Đơn vị hiển thị bên phải
            binary_mode: Nếu True, chỉ chấp nhận 0 hoặc 1
            note_text: Text ghi chú cố định (không edit được)
        """
        # Container chứa capsule input và ghi chú (vertical layout)
        row_widget = QWidget()
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        
        # Capsule input ở trên
        capsule_input = CapsuleInput(label_text, default_value, unit)
        
        # Nếu là binary mode, đặt validator đặc biệt
        if binary_mode:
            capsule_input.input_field.setValidator(BinaryValidator())
        
        row_layout.addWidget(capsule_input)
        
        # Label ghi chú cố định ở dưới (nếu có note_text)
        if note_text:
            note_label = QLabel(note_text)
            note_label.setFixedHeight(24)
            note_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            note_label.setWordWrap(True)
            note_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: #94A3B8;
                    font-size: 13px;
                    font-style: italic;
                    padding-left: 5px;
                    padding-right: 5px;
                }
            """)
            row_layout.addWidget(note_label)
            row_widget.note_label = note_label
        
        # Lưu references để có thể truy cập dễ dàng
        row_widget.capsule_input = capsule_input
        
        # Thêm helper methods để truy cập giá trị như trước
        row_widget.text = capsule_input.text
        row_widget.setText = capsule_input.setText
        row_widget.setEnabled = capsule_input.setEnabled
        
        # Expose signal từ capsule input
        row_widget.textChanged = capsule_input.textChanged
        
        return row_widget

    def create_angle_table(self):
        """Tạo bảng hiển thị góc tầm và góc hướng."""
        table = QWidget()
        layout = QGridLayout(table)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header chính (hàng 0) - span 2 cột cho mỗi tiêu đề
        header_label_empty = QLabel("")
        header_label_empty.setAlignment(Qt.AlignCenter)
        header_label_empty.setStyleSheet("""
            background-color: #334155;
            color: #F1F5F9;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
            border: 1px solid #475569;
        """)
        layout.addWidget(header_label_empty, 0, 0, 2, 1)  # Span 2 hàng

        # "Góc tầm" span 2 cột
        header_elevation = QLabel("Góc tầm")
        header_elevation.setAlignment(Qt.AlignCenter)
        header_elevation.setStyleSheet("""
            background-color: #334155;
            color: #F1F5F9;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
            border: 1px solid #475569;
        """)
        layout.addWidget(header_elevation, 0, 1, 1, 2)  # Span 2 cột

        # "Góc hướng" span 2 cột
        header_direction = QLabel("Góc hướng")
        header_direction.setAlignment(Qt.AlignCenter)
        header_direction.setStyleSheet("""
            background-color: #334155;
            color: #F1F5F9;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
            border: 1px solid #475569;
        """)
        layout.addWidget(header_direction, 0, 3, 1, 2)  # Span 2 cột

        # Sub-headers (hàng 1) - Trái/Phải cho mỗi nhóm
        sub_headers = ["Trái", "Phải", "Trái", "Phải"]
        for col, sub_header in enumerate(sub_headers, 1):
            label = QLabel(sub_header)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                background-color: #475569;
                color: #F1F5F9;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border: 1px solid #475569;
            """)
            layout.addWidget(label, 1, col)

        # Rows - Mặc định và Áp dụng lượng sửa
        row_labels = ["Mặc định", "Áp dụng lượng sửa"]
        self.angle_cells = {}

        for row, row_label in enumerate(row_labels, 2):  # Bắt đầu từ hàng 2
            # Row label
            label = QLabel(row_label)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                background-color: #334155;
                color: #F1F5F9;
                font-size: 13px;
                padding: 10px;
                border: 1px solid #475569;
            """)
            layout.addWidget(label, row, 0)

            # Cells: 4 cột (Góc tầm Trái, Góc tầm Phải, Góc hướng Trái, Góc hướng Phải)
            cell_keys = [
                ('elevation_left', 1),
                ('elevation_right', 2),
                ('direction_left', 3),
                ('direction_right', 4)
            ]

            for key_suffix, col in cell_keys:
                cell_label = QLabel("0.0°")
                cell_label.setAlignment(Qt.AlignCenter)
                cell_label.setStyleSheet("""
                    background-color: #1E293B;
                    color: #F1F5F9;
                    font-size: 14px;
                    padding: 10px;
                    border: 1px solid #475569;
                """)
                layout.addWidget(cell_label, row, col)

                # Lưu reference để update sau
                key = f"{'default' if row == 2 else 'corrected'}_{key_suffix}"
                self.angle_cells[key] = cell_label

        return table

    def create_standard_values(self):
        """Tạo widget hiển thị giá trị tiêu chuẩn."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Nhiệt độ không khí tiêu chuẩn
        self.std_temp_input = self.create_input_row("Nhiệt độ không khí tiêu chuẩn", str(self.standard_temp), "°C")
        layout.addWidget(self.std_temp_input)

        # Áp suất khí quyển tiêu chuẩn
        self.std_pressure_input = self.create_input_row("Áp suất khí quyển tiêu chuẩn", str(self.standard_pressure), "mmHg")
        layout.addWidget(self.std_pressure_input)

        # Nhiệt độ liều phóng tiêu chuẩn
        self.std_charge_temp_input = self.create_input_row("Nhiệt độ liều phóng tiêu chuẩn", str(self.standard_charge_temp), "°C")
        layout.addWidget(self.std_charge_temp_input)

        return widget

    def create_buttons(self):
        """Tạo nút Reset, OK và Cancel."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Reset Button (bên trái)
        self.reset_btn = QPushButton("↻")
        self.reset_btn.setFixedSize(50, 50)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: #F1F5F9;
                border: none;
                border-radius: 25px;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()

        # OK Button (checkmark icon)
        self.ok_btn = QPushButton("✓")
        self.ok_btn.setFixedSize(50, 50)
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #F1F5F9;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        button_layout.addWidget(self.ok_btn)

        # Cancel Button (X icon)
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(50, 50)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #F1F5F9;
                border: none;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        button_layout.addWidget(self.cancel_btn)

        return button_layout

    def on_ok_clicked(self):
        """Xử lý khi nhấn OK - áp dụng lượng sửa."""
        corrections = self.get_corrections()

        # KHÔNG cập nhật config - chỉ gửi lượng sửa để UI hiển thị
        # Gọi callback nếu có (để cập nhật UI với lượng sửa)
        if hasattr(self, 'on_angles_updated') and callable(self.on_angles_updated):
            self.on_angles_updated(corrections)

        # Ẩn widget
        self.hide()

    def on_cancel_clicked(self):
        """Xử lý khi nhấn Cancel - đóng mà không áp dụng."""
        self.hide()

    def on_reset_clicked(self):
        """Xử lý khi nhấn Reset - reset tất cả các input về giá trị mặc định."""
        # Reset các input gió về 0 (các input này mặc định là 0)
        for input_field in self.wind_speed_inputs + self.wind_dir_inputs:
            input_field.setText("0")
        
        # Reset áp suất, nhiệt độ về giá trị tiêu chuẩn (KHÔNG phải 0)
        self.air_density_input.setText(str(self.standard_pressure))  # 750 mmHg
        self.air_temp_input.setText(str(self.standard_temp))  # 15.9 °C
        self.charge_temp_input.setText(str(self.standard_charge_temp))  # 15 °C
        
        # Reset thuốc phóng kacn-14 và góc tạ về 0
        self.kacn_input.setText("0")
        self.target_angle_input.setText("0")
        
        # Reset các input thủ công về 0
        self.manual_elevation_left_input.setText("0")
        self.manual_elevation_right_input.setText("0")
        self.manual_direction_left_input.setText("0")
        self.manual_direction_right_input.setText("0")
        
        # Đảm bảo giá trị tiêu chuẩn không thay đổi
        self.std_temp_input.setText(str(self.standard_temp))
        self.std_pressure_input.setText(str(self.standard_pressure))
        self.std_charge_temp_input.setText(str(self.standard_charge_temp))
        
        # Reset về chế độ tự động nếu đang ở chế độ thủ công
        if not self.toggle_switch.is_auto:
            self.toggle_switch.is_auto = True
            self.toggle_switch.update()
            self.on_mode_changed(True)
        
        # Cập nhật lại hiển thị
        self.update_angle_display()

    def connect_signals(self):
        """Kết nối các signals để tự động cập nhật khi input thay đổi."""
        # Kết nối tất cả các input fields để tự động cập nhật
        for input_field in self.wind_speed_inputs + self.wind_dir_inputs:
            input_field.textChanged.connect(self.update_angle_display)

        self.air_density_input.textChanged.connect(self.update_angle_display)
        self.air_temp_input.textChanged.connect(self.update_angle_display)
        self.charge_temp_input.textChanged.connect(self.update_angle_display)
        self.kacn_input.textChanged.connect(self.update_angle_display)
        self.target_angle_input.textChanged.connect(self.update_angle_display)

        # Kết nối input fields của mode thủ công
        self.manual_elevation_left_input.textChanged.connect(self.update_angle_display)
        self.manual_direction_left_input.textChanged.connect(self.update_angle_display)
        self.manual_elevation_right_input.textChanged.connect(self.update_angle_display)
        self.manual_direction_right_input.textChanged.connect(self.update_angle_display)

        # Kết nối giá trị tiêu chuẩn
        self.std_temp_input.textChanged.connect(self.update_angle_display)
        self.std_pressure_input.textChanged.connect(self.update_angle_display)
        self.std_charge_temp_input.textChanged.connect(self.update_angle_display)

    def on_mode_changed(self, is_auto):
        """Xử lý khi chuyển đổi giữa tự động và thủ công."""
        # Enable/disable các input thủ công
        # Khi tự động: disable, khi thủ công: enable
        self.manual_elevation_left_input.setEnabled(not is_auto)
        self.manual_direction_left_input.setEnabled(not is_auto)
        self.manual_elevation_right_input.setEnabled(not is_auto)
        self.manual_direction_right_input.setEnabled(not is_auto)

        # Enable/disable các input bên trái
        # Khi tự động: enable, khi thủ công: disable
        for input_field in self.wind_speed_inputs + self.wind_dir_inputs:
            input_field.setEnabled(is_auto)

        self.air_density_input.setEnabled(is_auto)
        self.air_temp_input.setEnabled(is_auto)
        self.charge_temp_input.setEnabled(is_auto)
        self.kacn_input.setEnabled(is_auto)
        self.target_angle_input.setEnabled(is_auto)

        # Cập nhật lại góc khi chuyển mode
        self.update_angle_display()

    def calculate_corrections(self):
        """Tính toán lượng sửa dựa trên các thông số cho cả trái và phải.
        
        CÔNG THỨC GIẢ - CẦN CHỈNH SỬA LẠI THEO YÊU CẦU THỰC TẾ
        
        Returns:
            tuple: (elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr)
        """
        from common.utils import get_firing_table_interpolator, get_slope_correction_table
        
        try:
            # ========== LẤY INPUT TỪ CỘT BÊN TRÁI ==========
            # Gió
            wind_along_low = float(self.wind_speed_inputs[0].text() or 0)    # Gió dọc thấp (m/s)
            wind_along_high = float(self.wind_speed_inputs[1].text() or 0)   # Gió dọc cao (m/s)
            wind_cross_low = float(self.wind_dir_inputs[0].text() or 0)      # Gió ngang thấp (m/s)
            wind_cross_high = float(self.wind_dir_inputs[1].text() or 0)     # Gió ngang cao (m/s)
            
            # Môi trường
            air_pressure = float(self.air_density_input.text() or 0)         # Áp suất (mmHg)
            air_temp = float(self.air_temp_input.text() or 0)                # Nhiệt độ không khí (°C)
            charge_temp = float(self.charge_temp_input.text() or 0)          # Nhiệt độ liều phóng (°C)
            
            # Đạn và góc tà
            kacn14 = int(self.kacn_input.text() or 0)                        # Thuốc phóng kacn-14 (0 hoặc 1)
            slope_angle = float(self.target_angle_input.text() or 0)         # Góc tà mục tiêu (độ)
            
            # Giá trị tiêu chuẩn
            std_temp = float(self.std_temp_input.text() or self.standard_temp)
            std_pressure = float(self.std_pressure_input.text() or self.standard_pressure)
            std_charge_temp = float(self.std_charge_temp_input.text() or self.standard_charge_temp)
            
            # ========== LẤY DỮ LIỆU TỪ TABLE1 THEO KHOẢNG CÁCH ==========
            interpolator = get_firing_table_interpolator()
            if not interpolator:
                return 0, 0, 0, 0
            
            # Khoảng cách từ config
            X_left = config.DISTANCE_L   # Khoảng cách trái (m)
            X_right = config.DISTANCE_R  # Khoảng cách phải (m)
            
            # Nội suy các giá trị từ table1 cho TRÁI
            Z_left = interpolator.interpolate_z(X_left) if interpolator.z_data is not None else 0
            delta_Zwhz_left = interpolator.interpolate_delta_zwhz(X_left)
            delta_Zwbez_left = interpolator.interpolate_delta_zwbez(X_left)
            delta_Zwhx_left = interpolator.interpolate_delta_zwhx(X_left)
            delta_Xwhx_left = interpolator.interpolate_delta_xwhx(X_left)
            delta_Xwhz_left = interpolator.interpolate_delta_xwhz(X_left)
            delta_Xwbex_left = interpolator.interpolate_delta_xwbex(X_left)
            delta_Xkacn_left = interpolator.interpolate_delta_xkacn(X_left)
            delta_XH_left = interpolator.interpolate_delta_xh(X_left)
            delta_XT_left = interpolator.interpolate_delta_xt(X_left)
            delta_XTsz_left = interpolator.interpolate_delta_xtsz(X_left)
            delta_XTbic_left = interpolator.interpolate_delta_xtbic(X_left)
            
            # Nội suy các giá trị từ table1 cho PHẢI
            Z_right = interpolator.interpolate_z(X_right) if interpolator.z_data is not None else 0
            delta_Zwhz_right = interpolator.interpolate_delta_zwhz(X_right)
            delta_Zwbez_right = interpolator.interpolate_delta_zwbez(X_right)
            delta_Zwhx_right = interpolator.interpolate_delta_zwhx(X_right)
            delta_Xwhx_right = interpolator.interpolate_delta_xwhx(X_right)
            delta_Xwhz_right = interpolator.interpolate_delta_xwhz(X_right)
            delta_Xwbex_right = interpolator.interpolate_delta_xwbex(X_right)
            delta_Xkacn_right = interpolator.interpolate_delta_xkacn(X_right)
            delta_XH_right = interpolator.interpolate_delta_xh(X_right)
            delta_XT_right = interpolator.interpolate_delta_xt(X_right)
            delta_XTsz_right = interpolator.interpolate_delta_xtsz(X_right)
            delta_XTbic_right = interpolator.interpolate_delta_xtbic(X_right)
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC TẦM (TRÁI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            elev_correction_left_mils = (
                # Ảnh hưởng nhiệt độ
                delta_XT_left * (air_temp - std_temp)*0.1 +
                delta_XTsz_left * (charge_temp - std_charge_temp)*0.1 +
                
                # Ảnh hưởng áp suất/độ cao
                delta_XH_left * (air_pressure - std_pressure) * 0.1 +
                
                # Ảnh hưởng gió dọc
                delta_Xwhx_left * wind_along_low * 0.1 +
                delta_Xwbex_left * wind_along_high * 0.1 +
                
                # Ảnh hưởng gió ngang lên góc tầm
                delta_Xwhz_left * wind_cross_low * 0.1 +
                
                # Ảnh hưởng thuốc phóng kacn-14
                delta_Xkacn_left * kacn14
            ) / delta_XTbic_left if delta_XTbic_left !=0 else 0
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC TẦM (PHẢI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            elev_correction_right_mils = (
                # Ảnh hưởng nhiệt độ
                delta_XT_right * (air_temp - std_temp) * 0.1 +
                delta_XTsz_right * (charge_temp - std_charge_temp) * 0.1 +

                # Ảnh hưởng áp suất/độ cao
                delta_XH_right * (air_pressure - std_pressure) * 0.1 +
                
                # Ảnh hưởng gió dọc
                delta_Xwhx_right * wind_along_low * 0.1 +
                delta_Xwbex_right * wind_along_high * 0.1 +
                
                # Ảnh hưởng gió ngang lên góc tầm
                delta_Xwhz_right * wind_cross_low * 0.1 +

                # Ảnh hưởng thuốc phóng kacn-14
                delta_Xkacn_right * kacn14
            ) / delta_XTbic_right if delta_XTbic_right != 0 else 0
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC HƯỚNG (TRÁI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            dir_correction_left_mils = (
                # Ảnh hưởng gió ngang lên góc hướng
                delta_Zwhz_left * wind_cross_low * 0.1 +
                delta_Zwhx_left * wind_along_low * 0.1 +
                delta_Zwbez_left * wind_cross_high * 0.1
            )
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC HƯỚNG (PHẢI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            dir_correction_right_mils = (
                # Ảnh hưởng gió ngang lên góc hướng
                delta_Zwhz_right * wind_cross_low * 0.1 +
                delta_Zwhx_right * wind_along_low * 0.1 +
                delta_Zwbez_right * wind_cross_high * 0.1
            )
            
            # ========== THÊM LƯỢNG SỬA CHÊNH TÀ TỪ TABLE2 (NẾU CÓ) ==========
            if slope_angle != 0:
                slope_table = get_slope_correction_table()
                if slope_table:
                    # Lấy ly giác hiện tại từ góc tầm mục tiêu
                    current_elev_mils_left = config.AIM_ANGLE_L / 0.05625  # Chuyển độ về ly giác
                    current_elev_mils_right = config.AIM_ANGLE_R / 0.05625
                    
                    # Tra bảng table2
                    try:
                        p_correction_left_mils = slope_table.lookup(slope_angle, current_elev_mils_left)
                        p_correction_right_mils = slope_table.lookup(slope_angle, current_elev_mils_right)
                        
                        # Cộng thêm vào lượng sửa góc tầm
                        elev_correction_left_mils += p_correction_left_mils
                        elev_correction_right_mils += p_correction_right_mils
                    except Exception as e:
                        print(f"Lỗi tra bảng chênh tà: {e}")
            
            # ========== CHUYỂN ĐỔI TỪ LY GIÁC SANG ĐỘ ==========
            elev_left_corr = elev_correction_left_mils * 0.05625
            elev_right_corr = elev_correction_right_mils * 0.05625
            dir_left_corr = dir_correction_left_mils * 0.05625
            dir_right_corr = dir_correction_right_mils * 0.05625
            
            return elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr

        except Exception as e:
            print(f"Lỗi tính toán lượng sửa: {e}")
            return 0, 0, 0, 0

    def update_angle_display(self):
        """Cập nhật hiển thị góc tầm và góc hướng."""
        # ĐỌC TRỰC TIẾP từ config
        # Góc MỤC TIÊU (từ nội suy bảng bắn) - đây là góc cơ sở để áp dụng lượng sửa
        aim_elevation_left = config.AIM_ANGLE_L
        aim_elevation_right = config.AIM_ANGLE_R
        aim_direction_left = config.AIM_DIRECTION_L
        aim_direction_right = config.AIM_DIRECTION_R
        
        if self.toggle_switch.is_auto:
            # Chế độ tự động - tính toán lượng sửa cho cả trái và phải
            elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr = self.calculate_corrections()

            # Hiển thị góc mặc định (góc mục tiêu từ nội suy) - cả trái và phải
            self.angle_cells['default_elevation_left'].setText(f"{aim_elevation_left:.1f}°")
            self.angle_cells['default_elevation_right'].setText(f"{aim_elevation_right:.1f}°")
            self.angle_cells['default_direction_left'].setText(f"{aim_direction_left:.1f}°")
            self.angle_cells['default_direction_right'].setText(f"{aim_direction_right:.1f}°")

            # Hiển thị góc sau khi áp dụng lượng sửa (góc mục tiêu + lượng sửa)
            corrected_elevation_left = aim_elevation_left + elev_left_corr
            corrected_elevation_right = aim_elevation_right + elev_right_corr
            corrected_direction_left = aim_direction_left + dir_left_corr
            corrected_direction_right = aim_direction_right + dir_right_corr

            self.angle_cells['corrected_elevation_left'].setText(f"{corrected_elevation_left:.1f}°")
            self.angle_cells['corrected_elevation_right'].setText(f"{corrected_elevation_right:.1f}°")
            self.angle_cells['corrected_direction_left'].setText(f"{corrected_direction_left:.1f}°")
            self.angle_cells['corrected_direction_right'].setText(f"{corrected_direction_right:.1f}°")

        else:
            # Chế độ thủ công - lấy lượng sửa từ input (đơn vị: ly giác)
            try:
                elev_left_corr_mils = float(self.manual_elevation_left_input.text() or 0)
                elev_right_corr_mils = float(self.manual_elevation_right_input.text() or 0)
                dir_left_corr_mils = float(self.manual_direction_left_input.text() or 0)
                dir_right_corr_mils = float(self.manual_direction_right_input.text() or 0)
                
                # Chuyển đổi từ ly giác sang độ: 1 ly giác = 0.05625 độ
                elev_left_corr = elev_left_corr_mils * 0.05625
                elev_right_corr = elev_right_corr_mils * 0.05625
                dir_left_corr = dir_left_corr_mils * 0.05625
                dir_right_corr = dir_right_corr_mils * 0.05625
            except ValueError:
                elev_left_corr = 0
                elev_right_corr = 0
                dir_left_corr = 0
                dir_right_corr = 0

            # Hiển thị góc mặc định (góc mục tiêu từ nội suy)
            self.angle_cells['default_elevation_left'].setText(f"{aim_elevation_left:.1f}°")
            self.angle_cells['default_direction_left'].setText(f"{aim_direction_left:.1f}°")
            self.angle_cells['default_elevation_right'].setText(f"{aim_elevation_right:.1f}°")
            self.angle_cells['default_direction_right'].setText(f"{aim_direction_right:.1f}°")

            # Hiển thị góc sau khi áp dụng lượng sửa (góc mục tiêu + lượng sửa đã chuyển sang độ)
            corrected_elevation_left = aim_elevation_left + elev_left_corr
            corrected_elevation_right = aim_elevation_right + elev_right_corr
            corrected_direction_left = aim_direction_left + dir_left_corr
            corrected_direction_right = aim_direction_right + dir_right_corr

            self.angle_cells['corrected_elevation_left'].setText(f"{corrected_elevation_left:.1f}°")
            self.angle_cells['corrected_direction_left'].setText(f"{corrected_direction_left:.1f}°")
            self.angle_cells['corrected_elevation_right'].setText(f"{corrected_elevation_right:.1f}°")
            self.angle_cells['corrected_direction_right'].setText(f"{corrected_direction_right:.1f}°")

    def get_corrections(self):
        """Lấy lượng sửa (không bao gồm góc gốc) - đã chuyển đổi sang độ."""
        if self.toggle_switch.is_auto:
            # Chế độ tự động - calculate_corrections() đã trả về giá trị bằng độ
            elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr = self.calculate_corrections()
        else:
            # Chế độ thủ công - cần chuyển từ ly giác sang độ
            try:
                elev_left_corr_mils = float(self.manual_elevation_left_input.text() or 0)
                elev_right_corr_mils = float(self.manual_elevation_right_input.text() or 0)
                dir_left_corr_mils = float(self.manual_direction_left_input.text() or 0)
                dir_right_corr_mils = float(self.manual_direction_right_input.text() or 0)
                
                # Chuyển đổi từ ly giác sang độ: 1 ly giác = 0.05625 độ
                elev_left_corr = elev_left_corr_mils * 0.05625
                elev_right_corr = elev_right_corr_mils * 0.05625
                dir_left_corr = dir_left_corr_mils * 0.05625
                dir_right_corr = dir_right_corr_mils * 0.05625
            except ValueError:
                elev_left_corr = 0
                elev_right_corr = 0
                dir_left_corr = 0
                dir_right_corr = 0

        return {
            'elevation_correction_left': elev_left_corr,
            'elevation_correction_right': elev_right_corr,
            'direction_correction_left': dir_left_corr,
            'direction_correction_right': dir_right_corr
        }

    def get_corrected_angles(self):
        """Lấy góc đã được điều chỉnh (góc gốc + lượng sửa)."""
        # ĐỌC TRỰC TIẾP từ config để luôn có giá trị mới nhất từ cảm biến
        current_elevation_left = config.ANGLE_L
        current_elevation_right = config.ANGLE_R
        current_direction_left = config.DIRECTION_L
        current_direction_right = config.DIRECTION_R
        
        corrections = self.get_corrections()

        return {
            'elevation_left': current_elevation_left + corrections['elevation_correction_left'],
            'elevation_right': current_elevation_right + corrections['elevation_correction_right'],
            'direction_left': current_direction_left + corrections['direction_correction_left'],
            'direction_right': current_direction_right + corrections['direction_correction_right'],
            'elevation_correction_left': corrections['elevation_correction_left'],
            'elevation_correction_right': corrections['elevation_correction_right'],
            'direction_correction_left': corrections['direction_correction_left'],
            'direction_correction_right': corrections['direction_correction_right']
        }

    def apply_styles(self):
        """Áp dụng stylesheet chung cho widget."""
        # Chỉ áp dụng cho widget chính (dùng ID selector)
        self.setStyleSheet("""
            #ballistic_calculator_main {
                background-color: #000000;
                border: 3px solid #FFFFFF;
            }
        """)
