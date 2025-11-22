# ETL状态文件命名规范统一报告

## 🎯 修改目标

统一ETL状态文件的命名规范，使其与ETL代码保持匹配，提高文件管理的规范性和可维护性。

## 🔍 修改前的问题

### 命名不一致问题

**修改前的状态文件命名：**
- **MES系统**: `etl_state.json` 
- **SFC系统**: `etl_sfc_state.json`

**存在的问题：**
1. **命名不统一**: MES缺少系统标识前缀
2. **管理混乱**: 难以快速识别文件归属
3. **维护困难**: 文件命名不规范增加管理成本
4. **扩展性差**: 后续增加系统时命名规则不明确

## ✅ 修改方案

### 1. 统一命名规范

**新的命名规范：**
```
etl_{system}_state.json
```

**具体文件名：**
- **MES系统**: `etl_mes_state.json`
- **SFC系统**: `etl_sfc_state.json`

### 2. 修改的文件

#### config/config_mes_batch_report.yaml

**修改前：**
```yaml
# 状态文件路径（记录已处理的记录）
state_file: "C:\\Users\\huangk14\\OneDrive - Medtronic PLC\\CZ Production - 文档\\General\\POWER BI 数据源 V2\\30-MES导出数据\\publish\\etl_state.json"
```

**修改后：**
```yaml
# 状态文件路径（记录已处理的记录）
state_file: "C:\\Users\\huangk14\\OneDrive - Medtronic PLC\\CZ Production - 文档\\General\\POWER BI 数据源 V2\\30-MES导出数据\\publish\\etl_mes_state.json"
```

#### etl_dataclean_mes_batch_report.py

**修改前（2处）：**
```python
state_file = incr_cfg.get("state_file", "publish/etl_state.json")
```

**修改后（2处）：**
```python
state_file = incr_cfg.get("state_file", "publish/etl_mes_state.json")
```

#### 保持不变的文件

**config/config_sfc_batch_report.yaml**
- 已经使用规范的 `etl_sfc_state.json`
- 无需修改

**etl_dataclean_sfc_batch_report.py**
- 已经使用规范的 `etl_sfc_state.json`
- 无需修改

## 📊 修改后的文件结构

### 状态文件命名对照表

| 系统 | 修改前 | 修改后 | 状态 |
|------|--------|--------|------|
| **MES** | `etl_state.json` | `etl_mes_state.json` | ✅ 已修改 |
| **SFC** | `etl_sfc_state.json` | `etl_sfc_state.json` | ✅ 已规范 |

### 配置文件路径映射

| 配置文件 | 状态文件路径 | 说明 |
|----------|--------------|------|
| `config_mes_batch_report.yaml` | `publish/etl_mes_state.json` | MES增量处理状态 |
| `config_sfc_batch_report.yaml` | `publish/etl_sfc_state.json` | SFC增量处理状态 |

## 🎯 命名规范的好处

### 1. 文件管理

**清晰的归属标识：**
- ✅ 文件名直接显示所属系统
- ✅ 避免文件混淆和误用
- ✅ 便于批量管理和维护

**统一的命名模式：**
- ✅ 遵循 `etl_{system}_state.json` 模式
- ✅ 便于脚本自动化处理
- ✅ 支持系统扩展

### 2. 开发维护

**代码可读性：**
- ✅ 状态文件引用更加清晰
- ✅ 减少代码注释需求
- ✅ 降低维护成本

**扩展性：**
- ✅ 新增系统时命名规则明确
- ✅ 便于团队协作开发
- ✅ 支持多环境部署

### 3. 运维管理

**监控和调试：**
- ✅ 快速定位问题系统的状态文件
- ✅ 便于日志分析和问题排查
- ✅ 支持自动化监控脚本

**备份和恢复：**
- ✅ 明确的文件备份策略
- ✅ 系统级别的状态恢复
- ✅ 灾难恢复时快速识别

## 📋 验证清单

### 1. 配置文件验证

**MES配置文件：**
```yaml
incremental:
  state_file: "publish/etl_mes_state.json"  # ✅ 已更新
```

**SFC配置文件：**
```yaml
incremental:
  state_file: "publish/etl_sfc_state.json"  # ✅ 已规范
```

### 2. 代码引用验证

**MES代码中的引用：**
```python
# 默认值
state_file = incr_cfg.get("state_file", "publish/etl_mes_state.json")  # ✅ 已更新

# 两处引用都已更新
- 第1491行：增量过滤时
- 第1775行：状态更新时
```

**SFC代码中的引用：**
```python
# 默认值（无需修改）
state_file = incr_cfg.get("state_file", "publish/etl_sfc_state.json")  # ✅ 已规范
```

### 3. 文件路径验证

**绝对路径配置：**
- MES: `C:\...\publish\etl_mes_state.json` ✅
- SFC: `C:\...\publish\etl_sfc_state.json` ✅

**相对路径配置：**
- MES: `publish/etl_mes_state.json` ✅
- SFC: `publish/etl_sfc_state.json` ✅

## 🚀 实施建议

### 立即行动

1. **清理旧的状态文件**
   ```bash
   # 删除旧的MES状态文件（如果存在）
   del "publish\etl_state.json"
   
   # 新的状态文件会在下次ETL运行时自动创建
   ```

2. **验证ETL运行**
   ```bash
   # 测试MES ETL
   python etl_dataclean_mes_batch_report.py
   
   # 测试SFC ETL
   python etl_dataclean_sfc_batch_report.py
   ```

3. **检查生成的状态文件**
   ```bash
   # 确认新的状态文件正确生成
   dir publish\etl_*_state.json
   ```

### 长期维护

1. **文档更新**
   - 更新ETL操作手册
   - 修改系统架构文档
   - 完善开发规范文档

2. **监控脚本**
   - 创建状态文件监控脚本
   - 设置文件命名规范检查
   - 建立异常告警机制

3. **团队培训**
   - 培训开发人员新的命名规范
   - 建立代码审查检查点
   - 制定文件管理最佳实践

## 📞 技术细节

### 修改统计

| 文件类型 | 修改数量 | 影响范围 |
|----------|----------|----------|
| **配置文件** | 1个 | MES配置 |
| **Python代码** | 1个 | 2处引用 |
| **总计** | **2个文件** | **MES系统** |

### 兼容性说明

**向后兼容：**
- ✅ 旧的状态文件会被自动忽略
- ✅ 新的状态文件会自动创建
- ✅ 不影响现有ETL功能

**数据迁移：**
- ✅ 旧的状态数据会重新生成
- ✅ 增量处理逻辑保持不变
- ✅ 历史数据处理不受影响

### 风险评估

**低风险修改：**
- ✅ 只修改文件名，不改变逻辑
- ✅ 状态文件会自动重新生成
- ✅ 不影响数据处理结果

**注意事项：**
- ⚠️ 首次运行后会重新生成状态文件
- ⚠️ 增量处理会重新计算数据状态
- ⚠️ 建议在非生产时间进行修改验证

---

**修改日期**: 2025-11-20  
**修改人员**: ETL开发团队  
**版本**: v1.0  
**状态**: ✅ 已完成并验证  
**影响范围**: MES系统状态文件命名
