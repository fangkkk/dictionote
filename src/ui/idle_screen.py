from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QTime, QDate
from PyQt6.QtGui import QFont, QColor, QPainter, QIcon
import random
from src.utils.mdx_reader import DictionaryManager

class IdleScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标志和属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 获取配置管理器
        if parent and hasattr(parent, 'config_manager'):
            self.config_manager = parent.config_manager
        else:
            from src.utils.config_manager import ConfigManager
            self.config_manager = ConfigManager()
        
        # 初始化字典管理器
        current_dict = self.config_manager.get("dictionary.current", "")
        self.dict_manager = DictionaryManager(current_dict)
        
        self.setup_ui()
        self.setup_timer()
        self.quotes = [
            "记录生活，记录心情",
            "写下此刻的想法",
            "生活因记录而美好",
            "让文字承载记忆",
            "点滴时光，珍贵回忆"
        ]
        
    def setup_ui(self):
        """设置用户界面"""
        # 保存当前显示的内容（如果有的话）
        old_word = None
        old_meaning = None
        if hasattr(self, 'word_label'):
            old_word = self.word_label.text()
        if hasattr(self, 'meaning_label'):
            old_meaning = self.meaning_label.text()
        
        # 清理旧的UI组件
        if hasattr(self, 'content_widget'):
            self.content_widget.deleteLater()
        if hasattr(self, 'restore_btn'):
            self.restore_btn.deleteLater()
        
        # 设置透明背景
        self.setStyleSheet("""
            IdleScreen {
                background-color: transparent;
            }
            QWidget#content_widget {
                background-color: transparent;
            }
        """)
        
        # 创建内容容器
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加恢复按钮
        self.restore_btn = QPushButton(self)
        self.restore_btn.setFixedSize(32, 32)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 10%);
                border-radius: 16px;
            }
        """)
        self.restore_btn.setIcon(QIcon("resources/icons/restore.png"))
        self.restore_btn.clicked.connect(self.restore_main_window)
        self.restore_btn.raise_()
        
        # 根据模式显示不同内容
        mode = self.config_manager.get("appearance.idle_mode", "dictionary")
        
        if mode == "dictionary":
            # 创建词条容器
            word_container = QWidget()
            word_layout = QVBoxLayout(word_container)
            word_layout.setContentsMargins(0, 0, 0, 0)
            word_layout.setSpacing(10)  # 减小词条和释义之间的间距
            
            # 词条显示
            self.word_label = QLabel()
            self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 应用词条字体和颜色设置
            word_family = self.config_manager.get("fonts.word_family")
            word_size = self.config_manager.get("fonts.word_size")
            word_color = self.config_manager.get("colors.word", "#2980b9")
            
            if word_family and word_size:
                self.word_label.setFont(QFont(word_family, word_size, QFont.Weight.Bold))
            else:
                self.word_label.setFont(QFont("宋体", 36, QFont.Weight.Bold))
            
            self.word_label.setStyleSheet(f"""
                QLabel {{
                    color: {word_color};
                    background-color: transparent;
                    padding-bottom: 10px;  /* 增加下边距 */
                }}
            """)
            word_layout.addWidget(self.word_label)
            
            # 添加释义标签
            self.meaning_label = QLabel()
            self.meaning_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.meaning_label.setWordWrap(True)
            
            # 应用释义字体和颜色设置
            meaning_family = self.config_manager.get("fonts.meaning_family")
            meaning_size = self.config_manager.get("fonts.meaning_size")
            meaning_color = self.config_manager.get("colors.meaning", "#7f8c8d")
            
            if meaning_family and meaning_size:
                self.meaning_label.setFont(QFont(meaning_family, meaning_size))
            else:
                self.meaning_label.setFont(QFont("宋体", 16))
            
            self.meaning_label.setStyleSheet(f"""
                QLabel {{
                    color: {meaning_color};
                    background-color: transparent;
                    padding: 20px 40px;
                    line-height: 150%;
                }}
            """)
            word_layout.addWidget(self.meaning_label)
            
            # 设置词条容器占比
            word_layout.setStretch(0, 1)  # 词条占 1
            word_layout.setStretch(1, 3)  # 释义占 3
            
            # 将词条容器添加到主布局
            content_layout.addWidget(word_container)
            content_layout.setStretch(0, 1)
        else:
            # 时钟模式显示
            self.time_label = QLabel()
            self.date_label = QLabel()
            
            for label in [self.time_label, self.date_label]:
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 应用时钟字体和颜色设置
            clock_family = self.config_manager.get("fonts.clock_family", "Arial")
            clock_size = self.config_manager.get("fonts.clock_size", 72)
            clock_color = self.config_manager.get("colors.clock", "#2c3e50")
            
            self.time_label.setFont(QFont(clock_family, clock_size))
            self.time_label.setStyleSheet(f"""
                QLabel {{
                    color: {clock_color};
                    background-color: transparent;
                }}
            """)
            
            # 应用日期字体和颜色设置
            date_family = self.config_manager.get("fonts.date_family", "Arial")
            date_size = self.config_manager.get("fonts.date_size", 24)
            date_color = self.config_manager.get("colors.date", "#34495e")
            
            self.date_label.setFont(QFont(date_family, date_size))
            self.date_label.setStyleSheet(f"""
                QLabel {{
                    color: {date_color};
                    background-color: transparent;
                }}
            """)
            
            content_layout.addWidget(self.time_label)
            content_layout.addWidget(self.date_label)
        
        # 在设置完所有UI后应用字体
        self.apply_fonts()
        
        # 恢复之前显示的内容
        if old_word and hasattr(self, 'word_label'):
            self.word_label.setText(old_word)
        if old_meaning and hasattr(self, 'meaning_label'):
            self.meaning_label.setText(old_meaning)
    
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)  # 每秒更新一次
    
    def update_display(self):
        """更新显示内容"""
        mode = self.config_manager.get("appearance.idle_mode", "dictionary")
        
        # 如果模式改变，重新设置UI
        if not hasattr(self, '_current_mode') or self._current_mode != mode:
            self._current_mode = mode
            self.setup_ui()
            return
        
        if mode == "dictionary":
            if hasattr(self, 'word_label'):
                if not hasattr(self, '_last_word_update'):
                    self._last_word_update = 0
                
                word_interval = self.config_manager.get("appearance.word_interval", 30)
                if self._last_word_update >= word_interval:
                    word, meaning = self.dict_manager.get_random_entry()
                    self.word_label.setText(word)
                    
                    # 处理释义文本
                    meanings = meaning.split('\n')  # 按换行符分割释义
                    formatted_meanings = []
                    
                    for m in meanings:
                        m = m.strip()
                        if m:  # 忽略空行
                            # 如果是数字编号开头，添加额外的缩进
                            if m[0].isdigit():
                                formatted_meanings.append(f"    {m}")
                            else:
                                formatted_meanings.append(m)
                    
                    # 使用HTML格式化文本，添加行间距
                    formatted_text = "<br><br>".join(formatted_meanings)
                    self.meaning_label.setText(formatted_text)
                    
                    self._last_word_update = 0
                
                self._last_word_update += 1
        else:
            if hasattr(self, 'time_label'):
                current_time = QTime.currentTime()
                current_date = QDate.currentDate()
                
                self.time_label.setText(current_time.toString("hh:mm"))
                self.date_label.setText(current_date.toString("yyyy年MM月dd日 dddd"))
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        if self.parent():
            self.setGeometry(self.parent().geometry())
        # 确保按钮在最上层
        self.restore_btn.raise_()
    
    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        # 调整内容容器大小
        self.content_widget.setGeometry(self.rect())
        # 调整恢复按钮位置并确保在最上层
        self.restore_btn.move(self.width() - 40, 8)
        self.restore_btn.raise_()
    
    def restore_main_window(self):
        """恢复主窗口"""
        self.hide()
        if self.parent():
            # 临时禁用待机功能，防止立即重新触发
            if hasattr(self.parent(), 'disable_idle_temporarily'):
                self.parent().disable_idle_temporarily()
            self.parent().show()
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        # 不再处理鼠标点击事件，改用按钮控制
        pass
    
    def apply_fonts(self):
        """应用字体设置"""
        try:
            if hasattr(self, 'word_label') and self.word_label.parent() is not None:
                # 应用词条字体
                word_family = self.config_manager.get("fonts.word_family", "Arial")
                word_size = self.config_manager.get("fonts.word_size", 36)
                self.word_label.setFont(QFont(word_family, word_size, QFont.Weight.Bold))
            
            if hasattr(self, 'meaning_label') and self.meaning_label.parent() is not None:
                # 应用释义字体
                meaning_family = self.config_manager.get("fonts.meaning_family", "Arial")
                meaning_size = self.config_manager.get("fonts.meaning_size", 16)
                self.meaning_label.setFont(QFont(meaning_family, meaning_size))
            
            if hasattr(self, 'time_label') and self.time_label.parent() is not None:
                # 应用时钟字体
                clock_family = self.config_manager.get("fonts.clock_family", "Arial")
                clock_size = self.config_manager.get("fonts.clock_size", 72)
                self.time_label.setFont(QFont(clock_family, clock_size))
        except (RuntimeError, AttributeError):
            # 如果对象已被删除或发生其他错误，忽略它
            pass
    
    def closeEvent(self, event):
        """关闭事件处理"""
        self.timer.stop()  # 停止更新定时器
        event.accept()