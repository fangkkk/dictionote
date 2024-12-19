import os
import random
from readmdict import MDX
import re

class DictionaryManager:
    def __init__(self, current_dict: str = "", dict_dir: str = "dict"):
        self.dict_dir = dict_dir
        self.current_dict = current_dict
        self.dictionaries = {}
        self.entries = []
        self.load_dictionaries()
    
    def load_dictionaries(self):
        """加载字典文件"""
        try:
            # 确保目录存在
            if not os.path.exists(self.dict_dir):
                os.makedirs(self.dict_dir)
                return
            
            # 加载指定的字典文件或所有字典文件
            files_to_load = []
            if self.current_dict and os.path.exists(os.path.join(self.dict_dir, self.current_dict)):
                files_to_load.append(self.current_dict)
            else:
                files_to_load = [f for f in os.listdir(self.dict_dir) if f.endswith('.mdx')]
            
            # 加载字典
            for file in files_to_load:
                try:
                    dict_path = os.path.join(self.dict_dir, file)
                    mdx = MDX(dict_path)
                    # 获取所有词条和释义
                    items = list(mdx.items())
                    # 构建词条字典
                    for word, meaning in items:
                        try:
                            word = word.decode('utf-8').strip()
                            if word:  # 只添加非空词条
                                self.entries.append(word)
                                self.dictionaries[word] = meaning.decode('utf-8')
                        except Exception as e:
                            print(f"处理词条失败: {e}")
                            continue
                except Exception as e:
                    print(f"加载字典文件 {file} 失败: {e}")
                    continue
        except Exception as e:
            print(f"加载字典文件失败: {e}")
    
    def reload_dictionary(self, dict_name: str):
        """重新加载指定的字典"""
        self.current_dict = dict_name
        self.dictionaries.clear()
        self.entries.clear()
        self.load_dictionaries()
    
    def get_random_entry(self):
        """获取随机词条及其释义"""
        if not self.entries:
            return "No dictionary loaded", "Please add .mdx files to the dict folder"
        
        try:
            # 随机选择一个词条
            word = random.choice(self.entries)
            meaning = self.get_meaning(word)
            return word, meaning
        except Exception as e:
            print(f"获取随机词条失败: {e}")
            return "Error", "Failed to get random entry"
    
    def get_meaning(self, word: str) -> str:
        """获取词条释义"""
        try:
            if word in self.dictionaries:
                meaning = self.dictionaries[word]
                
                # 清理HTML标签
                meaning = re.sub(r'<[^>]+>', '', meaning)
                
                # 清理音标
                meaning = re.sub(r'/[^/]+/', '', meaning)
                
                # 替换特定标记为更清晰的格式
                meaning = re.sub(r'■', '▪ ', meaning)  # 将实心方块替换为项目符号
                meaning = re.sub(r'●', '• ', meaning)  # 将实心圆替换为项目符号
                meaning = re.sub(r'\d+\.\s*', '\n\\g<0>', meaning)  # 数字编号前添加换行
                meaning = re.sub(r'\s*\n\s*', '\n', meaning)  # 规范化换行
                meaning = re.sub(r'\n+', '\n', meaning)  # 删除多余换行
                
                # 处理词性标记，使其更醒目
                meaning = re.sub(r'\[(.*?)\]', r'\n[\1] ', meaning)  # 方括号内容单独成行
                
                # 处理例句，使其缩进显示
                meaning = re.sub(r'例：', '\n    例：', meaning)
                meaning = re.sub(r'例句：', '\n    例句：', meaning)
                
                # 清理多余的空白字符（保留换行）
                meaning = re.sub(r'[ \t]+', ' ', meaning)
                
                # 清理开头和结尾的空白
                meaning = meaning.strip()
                
                return meaning
            return "未找到释义"
        except Exception as e:
            print(f"获取词条释义失败: {e}")
            return "Error getting meaning" 