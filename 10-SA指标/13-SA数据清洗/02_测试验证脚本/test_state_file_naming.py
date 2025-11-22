#!/usr/bin/env python3
"""
测试ETL状态文件命名规范
验证MES和SFC使用正确的状态文件名
"""

import sys
import os
import yaml

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return None

def test_state_file_naming():
    """测试状态文件命名规范"""
    print("=" * 80)
    print("ETL状态文件命名规范验证")
    print("=" * 80)
    print()
    
    # 测试MES配置
    print("1. MES系统配置验证")
    print("-" * 40)
    mes_config = load_config("config/config_mes_batch_report.yaml")
    if mes_config:
        mes_state_file = mes_config.get("incremental", {}).get("state_file", "")
        print(f"状态文件路径: {mes_state_file}")
        
        # 检查文件名
        if "etl_mes_state.json" in mes_state_file:
            print("✅ MES状态文件命名正确")
        else:
            print("❌ MES状态文件命名不正确")
            print(f"   期望包含: etl_mes_state.json")
    else:
        print("❌ 无法加载MES配置文件")
    print()
    
    # 测试SFC配置
    print("2. SFC系统配置验证")
    print("-" * 40)
    sfc_config = load_config("config/config_sfc_batch_report.yaml")
    if sfc_config:
        sfc_state_file = sfc_config.get("incremental", {}).get("state_file", "")
        print(f"状态文件路径: {sfc_state_file}")
        
        # 检查文件名
        if "etl_sfc_state.json" in sfc_state_file:
            print("✅ SFC状态文件命名正确")
        else:
            print("❌ SFC状态文件命名不正确")
            print(f"   期望包含: etl_sfc_state.json")
    else:
        print("❌ 无法加载SFC配置文件")
    print()
    
    # 测试代码中的默认值
    print("3. 代码默认值验证")
    print("-" * 40)
    
    # 检查MES代码
    try:
        with open("etl_dataclean_mes_batch_report.py", 'r', encoding='utf-8') as f:
            mes_code = f.read()
            if 'publish/etl_mes_state.json' in mes_code:
                print("✅ MES代码中的默认状态文件名正确")
            else:
                print("❌ MES代码中的默认状态文件名不正确")
    except Exception as e:
        print(f"❌ 无法读取MES代码文件: {e}")
    
    # 检查SFC代码
    try:
        with open("etl_dataclean_sfc_batch_report.py", 'r', encoding='utf-8') as f:
            sfc_code = f.read()
            if 'publish/etl_sfc_state.json' in sfc_code:
                print("✅ SFC代码中的默认状态文件名正确")
            else:
                print("❌ SFC代码中的默认状态文件名不正确")
    except Exception as e:
        print(f"❌ 无法读取SFC代码文件: {e}")
    print()
    
    # 总结
    print("=" * 80)
    print("命名规范总结")
    print("=" * 80)
    print("✅ MES系统: etl_mes_state.json")
    print("✅ SFC系统: etl_sfc_state.json")
    print("✅ 命名规范: etl_{system}_state.json")
    print()
    print("建议:")
    print("1. 运行ETL脚本验证新的状态文件是否正确生成")
    print("2. 删除旧的etl_state.json文件（如果存在）")
    print("3. 更新相关文档和操作手册")
    print("=" * 80)

if __name__ == "__main__":
    test_state_file_naming()
