# X 光识别快速参考

## 🎯 系统状态

✅ **后端服务**：运行在 9527 端口
✅ **前端服务**：运行在 7788 端口
✅ **AI 识别**：通义千问 API（qwen3-vl-plus）
✅ **识别能力**：2000+ 种物品

## 📍 访问地址

- **前端应用**：http://localhost:7788/
- **后端 API**：http://localhost:9527/
- **API 文档**：http://localhost:9527/docs

## 🚀 快速开始

### 1. 启动服务

```bash
# 启动后端（如果未启动）
python backend/main_xray_demo.py

# 启动前端（如果未启动）
npm run dev
```

### 2. 打开前端应用

访问 http://localhost:7788/

### 3. 使用流程

#### 入场安检
1. 点击"入场安检"标签
2. 输入身份证号（如：110101199003151234）
3. 点击"验证身份"
4. 上传 X 光图片（拖拽或点击选择）
5. 查看识别结果

#### 离场安检
1. 点击"离场安检"标签
2. 输入身份证号（必须与入场时相同）
3. 点击"验证身份"
4. 上传 X 光图片
5. 查看比对结果和异常提示

#### 查看数据
1. 点击"数据看板"查看统计信息
2. 点击"异常记录"查看异常物品

## 📸 图片要求

| 要求 | 说明 |
|------|------|
| **最小尺寸** | 10x10 像素 |
| **推荐尺寸** | 800x600 或更大 |
| **格式** | JPEG、PNG |
| **文件大小** | < 10 MB |
| **内容** | X 光扫描图像 |

## 🎯 识别物品示例

系统可以识别以下物品：

### 电子产品
- 手机、笔记本电脑、平板电脑
- 充电宝、充电器、数据线
- 耳机、相机、智能手表

### 个人物品
- 背包、钱包、钥匙
- 手表、眼镜、皮带

### 衣服鞋帽
- T恤、衬衫、裤子
- 运动鞋、皮鞋、靴子

### 文具用品
- 笔、笔记本、橡皮
- 尺子、剪刀、胶水

### 其他物品
- 水杯、书籍、雨伞
- 手帕、纸巾、打火机

## 🔍 识别结果说明

### 识别信息
```json
{
  "name": "笔记本电脑",           // 物品名称
  "category": "电子产品",          // 物品类别
  "quantity": 1,                   // 数量
  "weight": 1.5,                   // 重量（kg）
  "confidence": 85                 // 置信度（0-100）
}
```

### 置信度说明
- **90-100**：非常确定
- **70-89**：较确定
- **50-69**：可能
- **< 50**：不确定

## ⚠️ 常见问题

### Q1: 识别失败怎么办？
**A**：
1. 检查图片尺寸是否 >= 10x10 像素
2. 检查图片格式是否为 JPEG 或 PNG
3. 检查网络连接是否正常
4. 查看后端日志获取详细错误信息

### Q2: 为什么识别结果是模拟数据？
**A**：
1. 图片尺寸太小（< 10x10）
2. API 调用失败，系统自动降级
3. 检查 API Key 是否正确配置

### Q3: 离场安检提示异常怎么办？
**A**：
1. 检查入场和离场的身份证号是否相同
2. 查看异常记录了解具体异常内容
3. 可能是物品数量或类型不匹配

### Q4: 如何查看 API 文档？
**A**：访问 http://localhost:9527/docs

## 🧪 测试识别功能

运行测试脚本验证系统是否正常：

```bash
python test_xray_recognition.py
```

预期输出：
```
✅ 通过 - 身份验证
✅ 通过 - 入场识别
✅ 通过 - 统计数据

总体：3/3 测试通过
🎉 所有测试通过！系统正常运行。
```

## 📊 API 端点

### 身份验证
```
POST /api/verify-identity
参数：idCard (身份证号)
返回：userId, status
```

### 入场识别
```
POST /api/entry
参数：image (图片), user_id, channel_no
返回：record_id, items, total_count, total_weight
```

### 离场识别
```
POST /api/exit
参数：image (图片), user_id, channel_no
返回：record_id, items, comparison_status, anomalies
```

### 获取统计
```
GET /api/statistics
返回：total_entry, total_exit, total_alerts, current_inside
```

### 获取异常
```
GET /api/anomalies
参数：user_id (可选), limit
返回：anomalies 列表
```

## 🔧 故障排查

### 后端无法启动
```bash
# 检查端口是否被占用
netstat -ano | findstr :9527

# 如果被占用，修改 backend/main_xray_demo.py 中的端口
uvicorn.run(app, host="0.0.0.0", port=9527)
```

### 前端无法启动
```bash
# 检查依赖是否安装
npm install

# 检查端口是否被占用
netstat -ano | findstr :7788

# 如果被占用，修改 vite.config.js 中的端口
port: 7788
```

### API 连接失败
```bash
# 检查后端是否运行
curl http://localhost:9527/

# 检查前端代理配置
# vite.config.js 中的 proxy 应该指向 http://localhost:9527
```

## 📝 日志位置

- **后端日志**：控制台输出
- **数据库**：security_system.db
- **上传图片**：uploads/ 目录

## 🎓 学习资源

- **Prompt 优化**：backend/app/prompts/security_check.py
- **AI 识别**：backend/app/services/ai_detector.py
- **数据比对**：backend/app/services/compare.py
- **前端代码**：src/views/

## 💡 提示

1. **首次使用**：建议先运行测试脚本验证系统
2. **图片质量**：清晰的 X 光图片识别效果更好
3. **批量测试**：可以上传多张图片进行测试
4. **数据导出**：所有数据保存在 security_system.db 中

## 📞 支持

如有问题，请：
1. 查看后端日志获取错误信息
2. 查看 API 文档了解接口详情
3. 运行测试脚本验证系统状态

---

**最后更新**：2026-03-13
**版本**：1.0.0
**状态**：✅ 生产就绪
