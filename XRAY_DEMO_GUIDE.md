# X 光安检机模拟 Demo - 完整运行指南

## 📋 项目概述

这是一个基于 Python FastAPI 和 HTML/JavaScript 的 X 光安检机模拟系统，用于展示：
- 图片上传和处理
- AI 物品识别（支持真实模型和模拟模式）
- 入场/离场物品比对
- 异常检测和记录

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 Web 界面                          │
│              (HTML + JavaScript + CSS)                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI 后端服务                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 图像处理模块  │  │ AI识别模块   │  │ 比对模块     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ SQLite
┌────────────────────▼────────────────────────────────────┐
│                   SQLite 数据库                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 用户表       │  │ 入场记录表   │  │ 异常记录表   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
security_ai_demo/
├── backend/
│   ├── main_xray_demo.py          # 后端主程序
│   ├── database.py                # 数据库管理
│   ├── requirements_xray_demo.txt # Python 依赖
│   └── app/
│       ├── services/
│       │   ├── ai_detector.py     # AI 识别模块
│       │   └── compare.py         # 物品比对模块
│       ├── config/
│       │   └── settings.py        # 配置管理
│       └── models.py              # 数据模型
├── frontend/
│   └── index.html                 # 前端页面
└── XRAY_DEMO_GUIDE.md            # 本文件
```

## 🚀 快速开始

### 1. 环境准备

#### Windows 用户
```bash
# 安装 Python 3.8+
# 从 https://www.python.org/downloads/ 下载并安装

# 验证 Python 安装
python --version
pip --version
```

#### macOS/Linux 用户
```bash
# 使用 Homebrew（macOS）
brew install python3

# 或使用包管理器（Linux）
sudo apt-get install python3 python3-pip
```

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements_xray_demo.txt
```

### 3. 启动后端服务

```bash
# 确保在 backend 目录中
cd backend

# 启动 FastAPI 服务
python main_xray_demo.py
```

输出应该显示：
```
============================================================
X 光安检机模拟 Demo - 后端服务
============================================================
✅ 数据库已初始化
✅ AI 识别器已初始化（模拟模式）
📍 API 文档: http://localhost:8888/docs
============================================================

INFO:     Uvicorn running on http://0.0.0.0:8888
```

### 4. 打开前端页面

在浏览器中访问：
```
http://localhost:8888/docs          # API 文档
http://localhost:8888/              # 前端页面（如果配置了静态文件）
```

或者直接打开 `frontend/index.html` 文件：
```bash
# Windows
start frontend/index.html

# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html
```

## 📖 使用流程

### 入场安检流程

1. **输入用户 ID**
   - 例如：USER001

2. **上传 X 光图片**
   - 点击"上传 X 光图片"按钮
   - 选择任意图片文件（系统会模拟识别）

3. **设置通道号**
   - 默认为 1，可根据需要修改

4. **点击"开始入场安检"**
   - 系统会识别物品并保存记录
   - 显示识别结果（物品名称、类别、数量、重量）

### 离场安检流程

1. **输入相同的用户 ID**
   - 必须与入场时使用的 ID 相同

2. **上传 X 光图片**
   - 点击"上传 X 光图片"按钮
   - 选择图片文件

3. **点击"开始离场安检"**
   - 系统会识别物品
   - 自动与入场记录比对
   - 显示比对结果和异常信息

### 异常检测

系统会自动检测以下异常：

- **多带物品**：离场时发现入场记录中不存在的物品
- **物品缺失**：入场物品在离场时未检测到
- **数量异常**：同一物品的数量不一致
- **重量异常**：总重量差异超过 0.5kg

## 🔧 API 文档

### 入场安检

```
POST /entry
Content-Type: multipart/form-data

参数：
- image: 图片文件（必需）
- user_id: 用户 ID（必需）
- channel_no: 通道号（可选，默认 1）

响应：
{
  "record_id": "ENTRY_20240101120000_abc12345",
  "user_id": "USER001",
  "items": [
    {
      "name": "笔记本电脑",
      "category": "电子产品",
      "quantity": 1,
      "weight": 1.5
    }
  ],
  "total_count": 4,
  "total_weight": 2.1,
  "timestamp": "2024-01-01T12:00:00"
}
```

### 离场安检

```
POST /exit
Content-Type: multipart/form-data

参数：
- image: 图片文件（必需）
- user_id: 用户 ID（必需）
- channel_no: 通道号（可选，默认 1）

响应：
{
  "record_id": "EXIT_20240101120500_def67890",
  "user_id": "USER001",
  "items": [...],
  "total_count": 4,
  "total_weight": 2.1,
  "comparison_status": "normal",  // 或 "anomaly"
  "anomalies": [
    {
      "type": "extra",
      "title": "检测到多带物品",
      "description": "离场时发现\"平板电脑\"..."
    }
  ],
  "timestamp": "2024-01-01T12:00:30"
}
```

### 获取统计信息

```
GET /statistics

响应：
{
  "total_entry": 10,
  "total_exit": 8,
  "total_alerts": 2,
  "current_inside": 2
}
```

### 获取历史记录

```
GET /records?user_id=USER001&record_type=alert&limit=100

响应：
{
  "records": [...],
  "total": 5
}
```

### 清空数据

```
POST /clear

响应：
{
  "status": "success",
  "message": "所有数据已清空"
}
```

## 🎯 示例场景

### 场景 1：正常入场和离场

1. 用户 USER001 入场
   - 上传图片
   - 系统识别：笔记本电脑、手机、钱包、水杯

2. 用户 USER001 离场
   - 上传图片
   - 系统识别：笔记本电脑、手机、钱包、水杯
   - 比对结果：✅ 正常

### 场景 2：检测到多带物品

1. 用户 USER002 入场
   - 识别：手机、钱包

2. 用户 USER002 离场
   - 识别：手机、钱包、平板电脑
   - 比对结果：⚠️ 异常 - 检测到多带物品

### 场景 3：检测到物品缺失

1. 用户 USER003 入场
   - 识别：笔记本电脑、手机、钱包

2. 用户 USER003 离场
   - 识别：笔记本电脑、手机
   - 比对结果：⚠️ 异常 - 物品缺失

## 🔍 数据库结构

### users 表
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    id_card TEXT UNIQUE,
    name TEXT,
    created_at TEXT
)
```

### entry_records 表
```sql
CREATE TABLE entry_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    items_json TEXT NOT NULL,
    total_count INTEGER,
    total_weight REAL,
    image_path TEXT,
    timestamp TEXT,
    channel_no INTEGER,
    created_at TEXT
)
```

### exit_records 表
```sql
CREATE TABLE exit_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    items_json TEXT NOT NULL,
    total_count INTEGER,
    total_weight REAL,
    image_path TEXT,
    timestamp TEXT,
    channel_no INTEGER,
    created_at TEXT
)
```

### alert_records 表
```sql
CREATE TABLE alert_records (
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
    created_at TEXT
)
```

## 🧪 测试

### 使用 curl 测试 API

```bash
# 入场安检
curl -X POST http://localhost:8888/entry \
  -F "image=@test_image.jpg" \
  -F "user_id=USER001" \
  -F "channel_no=1"

# 离场安检
curl -X POST http://localhost:8888/exit \
  -F "image=@test_image.jpg" \
  -F "user_id=USER001" \
  -F "channel_no=1"

# 获取统计信息
curl http://localhost:8888/statistics

# 清空数据
curl -X POST http://localhost:8888/clear
```

### 使用 Python 测试

```python
import requests

# 入场安检
with open('test_image.jpg', 'rb') as f:
    files = {'image': f}
    data = {'user_id': 'USER001', 'channel_no': 1}
    response = requests.post('http://localhost:8888/entry', files=files, data=data)
    print(response.json())

# 离场安检
with open('test_image.jpg', 'rb') as f:
    files = {'image': f}
    data = {'user_id': 'USER001', 'channel_no': 1}
    response = requests.post('http://localhost:8888/exit', files=files, data=data)
    print(response.json())
```

## 🐛 故障排查

### 问题 1：后端无法启动

**症状**：`Address already in use`

**解决方案**：
```bash
# Windows - 查找占用 8888 端口的进程
netstat -ano | findstr :8888

# 杀死进程
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8888
kill -9 <PID>
```

### 问题 2：前端无法连接后端

**症状**：请求失败，显示 CORS 错误

**解决方案**：
- 确保后端服务已启动
- 检查后端地址是否正确（http://localhost:8888）
- 检查浏览器控制台的错误信息

### 问题 3：图片上传失败

**症状**：上传图片后显示错误

**解决方案**：
- 确保图片格式正确（JPG、PNG）
- 检查图片大小（建议 < 10MB）
- 查看后端日志获取详细错误信息

## 📊 性能优化建议

1. **缓存识别结果**
   - 对相同图片的识别结果进行缓存
   - 减少重复计算

2. **异步处理**
   - 使用后台任务处理大量图片
   - 提高系统吞吐量

3. **数据库优化**
   - 添加索引加快查询
   - 定期清理过期数据

4. **前端优化**
   - 压缩图片后上传
   - 使用 WebWorker 处理图片

## 🔐 安全建议

1. **API 认证**
   - 添加 JWT 认证
   - 实现用户权限管理

2. **数据加密**
   - 加密敏感数据
   - 使用 HTTPS

3. **输入验证**
   - 验证所有用户输入
   - 防止 SQL 注入

4. **日志记录**
   - 记录所有操作
   - 便于审计和调试

## 📚 扩展功能

### 1. 集成真实 YOLOv8 模型

```python
# 在 ai_detector.py 中修改
ai_detector = AIDetector(use_yolo=True)
```

### 2. 添加人脸识别

```python
# 使用 face_recognition 库
import face_recognition

def recognize_face(image_data):
    # 人脸识别逻辑
    pass
```

### 3. 实时监控面板

```html
<!-- 添加 WebSocket 支持 -->
<script>
    const ws = new WebSocket('ws://localhost:8888/ws');
    ws.onmessage = (event) => {
        // 实时更新数据
    };
</script>
```

### 4. 数据导出

```python
# 导出为 CSV/Excel
import pandas as pd

def export_records(format='csv'):
    records = db.get_alert_records()
    df = pd.DataFrame(records)
    df.to_csv('records.csv', index=False)
```

## 📞 支持

如有问题，请：
1. 查看后端日志
2. 检查浏览器控制台错误
3. 访问 API 文档：http://localhost:8888/docs

## 📄 许可证

MIT License

---

**版本**：1.0.0  
**最后更新**：2024-01-01  
**作者**：AI 系统架构师
