from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import json
import base64
import os
import sys

# 添加 app 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# 导入服务
from app.services.qwen_service import QwenVisionService
from app.config.settings import settings

app = FastAPI(title="智能安检系统 API")

# 初始化 AI 服务
try:
    settings.validate()
    qwen_service = QwenVisionService()
    print("✅ AI 识别服务初始化成功")
except Exception as e:
    print(f"⚠️ AI 识别服务初始化失败：{str(e)}")
    print("⚠️ 将使用模拟数据模式运行")
    qwen_service = None

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据库
users_db = {}
security_records = {}  # 格式: {userId: {type, items, totalCount, totalWeight, checkTime, channelNo}}
anomalies_db = []
check_in_records = []  # 入场记录列表
check_out_records = []  # 离场记录列表

class Item(BaseModel):
    name: str
    category: str
    quantity: int
    weight: float

class CheckInResponse(BaseModel):
    userId: str
    items: List[Item]
    totalCount: int
    totalWeight: float
    checkTime: str
    channelNo: int

class ComparisonResult(BaseModel):
    status: str
    items: List[dict]
    anomalies: List[dict]

@app.get("/")
async def root():
    return {"message": "智能安检系统 API", "status": "running"}

@app.post("/api/verify-identity")
async def verify_identity(idCard: str = Form(None)):
    """身份验证 - 查找或创建用户"""
    # 查找是否已有该身份证号的用户
    for user_id, user_info in users_db.items():
        if user_info.get("idCard") == idCard:
            # 找到已存在的用户，返回该用户ID
            return {"userId": user_id, "status": "success"}
    
    # 如果没有找到，创建新用户
    user_id = f"USER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    users_db[user_id] = {
        "idCard": idCard,
        "verifyTime": datetime.now().isoformat()
    }
    return {"userId": user_id, "status": "success"}

@app.post("/api/checkin")
async def checkin(
    image: UploadFile = File(...),
    userId: str = Form(...),
    weight: float = Form(0),
    channelNo: int = Form(1)
):
    """入场安检 - AI识别物品"""
    
    try:
        # 读取图片
        image_data = await image.read()
        print(f"收到图片，大小：{len(image_data)} 字节")
        
        # 调用 AI 识别服务
        if qwen_service:
            try:
                print("正在调用 AI 识别...")
                items = await qwen_service.recognize_items(image_data)
                print(f"✅ AI识别成功，共 {len(items)} 个物品")
            except Exception as ai_error:
                print(f"⚠️ AI识别失败：{str(ai_error)}")
                print("⚠️ 使用模拟数据")
                # AI 识别失败时使用模拟数据
                items = [
                    {"name": "笔记本电脑", "category": "电子产品", "quantity": 1, "weight": 1.5},
                    {"name": "手机", "category": "电子产品", "quantity": 1, "weight": 0.2},
                    {"name": "钱包", "category": "个人物品", "quantity": 1, "weight": 0.1},
                    {"name": "水杯", "category": "个人物品", "quantity": 1, "weight": 0.3}
                ]
        else:
            # 如果 AI 服务未初始化，返回模拟数据
            print("⚠️ AI 服务未初始化，使用模拟数据")
            items = [
                {"name": "笔记本电脑", "category": "电子产品", "quantity": 1, "weight": 1.5},
                {"name": "手机", "category": "电子产品", "quantity": 1, "weight": 0.2},
                {"name": "钱包", "category": "个人物品", "quantity": 1, "weight": 0.1},
                {"name": "水杯", "category": "个人物品", "quantity": 1, "weight": 0.3}
            ]
        
        # 计算统计信息
        total_count = sum(item["quantity"] for item in items)
        total_weight = weight if weight > 0 else sum(item.get("weight", 0) for item in items)
        
        check_time = datetime.now()
        
        # 保存入场记录
        record = {
            "userId": userId,
            "type": "entry",
            "items": items,
            "totalCount": total_count,
            "totalWeight": total_weight,
            "checkTime": check_time.isoformat(),
            "checkTimeFormatted": check_time.strftime("%Y-%m-%d %H:%M:%S"),
            "channelNo": channelNo
        }
        
        security_records[userId] = record
        check_in_records.append(record)
        
        return {
            "userId": userId,
            "items": items,
            "totalCount": total_count,
            "totalWeight": total_weight,
            "checkTime": check_time.strftime("%Y-%m-%d %H:%M:%S"),
            "channelNo": channelNo
        }
    
    except Exception as e:
        print(f"❌ 入场安检失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"识别失败：{str(e)}")

@app.post("/api/checkout")
async def checkout(
    image: UploadFile = File(...),
    userId: str = Form(...),
    weight: float = Form(0),
    channelNo: int = Form(1)
):
    """离场安检 - AI识别并比对"""
    
    # 检查是否有入场记录
    if userId not in security_records:
        raise HTTPException(status_code=404, detail="未找到入场记录")
    
    entry_record = security_records[userId]
    
    # 读取图片并识别
    image_data = await image.read()
    
    try:
        # 调用 AI 识别
        if qwen_service:
            try:
                print("正在调用 AI 识别...")
                exit_items = await qwen_service.recognize_items(image_data)
                print(f"✅ AI识别成功，共 {len(exit_items)} 个物品")
            except Exception as ai_error:
                print(f"⚠️ AI识别失败：{str(ai_error)}")
                print("⚠️ 使用模拟数据")
                # AI 识别失败时使用模拟数据
                import random
                is_normal = random.random() > 0.3
                
                if is_normal:
                    exit_items = entry_record["items"]
                else:
                    exit_items = entry_record["items"].copy()
                    if random.random() > 0.5:
                        # 多带物品
                        exit_items.append({
                            "name": "平板电脑",
                            "category": "电子产品",
                            "quantity": 1,
                            "weight": 0.5
                        })
                    else:
                        # 少带物品
                        if len(exit_items) > 0:
                            exit_items = exit_items[:-1]
        else:
            # 模拟识别结果 - 随机生成正常或异常情况
            print("⚠️ AI 服务未初始化，使用模拟数据")
            import random
            is_normal = random.random() > 0.3
            
            if is_normal:
                exit_items = entry_record["items"]
            else:
                exit_items = entry_record["items"].copy()
                if random.random() > 0.5:
                    # 多带物品
                    exit_items.append({
                        "name": "平板电脑",
                        "category": "电子产品",
                        "quantity": 1,
                        "weight": 0.5
                    })
                else:
                    # 少带物品
                    if len(exit_items) > 0:
                        exit_items = exit_items[:-1]
        
        # 比对物品
        status, anomalies = compare_items(entry_record["items"], exit_items)
        
        check_time = datetime.now()
        
        # 保存离场记录
        checkout_record = {
            "userId": userId,
            "type": "exit",
            "items": exit_items,
            "totalCount": sum(item["quantity"] for item in exit_items),
            "totalWeight": weight if weight > 0 else sum(item.get("weight", 0) for item in exit_items),
            "checkTime": check_time.isoformat(),
            "checkTimeFormatted": check_time.strftime("%Y-%m-%d %H:%M:%S"),
            "channelNo": channelNo
        }
        check_out_records.append(checkout_record)
        
        # 如果有异常，记录异常信息
        if status == "anomaly":
            anomaly_record = {
                "id": f"AN{len(anomalies_db) + 1:03d}",
                "userId": userId,
                "type": anomalies[0]["type"] if anomalies else "unknown",
                "typeText": anomalies[0]["title"] if anomalies else "未知异常",
                "time": check_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "pending",
                "entryTime": entry_record["checkTimeFormatted"],
                "exitTime": check_time.strftime("%Y-%m-%d %H:%M:%S"),
                "entryChannel": entry_record["channelNo"],
                "exitChannel": channelNo,
                "entryItems": entry_record["items"],
                "exitItems": exit_items,
                "anomalyDescription": anomalies[0]["description"] if anomalies else "检测到异常"
            }
            anomalies_db.append(anomaly_record)
        else:
            # 正常离场，删除入场记录
            del security_records[userId]
        
        # 构建比对结果
        comparison_items = []
        for item in exit_items:
            comparison_items.append({
                **item,
                "status": status,
                "statusText": "一致" if status == "normal" else "异常"
            })
        
        return {
            "status": status,
            "items": comparison_items,
            "anomalies": anomalies
        }
    
    except Exception as e:
        print(f"❌ 离场安检失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"识别失败：{str(e)}")


def compare_items(entry_items: List[dict], exit_items: List[dict]):
    """比对入场和离场物品"""
    anomalies = []
    
    # 创建物品字典便于比对
    entry_dict = {item["name"]: item for item in entry_items}
    exit_dict = {item["name"]: item for item in exit_items}
    
    # 检查多带物品
    for name, item in exit_dict.items():
        if name not in entry_dict:
            anomalies.append({
                "type": "extra",
                "title": "检测到多带物品",
                "description": f'离场时发现"{name}"，入场记录中不存在该物品'
            })
    
    # 检查少带物品
    for name, item in entry_dict.items():
        if name not in exit_dict:
            anomalies.append({
                "type": "missing",
                "title": "物品缺失",
                "description": f'入场物品"{name}"在离场时未检测到'
            })
    
    # 检查数量异常
    for name in set(entry_dict.keys()) & set(exit_dict.keys()):
        if entry_dict[name]["quantity"] != exit_dict[name]["quantity"]:
            anomalies.append({
                "type": "quantity",
                "title": "数量异常",
                "description": f'物品"{name}"数量不一致：入场{entry_dict[name]["quantity"]}，离场{exit_dict[name]["quantity"]}'
            })
    
    status = "normal" if len(anomalies) == 0 else "anomaly"
    return status, anomalies

@app.get("/api/compare/{userId}")
async def get_comparison(userId: str):
    """获取比对结果"""
    if userId not in security_records:
        raise HTTPException(status_code=404, detail="未找到记录")
    
    return security_records[userId]

@app.get("/api/anomalies")
async def get_anomalies(
    userId: Optional[str] = None,
    type: Optional[str] = None,
    page: int = 1,
    pageSize: int = 10
):
    """获取异常记录"""
    filtered = anomalies_db
    
    if userId:
        filtered = [a for a in filtered if a["userId"] == userId]
    if type:
        filtered = [a for a in filtered if a["type"] == type]
    
    start = (page - 1) * pageSize
    end = start + pageSize
    
    return {
        "data": filtered[start:end],
        "total": len(filtered),
        "page": page,
        "pageSize": pageSize
    }

@app.get("/api/statistics")
async def get_statistics():
    """获取统计数据"""
    # 计算今日入场数
    today = datetime.now().date()
    today_check_in = sum(1 for record in check_in_records 
                         if datetime.fromisoformat(record["checkTime"]).date() == today)
    
    # 计算今日离场数
    today_check_out = sum(1 for record in check_out_records 
                          if datetime.fromisoformat(record["checkTime"]).date() == today)
    
    # 计算今日异常数
    today_anomalies = sum(1 for anomaly in anomalies_db 
                          if datetime.strptime(anomaly["time"], "%Y-%m-%d %H:%M:%S").date() == today)
    
    # 当前在场人数（入场但未离场）
    current_inside = len(security_records)
    
    return {
        "todayCheckIn": today_check_in,
        "todayCheckOut": today_check_out,
        "todayAnomalies": today_anomalies,
        "currentInside": current_inside
    }


@app.get("/api/recent-records")
async def get_recent_records(limit: int = 10):
    """获取最近的安检记录"""
    # 合并入场和离场记录
    all_records = []
    
    for record in check_in_records[-limit:]:
        all_records.append({
            "userId": record["userId"],
            "type": "入场",
            "itemCount": record["totalCount"],
            "time": record["checkTimeFormatted"],
            "channelNo": record["channelNo"]
        })
    
    for record in check_out_records[-limit:]:
        all_records.append({
            "userId": record["userId"],
            "type": "离场",
            "itemCount": record["totalCount"],
            "time": record["checkTimeFormatted"],
            "channelNo": record["channelNo"]
        })
    
    # 按时间排序
    all_records.sort(key=lambda x: x["time"], reverse=True)
    
    return all_records[:limit]


@app.get("/api/recent-anomalies")
async def get_recent_anomalies(limit: int = 10):
    """获取最近的异常记录"""
    return anomalies_db[-limit:][::-1]  # 返回最近的记录，倒序


@app.get("/api/channels")
async def get_channels():
    """获取通道使用情况"""
    today = datetime.now().date()
    
    channels = []
    for i in range(1, 5):  # 4个通道
        # 统计今日通过人数
        today_count = sum(1 for record in check_in_records 
                         if record["channelNo"] == i and 
                         datetime.fromisoformat(record["checkTime"]).date() == today)
        
        # 检查是否有人正在使用
        current_user = None
        for userId, record in security_records.items():
            if record["channelNo"] == i:
                current_user = userId
                break
        
        channels.append({
            "id": i,
            "active": current_user is not None,
            "todayCount": today_count,
            "currentUser": current_user
        })
    
    return channels

if __name__ == "__main__":
    print("=" * 50)
    print("智能安检系统后端服务启动")
    print("API 文档: http://localhost:8888/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8888)
