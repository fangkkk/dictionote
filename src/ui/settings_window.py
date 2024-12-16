from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QPushButton,
    QFontDialog, QColorDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt
from ..utils.config_manager import ConfigManager

class SettingsWindow(QDialog):
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.parent_window = parent  # 保存父窗口引用
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("设置")
        self.setFixedSize(800, 500)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        layout.setSpacing(0)  # 移除间距
        
        # 左侧列表
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(200)
        
        # 添加设置项
        items = [
            ("外观", "appearance"),
            ("字体", "fonts"),
            ("颜色", "colors"),
            ("关于", "about")
        ]
        
        for text, data in items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        # 右侧堆叠窗口
        self.stack = QStackedWidget()
        
        # 添加各个设置页面
        self.setup_appearance_page()
        self.setup_fonts_page()
        self.setup_colors_page()
        self.setup_about_page()
        
        layout.addWidget(self.stack)
        
        # 连接信号
        self.list_widget.currentRowChanged.connect(self.stack.setCurrentIndex)
        
        # 默认选中第一项
        self.list_widget.setCurrentRow(0)
    
    def apply_styles(self):
        """应用统一样式"""
        # 获取全局颜色
        toolbar_bg = self.config_manager.get("colors.toolbar_bg", "#ffffff")
        editor_bg = self.config_manager.get("colors.editor_bg", "#ffffff")
        editor_text = self.config_manager.get("colors.editor_text", "#2c3e50")
        title_text = self.config_manager.get("colors.title_text", "#2c3e50")
        
        # 获取全局字体
        font_family = self.config_manager.get("fonts.editor_family", "Consolas")
        font_size = self.config_manager.get("fonts.editor_size", 11)
        
        # 设置全局字体
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # 左侧列表样式
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {toolbar_bg};
                border: none;
                border-right: 1px solid #dcdde1;
                color: {title_text};
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #dcdde1;
            }}
            QListWidget::item:selected {{
                background-color: {editor_bg};
                color: {title_text};
                border-left: 4px solid #3498db;
            }}
            QListWidget::item:hover {{
                background-color: {QColor(toolbar_bg).darker(105).name()};
            }}
        """)
        
        # 右侧区域样式
        self.stack.setStyleSheet(f"""
            QWidget {{
                background-color: {editor_bg};
                color: {title_text};
            }}
            QPushButton {{
                background-color: {toolbar_bg};
                border: 1px solid #dcdde1;
                padding: 8px;
                border-radius: 4px;
                margin: 5px;
                color: {title_text};
            }}
            QPushButton:hover {{
                background-color: {QColor(toolbar_bg).darker(105).name()};
            }}
            QLabel {{
                color: {title_text};
                padding: 5px;
            }}
        """)
    
    def setup_appearance_page(self):
        """设置外观页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # 添加外观设置选项
        layout.addWidget(QLabel("主题"))
        # ... 添加主题选择控件
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def setup_fonts_page(self):
        """设置字体页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 便签字体
        font_btn = QPushButton("便签字体设置")
        font_btn.clicked.connect(lambda: self.show_font_dialog("editor"))
        layout.addWidget(font_btn)
        
        # 添加说明标签
        note_label = QLabel("设置便签的显示字体，包括标题和内容。")
        note_label.setWordWrap(True)  # 允许文字换行
        note_label.setStyleSheet("color: #666;")
        layout.addWidget(note_label)
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def setup_colors_page(self):
        """设置颜色页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)  # 添加内边距
        
        # 添加颜色设置按钮
        color_settings = [
            ("背景颜色", "toolbar_bg"),  # 统一使用 toolbar_bg 作为背景色
            ("编辑区背景", "editor_bg"),
            ("编辑区文字", "editor_text"),
            ("标题文字", "title_text"),
        ]
        
        for text, key in color_settings:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, k=key: self.show_color_dialog(k))
            layout.addWidget(btn)
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def setup_about_page(self):
        """设置关于页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)  # 添加内边距
        
        # 添加关于信息
        title_label = QLabel("DictiNote")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        layout.addWidget(QLabel("版本：1.0.4"))
        layout.addWidget(QLabel("作者：F Ray"))
        layout.addWidget(QLabel("一个简单的便签应用"))
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def show_font_dialog(self, target: str):
        """显示字体选择对话框"""
        # 获取当前字体
        family = self.config_manager.get(f"fonts.{target}_family", "Consolas")
        size = self.config_manager.get(f"fonts.{target}_size", 11)
        current_font = QFont(family, size)
        
        # 显示字体对话框
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            # 保存字体设置到所有字体配置
            for key in ["editor", "title"]:
                if not self.config_manager.set(f"fonts.{key}_family", font.family()):
                    QMessageBox.warning(self, "错误", "保存字体系列设置失败")
                if not self.config_manager.set(f"fonts.{key}_size", font.pointSize()):
                    QMessageBox.warning(self, "错误", "保存字体大小设置失败")
            
            # 立即应用新的字体设置
            if hasattr(self.parent_window, 'apply_fonts'):
                self.parent_window.apply_fonts()
            # 更新设置窗口的样式
            self.apply_styles()
    
    def show_color_dialog(self, color_type: str):
        """显示颜色选择对话框"""
        # 获取当前颜色
        current_color = QColor(self.config_manager.get(f"colors.{color_type}", "#ffffff"))
        
        # 显示颜色对话框
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            # 保存颜色设置
            if not self.config_manager.set(f"colors.{color_type}", color.name()):
                QMessageBox.warning(self, "错误", "保存颜色设置失败")
            else:
                # 立即应用新的颜色设置
                if hasattr(self.parent_window, 'apply_colors'):
                    self.parent_window.apply_colors()
                # 更新设置窗口的样式
                self.apply_styles()
    