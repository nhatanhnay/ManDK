import sys
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

# Updated imports for new file structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_management import system_data_manager, module_manager

# Import components
from ui.components.grid_background_renderer import GridBackgroundWidget
from ui.components.system_diagram_renderer import SystemDiagramRenderer
from ui.components.info_panel_renderer import InfoPanelRenderer
from ui.components.event_handler import InfoTabEventHandler


# Refactored: Use common utilities instead of duplicated function
try:
    from common.utils import resource_path
    from common.constants import DATA_UPDATE_INTERVAL
except ImportError:
    # Fallback implementation
    def resource_path(relative_path):
        """Lấy đường dẫn tuyệt đối đến file resource."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)

    DATA_UPDATE_INTERVAL = 1000  # Fallback constant


class InfoTab(GridBackgroundWidget):
    """Main InfoTab coordinator that orchestrates all components."""

    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data

        # Initialize components
        self.system_diagram_renderer = SystemDiagramRenderer()
        self.info_panel_renderer = InfoPanelRenderer()
        self.event_handler = InfoTabEventHandler()

        # Timer để cập nhật dữ liệu và mô phỏng - Refactored to use constant
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self._update_data)
        self.data_timer.start(DATA_UPDATE_INTERVAL)  # Cập nhật mỗi giây

    def _update_data(self):
        """Cập nhật dữ liệu mô phỏng và refresh display."""
        system_data_manager.simulate_data()
        module_manager.simulate_realtime_data()  # Cập nhật dữ liệu module
        self.update()  # Trigger repaint

    def mousePressEvent(self, event):
        """Xử lý sự kiện click chuột."""
        node_regions = self.system_diagram_renderer.node_regions
        should_update = self.event_handler.handle_mouse_press(event, node_regions, self.size())

        if should_update:
            self.update()
        else:
            super().mousePressEvent(event)

    def wheelEvent(self, event):
        """Xử lý sự kiện scroll wheel."""
        should_update = self.event_handler.handle_wheel_event(event)

        if should_update:
            self.update()
            event.accept()
        else:
            super().wheelEvent(event)

    def paintEvent(self, event):
        """Override để vẽ cả background grid và sơ đồ hệ thống."""
        # Vẽ background grid trước
        super().paintEvent(event)

        # Vẽ sơ đồ hệ thống
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.system_diagram_renderer.draw_system_diagram(painter, self.size())

        # Vẽ info panel nếu được yêu cầu
        state = self.event_handler.get_state()
        if state['show_info_panel'] and state['selected_node_data']:
            max_scroll = self.info_panel_renderer.draw_info_panel(
                painter,
                self.rect(),
                state['selected_node_data'],
                state['info_panel_rect'],
                state['close_button_rect'],
                state['scroll_offset']
            )
            # Cập nhật scroll limits
            if max_scroll is not None:
                self.event_handler.update_scroll_limits(max_scroll)

            # Update parameter boxes for click detection
            parameter_boxes = self.info_panel_renderer.get_parameter_boxes()
            self.event_handler.update_parameter_boxes(parameter_boxes)