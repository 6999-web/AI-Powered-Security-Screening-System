# 智能安检系统 - 后端 API

基于 FastAPI 的智能安检系统后端服务。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python main.py
```

服务将在 http://localhost:8888 启动

API 文档: http://localhost:8888/docs

## 集成大模型 API

### 方案一：OpenAI GPT-4V

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

async def recognize_items(image_data):
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "请识别图片中的物品，返回JSON格式：[{name, category, quantity, weight}]"
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }]
    )
    
    return parse_response(response)
```

### 方案二：Anthropic Claude 3.5

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

async def recognize_items(image_data):
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                },
                {
                    "type": "text",
                    "text": "请识别图片中的物品，返回JSON格式"
                }
            ]
        }]
    )
    
    return parse_response(message)
```
