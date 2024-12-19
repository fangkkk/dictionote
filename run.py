# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from PyQt6.QtWidgets import QApplication
from src.main.init import init_project
from src.main.note_manager import NoteManager
from src.ui.main_window import MainWindow

def setup_environment():
    """设置运行环境"""
    # 确保必要目录存在
    os.makedirs("data/notes", exist_ok=True)
    os.makedirs("resources/icons", exist_ok=True)

def main():
    try:
        setup_environment()
        
        # 创建应用实例
        app = QApplication(sys.argv)
        
        # 初始化应用
        config_manager = init_project()
        note_manager = NoteManager(config_manager)
        window = MainWindow(note_manager)
        window.show()
        
        return app.exec()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 