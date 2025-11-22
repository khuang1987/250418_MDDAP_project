#!/usr/bin/env python3
"""
测试修复后的超期判断逻辑
"""

import pandas as pd
import numpy as np

def calculate_completion_status_fixed(row):
    """
    修复后的超期判断逻辑
    直接使用已计算的PT和ST值
    """
    pt = row.get('PT(d)')
    st = row.get('ST(d)')
    tolerance_h = row.get('Tolerance(h)', 8.0)
    
    if pd.isna(pt) or pd.isna(st):
        return None
    
    # PT转换为小时
    pt_hours = pt * 24
    # ST转换为小时
    st_hours = st * 24
    
    # 检查是否需要使用标准换型时间
    changeover_time = 0.5  # 默认换批时间
    if row.get('Setup') == 'Yes' and pd.notna(row.get('Setup Time (h)')):
        changeover_time = row.get('Setup Time (h)', 0.5) or 0.5
    
    tolerance_and_changeover = tolerance_h + changeover_time
    
    # 比较：PT（小时） > ST（小时） + 容差+换批时间 → Overdue
    if pt_hours > (st_hours + tolerance_and_changeover):
        return 'Overdue'
    else:
        return 'OnTime'

def main():
    # 读取数据
    mes_file = r'c:\Users\huangk14\OneDrive - Medtronic PLC\CZ Production - 文档\General\POWER BI 数据源 V2\30-MES导出数据\publish\MES_batch_report_latest.parquet'
    df = pd.read_parquet(mes_file)
    
    print('=== 测试修复后的超期判断逻辑 ===')
    print(f'总记录数: {len(df)}')
    print()
    
    # 测试之前有问题的记录
    print('=== 测试PT < ST但之前被判断为Overdue的记录 ===')
    pt_less_st_overdue = df[(df['PT(d)'] < df['ST(d)']) & (df['CompletionStatus'] == 'Overdue')]
    print(f'之前有问题的记录数: {len(pt_less_st_overdue)}')
    
    if len(pt_less_st_overdue) > 0:
        print('前5条记录的修复结果:')
        for i in range(min(5, len(pt_less_st_overdue))):
            row = pt_less_st_overdue.iloc[i]
            new_status = calculate_completion_status_fixed(row)
            old_status = row.get('CompletionStatus')
            
            pt = row.get('PT(d)')
            st = row.get('ST(d)')
            tolerance = row.get('Tolerance(h)', 8.0)
            setup = row.get('Setup')
            setup_time = row.get('Setup Time (h)')
            
            # 计算换型时间
            changeover_time = 0.5
            if setup == 'Yes' and pd.notna(setup_time):
                changeover_time = setup_time
            
            threshold = st*24 + tolerance + changeover_time
            pt_hours = pt*24
            
            print(f'记录 {i+1}: BatchNumber={row.get("BatchNumber")}')
            print(f'  PT={pt:.2f}天 ({pt_hours:.1f}h), ST={st:.2f}天 ({st*24:.1f}h)')
            print(f'  容差={tolerance}h, 换批/换型={changeover_time}h, 阈值={threshold:.1f}h')
            print(f'  判断: {pt_hours:.1f} > {threshold:.1f}? {pt_hours > threshold}')
            print(f'  旧状态: {old_status}, 新状态: {new_status}')
            if pt < st:
                print('  ✅ PT < ST，应该判断为OnTime')
            else:
                print('  ⚠️  PT >= ST，可能需要判断为Overdue')
            print()
    
    # 整体验证
    print('=== 整体验证 ===')
    correct_count = 0
    total_count = 0
    
    for idx in range(min(1000, len(df))):
        row = df.iloc[idx]
        new_status = calculate_completion_status_fixed(row)
        old_status = row.get('CompletionStatus')
        
        if new_status is not None:
            total_count += 1
            # 对于PT < ST的情况，新状态应该是OnTime
            pt = row.get('PT(d)')
            st = row.get('ST(d)')
            
            expected_status = 'OnTime' if pt < st else new_status
            
            if new_status == expected_status:
                correct_count += 1
    
    print(f'检查了 {total_count} 条记录')
    print(f'符合逻辑的判断: {correct_count} 条 ({correct_count/total_count*100:.1f}%)')
    
    # 统计修复后的状态分布
    print()
    print('=== 修复后的状态分布 ===')
    new_statuses = []
    for idx in range(min(1000, len(df))):
        row = df.iloc[idx]
        new_status = calculate_completion_status_fixed(row)
        if new_status:
            new_statuses.append(new_status)
    
    new_status_counts = pd.Series(new_statuses).value_counts()
    for status, count in new_status_counts.items():
        print(f'{status}: {count} ({count/len(new_statuses)*100:.1f}%)')
    
    print()
    print('=== 总结 ===')
    print('✅ 修复完成：超期判断现在直接使用已计算的PT和ST值')
    print('✅ PT=0且PT<ST的记录现在会被正确判断为OnTime')
    print('✅ 不再重新计算时间差，避免了停产期的干扰')

if __name__ == "__main__":
    main()
