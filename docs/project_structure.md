# 项目管理系统目录结构

## 整体目录结构

```
labelImg/
├── labelImg.py                    # 主程序
├── libs/                          # 库文件
│   ├── project_manager.py         # 项目管理核心
│   ├── project_config_adapter.py  # 配置适配器
│   ├── project_management_dialog.py # 项目管理GUI
│   └── project_selector.py        # 项目选择器组件
├── configs/                       # 旧版配置目录（向后兼容）
└── projects/                      # 项目管理根目录
    ├── projects_index.json        # 项目索引文件
    ├── shared/                    # 共享资源
    │   └── models/               # 共享模型文件
    │       ├── yolov8n.pt
    │       ├── yolov8s.pt
    │       └── custom_model.pt
    ├── default/                   # 默认项目
    │   ├── project.json          # 项目元数据
    │   ├── configs/              # 项目配置
    │   │   ├── class_config.yaml
    │   │   ├── training_preferences.json
    │   │   ├── training_history.json
    │   │   ├── ui_preferences.json
    │   │   ├── shortcuts.json
    │   │   └── ai_settings.json
    │   ├── data/                 # 项目数据
    │   │   ├── images/          # 图像文件
    │   │   ├── annotations/     # 标注文件
    │   │   └── datasets/        # 数据集
    │   ├── models/              # 项目专用模型
    │   ├── exports/             # 导出文件
    │   └── runs/                # 训练运行记录
    └── my_project/              # 用户项目示例
        ├── project.json
        ├── configs/
        ├── data/
        ├── models/
        ├── exports/
        └── runs/
```

## 项目索引文件格式

`projects/projects_index.json`:

```json
{
  "version": "1.0",
  "current_project": "default",
  "projects": {
    "default": {
      "display_name": "默认项目",
      "description": "系统默认项目",
      "created_at": "2025-01-19T10:00:00",
      "updated_at": "2025-01-19T10:00:00",
      "path": "/path/to/projects/default"
    },
    "my_project": {
      "display_name": "我的项目",
      "description": "用户自定义项目",
      "created_at": "2025-01-19T11:00:00",
      "updated_at": "2025-01-19T11:00:00",
      "path": "/path/to/projects/my_project"
    }
  }
}
```

## 项目元数据文件格式

`projects/[project_name]/project.json`:

```json
{
  "name": "my_project",
  "display_name": "我的项目",
  "description": "这是一个示例项目",
  "created_at": "2025-01-19T11:00:00",
  "updated_at": "2025-01-19T11:00:00",
  "version": "1.0",
  "author": "用户名",
  "tags": ["demo", "training"]
}
```

## 项目配置文件

### 1. 类别配置 (`configs/class_config.yaml`)
与现有格式兼容，包含类别列表和元数据。

### 2. 训练偏好 (`configs/training_preferences.json`)
```json
{
  "epochs": 100,
  "batch_size": 16,
  "img_size": 640,
  "model": "yolov8n.pt",
  "device": "auto",
  "patience": 50,
  "save_period": 10
}
```

### 3. 训练历史 (`configs/training_history.json`)
与现有格式兼容，记录训练历史。

### 4. UI偏好 (`configs/ui_preferences.json`)
```json
{
  "theme": "material_light",
  "language": "zh_CN",
  "auto_save": true,
  "auto_backup": true,
  "recent_files_limit": 10
}
```

### 5. 快捷键设置 (`configs/shortcuts.json`)
```json
{
  "save": "Ctrl+S",
  "open": "Ctrl+O",
  "delete": "Delete",
  "next_image": "D",
  "prev_image": "A"
}
```

### 6. AI设置 (`configs/ai_settings.json`)
```json
{
  "enabled": true,
  "auto_predict": false,
  "confidence_threshold": 0.5,
  "model_path": "",
  "batch_predict": false
}
```

## 数据隔离策略

### 1. 配置隔离
- 每个项目有独立的配置文件
- 项目间配置互不影响
- 支持从其他项目复制配置

### 2. 数据隔离
- 每个项目有独立的data目录
- 图像和标注文件分项目存储
- 训练数据集按项目组织

### 3. 模型管理
- 共享模型：存储在`projects/shared/models/`
- 项目专用模型：存储在各项目的`models/`目录
- 支持模型的共享和复制

### 4. 训练记录隔离
- 每个项目独立的训练历史
- 运行记录按项目存储
- 导出文件分项目管理

## 向后兼容性

### 1. 配置迁移
- 自动检测旧版`configs/`目录
- 首次启动时将旧配置迁移到`default`项目
- 保持现有文件格式不变

### 2. 接口兼容
- 提供配置适配器类
- 现有代码无需修改即可使用新系统
- 渐进式迁移，确保系统稳定

### 3. 数据迁移
- 现有的图像和标注数据自动归入`default`项目
- 训练历史和模型文件自动迁移
- 用户设置和快捷键配置保持不变

## 扩展性设计

### 1. 插件支持
- 项目可以安装特定的插件
- 插件配置按项目隔离
- 支持项目级别的功能扩展

### 2. 团队协作
- 项目配置可以导出/导入
- 支持项目模板功能
- 便于团队间共享项目设置

### 3. 云同步准备
- 项目结构设计考虑云同步需求
- 配置文件格式便于版本控制
- 支持项目的备份和恢复

## 安全考虑

### 1. 路径安全
- 所有路径操作使用相对路径
- 防止路径遍历攻击
- 验证项目名称合法性

### 2. 数据安全
- 项目删除前确认操作
- 重要数据自动备份
- 支持项目导出备份

### 3. 配置验证
- 配置文件格式验证
- 防止恶意配置注入
- 默认配置安全可靠