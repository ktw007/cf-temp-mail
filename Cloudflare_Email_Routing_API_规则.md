# Cloudflare Email Routing API 调用规则

## 📋 目录
1. [API 端点列表](#api-端点列表)
2. [认证方式](#认证方式)
3. [路由规则 API](#路由规则-api)
4. [分页规则](#分页规则)
5. [配额限制](#配额限制)
6. [响应格式](#响应格式)
7. [最佳实践](#最佳实践)

---

## API 端点列表

### 路由规则管理（Routing Rules）
| 方法 | 端点 | 说明 |
|------|------|------|
| **GET** | `/zones/{zone_id}/email/routing/rules` | 列出所有路由规则 |
| **POST** | `/zones/{zone_id}/email/routing/rules` | 创建路由规则 |
| **GET** | `/zones/{zone_id}/email/routing/rules/{rule_id}` | 获取单个规则详情 |
| **PUT** | `/zones/{zone_id}/email/routing/rules/{rule_id}` | 更新路由规则 |
| **DELETE** | `/zones/{zone_id}/email/routing/rules/{rule_id}` | 删除路由规则 |

### Catch-All 规则
| 方法 | 端点 | 说明 |
|------|------|------|
| **GET** | `/zones/{zone_id}/email/routing/rules/catch_all` | 获取兜底规则 |
| **PUT** | `/zones/{zone_id}/email/routing/rules/catch_all` | 更新兜底规则 |

### 目标地址管理
| 方法 | 端点 | 说明 |
|------|------|------|
| **GET** | `/accounts/{account_id}/email/routing/addresses` | 列出目标地址 |
| **POST** | `/accounts/{account_id}/email/routing/addresses` | 创建目标地址 |
| **GET** | `/accounts/{account_id}/email/routing/addresses/{address_id}` | 获取地址详情 |
| **DELETE** | `/accounts/{account_id}/email/routing/addresses/{address_id}` | 删除目标地址 |

### Email Routing 设置
| 方法 | 端点 | 说明 |
|------|------|------|
| **GET** | `/zones/{zone_id}/email/routing` | 获取 Email Routing 设置 |
| **POST** | `/zones/{zone_id}/email/routing/dns` | 启用 Email Routing 并配置 DNS |
| **DELETE** | `/zones/{zone_id}/email/routing/dns` | 禁用 Email Routing 并移除 DNS |

---

## 认证方式

### 方式 1: API Token（推荐）
```bash
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json
```

**所需权限：**
- 读取规则：`Email Routing Rules Read`
- 写入规则：`Email Routing Rules Write`

### 方式 2: API Key + Email（传统方式）
```bash
X-Auth-Email: user@example.com
X-Auth-Key: YOUR_API_KEY
Content-Type: application/json
```

---

## 路由规则 API

### 1. 列出所有路由规则

**请求：**
```http
GET /zones/{zone_id}/email/routing/rules?page=1&per_page=50&enabled=true
```

**查询参数：**
| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `page` | integer | 页码（≥1） | 1 |
| `per_page` | integer | 每页记录数（5-50） | 20 |
| `enabled` | boolean | 过滤启用状态 | - |

**响应示例：**
```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": [
    {
      "id": "a7e6fb77503c41d8a7f3113c6918f10c",
      "tag": "a7e6fb77503c41d8a7f3113c6918f10c",
      "name": "Send to user@example.net rule.",
      "enabled": true,
      "priority": 0,
      "matchers": [
        {
          "type": "literal",
          "field": "to",
          "value": "test@example.com"
        }
      ],
      "actions": [
        {
          "type": "forward",
          "value": ["destinationaddress@example.net"]
        }
      ]
    }
  ],
  "result_info": {
    "page": 1,
    "per_page": 50,
    "count": 1,
    "total_count": 1,
    "total_pages": 1
  }
}
```

### 2. 创建路由规则

**请求：**
```http
POST /zones/{zone_id}/email/routing/rules
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "Send to user@example.net rule.",
  "enabled": true,
  "matchers": [
    {
      "type": "literal",
      "field": "to",
      "value": "test@example.com"
    }
  ],
  "actions": [
    {
      "type": "forward",
      "value": ["destinationaddress@example.net"]
    }
  ]
}
```

**参数说明：**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 否 | 规则描述 |
| `enabled` | boolean | 否 | 是否启用（默认 true） |
| `matchers` | array | **是** | 匹配条件数组 |
| `actions` | array | **是** | 动作数组 |

**Matchers 结构：**
```json
{
  "type": "literal",        // 匹配类型：literal（精确匹配）
  "field": "to",           // 匹配字段：to（收件人）
  "value": "email@domain"  // 匹配值
}
```

**Actions 结构：**
```json
{
  "type": "forward",              // 动作类型：forward（转发）
  "value": ["target@example.com"] // 目标邮箱数组
}
```

**成功响应（200）：**
```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "a7e6fb77503c41d8a7f3113c6918f10c",
    "tag": "a7e6fb77503c41d8a7f3113c6918f10c",
    "name": "Send to user@example.net rule.",
    "enabled": true,
    "priority": 0,
    "matchers": [...],
    "actions": [...]
  }
}
```

### 3. 删除路由规则

**请求：**
```http
DELETE /zones/{zone_id}/email/routing/rules/{rule_id}
```

**成功响应：**
```json
{
  "success": true,
  "errors": [],
  "messages": []
}
```

---

## 分页规则

### 分页参数
- **默认每页记录数：** 20
- **最小每页记录数：** 5
- **最大每页记录数：** 50
- **页码起始值：** 1

### 分页信息（result_info）
```json
{
  "page": 1,           // 当前页码
  "per_page": 50,      // 每页记录数
  "count": 45,         // 本页实际记录数
  "total_count": 145,  // 总记录数
  "total_pages": 3     // 总页数
}
```

### 判断是否还有下一页
```python
# 方法 1: 检查当前页记录数
if len(result) < per_page:
    # 没有更多数据

# 方法 2: 使用 result_info
if page >= result_info['total_pages']:
    # 已到最后一页

# 方法 3: 检查总记录数
if len(all_results) >= result_info['total_count']:
    # 已获取全部数据
```

---

## 配额限制

### 核心限制
| 项目 | 限制 |
|------|------|
| **路由规则数量** | 200 条 |
| **目标地址数量** | 200 个 |
| **单封邮件大小** | 25 MiB |

### 速率限制
- 文档未明确说明 API 速率限制
- 建议：每秒请求数控制在合理范围（如 5-10 req/s）
- 遇到速率限制会返回 429 状态码

### Email Workers 限制
- 受 Cloudflare Workers 标准限制约束
- 免费计划有 CPU 时间限制
- 可能遇到 `EXCEEDED_CPU` 错误
- 付费计划提供更高的使用限制

### 申请提升限制
- 可通过 Cloudflare 提交 **Limit Increase Request Form** 申请提升配额

---

## 响应格式

### 标准响应结构
所有 API 响应都遵循统一的信封格式：

```json
{
  "success": true,           // 请求是否成功
  "errors": [],              // 错误信息数组
  "messages": [],            // 提示信息数组
  "result": {...},           // 实际数据
  "result_info": {...}       // 分页信息（仅列表接口）
}
```

### 错误响应示例
```json
{
  "success": false,
  "errors": [
    {
      "code": 1003,
      "message": "Invalid or missing zone id.",
      "documentation_url": "https://developers.cloudflare.com/api/"
    }
  ],
  "messages": [],
  "result": null
}
```

### 常见 HTTP 状态码
| 状态码 | 说明 |
|--------|------|
| **200** | 成功 |
| **400** | 请求参数错误 |
| **401** | 认证失败（Token 无效） |
| **403** | 权限不足 |
| **404** | 资源不存在 |
| **429** | 速率限制（Too Many Requests） |
| **500** | 服务器内部错误 |

---

## 最佳实践

### 1. 认证安全
```bash
# ✅ 推荐：使用 API Token
Authorization: Bearer YOUR_API_TOKEN

# ❌ 避免：在代码中硬编码 Token
# 使用环境变量存储敏感信息
export CLOUDFLARE_API_TOKEN="your-token"
```

### 2. 错误处理
```python
try:
    response = make_request(endpoint)
    if not response.get("success"):
        errors = response.get("errors", [])
        for error in errors:
            print(f"错误 {error['code']}: {error['message']}")
except urllib.error.HTTPError as e:
    if e.code == 429:
        # 处理速率限制：等待后重试
        time.sleep(60)
    elif e.code == 401:
        # 认证失败：检查 Token
        print("Token 无效或已过期")
```

### 3. 分页处理
```python
def fetch_all_rules(zone_id):
    all_rules = []
    page = 1
    per_page = 50  # 使用最大值提高效率

    while True:
        response = get_rules(zone_id, page, per_page)
        rules = response['result']

        if not rules:
            break

        all_rules.extend(rules)

        # 检查是否还有更多页
        result_info = response.get('result_info', {})
        if page >= result_info.get('total_pages', 1):
            break

        page += 1

        # 安全限制：防止无限循环
        if page > 100:
            break

    return all_rules
```

### 4. 批量操作优化
```python
# ✅ 批量创建时添加延迟
for email in email_list:
    create_rule(email)
    time.sleep(0.2)  # 避免触发速率限制

# ✅ 批量删除时显示进度
for i, rule in enumerate(rules_to_delete, 1):
    delete_rule(rule['id'])
    print(f"进度: {i}/{len(rules_to_delete)}")
```

### 5. 规则命名规范
```python
# ✅ 使用描述性名称
name = f"Temporary email created at {datetime.now().isoformat()}"

# ✅ 包含关键信息
name = f"Forward {email} to {target}"

# ❌ 避免使用无意义的名称
name = "rule1"
```

### 6. 配额监控
```python
# 定期检查规则数量
rules = list_all_rules()
print(f"当前规则数: {len(rules)}/200")

if len(rules) > 180:
    print("⚠️  接近配额限制，建议清理旧规则")
```

### 7. DNS 配置要求
在使用 Email Routing 前，确保：
- ✅ 域名使用 Cloudflare 作为权威 DNS
- ✅ MX 记录正确配置
- ✅ SPF 记录包含 Cloudflare
- ✅ 目标邮箱已验证

---

## 项目当前实现分析

### 已实现的最佳实践 ✅
1. **错误处理**：`temp_email.py:66-76` 完善的异常捕获
2. **分页支持**：`temp_email.py:127-187` 自动分页获取所有规则
3. **环境变量**：使用 `.env` 存储敏感信息
4. **确认提示**：删除操作前需要确认

### 建议改进 🔧
1. **速率限制处理**：
   ```python
   # 在 _make_request 中添加重试逻辑
   if e.code == 429:
       time.sleep(60)
       # 重试请求
   ```

2. **配额检查**：
   ```python
   def check_quota_before_create(self):
       rules = self.list_routing_rules()
       if len(rules) >= 190:
           print("⚠️  警告：接近规则数量限制 (200)")
   ```

3. **批量操作延迟**：
   ```python
   # 在批量创建时添加延迟
   for i in range(count):
       create_rule(...)
       if i < count - 1:
           time.sleep(0.2)  # 避免速率限制
   ```

---

## 参考链接

- [Cloudflare Email Routing 官方文档](https://developers.cloudflare.com/email-routing/)
- [Email Routing API 参考](https://developers.cloudflare.com/api/operations/email-routing-routing-rules-list-routing-rules)
- [配额限制说明](https://developers.cloudflare.com/email-routing/limits/)
- [故障排除指南](https://developers.cloudflare.com/email-routing/troubleshooting/)

---

**文档生成时间：** 2025-10-23
**API 版本：** Cloudflare API v4
