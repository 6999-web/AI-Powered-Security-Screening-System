"""
配置管理
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    """系统配置"""
    
    # API 配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3-vl-plus")
    QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # 图片配置
    MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
    
    # 缓存配置
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1小时
    
    # 请求配置
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 未配置")
        
        print("=" * 50)
        print("系统配置：")
        print(f"  API Key: {cls.DASHSCOPE_API_KEY[:10]}...")
        print(f"  模型: {cls.QWEN_MODEL}")
        print(f"  缓存: {'启用' if cls.ENABLE_CACHE else '禁用'}")
        print("=" * 50)


# 创建全局配置实例
settings = Settings()
