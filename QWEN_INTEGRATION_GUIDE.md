# 通义千问视觉模型集成指南

## 📋 项目概述

本指南将帮助你将阿里云通义千问视觉模型（Qwen-VL）集成到智能安检系统中，实现高精度的物品识别功能。

## 🎯 集成方案总览

### 方案特点

✅ **兼容 OpenAI 接口** - 使用 OpenAI SDK 即可调用  
✅ **国内访问稳定** - 阿里云服务，低延迟  
✅ **中文识别优秀** - 针对中文场景优化  
✅ **成本可控** - 按 token 计费，支持缓存  
✅ **多模型可选** - Plus/Max/3.0 版本可选

### 推荐模型

| 模型 | 特点 | 适用场景 | 价格 |
|------|------|----------|------|
| **qwen3-vl-plus** ⭐ | 最新版本，性价比高 | 日常安检 | ¥0.01/千tokens |
| qwen-vl-max | 识别精度最高 | 高安全场景 | ¥0.02/千tokens |
| qwen-vl-plus | 标准版本 | 一般场景 | ¥0.008/千tokens |

**推荐使用：qwen3-vl-plus**

## 🚀 快速开始

### 步骤 1：获取 API Key

1. 访问 [阿里云百炼平台](https://help.aliyun.com/zh/model-studio/get-api-key)
2. 注册/登录账号
3. 创建 API Key
4. 复制保存 API Key（格式：`sk-xxxxxx`）

### 步骤 2：配置环境变量

创建 `backend/.env` 文件：

```bash
# 阿里云 API 配置
DASHSCOPE_API_KEY=sk-your-api-key-here

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

### 步骤 3：安装依赖

```bash
cd backend
pip install openai python-dotenv pillow
```

### 步骤 4：测试 API 连接

创建测试脚本 `backend/test_qwen.py`：

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 测试调用
response = client.chat.completions.create(
    model="qwen3-vl-plus",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "这是什么？"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
                }
            }
        ]
    }]
)

print(response.choices[0].message.content)
```

运行测试：

```bash
python test_qwen.py
```

如果看到识别结果，说明配置成功！

## 📁 项目结构

```
backend/
├── .env                          # 环境变量配置
├── requirements.txt              # Python 依赖
├── main.py                       # 主程序
├── app/
│   ├── config/
│   │   └── settings.py          # 配置管理
│   ├── services/
│   │   ├── qwen_service.py      # Qwen API 封装 ⭐
│   │   ├── image_processor.py   # 图片处理
│   │   └── cache_service.py     # 缓存服务
│   ├── schemas/
│   │   └── recognition.py       # 数据模型
│   ├── utils/
│   │   └── logger.py            # 日志工具
│   └── prompts/
│       └── security_check.py    # Prompt 模板 ⭐
└── tests/
    └── test_qwen_service.py     # 单元测试
```

## 🔧 核心代码实现

### 1. Qwen 服务封装

`backend/app/services/qwen_service.py`：

```python
from openai import OpenAI
import os
import json
from typing import List
import base64

class QwenVisionService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("QWEN_BASE_URL")
        )
        self.model = os.getenv("QWEN_MODEL", "qwen3-vl-plus")
    
    async def recognize_items(self, image_data: bytes) -> List[dict]:
        """识别图片中的物品"""
        
        # 转换为 base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # 构建请求
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": self._get_prompt()
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }]
        
        # 调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1  # 降低随机性，提高稳定性
        )
        
        # 解析结果
        content = response.choices[0].message.content
        items = self._parse_response(content)
        
        return items
    
    def _get_prompt(self) -> str:
        """获取 Prompt 模板"""
        return """
请识别图片中的所有物品，返回 JSON 数组格式：
[
  {
    "name": "物品名称（中文）",
    "category": "物品类别（电子产品/个人物品/文具用品/食品饮料/其他）",
    "quantity": 数量（整数）,
    "weight": 估计重量（kg，浮点数，无法判断则为0）
  }
]

要求：
1. 只返回 JSON 数组，不要其他文字
2. 相同物品合并统计数量
3. 如果没有物品，返回 []
"""
    
    def _parse_response(self, content: str) -> List[dict]:
        """解析 API 响应"""
        try:
            # 提取 JSON 部分
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                items = json.loads(json_str)
                return items
            return []
        except Exception as e:
            print(f"解析错误: {e}")
            return []
```

### 2. 更新入场安检接口

`backend/main.py`：

```python
from app.services.qwen_service import QwenVisionService

qwen_service = QwenVisionService()

@app.post("/api/checkin")
async def checkin(
    image: UploadFile = File(...),
    userId: str = Form(...),
    weight: float = Form(0),
    channelNo: int = Form(1)
):
    """入场安检 - 使用 Qwen-VL 识别"""
    
    # 读取图片
    image_data = await image.read()
    
    # 调用 Qwen 识别
    items = await qwen_service.recognize_items(image_data)
    
    # 计算统计信息
    total_count = sum(item["quantity"] for item in items)
    total_weight = weight if weight > 0 else sum(item.get("weight", 0) for item in items)
    
    # 保存记录
    security_records[userId] = {
        "type": "entry",
        "items": items,
        "totalCount": total_count,
        "totalWeight": total_weight,
        "checkTime": datetime.now().isoformat(),
        "channelNo": channelNo
    }
    
    return {
        "userId": userId,
        "items": items,
        "totalCount": total_count,
        "totalWeight": total_weight,
        "checkTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "channelNo": channelNo
    }
```

## 💡 Prompt 优化技巧

### 基础 Prompt（当前使用）

```python
BASIC_PROMPT = """
请识别图片中的所有物品，返回 JSON 数组格式：
[{"name": "物品名", "category": "类别", "quantity": 数量}]
"""
```

### 优化 Prompt（推荐）

```python
OPTIMIZED_PROMPT = """
你是专业的安检物品识别助手。请仔细分析图片中的所有物品。

**识别要求：**
1. 识别所有可见物品
2. 提供准确的中文名称
3. 合并相同物品的数量

**物品类别：**
- 电子产品：手机、电脑、平板、充电宝等
- 个人物品：钱包、钥匙、手表、包等
- 文具用品：笔、本子、文件夹等
- 食品饮料：水杯、食物、饮料等
- 其他：无法归类的物品

**输出格式（严格遵守）：**
[
  {
    "name": "物品名称",
    "category": "物品类别",
    "quantity": 数量,
    "weight": 重量（kg，无法判断则为0）
  }
]

注意：只返回 JSON 数组，不要其他文字。
"""
```

### 提高准确率的技巧

1. **明确输出格式** - 要求严格的 JSON 格式
2. **提供示例** - 在 Prompt 中给出示例
3. **降低 temperature** - 设置为 0.1-0.3
4. **分类明确** - 提供清晰的类别定义
5. **多次测试** - 用不同图片测试优化

## 📊 成本估算

### 使用场景

假设每天 200 次安检：

```
每次识别消耗：
- 图片 tokens: ~1500
- 文本 tokens: ~500
- 总计: ~2000 tokens

每天成本：
200 次 × 2000 tokens = 400,000 tokens
400 × 0.01 元 = 4 元/天

每月成本：
4 元 × 30 天 = 120 元/月
```

### 成本优化建议

1. **启用缓存** - 相同图片不重复识别（节省 30-50%）
2. **压缩图片** - 减小图片尺寸降低 tokens
3. **简化 Prompt** - 减少不必要的文字
4. **批量处理** - 合并多个请求（如果支持）

## 🔍 测试和验证

### 功能测试

```bash
# 测试单个物品识别
curl -X POST http://localhost:8888/api/checkin \
  -F "image=@test_images/laptop.jpg" \
  -F "userId=TEST_001" \
  -F "weight=1.5" \
  -F "channelNo=1"

# 测试多个物品识别
curl -X POST http://localhost:8888/api/checkin \
  -F "image=@test_images/multiple_items.jpg" \
  -F "userId=TEST_002" \
  -F "weight=3.0" \
  -F "channelNo=1"
```

### 准确率测试

准备测试数据集：
- 10 张单物品图片
- 10 张多物品图片
- 5 张边界情况图片（模糊、遮挡等）

记录识别结果，计算准确率。

## 🐛 常见问题

### 1. API Key 无效

**错误：** `invalid_api_key`

**解决：**
- 检查 `.env` 文件中的 API Key 是否正确
- 确认 API Key 已激活
- 检查是否有余额

### 2. 网络超时

**错误：** `Request timeout`

**解决：**
- 增加 `REQUEST_TIMEOUT` 配置
- 检查网络连接
- 使用国内服务器

### 3. 识别结果不准确

**解决：**
- 优化 Prompt 模板
- 降低 temperature 参数
- 使用更高级的模型（qwen-vl-max）
- 提高图片质量

### 4. JSON 解析失败

**错误：** `JSONDecodeError`

**解决：**
- 在 Prompt 中强调 JSON 格式
- 添加更严格的解析逻辑
- 使用正则表达式提取 JSON

## 📚 参考资料

- [通义千问 API 文档](https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-by-calling-api)
- [OpenAI 兼容接口说明](https://help.aliyun.com/zh/model-studio/qwen-vl-compatible-with-openai)
- [获取 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
- [Qwen-VL GitHub](https://github.com/QwenLM/Qwen-VL)

## 🎉 下一步

完成基础集成后，可以：

1. ✅ 实现缓存机制降低成本
2. ✅ 添加监控和日志
3. ✅ 优化 Prompt 提高准确率
4. ✅ 实现批量识别
5. ✅ 添加人工复核流程

## 📞 技术支持

如有问题，可以：
- 查看阿里云百炼文档
- 提交工单到阿里云
- 参考 GitHub Issues

---

**祝你集成顺利！🚀**
