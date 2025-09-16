import sys
import os
from PyQt5.QtCore import Qt, QRect

# Thêm đường dẫn để import data module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data import system_data_manager


class InfoTabEventHandler:
    """Handles mouse and keyboard events for InfoTab."""

    def __init__(self):
        self.show_info_panel = False
        self.selected_node_data = None
        self.info_panel_rect = QRect()
        self.close_button_rect = QRect()
        self.scrollbar_rect = QRect()
        self.scrollbar_thumb_rect = QRect()
        self.scrolling = False
        self.scroll_offset = 0
        self.max_scroll = 0

    def handle_mouse_press(self, event, node_regions, widget_size):
        """Xử lý sự kiện click chuột."""
        if event.button() == Qt.LeftButton:
            click_pos = event.pos()

            # Nếu đang hiển thị info panel
            if self.show_info_panel:
                # Kiểm tra click vào nút đóng
                if self.close_button_rect.contains(click_pos):
                    self.show_info_panel = False
                    self.selected_node_data = None
                    return True

                # Kiểm tra click vào scrollbar
                if self.scrollbar_rect.contains(click_pos):
                    # Tính toán vị trí scroll mới
                    relative_y = click_pos.y() - self.scrollbar_rect.top()
                    scroll_ratio = relative_y / self.scrollbar_rect.height()
                    self.scroll_offset = int(scroll_ratio * self.max_scroll)
                    self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                    return True

                # Nếu click vào info panel thì không làm gì (để tránh đóng panel)
                if self.info_panel_rect.contains(click_pos):
                    return True
            else:
                # Kiểm tra xem click có trúng node nào không
                for region in node_regions:
                    if region['rect'].contains(click_pos):
                        # Lấy thông tin node và hiển thị info panel
                        node_data = system_data_manager.get_node(region['node_id'])
                        if node_data:
                            self.selected_node_data = node_data
                            self.show_info_panel = True
                            self.scroll_offset = 0  # Reset scroll
                            self._calculate_info_panel_rect(widget_size)
                            return True
                        break

        return False

    def handle_wheel_event(self, event):
        """Xử lý sự kiện scroll wheel."""
        if self.show_info_panel and self.selected_node_data:
            # Scroll trong info panel
            delta = event.angleDelta().y()
            scroll_step = 30

            if delta > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - scroll_step)
            else:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + scroll_step)

            return True

        return False

    def _calculate_info_panel_rect(self, widget_size):
        """Tính toán kích thước và vị trí của info panel."""
        padding = 10

        # Panel gần bằng kích thước tab với padding 10px
        panel_width = widget_size.width() - 2 * padding
        panel_height = widget_size.height() - 2 * padding

        # Vị trí panel
        x = padding
        y = padding

        self.info_panel_rect = QRect(x, y, panel_width, panel_height)

        # Vị trí nút đóng (góc trên phải)
        close_size = 30
        self.close_button_rect = QRect(
            x + panel_width - close_size - 15,
            y + 15,
            close_size,
            close_size
        )

        # Tính toán scrollbar rect
        content_x = self.info_panel_rect.left() + 290
        content_y = self.info_panel_rect.top() + 60
        content_width = self.info_panel_rect.width() - 330
        content_height = self.info_panel_rect.height() - 100

        scrollbar_width = 8
        scrollbar_x = content_x + content_width - scrollbar_width - 5
        scrollbar_y = content_y + 5
        scrollbar_height = content_height - 10

        self.scrollbar_rect = QRect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)

    def update_scroll_limits(self, max_scroll):
        """Cập nhật giới hạn scroll từ InfoPanelRenderer."""
        self.max_scroll = max_scroll

    def get_state(self):
        """Trả về state hiện tại của event handler."""
        return {
            'show_info_panel': self.show_info_panel,
            'selected_node_data': self.selected_node_data,
            'info_panel_rect': self.info_panel_rect,
            'close_button_rect': self.close_button_rect,
            'scroll_offset': self.scroll_offset,
            'max_scroll': self.max_scroll
        }