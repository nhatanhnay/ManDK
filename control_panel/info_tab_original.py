
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF, QRect, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QPolygon, QFontMetrics, QPixmap
import math
import sys
import os

# Thêm đường dẫn để import data module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import system_data_manager, get_node_id_for_compartment, module_manager

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file resource."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)

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

class InfoTab(GridBackgroundWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data
        
        # Timer để cập nhật dữ liệu và mô phỏng
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self._update_data)
        self.data_timer.start(1000)  # Cập nhật mỗi giây
        
        # Danh sách các vùng clickable của node (để detect mouse click)
        self.node_regions = []
        
        # Info panel state
        self.show_info_panel = False
        self.selected_node_data = None
        self.info_panel_rect = QRect()
        self.close_button_rect = QRect()
        
        # Scrolling state
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scrollbar_rect = QRect()
        self.scrollbar_thumb_rect = QRect()
        self.scrolling = False
        
        # Thông tin panel và scroll
        self.selected_node_data = None
        self.info_panel_rect = None
        self.close_button_rect = None
        self.scroll_offset = 0  # Vị trí scroll hiện tại
        self.max_scroll = 0     # Giới hạn scroll tối đa
        self.module_height = 80  # Chiều cao mỗi module
        
    def _update_data(self):
        """Cập nhật dữ liệu mô phỏng và refresh display."""
        system_data_manager.simulate_data()
        module_manager.simulate_realtime_data()  # Cập nhật dữ liệu module
        self.update()  # Trigger repaint
        
    def mousePressEvent(self, event):
        """Xử lý sự kiện click chuột."""
        if event.button() == Qt.LeftButton:
            click_pos = event.pos()
            
            # Nếu đang hiển thị info panel
            if self.show_info_panel:
                # Kiểm tra click vào nút đóng
                if self.close_button_rect.contains(click_pos):
                    self.show_info_panel = False
                    self.selected_node_data = None
                    self.update()
                    return
                
                # Kiểm tra click vào scrollbar
                if self.scrollbar_rect.contains(click_pos):
                    # Tính toán vị trí scroll mới
                    relative_y = click_pos.y() - self.scrollbar_rect.top()
                    scroll_ratio = relative_y / self.scrollbar_rect.height()
                    self.scroll_offset = int(scroll_ratio * self.max_scroll)
                    self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                    self.update()
                    return
                
                # Nếu click vào info panel thì không làm gì (để tránh đóng panel)
                if self.info_panel_rect.contains(click_pos):
                    return
            else:
                # Kiểm tra xem click có trúng node nào không
                for region in self.node_regions:
                    if region['rect'].contains(click_pos):
                        # Lấy thông tin node và hiển thị info panel
                        node_data = system_data_manager.get_node(region['node_id'])
                        if node_data:
                            self.selected_node_data = node_data
                            self.show_info_panel = True
                            self.scroll_offset = 0  # Reset scroll
                            self._calculate_info_panel_rect()
                            self.update()
                        break
        
        super().mousePressEvent(event)
        
    def wheelEvent(self, event):
        """Xử lý sự kiện scroll wheel."""
        if self.show_info_panel and self.selected_node_data:
            # Scroll trong info panel
            delta = event.angleDelta().y()
            scroll_step = 30
            
            if delta > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - scroll_step)
            else:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + scroll_step)
            
            self.update()
            event.accept()
        else:
            super().wheelEvent(event)
        
    def _calculate_info_panel_rect(self):
        """Tính toán kích thước và vị trí của info panel."""
        padding = 10
        
        # Panel gần bằng kích thước tab với padding 10px
        panel_width = self.width() - 2 * padding
        panel_height = self.height() - 2 * padding
        
        # Vị trí panel
        x = padding
        y = padding
        
        self.info_panel_rect = QRect(x, y, panel_width, panel_height)
        
        # Vị trí nút đóng (góc trên phải)
        close_size = 30  # Tăng kích thước nút đóng một chút
        self.close_button_rect = QRect(
            x + panel_width - close_size - 15,
            y + 15,
            close_size,
            close_size
        )
        
    def paintEvent(self, event):
        """Override để vẽ cả background grid và sơ đồ hệ thống."""
        # Vẽ background grid trước
        super().paintEvent(event)
        
        # Vẽ sơ đồ hệ thống
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._draw_system_diagram(painter)
        
        # Vẽ info panel nếu được yêu cầu
        if self.show_info_panel and self.selected_node_data:
            self._draw_info_panel(painter)
        
    def _draw_system_diagram(self, painter):
        """Vẽ sơ đồ hệ thống fire control."""
        # Reset danh sách vùng clickable
        self.node_regions = []
        
        # Thiết lập font cho text
        font = QFont("Arial", 10, QFont.Normal)
        painter.setFont(font)
        
        # Màu sắc cho các thành phần
        box_color = QColor(255, 255, 255)       # Màu trắng cho nền
        text_color = QColor(255, 255, 255)            # Màu đen cho text
        border_color = QColor(255, 255, 255)     # Màu viền trắng
        arrow_color = QColor(150, 150, 150)     # Màu xám cho mũi tên
        
        # Kích thước và vị trí của các khoang
        compartment_width = 450
        compartment_width_center = 200  # Chiều ngang của khoang giữa bằng 1/2
        compartment_height = 400
        sight_column_height = 150  # Chiều cao cột ngắm thấp hơn
        spacing = 50

        # Tính toán vị trí để căn giữa
        total_width = 2 * compartment_width + compartment_width_center + 2 * spacing
        start_x = (self.width() - total_width) // 2
        start_y = (self.height() - compartment_height) // 2

        # Vị trí cột ngắm (phía trên khoang điều khiển giữa)
        sight_column_x = start_x + compartment_width + spacing
        sight_column_y = start_y - sight_column_height - 30  # Cách khoang điều khiển 30px
        
        # Vẽ cột ngắm trước
        sight_column = {
            'title': 'Cột ngắm',
            'x': sight_column_x,
            'y': sight_column_y,
            'width': compartment_width_center,
            'height': sight_column_height,
            'boxes': [
                ('Hộp điện', 25, 25),
                ('Hộp quang\nđiện tử', 25, 75)
            ]
        }
        self._draw_compartment(painter, sight_column, compartment_width_center, sight_column_height,
                             box_color, text_color, border_color)

        # Vẽ 3 khoang điều khiển
        compartments = [
            {
                'title': 'Khoang điều khiển tại chỗ 1',
                'x': start_x,
                'y': start_y,
                'boxes': [
                    ('Tủ ác quy', 20, 140),
                    ('Tủ phân phối\nbiến đổi', 80, 250),
                    ('Tủ biến áp', 88, 340),
                    ('Hộp dẫn động\nkềnh hướng', 150, 30),
                    ('Hộp dẫn động\nkềnh tâm', 150, 100),
                    ('Tủ điều khiển\ntại chỗ 1', 220, 170),
                    ('Bàn điều\nkhiển tại chỗ', 314, 250),
                    ('HN11', 335, 100),
                    ('HN12', 335, 30)
                ]
            },
            {
                'title': 'Khoang điều khiển',
                'x': start_x + compartment_width + spacing,
                'y': start_y,
                'width': compartment_width_center,
                'boxes': [
                    ('Khối giao tiếp\nhàng hải', 25, 30),
                    ('Bàn điều\nkhiển chính từ\nxa', 25, 163),
                    ('Bảng điện\nchính', 25, 332)
                ]
            },
            {
                'title': 'Khoang điều khiển tại chỗ 2',
                'x': start_x + compartment_width + compartment_width_center + 2 * spacing,
                'y': start_y,
                'boxes': [
                    ('Tủ ác quy', 20, 140),  # Sử dụng vị trí gốc, sẽ được tính đối xứng tự động
                    ('Tủ phân phối\nbiến đổi', 80, 250),
                    ('Tủ biến áp', 88, 340),
                    ('Hộp dẫn động\nkềnh hướng', 150, 30),
                    ('Hộp dẫn động\nkềnh tâm', 150, 100),
                    ('Tủ điều khiển\ntại chỗ 2', 220, 170),
                    ('Bàn điều\nkhiển tại chỗ', 314, 250),
                    ('HN22', 335, 30),
                    ('HN21', 335, 100)
                ]
            }
        ]
        
        # Vẽ từng khoang
        for i, comp in enumerate(compartments):
            # Sử dụng chiều rộng khác nhau cho khoang giữa
            width = compartment_width_center if i == 1 else compartment_width
            self._draw_compartment(painter, comp, width, compartment_height, 
                                 box_color, text_color, border_color)
        
        # Vẽ các kết nối orthogonal giữa các components
        self._draw_block_diagram_connections(painter, compartments, sight_column, 
                                           compartment_width, compartment_width_center, 
                                           compartment_height, sight_column_height)
    
    def _draw_compartment(self, painter, compartment, width, height, box_color, text_color, border_color):
        """Vẽ một khoang điều khiển với các thành phần bên trong."""
        x, y = compartment['x'], compartment['y']

        # Vẽ khung khoang với đường đứt nét (tùy chỉnh khoảng cách nét để giãn)
        pen = QPen(border_color, 2)
        # Dùng dash pattern: [dashLength, gapLength] (px). Tăng gapLength để giãn khoảng cách.
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([6.0, 6.0])  # ví dụ: 6px nét, 12px khoảng cách
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(50, 50, 50, 100)))  # Nền trong suốt
        painter.drawRect(x, y, width, height)

        # Vẽ tiêu đề khoang ở góc trái dưới
        painter.setPen(QPen(text_color))

        # Tính toán kích thước text
        metrics = QFontMetrics(painter.font())
        title_text = compartment['title']
        text_width = metrics.width(title_text)
        text_height = metrics.height()

        # Vị trí tiêu đề ở góc trái dưới (bên trong border)
        title_x = x + 10  # Cách lề trái 10px
        title_y = y + height - text_height - 10  # Cách lề dưới 10px

        # Vẽ text tiêu đề
        title_rect = QRect(title_x, title_y, text_width, text_height)
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignTop, title_text)
        
        # Vẽ các hộp thành phần
        for box_name, box_x, box_y in compartment['boxes']:
            # Lấy node ID để kiểm tra lỗi
            node_id = get_node_id_for_compartment(box_name, compartment['title'])
            node = system_data_manager.get_node(node_id)
            
            # Thay đổi màu nếu node có lỗi
            current_box_color = box_color
            current_text_color = QColor(0, 0, 0)
            if node and node.has_error:
                current_box_color = QColor(255, 0, 0)  # Nền đỏ khi có lỗi
                current_text_color = QColor(255, 255, 255)  # Text trắng khi có lỗi
            
            if width == 200:  # Khoang giữa nhỏ hơn hoặc Cột ngắm
                # Tính chiều rộng text để căn giữa
                metrics = QFontMetrics(painter.font())
                lines = box_name.split('\n')
                max_text_width = max(metrics.width(line) for line in lines)
                box_width = max_text_width + 20
                # Căn giữa trong khoang 200px
                centered_x = (width - box_width) // 2
                self._draw_component_box(painter, x + centered_x, y + box_y, box_name,
                                       current_box_color, current_text_color, border_color)
                # Cập nhật node_id cho region vừa thêm
                if self.node_regions:
                    self.node_regions[-1]['node_id'] = node_id
            elif compartment['title'] == 'Khoang điều khiển tại chỗ 2':
                # Tính toán vị trí đối xứng cho khoang 2
                metrics = QFontMetrics(painter.font())
                lines = box_name.split('\n')
                max_text_width = max(metrics.width(line) for line in lines)
                box_width = max_text_width + 20
                # Áp dụng công thức: vị_trí_mới = chiều_rộng_khoang - (vị_trí_cũ + chiều_rộng_box)
                mirrored_x = width - (box_x + box_width)
                self._draw_component_box(painter, x + mirrored_x, y + box_y, box_name,
                                       current_box_color, current_text_color, border_color)
                # Cập nhật node_id cho region vừa thêm
                if self.node_regions:
                    self.node_regions[-1]['node_id'] = node_id
            else:
                # Khoang 1 giữ nguyên vị trí
                self._draw_component_box(painter, x + box_x, y + box_y, box_name,
                                       current_box_color, current_text_color, border_color)
                # Cập nhật node_id cho region vừa thêm
                if self.node_regions:
                    self.node_regions[-1]['node_id'] = node_id
    
    def _draw_component_box(self, painter, x, y, text, box_color, text_color, border_color):
        """Vẽ một hộp thành phần."""
        # Tính kích thước hộp dựa trên text
        metrics = QFontMetrics(painter.font())
        lines = text.split('\n')
        max_width = max(metrics.width(line) for line in lines)
        box_width = max_width + 20
        box_height = len(lines) * metrics.height() + 10
        
        # Lưu vùng clickable của node
        node_rect = QRect(x, y, box_width, box_height)
        self.node_regions.append({
            'rect': node_rect,
            'name': text,
            'node_id': None  # Sẽ được set từ bên ngoài
        })
        
        # Vẽ hộp
        painter.setPen(QPen(QColor(100, 200, 255), 1))
        painter.setBrush(QBrush(box_color))
        painter.drawRect(x, y, box_width, box_height)
        
        # Vẽ text
        painter.setPen(QPen(text_color))
        text_rect = QRect(x + 5, y + 5, box_width - 10, box_height - 10)
        painter.drawText(text_rect, Qt.AlignCenter, text)
    
    def _draw_block_diagram_connections(self, painter, compartments, sight_column, 
                                      comp_width, comp_width_center, comp_height, sight_column_height):
        """Vẽ các kết nối orthogonal (vuông góc) giữa các components theo block diagram."""
        
        # Tạo dictionary mapping tên component sang vị trí thực tế
        component_positions = {}
        
        # Thu thập tất cả vị trí components từ các khoang
        for i, comp in enumerate(compartments):
            comp_x = comp['x']
            comp_y = comp['y']
            width = comp_width_center if i == 1 else comp_width
            
            for box_name, box_x, box_y in comp['boxes']:
                # Tính toán vị trí thực tế của component
                metrics = QFontMetrics(painter.font())
                lines = box_name.split('\n')
                max_text_width = max(metrics.width(line) for line in lines)
                box_width = max_text_width + 20
                box_height = len(lines) * metrics.height() + 10
                
                # Xử lý đối xứng cho khoang 2
                if comp['title'] == 'Khoang điều khiển tại chỗ 2':
                    mirrored_x = width - (box_x + box_width)
                    actual_x = comp_x + mirrored_x
                elif width == 200:  # Khoang giữa
                    centered_x = (width - box_width) // 2
                    actual_x = comp_x + centered_x
                else:
                    actual_x = comp_x + box_x
                
                actual_y = comp_y + box_y
                
                # Lưu vị trí trung tâm của component
                center_x = actual_x + box_width // 2
                center_y = actual_y + box_height // 2
                
                # Chuẩn hóa tên component để matching
                normalized_name = self._normalize_component_name(box_name, comp['title'])
                component_positions[normalized_name] = {
                    'center_x': center_x,
                    'center_y': center_y,
                    'width': box_width,
                    'height': box_height,
                    'left': actual_x,
                    'right': actual_x + box_width,
                    'top': actual_y,
                    'bottom': actual_y + box_height
                }
        
        # Thêm components từ cột ngắm
        sight_x = sight_column['x']
        sight_y = sight_column['y']
        for box_name, box_x, box_y in sight_column['boxes']:
            metrics = QFontMetrics(painter.font())
            lines = box_name.split('\n')
            max_text_width = max(metrics.width(line) for line in lines)
            box_width = max_text_width + 20
            box_height = len(lines) * metrics.height() + 10
            
            # Căn giữa trong cột ngắm
            centered_x = math.ceil((comp_width_center - box_width) // 2)
            actual_x = sight_x + centered_x
            actual_y = sight_y + box_y
            
            center_x = actual_x + box_width // 2
            center_y = actual_y + box_height // 2
            
            normalized_name = self._normalize_component_name(box_name, 'Cột ngắm')
            component_positions[normalized_name] = {
                'center_x': center_x,
                'center_y': center_y,
                'width': box_width,
                'height': box_height,
                'left': actual_x,
                'right': actual_x + box_width,
                'top': actual_y,
                'bottom': actual_y + box_height
            }
        
        # Định nghĩa các kết nối với edge cụ thể
        # Format: (start_comp, end_comp, start_edge, end_edge)
        # Edge: 1=trên, 2=phải, 3=dưới, 4=trái, None=tự động
        connections = [
            # Khoang điều khiển tại chỗ 1
            ('tu_ac_quy_1', 'tu_phan_phoi_bien_doi_1', 3, 4, 0, 0),  # Từ phải tủ ắc quy -> trái tủ phân phối
            ('tu_phan_phoi_bien_doi_1', 'tu_bien_ap_1', 3, 1, 0, 0),  # Từ dưới phân phối -> trên biến áp
            ('tu_phan_phoi_bien_doi_1', 'tu_dieu_khien_tai_cho_1', 2, 3, -5, 0),  # Từ trái phân phối 1 -> phải phân phối 2
            ('tu_phan_phoi_bien_doi_1', 'ban_dieu_khien_tai_cho_1', 2, 4, 0, 0),  # Từ phải phân phối -> trái điều khiển
            ('ban_dieu_khien_tai_cho_1', 'tu_dieu_khien_tai_cho_1', 1, 2, 0, 5),
            ('tu_dieu_khien_tai_cho_1', 'hop_dan_dong_kenh_huong_1', 1, 2, 0, 0), 
            ('tu_dieu_khien_tai_cho_1', 'hop_dan_dong_kenh_tam_1', 1, 2, -5, 0),
            ('tu_phan_phoi_bien_doi_1', 'hop_dan_dong_kenh_huong_1', 1, 4, 0, 0), 
            ('tu_phan_phoi_bien_doi_1', 'hop_dan_dong_kenh_tam_1', 1, 4, 5, 0),
            ('hn12', 'hn11', 3, 1, 0, 0),  # Từ dưới HN12 -> trên điều khiển
            ('hn11', 'tu_dieu_khien_tai_cho_1', 3, 2, 0, -5),  # Từ dưới HN11 -> trên điều khiển
            ('tu_bien_ap_1', 'bang_dien_chinh', 2, 4, 0, 0),  # Từ phải biến áp -> trái bảng điện
            
            # Khoang điều khiển
            ('khoi_giao_tiep_hang_hai', 'ban_dieu_khien_chinh_tu_xa', 3, 1, 0, 0),  # Từ dưới giao tiếp -> trên bàn điều khiển
            ('ban_dieu_khien_chinh_tu_xa', 'bang_dien_chinh', 3, 1, 0, 0),  # Từ dưới bàn -> trên bảng điện
            ('ban_dieu_khien_chinh_tu_xa', 'tu_dieu_khien_tai_cho_1', 4, 2, 0, 0),  # Từ trái bàn -> phải điều khiển 1
            ('ban_dieu_khien_chinh_tu_xa', 'tu_dieu_khien_tai_cho_2', 2, 4, 0, 0),  # Từ phải bàn -> trái điều khiển 2
            
            # Khoang điều khiển tại chỗ 2
            ('tu_ac_quy_2', 'tu_phan_phoi_bien_doi_2', 3, 2, 0, 0),  # Từ trái tủ ắc quy -> phải tủ phân phối
            ('tu_phan_phoi_bien_doi_2', 'tu_bien_ap_2', 3, 1, 0, 0),  # Từ dưới phân phối -> trên biến áp
            ('tu_phan_phoi_bien_doi_2', 'tu_dieu_khien_tai_cho_2', 4, 3, -5, 0),  # Từ trái phân phối -> phải điều khiển
            ('tu_phan_phoi_bien_doi_2', 'ban_dieu_khien_tai_cho_2', 4, 2, 0, 0), 
            ('ban_dieu_khien_tai_cho_2', 'tu_dieu_khien_tai_cho_2', 1, 4, 0, 5),
            ('tu_dieu_khien_tai_cho_2', 'hop_dan_dong_kenh_tam_2', 1, 4, 5, 0),
            ('tu_dieu_khien_tai_cho_2', 'hop_dan_dong_kenh_huong_2', 1, 4, 0, 0),
            ('tu_phan_phoi_bien_doi_2', 'hop_dan_dong_kenh_tam_2', 1, 2, -5, 0),
            ('tu_phan_phoi_bien_doi_2', 'hop_dan_dong_kenh_huong_2', 1, 2, 0, 0),
            ('hn22', 'hn21', 3, 1, 0, 0),  # Từ dưới HN22 -> trên điều khiển
            ('hn21', 'tu_dieu_khien_tai_cho_2', 3, 4, 0, -5),  # Từ dưới HN21 -> trên điều khiển
            ('tu_bien_ap_2', 'bang_dien_chinh', 4, 2, 0, 0),  # Từ trái biến áp -> phải bảng điện
            
            # Cột ngắm
            ('khoi_giao_tiep_hang_hai', 'hop_quang_dien_tu', 1, 3, 0, 0),  # Từ trên bàn -> dưới hộp quang
            # Thay đổi routing: kết nối từ Hộp quang điện tử và Hộp điện tới
            # Bàn điều khiển chính từ xa (đi từ đáy các hộp lên đỉnh bàn từ xa)
            # dùng edge 3 (dưới) -> 1 (trên) với offset nhỏ để tránh chồng đường
            ('hop_quang_dien_tu', 'ban_dieu_khien_chinh_tu_xa', 2, 2, 0, -10, 40),
            ('hop_dien', 'ban_dieu_khien_chinh_tu_xa', 2, 2, 0, -5, 50),
        ]
        
        # Vẽ các kết nối
        connection_color = QColor(100, 200, 255)  # Màu xanh lam nhạt
        painter.setPen(QPen(connection_color, 2))
        
        for connection_data in connections:
            # Parse tuple length safely (support 2,6,7 length formats)
            if len(connection_data) == 7:
                start_comp, end_comp, start_edge, end_edge, start_offset, end_offset, straight_distance  = connection_data
            elif len(connection_data) == 6:
                start_comp, end_comp, start_edge, end_edge, start_offset, end_offset = connection_data
                straight_distance = 50
            elif len(connection_data) == 2:
                start_comp, end_comp = connection_data
                start_edge = end_edge = None
                start_offset = end_offset = 0
                straight_distance = 50
            else:
                # Fallback for unexpected formats
                start_comp, end_comp = connection_data[:2]
                start_edge = end_edge = None
                start_offset = end_offset = 0
                straight_distance = 50
                
            if start_comp in component_positions and end_comp in component_positions:
                #if component is hop_quang_dien_tu or hop_dien
                if start_comp == 'hop_quang_dien_tu' or start_comp == 'hop_dien':
                    # Defensive: ensure start_point can be computed inside special function
                    self._draw_orthogonal_connection_special(painter, 
                                               component_positions[start_comp],
                                               component_positions[end_comp],
                                               start_edge, end_edge,
                                               start_offset, end_offset, straight_distance)
                else:
                    self._draw_orthogonal_connection(painter, 
                                               component_positions[start_comp],
                                               component_positions[end_comp],
                                               start_edge, end_edge,
                                               start_offset, end_offset)
    
    def _normalize_component_name(self, name, compartment_title=None):
        """Chuẩn hóa tên component để matching kết nối."""
        # Loại bỏ ký tự xuống dòng và chuẩn hóa
        normalized = name.replace('\n', ' ').lower()
        
        # Mapping các tên component
        name_mapping = {
            'tủ ác quy': 'tu_ac_quy',
            'tủ phân phối biến đổi': 'tu_phan_phoi_bien_doi', 
            'tủ biến áp': 'tu_bien_ap',
            'hộp dẫn động kềnh hướng': 'hop_dan_dong_kenh_huong',
            'hộp dẫn động kềnh tâm': 'hop_dan_dong_kenh_tam',
            'tủ điều khiển tại chỗ 1': 'tu_dieu_khien_tai_cho_1',
            'tủ điều khiển tại chỗ 2': 'tu_dieu_khien_tai_cho_2',
            'bàn điều khiển tại chỗ': 'ban_dieu_khien_tai_cho',
            'hn11': 'hn11',
            'hn12': 'hn12',
            'hn21': 'hn21', 
            'hn22': 'hn22',
            'khối giao tiếp hàng hải': 'khoi_giao_tiep_hang_hai',
            'bàn điều khiển chính từ xa': 'ban_dieu_khien_chinh_tu_xa',
            'bảng điện chính': 'bang_dien_chinh',
            'hộp điện': 'hop_dien',
            'hộp quang điện tử': 'hop_quang_dien_tu'
        }
        
        # Tìm mapping cơ bản
        base_name = None
        for original, mapped in name_mapping.items():
            if normalized == original:
                base_name = mapped
                break
        
        if not base_name:
            base_name = normalized.replace(' ', '_')
        
        # Thêm suffix dựa trên compartment
        if compartment_title:
            if 'tại chỗ 1' in compartment_title:
                if base_name in ['tu_ac_quy', 'tu_phan_phoi_bien_doi', 'tu_bien_ap', 
                               'hop_dan_dong_kenh_huong', 'hop_dan_dong_kenh_tam', 'ban_dieu_khien_tai_cho']:
                    base_name += '_1'
            elif 'tại chỗ 2' in compartment_title:
                if base_name in ['tu_ac_quy', 'tu_phan_phoi_bien_doi', 'tu_bien_ap',
                               'hop_dan_dong_kenh_huong', 'hop_dan_dong_kenh_tam', 'ban_dieu_khien_tai_cho']:
                    base_name += '_2'
        
        return base_name
    
    def _get_point_from_edge(self, pos, edge):
        """Lấy điểm kết nối từ cạnh được chỉ định.
        Args:
            pos: dictionary chứa thông tin vị trí node
            edge: 1=trên, 2=phải, 3=dưới, 4=trái
        Returns:
            tuple: (x, y) tọa độ điểm kết nối
        """
        if edge == 1:  # Trên
            return (pos['center_x'], pos['top'])
        elif edge == 2:  # Phải
            return (pos['right'], pos['center_y'])
        elif edge == 3:  # Dưới
            return (pos['center_x'], pos['bottom'])
        elif edge == 4:  # Trái
            return (pos['left'], pos['center_y'])
        else:
            # Fallback về center nếu edge không hợp lệ
            return (pos['center_x'], pos['center_y'])
    
    def _get_edge_direction(self, pos, point):
        """Xác định hướng của cạnh dựa trên điểm kết nối.
        Returns:
            int: 1=trên, 2=phải, 3=dưới, 4=trái
        """
        point_x, point_y = point
        center_x, center_y = pos['center_x'], pos['center_y']
        
        if point_x == center_x and point_y < center_y:
            return 1  # Trên
        elif point_x > center_x and point_y == center_y:
            return 2  # Phải
        elif point_x == center_x and point_y > center_y:
            return 3  # Dưới
        elif point_x < center_x and point_y == center_y:
            return 4  # Trái
        else:
            return 1  # Fallback
    
    def _get_intermediate_point(self, start_point, direction, distance):
        """Tính toán điểm trung gian sau khi đi thẳng theo hướng cạnh.
        Args:
            start_point: (x, y) điểm xuất phát
            direction: 1=trên, 2=phải, 3=dưới, 4=trái
            distance: khoảng cách đi thẳng
        Returns:
            tuple: (x, y) tọa độ điểm trung gian
        """
        x, y = start_point
        if direction == 1:  # Trên
            return (x, y - distance)
        elif direction == 2:  # Phải
            return (x + distance, y)
        elif direction == 3:  # Dưới
            return (x, y + distance)
        elif direction == 4:  # Trái
            return (x - distance, y)
        else:
            return start_point
    
    def _get_auto_end_point(self, end_pos, intermediate_point, start_direction):
        """Tự động chọn điểm kết thúc tối ưu dựa trên vị trí trung gian và hướng xuất phát."""
        inter_x, inter_y = intermediate_point
        
        if start_direction in [1, 3]:  # Xuất phát từ trên/dưới -> rẽ ngang
            if inter_x < end_pos['center_x']:
                return (end_pos['left'], inter_y)
            else:
                return (end_pos['right'], inter_y)
        else:  # Xuất phát từ trái/phải -> rẽ dọc
            if inter_y < end_pos['center_y']:
                return (inter_x, end_pos['top'])
            else:
                return (inter_x, end_pos['bottom'])
    
    def _draw_orthogonal_connection_special(self, painter, start_pos, end_pos, start_edge=None, end_edge=None, pos_offset_start=0, pos_offset_end=0, straight_distance=50):
        """Vẽ kết nối orthogonal đặc biệt: từ cạnh được chỉ định của start, đi thẳng theo hướng cạnh đó một khoảng cố định rồi rẽ đến cạnh được chỉ định của end.
        
        Args:
            start_edge: 1=trên, 2=phải, 3=dưới, 4=trái (None = tự động chọn)
            end_edge: 1=trên, 2=phải, 3=dưới, 4=trái (None = tự động chọn)
            straight_distance: khoảng cách đi thẳng ban đầu
        """
        start_point = None
        # Chọn start point dựa trên cạnh được chỉ định hoặc tự động
        if start_edge is not None:
            start_point = self._get_point_from_edge(start_pos, start_edge)
        # Defensive fallback: nếu _get_point_from_edge trả None (không hợp lệ),
        # đặt start_point thành tâm node để tránh TypeError
        if start_point is None:
            start_point = (start_pos.get('center_x', 0), start_pos.get('center_y', 0))

        # Xác định điểm kết thúc dựa trên cạnh được chỉ định hoặc tự động
        if end_edge is not None:
            final_point = self._get_point_from_edge(end_pos, end_edge)
        else:
            final_point = (end_pos['center_x'], end_pos['center_y'])

        # Apply offsets to start and final points
        start_x, start_y = start_point
        final_x, final_y = final_point

        # Xác định hướng của start edge
        start_direction = self._get_edge_direction(start_pos, start_point)

        if start_direction == 1 or start_direction == 3:  # Trên hoặc Dưới -> các đoạn dọc trước
            start_y += pos_offset_start
            final_y += pos_offset_end
        else:  # Trái hoặc Phải -> các đoạn ngang trước
            start_y += pos_offset_start
            final_y += pos_offset_end

        start_point = (start_x, start_y)
        final_point = (final_x, final_y)

        # Snap/grid size (dùng grid spacing nếu có, fallback 20)
        snap = getattr(self, 'grid_spacing', 20) or 20

        # Nếu xuất phát theo hướng dọc, ta route theo pattern: vertical -> horizontal(shared X) -> final
        if start_direction in (1, 3):
            # compute a shared X channel based on end_pos center, snapped to grid
            shared_x = int(round(end_pos['center_x'] / snap) * snap)

            # intermediate points
            # point A: đi thẳng dọc từ start point by straight_distance
            dir_sign = 1 if start_direction == 3 else -1
            inter_a = (start_point[0], start_point[1] + dir_sign * straight_distance)
            # point B: horizontal move to shared_x
            inter_b = (shared_x, inter_a[1])

            # Draw segments: start -> A -> B -> final
            painter.drawLine(start_point[0], start_point[1], inter_a[0], inter_a[1])
            painter.drawLine(inter_a[0], inter_a[1], inter_b[0], inter_b[1])
            painter.drawLine(inter_b[0], inter_b[1], final_point[0], final_point[1])
            # painter.drawLine(inter_c[0], inter_c[1], final_point[0], final_point[1])
        else:
            # start_direction is horizontal: route horizontal -> vertical(shared Y)  -> final

            dir_sign = 1 if start_direction == 2 else -1
            inter_a = (start_point[0] + dir_sign * straight_distance, start_point[1])
            inter_b = (inter_a[0], final_point[1])

            painter.drawLine(start_point[0], start_point[1], inter_a[0], inter_a[1])
            painter.drawLine(inter_a[0], inter_a[1], inter_b[0], final_point[1])
            painter.drawLine(inter_b[0], final_point[1], final_point[0], final_point[1])
            # painter.drawLine(inter_c[0], inter_c[1], final_point[0], final_point[1])

    def _draw_orthogonal_connection(self, painter, start_pos, end_pos, start_edge=None, end_edge=None, pos_offset_start=0, pos_offset_end=0):
        """Vẽ kết nối orthogonal: từ cạnh được chỉ định của start, đi thẳng theo hướng cạnh đó rồi rẽ đến cạnh được chỉ định của end.
        
        Args:
            start_edge: 1=trên, 2=phải, 3=dưới, 4=trái (None = tự động chọn)
            end_edge: 1=trên, 2=phải, 3=dưới, 4=trái (None = tự động chọn)
        """
        start_point = None
        # Chọn start point dựa trên cạnh được chỉ định hoặc tự động
        if start_edge is not None:
            start_point = self._get_point_from_edge(start_pos, start_edge)

        # Kiểm tra xem 2 nodes có gần như thẳng hàng theo chiều dọc không
        horizontal_distance = abs(start_pos['center_x'] - end_pos['center_x'])
        vertical_distance = abs(start_pos['center_y'] - end_pos['center_y'])
        alignment_threshold = 30  # pixels - ngưỡng để coi là "gần như thẳng hàng"
        
        if horizontal_distance <= alignment_threshold:
            # Nodes gần như thẳng hàng theo chiều dọc
            if start_pos['center_y'] < end_pos['center_y']:
                # Start ở trên, end ở dưới - nối từ bottom của start đến top của end
                start_vertical_point = (start_pos['center_x'], start_pos['bottom'])
                end_vertical_point = (end_pos['center_x'], end_pos['top'])
            else:
                # Start ở dưới, end ở trên - nối từ top của start đến bottom của end
                start_vertical_point = (start_pos['center_x'], start_pos['top'])
                end_vertical_point = (end_pos['center_x'], end_pos['bottom'])
            
            painter.drawLine(start_vertical_point[0], start_vertical_point[1], end_vertical_point[0], end_vertical_point[1])
        elif vertical_distance <= alignment_threshold:
            # Nodes gần như thẳng hàng theo chiều ngang - nối từ side edge sang side edge
            if start_pos['center_x'] < end_pos['center_x']:
                # Start ở bên trái, end ở bên phải
                start_side_point = (start_pos['right'], start_pos['center_y'])
                end_side_point = (end_pos['left'], end_pos['center_y'])
            else:
                # Start ở bên phải, end ở bên trái
                start_side_point = (start_pos['left'], start_pos['center_y'])
                end_side_point = (end_pos['right'], end_pos['center_y'])
            
            # Vẽ đường thẳng ngang
            painter.drawLine(start_side_point[0], start_side_point[1], end_side_point[0], end_side_point[1])
        else:
            # Nodes không thẳng hàng - logic mới: đi thẳng theo hướng cạnh trước khi rẽ 1 lần duy nhất
            start_x, start_y = start_point
            
            # Xác định hướng của start edge và khoảng cách đi thẳng
            
            # Tính toán intermediate point dựa trên hướng xuất phát
            start_direction = self._get_edge_direction(start_pos, start_point)
            # Xác định điểm kết thúc dựa trên cạnh được chỉ định hoặc tự động
            if end_edge is not None:
                final_point = self._get_point_from_edge(end_pos, end_edge)

            final_x, final_y = final_point

            if start_direction == 1 or start_direction == 3:  # Trên hoặc Dưới
                start_x += pos_offset_start
                final_y += pos_offset_end
            else:  # Trái hoặc Phải
                start_y += pos_offset_start
                final_x += pos_offset_end

            start_point = (start_x, start_y)
            final_point = (final_x, final_y)

            straight_distance = max(abs(final_x - start_x), abs(final_y - start_y))
            intermediate_point = self._get_intermediate_point(start_point, start_direction, straight_distance)
            # Vẽ chỉ hai đoạn thẳng (rẽ 1 lần duy nhất):
            # 1. Từ start đi thẳng theo hướng cạnh
            painter.drawLine(start_point[0], start_point[1], intermediate_point[0], intermediate_point[1])
            # 2. Rẽ một lần duy nhất đến target
            painter.drawLine(intermediate_point[0], intermediate_point[1], final_point[0], final_point[1])
        
    def _draw_info_panel(self, painter):
        """Vẽ panel thông tin node overlay với layout mới."""
        if not self.selected_node_data:
            return
            
        # Vẽ overlay tối (làm mờ background)
        overlay_color = QColor(0, 0, 0, 120)
        painter.fillRect(self.rect(), overlay_color)
        
        # Vẽ panel chính với nền đen
        panel_color = QColor(30, 30, 30, 255)    # Nền đen
        border_color = QColor(255, 255, 255)     # Viền trắng

        # Pen cho panel chính: viền đậm hơn nhưng dashed với khoảng cách giãn
        painter.setPen(QPen(border_color, 3))
        painter.setBrush(QBrush(panel_color))
        painter.drawRect(self.info_panel_rect)
        
        # Vẽ header với tiêu đề và nút đóng
        self._draw_panel_header(painter)
        
        # Vẽ sidebar bên trái
        self._draw_left_sidebar(painter)
        
        # Vẽ main content area (charts)
        self._draw_main_content_area(painter)
        
    def _draw_panel_header(self, painter):
        """Vẽ header với tiêu đề và nút X."""
        # Tiêu đề
        title_font = QFont("Arial", 14, QFont.Normal)  # Tăng lại size
        painter.setFont(title_font)
        painter.setPen(QPen(QColor(255, 255, 255)))  # Chữ trắng trên nền đen
        
        # Lấy tên node và loại bỏ ký tự xuống dòng
        title_text = self.selected_node_data.name.replace('\n', ' ')
        
        # Tính toán vùng hiển thị tiêu đề (tận dụng hết không gian trừ nút X)
        header_rect = QRect(self.info_panel_rect.left() + 20, 
                           self.info_panel_rect.top() + 15, 
                           self.info_panel_rect.width() - 70, 30)  # Giảm margin cho nút X
        
        # Vẽ text trên một dòng, không word wrap
        painter.drawText(header_rect, Qt.AlignLeft | Qt.AlignVCenter, title_text)
        
        # Nút đóng X
        self._draw_close_button(painter)
    
    def _draw_left_sidebar(self, painter):
        """Vẽ sidebar bên trái với ô trạng thái và hình ảnh."""
        sidebar_x = self.info_panel_rect.left() + 20
        sidebar_y = self.info_panel_rect.top() + 60  # Trở về 60 vì tiêu đề chỉ 1 dòng
        sidebar_width = 250  # Tăng từ 160 lên 250
        
        # Ô trạng thái (thay vì nút "Lỗi")
        status_rect = QRect(sidebar_x, sidebar_y, sidebar_width - 20, 35)
        
        if self.selected_node_data.has_error:
            status_color = QColor(220, 60, 60)  # Màu đỏ cho lỗi
            status_text = "LỖI"
            text_color = QColor(255, 255, 255)
        else:
            status_color = QColor(60, 180, 60)  # Màu xanh cho bình thường
            status_text = "BÌNH THƯỜNG"
            text_color = QColor(255, 255, 255)
        
        painter.setPen(QPen(QColor(40, 40, 40), 2))
        painter.setBrush(QBrush(status_color))
        painter.drawRect(status_rect)
        
        painter.setFont(QFont("Arial", 10, QFont.Normal))
        painter.setPen(QPen(text_color))
        painter.drawText(status_rect, Qt.AlignCenter, status_text)
        
        # Hình ảnh thiết bị (cũng rộng hơn)
        image_rect = QRect(sidebar_x, sidebar_y + 50, sidebar_width - 20, 240)  # Tăng lại chiều cao
        self._draw_device_image(painter, image_rect)
    
    def _draw_device_image(self, painter, rect):
        """Vẽ hình ảnh thiết bị từ assets."""
        # Tạo mapping từ node_id sang file ảnh
        image_mapping = {
            'bang_dien_chinh': 'bangdienchinh.png',
            'ban_dieu_khien_chinh': 'bandieukhienchinhtuxa.png',
            'ban_dieu_khien_1': 'bangdieukhientaicho1.png',
            'ban_dieu_khien_2': 'bangdieukhientaicho2.png',
            'dan_dong_huong_1': 'hopdandongkenhhuong.png',
            'dan_dong_huong_2': 'hopdandongkenhhuong.png',
            'dan_dong_tam_1': 'hopdandongkenhtam.png',
            'dan_dong_tam_2': 'hopdandongkenhtam.png',
            'hn11': 'hophn11.png',
            'hn12': 'hophn12.png',
            'hn21': 'hophn11.png',  # Dùng chung ảnh
            'hn22': 'hophn12.png', # Dùng chung ảnh
            'giao_tiep_hang_hai': 'hopketnoihanghaivagiamsat.png',
            'ac_quy_1': 'tuacquy.png',
            'ac_quy_2': 'tuacquy.png',
            'bien_ap_1': 'tubienap.png',
            'bien_ap_2': 'tubienap.png',
            'phan_phoi_1': 'tubiendoiphanphoi.png',
            'phan_phoi_2': 'tubiendoiphanphoi.png',
            'dieu_khien_1': 'tudieukhientaicho.png',
            'dieu_khien_2': 'tudieukhientaicho.png',
            'hop_dien': 'hopdien.png',
            'hop_quang_dien_tu': 'hopquangdientu.png',
        }
        
        # Lấy file ảnh tương ứng với node
        image_file = image_mapping.get(self.selected_node_data.node_id, 'bangdienchinh.png')
        image_path = resource_path(f'assets/image/{image_file}')
        
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale ảnh cho vừa với rect
                scaled_pixmap = pixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Căn giữa ảnh trong rect
                x_offset = (rect.width() - scaled_pixmap.width()) // 2
                y_offset = (rect.height() - scaled_pixmap.height()) // 2
                
                draw_rect = QRect(rect.x() + x_offset, rect.y() + y_offset, 
                                scaled_pixmap.width(), scaled_pixmap.height())
                
                painter.drawPixmap(draw_rect, scaled_pixmap)
            else:
                # Fallback: vẽ placeholder nếu không load được ảnh
                painter.setPen(QPen(QColor(150, 150, 150), 1))
                painter.setBrush(QBrush(QColor(220, 220, 220)))
                painter.drawRect(rect)
                
                painter.setPen(QPen(QColor(100, 100, 100)))
                painter.setFont(QFont("Arial", 10))
                painter.drawText(rect, Qt.AlignCenter, "Không có\nhình ảnh")
                
        except Exception as e:
            # Fallback nếu có lỗi
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.setBrush(QBrush(QColor(220, 220, 220)))
            painter.drawRect(rect)
            
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(rect, Qt.AlignCenter, f"Lỗi load ảnh\n{image_file}")
    
    def _draw_main_content_area(self, painter):
        """Vẽ vùng nội dung chính với scrollable modules."""
        content_x = self.info_panel_rect.left() + 290
        content_y = self.info_panel_rect.top() + 60
        content_width = self.info_panel_rect.width() - 330
        content_height = self.info_panel_rect.height() - 100
        
        # Tạo clipping rect để chỉ vẽ trong vùng content
        content_rect = QRect(content_x, content_y, content_width, content_height)
        painter.setClipping(True)
        painter.setClipRect(content_rect)
        
        # Lấy dữ liệu module thực từ module_manager
        node_modules = module_manager.get_node_modules(self.selected_node_data.node_id)
        modules_list = list(node_modules.values())
        num_modules = len(modules_list)
        
        # Kích thước module
        module_width = content_width - 60  # Trừ thêm cho scrollbar
        self.module_height = 80
        module_spacing = 15
        
        # Tính toán scroll
        total_height = num_modules * (self.module_height + module_spacing) - module_spacing
        visible_height = content_height
        self.max_scroll = max(0, total_height - visible_height)
        
        # Vẽ các module với offset scroll
        current_y = content_y - self.scroll_offset
        
        for i, module_data in enumerate(modules_list):
            module_rect = QRect(content_x + 20, current_y, module_width, self.module_height)
            
            # Chỉ vẽ module nếu nó nằm trong vùng hiển thị
            if (current_y + self.module_height >= content_y and 
                current_y <= content_y + content_height):
                self._draw_module(painter, module_rect, module_data)
            
            current_y += self.module_height + module_spacing
        
        # Vẽ scroll bar nếu cần
        if self.max_scroll > 0:
            self._draw_scrollbar(painter, content_rect)
        
        # Tắt clipping
        painter.setClipping(False)
        
    def _draw_scrollbar(self, painter, content_rect):
        """Vẽ thanh scroll."""
        scrollbar_width = 8
        scrollbar_x = content_rect.right() - scrollbar_width - 5
        scrollbar_y = content_rect.top() + 5
        scrollbar_height = content_rect.height() - 10
        
        # Nền scrollbar
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        scrollbar_bg_rect = QRect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        painter.drawRect(scrollbar_bg_rect)
        
        # Thumb scrollbar
        if self.max_scroll > 0:
            total_content_height = self.max_scroll + content_rect.height()
            thumb_height = max(20, int(scrollbar_height * content_rect.height() / total_content_height))
            thumb_y = scrollbar_y + int(self.scroll_offset * (scrollbar_height - thumb_height) / self.max_scroll)
            
            painter.setBrush(QBrush(QColor(150, 150, 150)))
            thumb_rect = QRect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            painter.drawRect(thumb_rect)
    
    def _draw_module(self, painter, rect, module_data):
        """Vẽ một module với 4 thông số sử dụng dữ liệu thực."""
        # Tính toán vị trí
        param_width = (rect.width() - 40) // 4
        param_height = 50  # Tăng chiều cao từ 35 lên 50
        param_y = rect.top() + 25
        
        # Tạo rect cho module với cạnh dưới đi qua trung điểm của parameter boxes
        module_bottom = param_y + param_height // 2  # Trung điểm của parameter boxes
        module_rect = QRect(rect.left(), rect.top(), rect.width(), module_bottom - rect.top())
        
        # Màu sắc khung module theo trạng thái
        border_color = QColor(150, 150, 150)  # Xám cho bình thường
        
        # Vẽ khung module với cạnh dưới đi qua trung điểm các box
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(module_rect)
        
        # Vẽ tiêu đề module (không có background, đè trực tiếp lên cạnh trên)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 10, QFont.Normal))
        
        title_text = module_data.name
        
        # Vẽ text tiêu đề đè lên cạnh trên
        title_rect = QRect(rect.left() + 20, rect.top() - 6, 150, 20)
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignVCenter, title_text)
        
        # Lấy thông số thực từ module_data
        params = module_data.parameters
        voltage_display = f"{params.voltage:.1f}"
        current_display = f"{params.current:.1f}"
        power_display = f"{params.power:.1f}"
        resistance_display = f"{params.resistance:.1f}"
        
        # Vị trí các thông số (4 cột) - cạnh dưới module đi qua trung điểm các box này
        parameters = [
            ("Điện áp", f"{voltage_display}V"),
            ("Dòng điện", f"{current_display}A"),
            ("Công suất", f"{power_display}W"),
            ("Điện trở", f"{resistance_display}Ω")
        ]
        
        for i, (label, value) in enumerate(parameters):
            param_x = rect.left() + 20 + i * param_width
            param_rect = QRect(param_x, param_y, param_width - 10, param_height)
            
            self._draw_parameter_box(painter, param_rect, label, value, module_data.name)
    
    def _draw_parameter_box(self, painter, rect, label, value, module_name="Module 1"):
        """Vẽ một hộp thông số với đường kẻ màu theo trạng thái."""
        # Nền thông số (màu xám đậm như trong hình)
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(70, 70, 70)))
        painter.drawRect(rect)
        
        # Label (phần trên) - căn giữa theo chiều cao mới
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.setFont(QFont("Arial", 9))
        label_height = rect.height() // 4 # Nửa trên của box
        label_rect = QRect(rect.left(), rect.top() + 5, rect.width(), label_height)
        painter.drawText(label_rect, Qt.AlignCenter, label)
        
        # Xác định màu đường kẻ dựa trên giá trị và loại thông số
        line_color = self._get_parameter_status_color(label, value, module_name)
        
        # Đường phân cách với màu theo trạng thái - ở giữa box
        painter.setPen(QPen(line_color, 2))  # Tăng độ dày lên 2 để rõ hơn
        separator_y = rect.top() + rect.height() // 2
        painter.drawLine(rect.left() + 5, separator_y, rect.right() - 5, separator_y)
        
        # Giá trị (phần dưới) - căn giữa theo chiều cao mới
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 12, QFont.Normal))
        value_height = rect.height() // 2 - 2  # Nửa dưới của box
        value_rect = QRect(rect.left(), separator_y + 2, rect.width(), value_height)
        painter.drawText(value_rect, Qt.AlignCenter, value)
    
    def _get_parameter_status_color(self, label, value, module_name="Module 1"):
        """Xác định màu sắc dựa trên trạng thái thông số."""
        # Import module thresholds
        try:
            from data.module_thresholds import get_threshold_for_parameter, is_parameter_normal
        except ImportError:
            # Fallback nếu không import được
            return QColor(0, 255, 0)
        
        # Lấy giá trị số từ string (bỏ đơn vị)
        try:
            numeric_value = float(''.join(filter(str.isdigit, value)))
        except:
            return QColor(0, 255, 0)  # Xanh mặc định nếu không parse được
        
        # Kiểm tra trạng thái dựa trên file cấu hình
        if is_parameter_normal(module_name, label, numeric_value):
            return QColor(0, 255, 0)    # Xanh - bình thường
        else:
            return QColor(255, 0, 0)    # Đỏ - cao/thấp
    
    def _draw_close_button(self, painter):
        """Vẽ nút đóng X."""
        # Nút đóng ở góc phải trên
        close_size = 30
        close_x = self.info_panel_rect.right() - close_size - 15
        close_y = self.info_panel_rect.top() + 15
        self.close_button_rect = QRect(close_x, close_y, close_size, close_size)
        
        # Nền nút đóng (trong suốt)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(self.close_button_rect)
        
        # Vẽ chữ X
        painter.setPen(QPen(QColor(255, 255, 255), 3))  # X màu trắng
        margin = 8
        x1 = self.close_button_rect.left() + margin
        y1 = self.close_button_rect.top() + margin
        x2 = self.close_button_rect.right() - margin
        y2 = self.close_button_rect.bottom() - margin
        
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y1, x1, y2)
