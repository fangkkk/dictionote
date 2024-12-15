import json
import os
from typing import List, Dict
from datetime import datetime

class NoteStorage:
    def __init__(self, storage_dir: str = "data/notes"):
        self.storage_dir = storage_dir
        self.storage_file = os.path.join(storage_dir, "notes.json")
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_notes(self, notes: List[Dict]) -> bool:
        """保存便签到文件"""
        try:
            # 添加保存时间
            notes_data = []
            for note in notes:
                note_data = note.copy()
                note_data['updated_at'] = datetime.now().isoformat()
                notes_data.append(note_data)
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存便签失败: {e}")
            return False
    
    def load_notes(self) -> List[Dict]:
        """从文件加载便签"""
        try:
            if not os.path.exists(self.storage_file):
                return []
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载便签失败: {e}")
            return [] 