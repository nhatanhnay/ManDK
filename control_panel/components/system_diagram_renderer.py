import sys
import os
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics
import math

# Thêm đường dẫn để import data module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data import system_data_manager, get_node_id_for_compartment


class SystemDiagramRenderer:
    """Handles rendering of the fire control system diagram."""

    def __init__(self):
        self.node_regions = []

    def draw_system_diagram(self, painter, widget_size):
        """Vẽ sơ đồ hệ thống fire control."""
        # Reset danh sách vùng clickable
        self.node_regions = []

        # Thiết lập font cho text
        font = QFont("Arial", 10, QFont.Normal)
        painter.setFont(font)

        # Màu sắc cho các thành phần
        box_color = QColor(255, 255, 255)       # Màu trắng cho nền
        text_color = QColor(255, 255, 255)      # Màu trắng cho text
        border_color = QColor(255, 255, 255)    # Màu viền trắng

        # Kích thước và vị trí của các khoang
        compartment_width = 450
        compartment_width_center = 200  # Chiều ngang của khoang giữa bằng 1/2
        compartment_height = 400
        sight_column_height = 150  # Chiều cao cột ngắm thấp hơn
        spacing = 50

        # Tính toán vị trí để căn giữa
        total_width = 2 * compartment_width + compartment_width_center + 2 * spacing
        start_x = (widget_size.width() - total_width) // 2
        start_y = (widget_size.height() - compartment_height) // 2

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
        connections = self._get_connection_definitions()

        # Vẽ các kết nối
        connection_color = QColor(100, 200, 255)  # Màu xanh lam nhạt
        painter.setPen(QPen(connection_color, 2))

        for connection_data in connections:
            # Parse tuple length safely (support 2,6,7 length formats)
            if len(connection_data) == 7:
                start_comp, end_comp, start_edge, end_edge, start_offset, end_offset, straight_distance = connection_data
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
                if start_comp == 'hop_quang_dien_tu' or start_comp == 'hop_dien':
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

    def _get_connection_definitions(self):
        """Định nghĩa các kết nối giữa components."""
        return [
            # Khoang điều khiển tại chỗ 1
            ('tu_ac_quy_1', 'tu_phan_phoi_bien_doi_1', 3, 4, 0, 0),
            ('tu_phan_phoi_bien_doi_1', 'tu_bien_ap_1', 3, 1, 0, 0),
            ('tu_phan_phoi_bien_doi_1', 'tu_dieu_khien_tai_cho_1', 2, 3, -5, 0),
            ('tu_phan_phoi_bien_doi_1', 'ban_dieu_khien_tai_cho_1', 2, 4, 0, 0),
            ('ban_dieu_khien_tai_cho_1', 'tu_dieu_khien_tai_cho_1', 1, 2, 0, 5),
            ('tu_dieu_khien_tai_cho_1', 'hop_dan_dong_kenh_huong_1', 1, 2, 0, 0),
            ('tu_dieu_khien_tai_cho_1', 'hop_dan_dong_kenh_tam_1', 1, 2, -5, 0),
            ('tu_phan_phoi_bien_doi_1', 'hop_dan_dong_kenh_huong_1', 1, 4, 0, 0),
            ('tu_phan_phoi_bien_doi_1', 'hop_dan_dong_kenh_tam_1', 1, 4, 5, 0),
            ('hn12', 'hn11', 3, 1, 0, 0),
            ('hn11', 'tu_dieu_khien_tai_cho_1', 3, 2, 0, -5),
            ('tu_bien_ap_1', 'bang_dien_chinh', 2, 4, 0, 0),

            # Khoang điều khiển
            ('khoi_giao_tiep_hang_hai', 'ban_dieu_khien_chinh_tu_xa', 3, 1, 0, 0),
            ('ban_dieu_khien_chinh_tu_xa', 'bang_dien_chinh', 3, 1, 0, 0),
            ('ban_dieu_khien_chinh_tu_xa', 'tu_dieu_khien_tai_cho_1', 4, 2, 0, 0),
            ('ban_dieu_khien_chinh_tu_xa', 'tu_dieu_khien_tai_cho_2', 2, 4, 0, 0),

            # Khoang điều khiển tại chỗ 2
            ('tu_ac_quy_2', 'tu_phan_phoi_bien_doi_2', 3, 2, 0, 0),
            ('tu_phan_phoi_bien_doi_2', 'tu_bien_ap_2', 3, 1, 0, 0),
            ('tu_phan_phoi_bien_doi_2', 'tu_dieu_khien_tai_cho_2', 4, 3, -5, 0),
            ('tu_phan_phoi_bien_doi_2', 'ban_dieu_khien_tai_cho_2', 4, 2, 0, 0),
            ('ban_dieu_khien_tai_cho_2', 'tu_dieu_khien_tai_cho_2', 1, 4, 0, 5),
            ('tu_dieu_khien_tai_cho_2', 'hop_dan_dong_kenh_tam_2', 1, 4, 5, 0),
            ('tu_dieu_khien_tai_cho_2', 'hop_dan_dong_kenh_huong_2', 1, 4, 0, 0),
            ('tu_phan_phoi_bien_doi_2', 'hop_dan_dong_kenh_tam_2', 1, 2, -5, 0),
            ('tu_phan_phoi_bien_doi_2', 'hop_dan_dong_kenh_huong_2', 1, 2, 0, 0),
            ('hn22', 'hn21', 3, 1, 0, 0),
            ('hn21', 'tu_dieu_khien_tai_cho_2', 3, 4, 0, -5),
            ('tu_bien_ap_2', 'bang_dien_chinh', 4, 2, 0, 0),

            # Cột ngắm
            ('khoi_giao_tiep_hang_hai', 'hop_quang_dien_tu', 1, 3, 0, 0),
            ('hop_quang_dien_tu', 'ban_dieu_khien_chinh_tu_xa', 2, 2, 0, -10, 40),
            ('hop_dien', 'ban_dieu_khien_chinh_tu_xa', 2, 2, 0, -5, 50),
        ]

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
        """Lấy điểm kết nối từ cạnh được chỉ định."""
        if edge == 1:  # Trên
            return (pos['center_x'], pos['top'])
        elif edge == 2:  # Phải
            return (pos['right'], pos['center_y'])
        elif edge == 3:  # Dưới
            return (pos['center_x'], pos['bottom'])
        elif edge == 4:  # Trái
            return (pos['left'], pos['center_y'])
        else:
            return (pos['center_x'], pos['center_y'])

    def _get_edge_direction(self, pos, point):
        """Xác định hướng của cạnh dựa trên điểm kết nối."""
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
        """Tính toán điểm trung gian sau khi đi thẳng theo hướng cạnh."""
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

    def _draw_orthogonal_connection_special(self, painter, start_pos, end_pos, start_edge=None, end_edge=None,
                                          pos_offset_start=0, pos_offset_end=0, straight_distance=50):
        """Vẽ kết nối orthogonal đặc biệt cho cột ngắm."""
        start_point = None
        if start_edge is not None:
            start_point = self._get_point_from_edge(start_pos, start_edge)

        if start_point is None:
            start_point = (start_pos.get('center_x', 0), start_pos.get('center_y', 0))

        if end_edge is not None:
            final_point = self._get_point_from_edge(end_pos, end_edge)
        else:
            final_point = (end_pos['center_x'], end_pos['center_y'])

        # Apply offsets
        start_x, start_y = start_point
        final_x, final_y = final_point

        start_direction = self._get_edge_direction(start_pos, start_point)

        if start_direction == 1 or start_direction == 3:
            start_y += pos_offset_start
            final_y += pos_offset_end
        else:
            start_y += pos_offset_start
            final_y += pos_offset_end

        start_point = (start_x, start_y)
        final_point = (final_x, final_y)

        # Snap/grid size
        snap = 20

        if start_direction in (1, 3):
            shared_x = int(round(end_pos['center_x'] / snap) * snap)

            dir_sign = 1 if start_direction == 3 else -1
            inter_a = (start_point[0], start_point[1] + dir_sign * straight_distance)
            inter_b = (shared_x, inter_a[1])

            painter.drawLine(start_point[0], start_point[1], inter_a[0], inter_a[1])
            painter.drawLine(inter_a[0], inter_a[1], inter_b[0], inter_b[1])
            painter.drawLine(inter_b[0], inter_b[1], final_point[0], final_point[1])
        else:
            dir_sign = 1 if start_direction == 2 else -1
            inter_a = (start_point[0] + dir_sign * straight_distance, start_point[1])
            inter_b = (inter_a[0], final_point[1])

            painter.drawLine(start_point[0], start_point[1], inter_a[0], inter_a[1])
            painter.drawLine(inter_a[0], inter_a[1], inter_b[0], final_point[1])
            painter.drawLine(inter_b[0], final_point[1], final_point[0], final_point[1])

    def _draw_orthogonal_connection(self, painter, start_pos, end_pos, start_edge=None, end_edge=None,
                                  pos_offset_start=0, pos_offset_end=0):
        """Vẽ kết nối orthogonal thông thường."""
        start_point = None
        if start_edge is not None:
            start_point = self._get_point_from_edge(start_pos, start_edge)

        # Kiểm tra thẳng hàng
        horizontal_distance = abs(start_pos['center_x'] - end_pos['center_x'])
        vertical_distance = abs(start_pos['center_y'] - end_pos['center_y'])
        alignment_threshold = 30

        if horizontal_distance <= alignment_threshold:
            # Thẳng hàng dọc
            if start_pos['center_y'] < end_pos['center_y']:
                start_vertical_point = (start_pos['center_x'], start_pos['bottom'])
                end_vertical_point = (end_pos['center_x'], end_pos['top'])
            else:
                start_vertical_point = (start_pos['center_x'], start_pos['top'])
                end_vertical_point = (end_pos['center_x'], end_pos['bottom'])

            painter.drawLine(start_vertical_point[0], start_vertical_point[1],
                           end_vertical_point[0], end_vertical_point[1])
        elif vertical_distance <= alignment_threshold:
            # Thẳng hàng ngang
            if start_pos['center_x'] < end_pos['center_x']:
                start_side_point = (start_pos['right'], start_pos['center_y'])
                end_side_point = (end_pos['left'], end_pos['center_y'])
            else:
                start_side_point = (start_pos['left'], start_pos['center_y'])
                end_side_point = (end_pos['right'], end_pos['center_y'])

            painter.drawLine(start_side_point[0], start_side_point[1],
                           end_side_point[0], end_side_point[1])
        else:
            # Logic orthogonal phức tạp
            start_x, start_y = start_point

            start_direction = self._get_edge_direction(start_pos, start_point)
            if end_edge is not None:
                final_point = self._get_point_from_edge(end_pos, end_edge)

            final_x, final_y = final_point

            if start_direction == 1 or start_direction == 3:
                start_x += pos_offset_start
                final_y += pos_offset_end
            else:
                start_y += pos_offset_start
                final_x += pos_offset_end

            start_point = (start_x, start_y)
            final_point = (final_x, final_y)

            straight_distance = max(abs(final_x - start_x), abs(final_y - start_y))
            intermediate_point = self._get_intermediate_point(start_point, start_direction, straight_distance)

            painter.drawLine(start_point[0], start_point[1], intermediate_point[0], intermediate_point[1])
            painter.drawLine(intermediate_point[0], intermediate_point[1], final_point[0], final_point[1])