# 快捷键冲突解决方案

## 分析摘要

通过完整的快捷键分析，我们发现了以下情况：
- **主程序快捷键数量**: 42个
- **管理器快捷键数量**: 35个  
- **总计唯一快捷键**: 64个
- **发现冲突数量**: 13个

## 冲突分类

### 1. 功能重复冲突（建议保留管理器版本）
这些冲突是因为主程序和管理器实现了相同的功能：

| 快捷键 | 主程序功能 | 管理器功能 | 解决方案 |
|--------|------------|------------|----------|
| `Ctrl+P` | ai_predict_current | ai_predict_current | 保留管理器版本，移除主程序定义 |
| `Ctrl+Shift+P` | ai_predict_batch | ai_predict_batch | 保留管理器版本，移除主程序定义 |
| `F9` | ai_toggle_panel | ai_toggle_panel | 保留管理器版本，移除主程序定义 |
| `Ctrl+B` | batch_operations | batch_operations | 保留管理器版本，移除主程序定义 |
| `Ctrl+Shift+C` | batch_copy | batch_copy | 保留管理器版本，移除主程序定义 |

### 2. 功能不同冲突（需要重新分配）
这些冲突是因为相同快捷键被分配给了不同的功能：

| 快捷键 | 主程序功能 | 管理器功能 | 解决方案 |
|--------|------------|------------|----------|
| `Ctrl+Shift+M` | export_model | single_class_mode | 管理器改为 `Ctrl+Alt+M` |
| `Ctrl+Shift+D` | delete_image | batch_delete | 管理器改为 `Ctrl+Alt+D` |
| `Ctrl+D` | copy | duplicate_shape | 管理器改为 `Ctrl+Alt+C` |
| `Ctrl+Shift+A` | advanced_mode | about | 管理器改为 `F12` |
| `Ctrl+H` | hide_all | show_shortcuts | 管理器改为 `F1` |
| `Ctrl+Shift+T` | labels_toggle | batch_convert | 管理器改为 `Ctrl+Alt+T` |
| `Ctrl+Shift+R` | draw_squares_option | toggle_draw_square | 管理器改为 `Ctrl+Alt+R` |
| `Ctrl+Shift+L` | display_label_option | color_dialog | 管理器改为 `Ctrl+Alt+L` |

## 详细修复计划

### 阶段1：移除重复功能的快捷键定义

**文件**: `labelImg.py`
**操作**: 注释或删除以下行的快捷键定义

1. **行 1001**: `Ctrl+P` (ai_predict_current) - 保留管理器版本
2. **行 1003**: `Ctrl+Shift+P` (ai_predict_batch) - 保留管理器版本  
3. **行 1005**: `F9` (ai_toggle_panel) - 保留管理器版本
4. **行 1009**: `Ctrl+B` (batch_operations) - 保留管理器版本
5. **行 1011**: `Ctrl+Shift+C` (batch_copy) - 保留管理器版本

### 阶段2：修改管理器中的冲突快捷键

**文件**: `libs/shortcut_manager.py`
**操作**: 修改以下快捷键定义

1. **行 95**: `single_class_mode` 从 `Ctrl+Shift+M` 改为 `Ctrl+Alt+M`
2. **行 131**: `batch_delete` 从 `Ctrl+Shift+D` 改为 `Ctrl+Alt+D`
3. **行 111**: `duplicate_shape` 从 `Ctrl+D` 改为 `Ctrl+Alt+C`
4. **行 143**: `about` 从 `Ctrl+Shift+A` 改为 `F12`
5. **行 142**: `show_shortcuts` 从 `Ctrl+H` 改为 `F1`
6. **行 132**: `batch_convert` 从 `Ctrl+Shift+T` 改为 `Ctrl+Alt+T`
7. **行 93**: `toggle_draw_square` 从 `Ctrl+Shift+R` 改为 `Ctrl+Alt+R`
8. **行 138**: `color_dialog` 从 `Ctrl+Shift+L` 改为 `Ctrl+Alt+L`

### 阶段3：验证修复结果

1. **重新运行分析脚本**确认冲突已解决
2. **功能测试**确保所有快捷键正常工作
3. **用户体验测试**确保新的快捷键组合合理易用

## 快捷键设计原则

### 1. 优先级原则
- 主程序核心功能 > 管理器扩展功能
- 常用功能 > 不常用功能
- 标准快捷键 > 自定义快捷键

### 2. 一致性原则
- 相同功能使用相同快捷键
- 相关功能使用相似的快捷键模式
- 遵循操作系统和应用程序的快捷键惯例

### 3. 易记性原则
- 快捷键与功能名称相关（如 Ctrl+S 保存）
- 使用逻辑分组（如 Ctrl+Alt+* 用于高级功能）
- 避免过于复杂的组合键

### 4. 冲突避免原则
- 定期检查快捷键冲突
- 建立快捷键注册机制
- 提供快捷键自定义功能

## 修复后的快捷键分布

### 主程序保留的快捷键 (42个)
- 文件操作: `Ctrl+Q`, `Ctrl+O`, `Ctrl+S`, `Ctrl+Shift+S` 等
- 编辑操作: `Ctrl+D`, `Ctrl+A`, `Ctrl+H`, `Delete` 等  
- 视图操作: `Ctrl++`, `Ctrl+-`, `Ctrl+F` 等
- 导航操作: `d`, `a`, `space` 等

### 管理器修改后的快捷键 (35个)
- 基础操作保持不变: `R`, `P`, `C`, `L`, `E` 等
- 高级功能使用 `Ctrl+Alt+*` 模式
- 帮助功能使用功能键: `F1`, `F12` 等

## 实施时间表

1. **第1天**: 实施阶段1（移除重复定义）
2. **第2天**: 实施阶段2（修改管理器快捷键）
3. **第3天**: 验证和测试
4. **第4天**: 更新文档和用户指南

## 风险评估

### 低风险
- 移除重复功能定义（功能仍可通过管理器访问）
- 修改不常用功能的快捷键

### 中等风险  
- 修改常用功能的快捷键（需要用户适应）
- 可能影响现有用户的使用习惯

### 缓解措施
- 提供快捷键迁移指南
- 保留旧快捷键一段时间并显示警告
- 允许用户自定义快捷键
