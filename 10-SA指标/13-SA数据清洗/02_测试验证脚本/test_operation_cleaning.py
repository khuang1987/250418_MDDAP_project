"""
测试MES工序名称清洗功能
验证新的清洗合并规则是否正确实现
"""

import pandas as pd
import sys
import os

# 添加当前目录到路径，以便导入etl_dataclean_mes_batch_report
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl_dataclean_mes_batch_report import standardize_operation_name

def test_operation_cleaning():
    """测试工序名称清洗功能"""
    
    # 测试数据：包含所有需要清洗的工序类型
    test_cases = [
        # 需要合并的工序组
        ("CZM 线切割", "线切割"),
        ("CZM 线切割（可外协）", "线切割"),
        ("CZM 线切割-慢丝（可外协）", "线切割"),
        ("CZM 数控铣", "数控铣"),
        ("CZM 数控铣（可外协）", "数控铣"),
        ("CZM 纵切车", "纵切车"),
        ("CZM 纵切车（可外协）", "纵切车"),
        ("CZM 数控车", "数控车"),
        ("CZM 数控车（可外协）", "数控车"),
        ("CZM 车削", "车削"),
        ("CZM 车削（可外协）", "车削"),
        ("CZM 锯", "锯"),
        ("CZM 锯（可外协）", "锯"),
        
        # 保持独立的工序
        ("CZM 清洗", "清洗"),
        ("CZM 终检", "终检"),
        ("CZM 钳工", "钳工"),
        ("CZM 钝化", "钝化"),
        ("CZM 点钝化", "点钝化"),
        ("CZM 喷砂", "喷砂"),
        ("CZM 微喷砂", "微喷砂"),
        ("CZM 包装", "包装"),
        ("CZM 电解", "电解"),
        ("CZM 电解去氢", "电解去氢"),
        ("CZM 抛光", "抛光"),
        ("CZM 激光打标", "激光打标"),
        ("CZM 真空热处理", "真空热处理"),
        ("CZM 真空热处理（可外协）", "真空热处理"),
        ("CZM 非真空热处理", "非真空热处理"),
        ("CZM 研磨", "研磨"),
        ("CZM 无心磨", "无心磨"),
        ("CZM 无心磨（可外协）", "无心磨"),
        ("CZM Preparation step", "Preparation step"),
        ("CZM 五轴磨（可外协）", "五轴磨"),
        ("CZM 折弯", "折弯"),
        ("CZM 氩弧焊", "氩弧焊"),
        ("CZM 注塑", "注塑"),
        ("CZM 涂层（外协）", "涂层"),
        ("CZM 涂色", "涂色"),
        ("CZM 深孔钻", "深孔钻"),
        ("CZM 深孔钻（可外协）", "深孔钻"),
        ("CZM 激光焊接", "激光焊接"),
        ("CZM 装配", "装配"),
        ("CZM 阳极氧化（外协）", "阳极氧化"),
        ("CZM 电火花（外协）", "电火花"),
        ("CZM 镀铬（外协）", "镀铬"),
        
        # 边界情况
        ("", ""),
        (None, ""),
        ("   CZM 清洗   ", "清洗"),
        ("未知工序", "未知工序"),
    ]
    
    print("🧪 开始测试MES工序名称清洗功能")
    print("=" * 60)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (input_name, expected) in enumerate(test_cases, 1):
        result = standardize_operation_name(input_name)
        status = "✅" if result == expected else "❌"
        
        if result != expected:
            print(f"{status} 测试 {i:2d}: '{input_name}' -> '{result}' (期望: '{expected}')")
        else:
            success_count += 1
            
    print("=" * 60)
    print(f"测试完成: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！工序清洗功能正常")
    else:
        print("⚠️  部分测试失败，请检查清洗逻辑")
        
    return success_count == total_count

def test_with_real_data():
    """使用真实数据测试清洗功能"""
    print("\n📊 使用真实数据验证清洗效果")
    print("=" * 60)
    
    # 读取真实数据
    data_path = r"c:\Users\huangk14\OneDrive - Medtronic PLC\Huangkai Files\B1_Project\250418_MDDAP_project\10-SA指标\11数据模板\Product Output -CZM -FY26.csv"
    
    try:
        df = pd.read_csv(data_path, low_memory=False)
        if 'Step_Name' not in df.columns:
            print("❌ 未找到Step_Name列")
            return False
            
        # 应用清洗函数
        df['Cleaned_Operation'] = df['Step_Name'].apply(standardize_operation_name)
        
        # 统计清洗前后的工序数量
        original_count = df['Step_Name'].nunique()
        cleaned_count = df['Cleaned_Operation'].nunique()
        
        print(f"原始工序数量: {original_count}")
        print(f"清洗后工序数量: {cleaned_count}")
        print(f"减少工序数量: {original_count - cleaned_count}")
        print(f"减少比例: {((original_count - cleaned_count) / original_count * 100):.1f}%")
        
        print("\n📋 清洗后工序分布:")
        cleaned_stats = df['Cleaned_Operation'].value_counts()
        for i, (op_name, count) in enumerate(cleaned_stats.head(15).items(), 1):
            percentage = count / len(df) * 100
            print(f"{i:2d}. {op_name}: {count:5d}条 ({percentage:4.1f}%)")
            
        # 验证合并组
        print("\n🔍 验证合并组:")
        merge_groups = {
            "线切割": ["CZM 线切割", "CZM 线切割（可外协）", "CZM 线切割-慢丝（可外协）"],
            "数控铣": ["CZM 数控铣", "CZM 数控铣（可外协）"],
            "纵切车": ["CZM 纵切车", "CZM 纵切车（可外协）"],
            "数控车": ["CZM 数控车", "CZM 数控车（可外协）"],
            "车削": ["CZM 车削", "CZM 车削（可外协）"],
            "锯": ["CZM 锯", "CZM 锯（可外协）"]
        }
        
        for target_op, source_ops in merge_groups.items():
            total_count = 0
            for source_op in source_ops:
                count = df[df['Step_Name'] == source_op].shape[0]
                total_count += count
                if count > 0:
                    print(f"  {source_op}: {count}条")
            
            cleaned_count = df[df['Cleaned_Operation'] == target_op].shape[0]
            print(f"  -> {target_op}: {cleaned_count}条 (总计: {total_count}条)")
            
            if total_count != cleaned_count:
                print(f"  ❌ 数量不匹配！")
            else:
                print(f"  ✅ 合并正确")
                
        return True
        
    except Exception as e:
        print(f"❌ 读取数据失败: {e}")
        return False

if __name__ == "__main__":
    # 运行单元测试
    unit_test_passed = test_operation_cleaning()
    
    # 运行真实数据测试
    real_test_passed = test_with_real_data()
    
    print("\n" + "=" * 60)
    if unit_test_passed and real_test_passed:
        print("🎉 所有测试通过！工序清洗功能可以投入使用")
    else:
        print("⚠️  测试未完全通过，请检查实现")
