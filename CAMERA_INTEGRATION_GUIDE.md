# 摄像头集成实施指南

## 🎯 目标

在现有系统基础上，实现点击按钮调用外接摄像头，拍摄后自动调用通义千问 AI 模型识别物品。

## 📋 前置条件

- ✅ 外接摄像头已连接
- ✅ API Key：`sk-88ed49180e7d4462b16b8f2902f63c7a`
- ✅ 前端界面已完成
- ✅ 后端框架已搭建

## 🚀 快速开始（3 步完成）

### 步骤 1：配置后端 AI 识别服务（30 分钟）

#### 1.1 安装依赖

```bash
cd backend
pip install openai python-dotenv pillow
```

#### 1.2 创建 .env 配置文件

在 `backend/.env` 文件中添加：

```bash
DASHSCOPE_API_KEY=sk-88ed49180e7d4462b16b8f2902f63c7a
QWEN_MODEL=qwen3-vl-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MAX_IMAGE_SIZE_MB=10
ENABLE_CACHE=true
```

#### 1.3 创建目录结构

```bash
cd backend
mkdir -p app/services app/prompts app/config
```

### 步骤 2：实现后端服务（1 小时）

详细代码见下方"核心代码实现"部分。

### 步骤 3：实现前端摄像头调用（1 小时）

详细代码见下方"前端摄像头集成"部分。

## 💻 核心代码实现

### 后端部分

#### 文件 1：`backend/app/prompts/security_check.py`

创建 Prompt 模板文件。

#### 文件 2：`backend/app/services/qwen_service.py`

创建 AI 识别服务。

#### 文件 3：`backend/app/config/settings.py`

创建配置管理。

#### 文件 4：更新 `backend/main.py`

集成 AI 识别服务到现有接口。

### 前端部分

#### 更新 `src/views/CheckIn.vue`

添加摄像头调用功能。

## 🎥 摄像头调用流程

```
用户点击"调用摄像头"按钮
    ↓
请求摄像头权限
    ↓
显示摄像头预览（video 元素）
    ↓
用户点击"拍照"按钮
    ↓
Canvas 截取当前帧
    ↓
转换为 Blob 格式
    ↓
上传到后端 /api/checkin
    ↓
后端转 Base64 调用通义千问 API
    ↓
返回识别结果
    ↓
前端展示识别的物品列表
```

## 🧪 测试步骤

### 1. 测试 API 连接

创建 `backend/test_api.py`：

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen3-vl-plus",
    messages=[{
        "role": "user",
        "content": "你好"
    }]
)

print(response.choices[0].message.content)
```

运行测试：
```bash
python test_api.py
```

### 2. 测试完整流程

1. 启动后端：`python main.py`
2. 启动前端：`npm run dev`
3. 访问：http://localhost:5173
4. 点击"入场安检"
5. 点击"调用摄像头"
6. 拍照并识别

## 📝 注意事项

1. **摄像头权限**：浏览器需要 HTTPS 或 localhost 才能访问摄像头
2. **图片大小**：建议压缩到 1MB 以下，降低 API 成本
3. **识别时间**：通常 2-3 秒，请添加加载提示
4. **错误处理**：网络失败时需要友好提示
5. **成本控制**：建议实现缓存机制

## 🐛 常见问题

### Q1: 摄像头无法调用？
- 检查浏览器权限设置
- 确保使用 localhost 或 HTTPS
- 检查摄像头是否被其他程序占用

### Q2: API 调用失败？
- 检查 API Key 是否正确
- 检查网络连接
- 查看后端日志

### Q3: 识别结果不准确？
- 优化 Prompt 模板
- 提高图片质量
- 调整拍摄角度和光线

## 📚 下一步优化

1. 添加图片压缩功能
2. 实现缓存机制节省成本
3. 优化 Prompt 提高准确率
4. 添加多次拍摄功能
5. 实现离场安检的摄像头调用

---

**预计完成时间：2-3 小时**
**难度等级：⭐⭐⭐ 中等**
