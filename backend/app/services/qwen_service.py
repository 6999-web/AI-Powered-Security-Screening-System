"""
通义千问视觉模型服务
"""
from openai import OpenAI
import os
import json
import base64
from typing import List, Dict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts.security_check import get_security_check_prompt


class QwenVisionService:
    """通义千问视觉识别服务"""
    
    def __init__(self):
        """初始化服务"""
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model = os.getenv("QWEN_MODEL", "qwen3-vl-plus")
        self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def recognize_items(self, image_data: bytes) -> List[Dict]:
        """
        识别图片中的物品
        
        Args:
            image_data: 图片二进制数据
            
        Returns:
            识别结果列表，格式：[{"name": "物品名", "category": "类别", "quantity": 1, "weight": 0.5}]
        """
        try:
            # 1. 转换为 base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 2. 构建请求消息
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": get_security_check_prompt()
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }]
            
            # 3. 调用 API
            print(f"正在调用通义千问 API，模型：{self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1  # 降低随机性，提高稳定性
            )
            
            # 4. 解析响应
            content = response.choices[0].message.content
            print(f"API 响应：{content}")
            
            items = self._parse_response(content)
            return items
            
        except Exception as e:
            print(f"识别失败：{str(e)}")
            raise Exception(f"AI 识别失败：{str(e)}")
    
    def _parse_response(self, content: str) -> List[Dict]:
        """
        解析 API 响应，提取 JSON 数据
        
        Args:
            content: API 返回的文本内容
            
        Returns:
            解析后的物品列表
        """
        try:
            # 尝试直接解析
            items = json.loads(content)
            if isinstance(items, list):
                return items
        except:
            pass
        
        # 尝试提取 JSON 部分
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                items = json.loads(json_str)
                return items
        except Exception as e:
            print(f"JSON 解析失败：{str(e)}")
        
        # 如果都失败，返回空列表
        return []


# 测试代码
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test():
        service = QwenVisionService()
        
        # 测试图片（需要替换为实际图片路径）
        with open("test_image.jpg", "rb") as f:
            image_data = f.read()
        
        items = await service.recognize_items(image_data)
        print("识别结果：")
        for item in items:
            print(f"  - {item['name']} ({item['category']}) x{item['quantity']}")
    
    asyncio.run(test())
