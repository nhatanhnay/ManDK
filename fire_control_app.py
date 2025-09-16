# Refactored: Import optimized and organized
import sys
import os
import time
import threading
from PyQt5 import QtWidgets

# Enable backwards compatibility for renamed files
import compatibility_layer

# Import project modules - Updated for new structure
from control_panel import FireControl
from communication import data_receiver as receiver

# Import common constants
try:
    from common.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
except ImportError:
    # Fallback constants
    DEFAULT_WINDOW_WIDTH = 1280
    DEFAULT_WINDOW_HEIGHT = 800

threading.Thread(target=receiver.run, daemon=True).start()
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = FireControl()
ui.setupUi(MainWindow)
MainWindow.show()
try:
    ui.main_tab.update_data()
    time.sleep(1)
except Exception as e:
    print(f"An error occurred: {e}")
sys.exit(app.exec_())
