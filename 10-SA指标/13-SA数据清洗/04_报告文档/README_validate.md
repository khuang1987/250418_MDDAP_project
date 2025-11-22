# SA指标数据清洗结果验证工具

## 📋 概述

`etl_validate_sa_results.py` 是一个专门用于验证SA指标ETL数据清洗结果正确性的工具。该工具通过抽样检查、统计分析和业务逻辑验证，确保数据清洗过程的准确性和完整性。

## 🎯 验证功能

### 1. SFC批次报工数据验证
- **时间计算验证**: 抽样检查 LT、PT、ST 计算准确性
- **标准时间统计**: 验证 EH_machine(s) 等标准时间字段匹配情况
- **数据完整性检查**: 确保关键字段的非空率

### 2. MES批次报工数据验证
- **SFC数据合并统计**: 检查MES与SFC数据合并的成功率
- **标准时间匹配验证**: 验证标准时间字段匹配覆盖率
- **DueTime逻辑检查**: 确保交期时间计算正确
- **PreviousBatchEndTime验证**: 检查批次时间序列逻辑

### 3. SAP Routing标准时间数据验证
- **关键字段完整性**: 检查Material Number、Operation、Group字段
- **标准时间数据合理性**: 验证EH_machine(s)、EH_labor(s)、OEE数值范围
- **数据唯一性检查**: 检测Material Number + Operation重复记录

## 🚀 使用方法

### 基本使用
```bash
# 运行完整验证
python etl_validate_sa_results.py
```

### 输出结果
- **控制台输出**: 验证结果摘要
- **报告文件**: `logs/validation_report_sa_YYYYMMDD_HHMMSS.txt`
- **日志文件**: `logs/etl_validate_sa.log`

## ⚙️ 配置文件

验证参数通过 `config/config_validate_sa.yaml` 配置：

```yaml
# 验证参数配置
validation:
  sample_size: 10          # 抽样验证数量
  time_tolerance: 0.1      # 时间计算误差容忍度（小时）
  
# 数据质量评分
quality_score:
  penalty_per_error: 2     # 每个错误扣除的分数
  passing_score: 80        # 最低合格分数
```

## 📊 验证报告解读

### 状态标识
- ✅ **验证通过**: 该项数据验证正常
- ❌ **发现问题**: 该项数据验证发现错误
- ⚠️ **警告**: 需要注意的问题

### 关键指标
- **数据完整性**: 关键字段的非空率统计
- **匹配率**: 标准时间数据匹配成功率
- **合并率**: SFC与MES数据合并成功率
- **数据质量评分**: 0-100分的综合评分

### 常见问题类型
1. **时间计算差异**: LT/PT/ST计算误差超过容忍度
2. **DueTime计算错误**: 交期时间早于报工时间
3. **PreviousBatchEndTime计算错误**: 批次时间序列逻辑错误
4. **缺少关键字段**: 必需字段不存在或为空

## 🔧 自定义配置

### 修改验证参数
编辑 `config/config_validate_sa.yaml`：

```yaml
# 增加抽样数量
validation:
  sample_size: 20          # 从10增加到20
  
# 调整误差容忍度
validation:
  time_tolerance: 0.05     # 从0.1小时减少到0.05小时
```

### 添加验证字段
在配置文件中添加新的验证字段：

```yaml
sfc_validation:
  required_fields:
    - "BatchNumber"
    - "Operation"
    - "TrackOutTime"
    - "machine"
    - "NewField"           # 添加新字段
```

## 📈 验证结果分析

### 优秀结果示例
```
🎉 所有数据验证通过！清洗结果正确。
数据质量评分: 100/100
```

### 需要关注的结果示例
```
⚠️ 发现 5 个问题，建议详细检查。
数据质量评分: 90/100
```

### 关键阈值建议
- **数据完整性**: >95%
- **标准时间匹配率**: >80%
- **SFC数据合并率**: >70%
- **数据质量评分**: >85分

## 🛠️ 故障排除

### 常见错误及解决方案

1. **文件不存在错误**
   ```
   FileNotFoundError: 数据文件不存在
   ```
   **解决**: 确保ETL流程已完成，输出文件存在

2. **配置文件错误**
   ```
   yaml.scanner.ScannerError
   ```
   **解决**: 检查YAML配置文件格式是否正确

3. **内存不足**
   ```
   MemoryError: Unable to allocate array
   ```
   **解决**: 减少sample_size配置值

## 📝 最佳实践

1. **定期验证**: 建议每次ETL运行后都进行验证
2. **配置备份**: 保存不同版本的配置文件
3. **报告归档**: 保留历史验证报告用于趋势分析
4. **阈值调整**: 根据业务需求调整验证阈值

## 🔄 集成到ETL流程

可以在 `run_all_etl.bat` 中添加验证步骤：

```batch
echo Step 3: Validating ETL Results
python etl_validate_sa_results.py
if errorlevel 1 (
    echo ETL Validation Failed!
    pause
    exit /b 1
)
```

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件：`logs/etl_validate_sa.log`
2. 配置文件：`config/config_validate_sa.yaml`
3. 数据文件路径是否正确
4. Python环境是否完整

---

**版本**: 1.0  
**更新日期**: 2025-11-20  
**维护者**: ETL开发团队
