from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
import os
import math

def generate_icons():
    """生成并保存图标"""
    icons = {
        'new': generate_new_icon(),
        'delete': generate_delete_icon(),
        'app': generate_app_icon(),
        'list': generate_list_icon(),
        'settings': generate_settings_icon(),
    }
    
    # 确保目录存在
    os.makedirs('resources/icons', exist_ok=True)
    
    # 保存图标
    for name, icon in icons.items():
        save_icon(icon, f'resources/icons/{name}.png')
    
    # 生成日期状态图标
    generate_date_status_icons()

def save_icon(icon: QIcon, path: str):
    """保存图标为PNG文件"""
    size = 32 if 'app.png' in path else 16
    pixmap = icon.pixmap(size, size)
    pixmap.save(path)

def generate_new_icon() -> QIcon:
    """生成新建图标（加号）"""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor("#3498db"), 2))
    
    # 画加号
    painter.drawLine(8, 4, 8, 12)  # 垂直线
    painter.drawLine(4, 8, 12, 8)  # 水平线
    
    painter.end()
    return QIcon(pixmap)

def generate_delete_icon() -> QIcon:
    """生成删除图标（垃圾桶）"""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor("#e74c3c"), 2))
    
    # 画垃圾桶
    painter.drawRect(4, 5, 8, 8)  # 主体
    painter.drawLine(3, 5, 13, 5)  # 上边
    painter.drawLine(7, 3, 9, 3)  # 把手
    
    painter.end()
    return QIcon(pixmap)

def generate_app_icon() -> QIcon:
    """生成应用程序图标（便签）"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 画便签背景
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#f1c40f"))  # 黄色背景
    painter.drawRoundedRect(4, 4, 24, 24, 3, 3)
    
    # 画便签线条
    painter.setPen(QPen(QColor("#e67e22"), 2))  # 橙色线条
    for y in range(12, 24, 4):
        painter.drawLine(8, y, 24, y)
    
    painter.end()
    return QIcon(pixmap)

def generate_tab_icon() -> QIcon:
    """生成标签分布图标（三层圆环）"""
    pixmap = QPixmap(32, 32)  # 使用更大的尺寸以显示更多细节
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 定义三个圆环的半径
    outer_radius = 14
    middle_radius = 10
    inner_radius = 6
    
    # 定义颜色
    colors = {
        'outer': QColor("#3498db"),  # 蓝色
        'middle': QColor("#2ecc71"),  # 绿色
        'inner': QColor("#e74c3c"),  # 红色
    }
    
    center = QPoint(16, 16)
    
    # 画外层圆环（4等分）
    painter.setPen(QPen(colors['outer'], 2))
    for i in range(4):
        start_angle = i * 90 * 16  # Qt使用16分之一度作为单位
        painter.drawArc(
            QRectF(
                center.x() - outer_radius,
                center.y() - outer_radius,
                outer_radius * 2,
                outer_radius * 2
            ),
            start_angle,
            85 * 16  # 留一点间隔
        )
    
    # 画中层圆环（4等分）
    painter.setPen(QPen(colors['middle'], 2))
    for i in range(4):
        start_angle = (i * 90 + 45) * 16  # 错开45度
        painter.drawArc(
            QRectF(
                center.x() - middle_radius,
                center.y() - middle_radius,
                middle_radius * 2,
                middle_radius * 2
            ),
            start_angle,
            85 * 16
        )
    
    # 画内层圆环（2等分）
    painter.setPen(QPen(colors['inner'], 2))
    for i in range(2):
        start_angle = i * 180 * 16
        painter.drawArc(
            QRectF(
                center.x() - inner_radius,
                center.y() - inner_radius,
                inner_radius * 2,
                inner_radius * 2
            ),
            start_angle,
            175 * 16
        )
    
    painter.end()
    return QIcon(pixmap)

def generate_list_icon() -> QIcon:
    """生成列表图标"""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#2980b9"), 2))
    
    # 画三条横线
    y_positions = [4, 8, 12]
    for y in y_positions:
        painter.drawLine(3, y, 13, y)
    
    painter.end()
    return QIcon(pixmap)

def generate_settings_icon() -> QIcon:
    """生成设置图标（齿轮）"""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 设置画笔
    painter.setPen(QPen(QColor("#7f8c8d"), 2))  # 使用灰色
    
    # 画齿轮外圈
    center = QPoint(8, 8)
    outer_radius = 6
    inner_radius = 3
    
    # 画八个齿
    for i in range(8):
        angle = i * 45 * math.pi / 180  # 转换为弧度
        
        # 外部点
        outer_x = center.x() + outer_radius * math.cos(angle)
        outer_y = center.y() + outer_radius * math.sin(angle)
        
        # 内部点
        inner_x = center.x() + inner_radius * math.cos(angle)
        inner_y = center.y() + inner_radius * math.sin(angle)
        
        painter.drawLine(
            int(inner_x), int(inner_y),
            int(outer_x), int(outer_y)
        )
    
    # 画中心圆
    painter.setBrush(QColor("#7f8c8d"))
    painter.drawEllipse(center, 2, 2)
    
    painter.end()
    return QIcon(pixmap)

def generate_date_status_icons():
    """生成日期状态图标（当前日期和其他日期）"""
    # 当前日期图标（绿色圆圈）
    current_pixmap = QPixmap(16, 16)
    current_pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(current_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#2ecc71"))  # 绿色
    painter.drawEllipse(4, 4, 8, 8)
    painter.end()
    
    # 其他日期图标（红色空心三角形）
    other_pixmap = QPixmap(16, 16)
    other_pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(other_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 设置红色画笔
    color = QColor("#e74c3c")
    painter.setPen(QPen(color, 1.5))  # 使用1.5的线宽
    painter.setBrush(Qt.BrushStyle.NoBrush)  # 不填充
    
    # 画更大的三角形
    points = [
        QPoint(8, 2),    # 顶点
        QPoint(14, 13),  # 右下
        QPoint(2, 13)    # 左下
    ]
    painter.drawPolygon(points)
    
    painter.end()
    
    # 保存图标
    current_pixmap.save('resources/icons/current_date.png')
    other_pixmap.save('resources/icons/other_date.png')

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    generate_icons()
    print("图标生成完成")