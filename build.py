import PyInstaller.__main__
import os
import shutil
from datetime import datetime
from PIL import Image
import sys
import codecs

if sys.platform.startswith('win'):
    # 设置控制台输出编码为 utf-8
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

def convert_png_to_ico(png_path, ico_path):
    """将 PNG 转换为 ICO"""
    try:
        # 打开 PNG 图像
        img = Image.open(png_path)
        
        # 确保图像是 RGBA 模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建多个尺寸的图标
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        icons = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # 保存为 ICO
        icons[0].save(ico_path, format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
        return True
    except Exception as e:
        print(f"转换图标失败: {e}")
        return False

def clean_build():
    """清理构建目录"""
    for path in ['dist', 'build']:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # 删除 spec 文件和临时文件
    for file in os.listdir('.'):
        if file.endswith(('.spec', '.ico')):
            os.remove(file)

def create_directories():
    """创建必要的目录"""
    dirs = [
        'dist/data/notes',
        'dist/data/config',
        'dist/resources/icons'
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def copy_resources():
    """复制资源文件"""
    if os.path.exists('README.md'):
        shutil.copy('README.md', 'dist/README.md')

def create_version_file():
    """创建版本信息文件"""
    version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [StringStruct('CompanyName', 'Your Company'),
           StringStruct('FileDescription', 'DictiNote - Simple Note Taking App'),
           StringStruct('FileVersion', '1.0.0'),
           StringStruct('InternalName', 'DictiNote'),
           StringStruct('LegalCopyright', 'Copyright (C) {datetime.now().year}'),
           StringStruct('OriginalFilename', 'DictiNote.exe'),
           StringStruct('ProductName', 'DictiNote'),
           StringStruct('ProductVersion', '1.0.0')])
      ]
    ),
    VarFileInfo([VarStruct('Translation', [0x409, 1200])])
  ]
)
"""
    
    # 创建版本文件
    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)

def build_app():
    """构建应用程序"""
    # 清理旧���构建文件
    clean_build()
    
    # 创建版本文件
    create_version_file()
    
    # 转换图标
    png_icon = "resources/icons/app.png"
    ico_icon = "app.ico"
    if not convert_png_to_ico(png_icon, ico_icon):
        print("警告: 图标转换失败，将使用默认图标")
        ico_icon = None
    
    # PyInstaller 配置
    PyInstaller.__main__.run([
        'run.py',                    # 主程序
        '--name=DictiNote',          # 程序名
        '--windowed',                # 无控制台窗口
        '--onefile',                 # 打包成单个文件
        f'--icon={ico_icon}' if ico_icon else '',  # 程序图标
        '--add-data=resources/icons/*.png;resources/icons',  # 添加图标文件
        '--noconsole',               # 禁用控制台输出
        '--clean',                   # 清理临时文件
        '--version-file=version.txt'  # 版本信息文件
    ])
    
    # 创建目录并复制资源
    create_directories()
    copy_resources()
    
    # 创建发布包
    version = datetime.now().strftime("%Y%m%d")
    archive_name = f'DictiNote_v{version}'
    shutil.make_archive(archive_name, 'zip', 'dist')
    print(f"构建完成: {archive_name}.zip")
    
    # 清理临时文件
    for file in ['version.txt', 'app.ico']:
        if os.path.exists(file):
            os.remove(file)

if __name__ == '__main__':
    build_app() 