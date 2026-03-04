# GitHub CLI 登录指南

## 📋 当前状态
- ✅ GitHub CLI 已安装（版本 2.87.3）
- ❌ 尚未登录 GitHub 账户

## 🔐 登录步骤

### 步骤 1：启动登录流程
在 PowerShell 中执行以下命令：

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth login
```

### 步骤 2：选择 GitHub 主机
系统会询问你要登录的 GitHub 主机，选择：
```
? What is your preferred protocol for Git operations?
> HTTPS
  SSH
```

选择 **HTTPS**（推荐）

### 步骤 3：选择认证方式
系统会询问如何进行身份验证：
```
? How would you like to authenticate GitHub CLI?
> Login with a web browser
  Paste an authentication token
```

选择 **Login with a web browser**（使用网页浏览器登录）

### 步骤 4：浏览器授权
- 系统会打开浏览器
- 访问 GitHub 授权页面
- 点击 **Authorize github** 按钮
- 输入你的 GitHub 密码（如果需要）
- 完成授权

### 步骤 5：确认登录
返回 PowerShell，系统会显示：
```
✓ Authentication complete. You're logged in as <your-username>
```

## ✅ 验证登录

登录完成后，执行以下命令验证：

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth status
```

应该看到类似的输出：
```
github.com
  ✓ Logged in to github.com as <your-username>
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: gho_****...
  ✓ Token scopes: gist, read:org, repo, workflow
```

## 🚀 登录后的操作

登录完成后，可以执行以下命令来修改仓库名称：

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" repo rename 智能安检门 --repo 6999-web/-
```

## 📝 常用 GitHub CLI 命令

```powershell
# 查看认证状态
& "C:\Program Files\GitHub CLI\gh.exe" auth status

# 登出
& "C:\Program Files\GitHub CLI\gh.exe" auth logout

# 查看仓库信息
& "C:\Program Files\GitHub CLI\gh.exe" repo view

# 列出仓库
& "C:\Program Files\GitHub CLI\gh.exe" repo list

# 创建仓库
& "C:\Program Files\GitHub CLI\gh.exe" repo create <name>

# 删除仓库
& "C:\Program Files\GitHub CLI\gh.exe" repo delete <repo>
```

## 🔒 安全提示

1. **Token 安全**
   - GitHub CLI 会安全地存储你的认证令牌
   - 不要在命令行中暴露 token

2. **权限范围**
   - 登录时会请求必要的权限
   - 只授予需要的权限

3. **登出**
   - 在公共电脑上使用后，记得登出：
   ```powershell
   & "C:\Program Files\GitHub CLI\gh.exe" auth logout
   ```

## 🎯 下一步

1. 执行 `gh auth login` 命令
2. 按照浏览器提示完成授权
3. 返回 PowerShell 确认登录成功
4. 执行改名命令

---

**准备好了吗？** 请执行登录命令，然后告诉我登录是否成功！
