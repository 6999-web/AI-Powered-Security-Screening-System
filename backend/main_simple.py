"""
简化版后端服务 - 用于测试
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime

app = FastAPI(title="智能安检系统 API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据库
security_records = {}
anomalies_db = []
check_in_records = []
check_out_records = []

@app.get("/")
async def root():
    return {"message": "智能安检系统 API", "status": "running"}

@app.get("/api/statistics")
async def get_statistics():
    """获取统计数据"""
    today = datetime.now().date()
    today_check_in = sum(1 for record in check_in_records 
                         if datetime.fromisoformat(record["checkTime"]).date() == today)
    today_check_out = sum(1 for record in check_out_records 
                          if datetime.fromisoformat(record["checkTime"]).date() == today)
    today_anomalies = sum(1 for anomaly in anomalies_db 
                          if datetime.strptime(anomaly["time"], "%Y-%m-%d %H:%M:%S").date() == today)
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
    
    all_records.sort(key=lambda x: x["time"], reverse=True)
    return all_records[:limit]

@app.get("/api/recent-anomalies")
async def get_recent_anomalies(limit: int = 10):
    """获取最近的异常记录"""
    return anomalies_db[-limit:][::-1]

@app.get("/api/channels")
async def get_channels():
    """获取通道使用情况"""
    today = datetime.now().date()
    
    channels = []
    for i in range(1, 5):
        today_count = sum(1 for record in check_in_records 
                         if record["channelNo"] == i and 
                         datetime.fromisoformat(record["checkTime"]).date() == today)
        
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

if __name__ == "__main__":
    print("=" * 50)
    print("智能安检系统后端服务启动（简化版）")
    print("API 文档: http://localhost:8888/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8888)
