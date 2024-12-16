# -*- coding: utf-8 -*-
import PyInstaller.__main__
import os
import shutil
from datetime import datetime
from PIL import Image
import sys
import codecs
import locale

def print_utf8(message, is_error=False):
    """统一处理输出的辅助函数"""
    try:
        # 尝试直接打印
        if is_error:
            print(message, file=sys.stderr)
        else:
            print(message)
        sys.stdout.flush()
    except UnicodeEncodeError:
        # 如果失败，使用 buffer.write
        message = f"{message}\n".encode('utf-8')
        if is_error:
            sys.stderr.buffer.write(message)
        else:
            sys.stdout.buffer.write(message)
        sys.stdout.buffer.flush()

def setup_encoding():
    """设置环境编码"""
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 设置标准输出编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    
    # 设置区域
    try:
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass

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
        print_utf8(f"转换图标失败: {e}", is_error=True)
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

def copy_resources():
    """复制资源文件"""
    try:
        # 复制 README
        if os.path.exists('README.md'):
            shutil.copy('README.md', 'dist/README.md')
        
        # 复制图标
        icons_src = 'resources/icons'
        icons_dst = 'dist/resources/icons'
        if os.path.exists(icons_src):
            for icon in os.listdir(icons_src):
                if icon.endswith('.png'):
                    shutil.copy(
                        os.path.join(icons_src, icon),
                        os.path.join(icons_dst, icon)
                    )
        
        # 复制字典文件
        dict_src = 'dict'
        dict_dst = 'dist/dict'
        if os.path.exists(dict_src):
            if not os.path.exists(dict_dst):
                os.makedirs(dict_dst)
            for file in os.listdir(dict_src):
                if file.endswith('.mdx'):
                    shutil.copy(
                        os.path.join(dict_src, file),
                        os.path.join(dict_dst, file)
                    )
        
        # 复制配置文件（如果存在）
        config_src = 'data/config'
        config_dst = 'dist/data/config'
        if os.path.exists(config_src):
            for file in os.listdir(config_src):
                if file.endswith('.json'):
                    shutil.copy(
                        os.path.join(config_src, file),
                        os.path.join(config_dst, file)
                    )
        
        print_utf8("资源文件复制完成")
    except Exception as e:
        print_utf8(f"复制资源文件时出错: {e}", is_error=True)

def create_directories():
    """创建必要的目录"""
    dirs = [
        'dist/data/notes',
        'dist/data/config',
        'dist/resources/icons',
        'dist/dict'  # 添加字典目录
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def create_version_file():
    """创建版本信息文件"""
    version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 1, 0),
    prodvers=(1, 0, 1, 0),
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
           StringStruct('FileVersion', '1.0.1'),
           StringStruct('InternalName', 'DictiNote'),
           StringStruct('LegalCopyright', 'Copyright (C) {datetime.now().year}'),
           StringStruct('OriginalFilename', 'DictiNote.exe'),
           StringStruct('ProductName', 'DictiNote'),
           StringStruct('ProductVersion', '1.0.1')])
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
    try:
        # 设置编码环境
        setup_encoding()
        
        # 清理旧的构建文件
        clean_build()
        
        # 创建版本文件
        create_version_file()
        
        # 转换图标
        png_icon = "resources/icons/app.png"
        ico_icon = "app.ico"
        if not convert_png_to_ico(png_icon, ico_icon):
            print_utf8("警告: 图标转换失败，将使用默认图标")
            ico_icon = None
        
        # PyInstaller 配置
        PyInstaller.__main__.run([
            'run.py',                    # 主程序
            '--name=DictiNote',          # 程序名
            '--windowed',                # 无控制台窗口
            '--onefile',                 # 打包成单个文件
            f'--icon={ico_icon}' if ico_icon else '',  # 程序图标
            '--add-data=resources/icons/*.png;resources/icons',  # 添加图标文件
            '--add-data=dict/*.mdx;dict',  # 添加字典文件
            '--noconsole',               # 禁用控制台输出
            '--clean',                   # 清理临时文件
            '--version-file=version.txt',  # 版本信息文件
            '--collect-all=markdown',    # 确保 markdown 模块完整打包
            '--collect-all=PIL',         # 确保 PIL 模块完整打包
        ])
        
        # 创建目录并复制资源
        create_directories()
        copy_resources()
        
        # 创建发布包
        version = datetime.now().strftime("%Y%m%d")
        archive_name = f'DictiNote_v{version}'
        shutil.make_archive(archive_name, 'zip', 'dist')
        
        print_utf8(f"构建完成: {archive_name}.zip")
        
        # 清理临时文件
        for file in ['version.txt', 'app.ico']:
            if os.path.exists(file):
                os.remove(file)
    except Exception as e:
        print_utf8(f"构建过程中出现错误: {str(e)}", is_error=True)
        raise

if __name__ == '__main__':
    build_app() 