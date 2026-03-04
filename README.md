# 🔐 智能安检系统

基于 AI 视觉识别的智能安检系统，支持入场安检、离场比对和异常检测。

## ✨ 功能特点

- 🤖 **AI 智能识别** - 使用通义千问 VL Plus 模型识别物品
- 📷 **摄像头实时拍照** - 支持浏览器调用摄像头实时拍照
- 🔍 **智能比对** - 自动比对入场和离场物品，检测异常
- 📊 **数据可视化** - 实时统计数据看板
- ⚠️ **异常检测** - 自动检测多带、缺失、数量异常等情况
- 🎨 **现代化界面** - 基于 Vue 3 + Element Plus 的美观界面

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- 阿里云通义千问 API Key

### 安装依赖

#### 后端

```bash
cd backend
pip install -r requirements.txt
```

#### 前端

```bash
npm install
```

### 配置 API Key

编辑 `backend/.env` 文件：

```env
DASHSCOPE_API_KEY=your_api_key_here
QWEN_MODEL=qwen3-vl-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 启动服务

#### 启动后端

```bash
cd backend
python main.py
```

后端服务将运行在 http://localhost:8888

#### 启动前端

```bash
npm run dev
```

前端服务将运行在 http://localhost:5173

### 或使用一键启动脚本

Windows 用户可以直接运行：

```bash
启动系统.bat
```

## 📖 使用指南

### 入场安检

1. 访问 http://localhost:5173
2. 点击"入场安检"
3. 输入身份证号（18位）
4. 点击"验证身份"
5. 点击摄像头区域调用摄像头
6. 拍照识别物品
7. 确认入场

### 离场安检

1. 点击"离场安检"
2. 输入**相同的**身份证号
3. 点击"验证身份"
4. 查看入场记录
5. 点击摄像头区域
6. 拍照识别离场物品
7. 查看比对结果

### 数据看板

- 实时显示今日入场、离场、异常数据
- 显示当前在场人数
- 显示最近安检记录
- 显示通道使用情况

### 异常记录

- 查看所有异常记录
- 支持按用户ID、类型筛选
- 支持分页查询

## 🛠️ 技术栈

### 后端

- **FastAPI** - 现代化的 Python Web 框架
- **Uvicorn** - ASGI 服务器
- **OpenAI SDK** - 调用通义千问 API
- **Pillow** - 图像处理
- **Python-dotenv** - 环境变量管理

### 前端

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 组件库
- **Axios** - HTTP 客户端

### AI 模型

- **通义千问 VL Plus** - 阿里云视觉语言模型
- 支持图像识别、物品分类、数量统计

## 📁 项目结构

```
智能安检系统/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── config/         # 配置文件
│   │   ├── prompts/        # AI Prompt 模板
│   │   └── services/       # 服务层
│   ├── main.py             # 主程序
│   ├── requirements.txt    # Python 依赖
│   └── .env               # 环境变量
├── src/                    # 前端代码
│   ├── api/               # API 接口
│   ├── router/            # 路由配置
│   ├── views/             # 页面组件
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── public/                # 静态资源
├── index.html             # HTML 模板
├── vite.config.js         # Vite 配置
├── package.json           # Node 依赖
└── README.md              # 项目说明

```

## 🔧 配置说明

### 后端配置 (backend/.env)

```env
# API 配置
DASHSCOPE_API_KEY=your_api_key_here
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

### 前端配置 (vite.config.js)

```javascript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8888',
        changeOrigin: true
      }
    }
  }
})
```

## 📊 API 文档

启动后端服务后，访问：http://localhost:8888/docs

查看完整的 API 文档（自动生成）。

### 主要接口

- `POST /api/verify-identity` - 身份验证
- `POST /api/checkin` - 入场安检
- `POST /api/checkout` - 离场安检
- `GET /api/compare/{userId}` - 获取入场记录
- `GET /api/statistics` - 获取统计数据
- `GET /api/anomalies` - 获取异常记录

## 🎯 功能说明

### AI 识别能力

系统可以识别以下物品类别：

- **电子产品**：笔记本电脑、手机、平板、充电宝、耳机等
- **个人物品**：钱包、钥匙、手表、眼镜、包等
- **文具用品**：笔、本子、文件夹、计算器等
- **食品饮料**：水杯、食物、饮料等
- **其他物品**：书籍、玩具、化妆品等

### 异常检测

- **多带物品**：离场时发现入场记录中不存在的物品
- **缺失物品**：入场物品在离场时未检测到
- **数量异常**：物品数量不一致

## 🐛 故障排查

### 摄像头无法启动

1. 检查是否有其他程序占用摄像头（微信、QQ、钉钉等）
2. 检查浏览器权限设置
3. 尝试刷新浏览器（Ctrl + Shift + R）

### API 调用失败

1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看后端日志

### 404 错误

1. 确认后端服务已启动
2. 清除浏览器缓存
3. 检查代理配置

## 📝 注意事项

1. **API Key 安全**：不要将 API Key 提交到公共仓库
2. **数据持久化**：当前数据存储在内存中，重启后端会清空
3. **浏览器兼容性**：推荐使用 Chrome、Edge、Firefox
4. **摄像头权限**：首次使用需要允许浏览器访问摄像头

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

智能安检系统开发团队

## 🙏 致谢

- 阿里云通义千问团队
- Vue.js 团队
- FastAPI 团队
- Element Plus 团队

---

**最后更新：** 2026-03-02  
**版本：** v1.0.0
