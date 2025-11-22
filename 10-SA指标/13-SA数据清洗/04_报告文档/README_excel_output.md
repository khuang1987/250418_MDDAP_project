# ETL数据Excel输出功能说明

## 📋 功能概述

为了方便数据完整性检查，所有ETL脚本现在都支持在输出Parquet文件的同时，自动生成对应的Excel文件到publish文件夹的excel子目录中。

## 🎯 功能特点

### 1. 自动Excel输出
- **同步生成**: 每次保存Parquet文件时自动生成Excel文件
- **相同命名**: Excel文件名与Parquet文件名保持一致（扩展名不同）
- **独立目录**: Excel文件保存在`publish/excel/`子目录中

### 2. 智能数据处理
- **大文件处理**: 数据量超过配置限制时，只保存前N行记录
- **格式优化**: 自动处理日期、数字等字段格式
- **统计信息**: 可选生成数据统计工作表

### 3. 灵活配置
- **可开关**: 通过配置文件控制是否启用Excel输出
- **自定义**: 可配置最大行数、是否包含统计信息等

## 📁 文件结构

```
publish/
├── excel/                          # Excel输出目录
│   ├── SFC_batch_report_latest.xlsx
│   ├── MES_batch_report_latest.xlsx
│   └── SAP_Routing_latest.xlsx
├── SFC_batch_report_latest.parquet  # Parquet文件
├── MES_batch_report_latest.parquet
└── SAP_Routing_latest.parquet
```

## ⚙️ 配置说明

### 在配置文件中添加Excel设置：

```yaml
output:
  # Parquet压缩配置
  parquet:
    compression: "snappy"
  
  # Excel输出配置
  excel:
    enabled: true           # 是否启用Excel输出
    max_rows: 10000        # Excel文件最大行数（避免文件过大）
    include_stats: true    # 是否包含统计信息工作表
```

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用Excel输出功能 |
| `max_rows` | int | 10000 | Excel文件最大行数，超过则截取 |
| `include_stats` | bool | true | 是否在Excel中添加统计信息工作表 |

## 📊 Excel文件内容

### 工作表1：数据
- 包含处理后的完整数据（或前N行）
- 保持与Parquet文件相同的字段结构
- 自动优化数据类型和格式

### 工作表2：统计信息（可选）
| 字段 | 说明 |
|------|------|
| 字段名 | 数据列名称 |
| 数据类型 | 列的数据类型 |
| 总记录数 | 数据总行数 |
| 非空记录数 | 非空值的记录数 |
| 空值记录数 | 空值的记录数 |
| 非空率 | 非空值占比 |
| 唯一值数量 | 唯一值的个数 |
| 最小值 | 数值字段的最小值 |
| 最大值 | 数值字段的最大值 |
| 平均值 | 数值字段的平均值 |
| 中位数 | 数值字段的中位数 |

## 🚀 使用方法

### 1. 启用Excel输出
在配置文件中设置：
```yaml
output:
  excel:
    enabled: true
```

### 2. 运行ETL脚本
```bash
# 运行任意ETL脚本
python etl_dataclean_sfc_batch_report.py
python etl_dataclean_mes_batch_report.py
python etl_dataclean_sap_routing.py
```

### 3. 查看Excel文件
Excel文件会自动保存到：`publish/excel/`目录

## 📈 数据完整性检查

### 1. 基本检查
- **记录数量**: 对比Excel和原始数据的记录数
- **字段完整性**: 检查关键字段的非空率
- **数据类型**: 确认字段类型转换正确

### 2. 业务逻辑检查
- **时间字段**: 验证时间序列的合理性
- **数值范围**: 检查数值是否在预期范围内
- **关联关系**: 验证数据间的关联逻辑

### 3. 质量评估
- **唯一性**: 检查重复记录情况
- **完整性**: 评估数据缺失情况
- **一致性**: 验证跨表数据一致性

## 🛠️ 故障排除

### 常见问题

1. **Excel文件未生成**
   - 检查配置文件中`excel.enabled`是否为`true`
   - 确认已安装`openpyxl`包：`pip install openpyxl`

2. **Excel文件过大**
   - 调整`max_rows`配置参数
   - 考虑分批次检查数据

3. **数据格式问题**
   - 查看统计信息工作表了解字段详情
   - 检查日志中的数据转换警告

4. **权限错误**
   - 确保对publish目录有写入权限
   - 检查Excel文件是否被其他程序打开

## 📋 最佳实践

### 1. 定期检查
- 每次ETL运行后检查Excel文件
- 关注统计信息中的异常指标
- 建立数据质量检查清单

### 2. 版本管理
- 保留重要时间点的Excel文件
- 对比不同版本的数据变化
- 建立数据质量趋势分析

### 3. 团队协作
- 共享Excel文件给业务人员验证
- 收集数据质量反馈
- 持续优化ETL流程

## 🔄 集成验证工具

Excel输出功能与数据验证工具`etl_validate_sa_results.py`配合使用：

1. **ETL处理** → 生成Parquet + Excel文件
2. **Excel检查** → 人工验证数据完整性
3. **验证工具** → 自动化数据质量检查
4. **问题修复** → 根据检查结果优化ETL

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件：`logs/etl_*.log`
2. 配置文件：`config/config_*.yaml`
3. 依赖包：确保已安装`openpyxl`
4. 文件权限：确保对输出目录有写入权限

---

**版本**: 1.0  
**更新日期**: 2025-11-20  
**维护者**: ETL开发团队
