# 常用模式和最佳实践

- 快捷键功能实现模式 - labelImg项目

## 实现的功能
- X键：删除选中的标注框（复用delete_selected_shape函数，与DEL键功能相同但不覆盖）
- Tab键：循环选择画布上的标注框（实现cycle_select_shape函数，支持循环切换）

## 技术架构
1. 快捷键管理器注册：在libs/shortcut_manager.py的init_default_shortcuts()中注册
2. Canvas直接处理：在libs/canvas.py的keyPressEvent()中处理键盘事件
3. 主窗口逻辑：在labelImg.py中实现具体功能函数和信号处理

## 关键解决方案
- **冲突处理**：S键与原有toggle_shapes冲突，改用Tab键避免冲突
- **焦点管理**：Canvas设置StrongFocus策略，鼠标点击时setFocus()
- **双重保险**：快捷键管理器 + Canvas直接处理，确保功能可靠

## 修改的文件
1. libs/shortcut_manager.py - 注册X键和Tab键快捷键
2. libs/canvas.py - 键盘事件处理，焦点管理
3. labelImg.py - cycle_select_shape函数实现，信号处理

## 调试经验
- 使用详细的调试日志定位问题
- lambda闭包问题用partial函数解决
- 快捷键冲突需要检查已有绑定

这种模式可以应用于其他快捷键功能的扩展。
- CSS兼容性Bug修复模式 - labelImg项目

## 问题类型
Qt样式表不支持CSS3属性导致的警告和错误

## 常见不支持的CSS3属性
- transition: 过渡动画属性
- animation: 关键帧动画属性  
- transform: 变换属性
- box-shadow: 盒子阴影属性

## 修复策略
1. **清空无效属性值**: 将UITransitions类中的所有值设为空字符串
2. **批量移除属性**: 使用MultiEdit工具批量移除所有不支持的CSS属性
3. **创建缺失模块**: 当import错误时，创建必要的模块文件（如logger_config.py）

## 修复过程
1. 识别问题：通过控制台Unknown property警告定位
2. 查找源头：使用Grep工具找到所有相关属性
3. 批量修复：使用MultiEdit一次性处理多个相同问题
4. 测试验证：运行程序确认警告消失

## 技术要点
- Qt样式表基于CSS2，不支持CSS3高级功能
- 动画效果应使用QPropertyAnimation等Qt原生动画系统
- 批量修复时要注意使用replace_all参数
- 保持基本样式功能，只移除不支持的增强效果

这种模式适用于所有Qt应用的CSS兼容性问题修复。
