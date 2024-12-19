import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from PyQt6.QtWidgets import QApplication
from src.ui.idle_screen import IdleScreen

def main():
    app = QApplication(sys.argv)
    window = IdleScreen()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 