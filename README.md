# 🚀 Cloudflare 临时邮箱自动生成工具

一个基于 Cloudflare Email Routing API 的临时邮箱自动生成工具，支持命令行一键创建、管理临时邮箱地址。

## ✨ 核心特性

### 基础功能
- ✅ **零外部依赖** - 仅使用 Python 标准库，无需 `pip install`
- ✅ **无需 CLI 工具** - 直接调用 Cloudflare REST API
- ✅ **无需重复验证** - 使用 API Token 持久化认证
- ✅ **完全自动化** - 命令行一键生成临时邮箱
- ✅ **安全转发** - 邮件自动转发到您的真实邮箱
- ✅ **跨平台支持** - Linux/macOS/Windows (PowerShell/CMD)

### 邮箱生成模式
- 🎲 **纯随机模式** - 生成 8 位纯字母随机邮箱（如 `abcdefgh@domain.com`）
- 🔤 **前缀模式** - 带前缀的随机邮箱（如 `test-abcdefgh@domain.com`）
- 🔢 **编号模式（NEW）** - 固定前缀+数字编号（如 `ul0001@domain.com`、`ul9977@domain.com`）
- 📝 **自定义模式** - 指定完整邮箱地址

### 高级功能
- 📦 **批量创建** - 支持一次创建多个邮箱（连续编号或随机）
- 🔍 **批量删除** - 支持通配符模式批量删除
- 📊 **自动分页** - 支持管理最多 5000 条路由规则
- 💾 **导出功能** - 可将生成的邮箱保存到文件

---

## 📋 前置要求

### 1. 软件环境

| 软件 | 版本要求 | 说明 | 检查方法 |
|------|---------|------|---------|
| **Python** | 3.6+ | 脚本运行环境，**仅需标准库** | `python --version` |

**重要说明**：
- ✅ **无需安装任何 Python 包**（不需要 `pip install` 任何东西）
- ✅ **无需安装 Cloudflare CLI**（工具直接调用 REST API）
- ✅ 所有依赖均为 Python 内置标准库

<details>
<summary><b>📦 Python 安装指南（点击展开）</b></summary>

#### Windows 系统

**方法 1：官方安装包（推荐）**
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载最新的 Python 3.x 版本（例如 3.12.x）
3. 运行安装程序
4. ⚠️ **务必勾选** "Add Python to PATH"
5. 点击 "Install Now"

**方法 2：Microsoft Store**
1. 打开 Microsoft Store
2. 搜索 "Python 3.12"
3. 点击安装

**验证安装**
```cmd
python --version
# 输出: Python 3.12.x
```

#### macOS 系统

**方法 1：Homebrew（推荐）**
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python3
```

**方法 2：官方安装包**
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 macOS 安装包
3. 运行 .pkg 安装程序

**验证安装**
```bash
python3 --version
# 输出: Python 3.x.x
```

#### Linux 系统

**Ubuntu/Debian**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**CentOS/RHEL**
```bash
sudo yum install python3
```

**Fedora**
```bash
sudo dnf install python3
```

**Arch Linux**
```bash
sudo pacman -S python
```

**验证安装**
```bash
python3 --version
# 输出: Python 3.x.x
```

</details>

---

### 2. Cloudflare 账号要求

| 项目 | 说明 |
|------|------|
| **Cloudflare 账号** | 免费账号即可 |
| **域名** | 至少一个已添加到 Cloudflare 的域名 |
| **Email Routing** | 必须启用（免费功能） |
| **验证的邮箱** | 至少一个已验证的转发目标邮箱 |
| **API Token** | 需要创建一个具有 Email Routing 权限的 Token |

**配额限制（重要）：**
- 📊 路由规则：最多 **200 条**
- 📮 目标地址：最多 **200 个**
- 📧 邮件大小：最大 **25 MiB**

---

## 🔧 安装与配置

### 步骤 1：下载工具

```bash
# 克隆仓库
git clone https://github.com/yourusername/cf-cli.git
cd cf-cli
```

或直接下载所有文件到本地目录。

---

### 步骤 2：配置 Cloudflare Email Routing

#### 2.1 启用 Email Routing

1. 访问 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择您的域名
3. 左侧菜单选择 **"Email"** → **"Email Routing"**
4. 点击 **"Get started"** 或 **"Enable Email Routing"**
5. 添加并验证您的转发目标邮箱地址
   - 输入您的真实邮箱（如 `your-email@gmail.com`）
   - 打开邮箱，点击验证链接
6. Cloudflare 会自动配置 MX 记录

#### 2.2 获取 API Token

1. 访问 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens) 拉到最下，选择自定义创建
2. 点击 **"Create Token"**
3. 选择 **"Create Custom Token"**
4. 配置权限：
   ```
   权限设置（Permissions）：
   ├─ Zone（区域）
   │  ├─ Email Routing Rules - Edit
   ├─ account（账户）
   │  └─ Email Routing Addresses - Edit
   └─ Zone Resources、Account Resources、Client IP Address Filtering (一般默认即可)

   ```
5. 点击 **"Continue to summary"** → **"Create Token"**
6. ⚠️ **立即复制并保存 Token**（只显示一次！）

#### 2.3 获取 Zone ID

1. 在 Cloudflare Dashboard 中选择您的域名
2. 滚动到页面右侧，找到 **"API"** 部分
3. 复制 **"Zone ID"**（格式如：`1c9a06ed282ed8eaadee65dd77200a68`）

#### 2.4 获取 Account ID（可选）

1. 在 Cloudflare Dashboard 主页
2. 右侧找到 **"Account ID"**
3. 点击复制

---

### 步骤 3：配置环境变量

#### 3.1 创建 `.env` 文件

```bash
# Linux/macOS
cp .env.example .env

# Windows (PowerShell)
copy .env.example .env

# Windows (CMD)
copy .env.example .env
```

#### 3.2 编辑 `.env` 文件

用文本编辑器打开 `.env` 文件，填写以下信息：

```bash
# Cloudflare API Configuration
CLOUDFLARE_API_TOKEN=your_api_token_here          # 步骤 2.2 获取的 Token
CLOUDFLARE_ZONE_ID=your_zone_id_here              # 步骤 2.3 获取的 Zone ID
CLOUDFLARE_ACCOUNT_ID=your_account_id_here        # 步骤 2.4 获取的 Account ID（可选）

# 邮件转发目标地址（必须已在 Email Routing 中验证）
FORWARD_TO_EMAIL=your-real-email@example.com      # 您的真实邮箱

# 临时邮箱域名（使用您在 Cloudflare 中管理的域名）
EMAIL_DOMAIN=yourdomain.com                       # 您的域名

# 可选：临时邮箱前缀（默认不使用前缀）
#EMAIL_PREFIX=temp
```

**配置示例**：
```bash
CLOUDFLARE_API_TOKEN=A-JgYzgaYHtpEuKnvKnKi5bcKZ16i1uCl-1QBYGW
CLOUDFLARE_ZONE_ID=1c9a06ed282ed8eaadee65dd77200a68
CLOUDFLARE_ACCOUNT_ID=8bad9a137f7e5a53a9234e8bdc5032d9
FORWARD_TO_EMAIL=203320879@qq.com
EMAIL_DOMAIN=ktwi.online
```

---

## 🎯 使用方法

> 下面将分四种模式展示使用方法：编号模式（NEW）、随机模式、批量操作、管理操作

### 📌 编号模式（NEW - 推荐用于固定邮箱）

生成固定前缀+数字编号的邮箱，适合需要可预测邮箱地址的场景。

#### Windows (PowerShell)
```powershell
# 创建单个编号邮箱: ul0001@domain.com
.\temp-email.ps1 create --prefix ul --number 1

# 创建指定编号: ul9977@domain.com
.\temp-email.ps1 create --prefix ul --number 9977

# 批量创建连续编号: ul0001 到 ul0010
.\temp-email.ps1 create --prefix ul --start 1 --count 10

# 自定义编号位数（3位）: ul001 到 ul010
.\temp-email.ps1 create --prefix ul --start 1 --count 10 --digits 3
```

#### Linux/macOS
```bash
# 创建单个编号邮箱
./temp-email.sh create --prefix ul --number 1

# 批量创建连续编号
./temp-email.sh create --prefix ul --start 1 --count 10
```

#### Windows (CMD)
```cmd
REM 创建编号邮箱
temp-email.bat create --prefix ul --number 1

REM 批量创建连续编号
temp-email.bat create --prefix ul --start 1 --count 10
```

---

### 🎲 随机模式（默认）

生成完全随机的临时邮箱地址。

#### Windows (PowerShell)
```powershell
# 创建纯随机邮箱: abcdefgh@domain.com
.\temp-email.ps1 create

# 创建带前缀的随机邮箱: test-abcdefgh@domain.com
.\temp-email.ps1 create --prefix test

# 创建自定义邮箱
.\temp-email.ps1 create --email my-custom-name
```

#### Linux/macOS
```bash
# 创建随机邮箱
./temp-email.sh create

# 创建带前缀的邮箱
./temp-email.sh create --prefix test
```

---

### 📦 批量操作

#### 批量创建
```powershell
# 批量创建 10 个随机邮箱
.\temp-email.ps1 create --count 10

# 批量创建并指定转发目标
.\temp-email.ps1 create --count 10 --to your-email@qq.com

# 批量创建并保存到文件
.\temp-email.ps1 create --count 50 --output-dir ./out
```

---

### 🗂️ 管理操作

#### 列出所有邮箱
```powershell
# 列出所有邮箱
.\temp-email.ps1 list

# 详细模式（显示分页信息）
.\temp-email.ps1 list -v
```

#### 删除邮箱
```powershell
# 删除单个邮箱
.\temp-email.ps1 delete abcdefgh@domain.com

# 删除单个邮箱（跳过确认）
.\temp-email.ps1 delete abcdefgh@domain.com -y

# 批量删除：所有 ul 开头+4位数字的邮箱
.\temp-email.ps1 delete --batch 'ul[0-9][0-9][0-9][0-9]'

# 批量删除：所有 u 开头的邮箱
.\temp-email.ps1 delete --batch 'u*'

# 批量删除并跳过确认
.\temp-email.ps1 delete --batch 'test*' -y
```

#### 清理所有邮箱
```powershell
# 清理所有邮箱（会提示确认）
.\temp-email.ps1 cleanup

# 清理所有邮箱（跳过确认）
.\temp-email.ps1 cleanup -y
```

---

## 📖 命令详解

### `create` - 创建临时邮箱

创建新的临时邮箱地址，并自动配置邮件转发规则。

**所有选项：**

| 选项 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `--prefix TEXT` | 字符串 | 邮箱前缀（随机模式或编号模式） | `--prefix ul` |
| `--number N` | 整数 | 指定编号（需配合 prefix） | `--number 1` |
| `--start N` | 整数 | 批量创建时的起始编号 | `--start 1` |
| `--digits N` | 整数 | 编号位数（默认4） | `--digits 3` |
| `--count N` | 整数 | 批量创建数量（默认1） | `--count 10` |
| `--to EMAIL` | 字符串 | 指定转发目标邮箱 | `--to your@qq.com` |
| `--email TEXT` | 字符串 | 指定完整邮箱地址 | `--email custom` |
| `--description TEXT` | 字符串 | 添加规则描述 | `--description "测试"` |
| `--output-dir PATH` | 路径 | 将结果写入文件 | `--output-dir ./out` |
| `--no-prefix` | 标志 | 不使用前缀 | `--no-prefix` |

**邮箱生成格式对照表：**

| 命令 | 生成格式 | 示例 |
|------|---------|------|
| `create` | `xxxxxxxx@domain.com` | `abcdefgh@domain.com` |
| `create --prefix test` | `test-xxxxxxxx@domain.com` | `test-abcdefgh@domain.com` |
| `create --prefix ul --number 1` | `ul0001@domain.com` | `ul0001@domain.com` |
| `create --prefix ul --number 9977` | `ul9977@domain.com` | `ul9977@domain.com` |
| `create --email custom` | `custom@domain.com` | `custom@domain.com` |

**使用示例：**

```bash
# 编号模式示例
create --prefix ul --number 1                    # ul0001@domain.com
create --prefix ul --start 1 --count 10          # ul0001 到 ul0010
create --prefix test --number 123 --digits 5     # test00123@domain.com

# 随机模式示例
create                                            # abcdefgh@domain.com
create --prefix test                              # test-abcdefgh@domain.com
create --count 10                                 # 10个随机邮箱

# 自定义模式示例
create --email my-custom-name                     # my-custom-name@domain.com
```

---

### `list` - 列出所有邮箱

显示当前所有配置的邮件路由规则。**支持自动分页，可获取所有邮箱**（最多 5000 条）。

**选项：**
- `-v, --verbose` - 显示详细的分页调试信息

**示例：**
```bash
# 列出所有邮箱
list

# 详细模式：显示分页过程
list -v
```

**示例输出：**
```
📋 正在获取所有邮件路由规则...

找到 3 条路由规则:

序号 邮箱地址                                   规则ID               状态     创建时间
----------------------------------------------------------------------------------------------------
1    ul0001@ktwi.online                       f8d7e6c5b4a3        ✅ 启用  2025-10-19T10:30:00Z
2    test-abcdefgh@ktwi.online                c4d5e6f7a8b9        ✅ 启用  2025-10-19T11:00:00Z
3    custom@ktwi.online                       a1b2c3d4e5f6        ✅ 启用  2025-10-19T12:00:00Z
```

---

### `delete` - 删除临时邮箱

删除指定的临时邮箱及其路由规则。支持单个删除和批量通配符删除。

**选项：**
- `--batch` - 批量删除模式，使用通配符匹配邮箱用户名
- `-y, --yes` - 跳过确认提示

**通配符语法（仅在 --batch 模式下）：**
- `*` - 匹配任意数量的字符
- `?` - 匹配单个字符
- `[abc]` - 匹配字符集中的任意一个字符
- `[0-9]` - 匹配任意数字
- `[!abc]` - 匹配不在字符集中的任意字符

**示例：**
```bash
# 单个删除
delete abcdefgh@domain.com
delete ul0001@domain.com -y

# 批量删除
delete --batch 'ul[0-9][0-9][0-9][0-9]'    # 删除 ul0000-ul9999
delete --batch 'ul*'                       # 删除所有 ul 开头的
delete --batch 'test*' -y                  # 删除 test 开头（跳过确认）
```

---

### `cleanup` - 清理所有邮箱

删除所有邮件路由规则。

**选项：**
- `-y, --yes` - 跳过确认提示

**示例：**
```bash
cleanup        # 会提示确认
cleanup -y     # 跳过确认
```

---

## 🛠️ 故障排查

### 常见问题

<details>
<summary><b>问题 1: ❌ 缺少必需的环境变量</b></summary>

**原因**：`.env` 文件不存在或配置不完整

**解决方法**：
1. 确认 `.env` 文件存在于项目根目录
2. 检查所有必需字段是否已填写：
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ZONE_ID`
   - `FORWARD_TO_EMAIL`
   - `EMAIL_DOMAIN`

</details>

<details>
<summary><b>问题 2: ❌ API 请求失败: 401 Unauthorized</b></summary>

**原因**：API Token 无效或已过期

**解决方法**：
1. 访问 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. 检查 Token 是否仍然有效
3. 重新生成 API Token
4. 更新 `.env` 文件中的 `CLOUDFLARE_API_TOKEN`

</details>

<details>
<summary><b>问题 3: ❌ API 请求失败: 403 Forbidden</b></summary>

**原因**：Token 权限不足

**解决方法**：
1. 确认 Token 包含以下权限：
   - `Zone.Email Routing Rules.Edit`
   - `Account.Email Routing Addresses.Edit`
2. 检查 Zone Resources 是否包含目标域名
3. 重新创建 Token 并确保权限正确

</details>

<details>
<summary><b>问题 4: ❌ 请求异常: getaddrinfo failed</b></summary>

**原因**：网络连接问题

**解决方法**：
1. 检查网络连接是否正常
2. 尝试访问 https://api.cloudflare.com
3. 检查代理设置
4. 临时关闭 VPN 重试
5. 检查防火墙是否阻止 Python

</details>

<details>
<summary><b>问题 5: PowerShell 执行策略错误</b></summary>

**错误信息**：`无法加载文件 temp-email.ps1，因为在此系统上禁止运行脚本`

**解决方法**：
```powershell
# 临时允许当前会话运行脚本
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 或使用 CMD 运行批处理文件
temp-email.bat create
```

</details>

---

## 🔒 安全建议

1. **保护 `.env` 文件**
   - ⚠️ 不要将 `.env` 提交到版本控制系统
   - 已添加到 `.gitignore` 中

2. **API Token 权限最小化**
   - 仅授予必需的权限
   - 仅授权特定域名（Zone Resources）

3. **定期轮换 Token**
   - 建议每 90 天更换一次 API Token
   - 删除不再使用的 Token

4. **监控配额使用**
   - 定期检查临时邮箱数量（最多 200 条）
   - 及时删除不再使用的邮箱

---

## 📦 项目文件说明

```
cf-cli/
├── temp_email.py                        # 核心 Python 脚本（主程序）
├── temp-email.ps1                       # PowerShell 包装器（Windows 推荐）
├── temp-email.sh                        # Shell 包装器（Linux/macOS）
├── temp-email.bat                       # 批处理包装器（Windows CMD）
├── .env.example                         # 环境变量配置模板
├── .env                                 # 环境变量配置文件（需手动创建）
├── .gitignore                           # Git 忽略文件配置
├── README.md                            # 本文档
├── CLAUDE.md                            # Claude Code 项目指南
├── test_numbered_email.py               # 编号功能测试脚本
├── 编号邮箱使用说明.md                   # 编号功能详细说明
└── Cloudflare_Email_Routing_API_规则.md # API 调用规则文档
```

---

## 🔗 相关链接

- [Cloudflare Email Routing 文档](https://developers.cloudflare.com/email-routing/)
- [Cloudflare API 文档](https://developers.cloudflare.com/api/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [Python 官网](https://www.python.org/)

---

## ❓ 常见问题 FAQ

**Q: 临时邮箱可以接收邮件吗？**
A: 是的！创建的临时邮箱会自动转发邮件到您配置的真实邮箱。

**Q: 需要安装 Cloudflare CLI 吗？**
A: 不需要！本工具直接调用 Cloudflare REST API。

**Q: 需要安装 Python 包吗？**
A: 不需要！本工具仅使用 Python 标准库，无需 `pip install`。

**Q: 可以创建多少个临时邮箱？**
A: Cloudflare 限制每个账号最多 200 条路由规则。本工具支持管理最多 5000 个邮箱（自动分页）。

**Q: 编号邮箱和随机邮箱有什么区别？**
A: 编号邮箱（如 `ul0001`）是固定可预测的，适合需要记忆或批量管理的场景；随机邮箱（如 `abcdefgh`）更加随机，适合一次性使用。

**Q: 邮箱会自动过期吗？**
A: 不会自动过期，需要手动删除。可以使用 `cleanup` 命令批量清理。

**Q: 支持发送邮件吗？**
A: 本脚本仅支持接收邮件并转发，不支持发送邮件。

**Q: Windows 应该用哪个脚本？**
A: 推荐 PowerShell 用户使用 `temp-email.ps1`，CMD 用户使用 `temp-email.bat`。

---

## 🎓 高级用法

### 在脚本中使用

```bash
#!/bin/bash

# 创建临时邮箱用于注册
EMAIL=$(./temp-email.sh create --prefix ul --number 1 | grep "📧 邮箱地址:" | awk '{print $3}')

echo "使用邮箱: $EMAIL 进行注册..."
# 执行注册操作...

# 稍后删除邮箱
./temp-email.sh delete "$EMAIL" -y
```

### 批量管理多个转发目标

```bash
# 为不同邮箱创建专属临时邮箱池
./temp-email.sh create --count 10 --to user1@qq.com --output-dir ./emails
./temp-email.sh create --count 10 --to user2@gmail.com --output-dir ./emails

# 生成的文件：
# ./emails/user1@qq.com.txt (10个邮箱)
# ./emails/user2@gmail.com.txt (10个邮箱)
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

**Made with ❤️ | 基于 Cloudflare Email Routing API**
