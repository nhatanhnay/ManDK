# -*- coding: utf-8 -*-

import math, os, sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class HalfCircleWidget(QWidget):
    _instance_counter = 0  # Class variable để đếm instance
    
    def __init__(self, current_angle, aim_angle, parent=None):
        super().__init__(parent)
        # Tạo ID duy nhất cho mỗi instance
        HalfCircleWidget._instance_counter += 1
        self._widget_id = f"Widget{HalfCircleWidget._instance_counter}"
        
        self._current_angle = current_angle
        self._aim_angle = aim_angle
        # Thêm các thuộc tính cho góc hướng (360 độ)
        self._current_direction = 0
        self._aim_direction = 0
        # Thêm flag để kiểm tra lần đầu tiên cập nhật
        self._first_update = True
        self.static_pixmap = None
        self._current_angle_anim = QPropertyAnimation(self, b"currentAngle")
        self._aim_angle_anim = QPropertyAnimation(self, b"aimAngle")
        self._current_angle_anim.setDuration(500)
        self._aim_angle_anim.setDuration(500)
        self._current_angle_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._aim_angle_anim.setEasingCurve(QEasingCurve.InOutQuad)

    def getCurrentAngle(self):
        return self._current_angle
    def setCurrentAngle(self, value):
        self._current_angle = value
        self.update()
    currentAngle = pyqtProperty(float, fget=getCurrentAngle, fset=setCurrentAngle)

    def getAimAngle(self):
        return self._aim_angle
    def setAimAngle(self, value):
        self._aim_angle = value
        self.update()
    aimAngle = pyqtProperty(float, fget=getAimAngle, fset=setAimAngle)

    def resizeEvent(self, event):
        """Vẽ lại giao diện tĩnh khi kích thước thay đổi."""
        # Only create static pixmap when we have a valid (non-zero) size
        w = max(0, self.width())
        h = max(0, self.height())
        if w <= 0 or h <= 0:
            self.static_pixmap = None
            return

        self.static_pixmap = QPixmap(w, h)
        self.static_pixmap.fill(Qt.transparent)
        painter = QPainter()
        if not painter.begin(self.static_pixmap):
            # If painter cannot begin, don't attempt to draw static content
            self.static_pixmap = None
            return
        painter.setRenderHint(QPainter.Antialiasing)

        # Thiết lập cho 2 wheel: 60 độ và 360 độ
        total_width = self.width()
        total_height = self.height()
        
        # Tính toán để 2 wheel chia đều chiều rộng
        wheel_width = total_width * 0.25  # Mỗi wheel chiếm 45% widget
        wheel_height = min(total_height * 0.75, 220)
        spacing = 20  # Khoảng cách giữa 2 wheel chỉ 20px
        
        # Căn giữa hoàn hảo trong widget
        center_y = total_height / 2
        total_wheel_width = 2 * wheel_width + spacing
        start_x = (total_width - total_wheel_width) / 2
        
        # Vị trí 2 wheel - căn giữa hoàn hảo
        left_wheel_center = QPointF(start_x + wheel_width/2, center_y)
        right_wheel_center = QPointF(start_x + wheel_width + spacing + wheel_width/2, center_y)

        # Vẽ wheel 60 độ bên trái
        self._draw_vertical_wheel_static(painter, left_wheel_center, wheel_width, wheel_height, is_360=False)
        # Vẽ wheel 360 độ bên phải
        self._draw_vertical_wheel_static(painter, right_wheel_center, wheel_width, wheel_height, is_360=True)
        if painter.isActive():
            painter.end()

    def update_angle(self, current_angle: float = 0, aim_angle: float = 0, 
                     current_direction: float = 0, aim_direction: float = 0) -> None:
        """Cập nhật góc tầm và góc hướng của giàn phóng với animation"""
        
        # Validate input values - nếu là None hoặc NaN thì dùng giá trị mặc định 0
        if current_angle is None or (isinstance(current_angle, float) and math.isnan(current_angle)):
            print(f"[WARNING] {self._widget_id}: current_angle is None or NaN, using 0")
            current_angle = 0
        if aim_angle is None or (isinstance(aim_angle, float) and math.isnan(aim_angle)):
            print(f"[WARNING] {self._widget_id}: aim_angle is None or NaN, using 0")
            aim_angle = 0
        if current_direction is None or (isinstance(current_direction, float) and math.isnan(current_direction)):
            print(f"[WARNING] {self._widget_id}: current_direction is None or NaN, using 0")
            current_direction = 0
        if aim_direction is None or (isinstance(aim_direction, float) and math.isnan(aim_direction)):
            print(f"[WARNING] {self._widget_id}: aim_direction is None or NaN, using 0")
            aim_direction = 0
        
        if self._first_update:
            # Lần đầu tiên: cập nhật trực tiếp mà không có animation
            self.setCurrentAngle(current_angle)
            self.setAimAngle(aim_angle)
            self._current_direction = current_direction
            self._aim_direction = aim_direction
            self._first_update = False
            self.update()  # Trigger repaint
            return
        
        # Animate current_angle (for 60° wheel) - TẮT ANIMATION TẠM THỜI
        # Update trực tiếp để tránh lỗi animation
        if abs(self._current_angle - current_angle) > 0:
            self.setCurrentAngle(current_angle)
        
        # Animate aim_angle (for 60° wheel) - TẮT ANIMATION TẠM THỜI
        # Update trực tiếp để tránh lỗi animation
        if abs(self._aim_angle - aim_angle) > 0:
            self.setAimAngle(aim_angle)
        
        # Update direction values (for 360° wheel) - no animation for now, just direct update
        self._current_direction = current_direction
        self._aim_direction = aim_direction
        self.update()  # Trigger repaint to show direction changes

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ phần tĩnh
        if self.static_pixmap:
            painter.drawPixmap(0, 0, self.static_pixmap)
            
        # Thiết lập cho 2 wheel: 60 độ và 360 độ
        total_width = self.width()
        total_height = self.height()
        
        # Tính toán để 2 wheel chia đều chiều rộng
        wheel_width = total_width * 0.25  # Mỗi wheel chiếm 45% widget
        wheel_height = min(total_height * 0.75, 220)
        spacing = 20  # Khoảng cách giữa 2 wheel chỉ 20px
        
        # Căn giữa hoàn hảo trong widget
        center_y = total_height / 2
        total_wheel_width = 2 * wheel_width + spacing
        start_x = (total_width - total_wheel_width) / 2
        
        # Vị trí 2 wheel - căn giữa hoàn hảo  
        left_wheel_center = QPointF(start_x + wheel_width/2, center_y)
        right_wheel_center = QPointF(start_x + wheel_width + spacing + wheel_width/2, center_y)
        
        # Vẽ wheel 60 độ bên trái (sử dụng current_angle và aim_angle)
        self._draw_vertical_wheel_dynamic(painter, left_wheel_center, wheel_width, wheel_height, 
                                        self._current_angle, self._aim_angle, is_360=False)
        # Vẽ wheel 360 độ bên phải (sử dụng current_direction và aim_direction)
        self._draw_vertical_wheel_dynamic(painter, right_wheel_center, wheel_width, wheel_height, 
                                        self._current_direction, self._aim_direction, is_360=True)
        
        # Vẽ đèn thông báo ở dưới cùng khi cả 2 wheel trùng khớp
        self._draw_status_light(painter, total_width, total_height, total_wheel_width, start_x)

    def _draw_vertical_wheel_static(self, painter: QPainter, center: QPointF, width: float, height: float, is_360: bool = False) -> None:
        """Vẽ phần tĩnh của vertical picker wheel - chỉ vẽ background wheel."""
        # Vẽ background wheel
        
        wheel_rect = QRectF(center.x() - width/2, center.y() - height/2, width, height)
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.setBrush(QColor(80, 80, 80, 100))
        painter.drawRoundedRect(wheel_rect, 10, 10)
        
        # Vẽ nhãn cho wheel
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white, 2))
        
        if is_360:
            label1 = "GÓC HƯỚNG"
        else:
            label1 = "GÓC TẦM"
            
        label_rect1 = QRectF(center.x() - width/2, center.y() - height/2 - 30, width, 15)
        painter.drawText(label_rect1, Qt.AlignCenter, label1)

    def _draw_vertical_wheel_dynamic(self, painter: QPainter, center: QPointF, width: float, height: float, 
                                   current_angle: float, aim_angle: float, is_360: bool = False) -> None:
        """Vẽ phần động của vertical picker wheel - wheel xoay để giá trị current_angle nằm ở thanh giữa, 
        và thanh kẻ ngang màu đỏ cố định cho aim_angle."""
        
        # Vẽ thanh liquid glass highlight cố định ở giữa wheel cho current_angle (phần động)
        highlight_rect = QRectF(center.x() - width/2 + 5, center.y() - 10, width - 10, 20)
        
        # Kiểm tra nếu current_angle/current_direction sai lệch ±1 hoặc bằng aim_angle/aim_direction
        if is_360:
            # Cho wheel 360 độ, so sánh current_direction với aim_direction (xử lý góc âm)
            angle_diff = min(abs(current_angle - aim_angle),
                           abs(current_angle - aim_angle + 360),
                           abs(current_angle - aim_angle - 360))
        else:
            # Cho wheel 60 độ, so sánh current_angle với aim_angle
            angle_diff = abs(current_angle - aim_angle)
        is_close_to_aim = angle_diff <= 1.0
        
        # Tạo hiệu ứng liquid glass với gradient trong suốt (không màu)
        from PyQt5.QtGui import QLinearGradient, QRadialGradient
        
        # Background glass với gradient - thay đổi màu dựa trên điều kiện
        glass_gradient = QLinearGradient(highlight_rect.topLeft(), highlight_rect.bottomRight())
        if is_close_to_aim:
            # Màu trắng không trong suốt khi close to aim
            glass_gradient.setColorAt(0, QColor(255, 255, 255, 200))   # Trắng đậm
            glass_gradient.setColorAt(0.5, QColor(255, 255, 255, 180)) # Trắng đậm
            glass_gradient.setColorAt(1, QColor(255, 255, 255, 220))   # Trắng rất đậm
        else:
            # Màu bình thường khi không close to aim
            glass_gradient.setColorAt(0, QColor(255, 255, 255, 30))   # Trắng trong suốt nhạt
            glass_gradient.setColorAt(0.5, QColor(255, 255, 255, 15)) # Trắng trong suốt rất nhạt
            glass_gradient.setColorAt(1, QColor(255, 255, 255, 40))   # Trắng trong suốt đậm hơn
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(glass_gradient)
        painter.drawRoundedRect(highlight_rect, 8, 8)
        
        # Thêm viền glass effect - cũng thay đổi theo điều kiện
        if is_close_to_aim:
            glass_border = QPen(QColor(255, 255, 255, 255), 2)  # Viền trắng đậm và dày hơn
        else:
            glass_border = QPen(QColor(255, 255, 255, 80), 1)   # Viền bình thường
        painter.setPen(glass_border)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(highlight_rect, 8, 8)
        
        # Thêm highlight shine effect - cũng thay đổi theo điều kiện
        shine_rect = QRectF(highlight_rect.x() + 2, highlight_rect.y() + 2, 
                           highlight_rect.width() - 4, highlight_rect.height() * 0.4)
        shine_gradient = QLinearGradient(shine_rect.topLeft(), shine_rect.bottomLeft())
        if is_close_to_aim:
            shine_gradient.setColorAt(0, QColor(255, 255, 255, 255))  # Shine đậm hơn
            shine_gradient.setColorAt(1, QColor(255, 255, 255, 120))
        else:
            shine_gradient.setColorAt(0, QColor(255, 255, 255, 60))   # Shine bình thường
            shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(shine_gradient)
        painter.drawRoundedRect(shine_rect, 6, 6)
        
        # Tính offset để wheel xoay sao cho current_angle nằm ở giữa (liquid glass)
        angle_range = 360 if is_360 else 60  # Xác định angle_range dựa trên is_360
        if is_360:
            # Cho wheel 360 độ, sử dụng cùng wheel_height_factor như wheel góc tầm để giãn ra
            wheel_height_factor = 0.7  # Giống hệt wheel góc tầm
            wheel_range = height * wheel_height_factor  # Phạm vi di chuyển trong wheel
        else:
            wheel_height_factor = 0.7
            wheel_range = height * wheel_height_factor  # Phạm vi di chuyển trong wheel
        
        # Logic đúng: để current_angle nằm ở center.y() (liquid glass)
        if is_360:
            # Cho wheel 360 độ, chuyển đổi current_direction thành vị trí trong range ±30 (tổng 60 độ)
            center_angle = self._current_direction if hasattr(self, '_current_direction') else 0
            # Current_direction luôn ở giữa range (tại vị trí 30 trong range 0-60)
            normalized_current = 0.5  # Luôn ở giữa
            wheel_offset = -(wheel_range/2 - normalized_current * wheel_range)
        else:
            # Cho wheel 60 độ, normalize trực tiếp
            normalized_current = current_angle / angle_range  # 0 đến 1
            wheel_offset = -(height/2 * wheel_height_factor - normalized_current * height * wheel_height_factor)
        
        # Vẽ các vạch chia độ với offset
        self._draw_vertical_marks_with_offset(painter, center, width, height, wheel_offset, is_360)
        
        # Vẽ thanh kẻ ngang màu trắng cố định cho aim_angle
        self._draw_white_horizontal_bar(painter, center, width, height, aim_angle, wheel_offset, is_360)
        
        # Hiển thị số current_angle bên dưới wheel với khung
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        # Text giá trị current_angle bên dưới wheel, căn giữa theo chiều ngang
        displayed_value = current_angle
        text_x = center.x() - width/2  # Bắt đầu từ cạnh trái wheel
        text_y = center.y() + height/2 + 15  # Bên dưới wheel với khoảng cách 15px
        value_rect1 = QRectF(text_x, text_y - 10, width, 20)  # Chiều ngang bằng với wheel
        
        # Vẽ nền khung cho text
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(60, 60, 60, 180))  # Nền xám đậm với độ trong suốt
        painter.drawRoundedRect(value_rect1, 5, 5)
        
        # Vẽ viền cho khung
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(value_rect1, 5, 5)
        
        # Vẽ text với màu trắng
        painter.setPen(QPen(Qt.white, 2))
        painter.drawText(value_rect1, Qt.AlignCenter, f"{displayed_value:.1f}°")

    def _draw_white_horizontal_bar(self, painter: QPainter, center: QPointF, width: float, height: float, 
                               aim_angle: float, wheel_offset: float, is_360: bool = False) -> None:
        """Vẽ thanh kẻ ngang cho aim_angle - màu đỏ bình thường, màu trắng khi gần chạm current_angle."""
        angle_range = 360 if is_360 else 60  # Xác định angle_range dựa trên is_360
        
        # Kiểm tra nếu current_angle/current_direction gần bằng aim_angle/aim_direction
        if is_360:
            # Cho wheel 360 độ, so sánh current_direction với aim_direction (xử lý góc âm)
            angle_diff = min(abs(self._current_direction - aim_angle),
                           abs(self._current_direction - aim_angle + 360),
                           abs(self._current_direction - aim_angle - 360))
        else:
            # Cho wheel 60 độ, so sánh current_angle với aim_angle
            angle_diff = abs(self._current_angle - aim_angle)
        is_close_to_aim = angle_diff <= 1.0
        
        # Chọn màu dựa trên điều kiện
        if is_close_to_aim:
            line_color = QColor(255, 100, 100)  # Màu trắng khi gần
            text_color = QColor(0, 0, 0)        # Text đen trên nền trắng
        else:
            line_color = QColor(255, 0, 0)      # Màu đỏ bình thường
            text_color = QColor(255, 255, 255)  # Text trắng trên nền đỏ
        
        # Tính vị trí Y cho aim_angle (SỬ DỤNG wheel_offset để đồng bộ với wheel)
        # Thanh phải di chuyển theo wheel để luôn ở đúng vị trí tương đối
        if is_360:
            # Cho wheel 360 độ, tính toán aim_direction trong range ±30 từ current_direction (tổng 60 độ)
            center_angle = self._current_direction if hasattr(self, '_current_direction') else 0
            start_angle = center_angle - 30
            # Normalize aim_direction trong range 60 độ - giống hệt wheel góc tầm
            normalized_aim = (aim_angle - start_angle) / 60  # 0 đến 1
            wheel_height_factor = 0.7  # Giống hệt wheel góc tầm
            y_pos = center.y() + height/2 * wheel_height_factor - normalized_aim * height * wheel_height_factor + wheel_offset
        else:
            # Cho wheel 60 độ, normalize trực tiếp
            normalized_aim = aim_angle / angle_range  # 0 đến 1
            wheel_height_factor = 0.7
            y_pos = center.y() + height/2 * wheel_height_factor - normalized_aim * height * wheel_height_factor + wheel_offset
        
        # Kiểm tra xem thanh có nằm trong wheel không
        wheel_top = center.y() - height/2 + 10
        wheel_bottom = center.y() + height/2 - 10
        
        if wheel_top <= y_pos <= wheel_bottom:
            # Thanh nằm trong wheel - vẽ thanh với màu thay đổi
            painter.setPen(QPen(line_color, 3))  # Màu thay đổi, độ dày 3px
            start_x = center.x() - width/2 + 5  # Bắt đầu từ cạnh trái wheel
            end_x = center.x() + width/2 - 5    # Kết thúc ở cạnh phải wheel
            painter.drawLine(QPointF(start_x, y_pos), QPointF(end_x, y_pos))
            
            # Vẽ tam giác chỉ vào thanh
            if is_360:
                # Wheel 360 độ: tam giác bên phải wheel
                indicator_x = center.x() + width/2 + 5  # Vị trí bên phải wheel
                painter.setPen(QPen(line_color, 2))
                painter.setBrush(line_color)
                
                # Tam giác chỉ sang trái vào wheel
                triangle_size = 8
                painter.drawPolygon([
                    QPointF(indicator_x, y_pos),
                    QPointF(indicator_x + triangle_size, y_pos - triangle_size/2),
                    QPointF(indicator_x + triangle_size, y_pos + triangle_size/2)
                ])
            else:
                # Wheel 60 độ: tam giác bên trái wheel
                indicator_x = center.x() - width/2 - 5  # Vị trí bên trái wheel
                painter.setPen(QPen(line_color, 2))
                painter.setBrush(line_color)
                
                # Tam giác chỉ sang phải vào wheel
                triangle_size = 8
                painter.drawPolygon([
                    QPointF(indicator_x, y_pos),
                    QPointF(indicator_x - triangle_size, y_pos - triangle_size/2),
                    QPointF(indicator_x - triangle_size, y_pos + triangle_size/2)
                ])
        else:
            # Thanh nằm ngoài wheel - vẽ mũi tên chỉ hướng với màu thay đổi
            painter.setPen(QPen(line_color, 2))
            painter.setBrush(line_color)
            
            # Xác định vị trí và hướng mũi tên
            if y_pos < wheel_top:
                # Thanh đỏ ở trên wheel - vẽ mũi tên chỉ lên
                if is_360:
                    arrow_x = center.x() + width/2 + 15  # Bên phải cho wheel 360 độ
                else:
                    arrow_x = center.x() - width/2 - 15  # Bên trái cho wheel 60 độ
                arrow_y = wheel_top - 10
                triangle_size = 12
                painter.drawPolygon([
                    QPointF(arrow_x, arrow_y),  # Đỉnh mũi tên
                    QPointF(arrow_x - triangle_size/2, arrow_y + triangle_size),  # Góc trái
                    QPointF(arrow_x + triangle_size/2, arrow_y + triangle_size)   # Góc phải
                ])
            else:
                # Thanh đỏ ở dưới wheel - vẽ mũi tên chỉ xuống
                if is_360:
                    arrow_x = center.x() + width/2 + 15  # Bên phải cho wheel 360 độ
                else:
                    arrow_x = center.x() - width/2 - 15  # Bên trái cho wheel 60 độ
                arrow_y = wheel_bottom + 10
                triangle_size = 12
                painter.drawPolygon([
                    QPointF(arrow_x, arrow_y),  # Đỉnh mũi tên
                    QPointF(arrow_x - triangle_size/2, arrow_y - triangle_size),  # Góc trái
                    QPointF(arrow_x + triangle_size/2, arrow_y - triangle_size)   # Góc phải
                ])
        
        # Hiển thị số aim_angle bên cạnh (luôn hiển thị)
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        # Vị trí text tùy thuộc vào thanh đỏ có nằm trong wheel hay không
        if wheel_top <= y_pos <= wheel_bottom:
            # Text bên cạnh tam giác chỉ vào wheel
            if is_360:
                text_x = center.x() + width/2 + 18  # Bên phải cho wheel 360 độ
            else:
                text_x = center.x() - width/2 - 53  # Bên trái cho wheel 60 độ (53 = 35 + 18)
            text_y = y_pos
        else:
            # Text bên cạnh mũi tên
            if is_360:
                text_x = center.x() + width/2 + 10  # Bên phải cho wheel 360 độ
            else:
                text_x = center.x() - width/2 - 45  # Bên trái cho wheel 60 độ (45 = 35 + 10)
            if y_pos < wheel_top:
                text_y = wheel_top - 10
            else:
                text_y = wheel_bottom + 10
                
        value_rect = QRectF(text_x, text_y - 10, 50, 20)
        
        # Vẽ nền cho text để dễ đọc hơn
        painter.setPen(Qt.NoPen)
        if is_close_to_aim:
            painter.setBrush(QColor(255, 255, 255, 200))  # Nền trắng khi gần
        else:
            painter.setBrush(QColor(255, 0, 0, 200))      # Nền đỏ bình thường
        painter.drawRoundedRect(value_rect, 5, 5)
        
        # Vẽ text với màu tương phản
        painter.setPen(QPen(text_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawText(value_rect, Qt.AlignCenter, f"{aim_angle:.1f}°")

    def _draw_vertical_marks_with_offset(self, painter: QPainter, center: QPointF, width: float, height: float, 
                                       offset_y: float, is_360: bool = False) -> None:
        """Vẽ các vạch chia độ trên vertical wheel với offset để wheel có thể xoay."""
        painter.setPen(QPen(Qt.white, 1))
        
        # Vẽ các vạch từ 0 đến angle_range độ với offset (0 ở dưới, angle_range ở trên)
        angle_range = 60 if is_360 else 60  # Cả hai wheel đều hiển thị 60 độ
        step = 5  # Sử dụng cùng step như wheel góc tầm
        
        if is_360:
            # Cho wheel 360 độ, hiển thị ±30 độ xung quanh current_direction (tổng 60 độ)
            center_angle = self._current_direction if hasattr(self, '_current_direction') else 0
            start_angle = center_angle - 30
            end_angle = center_angle + 30
            angles = range(int(start_angle), int(end_angle) + 1, step)
        else:
            # Cho wheel 60 độ, hiển thị từ 0 đến 60
            angles = range(0, angle_range + 1, step)
            
        for angle in angles:
            # Tính vị trí Y dựa vào góc và offset
            if is_360:
                # Cho wheel 360 độ, tính toán dựa trên range ±30 độ từ current_direction (tổng 60 độ)
                center_angle = self._current_direction if hasattr(self, '_current_direction') else 0
                start_angle = center_angle - 30
                # Normalize angle trong range 60 độ (0 đến 1) - giống hệt wheel góc tầm
                normalized_angle_for_pos = (angle - start_angle) / 60  # 0 đến 1
                wheel_height_factor = 0.7  # Giống hệt wheel góc tầm
                y_pos = center.y() + height/2 * wheel_height_factor - normalized_angle_for_pos * height * wheel_height_factor + offset_y
            else:
                normalized_angle_for_pos = angle / angle_range  # 0 đến 1
                wheel_height_factor = 0.7
                y_pos = center.y() + height/2 * wheel_height_factor - normalized_angle_for_pos * height * wheel_height_factor + offset_y
                
            # Chỉ vẽ vạch nếu nằm trong wheel
            if center.y() - height/2 + 10 <= y_pos <= center.y() + height/2 - 10:
                # Kiểm tra nếu vạch trắng sai lệch ±1 hoặc bằng vạch đỏ (aim_angle)
                if is_360:
                    # Cho wheel 360 độ, so sánh với _aim_direction (xử lý góc âm)
                    angle_diff = min(abs(angle - self._aim_direction), 
                                   abs(angle - self._aim_direction + 360),
                                   abs(angle - self._aim_direction - 360))
                else:
                    # Cho wheel 60 độ, so sánh với _aim_angle
                    angle_diff = abs(angle - self._aim_angle)
                is_close_to_aim = angle_diff <= 1.0
                
                # Kiểm tra xem vạch có nằm trong khoảng 10-60 độ không (chỉ cho wheel góc tầm)
                is_in_bright_range = True  # Mặc định là sáng
                if not is_360:  # Chỉ áp dụng cho wheel góc tầm (bên trái)
                    is_in_bright_range = (10 <= angle <= 60)
                
                # Độ dài vạch tùy vào góc - logic giống wheel góc tầm
                if angle % 15 == 0:  # Vạch dài cho góc chia hết cho 15 (cả hai wheel)
                    mark_width = width * 0.3
                    if is_close_to_aim:
                        painter.setPen(QPen(QColor(255, 255, 255, 255), 2))  # Trắng không trong suốt
                    elif is_in_bright_range:
                        painter.setPen(QPen(Qt.white, 2))
                    else:
                        painter.setPen(QPen(QColor(100, 100, 100), 2))  # Xám cho vạch ngoài khoảng 10-60
                elif angle % (10 if is_360 else 10) == 0:  # Vạch trung bình
                    mark_width = width * 0.2
                    if is_close_to_aim:
                        painter.setPen(QPen(QColor(255, 255, 255, 255), 1.5))  # Trắng không trong suốt
                    elif is_in_bright_range:
                        painter.setPen(QPen(Qt.white, 1.5))
                    else:
                        painter.setPen(QPen(QColor(100, 100, 100), 1.5))  # Xám
                else:  # Vạch ngắn
                    mark_width = width * 0.1
                    if is_close_to_aim:
                        painter.setPen(QPen(QColor(255, 255, 255, 255), 1))  # Trắng không trong suốt
                    elif is_in_bright_range:
                        painter.setPen(QPen(Qt.white, 1))
                    else:
                        painter.setPen(QPen(QColor(100, 100, 100), 1))  # Xám
                
                # Vẽ vạch
                start_x = center.x() - mark_width/2
                end_x = center.x() + mark_width/2
                painter.drawLine(QPointF(start_x, y_pos), QPointF(end_x, y_pos))
                
                # Vẽ số cho các góc chính
                if angle % 15 == 0:  # Cả hai wheel đều vẽ số cho góc chia hết cho 15
                    font = painter.font()
                    font.setPointSize(8)
                    painter.setFont(font)
                    if is_close_to_aim:
                        painter.setPen(QPen(QColor(255, 255, 255, 255), 2))  # Text trắng không trong suốt
                    elif is_in_bright_range:
                        painter.setPen(QPen(Qt.white, 2))
                    else:
                        painter.setPen(QPen(QColor(120, 120, 120), 2))  # Text xám
                    text_rect = QRectF(center.x() + width/2 - 25, y_pos - 8, 20, 16)
                    painter.drawText(text_rect, Qt.AlignCenter, str(angle))

    def _draw_status_light(self, painter: QPainter, total_width: float, total_height: float, 
                          total_wheel_width: float, start_x: float) -> None:
        """Vẽ đèn thông báo khi cả 2 wheel đều trùng khớp."""
        
        # Kiểm tra điều kiện: cả 2 wheel đều gần với aim (±0.5°) - strict hơn
        angle_diff_60 = abs(self._current_angle - self._aim_angle)
        angle_diff_360 = min(abs(self._current_direction - self._aim_direction),
                           abs(self._current_direction - self._aim_direction + 360),
                           abs(self._current_direction - self._aim_direction - 360))
        
        # Strict hơn: chỉ sáng khi cả hai đều <= 0.5°
        both_aligned = (angle_diff_60 <= 0.5) and (angle_diff_360 <= 0.5)
        
        # Vị trí đèn: dưới cùng widget, căn giữa theo cả 2 wheel
        light_width = total_wheel_width  # Chiều rộng bằng cả 2 wheel
        light_height = 25  # Chiều cao bằng phần text trong khung
        light_x = start_x
        light_y = total_height - light_height - 10  # Cách đáy 10px (dịch lên 10px từ 10px)

        light_rect = QRectF(light_x, light_y, light_width, light_height)
        
        # Vẽ đèn với màu sắc tùy theo trạng thái
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        
        if both_aligned:
            # Đèn sáng đỏ khi trùng khớp
            from PyQt5.QtGui import QLinearGradient
            light_gradient = QLinearGradient(light_rect.topLeft(), light_rect.bottomRight())
            light_gradient.setColorAt(0, QColor(255, 0, 0, 220))   # Đỏ sáng
            light_gradient.setColorAt(0.5, QColor(255, 50, 50, 200))
            light_gradient.setColorAt(1, QColor(200, 0, 0, 240))
            painter.setBrush(light_gradient)
        else:
            # Đèn tắt (xám đậm) khi chưa trùng khớp
            painter.setBrush(QColor(60, 60, 60, 150))
        
        painter.drawRoundedRect(light_rect, 8, 8)
        
        # Thêm hiệu ứng sáng khi đèn bật
        if both_aligned:
            # Viền sáng xung quanh - cùng vị trí với đèn chính
            painter.setPen(QPen(QColor(255, 0, 0, 180), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(light_rect, 8, 8)
            
            # Hiệu ứng shine bên trong - cùng vị trí với đèn chính
            shine_rect = QRectF(light_rect.x() + 5, light_rect.y() + 3, 
                               light_rect.width() - 10, light_rect.height() * 0.4)
            shine_gradient = QLinearGradient(shine_rect.topLeft(), shine_rect.bottomLeft())
            shine_gradient.setColorAt(0, QColor(255, 255, 255, 150))
            shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(shine_gradient)
            painter.drawRoundedRect(shine_rect, 5, 5)

    def _draw_vertical_marks(self, painter: QPainter, center: QPointF, width: float, height: float, is_left: bool = True) -> None:
        """Vẽ các vạch chia độ trên vertical wheel."""
        painter.setPen(QPen(Qt.white, 1))
        
        # Vẽ các vạch từ 0 đến 60 độ (0 ở dưới, 60 ở trên)
        for angle in range(0, 61, 5):
            # Tính vị trí Y dựa vào góc (đảo ngược: góc 0 ở dưới, 60 ở trên)
            normalized_angle = (60 - angle) / 60.0  # Đảo ngược thứ tự
            y_pos = center.y() - height/2 * 0.7 + normalized_angle * height * 0.7
            
            # Độ dài vạch tùy vào góc
            if angle % 15 == 0:  # Vạch dài cho góc chính
                mark_width = width * 0.3
                painter.setPen(QPen(Qt.white, 2))
            elif angle % 10 == 0:  # Vạch trung bình
                mark_width = width * 0.2
                painter.setPen(QPen(Qt.white, 1.5))
            else:  # Vạch ngắn
                mark_width = width * 0.1
                painter.setPen(QPen(Qt.white, 1))
            
            # Vẽ vạch
            start_x = center.x() - mark_width/2
            end_x = center.x() + mark_width/2
            painter.drawLine(QPointF(start_x, y_pos), QPointF(end_x, y_pos))
            
            # Vẽ số cho các góc chính
            if angle % 15 == 0:
                font = painter.font()
                font.setPointSize(8)
                painter.setFont(font)
                text_rect = QRectF(center.x() + width/2 - 25, y_pos - 8, 20, 16)
                painter.drawText(text_rect, Qt.AlignCenter, str(angle))

    def _draw_half_circle(self, painter: QPainter, center: QPointF, radius: float, inner_circle: bool = False) -> None:
        """Vẽ một phần đường tròn từ -5 độ đến 60 độ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.
            inner_circle (bool): Nếu True, vẽ vòng tròn bên trong. Nếu False, vẽ bên ngoài.
        
        Returns:
            None
        """
        diameter = radius * 2
        rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            diameter,
            diameter
        )
        painter.setPen(QPen(Qt.white, 2))
        
        # Thay đổi màu fill dựa vào điều kiện góc
        if inner_circle and self._current_angle == self._aim_angle:
            # Cung nhỏ và 2 góc bằng nhau -> màu xanh
            painter.setBrush(QColor(0, 255, 0, 100))  # Green với alpha=100
        else:
            # Mặc định -> màu trắng
            painter.setBrush(QColor(255, 255, 255, 100))  # White với alpha=100
            
        painter.drawPie(rect, -5 * 16, 70 * 16)  # Draw a half-circle (-5 degrees to 60 degrees)

    def _draw_angle_marks(self, painter: QPainter, center: QPointF, radius: float) -> None:
        """Vẽ các vạch góc trên vòng tròn.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.

        Returns:
            None
        """
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        for angle in range(-5, 65, 5):
            angle_rad = math.radians(angle)
            end_point = QPointF(center.x() + radius * math.cos(angle_rad), center.y() - radius * math.sin(angle_rad))
            
            if angle % 15 == 0:
                painter.setPen(QPen(Qt.white, 2))
                start_point = QPointF(center.x() + radius * 0.92 * math.cos(angle_rad), center.y() - radius * 0.92 * math.sin(angle_rad))
            else:
                painter.setPen(QPen(Qt.white, 1))
                start_point = QPointF(center.x() + radius * 0.96 * math.cos(angle_rad), center.y() - radius * 0.96 * math.sin(angle_rad))
            painter.drawLine(start_point, end_point)

    def _draw_pointer_triangle(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float, size: float, inner_circle: bool = True) -> None:
        """Vẽ con trỏ tam giác chỉ góc hiện tại trên vòng tròn.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.
            angle_deg (float): Góc hiện tại (độ).
            size (float): Kích thước của tam giác.
            inner_circle (bool): Nếu True, vẽ tam giác bên trong vòng tròn. Nếu False, vẽ bên ngoài.

        Returns:
            None
        """
        angle_rad = math.radians(angle_deg)

        # Đỉnh đầu tiên nằm trên đường tròn
        x1 = center.x() + radius * math.cos(angle_rad)
        y1 = center.y() - radius * math.sin(angle_rad)
        p1 = QPointF(x1, y1)

        # Hai đỉnh còn lại để tạo tam giác đều hướng ra ngoài
        angle1 = angle_rad + math.radians(30)
        angle2 = angle_rad - math.radians(30)

        x2 = x1 + size * math.cos(angle1)
        y2 = y1 - size * math.sin(angle1)
        x3 = x1 + size * math.cos(angle2)
        y3 = y1 - size * math.sin(angle2)

        p2 = QPointF(x2, y2)
        p3 = QPointF(x3, y3)

        # Vẽ tam giác
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.red)
        painter.drawPolygon(p1, p2, p3)

        # Tính toán tọa đọ của chữ nếu vẽ bên ngoài
        x4 = center.x() + radius * math.cos(angle_rad) * 1.1
        y4 = center.y() - radius * math.sin(angle_rad) * 1.1
        p4 = QPointF(x4, y4)

        text_rect = QRectF(p4.x() - 10, p4.y() - 10, 40, 20)  # Kích thước hình chữ nhật bao quanh văn bản
        painter.setPen(QPen(Qt.red, 20))
        painter.drawText(text_rect, Qt.AlignCenter, f"{angle_deg:.1f}°")

    def _draw_aim_icon(self, painter: QPainter, center: QPointF, radius: float, current_angle: float) -> None:
        """Vẽ icon chỉ vị trí aim_angle trên cung tròn nhỏ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ
            center (QPointF): Tọa độ trung tâm
            radius (float): Bán kính cung tròn nhỏ
            angle_deg (float): Góc current_angle (độ)
        """
        angle_rad = math.radians(current_angle)
        
        # Scale icon theo tỷ lệ radius
        icon_size = radius / 2  # Icon size = 1/4 radius
        x = center.x() + radius * math.cos(angle_rad) - icon_size / 2
        y = center.y() - radius * math.sin(angle_rad) - icon_size / 2
        
        # Load icon
        icon_path = resource_path(r"assets\Icons\missileIcon.png").replace("\\", "/")
        
        aim_icon = QPixmap(icon_path)

        # Validate pixmap loaded successfully
        if aim_icon.isNull():
            # Fail quietly to avoid spamming console during UI startup
            return
            
        # Thêm render hints để khử răng cưa
        painter.setRenderHints(
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.HighQualityAntialiasing
        )
        
        # Scale icon với TransformationMode.SmoothTransformation
        scaled_icon = aim_icon.scaled(
            int(icon_size), int(icon_size),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Lưu trạng thái và transform
        painter.save()
        painter.translate(x + icon_size/2, y + icon_size/2)
        painter.rotate(44 - self._current_angle)
        
        # Vẽ icon với smooth transform
        painter.drawPixmap(int(-icon_size/2), int(-icon_size/2), scaled_icon)
        
        # Khôi phục trạng thái
        painter.restore()

        x4 = center.x() + radius * math.cos(angle_rad) * 1.36
        y4 = center.y() - radius * math.sin(angle_rad) * 1.36
        p4 = QPointF(x4, y4)

        text_rect = QRectF(p4.x() - 10, p4.y() - 10, 40, 20)  # Kích thước hình chữ nhật bao quanh văn bản
        painter.setPen(QPen(Qt.black, 20))
        painter.drawText(text_rect, Qt.AlignCenter, f"{current_angle:.1f}°")

# if __name__ == "__main__":
#     from PyQt5.QtWidgets import QApplication
#     import sys

#     app = QApplication(sys.argv)
#     widget = HalfCircleWidget(0, 0)
#     widget.resize(400, 300)
#     widget.setStyleSheet("background-color: black;")
#     widget.show()
#     sys.exit(app.exec_())