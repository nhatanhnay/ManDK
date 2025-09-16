import sys
import os
from PyQt5 import QtWidgets
from control_panel import FireControl
import time
import threading
import control_panel.receiver as receiver

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
