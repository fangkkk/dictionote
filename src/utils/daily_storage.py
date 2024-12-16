import os
import json
from datetime import datetime, date
from typing import Dict, List, Optional

class DailyStorage:
    def __init__(self, storage_dir: str = "data/notes"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def get_daily_file(self, date_obj: date) -> str:
        """获取指定日期的文件路径"""
        filename = f"{date_obj.year}_{date_obj.month:02d}_{date_obj.day:02d}.json"
        return os.path.join(self.storage_dir, filename)
    
    def save_notes(self, notes: Dict[str, dict], working_date: date = None) -> bool:
        """保存便签到指定日期的文件"""
        try:
            if working_date is None:
                working_date = date.today()
            
            file_path = self.get_daily_file(working_date)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存便签失败: {e}")
            return False
    
    def load_notes(self) -> Dict[str, dict]:
        """加载所有便签"""
        all_notes = {}
        
        try:
            # 遍历目录下的所有 json 文件
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.storage_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        day_notes = json.load(f)
                        all_notes.update(day_notes)
            
            return all_notes
        except Exception as e:
            print(f"加载便签失败: {e}")
            return {}
    
    def get_daily_notes(self, date: datetime = None) -> Dict[str, dict]:
        """获取指定日期的便签"""
        if date is None:
            date = datetime.now()
            
        file_path = self.get_daily_file(date)
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载便签失败: {e}")
            return {}
    
    def create_future_note(self, future_date: date, note: dict) -> bool:
        """创建未来日期的便签"""
        if future_date < date.today():
            return False
        
        file_path = self.get_daily_file(future_date)
        notes = {}
        
        # 如果文件已存在，先读取现有内容
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    notes = json.load(f)
            except Exception:
                pass
        
        # 如果是新文件，直接使用传入的便签作为第一个便签
        if not notes:
            notes["1"] = note
        else:
            # 如果文件已存在，添加新便签
            note_id = str(len(notes) + 1)
            while note_id in notes:
                note_id = str(int(note_id) + 1)
            notes[note_id] = note
        
        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"创建未来便签失败: {e}")
            return False 
    
    def get_all_notes(self) -> Dict[str, dict]:
        """获取所有便签"""
        all_notes = {}
        
        # 遍历存储目录中的所有 json 文件
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    # 从文件名获取日期
                    date_str = filename.replace('.json', '').replace('_', '-')
                    
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        notes = json.load(f)
                        
                    # 为每个便签添加日期信息
                    for note_id, note in notes.items():
                        note['date'] = date_str
                        note['id'] = note_id
                        all_notes[f"{date_str}_{note_id}"] = note
                        
                except Exception as e:
                    print(f"读取文件 {filename} 时出错: {e}")
                    continue
        
        return all_notes 