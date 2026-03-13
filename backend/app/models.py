"""
数据模型定义
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ItemInfo(BaseModel):
    """物品信息"""
    name: str
    category: str
    quantity: int
    weight: float = 0.0


class EntryRecord(BaseModel):
    """入场记录"""
    id: str
    user_id: str
    items: List[ItemInfo]
    total_count: int
    total_weight: float
    image_path: str
    timestamp: str
    channel_no: int = 1


class ExitRecord(BaseModel):
    """离场记录"""
    id: str
    user_id: str
    items: List[ItemInfo]
    total_count: int
    total_weight: float
    image_path: str
    timestamp: str
    channel_no: int = 1


class AlertRecord(BaseModel):
    """异常记录"""
    id: str
    user_id: str
    alert_type: str  # extra, missing, quantity
    detail: str
    entry_time: str
    exit_time: str
    timestamp: str
    entry_items: List[ItemInfo]
    exit_items: List[ItemInfo]


class ComparisonResult(BaseModel):
    """比对结果"""
    status: str  # normal, anomaly
    entry_items: List[ItemInfo]
    exit_items: List[ItemInfo]
    anomalies: List[dict]
    comparison_time: str
