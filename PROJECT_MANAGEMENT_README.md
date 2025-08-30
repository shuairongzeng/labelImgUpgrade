# 📁 labelImg 项目管理系统

这是为 labelImg 标注工具开发的完整项目管理系统，允许用户管理多个标注项目，每个项目都有独立的配置、类别和数据。

## 🌟 主要功能

### 📋 项目管理对话框 (ProjectManagementDialog)
- **项目列表显示**: 显示所有可用项目及其基本信息
- **创建新项目**: 支持从头创建或从现有项目复制配置
- **删除项目**: 安全删除项目（default项目受保护）
- **编辑项目信息**: 修改项目名称、描述、作者、标签等元数据
- **切换当前项目**: 快速切换工作项目

### 🔧 项目选择器组件 (ProjectSelector)
- **显示当前项目**: 实时显示当前工作项目
- **快速切换**: 通过下拉菜单快速切换项目
- **状态指示器**: 显示项目状态（活跃/正常/警告/错误）
- **工具栏集成**: 无缝集成到主应用工具栏

### 💾 项目配置管理
- **配置隔离**: 每个项目独立的配置文件
- **自动迁移**: 从旧配置系统平滑迁移
- **配置适配器**: 兼容现有代码结构

## 🎨 界面特性

- **Material Design 风格**: 现代化的扁平设计
- **响应式布局**: 适应不同屏幕尺寸
- **动画效果**: 流畅的用户交互体验
- **中文界面**: 完整的中文本地化支持
- **错误处理**: 完善的错误提示和恢复机制

## 🗂️ 文件结构

```
libs/
├── project_manager.py                  # 项目管理核心类
├── project_config_adapter.py           # 配置适配器（兼容旧系统）
├── project_management_dialog.py        # 项目管理对话框
├── project_selector.py                 # 项目选择器组件
└── ui_styles.py                        # 统一UI样式

projects/                               # 项目根目录
├── projects_index.json                # 项目索引文件
├── shared/                            # 共享资源
│   └── models/                        # 共享模型文件
├── default/                           # 默认项目
│   ├── project.json                   # 项目元数据
│   ├── configs/                       # 项目配置
│   ├── data/                          # 项目数据
│   ├── models/                        # 项目模型
│   ├── exports/                       # 导出文件
│   └── runs/                          # 运行记录
└── [其他项目目录]/
```

## 🚀 使用方法

### 1. 基本使用

```python
from libs.project_manager import get_project_manager
from libs.project_config_adapter import get_config_adapter

# 获取项目管理器
manager = get_project_manager()

# 创建新项目
success = manager.create_project(
    name="my_project",
    display_name="我的项目",
    description="项目描述"
)

# 切换项目
manager.switch_project("my_project")

# 获取当前项目配置
adapter = get_config_adapter()
classes = adapter.load_classes()
```

### 2. 集成到主应用

在 `labelImg.py` 中已经完成了集成：

```python
# 导入项目管理组件
from libs.project_selector import ProjectSelectorToolBar
from libs.project_management_dialog import ProjectManagementDialog

# 在工具栏中添加项目选择器
self.project_selector_toolbar = ProjectSelectorToolBar()
self.project_selector_toolbar.project_switched.connect(self.on_project_switched)

# 处理项目切换事件
def on_project_switched(self, project_name: str):
    # 保存当前工作
    # 重新加载项目配置
    # 更新界面状态
```

### 3. 项目管理对话框

```python
# 显示项目管理对话框
dialog = ProjectManagementDialog(parent)
dialog.project_switched.connect(self.on_project_switched)
dialog.exec_()
```

## 🧪 测试

运行测试脚本来验证功能：

```bash
python test_project_management.py
```

测试功能包括：
- ✅ 项目选择器组件功能
- ✅ 项目管理对话框功能  
- ✅ 项目创建、删除、切换
- ✅ 配置管理和迁移
- ✅ 界面响应和错误处理

## 📝 项目配置结构

每个项目包含以下配置文件：

```
configs/
├── class_config.yaml          # 类别配置
├── training_preferences.json  # 训练参数
├── training_history.json      # 训练历史
├── ui_preferences.json        # UI设置
├── shortcuts.json             # 快捷键配置
└── ai_settings.json          # AI助手设置
```

## 🔄 配置迁移

系统会自动检测并迁移旧的配置：

1. **检测旧配置**: 检查 `configs/` 目录
2. **创建默认项目**: 自动创建 default 项目
3. **迁移配置文件**: 复制配置到项目目录
4. **保持兼容性**: 通过配置适配器保证代码兼容

## 🛡️ 错误处理

- **配置文件损坏**: 自动恢复默认配置
- **项目切换失败**: 回退到上一个项目
- **权限问题**: 友好的错误提示
- **数据丢失保护**: default项目不可删除

## 🎯 最佳实践

1. **项目命名**: 使用有意义的英文名称作为项目内部名称
2. **定期备份**: 重要项目数据定期备份
3. **配置管理**: 通过项目管理对话框统一管理配置
4. **标签管理**: 为项目添加合适的标签便于分类

## 🔧 自定义扩展

系统提供了良好的扩展性：

```python
# 扩展项目元数据
class CustomProjectMetadata(ProjectMetadata):
    custom_field: str = ""

# 扩展项目配置
class CustomProjectConfig(ProjectConfig):
    custom_settings: Dict[str, Any] = None
```

## 📚 API 参考

### ProjectManager 主要方法

- `create_project(name, display_name, ...)` - 创建项目
- `delete_project(name)` - 删除项目
- `switch_project(name)` - 切换项目
- `list_projects()` - 列出所有项目
- `get_project_metadata(name)` - 获取项目元数据
- `save_project_config(name, config)` - 保存项目配置

### ProjectConfigAdapter 主要方法

- `load_classes()` - 加载当前项目类别
- `save_classes(classes)` - 保存类别配置
- `load_training_preferences()` - 加载训练设置
- `migrate_legacy_configs()` - 迁移旧配置

## 🐛 问题排查

常见问题及解决方案：

1. **项目切换后类别丢失**
   - 检查项目配置文件是否存在
   - 尝试重新加载配置

2. **创建项目失败**
   - 检查目录权限
   - 确认项目名称格式正确

3. **界面显示异常**
   - 重启应用程序
   - 检查Qt样式表语法

---

🎉 **享受高效的多项目标注体验！** 

如有问题或建议，欢迎反馈。