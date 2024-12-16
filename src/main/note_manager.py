import json
import os
from datetime import datetime, date
from typing import List, Dict
from ..utils.config_manager import ConfigManager
from ..utils.daily_storage import DailyStorage

class NoteManager:
    def __init__(self, config_manager: ConfigManager):
        """
        便签管理器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.storage = DailyStorage(config_manager.get("storage.notes_dir"))
        self.notes: Dict[str, dict] = {}
        
        # 当前系统日期，用于检测日期变化
        self.current_date = datetime.now().date()
        # 当前工作日期，用于指定操作的日期
        self.working_date = self.current_date
        
        self._load_notes()
    
    def check_date_change(self):
        """检查日期是否变化，如果变化则重新加载便签"""
        now = datetime.now().date()
        if now != self.current_date:
            self.current_date = now
            self.working_date = now  # 重置工作日期为当前日期
            self._load_notes()  # 重新加载当天的便签
            return True
        return False
    
    def set_working_date(self, date: date):
        """设置当前工作日期"""
        self.working_date = date
        self._load_notes()
    
    def _load_notes(self):
        """从存储加载便签"""
        # 加载工作日期的便签
        self.notes = self.storage.get_daily_notes(self.working_date)
    
    def _save_notes(self):
        """保存便签到存储"""
        self.storage.save_notes(self.notes, self.working_date)
    
    def create_note(self, title: str = "", content: str = "") -> dict:
        """创建新便签"""
        if not title:
            title = u"新建便签"
        
        note_id = str(len(self.notes) + 1)
        while note_id in self.notes:
            note_id = str(int(note_id) + 1)
        
        note = {
            'id': note_id,
            'title': title,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'date': self.working_date.strftime('%Y-%m-%d')
        }
        
        self.notes[note_id] = note
        self._save_notes()
        return note
    
    def get_note(self, note_id: str) -> dict:
        """获指定便签"""
        return self.notes.get(note_id)
    
    def update_note(self, note_id: str, title: str = None, content: str = None) -> dict:
        """更新便签"""
        note = self.notes.get(note_id)
        if note:
            if title is not None:
                note['title'] = title
            if content is not None:
                note['content'] = content
            note['updated_at'] = datetime.now().isoformat()
            self._save_notes()
        return note
    
    def delete_note(self, note_id: str) -> bool:
        """删除便签"""
        if note_id in self.notes:
            del self.notes[note_id]
            self._save_notes()
            return True
        return False
    
    def get_all_notes(self) -> List[dict]:
        """获取所有便签"""
        return list(self.notes.values()) 
    
    def get_daily_notes(self, date: datetime = None) -> List[dict]:
        """获取指定日期的便签"""
        notes = self.storage.get_daily_notes(date)
        return list(notes.values())
    
    def get_all_notes(self):
        """获取所有便签"""
        return self.storage.get_all_notes()