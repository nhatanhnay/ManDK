# -*- coding: utf-8 -*-
"""
Backwards compatibility layer for renamed files.
This ensures old import statements continue to work during transition.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import new modules and map them to old names
try:
    # Data management aliases
    import data_management.system_configuration as system_config
    import data_management.module_data_manager as module_data
    import data_management.configuration_manager as config_manager
    import data_management.node_data_manager as node_data
    import data_management.module_threshold_manager as module_thresholds
    import data_management.node_mapping_manager as node_mapping

    # Register old module names in sys.modules for backwards compatibility
    sys.modules['data.system_config'] = system_config
    sys.modules['data.module_data'] = module_data
    sys.modules['data.config_manager'] = config_manager
    sys.modules['data.node_data'] = node_data
    sys.modules['data.module_thresholds'] = module_thresholds
    sys.modules['data.node_mapping'] = node_mapping

    # UI component aliases
    import ui.components.ui_utilities as control_panel_utils
    import ui.widgets.compass_widget as compass
    import ui.widgets.half_compass_widget as half_compass
    import ui.widgets.ammunition_widget as bullet_widget
    import ui.widgets.numeric_display_widget as numeric_data
    import ui.widgets.custom_message_box_widget as custom_message_box
    import ui.components.grid_background_renderer as grid_background
    import ui.components.system_diagram_renderer as system_diagram_renderer
    import ui.components.info_panel_renderer as info_panel_renderer
    import ui.components.event_handler as event_handler

    # Register old component names
    sys.modules['control_panel.components.utils'] = control_panel_utils
    sys.modules['control_panel.components.compass'] = compass
    sys.modules['control_panel.components.half_compass'] = half_compass
    sys.modules['control_panel.components.bullet_widget'] = bullet_widget
    sys.modules['control_panel.components.numeric_data'] = numeric_data
    sys.modules['control_panel.components.custom_message_box'] = custom_message_box
    sys.modules['control_panel.components.grid_background'] = grid_background
    sys.modules['control_panel.components.system_diagram_renderer'] = system_diagram_renderer
    sys.modules['control_panel.components.info_panel_renderer'] = info_panel_renderer
    sys.modules['control_panel.components.event_handler'] = event_handler

    # Tab aliases
    import ui.tabs.main_control_tab as main_tab
    import ui.tabs.system_info_tab as info_tab
    import ui.tabs.event_log_tab as log_tab
    import ui.tabs.settings_tab as setting_tab

    sys.modules['control_panel.main_tab'] = main_tab
    sys.modules['control_panel.info_tab'] = info_tab
    sys.modules['control_panel.log_tab'] = log_tab
    sys.modules['control_panel.setting_tab'] = setting_tab

    # Communication aliases
    import communication.data_sender as sender
    import communication.data_receiver as receiver

    sys.modules['control_panel.sender'] = sender
    sys.modules['control_panel.receiver'] = receiver

    # UI config alias
    import ui.ui_config as ui_config
    sys.modules['control_panel.config'] = ui_config

    print("✅ Backwards compatibility layer loaded successfully")

except ImportError as e:
    print(f"⚠️  Warning: Could not load all modules for backwards compatibility: {e}")
    print("Some old import statements may not work. Consider updating imports.")

except Exception as e:
    print(f"❌ Error setting up backwards compatibility: {e}")


def enable_legacy_imports():
    """
    Call this function to ensure legacy import statements work.
    This is automatically called when this module is imported.
    """
    pass


# Auto-enable when imported
enable_legacy_imports()