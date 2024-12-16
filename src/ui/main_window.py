from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QMessageBox, QPushButton,
    QMenu, QListWidget, QListWidgetItem, QApplication,
    QCalendarWidget, QDialog, QLabel, QSplitter, QFontDialog
)
from PyQt6.QtGui import QIcon, QColor, QPixmap, QFont
from PyQt6.QtCore import Qt, QPoint, QTimer, QDate
from ..main.note_manager import NoteManager
from ..utils.note_storage import NoteStorage
from .color_dialog import ColorDialog
from datetime import datetime, timedelta
import os
import sys
import markdown

class MarkdownEditor(QTextEdit):
    """文本编辑器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)  # 只接受纯文本
        
        # 设置字体
        font = self.font()
        font.setFamily("Consolas")  # 使用等宽字体
        font.setPointSize(11)
        self.setFont(font)
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 获取当前行的文本
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # 获取缩进
            indent = ''
            for char in text:
                if char in ' \t':
                    indent += char
                else:
                    break
            
            # 普通回车
            super().keyPressEvent(event)
            # 保持缩进
            if indent:
                self.insertPlainText(indent)
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self, note_manager: NoteManager):
        super().__init__()
        self.note_manager = note_manager
        self.config_manager = note_manager.config_manager
        self.current_note = None  # 添加当前便签的引用
        
        # 从配置加载颜色
        self.colors = {
            "editor_bg": QColor(self.config_manager.get("colors.editor_bg", "#ffffff")),
            "editor_text": QColor(self.config_manager.get("colors.editor_text", "#2c3e50")),
            "title_bg": QColor(self.config_manager.get("colors.title_bg", "#ffffff")),
            "title_text": QColor(self.config_manager.get("colors.title_text", "#2c3e50")),
            "toolbar_bg": QColor(self.config_manager.get("colors.toolbar_bg", "#ffffff"))
        }
        
        # 添加菜单样式
        self.menu_style = """
            QMenu {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 3px;
                padding: 5px;
            }
            QMenu::item {
                color: #ecf0f1;
                padding: 8px 25px;
                margin: 2px 5px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #34495e;
            }
            QMenu::separator {
                height: 1px;
                background-color: #34495e;
                margin: 5px 0;
            }
        """
        
        self.setup_ui()
        self.apply_colors()
        self.apply_fonts()  # 应用字体设置
        
        # 设置当前日期并加载便签
        current_date = datetime.now().date()
        self.set_working_date(current_date)
        
        # 如果当前日期没有便签，创建一个新便签
        if not self.note_manager.notes:
            self.create_note()
        else:
            # 加载第一个便签
            first_note = next(iter(self.note_manager.notes.values()))
            self.current_note = first_note
            self.update_ui()
        
        # 添加日期更新定时器
        self.date_timer = QTimer(self)
        self.date_timer.timeout.connect(self.update_date_button)
        self.date_timer.start(60000)  # 每分钟更新一次
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(u"便签")
        self.setMinimumSize(600, 400)
        
        # 设置应用程序图标和任务栏图标
        app_icon = QIcon("resources/icons/app.png")
        self.setWindowIcon(app_icon)
        # 设置任务栏图标
        if hasattr(self, 'setTaskbarIcon'):  # Windows 特有
            self.setTaskbarIcon(app_icon)
        
        # 同时设置应用程序级别的图标
        QApplication.instance().setWindowIcon(app_icon)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 顶部工具栏区域
        toolbar_layout = QHBoxLayout()
        
        # 标题区域（包含日期、标题编辑框和列表按钮）
        title_container = QHBoxLayout()
        
        # 日期区域（包含按钮和状态图标）
        date_container = QHBoxLayout()
        
        # 上一天按钮
        self.prev_date_button = QPushButton()
        self.prev_date_button.setIcon(QIcon("resources/icons/prev.png"))
        self.prev_date_button.setFixedSize(24, 24)
        self.prev_date_button.clicked.connect(self.goto_prev_date)
        self.prev_date_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(44, 62, 80, 0.1);
            }
        """)
        date_container.addWidget(self.prev_date_button)
        
        # 日期按钮
        self.date_button = QPushButton()
        self.date_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 3px 8px;
                color: #2c3e50;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(44, 62, 80, 0.1);
                border-radius: 3px;
            }
        """)
        self.date_button.clicked.connect(self.show_calendar)
        date_container.addWidget(self.date_button)
        
        # 下一天按钮
        self.next_date_button = QPushButton()
        self.next_date_button.setIcon(QIcon("resources/icons/next.png"))
        self.next_date_button.setFixedSize(24, 24)
        self.next_date_button.clicked.connect(self.goto_next_date)
        self.next_date_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(44, 62, 80, 0.1);
            }
        """)
        date_container.addWidget(self.next_date_button)
        
        # 日期状态图标
        self.date_status = QLabel()
        self.date_status.setFixedSize(16, 16)
        date_container.addWidget(self.date_status)
        
        title_container.addLayout(date_container)
        
        # 添加一个小分隔
        title_container.addSpacing(5)
        
        # 标题编辑框
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(u"便签标题")
        self.title_edit.setMaximumWidth(200)
        self.title_edit.textChanged.connect(self.on_title_changed)
        title_container.addWidget(self.title_edit)
        
        # 列表按钮
        self.list_button = QPushButton()
        self.list_button.setIcon(QIcon("resources/icons/list.png"))
        self.list_button.setToolTipDuration(2000)
        self.list_button.setToolTip("显示所有便签")
        self.list_button.setFixedSize(24, 24)
        self.list_button.clicked.connect(self.show_notes_list)
        title_container.addWidget(self.list_button)
        
        # 添加弹簧，使标题区域靠左
        title_container.addStretch()
        
        # 将标题区域添加到工具栏
        toolbar_layout.addLayout(title_container)
        
        # 添加弹簧，使右侧按钮右
        toolbar_layout.addStretch()
        
        # 右侧按钮容器
        right_buttons = QHBoxLayout()
        right_buttons.setSpacing(8)  # 设置按钮之间的间距
        right_buttons.setContentsMargins(0, 0, 0, 0)  # 移除容器边距
        
        # 新建按钮
        self.new_button = QPushButton()
        self.new_button.setIcon(QIcon("resources/icons/new.png"))
        self.new_button.setToolTipDuration(2000)
        self.new_button.setToolTip(u"新建便签")
        self.new_button.setFixedSize(24, 24)
        self.new_button.clicked.connect(self.create_note)
        right_buttons.addWidget(self.new_button)
        
        # 删除按钮
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_button.setToolTipDuration(2000)
        self.delete_button.setToolTip("删除便签")
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.clicked.connect(self.delete_note)
        right_buttons.addWidget(self.delete_button)
        
        # 设置按钮
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("resources/icons/settings.png"))
        # 使用 setToolTipDuration 设置提示显示时间
        self.settings_button.setToolTipDuration(2000)  # 2秒
        # 设置样式，包括工具提示的样式
        self.settings_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-family: "Microsoft YaHei", "微软雅黑";
            }
        """)
        self.settings_button.setToolTip("设置")
        self.settings_button.setFixedSize(24, 24)
        self.settings_button.clicked.connect(self.show_settings)
        right_buttons.addWidget(self.settings_button)
        
        # 添加右侧按钮容器到工具栏
        toolbar_layout.addLayout(right_buttons)
        
        # 添加分隔
        toolbar_layout.addSpacing(10)
        
        # 添加工具栏到主布局
        layout.addLayout(toolbar_layout)
        
        # 编辑区域
        edit_container = QWidget()
        edit_layout = QVBoxLayout(edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        
        # 编辑器
        self.note_edit = MarkdownEditor()
        self.note_edit.textChanged.connect(self.on_text_changed)
        edit_layout.addWidget(self.note_edit)
        
        # 添加到主布局
        layout.addWidget(edit_container)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                border: none;
                padding: 3px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        self.new_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        self.list_button.setStyleSheet(button_style)
        self.settings_button.setStyleSheet(button_style)
        
        # 设置标题编辑框样式
        self.title_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 3px;
                padding: 3px;
                background-color: transparent;
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit:hover {
                background-color: rgba(44, 62, 80, 0.1);
            }
            QLineEdit:focus {
                background-color: white;
                border: 1px solid #3498db;
            }
        """)
        
        # 设置全局工具提示样式
        self.setStyleSheet("""
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-family: "Microsoft YaHei", "微软雅黑";
            }
        """)
    
    def get_current_color(self, color_type: str) -> QColor:
        """获取当前颜色"""
        return self.colors.get(color_type, QColor("#ffffff"))
    
    def change_color(self, color_type: str, color: QColor):
        """改变指定区域的颜色"""
        # 保存新的颜色
        self.colors[color_type] = color
        # 确保调用 set 方法并检查返回值
        if not self.config_manager.set(f"colors.{color_type}", color.name()):
            QMessageBox.warning(self, "错误", "保存颜色设置失败")
        
        # 应用颜色
        self.apply_colors()
    
    def apply_colors(self):
        """应用所有颜色设置"""
        # 获取颜色
        toolbar_bg = self.colors['toolbar_bg']  # 统一的背景色
        editor_bg = self.colors['editor_bg']
        editor_text = self.colors['editor_text']
        title_text = self.colors['title_text']
        
        # 编辑区
        self.note_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {editor_bg.name()};
                color: {editor_text.name()};
                border: none;
                border-radius: 3px;
            }}
        """)
        
        # 标题
        self.title_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {toolbar_bg.name()};
                color: {title_text.name()};
                border: none;
                border-radius: 3px;
                padding: 3px;
            }}
            QLineEdit:hover {{
                background-color: {toolbar_bg.lighter(110).name()};
            }}
            QLineEdit:focus {{
                border: 1px solid #3498db;
            }}
        """)
        
        # 工具栏背景和按钮
        self.centralWidget().setStyleSheet(f"""
            QWidget {{
                background-color: {toolbar_bg.name()};
            }}
            QPushButton {{
                color: {title_text.name()};
            }}
        """)
        
        # 更新所有打开的对话框
        for child in self.findChildren(QDialog):
            if hasattr(child, 'apply_styles'):
                child.apply_styles()
    
    def create_note(self):
        """创建新便签"""
        note = self.note_manager.create_note(u"新建便签")
        self.current_note = note
        self.title_edit.setText(note['title'])
        self.note_edit.clear()
    
    def delete_note(self):
        """删除当前便签"""
        if not self.current_note:
            return
        
        reply = QMessageBox.question(
            self,
            u"确认删除",
            u"确定要删除这个便签吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 获取便签 ID
            note_id = self.current_note.get('id')
            if not note_id:
                QMessageBox.warning(self, "错误", "无的便签ID")
                return
            
            # 删除便签
            if self.note_manager.delete_note(note_id):
                # 重新加载当前日期的便签
                self.note_manager._load_notes()
                notes = self.note_manager.notes
                
                if notes:
                    # 如果有他便签，显示第一个
                    self.current_note = next(iter(notes.values()))
                    self.update_ui()
                else:
                    # 如果没有便签了，创建新便签
                    self.create_note()
            else:
                QMessageBox.warning(self, "错误", "删除便签失败")
    
    def show_notes_list(self):
        """显示当前日期的便签列表"""
        # 创建便签列表对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{self.note_manager.working_date.strftime('%Y-%m-%d')} 的便签")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 便签列表
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: #2c3e50;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                background-color: white;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # 获取当前日期的便签
        notes = self.note_manager.notes
        
        # 添加便签到列表
        for note_id, note in notes.items():
            item = QListWidgetItem(note.get('title', '无标题'))
            item.setData(Qt.ItemDataRole.UserRole, note)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 打开按钮
        open_button = QPushButton("打开")
        def open_selected_note():
            if list_widget.currentItem():
                note = list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
                self.current_note = note
                self.update_ui()
                dialog.accept()
        open_button.clicked.connect(open_selected_note)
        button_layout.addWidget(open_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 双击打开便签
        list_widget.itemDoubleClicked.connect(lambda item: open_selected_note())
        
        # 默认选中第一项
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)
        
        dialog.exec()
    
    def show_calendar(self):
        """显示日历对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("选择日期")
        dialog.setFixedSize(400, 350)  # 调整大小以适应更多内容
        
        layout = QVBoxLayout(dialog)
        
        # 日历控件
        calendar = QCalendarWidget()
        # 移除最小日期限制，允许查看历史便签
        # calendar.setMinimumDate(datetime.now().date())
        
        # 添加日期提示标签
        date_label = QLabel()
        date_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 5px;
            }
        """)
        
        def update_date_info(date):
            """更新日期信息"""
            selected_date = date.toPyDate()
            current_date = datetime.now().date()
            
            if selected_date > current_date:
                date_label.setText("未来日期 - 可以创建新便签")
                date_label.setStyleSheet("QLabel { color: #27ae60; }")  # 绿色
            elif selected_date < current_date:
                date_label.setText("历史日期 - 仅可查看")
                date_label.setStyleSheet("QLabel { color: #e74c3c; }")  # 红色
            else:
                date_label.setText("当前日期")
                date_label.setStyleSheet("QLabel { color: #2980b9; }")  # 蓝色
        
        # 连接日期变化信号
        calendar.selectionChanged.connect(lambda: update_date_info(calendar.selectedDate()))
        
        # 初始化日期信息
        update_date_info(calendar.selectedDate())
        
        layout.addWidget(calendar)
        layout.addWidget(date_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 打开按钮
        open_button = QPushButton("打开")
        def open_selected_date():
            selected_date = calendar.selectedDate().toPyDate()
            current_date = datetime.now().date()
            
            if selected_date <= current_date:
                # 过去或当前日期：直接打开
                self.open_notes_file(calendar.selectedDate())
                dialog.accept()
            else:
                # 未来日期：询问是否创建新便签
                reply = QMessageBox.question(
                    dialog,
                    "创建便签",
                    f"是否在 {selected_date.strftime('%Y-%m-%d')} 创建新便签？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_notes_file(calendar.selectedDate())
                    dialog.accept()
        
        open_button.clicked.connect(open_selected_date)
        button_layout.addWidget(open_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 双击日期时自动打开
        calendar.activated.connect(lambda: open_selected_date())
        
        dialog.exec()
    
    def set_working_date(self, date_obj):
        """设置工作日期并更新显示"""
        self.note_manager.set_working_date(date_obj)
        # 更新日期按钮显示为工作日期
        self.date_button.setText(date_obj.strftime("%Y-%m-%d"))
        # 更新状态图标
        self.update_date_status()
    
    def open_notes_file(self, date):
        """打开指定日期的便签文件"""
        date_obj = date.toPyDate()
        current_date = datetime.now().date()
        
        # 设置工作日期并更新显示
        self.set_working_date(date_obj)
        
        # 如果是历史日期，设置编辑器为只读
        is_history = date_obj < current_date
        self.note_edit.setReadOnly(is_history)
        self.title_edit.setReadOnly(is_history)
        
        # 加载便签
        self.note_manager._load_notes()  # 重新加载当前工作日期的便签
        notes = self.note_manager.notes
        
        if not notes:
            if date_obj > current_date:
                # 未来日期：创建新便签
                self.create_note()  # 使用统一的创建便签方法
            else:
                # 历史日期：显示提示
                QMessageBox.information(
                    self,
                    "提示",
                    f"{date_obj.strftime('%Y-%m-%d')} 没有便签记录"
                )
                return
        else:
            # 如果有多个便签，显示列表让用户选择
            if len(notes) > 1:
                self.show_notes_list()
            else:
                # 只有一个便签时直接显示
                note = next(iter(notes.values()))
                self.current_note = note
                self.update_ui()
    
    def load_notes_for_date(self, date):
        """加载指定日期的便签"""
        notes = self.note_manager.get_daily_notes(date.toPyDate())
        if notes:
            # 示该日期便签列表
            menu = QMenu(self)
            menu.setStyleSheet(self.menu_style)
            
            for note in sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True):
                action = menu.addAction(note.get('title', '无标题'))
                action.triggered.connect(lambda checked, n=note: self.switch_to_note(n))
            
            # 在列表按钮位置示菜单
            button_pos = self.list_button.mapToGlobal(QPoint(0, self.list_button.height()))
            menu.exec(button_pos)
        else:
            QMessageBox.information(self, "提示", f"{date.toString('yyyy-MM-dd')} 没有便签记录")
    
    def switch_to_note(self, note):
        """切换到指定便签"""
        if note and 'id' in note:
            self.current_note = note
            self.update_ui()
    
    def update_ui(self):
        """更新界面显示"""
        if self.current_note and 'id' in self.current_note:
            # 暂时断开信号连接，避免触发更新
            self.title_edit.blockSignals(True)
            self.note_edit.blockSignals(True)
            
            try:
                # 更新标题
                self.title_edit.setText(self.current_note.get('title', ''))
                
                # 更新内容
                content = self.current_note.get('content', '')
                self.note_edit.setPlainText(content)
                
                # 将光标移到开始位置
                cursor = self.note_edit.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)  # 使用正确的枚举值
                self.note_edit.setTextCursor(cursor)
            finally:
                # 恢复信号连接
                self.title_edit.blockSignals(False)
                self.note_edit.blockSignals(False)
    
    def on_title_changed(self, text):
        """当标题改变时"""
        if self.current_note and 'id' in self.current_note:
            self.note_manager.update_note(self.current_note['id'], title=text)
    
    def on_text_changed(self):
        """当内容改变时"""
        if self.current_note and 'id' in self.current_note:
            content = self.note_edit.toPlainText()  # 使用 toPlainText
            self.note_manager.update_note(
                self.current_note['id'],
                content=content
            )
    
    def show_settings(self):
        """显示设置窗口"""
        from .settings_window import SettingsWindow
        dialog = SettingsWindow(self.config_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 应用设置
            self.apply_colors()
            self.apply_fonts()
    
    def update_date_button(self):
        """更新日期按钮显示"""
        current_date = datetime.now()
        
        # 检查日期变化
        if self.note_manager.check_date_change():
            # 如果日期已变化，更新显示并创建新便签
            self.date_button.setText(current_date.strftime("%Y-%m-%d"))
            if not self.note_manager.get_daily_notes():
                self.create_note()
    
    def update_date_status(self):
        """更新日期状态图标"""
        current_date = datetime.now().date()
        if self.note_manager.working_date == current_date:
            # 当前日期显示绿色圆圈
            self.date_status.setPixmap(QPixmap("resources/icons/current_date.png"))
            self.date_status.setToolTip(u"当前日期")
            self.date_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 3px 8px;
                    color: #2c3e50;
                    font-size: 14px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(44, 62, 80, 0.1);
                    border-radius: 3px;
                }
            """)
        else:
            # 非当前日期显示红色三角形
            self.date_status.setPixmap(QPixmap("resources/icons/other_date.png"))
            # 根据日期是过去还是未来显示不同提示
            if self.note_manager.working_date > current_date:
                self.date_status.setToolTip(u"未来日期")
            else:
                self.date_status.setToolTip(u"历史日期")
            # 日期文字也变成红色
            self.date_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 3px 8px;
                    color: #e74c3c;  /* 红色文字 */
                    font-size: 14px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(231, 76, 60, 0.1);  /* 红悬停效 */
                    border-radius: 3px;
                }
            """)
    
    def apply_fonts(self):
        """应用字体设置"""
        # 编辑区字体
        editor_font = QFont(
            self.config_manager.get("fonts.editor_family", "Consolas"),
            self.config_manager.get("fonts.editor_size", 11)
        )
        self.note_edit.setFont(editor_font)
        
        # 标题字体
        title_font = QFont(
            self.config_manager.get("fonts.title_family", "Arial"),
            self.config_manager.get("fonts.title_size", 14)
        )
        self.title_edit.setFont(title_font)
    
    def goto_prev_date(self):
        """切换到前一天"""
        current_date = self.note_manager.working_date
        prev_date = current_date - timedelta(days=1)
        self.open_notes_file(QDate(prev_date.year, prev_date.month, prev_date.day))
    
    def goto_next_date(self):
        """切换到后一天"""
        current_date = self.note_manager.working_date
        next_date = current_date + timedelta(days=1)
        self.open_notes_file(QDate(next_date.year, next_date.month, next_date.day))