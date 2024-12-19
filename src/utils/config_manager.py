import os
import json
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_dir: str = "data/config"):
        """
        配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "settings.json")
        
        # 默认配置
        self.default_config = {
            "storage": {
                "notes_dir": "data/notes",
                "dict_path": "dict/dictionary.mdx"
            },
            "colors": {
                "editor_bg": "#ffffff",
                "editor_text": "#2c3e50",
                "title_bg": "#ffffff",
                "title_text": "#2c3e50",
                "toolbar_bg": "#ffffff"
            },
            "fonts": {
                # 移除默认字体设置，让应用程序使用系统默认字体
            }
        }
        
        # 初始化配置
        self.config: Dict[str, Any] = self.default_config.copy()
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并加载的配置和默认配置
                    self._merge_configs(self.config, loaded_config)
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def _merge_configs(self, base: dict, update: dict):
        """递归合并配置字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 支持点号分隔的键
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        # 支持点号分隔的键
        keys = key.split('.')
        config = self.config
        
        # 如果值为None，删除该配置项
        if value is None:
            try:
                current = config
                for k in keys[:-1]:
                    current = current[k]
                if keys[-1] in current:
                    del current[keys[-1]]
                return self.save_config()
            except (KeyError, TypeError):
                return False
        
        # 遍历键路径
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置最终值
        config[keys[-1]] = value
        
        # 立即保存配置
        return self.save_config()