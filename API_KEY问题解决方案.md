# 🔑 API Key 问题解决方案

## 问题诊断

✅ **后端服务运行正常** - 端口 8888  
✅ **前端服务运行正常** - 端口 5173  
✅ **所有 API 端点正常** - 无 404 错误  
❌ **API Key 无效** - 401 错误

## 错误信息

```
Error code: 401 - Incorrect API key provided
```

这意味着您提供的 API Key (`sk-88ed49180e7d4462b16b8f2902f63c7a`) 无效或已过期。

## 解决方案

### 方案 1：获取新的 API Key（推荐）

#### 步骤 1：访问阿里云控制台

打开浏览器，访问：
```
https://dashscope.console.aliyun.com/apiKey
```

#### 步骤 2：登录阿里云账号

- 如果没有账号，需要先注册
- 登录后进入 DashScope 控制台

#### 步骤 3：创建 API Key

1. 点击"创建新的 API Key"按钮
2. 复制生成的 API Key（格式：sk-xxxxxxxxxxxxxxxx）
3. 保存好这个 API Key（只显示一次）

#### 步骤 4：更新 .env 文件

编辑 `backend/.env` 文件，替换 API Key：

```env
# 阿里云通义千问 API 配置
DASHSCOPE_API_KEY=sk-你的新API_Key

# 模型配置
QWEN_MODEL=qwen3-vl-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 图片配置
MAX_IMAGE_SIZE_MB=10

# 缓存配置
ENABLE_CACHE=true
CACHE_TTL=3600

# 请求配置
MAX_RETRIES=3
REQUEST_TIMEOUT=30
```

#### 步骤 5：重启后端服务

1. 找到运行 `python main.py` 的终端
2. 按 `Ctrl + C` 停止服务
3. 重新启动：
   ```bash
   cd backend
   python main.py
   ```

#### 步骤 6：验证 API Key

运行测试脚本：
```bash
cd backend
python test_api_key.py
```

如果看到 "✅ API Key 测试通过！"，说明配置成功。

---

### 方案 2：检查账户余额和额度

#### 步骤 1：访问控制台

```
https://dashscope.console.aliyun.com/
```

#### 步骤 2：检查余额

1. 查看账户余额是否充足
2. 查看 API 调用额度

#### 步骤 3：充值或申请免费额度

- 如果余额不足，需要充值
- 新用户可能有免费额度，需要激活

---

### 方案 3：使用模拟数据（临时方案）

如果暂时无法获取有效的 API Key，可以使用模拟数据进行测试。

#### 修改后端代码

编辑 `backend/main.py`，找到 `checkin` 函数中的这段代码：

```python
# 调用 AI 识别服务
if qwen_service:
    print("正在调用 AI 识别...")
    items = await qwen_service.recognize_items(image_data)
    print(f"识别成功，共 {len(items)} 个物品")
else:
    # 如果 AI 服务未初始化，返回模拟数据
    print("⚠️ AI 服务未初始化，使用模拟数据")
    items = [
        {"name": "笔记本电脑", "category": "电子产品", "quantity": 1, "weight": 1.5},
        {"name": "手机", "category": "电子产品", "quantity": 1, "weight": 0.2},
        {"name": "钱包", "category": "个人物品", "quantity": 1, "weight": 0.1}
    ]
```

将其修改为：

```python
# 临时使用模拟数据（跳过 AI 识别）
print("⚠️ 使用模拟数据进行测试")
items = [
    {"name": "笔记本电脑", "category": "电子产品", "quantity": 1, "weight": 1.5},
    {"name": "手机", "category": "电子产品", "quantity": 1, "weight": 0.2},
    {"name": "钱包", "category": "个人物品", "quantity": 1, "weight": 0.1},
    {"name": "水杯", "category": "个人物品", "quantity": 1, "weight": 0.3}
]
```

这样摄像头拍照后会返回模拟的识别结果，可以测试整个流程。

---

## 验证修复

### 测试 1：API Key 验证

```bash
cd backend
python test_api_key.py
```

预期输出：
```
✅ API Key 测试通过！
```

### 测试 2：摄像头识别测试

```bash
cd backend
python test_camera_recognition.py
```

预期输出：
```
✅ 测试成功！AI识别功能正常工作
```

### 测试 3：浏览器测试

1. 打开浏览器：`http://localhost:5173`
2. 进入"入场安检"页面
3. 完成身份验证
4. 点击摄像头区域
5. 拍照后查看识别结果

---

## 常见问题

### Q1: 如何获取免费的 API Key？

A: 阿里云通义千问提供免费试用额度：
1. 注册阿里云账号
2. 访问 DashScope 控制台
3. 创建 API Key
4. 新用户通常有一定的免费调用额度

### Q2: API Key 的格式是什么？

A: 正确的格式是 `sk-` 开头，后面跟随32位字符，例如：
```
sk-88ed49180e7d4462b16b8f2902f63c7a
```

### Q3: 为什么我的 API Key 无效？

A: 可能的原因：
1. API Key 已过期
2. API Key 被删除或禁用
3. 账户余额不足
4. API Key 复制时有多余的空格或换行

### Q4: 如何检查 API 调用额度？

A: 访问控制台查看：
```
https://dashscope.console.aliyun.com/overview
```

### Q5: 可以使用其他大模型吗？

A: 可以！您可以修改代码使用其他支持视觉识别的模型：
- OpenAI GPT-4 Vision
- Google Gemini Vision
- 百度文心一言
- 讯飞星火

只需修改 `backend/app/services/qwen_service.py` 中的 API 调用部分。

---

## 技术支持

### 阿里云官方文档

- API Key 管理：https://help.aliyun.com/zh/model-studio/get-api-key
- 通义千问 VL 文档：https://help.aliyun.com/zh/model-studio/developer-reference/qwen-vl-compatible-with-openai
- 错误码说明：https://help.aliyun.com/zh/model-studio/error-code

### 联系方式

- 阿里云工单系统
- DashScope 社区论坛

---

## 下一步

修复 API Key 后，您就可以：

1. ✅ 使用摄像头拍照
2. ✅ AI 自动识别物品
3. ✅ 入场安检记录
4. ✅ 离场安检比对
5. ✅ 异常检测和记录

---

**最后更新：** 2026-03-02  
**问题状态：** API Key 无效，需要更新
