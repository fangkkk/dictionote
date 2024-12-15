from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal

class ColorDialog(QDialog):
    colorChanged = pyqtSignal(QColor)  # 颜色改变信号
    
    def __init__(self, current_color: QColor, parent=None):
        super().__init__(parent)
        self.setWindowTitle("背景颜色设置")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # 颜色代码输入区域
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("颜色代码:"))
        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("#RRGGBB")
        self.color_edit.setText(current_color.name().upper())
        self.color_edit.textChanged.connect(self.update_color)
        input_layout.addWidget(self.color_edit)
        
        layout.addLayout(input_layout)
        
        # 提示文本
        hint_label = QLabel("请输入十六进制颜色代码，例如: #DCDCDC")
        hint_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(hint_label)
        
        # 预览区域
        self.preview = QLabel()
        self.preview.setFixedHeight(50)
        self.preview.setStyleSheet(f"""
            background-color: {current_color.name()};
            border: 1px solid #ccc;
            border-radius: 3px;
        """)
        layout.addWidget(self.preview)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("应用")
        apply_button.clicked.connect(self.apply_color)
        button_layout.addWidget(apply_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_color(self, text: str):
        """更新预览颜色"""
        # 确保输入是有效的颜色代码
        if not text.startswith('#'):
            text = '#' + text
        
        if len(text) == 7 and all(c in '0123456789ABCDEFabcdef' for c in text[1:]):
            self.preview.setStyleSheet(f"""
                background-color: {text};
                border: 1px solid #ccc;
                border-radius: 3px;
            """)
    
    def apply_color(self):
        """应用颜色"""
        color_text = self.color_edit.text()
        if not color_text.startswith('#'):
            color_text = '#' + color_text
            
        if len(color_text) == 7 and all(c in '0123456789ABCDEFabcdef' for c in color_text[1:]):
            color = QColor(color_text)
            self.colorChanged.emit(color)
            self.accept() 