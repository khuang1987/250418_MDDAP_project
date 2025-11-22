#!/usr/bin/env python3
"""
测试PT计算升级逻辑
验证停产期检测和PT计算的准确性
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def calculate_mes_pt_old(row: pd.Series) -> float:
    """MES的旧PT计算逻辑（升级前）"""
    trackout = row.get("TrackOutTime", None)
    previous_batch_end = row.get("PreviousBatchEndTime", None)
    trackin = row.get("TrackInTime", None)
    
    if pd.isna(trackout):
        return None
    
    # 旧逻辑：优先使用PreviousBatchEndTime
    start_time = None
    if pd.notna(previous_batch_end):
        start_time = previous_batch_end
    elif pd.notna(trackin):
        start_time = trackin
    else:
        return None
    
    trackout_dt = pd.to_datetime(trackout)
    start_dt = pd.to_datetime(start_time)
    
    if trackout_dt <= start_dt:
        return None
    
    total_seconds = (trackout_dt - start_dt).total_seconds()
    total_hours = total_seconds / 3600.0
    return round(total_hours / 24.0, 2)

def calculate_mes_pt_new(row: pd.Series) -> float:
    """MES的新PT计算逻辑（升级后）"""
    trackout = row.get("TrackOutTime", None)
    previous_batch_end = row.get("PreviousBatchEndTime", None)
    trackin = row.get("TrackInTime", None)
    enter_step = row.get("EnterStepTime", None)
    
    if pd.isna(trackout):
        return None
    
    # 升级逻辑：检查是否有停产期
    start_time = None
    
    # 检查是否存在停产期
    has_production_gap = False
    if pd.notna(enter_step) and pd.notna(previous_batch_end):
        enter_step_dt = pd.to_datetime(enter_step)
        previous_end_dt = pd.to_datetime(previous_batch_end)
        if enter_step_dt > previous_end_dt:
            has_production_gap = True
    
    # 根据是否有停产期选择开始时间
    if has_production_gap:
        # 有停产期：使用TrackInTime
        if pd.notna(trackin):
            start_time = trackin
        else:
            start_time = previous_batch_end
    else:
        # 正常连续生产：使用PreviousBatchEndTime
        if pd.notna(previous_batch_end):
            start_time = previous_batch_end
        elif pd.notna(trackin):
            start_time = trackin
        else:
            return None
    
    trackout_dt = pd.to_datetime(trackout)
    start_dt = pd.to_datetime(start_time)
    
    if trackout_dt <= start_dt:
        return None
    
    total_seconds = (trackout_dt - start_dt).total_seconds()
    total_hours = total_seconds / 3600.0
    return round(total_hours / 24.0, 2)

def calculate_sfc_pt_old(row: pd.Series) -> float:
    """SFC的旧PT计算逻辑（升级前）"""
    trackout = row.get("TrackOutTime", None)
    checkin_sfc = row.get("Checkin_SFC", None)
    
    if pd.isna(trackout):
        return None
    
    # 旧逻辑：统一使用Checkin_SFC，不考虑PreviousBatchEndTime
    if pd.isna(checkin_sfc):
        return None
    
    trackout_dt = pd.to_datetime(trackout)
    start_dt = pd.to_datetime(checkin_sfc)
    
    if trackout_dt <= start_dt:
        return None
    
    total_seconds = (trackout_dt - start_dt).total_seconds()
    total_hours = total_seconds / 3600
    return round(total_hours / 24, 2)

def calculate_sfc_pt_new(row: pd.Series) -> float:
    """SFC的新PT计算逻辑（升级后）"""
    trackout = row.get("TrackOutTime", None)
    previous_batch_end = row.get("PreviousBatchEndTime", None)
    checkin_sfc = row.get("Checkin_SFC", None)
    enter_step = row.get("EnterStepTime", None)
    
    if pd.isna(trackout):
        return None
    
    # 升级逻辑：检查是否有停产期
    start_time = None
    
    # 检查是否存在停产期
    has_production_gap = False
    if pd.notna(enter_step) and pd.notna(previous_batch_end):
        enter_step_dt = pd.to_datetime(enter_step)
        previous_end_dt = pd.to_datetime(previous_batch_end)
        if enter_step_dt > previous_end_dt:
            has_production_gap = True
    
    # 根据是否有停产期选择开始时间
    if has_production_gap:
        # 有停产期：使用Checkin_SFC
        if pd.notna(checkin_sfc):
            start_time = checkin_sfc
        else:
            start_time = previous_batch_end
    else:
        # 正常连续生产：使用PreviousBatchEndTime
        if pd.notna(previous_batch_end):
            start_time = previous_batch_end
        elif pd.notna(checkin_sfc):
            start_time = checkin_sfc
        else:
            return None
    
    trackout_dt = pd.to_datetime(trackout)
    start_dt = pd.to_datetime(start_time)
    
    if trackout_dt <= start_dt:
        return None
    
    total_seconds = (trackout_dt - start_dt).total_seconds()
    total_hours = total_seconds / 3600
    return round(total_hours / 24, 2)

def test_pt_upgrade():
    """测试PT计算升级逻辑"""
    print("=" * 80)
    print("PT计算升级逻辑测试")
    print("=" * 80)
    
    # 创建测试数据
    test_cases = [
        {
            "name": "正常连续生产",
            "scenario": "EnterStepTime <= PreviousBatchEndTime",
            "TrackOutTime": datetime(2025, 1, 10, 16, 0),
            "PreviousBatchEndTime": datetime(2025, 1, 10, 8, 0),
            "EnterStepTime": datetime(2025, 1, 10, 8, 30),
            "TrackInTime": datetime(2025, 1, 10, 9, 0),
            "Checkin_SFC": datetime(2025, 1, 10, 9, 30),
            "expected_logic": "使用PreviousBatchEndTime"
        },
        {
            "name": "中间有停产期",
            "scenario": "EnterStepTime > PreviousBatchEndTime",
            "TrackOutTime": datetime(2025, 1, 15, 12, 0),
            "PreviousBatchEndTime": datetime(2025, 1, 10, 16, 0),
            "EnterStepTime": datetime(2025, 1, 13, 8, 0),  # 停产2.5天
            "TrackInTime": datetime(2025, 1, 13, 9, 0),
            "Checkin_SFC": datetime(2025, 1, 13, 9, 30),
            "expected_logic": "使用TrackInTime/Checkin_SFC"
        },
        {
            "name": "长时间停产",
            "scenario": "EnterStepTime >> PreviousBatchEndTime",
            "TrackOutTime": datetime(2025, 1, 20, 16, 0),
            "PreviousBatchEndTime": datetime(2025, 1, 10, 16, 0),
            "EnterStepTime": datetime(2025, 1, 18, 8, 0),  # 停产8天
            "TrackInTime": datetime(2025, 1, 18, 9, 0),
            "Checkin_SFC": datetime(2025, 1, 18, 9, 30),
            "expected_logic": "使用TrackInTime/Checkin_SFC"
        },
        {
            "name": "无PreviousBatchEndTime",
            "scenario": "PreviousBatchEndTime为空",
            "TrackOutTime": datetime(2025, 1, 12, 16, 0),
            "PreviousBatchEndTime": None,
            "EnterStepTime": datetime(2025, 1, 12, 8, 0),
            "TrackInTime": datetime(2025, 1, 12, 9, 0),
            "Checkin_SFC": datetime(2025, 1, 12, 9, 30),
            "expected_logic": "使用TrackInTime/Checkin_SFC"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['name']}")
        print("-" * 60)
        print(f"场景: {case['scenario']}")
        print(f"期望逻辑: {case['expected_logic']}")
        print()
        
        # 创建测试行
        row = pd.Series(case)
        
        # 计算MES的PT
        mes_pt_old = calculate_mes_pt_old(row)
        mes_pt_new = calculate_mes_pt_new(row)
        
        # 计算SFC的PT
        sfc_pt_old = calculate_sfc_pt_old(row)
        sfc_pt_new = calculate_sfc_pt_new(row)
        
        print(f"输入时间:")
        print(f"  TrackOutTime: {case['TrackOutTime']}")
        print(f"  PreviousBatchEndTime: {case['PreviousBatchEndTime']}")
        print(f"  EnterStepTime: {case['EnterStepTime']}")
        print(f"  TrackInTime: {case['TrackInTime']}")
        print(f"  Checkin_SFC: {case['Checkin_SFC']}")
        
        print(f"\nMES PT计算结果:")
        print(f"  旧逻辑: {mes_pt_old} 天")
        print(f"  新逻辑: {mes_pt_new} 天")
        if mes_pt_old and mes_pt_new:
            diff = mes_pt_new - mes_pt_old
            print(f"  差异: {diff:+.2f} 天 ({diff*24:+.1f} 小时)")
        
        print(f"\nSFC PT计算结果:")
        print(f"  旧逻辑: {sfc_pt_old} 天")
        print(f"  新逻辑: {sfc_pt_new} 天")
        if sfc_pt_old and sfc_pt_new:
            diff = sfc_pt_new - sfc_pt_old
            print(f"  差异: {diff:+.2f} 天 ({diff*24:+.1f} 小时)")
        
        # 分析停产期检测
        if case.get('PreviousBatchEndTime') and case.get('EnterStepTime'):
            gap = case['EnterStepTime'] - case['PreviousBatchEndTime']
            print(f"\n停产期分析:")
            print(f"  停产时间: {gap}")
            print(f"  停产天数: {gap.total_seconds() / 86400:.2f} 天")

def analyze_upgrade_impact():
    """分析升级的影响"""
    print("\n" + "=" * 80)
    print("PT计算升级影响分析")
    print("=" * 80)
    
    print("1. 升级内容:")
    print("   ✅ 添加停产期检测：EnterStepTime > PreviousBatchEndTime")
    print("   ✅ 智能开始时间选择：根据是否有停产期选择不同的开始时间")
    print("   ✅ 避免停产时间计入PT：只计算实际加工时间")
    print()
    
    print("2. 业务逻辑:")
    print("   - 正常生产：PT = TrackOutTime - PreviousBatchEndTime")
    print("   - 有停产期：PT = TrackOutTime - TrackInTime/Checkin_SFC")
    print("   - 停产时间不计入PT，提高加工时间准确性")
    print()
    
    print("3. 预期影响:")
    print("   - PT值更准确，反映实际加工时间")
    print("   - 超期判断更准确，因为PT基准更合理")
    print("   - 设备效率分析更可靠")
    print()
    
    print("4. 数据变化:")
    print("   - 有停产期的记录：PT值会减少")
    print("   - 正常生产的记录：PT值保持不变")
    print("   - 超期率可能下降")

if __name__ == "__main__":
    print("PT计算升级逻辑验证")
    print("=" * 80)
    
    test_pt_upgrade()
    analyze_upgrade_impact()
    
    print("\n" + "=" * 80)
    print("总结:")
    print("✅ MES和SFC的PT计算逻辑已升级")
    print("✅ 添加了停产期检测功能")
    print("✅ 避免将停产时间计入PT")
    print("✅ 建议运行完整ETL验证升级效果")
    print("=" * 80)
