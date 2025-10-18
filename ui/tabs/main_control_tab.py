from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from ..widgets.compass_widget import AngleCompass
from ..widgets.half_compass_widget import HalfCircleWidget
from ..widgets.numeric_display_widget import NumericDataWidget
from ..widgets.ammunition_widget import BulletWidget
from ..widgets.custom_message_box_widget import CustomMessageBox
from ..widgets.ballistic_calculator_dialog import BallisticCalculatorWidget
from ..components.ui_utilities import ColoredSVGButton
import ui.ui_config as config
from communication.data_sender import sender
import yaml
import random
import math
from common.utils import resource_path, get_firing_table_interpolator

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

class MainTab(GridBackgroundWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data
        self._data_timer = None  # Thêm biến timer
        self._buttons_active_state = False  # Theo dõi trạng thái hiện tại của OK/Cancel button
        self._launch_all_active_state = False  # Theo dõi trạng thái hiện tại của Launch All button
        
        # Lưu lượng sửa từ ballistic calculator
        self.elevation_correction_left = 0
        self.elevation_correction_right = 0
        self.direction_correction_left = 0
        self.direction_correction_right = 0
        
        self.setupUi()

    def setupUi(self):
        # Tạo các compass từ config
        compass_left_config = self.config['Widgets']['CompassLeft']
        self.compass_left = AngleCompass(35, 35, compass_left_config.get('redlines', [210, 330]), 0, self)
        
        self.compass_left.setGeometry(QtCore.QRect(
            compass_left_config['x'], compass_left_config['y'] + 34,
            compass_left_config['width'], compass_left_config['height'])
        )
        
        self.compass_left.setStyleSheet(compass_left_config['style'])

        half_left_config = self.config['Widgets']['HalfCompassLeft']
        self.half_compass_left = HalfCircleWidget(15, 20, self)
        
        # Điều chỉnh vị trí để căn chỉnh chính xác với compass và cùng y với HalfCompassLeft
        self.half_compass_left.setGeometry(QtCore.QRect(
            half_left_config['x'],  # Sử dụng x từ config
            half_left_config['y'] + 30,  # Cùng offset với các widget khác
            half_left_config['width'], half_left_config['height'])
        )
        
        self.half_compass_left.setStyleSheet(half_left_config['style'])

        compass_right_config = self.config['Widgets']['CompassRight']
        self.compass_right = AngleCompass(45, 40, compass_right_config.get('redlines', [210, 330]), 0, self)
        
        self.compass_right.setGeometry(QtCore.QRect(
            compass_right_config['x'], compass_right_config['y'] + 34,
            compass_right_config['width'], compass_right_config['height'])
        )
        
        self.compass_right.setStyleSheet(compass_right_config['style'])

        half_right_config = self.config['Widgets']['HalfCompassRight']
        self.half_compass_right = HalfCircleWidget(30, 25, self)
        
        # Điều chỉnh vị trí để có cùng y với HalfCompassLeft, dịch lên trên 10px
        self.half_compass_right.setGeometry(QtCore.QRect(
            half_right_config['x'],  # Sử dụng x từ config
            half_left_config['y'] + 30,  # Dịch lên trên 10px so với HalfCompassLeft
            half_right_config['width'], half_right_config['height'])
        )
        
        self.half_compass_right.setStyleSheet(half_right_config['style'])

        # Thêm NumericDataWidget từ config
        numeric_config = self.config['Widgets']['NumericDataWidget']
        self.numeric_data_widget = NumericDataWidget()
        self.numeric_data_widget.setParent(self)
        
        self.numeric_data_widget.setGeometry(QtCore.QRect(
            numeric_config['x'], numeric_config['y'] + 34,
            numeric_config['width'], numeric_config['height'])
        )

        # Thêm các nút từ config
        # OK Button (Xác nhận) với SVG icon màu trắng và hiệu ứng isometric
        ok_config = self.config['Widgets']['Buttons']['OK']
        self.ok_button = ColoredSVGButton.create_isometric_button(self)
        
        self.ok_button.setGeometry(QtCore.QRect(
            ok_config['x'], ok_config['y'] + 34,
            ok_config['width'], ok_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        btn_colors = self.config.get('ButtonColors', {})
        enabled = btn_colors.get('enabled', {})
        ColoredSVGButton.setup_button(
            self.ok_button, 
            "assets/Icons/launch.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Cancel Button với SVG icon màu trắng và hiệu ứng isometric
        cancel_config = self.config['Widgets']['Buttons']['Cancel']
        self.cancel_button = ColoredSVGButton.create_isometric_button(self)
        
        self.cancel_button.setGeometry(QtCore.QRect(
            cancel_config['x'], cancel_config['y'] + 34,
            cancel_config['width'], cancel_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        ColoredSVGButton.setup_button(
            self.cancel_button, 
            "assets/Icons/cancel.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Launch All Button với SVG icon màu trắng và hiệu ứng isometric
        launch_config = self.config['Widgets']['Buttons']['LaunchAll']
        self.launch_all_button = ColoredSVGButton.create_isometric_button(self)
        
        self.launch_all_button.setGeometry(QtCore.QRect(
            launch_config['x'], launch_config['y'] + 34,
            launch_config['width'], launch_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        ColoredSVGButton.setup_button(
            self.launch_all_button, 
            "assets/Icons/launch_all.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Calculator Button với SVG icon màu trắng và hiệu ứng isometric
        calc_config = self.config['Widgets']['Buttons']['Calculator']
        self.calculator_button = ColoredSVGButton.create_isometric_button(self)
        
        self.calculator_button.setGeometry(QtCore.QRect(
            calc_config['x'], calc_config['y'] + 34,
            calc_config['width'], calc_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        ColoredSVGButton.setup_button(
            self.calculator_button, 
            "assets/Icons/calculator.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Tạo BulletWidget từ config
        bullet_config = self.config['Widgets']['BulletWidget']
        self.bullet_widget = BulletWidget(self)
        
        self.bullet_widget.setGeometry(QtCore.QRect(
            bullet_config['x'], bullet_config['y'] + 34 - 10,  # Dịch lên 10px
            bullet_config['width'], bullet_config['height'])
        )

        self.retranslateUi()
        self.make_connection()
        # Khởi tạo trạng thái nút ban đầu
        self._update_action_buttons_state()
        # Khởi động timer để update dữ liệu liên tục
        self._data_timer = QtCore.QTimer()
        self._data_timer.timeout.connect(self.update_data)
        self._data_timer.start(100)  # 100ms, có thể chỉnh lại nếu muốn nhanh/chậm hơn

    def retranslateUi(self):
        pass  # No translation needed here

    def make_connection(self):
        self.ok_button.clicked.connect(self.on_ok_button_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)
        self.launch_all_button.clicked.connect(self.on_launch_all_button_clicked)
        self.calculator_button.clicked.connect(self.on_calculator_button_clicked)

    def on_ok_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút OK."""
        left_selected = self.bullet_widget.left_selected_launchers
        right_selected = self.bullet_widget.right_selected_launchers
        if not (left_selected or right_selected):
            CustomMessageBox.warning(
                "Cảnh báo",
                "Chưa chọn ống phóng nào!"
            )
            return

        # Hiển thị message box xác nhận
        selected_count = len(left_selected) + len(right_selected)
        if CustomMessageBox.question(
            "Xác nhận phóng",
            f"Bạn có chắc chắn muốn phóng {selected_count} ống đã chọn?"
        ) == QMessageBox.Yes:
            # Cập nhật trạng thái các ống phóng đã chọn thành không sẵn sàng
            new_left_status = self.bullet_widget.left_launcher_status.copy()
            new_right_status = self.bullet_widget.right_launcher_status.copy()
            
            for idx in left_selected:
                new_left_status[idx-1] = False
            for idx in right_selected:
                new_right_status[idx-1] = False
                
            # Cập nhật trạng thái
            self.bullet_widget._update_launcher_status("Giàn trái", new_left_status)
            self.bullet_widget._update_launcher_status("Giàn phải", new_right_status)
            config.AMMO_L = new_left_status
            config.AMMO_R = new_right_status
            
            # Gửi lệnh qua CAN bus và kiểm tra kết quả
            can_success = True
            if len(left_selected) > 0:
                if not sender(0x31, left_selected):
                    can_success = False
            if len(right_selected) > 0:
                if not sender(0x32, right_selected):
                    can_success = False
            
            # Ghi log và thông báo kết quả
            from ui.tabs.event_log_tab import LogTab
            
            if can_success:
                success_msg = f"Đã phóng thành công {selected_count} ống (Trái: {len(left_selected)}, Phải: {len(right_selected)})"
                LogTab.log(success_msg, "SUCCESS")
                CustomMessageBox.information(
                    "Thông báo",
                    f"Đã phóng thành công {selected_count} ống!"
                )
            else:
                warning_msg = f"Đã cập nhật trạng thái {selected_count} ống nhưng không thể gửi lệnh qua CAN bus"
                LogTab.log(warning_msg, "WARNING")
                CustomMessageBox.warning(
                    "Cảnh báo",
                    f"Đã cập nhật trạng thái {selected_count} ống!\n"
                    f"Tuy nhiên không thể gửi lệnh qua CAN bus.\n"
                    f"Vui lòng kiểm tra kết nối thiết bị CAN."
                )
            
            # Cập nhật trạng thái nút sau khi phóng
            self._update_action_buttons_state()
        else:
            CustomMessageBox.information(
                "Thông báo",
                "Đã hủy phóng!"
            )
            self.on_cancel_button_clicked()

    def on_cancel_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Cancel."""
        # Xóa danh sách các ống phóng đã chọn
        self.bullet_widget.left_selected_launchers.clear()
        self.bullet_widget.right_selected_launchers.clear()
        
        # Cập nhật lại giao diện
        self.bullet_widget._update_launcher_status("Giàn trái", 
                                                self.bullet_widget.left_launcher_status)
        self.bullet_widget._update_launcher_status("Giàn phải", 
                                                self.bullet_widget.right_launcher_status)
        
        # Cập nhật trạng thái nút
        self._update_action_buttons_state()

    def on_launch_all_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Launch All."""
        # Chọn tất cả các ống phóng sẵn sàng
        
        self.bullet_widget.left_selected_launchers.clear()
        self.bullet_widget.right_selected_launchers.clear()

        for idx in range(18):
            if self.bullet_widget.left_launcher_status[idx]:
                self.bullet_widget.left_selected_launchers.append(idx + 1)
            if self.bullet_widget.right_launcher_status[idx]:
                self.bullet_widget.right_selected_launchers.append(idx + 1)
        
        # Cập nhật giao diện để hiển thị các ống phóng đã chọn
        self.bullet_widget._update_launcher_status("Giàn trái", self.bullet_widget.left_launcher_status)
        self.bullet_widget._update_launcher_status("Giàn phải", self.bullet_widget.right_launcher_status)
        # Gọi hàm xử lý OK để phóng
        self.on_ok_button_clicked()

    def on_calculator_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Calculator."""
        # Nếu widget chưa được tạo, tạo mới
        if not hasattr(self, 'calculator_widget'):
            self.calculator_widget = BallisticCalculatorWidget(self)
            # Đặt widget chiếm toàn bộ diện tích của tab (không bị che bởi tab bar)
            self.calculator_widget.setGeometry(0, 34, self.width(), self.height() - 34)
            self.calculator_widget.raise_()  # Đưa lên trên cùng
            
            # Gán callback để cập nhật half-compass widgets khi áp dụng lượng sửa
            self.calculator_widget.on_angles_updated = self.update_half_compass_angles

        # Toggle hiển thị widget
        if self.calculator_widget.isVisible():
            self.calculator_widget.hide()
        else:
            # Cập nhật lại size khi hiển thị (trong trường hợp window bị resize)
            self.calculator_widget.setGeometry(0, 34, self.width(), self.height() - 34)

            # Cập nhật lại góc hiện tại trước khi hiển thị
            self.calculator_widget.current_elevation_left = config.ANGLE_L
            self.calculator_widget.current_direction_left = config.DIRECTION_L
            self.calculator_widget.current_elevation_right = config.ANGLE_R
            self.calculator_widget.current_direction_right = config.DIRECTION_R
            self.calculator_widget.update_angle_display()
            self.calculator_widget.show()

    def update_half_compass_angles(self, corrections):
        """Lưu lượng sửa từ ballistic calculator - sẽ được áp dụng trong update_data()."""
        print(f"[DEBUG] Lưu lượng sửa:")
        print(f"  Elevation correction L: {corrections['elevation_correction_left']:.1f}° | R: {corrections['elevation_correction_right']:.1f}°")
        print(f"  Direction correction L: {corrections['direction_correction_left']:.1f}° | R: {corrections['direction_correction_right']:.1f}°")
        
        # Chỉ lưu lượng sửa, không thay đổi config
        self.elevation_correction_left = corrections['elevation_correction_left']
        self.elevation_correction_right = corrections['elevation_correction_right']
        self.direction_correction_left = corrections['direction_correction_left']
        self.direction_correction_right = corrections['direction_correction_right']
        
        # Lượng sửa sẽ được áp dụng tự động trong update_data()

    def _update_action_buttons_state(self):
        """Cập nhật trạng thái và giao diện của OK Button và Cancel Button dựa trên việc có nút nào được chọn."""
        has_selection = (len(self.bullet_widget.left_selected_launchers) > 0 or 
                         len(self.bullet_widget.right_selected_launchers) > 0)
        btn_colors = self.config.get('ButtonColors', {})

        # Kiểm tra có ống phóng nào sẵn sàng không (cho Launch All button)
        has_ready_launchers = (any(self.bullet_widget.left_launcher_status) or 
                               any(self.bullet_widget.right_launcher_status))

        # Luôn cập nhật OK Button và Cancel Button với màu mới từ config
        if has_selection:
            # Có nút được chọn - sử dụng màu enabled thay vì selected
            enabled = btn_colors.get('enabled', {})
            ColoredSVGButton.setup_button(
                self.ok_button, 
                "assets/Icons/launch.svg",
                icon_color=enabled.get("icon_color", "#000000"),
                icon_alpha=255,  # Icon không mờ khi enabled
                icon_size=(80, 80),
                top_color=enabled.get("top_color", "#ffffff"),
                border_color=enabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            ColoredSVGButton.setup_button(
                self.cancel_button, 
                "assets/Icons/cancel.svg",
                icon_color=enabled.get("icon_color", "#000000"),
                icon_alpha=255,  # Icon không mờ khi enabled
                icon_size=(80, 80),
                top_color=enabled.get("top_color", "#ffffff"),
                border_color=enabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            # Tăng độ cao isometric gấp đôi (từ 6 lên 12)
            self.ok_button.offset_y = 12
            self.cancel_button.offset_y = 12
            # Bật chức năng bấm
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
        else:
            # Không có nút nào được chọn - nút màu đen, SVG màu trắng, độ cao isometric bình thường
            disabled = btn_colors.get('disabled', {})
            ColoredSVGButton.setup_button(
                self.ok_button, 
                "assets/Icons/launch.svg",
                icon_color=disabled.get("icon_color", "#ffffff"),
                icon_alpha=disabled.get("icon_alpha", 48),
                icon_size=(80, 80),
                top_color=disabled.get("top_color", "#121212"),
                border_color=disabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            ColoredSVGButton.setup_button(
                self.cancel_button, 
                "assets/Icons/cancel.svg",
                icon_color=disabled.get("icon_color", "#ffffff"),
                icon_alpha=disabled.get("icon_alpha", 48),
                icon_size=(80, 80),
                top_color=disabled.get("top_color", "#121212"),
                border_color=disabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            # Khôi phục độ cao isometric ban đầu
            self.ok_button.offset_y = 6
            self.cancel_button.offset_y = 6
            # Tắt chức năng bấm
            self.ok_button.setEnabled(False)
            self.cancel_button.setEnabled(False)

        # Luôn cập nhật Launch All Button với màu mới từ config
        if has_ready_launchers:
            enabled = btn_colors.get('enabled', {})
            ColoredSVGButton.setup_button(
                self.launch_all_button, 
                "assets/Icons/launch_all.svg",
                icon_color=enabled.get("icon_color", "#000000"),
                icon_alpha=255,  # Icon không mờ khi enabled
                icon_size=(80, 80),
                top_color=enabled.get("top_color", "#ffffff"),
                border_color=enabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            self.launch_all_button.offset_y = 12
            self.launch_all_button.setEnabled(True)
        else:
            disabled = btn_colors.get('disabled', {})
            ColoredSVGButton.setup_button(
                self.launch_all_button, 
                "assets/Icons/launch_all.svg",
                icon_color=disabled.get("icon_color", "#ffffff"),
                icon_alpha=disabled.get("icon_alpha", 48),
                icon_size=(80, 80),
                top_color=disabled.get("top_color", "#121212"),
                border_color=disabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            self.launch_all_button.offset_y = 6
            self.launch_all_button.setEnabled(False)

        # Calculator Button luôn luôn enabled với màu enabled
        enabled = btn_colors.get('enabled', {})
        ColoredSVGButton.setup_button(
            self.calculator_button, 
            "assets/Icons/calculator.svg",
            icon_color=enabled.get("icon_color", "#000000"),
            icon_alpha=255,  # Icon không mờ khi enabled
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#ffffff"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )
        self.calculator_button.offset_y = 12
        self.calculator_button.setEnabled(True)

        # Trigger repaint cho tất cả button
        self.ok_button.update()
        self.cancel_button.update()
        self.launch_all_button.update()
        self.calculator_button.update()

    def update_data(self):
        """Cập nhật các thông số, trang thái của các ống phóng và góc hướng hiện tại
        và góc tính toán từ hệ thống điều khiển bắn.
        """
        # Tính toán góc tầm MỤC TIÊU liên tục từ khoảng cách hiện tại
        interpolator = get_firing_table_interpolator()
        if interpolator:
            # AIM_ANGLE = góc mục tiêu (từ nội suy bảng bắn)
            config.AIM_ANGLE_L = interpolator.interpolate_angle(config.DISTANCE_L)
            config.AIM_ANGLE_R = interpolator.interpolate_angle(config.DISTANCE_R)
            # AIM_DIRECTION = hướng mục tiêu (từ tính toán targeting)
            config.AIM_DIRECTION_L = config.DIRECTION_L
            config.AIM_DIRECTION_R = config.DIRECTION_R
            # ANGLE_L/R và DIRECTION_L/R = góc/hướng HIỆN TẠI từ cảm biến (CAN bus)
            # Sẽ được cập nhật từ data_receiver khi nhận CAN bus 0x200, 0x201
        
        self.bullet_widget._update_launcher_status("Giàn trái", config.AMMO_L)
        self.bullet_widget._update_launcher_status("Giàn phải", config.AMMO_R)
        
        # Cập nhật trạng thái của OK Button và Cancel Button
        self._update_action_buttons_state()
        w_direction = random.randint(30,60)  # Giả lập hướng của tàu so với địa lý (độ, 0 = Bắc)
        config.DISTANCE_L = random.uniform(4000, 5000)  # Giả lập khoảng cách đến mục tiêu (m)
        # DIRECTION_L/R = hướng hiện tại, AIM_DIRECTION_L/R = hướng mục tiêu
        # Áp dụng lượng sửa vào hướng mục tiêu hiển thị
        self.compass_left.update_angle(
            aim_direction=config.AIM_DIRECTION_L + self.direction_correction_left, 
            current_direction=config.DIRECTION_L, 
            w_direction=config.W_DIRECTION
        )
        self.compass_right.update_angle(
            aim_direction=config.AIM_DIRECTION_R + self.direction_correction_right, 
            current_direction=config.DIRECTION_R, 
            w_direction=config.W_DIRECTION
        )
        # self.compass_left.update_angle(aim_direction=-70, current_direction=-100, w_direction=config.W_DIRECTION)
        # self.compass_right.update_angle(aim_direction=90, current_direction=90, w_direction=w_direction)
        
        # ANGLE_L/R = góc hiện tại từ cảm biến, AIM_ANGLE_L/R = góc mục tiêu từ nội suy
        # Áp dụng lượng sửa (nếu có) vào góc mục tiêu hiển thị
        self.half_compass_left.update_angle(
            current_angle=config.ANGLE_L, 
            aim_angle=config.AIM_ANGLE_L + self.elevation_correction_left, 
            current_direction=config.DIRECTION_L, 
            aim_direction=config.AIM_DIRECTION_L + self.direction_correction_left
        )
        self.half_compass_right.update_angle(
            current_angle=config.ANGLE_R, 
            aim_angle=config.AIM_ANGLE_R + self.elevation_correction_right, 
            current_direction=config.DIRECTION_R, 
            aim_direction=config.AIM_DIRECTION_R + self.direction_correction_right
        )
        # self.half_compass_left.update_angle(current_angle=15, aim_angle=15,
        #                                     current_direction=45, aim_direction=16)
        # self.half_compass_right.update_angle(current_angle=45, aim_angle=45,
        #                                      current_direction=45, aim_direction=45)
        
        # Tính góc mục tiêu sau khi áp dụng lượng sửa (để hiển thị trong numeric display)
        aim_angle_left_corrected = config.AIM_ANGLE_L + self.elevation_correction_left
        aim_angle_right_corrected = config.AIM_ANGLE_R + self.elevation_correction_right
        aim_direction_left_corrected = config.AIM_DIRECTION_L + self.direction_correction_left
        aim_direction_right_corrected = config.AIM_DIRECTION_R + self.direction_correction_right
        
        self.numeric_data_widget.update_data(
            **{
                "Hướng ngắm hiện tại (độ)": (f"{config.DIRECTION_L:.1f}", f"{config.DIRECTION_R:.1f}"),
                "Hướng ngắm mục tiêu (độ)": (f"{aim_direction_left_corrected:.1f}", f"{aim_direction_right_corrected:.1f}"),
                "Góc tầm hiện tại (độ)": (f"{config.ANGLE_L:.1f}", f"{config.ANGLE_R:.1f}"),
                "Góc tầm mục tiêu (độ)": (f"{aim_angle_left_corrected:.1f}", f"{aim_angle_right_corrected:.1f}"),
                "Pháo sẵn sàng": (str(sum(self.bullet_widget.left_launcher_status)), str(sum(self.bullet_widget.right_launcher_status))),
                "Pháo đã chọn": (str(len(self.bullet_widget.left_selected_launchers)), str(len(self.bullet_widget.right_selected_launchers))),
                "Khoảng cách (m)": (f"{config.DISTANCE_L:.2f}", f"{config.DISTANCE_R:.2f}")
            }
        )
