#!/usr/bin/env python3
"""
Cloudflare 临时邮箱自动生成脚本
支持自动创建、列出、删除临时邮箱地址，无需每次验证
"""

import os
import sys
import json
import random
import string
import argparse
import fnmatch
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib.request
import urllib.error


class CloudflareEmailManager:
    """Cloudflare Email Routing API 管理器"""

    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(self):
        """从环境变量初始化配置"""
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.forward_to = os.getenv("FORWARD_TO_EMAIL")
        self.email_domain = os.getenv("EMAIL_DOMAIN")
        self.email_prefix = os.getenv("EMAIL_PREFIX", "temp")

        # 验证必需配置
        if not all([self.api_token, self.zone_id, self.forward_to, self.email_domain]):
            raise ValueError(
                "缺少必需的环境变量！请检查以下配置：\n"
                "- CLOUDFLARE_API_TOKEN\n"
                "- CLOUDFLARE_ZONE_ID\n"
                "- FORWARD_TO_EMAIL\n"
                "- EMAIL_DOMAIN\n\n"
                "请参考 .env.example 文件配置"
            )

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> Dict:
        """发送 HTTP 请求到 Cloudflare API"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        request_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method=method
        )

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ API 请求失败: {e.code} {e.reason}")
            print(f"详细信息: {error_body}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            sys.exit(1)

    def generate_random_email(self, prefix: Optional[str] = None) -> str:
        """生成随机邮箱地址
        规则：
        - prefix 为 None 或 "" 时，生成纯随机邮箱（8位小写字母）
        - prefix 为其他值时，生成 prefix-xxxxxxxx 格式
        """
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        if prefix is None or prefix == "":
            local_part = random_str
        else:
            local_part = f"{prefix}-{random_str}"
        return f"{local_part}@{self.email_domain}"

    def generate_numbered_email(self, prefix: str, number: int, digits: int = 4) -> str:
        """生成带编号的邮箱地址
        规则：
        - prefix: 前缀（如 'ul'）
        - number: 编号（如 1）
        - digits: 编号位数（如 4 表示 0001）
        返回: prefix + 补零编号 @ domain （如: ul0001@domain.com）
        """
        number_str = str(number).zfill(digits)
        local_part = f"{prefix}{number_str}"
        return f"{local_part}@{self.email_domain}"

    def create_routing_rule(
        self,
        email: str,
        description: Optional[str] = None,
        forward_to: Optional[str] = None
    ) -> Dict:
        """创建邮件路由规则"""
        endpoint = f"/zones/{self.zone_id}/email/routing/rules"

        rule_data = {
            "actions": [
                {
                    "type": "forward",
                    "value": [forward_to or self.forward_to]
                }
            ],
            "matchers": [
                {
                    "type": "literal",
                    "field": "to",
                    "value": email
                }
            ],
            "enabled": True,
            "name": description or f"Temp email: {email}"
        }

        response = self._make_request(endpoint, method="POST", data=rule_data)

        if response.get("success"):
            return response.get("result", {})
        else:
            errors = response.get("errors", [])
            print(f"❌ 创建路由规则失败: {errors}")
            sys.exit(1)

    def list_routing_rules(self, verbose: bool = False) -> List[Dict]:
        """列出所有邮件路由规则（支持分页）"""
        all_rules = []
        page = 1
        per_page = 50  # Cloudflare API 每页最多 50 条

        while True:
            endpoint = f"/zones/{self.zone_id}/email/routing/rules?page={page}&per_page={per_page}"
            response = self._make_request(endpoint)

            if not response.get("success"):
                print(f"❌ 获取路由规则失败: {response.get('errors')}")
                break

            result = response.get("result", [])
            result_info = response.get("result_info", {})

            if verbose:
                print(f"  第 {page} 页: 获取到 {len(result)} 条记录")
                print(f"  result_info: {result_info}")

            if not result:
                # 没有更多数据了
                if verbose:
                    print(f"  第 {page} 页没有数据，停止获取")
                break

            all_rules.extend(result)

            # 检查是否还有更多页 - 使用多种方式判断
            # 方法1: 检查返回的记录数是否少于每页数量
            if len(result) < per_page:
                if verbose:
                    print(f"  返回记录数 ({len(result)}) < 每页数量 ({per_page})，没有更多数据")
                break

            # 方法2: 检查 result_info 中的分页信息
            total_count = result_info.get("total_count")
            if total_count is not None and len(all_rules) >= total_count:
                if verbose:
                    print(f"  已获取所有记录 ({len(all_rules)}/{total_count})")
                break

            total_pages = result_info.get("total_pages")
            if total_pages is not None and page >= total_pages:
                if verbose:
                    print(f"  已到达最后一页 ({page}/{total_pages})")
                break

            page += 1

            # 安全限制：最多获取 100 页（防止无限循环）
            if page > 100:
                if verbose:
                    print(f"  达到最大页数限制 (100 页)，停止获取")
                break

        if verbose:
            print(f"  ✅ 总共获取到 {len(all_rules)} 条路由规则")

        return all_rules

    def delete_routing_rule(self, rule_id: str) -> bool:
        """删除邮件路由规则"""
        endpoint = f"/zones/{self.zone_id}/email/routing/rules/{rule_id}"
        response = self._make_request(endpoint, method="DELETE")

        return response.get("success", False)

    def find_rule_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱地址查找路由规则"""
        rules = self.list_routing_rules()
        for rule in rules:
            matchers = rule.get("matchers", [])
            for matcher in matchers:
                if matcher.get("field") == "to" and matcher.get("value") == email:
                    return rule
        return None


def create_email(args):
    """创建临时邮箱（支持批量、指定转发目标、输出目录、编号）"""
    manager = CloudflareEmailManager()

    # 目标转发地址（优先使用参数）
    target_to = getattr(args, 'to', None) or manager.forward_to

    created: List[str] = []
    count = max(1, int(getattr(args, 'count', 1) or 1))

    # 检查是否使用编号模式
    use_number = getattr(args, 'number', None) is not None or getattr(args, 'start', None) is not None

    if use_number:
        # 编号模式
        if not args.prefix:
            print("❌ 使用编号模式时必须指定 --prefix 参数")
            sys.exit(1)

        # 确定起始编号
        start_number = getattr(args, 'start', None) or getattr(args, 'number', None)
        if start_number is None:
            start_number = 1

        digits = getattr(args, 'digits', 4)

        for i in range(count):
            current_number = start_number + i
            email = manager.generate_numbered_email(args.prefix, current_number, digits)

            print(f"📧 正在创建临时邮箱: {email}")
            print(f"📮 转发目标: {target_to}")

            # 创建路由规则
            description = args.description or f"Numbered email created at {datetime.now().isoformat()}"
            rule = manager.create_routing_rule(email, description, forward_to=target_to)

            print(f"✅ 临时邮箱创建成功!")
            print(f"📧 邮箱地址: {email}")
            print(f"🆔 规则 ID: {rule.get('tag')}")
            print(f"📝 描述: {rule.get('name')}")
            if count > 1:
                print()  # 批量创建时添加空行分隔

            # 保存到本地记录（可选）
            save_to_history(email, rule.get('tag'), description)
            created.append(email)
    else:
        # 原有的随机模式
        for _ in range(count):
            # 生成邮箱地址
            if args.email and count == 1:
                email = args.email if '@' in args.email else f"{args.email}@{manager.email_domain}"
            else:
                # 处理无前缀选项或自定义前缀
                if getattr(args, 'no_prefix', False):
                    email = manager.generate_random_email("")
                else:
                    email = manager.generate_random_email(args.prefix)

            print(f"📧 正在创建临时邮箱: {email}")
            print(f"📮 转发目标: {target_to}")

            # 创建路由规则
            description = args.description or f"Temporary email created at {datetime.now().isoformat()}"
            rule = manager.create_routing_rule(email, description, forward_to=target_to)

            print(f"✅ 临时邮箱创建成功!")
            print(f"📧 邮箱地址: {email}")
            print(f"🆔 规则 ID: {rule.get('tag')}")
            print(f"📝 描述: {rule.get('name')}")

            # 保存到本地记录（可选）
            save_to_history(email, rule.get('tag'), description)
            created.append(email)

    # 若指定输出目录，则把生成的邮箱写入 以目标邮箱命名的 .txt 文件
    out_dir = getattr(args, 'output_dir', None)
    if out_dir:
        try:
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{target_to}.txt")
            with open(out_path, 'w', encoding='utf-8') as f:
                for e in created:
                    f.write(e + "\n")
            print(f"🗂 已写出 {len(created)} 个邮箱到: {out_path}")
        except Exception:
            # 静默失败，不影响主流程
            pass


def list_emails(args):
    """列出所有临时邮箱"""
    manager = CloudflareEmailManager()

    # 检查是否启用详细模式
    verbose = getattr(args, 'verbose', False)

    print("📋 正在获取所有邮件路由规则...")
    if verbose:
        print("🔍 启用详细模式，显示分页信息：")

    rules = manager.list_routing_rules(verbose=verbose)

    if not rules:
        print("📭 没有找到任何路由规则")
        return

    print(f"\n找到 {len(rules)} 条路由规则:\n")
    print(f"{'序号':<4} {'邮箱地址':<40} {'规则ID':<20} {'状态':<8} {'创建时间'}")
    print("-" * 100)

    for idx, rule in enumerate(rules, 1):
        email = "N/A"
        for matcher in rule.get("matchers", []):
            if matcher.get("field") == "to":
                email = matcher.get("value", "N/A")
                break

        rule_id = rule.get("tag", "N/A")[:18]
        status = "✅ 启用" if rule.get("enabled") else "❌ 禁用"
        created = rule.get("created", "N/A")

        print(f"{idx:<4} {email:<40} {rule_id:<20} {status:<8} {created}")


def delete_email(args):
    """删除临时邮箱"""
    manager = CloudflareEmailManager()

    # 检查是否为批量删除模式
    if getattr(args, 'batch', False):
        return delete_batch_emails(args, manager)

    email = args.email

    # 查找规则
    print(f"🔍 正在查找邮箱: {email}")
    rule = manager.find_rule_by_email(email)

    if not rule:
        print(f"❌ 未找到邮箱 {email} 对应的路由规则")
        sys.exit(1)

    rule_id = rule.get("tag")
    print(f"找到规则 ID: {rule_id}")

    # 确认删除
    if not args.yes:
        confirm = input(f"⚠️  确定要删除邮箱 {email} 吗? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 取消删除")
            return

    # 删除规则
    print(f"🗑️  正在删除...")
    success = manager.delete_routing_rule(rule_id)

    if success:
        print(f"✅ 成功删除邮箱: {email}")
    else:
        print(f"❌ 删除失败")
        sys.exit(1)


def delete_batch_emails(args, manager: CloudflareEmailManager):
    """批量删除符合通配符规则的邮箱"""
    pattern = args.email  # 在批量模式下，email 参数实际是通配符模式

    print(f"🔍 正在查找匹配 '{pattern}' 的邮箱...")

    # 获取所有路由规则
    all_rules = manager.list_routing_rules()

    if not all_rules:
        print("📭 没有找到任何路由规则")
        return

    # 过滤匹配的邮箱（仅匹配用户名部分）
    matched_rules = []
    for rule in all_rules:
        for matcher in rule.get("matchers", []):
            if matcher.get("field") == "to":
                email = matcher.get("value", "")
                if email and '@' in email:
                    username = email.split('@')[0]
                    # 使用 fnmatch 进行通配符匹配
                    if fnmatch.fnmatch(username, pattern):
                        matched_rules.append({
                            'rule': rule,
                            'email': email
                        })
                break

    # 检查是否有匹配项
    if not matched_rules:
        print(f"📭 没有找到匹配 '{pattern}' 的邮箱")
        return

    # 显示匹配的邮箱列表
    print(f"\n找到 {len(matched_rules)} 个匹配的邮箱：")
    print("-" * 60)
    for idx, item in enumerate(matched_rules, 1):
        email = item['email']
        rule_id = item['rule'].get('tag', 'N/A')[:18]
        print(f"{idx:<4} {email:<40} {rule_id}")
    print("-" * 60)

    # 确认删除
    if not args.yes:
        confirm = input(f"\n⚠️  确定要删除这 {len(matched_rules)} 个邮箱吗? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 取消删除")
            return

    # 批量删除
    print(f"\n🗑️  开始批量删除...")
    deleted = 0
    failed = 0

    for item in matched_rules:
        email = item['email']
        rule_id = item['rule'].get('tag')

        try:
            if manager.delete_routing_rule(rule_id):
                print(f"✅ 删除: {email}")
                deleted += 1
            else:
                print(f"❌ 失败: {email}")
                failed += 1
        except Exception as e:
            print(f"❌ 失败: {email} (错误: {e})")
            failed += 1

    # 显示结果统计
    print(f"\n{'='*60}")
    print(f"✅ 成功删除: {deleted} 个")
    if failed > 0:
        print(f"❌ 删除失败: {failed} 个")
    print(f"📊 总计: {deleted + failed} 个")
    print(f"{'='*60}")


def cleanup_emails(args):
    """清理所有临时邮箱"""
    manager = CloudflareEmailManager()

    print("🔍 正在获取所有路由规则...")
    rules = manager.list_routing_rules()

    if not rules:
        print("📭 没有找到任何路由规则")
        return

    print(f"找到 {len(rules)} 条规则")

    if not args.yes:
        confirm = input(f"⚠️  确定要删除所有 {len(rules)} 条规则吗? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 取消清理")
            return

    deleted = 0
    for rule in rules:
        rule_id = rule.get("tag")
        email = "N/A"
        for matcher in rule.get("matchers", []):
            if matcher.get("field") == "to":
                email = matcher.get("value", "N/A")
                break

        print(f"🗑️  删除: {email} ({rule_id[:18]}...)")
        if manager.delete_routing_rule(rule_id):
            deleted += 1

    print(f"\n✅ 成功删除 {deleted}/{len(rules)} 条规则")


def save_to_history(email: str, rule_id: str, description: str):
    """保存到本地历史记录"""
    history_file = "temp_emails.json"

    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []

        history.append({
            "email": email,
            "rule_id": rule_id,
            "description": description,
            "created_at": datetime.now().isoformat()
        })

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # 静默失败，不影响主要功能
        pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Cloudflare 临时邮箱管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 创建随机临时邮箱（纯随机8位字母，如: abcdefgh@domain.com）
  %(prog)s create
  %(prog)s create --no-prefix

  # 创建指定前缀的邮箱（如: test-abcdefgh@domain.com）
  %(prog)s create --prefix test

  # 创建指定邮箱地址
  %(prog)s create --email custom-name

  # 创建编号邮箱（如: ul0001@domain.com）
  %(prog)s create --prefix ul --number 1

  # 创建指定编号的邮箱（如: ul9977@domain.com）
  %(prog)s create --prefix ul --number 9977

  # 批量创建连续编号邮箱（如: ul0001 到 ul0010）
  %(prog)s create --prefix ul --start 1 --count 10

  # 批量创建指定位数的编号（如: ul001 到 ul010，3位数）
  %(prog)s create --prefix ul --start 1 --count 10 --digits 3

  # 批量创建10个随机邮箱
  %(prog)s create --count 10 --to 203320879@qq.com

  # 列出所有临时邮箱
  %(prog)s list

  # 删除指定邮箱
  %(prog)s delete abcdefgh@example.com

  # 批量删除：删除所有 ul 开头后跟4位数字的邮箱
  %(prog)s delete --batch 'ul[0-9][0-9][0-9][0-9]'

  # 批量删除：删除所有 u 开头的邮箱
  %(prog)s delete --batch 'u*'

  # 批量删除：删除 3 个字符长度的邮箱
  %(prog)s delete --batch '???'

  # 批量删除：删除 a、b、c 开头的邮箱
  %(prog)s delete --batch '[abc]*'

  # 批量删除并跳过确认
  %(prog)s delete --batch 'test*' -y

  # 清理所有临时邮箱
  %(prog)s cleanup
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # create 命令
    create_parser = subparsers.add_parser('create', help='创建临时邮箱')
    create_parser.add_argument('--prefix', help='邮箱前缀（随机模式: test 生成 test-abcdefgh@domain.com；编号模式: ul 生成 ul0001@domain.com）')
    create_parser.add_argument('--no-prefix', action='store_true', help='不使用前缀，生成纯随机邮箱: abcdefgh@domain.com（默认）')
    create_parser.add_argument('--email', help='指定完整邮箱地址或用户名')
    create_parser.add_argument('--number', type=int, help='指定编���（如: --prefix ul --number 1 生成 ul0001@domain.com）')
    create_parser.add_argument('--start', type=int, help='批量创建时的起始编号（如: --prefix ul --start 1 --count 10 生成 ul0001 到 ul0010）')
    create_parser.add_argument('--digits', type=int, default=4, help='编号位数（默认4位，如 0001）')
    create_parser.add_argument('--description', help='规则描述')
    create_parser.add_argument('--to', help='指定转发目标邮箱（覆盖 FORWARD_TO_EMAIL）')
    create_parser.add_argument('--count', type=int, help='批量创建数量（默认1）')
    create_parser.add_argument('--output-dir', help='将结果写入该目录下，以目标邮箱命名的 .txt 文件')
    create_parser.set_defaults(func=create_email)

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有临时邮箱')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细的分页信息')
    list_parser.set_defaults(func=list_emails)

    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除临时邮箱')
    delete_parser.add_argument('email', help='要删除的邮箱地址或通配符模式（配合 --batch 使用）')
    delete_parser.add_argument('--batch', action='store_true', help='批量删除模式：使用通配符模式匹配邮箱用户名')
    delete_parser.add_argument('-y', '--yes', action='store_true', help='跳过确认')
    delete_parser.set_defaults(func=delete_email)

    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理所有临时邮箱')
    cleanup_parser.add_argument('-y', '--yes', action='store_true', help='跳过确认')
    cleanup_parser.set_defaults(func=cleanup_emails)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    args.func(args)


if __name__ == "__main__":
    main()
