#!/usr/bin/env python3
"""
测试编号邮箱生成功能
这个测试脚本不会实际调用 API，只测试邮箱地址的生成逻辑
"""

import sys
import os

# 设置环境变量以通过初始化检查
os.environ['CLOUDFLARE_API_TOKEN'] = 'test_token'
os.environ['CLOUDFLARE_ZONE_ID'] = 'test_zone_id'
os.environ['FORWARD_TO_EMAIL'] = 'test@example.com'
os.environ['EMAIL_DOMAIN'] = 'example.com'

from temp_email import CloudflareEmailManager

def test_numbered_emails():
    """测试编号邮箱生成功能"""
    manager = CloudflareEmailManager()

    print("=" * 60)
    print("测试编号邮箱生成功能")
    print("=" * 60)
    print()

    # 测试1: 单个编号邮箱
    print("测试 1: 生成单个编号邮箱 (ul0001)")
    email = manager.generate_numbered_email("ul", 1, 4)
    print(f"  结果: {email}")
    assert email == "ul0001@example.com", f"期望 ul0001@example.com，得到 {email}"
    print("  ✅ 通过")
    print()

    # 测试2: 不同的编号
    print("测试 2: 生成不同编号的邮箱 (ul9977)")
    email = manager.generate_numbered_email("ul", 9977, 4)
    print(f"  结果: {email}")
    assert email == "ul9977@example.com", f"期望 ul9977@example.com，得到 {email}"
    print("  ✅ 通过")
    print()

    # 测试3: 不同位数
    print("测试 3: 生成3位数编号 (ul001)")
    email = manager.generate_numbered_email("ul", 1, 3)
    print(f"  结果: {email}")
    assert email == "ul001@example.com", f"期望 ul001@example.com，得到 {email}"
    print("  ✅ 通过")
    print()

    # 测试4: 5位数编号
    print("测试 4: 生成5位数编号 (test00123)")
    email = manager.generate_numbered_email("test", 123, 5)
    print(f"  结果: {email}")
    assert email == "test00123@example.com", f"期望 test00123@example.com，得到 {email}"
    print("  ✅ 通过")
    print()

    # 测试5: 批量连续编号
    print("测试 5: 批量生成连续编号 (ul0001 到 ul0010)")
    for i in range(1, 11):
        email = manager.generate_numbered_email("ul", i, 4)
        expected = f"ul{str(i).zfill(4)}@example.com"
        print(f"  {i}: {email}")
        assert email == expected, f"期望 {expected}，得到 {email}"
    print("  ✅ 通过")
    print()

    # 测试6: 大编号（超过位数）
    print("测试 6: 编号超过位数 (12345 with 4 digits)")
    email = manager.generate_numbered_email("ul", 12345, 4)
    print(f"  结果: {email}")
    print(f"  注意: 当编���超过指定位数时，会显示完整编号")
    assert email == "ul12345@example.com", f"期望 ul12345@example.com，得到 {email}"
    print("  ✅ 通过")
    print()

    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print()
    print("您现在可以使用以下命令创建编号邮箱：")
    print()
    print("  # 创建单个编号邮箱")
    print("  python temp_email.py create --prefix ul --number 1")
    print("  # 生成: ul0001@your-domain.com")
    print()
    print("  # 创建指定编号")
    print("  python temp_email.py create --prefix ul --number 9977")
    print("  # 生成: ul9977@your-domain.com")
    print()
    print("  # 批量创建连续编号")
    print("  python temp_email.py create --prefix ul --start 1 --count 10")
    print("  # 生成: ul0001 到 ul0010")
    print()

if __name__ == "__main__":
    try:
        test_numbered_emails()
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
