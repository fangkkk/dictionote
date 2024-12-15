import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.json")
        self.default_config = {
            "storage": {
                "notes_dir": os.path.join("data", "notes"),
                "dict_path": os.path.join("dict", "dictionary.mdx")
            },
            "colors": {
                "editor_bg": "#ffffff",
                "editor_text": "#2c3e50",
                "title_bg": "#ffffff",
                "title_text": "#2c3e50",
                "toolbar_bg": "#ffffff"
            },
            "fonts": {
                "editor_family": "Consolas",
                "editor_size": 11,
                "title_family": "Arial",
                "title_size": 14,
                "preview_family": "Arial",
                "preview_size": 14
            }
        }
        self._ensure_directories()
        self.config = self._load_config()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.config_dir,
            os.path.join("data", "notes"),
            os.path.join("data", "config"),
            os.path.join("dict"),
            os.path.join("resources", "icons")
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            self._save_config(self.default_config)
            return self.default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.config)