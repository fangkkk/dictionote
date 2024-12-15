import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.main.init import init_project
from src.main.note_manager import NoteManager
from src.ui.main_window import MainWindow

def setup_environment():
    """设置运行环境"""
    # 获取脚本所在目录作为项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 添加项目根目录到 Python 路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 确保目录存在
    os.makedirs("data/notes", exist_ok=True)
    os.makedirs("resources/icons", exist_ok=True)

def main():
    try:
        setup_environment()
        
        # 创建应用实例
        app = QApplication([])
        
        # 设置应用程序图标
        app_icon = QIcon("resources/icons/app.png")
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
        else:
            print("警告: 无法加载应用程序图标")
        
        # 生成图标
        try:
            from src.utils.icon_generator import generate_icons
            generate_icons()
        except Exception as e:
            print(f"警告: 图标生成失败 - {e}")
        
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