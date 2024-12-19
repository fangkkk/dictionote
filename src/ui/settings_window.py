from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QPushButton,
    QFontDialog, QColorDialog, QMessageBox, QGroupBox, QComboBox,
    QCheckBox, QFileDialog, QSlider, QGridLayout, QMenu
)
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt
from ..utils.config_manager import ConfigManager
import os
import shutil

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
            ("文件", "files"),
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
        self.setup_files_page()
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
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 待机设置组
        idle_group = QGroupBox("待机设置")
        idle_layout = QVBoxLayout()
        
        # 待机时间选择
        idle_time_layout = QHBoxLayout()
        idle_time_layout.addWidget(QLabel("待机时间:"))
        
        self.idle_time_combo = QComboBox()
        idle_times = [
            ("1 分钟", 60000),
            ("3 分钟", 180000),
            ("5 分钟", 300000),
            ("10 分钟", 600000),
            ("15 分钟", 900000),
            ("30 分钟", 1800000),
            ("从不", 0)
        ]
        
        current_idle_time = self.config_manager.get("appearance.idle_time", 300000)
        current_index = 2  # 默认5分钟
        
        for i, (text, value) in enumerate(idle_times):
            self.idle_time_combo.addItem(text, value)
            if value == current_idle_time:
                current_index = i
        
        self.idle_time_combo.setCurrentIndex(current_index)
        self.idle_time_combo.currentIndexChanged.connect(self.on_idle_time_changed)
        
        idle_time_layout.addWidget(self.idle_time_combo)
        idle_time_layout.addStretch()
        idle_layout.addLayout(idle_time_layout)
        
        # 添加词条切换时间设置
        word_time_layout = QHBoxLayout()
        word_time_layout.addWidget(QLabel("词条切换:"))
        
        self.word_time_combo = QComboBox()
        word_times = [
            ("5 秒", 5),
            ("10 秒", 10),
            ("30 秒", 30),
            ("1 分钟", 60),
            ("3 分钟", 180),
            ("5 分钟", 300)
        ]
        
        current_word_time = self.config_manager.get("appearance.word_interval", 30)
        current_word_index = 2  # 默认30秒
        
        for i, (text, value) in enumerate(word_times):
            self.word_time_combo.addItem(text, value)
            if value == current_word_time:
                current_word_index = i
        
        self.word_time_combo.setCurrentIndex(current_word_index)
        self.word_time_combo.currentIndexChanged.connect(self.on_word_time_changed)
        
        word_time_layout.addWidget(self.word_time_combo)
        word_time_layout.addStretch()
        idle_layout.addLayout(word_time_layout)
        
        # 待机显示模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("待机显示:"))
        
        self.idle_mode_combo = QComboBox()
        modes = [
            ("词典模式", "dictionary"),
            ("时钟模式", "clock")
        ]
        
        current_mode = self.config_manager.get("appearance.idle_mode", "dictionary")
        for text, value in modes:
            self.idle_mode_combo.addItem(text, value)
            if value == current_mode:
                self.idle_mode_combo.setCurrentText(text)
        
        self.idle_mode_combo.currentIndexChanged.connect(self.on_idle_mode_changed)
        mode_layout.addWidget(self.idle_mode_combo)
        mode_layout.addStretch()
        idle_layout.addLayout(mode_layout)
        
        idle_group.setLayout(idle_layout)
        layout.addWidget(idle_group)
        layout.addStretch()
        self.stack.addWidget(page)
    
    def update_dict_list(self):
        """更新字典列表"""
        self.dict_combo.clear()
        dict_dir = "dict"
        if os.path.exists(dict_dir):
            for file in os.listdir(dict_dir):
                if file.endswith('.mdx'):
                    self.dict_combo.addItem(file)
        
        # 设置当前选中的字典
        current_dict = self.config_manager.get("dictionary.current", "")
        index = self.dict_combo.findText(current_dict)
        if index >= 0:
            self.dict_combo.setCurrentIndex(index)
        
        self.dict_combo.currentTextChanged.connect(self.on_dict_changed)
    
    def add_dictionary(self):
        """添加字典文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择字典文件",
            "",
            "MDX Files (*.mdx)"
        )
        
        if file_name:
            # 复制文件到dict目录
            dict_dir = "dict"
            os.makedirs(dict_dir, exist_ok=True)
            target_path = os.path.join(dict_dir, os.path.basename(file_name))
            shutil.copy2(file_name, target_path)
            
            # 更新字典列表
            self.update_dict_list()
    
    def on_word_time_changed(self, index):
        """词条切换时间改变"""
        interval = self.word_time_combo.currentData()
        self.config_manager.set("appearance.word_interval", interval)
    
    def on_dict_changed(self, dict_name):
        """字典选择改变"""
        self.config_manager.set("dictionary.current", dict_name)
    
    def setup_fonts_page(self):
        """设置字体页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 字体选择组
        font_group = QGroupBox("字体配置")
        font_layout = QVBoxLayout()
        
        # 创建6个字体配置行
        self.font_rows = []
        for i in range(6):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # 字体预览按钮
            font_btn = QPushButton()
            font_btn.setFixedSize(120, 40)  # 增加按钮宽度
            
            # 获取预设字体信息但不应用到按钮
            font_family = self.config_manager.get(f"fonts.preset_{i}_family", "宋体")
            font_size = self.config_manager.get(f"fonts.preset_{i}_size", 12)
            
            # 使用固定字体显示文本
            fixed_font = QFont()
            fixed_font.setFamily("Microsoft YaHei")
            fixed_font.setPointSize(12)
            font_btn.setFont(fixed_font)
            
            # 显示预设字体信息
            font_btn.setText(f"{font_family} {font_size}")
            
            font_btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #dcdde1;
                    border-radius: 4px;
                    text-align: left;
                    padding-left: 10px;
                }
                QPushButton:hover {
                    border: 2px solid #3498db;
                }
            """)
            font_btn.clicked.connect(lambda checked, idx=i: self.select_preset_font(idx))
            row_layout.addWidget(font_btn)
            
            # 添加按钮
            add_btn = QPushButton()
            add_btn.setFixedSize(24, 24)
            add_btn.setIcon(QIcon("resources/icons/new.png"))
            add_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 3px;
                    border-radius: 3px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #f5f6fa;
                }
            """)
            add_btn.clicked.connect(lambda checked, idx=i: self.show_font_apply_menu(idx))
            row_layout.addWidget(add_btn)
            
            # 应用项目标签区域
            items_widget = QWidget()
            items_layout = QHBoxLayout(items_widget)
            items_layout.setContentsMargins(10, 0, 0, 0)
            items_layout.setSpacing(5)
            row_layout.addWidget(items_widget)
            
            row_layout.addStretch()
            font_layout.addWidget(row_widget)
            
            # 保存行的引用
            row = {
                'font_btn': font_btn,
                'add_btn': add_btn,
                'items_widget': items_widget,
                'applied_items': set()
            }
            self.font_rows.append(row)
            
            # 恢复已保存的字体设置
            preset_family = self.config_manager.get(f"fonts.preset_{i}_family", "宋体")
            preset_size = self.config_manager.get(f"fonts.preset_{i}_size", 12)
            
            # 遍历所有可能的文字项，检查是否使用了这个预设
            text_items = [
                ("便签标题", "title_text"),
                ("便签内容", "editor_text"),
                ("词条文字", "word"),
                ("释义文字", "meaning"),
                ("时钟文字", "clock"),
                ("日期文字", "date")
            ]
            
            # 检查配置中的字体设置
            fonts_config = self.config_manager.config.get('fonts', {})
            for text, key in text_items:
                family_key = f"{key}_family"
                size_key = f"{key}_size"
                
                # 如果配置中存在这个字体设置，且与当前预设匹配
                if (family_key in fonts_config and size_key in fonts_config and
                    fonts_config[family_key] == preset_family and 
                    fonts_config[size_key] == preset_size):
                    # 恢复标签
                    self.apply_font_to_item(i, key)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        layout.addStretch()
        self.stack.addWidget(page)
    
    def setup_colors_page(self):
        """设置颜色页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 颜色选择组
        color_group = QGroupBox("颜色配置")
        color_layout = QVBoxLayout()
        
        # 在创建颜色行之前，确保默认颜色设置存在
        default_colors = {
            "editor_text": "#000000",
            "title_text": "#000000",
            "word": "#000000",
            "meaning": "#000000",
            "clock": "#000000",
            "date": "#000000",
            "editor_bg": "#e2ebf0",
            "title_bg": "#ffffff",
            "toolbar_bg": "#cfd9df"
        }
        
        # 检查并设置默认颜色
        colors_config = self.config_manager.config.get('colors', {})
        for key, default_value in default_colors.items():
            if key not in colors_config:
                self.config_manager.set(f"colors.{key}", default_value)
        
        # 创建6个颜色配置行
        self.color_rows = []
        for i in range(6):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # 颜色按钮
            color_btn = QPushButton()
            color_btn.setFixedSize(40, 40)
            
            # 获取预设颜色，如果不存在则使用默认颜色
            preset_color = self.config_manager.get(f"colors.preset_{i}", None)
            if preset_color is None:
                # 为每个预设设置不同的默认颜色
                default_presets = ["#000000", "#ffffff", "#e2ebf0", "#cfd9df", "#f5f6fa", "#dcdde1"]
                preset_color = default_presets[i]
                self.config_manager.set(f"colors.preset_{i}", preset_color)
            
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {preset_color};
                    border: 1px solid #dcdde1;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border: 2px solid #3498db;
                }}
            """)
            color_btn.clicked.connect(lambda checked, idx=i: self.select_palette_color(idx))
            row_layout.addWidget(color_btn)
            
            # 添加按钮 - 使用与便签添加相同的图标
            add_btn = QPushButton()
            add_btn.setFixedSize(24, 24)  # 调整大小以匹配便签添加按钮
            add_btn.setIcon(QIcon("resources/icons/new.png"))  # 使用相同的图标
            add_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 3px;
                    border-radius: 3px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #f5f6fa;
                }
            """)
            add_btn.clicked.connect(lambda checked, idx=i: self.show_apply_menu(idx))
            row_layout.addWidget(add_btn)
            
            # 应用项目标签区域
            items_widget = QWidget()
            items_layout = QHBoxLayout(items_widget)
            items_layout.setContentsMargins(10, 0, 0, 0)
            items_layout.setSpacing(5)
            row_layout.addWidget(items_widget)
            
            row_layout.addStretch()
            color_layout.addWidget(row_widget)
            
            # 保存行的引用
            row = {
                'color_btn': color_btn,
                'add_btn': add_btn,
                'items_widget': items_widget,
                'applied_items': set()
            }
            self.color_rows.append(row)
            
            # 恢复已保存的颜色设置
            preset_color = self.config_manager.get(f"colors.preset_{i}", "#ffffff")
            
            # 检查配置中的颜色设置
            colors_config = self.config_manager.config.get('colors', {})
            text_items = [
                ("编辑器文字", "editor_text"),
                ("标题栏文字", "title_text"),
                ("单词", "word"),
                ("释义", "meaning"),
                ("时钟", "clock"),
                ("日期", "date")
            ]
            
            background_items = [
                ("编辑器背景", "editor_bg"),
                ("标题栏背景", "title_bg"),
                ("工具栏背景", "toolbar_bg")
            ]
            
            for text, key in text_items + background_items:
                # 如果配置中存在这个颜色设置，且与当前预设匹配
                if key in colors_config and colors_config[key] == preset_color:
                    # 恢复标签
                    self.apply_color_to_item(i, key, key in [k for _, k in background_items])
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        layout.addStretch()
        self.stack.addWidget(page)
    
    def select_palette_color(self, index):
        """选择调色板颜色"""
        color = QColorDialog.getColor(QColor(self.config_manager.get(f"colors.preset_{index}", "#ffffff")))
        if color.isValid():
            # 保存预设颜色
            self.config_manager.set(f"colors.preset_{index}", color.name())
            # 更新按钮颜色
            self.color_rows[index]['color_btn'].setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 1px solid #dcdde1;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border: 2px solid #3498db;
                }}
            """)
            
            # 更新所有使用这个预设的项目
            row = self.color_rows[index]
            for key in row['applied_items'].copy():
                self.config_manager.set(f"colors.{key}", color.name())
                # 更新主窗口颜色
                if hasattr(self.parent_window, 'apply_colors'):
                    self.parent_window.apply_colors()
                # 更新词典界面颜色
                if hasattr(self.parent_window, 'idle_screen'):
                    self.parent_window.idle_screen.apply_colors()
    
    def show_apply_menu(self, color_index):
        """显示应用颜色菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #2d3436;
            }
            QMenu::item:selected {
                background-color: #f5f6fa;
            }
        """)
        
        # 所有可配置的项目
        text_items = [
            ("编辑器文字", "editor_text"),
            ("标题栏文字", "title_text"),
            ("单词", "word"),
            ("释义", "meaning"),
            ("时钟", "clock"),
            ("日期", "date")
        ]
        
        background_items = [
            ("编辑器背景", "editor_bg"),
            ("标题栏背景", "title_bg"),
            ("工具栏背景", "toolbar_bg")
        ]
        
        def create_menu_items(items, is_background=False):
            menu_items = []
            for text, key in items:
                if key not in applied_items:
                    action = menu.addAction(text)
                    action.setData((key, is_background))
                    menu_items.append(action)
            return menu_items
        
        # 获取所有已被应用的项目
        applied_items = set()
        for row in self.color_rows:
            applied_items.update(row['applied_items'])
        
        # 在 show_apply_menu 方法中修改菜单创建
        menu.addSection("文字颜色")
        for text, key in text_items:
            if key not in applied_items:
                action = menu.addAction(text)
                action.setData((key, False))
                action.triggered.connect(lambda checked, k=key: self.apply_color_to_item(color_index, k, False))
        
        menu.addSection("背景颜色")
        for text, key in background_items:
            if key not in applied_items:
                action = menu.addAction(text)
                action.setData((key, True))
                action.triggered.connect(lambda checked, k=key: self.apply_color_to_item(color_index, k, True))
        
        # 在添加按钮位置显示菜单
        add_btn = self.color_rows[color_index]['add_btn']
        menu.exec(add_btn.mapToGlobal(add_btn.rect().bottomLeft()))
    
    def apply_color_to_item(self, color_index, key, is_background=False):
        """将颜色应用到指定项目"""
        # 获取预设颜色
        color = self.config_manager.get(f"colors.preset_{color_index}", "#ffffff")
        
        # 保存颜色设置到配置文件
        self.config_manager.set(f"colors.{key}", color)
        
        # 添加标签显示
        row = self.color_rows[color_index]
        items_layout = row['items_widget'].layout()
        
        # 创建标签容器
        label_container = QWidget()
        container_layout = QHBoxLayout(label_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)
        
        # 创建文本标签
        text_label = QLabel(next(text for text, k in [
            ("编辑器文字", "editor_text"),
            ("标题栏文字", "title_text"),
            ("单词", "word"),
            ("释义", "meaning"),
            ("时钟", "clock"),
            ("日期", "date"),
            ("编辑器背景", "editor_bg"),
            ("标题栏背景", "title_bg"),
            ("工具栏背景", "toolbar_bg")
        ] if k == key))
        
        # 强制设置固定字体大小
        fixed_font = QFont()
        fixed_font.setPointSize(12)  # 设置固定大小
        fixed_font.setFamily("Microsoft YaHei")  # 使用系统字体
        text_label.setFont(fixed_font)
        
        # 创建关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 14px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #e74c3c;
            }
        """)
        
        # 将标签和按钮添加到容器
        container_layout.addWidget(text_label)
        container_layout.addWidget(close_btn)
        
        # 设置容器样式
        label_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 10px;
                padding: 3px 8px;
            }
            QLabel {
                color: #2d3436;
                font-size: 12px;  /* 固定字体大小 */
            }
        """)
        
        items_layout.addWidget(label_container)
        
        # 记录已应用的项目
        row['applied_items'].add(key)
        
        # 修改关闭按钮点击事件
        def remove_item():
            # 从已应用项目中移除
            row['applied_items'].remove(key)
            # 移除标签容器
            label_container.deleteLater()
            # 不再从配置中移除颜色设置，保留设置直到下次更改
            # self.config_manager.set(f"colors.{key}", None)  # 注释掉这行
            # 更新主窗口颜色
            if hasattr(self.parent_window, 'apply_colors'):
                self.parent_window.apply_colors()
            # 更新词典界面颜色
            if hasattr(self.parent_window, 'idle_screen'):
                self.parent_window.idle_screen.apply_colors()
        
        close_btn.clicked.connect(remove_item)
    
    def setup_about_page(self):
        """设置关于页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        layout.addWidget(QLabel("版本：1.1.1"))
        layout.addWidget(QLabel("作者：F Ray"))
        layout.addWidget(QLabel("一个简单的便签应用"))
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def show_font_dialog(self, target: str):
        """显示字体选择对话框"""
        # 获取当前字体
        family = self.config_manager.get(f"fonts.{target}_family", "Arial")
        size = self.config_manager.get(f"fonts.{target}_size", 11)
        current_font = QFont(family, size)
        
        # 显示字体对话框
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            # 保存字体设置
            self.config_manager.set(f"fonts.{target}_family", font.family())
            self.config_manager.set(f"fonts.{target}_size", font.pointSize())
            
            # 根据不同目标更新界面
            if target == "editor_text":
                # 更新编辑器字体
                if hasattr(self.parent_window, 'apply_fonts'):
                    self.parent_window.apply_fonts()
            elif target in ["word", "meaning", "clock", "date", "title_text"]:
                # 更新待机界面字体
                if hasattr(self.parent_window, 'idle_screen'):
                    self.parent_window.idle_screen.setup_ui()  # 重新设置UI以应用新字体
            
            # 更新设置窗口的样式
            self.apply_styles()
    
    def show_color_dialog(self, color_type: str):
        """显示颜色选择对话框"""
        current_color = QColor(self.config_manager.get(f"colors.{color_type}", "#000000"))
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            self.config_manager.set(f"colors.{color_type}", color.name())
            # 立即应用新的颜色设置
            if hasattr(self.parent_window, 'apply_colors'):
                self.parent_window.apply_colors()
    
    def on_idle_time_changed(self, index):
        """待机时间改变时"""
        idle_time = self.idle_time_combo.currentData()
        if not self.config_manager.set("appearance.idle_time", idle_time):
            QMessageBox.warning(self, "错误", "保存待机时间设置失败")
        else:
            # 更新主窗口的待机时间
            if hasattr(self.parent_window, 'set_idle_time'):
                self.parent_window.set_idle_time(idle_time)
    
    def on_bg_color_clicked(self):
        """背景颜色选择"""
        current_color = QColor(self.config_manager.get("appearance.idle_bg_color", "#ffffff"))
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            self.config_manager.set("appearance.idle_bg_color", color.name())
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def on_opacity_changed(self, value):
        """不透明度改变"""
        self.config_manager.set("appearance.idle_opacity", value)
        self.opacity_label.setText(f"{value}%")
    
    def on_idle_mode_changed(self, index):
        """待机模式改变"""
        mode = self.idle_mode_combo.currentData()
        self.config_manager.set("appearance.idle_mode", mode)
    
    def select_preset_font(self, index):
        """选择预设字体"""
        current_font = QFont(
            self.config_manager.get(f"fonts.preset_{index}_family", "宋体"),
            self.config_manager.get(f"fonts.preset_{index}_size", 12)
        )
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            # 保存预设字体设置
            self.config_manager.set(f"fonts.preset_{index}_family", font.family())
            self.config_manager.set(f"fonts.preset_{index}_size", font.pointSize())
            
            # 更新按钮文本，但保持固定字体
            btn = self.font_rows[index]['font_btn']
            btn.setText(f"{font.family()} {font.pointSize()}")
            
            # 更新所有使用这个预设的文字项
            row = self.font_rows[index]
            for key in row['applied_items'].copy():  # 使用copy避免在迭代时修改
                self.config_manager.set(f"fonts.{key}_family", font.family())
                self.config_manager.set(f"fonts.{key}_size", font.pointSize())
    
    def show_font_apply_menu(self, font_index):
        """显示字体应用菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #2d3436;
                font-family: "Microsoft YaHei";
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: #f5f6fa;
            }
        """)
        
        # 修正键值以保持一致
        text_items = [
            ("编辑器文字", "editor_text"),
            ("标题栏文字", "title_text"),
            ("单词", "word"),
            ("释义", "meaning"),
            ("时钟", "clock"),
            ("日期", "date")
        ]
        
        # 获取所有已被应用的项目
        applied_items = set()
        for row in self.font_rows:
            applied_items.update(row['applied_items'])
        
        # 添加可用的项目到菜单
        for text, key in text_items:
            if key not in applied_items:
                action = menu.addAction(text)
                action.setData(key)
                action.triggered.connect(lambda checked, k=key: self.apply_font_to_item(font_index, k))
        
        add_btn = self.font_rows[font_index]['add_btn']
        menu.exec(add_btn.mapToGlobal(add_btn.rect().bottomLeft()))
    
    def apply_font_to_item(self, font_index, key):
        """将字体应用到指定项目"""
        # 获取预设字体
        font_family = self.config_manager.get(f"fonts.preset_{font_index}_family", "宋体")
        font_size = self.config_manager.get(f"fonts.preset_{font_index}_size", 12)
        
        # 保存字体设置到配置文件
        self.config_manager.set(f"fonts.{key}_family", font_family)
        self.config_manager.set(f"fonts.{key}_size", font_size)
        
        # 添加标签显示
        row = self.font_rows[font_index]
        items_layout = row['items_widget'].layout()
        
        # 创建标签容器
        label_container = QWidget()
        container_layout = QHBoxLayout(label_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)
        
        # 创建文本标签
        text_label = QLabel(next(text for text, k in [
            ("编辑器文字", "editor_text"),
            ("标题栏文字", "title_text"),
            ("单词", "word"),
            ("释义", "meaning"),
            ("时钟", "clock"),
            ("日期", "date")
        ] if k == key))
        
        # 强制设置固定字体大小
        fixed_font = QFont()
        fixed_font.setPointSize(12)  # 设置固定大小
        fixed_font.setFamily("Microsoft YaHei")  # 使用系统字体
        text_label.setFont(fixed_font)
        
        # 创建关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 14px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #e74c3c;
            }
        """)
        
        # 将标签和按钮添加到容器
        container_layout.addWidget(text_label)
        container_layout.addWidget(close_btn)
        
        # 设置容器样式
        label_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 10px;
                padding: 3px 8px;
            }
            QLabel {
                color: #2d3436;
                font-size: 12px;  /* 固定字体大小 */
            }
        """)
        
        items_layout.addWidget(label_container)
        
        # 记录已应用的项目
        row['applied_items'].add(key)
        
        # 修改关闭按钮点击事件
        def remove_item():
            try:
                # 从已应用项目中移除
                row['applied_items'].remove(key)
                # 移除标签容器
                label_container.deleteLater()
                # 从配置中移除字体设置
                self.config_manager.set(f"fonts.{key}_family", None)
                self.config_manager.set(f"fonts.{key}_size", None)
                # 更新主窗口字体
                if hasattr(self.parent_window, 'apply_fonts'):
                    self.parent_window.apply_fonts()
            except RuntimeError:
                # 如果对象已被删除，忽略错误
                pass
        
        close_btn.clicked.connect(remove_item)
        
        # 更新主窗口字体
        if hasattr(self.parent_window, 'apply_fonts'):
            self.parent_window.apply_fonts()
    
    def setup_files_page(self):
        """设置文件页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 字典设置组
        dict_group = QGroupBox("字典设置")
        dict_layout = QVBoxLayout()
        
        # 当前字典显示
        current_dict_layout = QHBoxLayout()
        current_dict_layout.addWidget(QLabel("当前字典:"))
        self.current_dict_label = QLabel(self.config_manager.get("dictionary.current", "未选择"))
        current_dict_layout.addWidget(self.current_dict_label)
        current_dict_layout.addStretch()
        dict_layout.addLayout(current_dict_layout)
        
        # 字典操作按钮
        btn_layout = QHBoxLayout()
        
        # 添加字典按钮
        add_dict_btn = QPushButton("添加字典")
        add_dict_btn.clicked.connect(self.add_dictionary)
        btn_layout.addWidget(add_dict_btn)
        
        # 切换字典按钮
        switch_dict_btn = QPushButton("切换字典")
        switch_dict_btn.clicked.connect(self.switch_dictionary)
        btn_layout.addWidget(switch_dict_btn)
        
        btn_layout.addStretch()
        dict_layout.addLayout(btn_layout)
        
        dict_group.setLayout(dict_layout)
        layout.addWidget(dict_group)
        
        # 数据目录设置组
        data_group = QGroupBox("数据目录")
        data_layout = QVBoxLayout()
        
        # 便签存储目录
        notes_dir_layout = QHBoxLayout()
        notes_dir_layout.addWidget(QLabel("便签目录:"))
        self.notes_dir_label = QLabel(self.config_manager.get("storage.notes_dir", "data/notes"))
        notes_dir_layout.addWidget(self.notes_dir_label)
        notes_dir_layout.addStretch()
        data_layout.addLayout(notes_dir_layout)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def add_dictionary(self):
        """添加字典"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择字典文件",
            "",
            "MDX字典文件 (*.mdx)"
        )
        
        if file_name:
            # 复制字典文件到应用目录
            try:
                dict_dir = "dict"
                os.makedirs(dict_dir, exist_ok=True)
                
                # 获取文件名
                dict_name = os.path.basename(file_name)
                target_path = os.path.join(dict_dir, dict_name)
                
                # 复制文件
                shutil.copy2(file_name, target_path)
                
                # 更新配置
                self.config_manager.set("dictionary.current", dict_name)
                self.current_dict_label.setText(dict_name)
                
                # 重新加载字典
                if hasattr(self.parent_window, 'idle_screen'):
                    self.parent_window.idle_screen.dict_manager.load_dictionaries()
                
                QMessageBox.information(self, "成功", "字典添加成功！")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"添加字典失败：{str(e)}")
    
    def switch_dictionary(self):
        """切换字典"""
        dict_dir = "dict"
        if not os.path.exists(dict_dir):
            QMessageBox.warning(self, "错误", "字典目录不存在！")
            return
        
        # 获取可用字典列表
        dict_files = [f for f in os.listdir(dict_dir) if f.endswith('.mdx')]
        if not dict_files:
            QMessageBox.warning(self, "错误", "没有可用的字典文件！")
            return
        
        # 创建字典选择菜单
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #2d3436;
            }
            QMenu::item:selected {
                background-color: #f5f6fa;
            }
        """)
        
        for dict_file in dict_files:
            action = menu.addAction(dict_file)
            action.triggered.connect(lambda checked, f=dict_file: self.select_dictionary(f))
        
        # 显示菜单
        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
    
    def select_dictionary(self, dict_file):
        """选择字典"""
        try:
            # 更新配置
            self.config_manager.set("dictionary.current", dict_file)
            self.current_dict_label.setText(dict_file)
            
            # 重新加载字典
            if hasattr(self.parent_window, 'idle_screen'):
                self.parent_window.idle_screen.dict_manager.load_dictionaries()
            
            QMessageBox.information(self, "成功", "字典切换成功！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"切换字典失败：{str(e)}")
    