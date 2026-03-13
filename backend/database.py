"""
数据库管理模块
使用 SQLite 存储数据
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class Database:
    """SQLite 数据库管理"""
    
    def __init__(self, db_path: str = "security_system.db"):
        """初始化数据库"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                id_card TEXT UNIQUE,
                name TEXT,
                created_at TEXT
            )
        ''')
        
        # 入场记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                items_json TEXT NOT NULL,
                total_count INTEGER,
                total_weight REAL,
                image_path TEXT,
                timestamp TEXT,
                channel_no INTEGER,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # 离场记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exit_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                items_json TEXT NOT NULL,
                total_count INTEGER,
                total_weight REAL,
                image_path TEXT,
                timestamp TEXT,
                channel_no INTEGER,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # 异常记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                alert_type TEXT,
                detail TEXT,
                entry_time TEXT,
                exit_time TEXT,
                entry_items_json TEXT,
                exit_items_json TEXT,
                timestamp TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库初始化完成：{self.db_path}")
    
    def add_user(self, user_id: str, id_card: str, name: str = "") -> bool:
        """添加用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, id_card, name, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, id_card, name, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user_by_id_card(self, id_card: str) -> Optional[Dict]:
        """根据身份证号获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, id_card, name FROM users WHERE id_card = ?', (id_card,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "user_id": row[0],
                "id_card": row[1],
                "name": row[2]
            }
        return None
    
    def add_entry_record(self, record_id: str, user_id: str, items: List[Dict], 
                        total_count: int, total_weight: float, image_path: str,
                        timestamp: str, channel_no: int = 1) -> bool:
        """添加入场记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO entry_records 
                (id, user_id, items_json, total_count, total_weight, image_path, timestamp, channel_no, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, user_id, json.dumps(items), total_count, total_weight, 
                  image_path, timestamp, channel_no, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 添加入场记录失败：{str(e)}")
            return False
    
    def add_exit_record(self, record_id: str, user_id: str, items: List[Dict],
                       total_count: int, total_weight: float, image_path: str,
                       timestamp: str, channel_no: int = 1) -> bool:
        """添加离场记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO exit_records
                (id, user_id, items_json, total_count, total_weight, image_path, timestamp, channel_no, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, user_id, json.dumps(items), total_count, total_weight,
                  image_path, timestamp, channel_no, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 添加离场记录失败：{str(e)}")
            return False
    
    def get_entry_record(self, user_id: str) -> Optional[Dict]:
        """获取用户的入场记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, items_json, total_count, total_weight, timestamp, channel_no
            FROM entry_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "items": json.loads(row[2]),
                "total_count": row[3],
                "total_weight": row[4],
                "timestamp": row[5],
                "channel_no": row[6]
            }
        return None
    
    def add_alert_record(self, alert_id: str, user_id: str, alert_type: str, detail: str,
                        entry_time: str, exit_time: str, entry_items: List[Dict],
                        exit_items: List[Dict]) -> bool:
        """添加异常记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alert_records
                (id, user_id, alert_type, detail, entry_time, exit_time, entry_items_json, exit_items_json, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, user_id, alert_type, detail, entry_time, exit_time,
                  json.dumps(entry_items), json.dumps(exit_items), 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 添加异常记录失败：{str(e)}")
            return False
    
    def get_alert_records(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """获取异常记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT id, user_id, alert_type, detail, entry_time, exit_time, timestamp
                FROM alert_records WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT id, user_id, alert_type, detail, entry_time, exit_time, timestamp
                FROM alert_records ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "alert_type": row[2],
                "detail": row[3],
                "entry_time": row[4],
                "exit_time": row[5],
                "timestamp": row[6]
            }
            for row in rows
        ]
    
    def get_recent_records(self, limit: int = 10) -> List[Dict]:
        """获取最近的入场和离场记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最近的入场记录
        cursor.execute('''
            SELECT 'entry' as type, id, user_id, total_count, timestamp
            FROM entry_records ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        entry_rows = cursor.fetchall()
        
        # 获取最近的离场记录
        cursor.execute('''
            SELECT 'exit' as type, id, user_id, total_count, timestamp
            FROM exit_records ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        exit_rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in entry_rows:
            records.append({
                "type": row[0],
                "id": row[1],
                "user_id": row[2],
                "total_count": row[3],
                "timestamp": row[4]
            })
        
        for row in exit_rows:
            records.append({
                "type": row[0],
                "id": row[1],
                "user_id": row[2],
                "total_count": row[3],
                "timestamp": row[4]
            })
        
        # 按时间排序
        records.sort(key=lambda x: x["timestamp"], reverse=True)
        return records[:limit]
    
    def get_statistics(self) -> Dict:
        """获取统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总入场数
        cursor.execute('SELECT COUNT(*) FROM entry_records')
        total_entry = cursor.fetchone()[0]
        
        # 总离场数
        cursor.execute('SELECT COUNT(*) FROM exit_records')
        total_exit = cursor.fetchone()[0]
        
        # 总异常数
        cursor.execute('SELECT COUNT(*) FROM alert_records')
        total_alerts = cursor.fetchone()[0]
        
        # 当前在场人数
        cursor.execute('''
            SELECT COUNT(DISTINCT e.user_id) FROM entry_records e
            LEFT JOIN exit_records x ON e.user_id = x.user_id
            WHERE x.user_id IS NULL
        ''')
        current_inside = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entry": total_entry,
            "total_exit": total_exit,
            "total_alerts": total_alerts,
            "current_inside": current_inside
        }
    
    def clear_all(self):
        """清空所有数据（仅用于测试）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alert_records')
        cursor.execute('DELETE FROM exit_records')
        cursor.execute('DELETE FROM entry_records')
        cursor.execute('DELETE FROM users')
        conn.commit()
        conn.close()
        print("✅ 数据库已清空")
