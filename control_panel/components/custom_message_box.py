from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

class CustomMessageBox:
    """Custom message box với style thống nhất."""
    
    STYLE_SHEET = """
        QMessageBox {
            background-color: #1E293B;
            color: #F1F5F9;
            border-radius: 16px;
            border: 1.5px solid rgba(0,0,0,0.2);
            font-family: 'Tahoma', Arial, sans-serif;
            font-size: 16px;
            min-width: 340px;
        }
        QMessageBox QLabel {
            font-size: 16px;
            color: #F1F5F9;
            background: transparent;
        }
        QMessageBox QPushButton {
            background-color: #10B981;
            color: #F1F5F9;
            padding: 7px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            margin: 0 8px;
            min-width: 100px;
        }
        QMessageBox QPushButton:hover {
            background-color: #059669;
        }
        QMessageBox QPushButton:pressed {
            background-color: #3B82F6;
        }
        /* Nút Cancel (No) */
        QMessageBox QPushButton[role="reject"],
        QMessageBox QPushButton:flat {
            background-color: #DC2626;
            color: #F1F5F9;
        }
        /* Nút OK (Yes) */
        QMessageBox QPushButton[role="accept"] {
            background-color: #10B981;
            color: #F1F5F9;
        }
    """

    @staticmethod
    def _center_on_screen(msg):
        """Đặt popup ở giữa màn hình."""
        if msg.parent():
            # Nếu có parent, đặt ở giữa parent
            parent_geometry = msg.parent().geometry()
            msg.move(
                parent_geometry.center().x() - msg.width() // 2,
                parent_geometry.center().y() - msg.height() // 2
            )
        else:
            # Nếu không có parent, đặt ở giữa màn hình
            screen_geometry = msg.screen().availableGeometry()
            msg.move(
                screen_geometry.center().x() - msg.width() // 2,
                screen_geometry.center().y() - msg.height() // 2
            )

    @staticmethod
    def warning(title, message, parent=None):
        """Hiển thị message box cảnh báo (không icon)."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        # Không setIcon
        msg.setStyleSheet(CustomMessageBox.STYLE_SHEET)
        # Đặt ở giữa màn hình
        msg.adjustSize()
        CustomMessageBox._center_on_screen(msg)
        return msg.exec_()

    @staticmethod
    def question(title, message, parent=None):
        """Hiển thị message box xác nhận (không icon, OK xanh, Cancel đỏ)."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        # Không setIcon
        yes = msg.addButton("OK", QMessageBox.YesRole)
        no = msg.addButton("Cancel", QMessageBox.NoRole)
        msg.setDefaultButton(yes)
        msg.setStyleSheet(CustomMessageBox.STYLE_SHEET)
        # Đặt màu cho từng nút bằng setStyleSheet riêng
        yes.setStyleSheet("background-color: #10B981; color: #F1F5F9; border-radius: 8px; font-weight: bold; font-size: 15px; min-width: 100px; margin: 0 8px;")
        no.setStyleSheet("background-color: #DC2626; color: #F1F5F9; border-radius: 8px; font-weight: bold; font-size: 15px; min-width: 100px; margin: 0 8px;")
        # Đặt ở giữa màn hình
        msg.adjustSize()
        CustomMessageBox._center_on_screen(msg)
        result = msg.exec_()
        if msg.clickedButton() == yes:
            return QMessageBox.Yes
        else:
            return QMessageBox.No

    @staticmethod
    def information(title, message, parent=None):
        """Hiển thị message box thông báo (không icon, không setIcon khi phóng thành công, nút OK xanh)."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        # Không setIcon
        ok = msg.addButton("OK", QMessageBox.AcceptRole)
        msg.setDefaultButton(ok)
        msg.setStyleSheet(CustomMessageBox.STYLE_SHEET)
        ok.setStyleSheet("background-color: #10B981; color: #F1F5F9; border-radius: 8px; font-weight: bold; font-size: 15px; min-width: 100px; margin: 0 8px;")
        # Đặt ở giữa màn hình
        msg.adjustSize()
        CustomMessageBox._center_on_screen(msg)
        return msg.exec_()