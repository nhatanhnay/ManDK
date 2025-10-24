# -*- coding: utf-8 -*-

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from PyQt5 import QtWidgets, QtCore, QtGui


class AuthWidget(QtWidgets.QWidget):
    """Authentication widget displayed in main window"""
    
    # Signal emitted when authentication is successful
    authenticated = QtCore.pyqtSignal()
    
    # Credentials (password is stored as Argon2 hash)
    ADMIN_USERNAME = "admin"
    # Argon2 hash of "CHXHCNVietN@m"
    ADMIN_PASSWORD_HASH = "$argon2id$v=19$m=102400,t=2,p=8$1Gp7SZTdBLyFE7I4weqgRA$mnQecavQHUd2Ip+6dlRbTQ"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the authentication UI"""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Center container
        center_widget = QtWidgets.QWidget()
        center_widget.setMaximumWidth(450)
        center_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
        """)
        
        # Center the widget
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(center_widget)
        h_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()
        
        # Form layout
        form_layout = QtWidgets.QVBoxLayout(center_widget)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Icon - Vietnam flag
        icon_label = QtWidgets.QLabel()
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Load Vietnam flag icon
        from ui.widgets.compass_widget import resource_path
        from PyQt5.QtGui import QPixmap
        icon_path = resource_path('assets/Icons/Vietnam.png')
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            # Scale to appropriate size (80x80)
            scaled_pixmap = pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to emoji if image not found
            icon_label.setStyleSheet("font-size: 48px;")
            icon_label.setText("🔐")
        
        form_layout.addWidget(icon_label)
        
        # Title
        title_label = QtWidgets.QLabel("XÁC THỰC ADMIN")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        form_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QtWidgets.QLabel("Vui lòng đăng nhập để tiếp tục")
        subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: #888888;
            font-size: 13px;
            margin-bottom: 20px;
        """)
        form_layout.addWidget(subtitle_label)
        
        # Username field
        username_container = QtWidgets.QWidget()
        username_layout = QtWidgets.QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(8)
        
        username_label = QtWidgets.QLabel("Tên đăng nhập")
        username_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        username_layout.addWidget(username_label)
        
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #64C8FF;
            }
        """)
        username_layout.addWidget(self.username_input)
        form_layout.addWidget(username_container)
        
        # Password field
        password_container = QtWidgets.QWidget()
        password_layout = QtWidgets.QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)
        
        password_label = QtWidgets.QLabel("Mật khẩu")
        password_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        password_layout.addWidget(password_label)
        
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #64C8FF;
            }
        """)
        password_layout.addWidget(self.password_input)
        form_layout.addWidget(password_container)
        
        # Error label
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("""
            color: #ff4444;
            font-size: 13px;
            padding: 8px;
            background-color: #3d1f1f;
            border-radius: 5px;
        """)
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setVisible(False)
        form_layout.addWidget(self.error_label)
        
        # Login button
        self.login_btn = QtWidgets.QPushButton("ĐĂNG NHẬP")
        self.login_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #64C8FF;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #50B4E6;
            }
            QPushButton:pressed {
                background-color: #3CA0D2;
            }
        """)
        self.login_btn.clicked.connect(self.validate_credentials)
        form_layout.addWidget(self.login_btn)
        
        # Exit button
        self.exit_btn = QtWidgets.QPushButton("Thoát ứng dụng")
        self.exit_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #ffffff;
                border: 1px solid #777777;
            }
        """)
        self.exit_btn.clicked.connect(self.exit_application)
        form_layout.addWidget(self.exit_btn)
        
        # Enter key triggers login
        self.password_input.returnPressed.connect(self.validate_credentials)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        
        # Focus on username field
        QtCore.QTimer.singleShot(100, self.username_input.setFocus)
    
    def validate_credentials(self):
        """Validate entered credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Vui lòng nhập đầy đủ thông tin!")
            return
        
        # Verify password using Argon2
        if username == self.ADMIN_USERNAME:
            try:
                ph = PasswordHasher()
                ph.verify(self.ADMIN_PASSWORD_HASH, password)
                # Successful login
                self.error_label.setVisible(False)
                self.authenticated.emit()
                return
            except VerifyMismatchError:
                # Wrong password
                pass
        
        # Failed login (wrong username or password)
        self.show_error("Tên đăng nhập hoặc mật khẩu không đúng!")
        self.password_input.clear()
        self.password_input.setFocus()
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        
        # Shake animation
        self.shake_widget(self.error_label)
    
    def shake_widget(self, widget):
        """Shake animation for error feedback"""
        animation = QtCore.QPropertyAnimation(widget, b"pos")
        animation.setDuration(500)
        animation.setLoopCount(1)
        
        pos = widget.pos()
        animation.setKeyValueAt(0, pos)
        animation.setKeyValueAt(0.1, QtCore.QPoint(pos.x() + 10, pos.y()))
        animation.setKeyValueAt(0.2, QtCore.QPoint(pos.x() - 10, pos.y()))
        animation.setKeyValueAt(0.3, QtCore.QPoint(pos.x() + 10, pos.y()))
        animation.setKeyValueAt(0.4, QtCore.QPoint(pos.x() - 10, pos.y()))
        animation.setKeyValueAt(0.5, QtCore.QPoint(pos.x() + 10, pos.y()))
        animation.setKeyValueAt(0.6, QtCore.QPoint(pos.x() - 10, pos.y()))
        animation.setKeyValueAt(0.7, QtCore.QPoint(pos.x() + 5, pos.y()))
        animation.setKeyValueAt(0.8, QtCore.QPoint(pos.x() - 5, pos.y()))
        animation.setKeyValueAt(0.9, QtCore.QPoint(pos.x() + 5, pos.y()))
        animation.setKeyValueAt(1, pos)
        
        animation.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
    
    def exit_application(self):
        """Exit the application"""
        QtWidgets.QApplication.quit()
    
    def paintEvent(self, event):
        """Paint the background"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Background color
        painter.fillRect(self.rect(), QtGui.QColor("#121212"))
