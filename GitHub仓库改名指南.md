# GitHub 仓库改名指南

## 📝 任务
将仓库名称从 `-` 改为 `智能安检门`

## 🔧 修改步骤

### 方法一：通过 GitHub 网页界面（推荐）

#### 步骤 1：访问仓库设置
1. 打开浏览器，访问：https://github.com/6999-web/-
2. 点击仓库页面右上角的 **Settings**（设置）按钮

#### 步骤 2：修改仓库名称
1. 在左侧菜单中找到 **General**（常规）选项
2. 在页面顶部找到 **Repository name**（仓库名称）字段
3. 将当前名称 `-` 改为 `智能安检门`
4. 点击 **Rename** 按钮确认

#### 步骤 3：更新本地配置
修改完成后，GitHub 会自动重定向旧 URL。但为了保持本地仓库同步，需要更新本地的远程 URL：

```bash
git remote set-url origin https://github.com/6999-web/智能安检门.git
```

验证更新：
```bash
git remote -v
```

应该看到：
```
origin  https://github.com/6999-web/智能安检门.git (fetch)
origin  https://github.com/6999-web/智能安检门.git (push)
```

### 方法二：通过 GitHub CLI（如果已安装）

```bash
# 登录 GitHub
gh auth login

# 重命名仓库
gh repo rename 智能安检门 --repo 6999-web/-
```

## ✅ 验证修改

修改完成后，验证以下内容：

1. **访问新 URL**
   - 打开：https://github.com/6999-web/智能安检门
   - 应该能正常访问仓库

2. **旧 URL 重定向**
   - 访问旧 URL：https://github.com/6999-web/-
   - 应该自动重定向到新 URL

3. **本地仓库同步**
   ```bash
   git remote -v
   # 确认 origin URL 已更新
   ```

## 📌 重要提示

1. **自动重定向**
   - GitHub 会自动将旧 URL 重定向到新 URL（通常持续 1 年）
   - 但建议立即更新本地配置

2. **CI/CD 配置**
   - 如果使用了 GitHub Actions，可能需要更新工作流文件中的仓库 URL

3. **第三方集成**
   - 如果有其他服务集成了此仓库，需要更新相应的 URL 配置

4. **文档更新**
   - 更新项目文档中的仓库 URL 引用

## 🔄 更新本地配置后的操作

修改完本地远程 URL 后，可以继续正常使用 Git：

```bash
# 拉取最新代码
git pull origin main

# 推送代码
git push origin main

# 查看日志
git log --oneline
```

## 📚 相关命令参考

```bash
# 查看当前远程配置
git remote -v

# 修改远程 URL
git remote set-url origin <新URL>

# 添加新的远程仓库
git remote add <名称> <URL>

# 删除远程仓库
git remote remove <名称>

# 重命名远程仓库别名
git remote rename <旧名称> <新名称>
```

## 🎉 完成

仓库名称修改完成后，新的仓库地址为：
```
https://github.com/6999-web/智能安检门
```

所有功能和代码保持不变，只是仓库名称更新了。

---

**更新时间**：2026-03-04  
**状态**：✅ 指南完成
