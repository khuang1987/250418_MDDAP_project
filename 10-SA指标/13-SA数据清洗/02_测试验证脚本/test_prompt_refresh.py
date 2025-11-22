#!/usr/bin/env python3
"""
测试修改后的prompt_refresh_mode函数
验证无倒计时，直接等待用户输入
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl_utils import prompt_refresh_mode

def test_prompt_refresh_mode():
    """测试刷新模式选择函数"""
    print("=" * 80)
    print("测试prompt_refresh_mode函数")
    print("=" * 80)
    print()
    print("说明：")
    print("- 此函数已修改为无倒计时版本")
    print("- 会直接等待用户输入，不会自动执行")
    print("- 输入1选择增量刷新，输入2选择全量刷新")
    print("- 直接回车使用默认选择（增量刷新）")
    print()
    
    # 测试默认增量刷新
    print("测试1: 默认增量刷新")
    result1 = prompt_refresh_mode(default_incremental=True)
    print(f"返回结果: {result1} ({'增量刷新' if result1 else '全量刷新'})")
    print()
    
    # 测试默认全量刷新
    print("测试2: 默认全量刷新")
    result2 = prompt_refresh_mode(default_incremental=False)
    print(f"返回结果: {result2} ({'增量刷新' if result2 else '全量刷新'})")
    print()
    
    print("=" * 80)
    print("测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_prompt_refresh_mode()
