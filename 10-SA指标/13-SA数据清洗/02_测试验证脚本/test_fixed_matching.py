"""
测试修复后的数据匹配效果
"""

import os
import sys
import pandas as pd
import logging

# 添加核心ETL程序目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '01_核心ETL程序'))
from etl_utils import load_config
from etl_dataclean_mes_batch_report import process_mes_data

def test_fixed_matching():
    """测试修复后的数据匹配效果"""
    
    # 加载配置
    cfg = load_config(os.path.join(os.path.dirname(__file__), '..', '03_配置文件', 'config', 'config_mes_batch_report.yaml'))
    
    print("测试修复后的数据匹配效果")
    print("="*50)
    
    # 读取MES数据
    mes_path = cfg.get("source", {}).get("mes_path", "")
    if os.path.exists(mes_path):
        mes_df = pd.read_excel(mes_path)
        print(f"原始 MES数据行数: {len(mes_df)}")
        
        # 使用修复后的process_mes_data函数
        processed_mes = process_mes_data(mes_df, cfg)
        print(f"处理后 MES数据行数: {len(processed_mes)}")
        
        print(f"\n处理后 MES Operation字段:")
        print(f"  数据类型: {processed_mes['Operation'].dtype}")
        print(f"  唯一值数量: {processed_mes['Operation'].nunique()}")
        unique_ops = [op for op in processed_mes['Operation'].unique() if op is not None]
        print(f"  唯一值: {sorted(unique_ops)}")
        
        # 读取SFC数据
        sfc_latest_file = cfg.get("source", {}).get("sfc_latest_file", "")
        if os.path.exists(sfc_latest_file):
            sfc_df = pd.read_parquet(sfc_latest_file)
            print(f"\nSFC数据行数: {len(sfc_df)}")
            
            print(f"SFC Operation字段:")
            print(f"  数据类型: {sfc_df['Operation'].dtype}")
            print(f"  唯一值数量: {sfc_df['Operation'].nunique()}")
            unique_sfc_ops = [op for op in sfc_df['Operation'].unique() if op is not None]
            print(f"  唯一值: {sorted(unique_sfc_ops)}")
            
            # 检查匹配情况
            print(f"\n匹配检查:")
            mes_ops_set = set(unique_ops)
            sfc_ops_set = set(unique_sfc_ops)
            
            common_ops = mes_ops_set.intersection(sfc_ops_set)
            print(f"共同Operation数量: {len(common_ops)}")
            print(f"匹配率: {len(common_ops) / len(mes_ops_set) * 100:.1f}%")
            
            # 模拟SFC数据合并
            print(f"\n模拟SFC数据合并:")
            
            # 创建合并键
            sfc_keys = set(zip(sfc_df['BatchNumber'], sfc_df['Operation']))
            mes_keys = set(zip(processed_mes['BatchNumber'], processed_mes['Operation']))
            
            print(f"SFC数据匹配键数量: {len(sfc_keys)}")
            print(f" MES数据匹配键数量: {len(mes_keys)}")
            
            common_keys = sfc_keys.intersection(mes_keys)
            print(f"共同匹配键数量: {len(common_keys)}")
            print(f"完整匹配率: {len(common_keys) / len(mes_keys) * 100:.1f}%")
            
            # 显示一些不匹配的例子
            mes_only_keys = mes_keys - sfc_keys
            print(f"\n仅在 MES中的匹配键（前5个）:")
            for key in list(mes_only_keys)[:5]:
                print(f"  BatchNumber: {key[0]}, Operation: {key[1]}")

if __name__ == "__main__":
    test_fixed_matching()
