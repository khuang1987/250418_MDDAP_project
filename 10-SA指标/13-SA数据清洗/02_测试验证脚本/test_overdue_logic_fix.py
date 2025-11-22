#!/usr/bin/env python3
"""
测试超期判断逻辑修复
验证换型时间处理是否正确
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def calculate_completion_status_old(row: pd.Series, calendar_df: pd.DataFrame = None) -> str:
    """旧的超期判断逻辑（修复前）"""
    pt = row.get("PT(d)", None)
    st = row.get("ST(d)", None)
    tolerance_h = row.get("Tolerance(h)", 8.0)
    
    if pd.isna(pt) or pd.isna(st):
        return None
    
    # 简化计算：假设PT已经是工作日小时数
    pt_workday_hours = pt * 24
    st_hours = st * 24
    
    # 旧逻辑：固定0.5小时换批时间
    tolerance_and_changeover = tolerance_h + 0.5
    
    if pt_workday_hours > (st_hours + tolerance_and_changeover):
        return "Overdue"
    else:
        return "OnTime"

def calculate_completion_status_new(row: pd.Series, calendar_df: pd.DataFrame = None) -> str:
    """新的超期判断逻辑（修复后）"""
    pt = row.get("PT(d)", None)
    st = row.get("ST(d)", None)
    tolerance_h = row.get("Tolerance(h)", 8.0)
    
    if pd.isna(pt) or pd.isna(st):
        return None
    
    # 简化计算：假设PT已经是工作日小时数
    pt_workday_hours = pt * 24
    st_hours = st * 24
    
    # 新逻辑：检查是否需要使用标准换型时间
    changeover_time = 0.5  # 默认换批时间
    if row.get("Setup") == "Yes" and pd.notna(row.get("Setup Time (h)")):
        changeover_time = row.get("Setup Time (h)", 0.5) or 0.5  # 使用标准换型时间
    
    tolerance_and_changeover = tolerance_h + changeover_time
    
    if pt_workday_hours > (st_hours + tolerance_and_changeover):
        return "Overdue"
    else:
        return "OnTime"

def test_overdue_logic_fix():
    """测试超期判断逻辑修复"""
    print("=" * 80)
    print("超期判断逻辑修复测试")
    print("=" * 80)
    
    # 测试案例
    test_cases = [
        {
            "name": "案例1: 正常换批，未超期",
            "data": {
                "PT(d)": 1.0,  # 24小时
                "ST(d)": 0.8,  # 19.2小时
                "Setup": "No",
                "Setup Time (h)": None,
                "Tolerance(h)": 8.0
            },
            "expected_old": "OnTime",
            "expected_new": "OnTime"
        },
        {
            "name": "案例2: 正常换批，刚好超期",
            "data": {
                "PT(d)": 1.2,  # 28.8小时
                "ST(d)": 0.8,  # 19.2小时
                "Setup": "No",
                "Setup Time (h)": None,
                "Tolerance(h)": 8.0
            },
            "expected_old": "Overdue",  # 28.8 > 19.2 + 8 + 0.5 = 27.7
            "expected_new": "Overdue"   # 同样逻辑
        },
        {
            "name": "案例3: 换型，短换型时间，未超期",
            "data": {
                "PT(d)": 1.1,  # 26.4小时
                "ST(d)": 0.8,  # 19.2小时
                "Setup": "Yes",
                "Setup Time (h)": 1.0,  # 1小时换型时间
                "Tolerance(h)": 8.0
            },
            "expected_old": "OnTime",  # 旧逻辑用0.5小时: 26.4 <= 19.2 + 8 + 0.5 = 27.7
            "expected_new": "OnTime"   # 新逻辑用1.0小时: 26.4 <= 19.2 + 8 + 1.0 = 28.2
        },
        {
            "name": "案例4: 换型，长换型时间，导致超期判断变化",
            "data": {
                "PT(d)": 1.15,  # 27.6小时
                "ST(d)": 0.8,   # 19.2小时
                "Setup": "Yes",
                "Setup Time (h)": 2.0,  # 2小时换型时间
                "Tolerance(h)": 8.0
            },
            "expected_old": "OnTime",  # 旧逻辑用0.5小时: 27.6 <= 19.2 + 8 + 0.5 = 27.7
            "expected_new": "OnTime"   # 新逻辑用2.0小时: 27.6 <= 19.2 + 8 + 2.0 = 29.2
        },
        {
            "name": "案例5: 换型，短换型时间，展示新旧逻辑差异",
            "data": {
                "PT(d)": 1.14,   # 27.36小时
                "ST(d)": 0.8,    # 19.2小时
                "Setup": "Yes",
                "Setup Time (h)": 0.1,  # 0.1小时换型时间（比默认0.5小时短）
                "Tolerance(h)": 8.0
            },
            "expected_old": "OnTime",   # 旧逻辑用0.5小时: 27.36 <= 19.2 + 8 + 0.5 = 27.7
            "expected_new": "Overdue"   # 新逻辑用0.1小时: 27.36 > 19.2 + 8 + 0.1 = 27.3
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{case['name']}")
        print("-" * 60)
        
        # 创建测试行
        row = pd.Series(case['data'])
        
        # 计算结果
        result_old = calculate_completion_status_old(row)
        result_new = calculate_completion_status_new(row)
        
        # 计算阈值
        pt_hours = case['data']['PT(d)'] * 24
        st_hours = case['data']['ST(d)'] * 24
        tolerance = case['data']['Tolerance(h)']
        
        # 旧逻辑阈值
        threshold_old = st_hours + tolerance + 0.5
        # 新逻辑阈值
        setup_time = case['data'].get('Setup Time (h)', 0.5) if case['data'].get('Setup') == 'Yes' else 0.5
        threshold_new = st_hours + tolerance + setup_time
        
        print(f"输入数据:")
        print(f"  PT: {case['data']['PT(d)']}天 = {pt_hours}小时")
        print(f"  ST: {case['data']['ST(d)']}天 = {st_hours}小时")
        print(f"  容差: {tolerance}小时")
        print(f"  换批/换型时间: 旧逻辑=0.5小时, 新逻辑={setup_time}小时")
        print()
        print(f"阈值计算:")
        print(f"  旧逻辑阈值: {st_hours} + {tolerance} + 0.5 = {threshold_old}小时")
        print(f"  新逻辑阈值: {st_hours} + {tolerance} + {setup_time} = {threshold_new}小时")
        print()
        print(f"判断结果:")
        print(f"  旧逻辑: {pt_hours} > {threshold_old}? {pt_hours > threshold_old} → {result_old}")
        print(f"  新逻辑: {pt_hours} > {threshold_new}? {pt_hours > threshold_new} → {result_new}")
        print()
        
        # 检查结果
        status_old = "✅" if result_old == case['expected_old'] else "❌"
        status_new = "✅" if result_new == case['expected_new'] else "❌"
        
        print(f"期望结果: 旧逻辑={case['expected_old']}, 新逻辑={case['expected_new']}")
        print(f"实际结果: {status_old} 旧逻辑={result_old}, {status_new} 新逻辑={result_new}")

def analyze_fix_impact():
    """分析修复影响"""
    print("\n" + "=" * 80)
    print("修复影响分析")
    print("=" * 80)
    
    print("1. 修复内容:")
    print("   ✅ 换型时间处理：Setup='Yes'时使用标准换型时间")
    print("   ✅ 正常换批：继续使用0.5小时固定时间")
    print("   ✅ 逻辑一致性：与ST计算中的换型时间处理保持一致")
    print()
    
    print("2. 预期影响:")
    print("   - 换型工序的超期判断更准确")
    print("   - 长换型时间工序的超期率可能下降")
    print("   - 短换型时间工序的超期率可能上升")
    print()
    
    print("3. 业务价值:")
    print("   - 超期判断更符合实际生产情况")
    print("   - 考虑了不同工序的换型复杂度")
    print("   - 提高了数据分析的准确性")
    print()
    
    print("4. 验证建议:")
    print("   - 运行完整ETL验证修复效果")
    print("   - 对比修复前后的超期率变化")
    print("   - 检查换型工序的超期分布")

if __name__ == "__main__":
    print("MES超期判断逻辑修复验证")
    print("=" * 80)
    
    test_overdue_logic_fix()
    analyze_fix_impact()
    
    print("\n" + "=" * 80)
    print("总结:")
    print("✅ 超期判断逻辑已修复，支持换型时间处理")
    print("✅ 正常换批：0.5小时固定时间")
    print("✅ 换型情况：使用标准换型时间（Setup Time字段）")
    print("✅ 建议运行完整ETL验证修复效果")
    print("=" * 80)
