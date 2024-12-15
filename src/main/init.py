import os
from ..utils.config_manager import ConfigManager

def init_project():
    """初始化项目目录和配置"""
    config_manager = ConfigManager("data/config")
    
    # 确保目录存在
    for directory in ["data/notes", "data/config", "dict", "resources/icons"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    return config_manager 