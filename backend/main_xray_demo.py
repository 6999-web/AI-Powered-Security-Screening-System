"""
X 光安检机模拟 Demo - 后端服务
支持图片上传、AI 识别、物品比对
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import os
import sys
import uuid

# 添加 app 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

# 导入模块
from app.services.ai_detector import AIDetector
from app.services.compare import ItemComparator
from database import Database

# 初始化应用
app = FastAPI(
    title="X 光安检机模拟 Demo API",
    description="支持图片上传、AI 识别、物品比对的安检系统",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
db = Database("security_system.db")

# 初始化 AI 识别器（使用通义千问 API）
ai_detector = AIDetector(use_qwen=True)

print("=" * 60)
print("X 光安检机模拟 Demo - 后端服务")
print("=" * 60)
print(f"✅ 数据库已初始化")
print(f"✅ AI 识别器已初始化（模拟模式）")
print(f"📍 API 文档: http://localhost:8888/docs")
print("=" * 60)


# ==================== 数据模型 ====================

class ItemInfo(BaseModel):
    """物品信息"""
    name: str
    category: str
    quantity: int
    weight: float = 0.0


class EntryResponse(BaseModel):
    """入场响应"""
    record_id: str
    user_id: str
    items: List[ItemInfo]
    total_count: int
    total_weight: float
    timestamp: str


class ExitResponse(BaseModel):
    """离场响应"""
    record_id: str
    user_id: str
    items: List[ItemInfo]
    total_count: int
    total_weight: float
    comparison_status: str
    anomalies: List[dict]
    timestamp: str


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根端点"""
    return {
        "name": "X 光安检机模拟 Demo",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.post("/api/verify-identity")
async def verify_identity(idCard: str = Form(None)):
    """身份验证 - 查找或创建用户"""
    try:
        if not idCard:
            raise HTTPException(status_code=400, detail="身份证号不能为空")
        
        # 生成用户 ID（基于身份证号）
        user_id = f"USER_{idCard[-6:]}"
        
        return {
            "userId": user_id,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entry")
async def entry_check(
    image: UploadFile = File(...),
    user_id: str = Form(...),
    channel_no: int = Form(1)
):
    """
    入场安检
    
    Args:
        image: X 光扫描图片
        user_id: 用户 ID
        channel_no: 通道号
        
    Returns:
        入场记录信息
    """
    try:
        # 读取图片
        image_data = await image.read()
        print(f"\n📸 收到入场图片，大小：{len(image_data)} 字节")
        
        # AI 识别物品
        print("🤖 正在识别物品...")
        items = ai_detector.detect(image_data)
        print(f"✅ 识别完成，共 {len(items)} 种物品")
        
        # 计算统计信息
        total_count = sum(item["quantity"] for item in items)
        total_weight = sum(item.get("weight", 0) for item in items)
        
        # 生成记录 ID
        record_id = f"ENTRY_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # 保存到数据库
        image_path = f"uploads/entry_{record_id}.jpg"
        db.add_entry_record(
            record_id=record_id,
            user_id=user_id,
            items=items,
            total_count=total_count,
            total_weight=total_weight,
            image_path=image_path,
            timestamp=timestamp,
            channel_no=channel_no
        )
        
        print(f"💾 入场记录已保存：{record_id}")
        
        return EntryResponse(
            record_id=record_id,
            user_id=user_id,
            items=[ItemInfo(**item) for item in items],
            total_count=total_count,
            total_weight=total_weight,
            timestamp=timestamp
        )
    
    except Exception as e:
        print(f"❌ 入场安检失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"入场安检失败：{str(e)}")


@app.post("/api/exit")
async def exit_check(
    image: UploadFile = File(...),
    user_id: str = Form(...),
    channel_no: int = Form(1)
):
    """
    离场安检
    
    Args:
        image: X 光扫描图片
        user_id: 用户 ID
        channel_no: 通道号
        
    Returns:
        离场记录和比对结果
    """
    try:
        # 检查是否有入场记录
        entry_record = db.get_entry_record(user_id)
        if not entry_record:
            raise HTTPException(status_code=404, detail=f"未找到用户 {user_id} 的入场记录")
        
        # 读取图片
        image_data = await image.read()
        print(f"\n📸 收到离场图片，大小：{len(image_data)} 字节")
        
        # AI 识别物品
        print("🤖 正在识别物品...")
        exit_items = ai_detector.detect(image_data)
        print(f"✅ 识别完成，共 {len(exit_items)} 种物品")
        
        # 比对物品
        print("🔍 正在比对物品...")
        status, anomalies = ItemComparator.compare(entry_record["items"], exit_items)
        print(f"✅ 比对完成，状态：{status}")
        
        # 计算统计信息
        total_count = sum(item["quantity"] for item in exit_items)
        total_weight = sum(item.get("weight", 0) for item in exit_items)
        
        # 生成记录 ID
        record_id = f"EXIT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # 保存到数据库
        image_path = f"uploads/exit_{record_id}.jpg"
        db.add_exit_record(
            record_id=record_id,
            user_id=user_id,
            items=exit_items,
            total_count=total_count,
            total_weight=total_weight,
            image_path=image_path,
            timestamp=timestamp,
            channel_no=channel_no
        )
        
        # 如果有异常，记录异常信息
        if status == "anomaly":
            for anomaly in anomalies:
                alert_id = f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
                db.add_alert_record(
                    alert_id=alert_id,
                    user_id=user_id,
                    alert_type=anomaly["type"],
                    detail=anomaly["description"],
                    entry_time=entry_record["timestamp"],
                    exit_time=timestamp,
                    entry_items=entry_record["items"],
                    exit_items=exit_items
                )
                print(f"⚠️ 异常记录已保存：{alert_id}")
        
        print(f"💾 离场记录已保存：{record_id}")
        
        return ExitResponse(
            record_id=record_id,
            user_id=user_id,
            items=[ItemInfo(**item) for item in exit_items],
            total_count=total_count,
            total_weight=total_weight,
            comparison_status=status,
            anomalies=anomalies,
            timestamp=timestamp
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 离场安检失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"离场安检失败：{str(e)}")


@app.get("/api/compare/{user_id}")
async def get_comparison(user_id: str):
    """
    获取比对结果
    
    Args:
        user_id: 用户 ID
        
    Returns:
        入场和离场物品的比对结果
    """
    try:
        entry_record = db.get_entry_record(user_id)
        if not entry_record:
            raise HTTPException(status_code=404, detail=f"未找到用户 {user_id} 的入场记录")
        
        return {
            "user_id": user_id,
            "entry_items": entry_record["items"],
            "entry_timestamp": entry_record["timestamp"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/records")
async def get_records(
    user_id: Optional[str] = None,
    record_type: Optional[str] = None,
    limit: int = 100
):
    """
    获取历史记录
    
    Args:
        user_id: 用户 ID（可选）
        record_type: 记录类型（entry/exit/alert）
        limit: 返回数量限制
        
    Returns:
        历史记录列表
    """
    try:
        if record_type == "alert":
            records = db.get_alert_records(user_id=user_id, limit=limit)
        else:
            records = []
        
        return {
            "records": records,
            "total": len(records)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """
    获取统计数据
    
    Returns:
        系统统计信息
    """
    try:
        stats = db.get_statistics()
        return {
            "total_entry": stats["total_entry"],
            "total_exit": stats["total_exit"],
            "total_alerts": stats["total_alerts"],
            "current_inside": stats["current_inside"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recent-records")
async def get_recent_records(limit: int = 10):
    """
    获取最近的入场和离场记录
    
    Args:
        limit: 返回数量限制
        
    Returns:
        最近的记录列表
    """
    try:
        records = db.get_recent_records(limit=limit)
        return {
            "records": records,
            "total": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recent-anomalies")
async def get_recent_anomalies(limit: int = 10):
    """
    获取最近的异常记录
    
    Args:
        limit: 返回数量限制
        
    Returns:
        最近的异常记录列表
    """
    try:
        anomalies = db.get_alert_records(limit=limit)
        return {
            "anomalies": anomalies,
            "total": len(anomalies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anomalies")
async def get_anomalies(user_id: Optional[str] = None, limit: int = 100):
    """
    获取异常记录
    
    Args:
        user_id: 用户 ID（可选）
        limit: 返回数量限制
        
    Returns:
        异常记录列表
    """
    try:
        anomalies = db.get_alert_records(user_id=user_id, limit=limit)
        return {
            "anomalies": anomalies,
            "total": len(anomalies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/channels")
async def get_channels():
    """
    获取通道信息
    
    Returns:
        通道列表
    """
    try:
        return {
            "channels": [
                {"id": 1, "name": "通道 1", "status": "active"},
                {"id": 2, "name": "通道 2", "status": "active"},
                {"id": 3, "name": "通道 3", "status": "inactive"},
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_data():
    """
    清空所有数据（仅用于测试）
    
    Returns:
        清空结果
    """
    try:
        db.clear_all()
        return {"status": "success", "message": "所有数据已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("\n🚀 启动 X 光安检机模拟 Demo 后端服务...")
    uvicorn.run(app, host="0.0.0.0", port=9527)
