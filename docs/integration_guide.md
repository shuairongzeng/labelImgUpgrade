# 项目管理系统集成指南

## 集成概述

项目管理系统采用渐进式集成策略，确保与现有labelImg系统无缝兼容。通过配置适配器模式，现有代码无需大规模修改即可支持项目隔离功能。

## 核心组件集成

### 1. 主程序集成 (labelImg.py)

在主窗口类中添加项目管理支持：

```python
# 在MainWindow类的__init__方法中添加
from libs.project_manager import get_project_manager
from libs.project_config_adapter import get_config_adapter
from libs.project_selector import ProjectSelector
from libs.project_management_dialog import ProjectManagementDialog

class MainWindow(QMainWindow, WindowMixin):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # 初始化项目管理
        self.project_manager = get_project_manager()
        self.config_adapter = get_config_adapter()
        
        # ... 现有初始化代码 ...
        
        # 添加项目选择器到工具栏
        self.setup_project_toolbar()
        
        # 连接项目切换信号
        self.connect_project_signals()
    
    def setup_project_toolbar(self):
        """设置项目工具栏"""
        # 添加项目选择器
        self.project_selector = ProjectSelector()
        self.project_selector.project_changed.connect(self.on_project_changed)
        self.project_selector.manage_projects.connect(self.open_project_management)
        
        # 添加到主工具栏
        project_action = self.toolBar.addWidget(self.project_selector)
        project_action.setToolTip("项目管理")
    
    def connect_project_signals(self):
        """连接项目相关信号"""
        # 项目切换时重新加载配置
        self.project_selector.project_changed.connect(self.reload_project_config)
    
    def on_project_changed(self, project_name):
        """项目切换处理"""
        # 保存当前工作
        if self.mayContinue():
            # 重新加载项目配置
            self.reload_project_config()
            # 更新窗口标题
            self.update_window_title()
            # 刷新类别列表
            self.load_predefined_classes()
        else:
            # 如果用户取消，恢复原项目选择
            old_project = self.project_manager.get_current_project()
            self.project_selector.set_current_project(old_project)
    
    def reload_project_config(self):
        """重新加载项目配置"""
        try:
            # 重新加载类别配置
            self.load_predefined_classes()
            
            # 重新加载训练配置
            self.load_training_preferences()
            
            # 重新加载UI配置
            self.load_ui_preferences()
            
            # 更新状态栏
            self.statusBar().showMessage(f"已切换到项目: {self.project_manager.get_current_project()}", 3000)
            
        except Exception as e:
            logger.error(f"重新加载项目配置失败: {e}")
    
    def update_window_title(self):
        """更新窗口标题"""
        current_project = self.project_manager.get_current_project()
        projects = self.project_manager.list_projects()
        
        if current_project in projects:
            project_name = projects[current_project].get('display_name', current_project)
            self.setWindowTitle(f"{__appname__} - {project_name}")
        else:
            self.setWindowTitle(__appname__)
    
    def open_project_management(self):
        """打开项目管理对话框"""
        dialog = ProjectManagementDialog(self)
        dialog.project_switched.connect(self.on_project_changed)
        dialog.show()
```

### 2. 类别管理集成

修改现有的类别加载和保存方法：

```python
# 在相关方法中使用配置适配器

def load_predefined_classes(self, predefClassesFile=None):
    """加载预定义类别（兼容项目管理）"""
    if predefClassesFile is None:
        # 使用项目配置适配器获取类别
        classes = self.config_adapter.load_classes()
        if classes:
            for class_name in classes:
                self.labelHist.append(class_name)
        return
    
    # 原有的文件加载逻辑保持不变
    # ...

def save_predefined_classes(self, classes=None):
    """保存预定义类别（兼容项目管理）"""
    if classes is None:
        classes = list(self.labelHist)
    
    # 使用配置适配器保存
    return self.config_adapter.save_classes(classes)
```

### 3. 训练配置集成

修改训练相关的配置加载和保存：

```python
def load_training_preferences(self):
    """加载训练偏好配置"""
    try:
        prefs = self.config_adapter.load_training_preferences()
        
        # 应用配置到UI控件
        if hasattr(self, 'training_dialog'):
            self.training_dialog.apply_preferences(prefs)
            
        return prefs
    except Exception as e:
        logger.error(f"加载训练配置失败: {e}")
        return {}

def save_training_preferences(self, preferences):
    """保存训练偏好配置"""
    return self.config_adapter.save_training_preferences(preferences)

def add_training_record(self, record):
    """添加训练记录"""
    return self.config_adapter.add_training_record(record)
```

### 4. 路径管理集成

使用项目相关的路径：

```python
def get_project_data_path(self):
    """获取当前项目数据路径"""
    return self.config_adapter.get_project_data_path()

def get_project_models_path(self):
    """获取当前项目模型路径"""
    return self.config_adapter.get_project_models_path()

def get_project_exports_path(self):
    """获取当前项目导出路径"""
    return self.config_adapter.get_project_exports_path()
```

## 状态栏集成

在状态栏添加项目信息显示：

```python
def setup_status_bar(self):
    """设置状态栏"""
    # 现有状态栏设置...
    
    # 添加项目状态显示
    from libs.project_selector import CompactProjectSelector
    
    self.project_status = CompactProjectSelector()
    self.project_status.project_changed.connect(self.on_project_changed)
    
    # 添加到状态栏右侧
    self.statusBar().addPermanentWidget(self.project_status)
```

## 菜单集成

在主菜单中添加项目管理菜单：

```python
def setup_project_menu(self):
    """设置项目菜单"""
    # 创建项目菜单
    project_menu = self.menubar.addMenu('项目(&P)')
    
    # 项目管理
    manage_action = QAction('项目管理(&M)...', self)
    manage_action.setShortcut('Ctrl+Shift+P')
    manage_action.triggered.connect(self.open_project_management)
    project_menu.addAction(manage_action)
    
    # 新建项目
    new_project_action = QAction('新建项目(&N)...', self)
    new_project_action.triggered.connect(self.create_new_project)
    project_menu.addAction(new_project_action)
    
    project_menu.addSeparator()
    
    # 项目切换子菜单（动态）
    self.project_switch_menu = project_menu.addMenu('切换项目(&S)')
    self.update_project_switch_menu()

def update_project_switch_menu(self):
    """更新项目切换菜单"""
    self.project_switch_menu.clear()
    
    projects = self.project_manager.list_projects()
    current_project = self.project_manager.get_current_project()
    
    for name, info in projects.items():
        display_name = info.get('display_name', name)
        action = QAction(display_name, self)
        action.setCheckable(True)
        action.setChecked(name == current_project)
        action.triggered.connect(lambda checked, pn=name: self.switch_to_project(pn))
        self.project_switch_menu.addAction(action)
```

## 配置文件迁移

在应用启动时自动执行配置迁移：

```python
def migrate_legacy_config(self):
    """迁移旧版配置"""
    try:
        # 检查是否需要迁移
        legacy_config_path = Path("configs")
        if legacy_config_path.exists():
            # 执行迁移
            success = self.config_adapter.migrate_legacy_configs()
            if success:
                logger.info("旧版配置迁移完成")
                # 可选：备份旧配置
                backup_path = Path("configs_backup")
                if not backup_path.exists():
                    shutil.move(legacy_config_path, backup_path)
                    logger.info("旧配置已备份到configs_backup目录")
        
    except Exception as e:
        logger.error(f"配置迁移失败: {e}")
```

## 现有组件适配

### 1. 训练对话框适配

```python
# 在训练对话框中使用项目路径
class TrainingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_adapter = get_config_adapter()
        
    def get_dataset_path(self):
        """获取数据集路径"""
        return self.config_adapter.get_project_data_path()
    
    def get_model_output_path(self):
        """获取模型输出路径"""
        return self.config_adapter.get_project_models_path()
    
    def save_training_config(self, config):
        """保存训练配置"""
        return self.config_adapter.save_training_preferences(config)
```

### 2. AI助手适配

```python
# 在AI助手中使用项目特定的设置
class AIAssistantPanel(QWidget):
    def load_ai_settings(self):
        """加载AI设置"""
        return self.config_adapter.load_ai_settings()
    
    def save_ai_settings(self, settings):
        """保存AI设置"""
        return self.config_adapter.save_ai_settings(settings)
```

## 测试集成

创建集成测试验证项目管理功能：

```python
def test_project_integration():
    """测试项目集成功能"""
    # 测试项目创建
    manager = get_project_manager()
    assert manager.create_project("test_project", "测试项目")
    
    # 测试项目切换
    assert manager.switch_project("test_project")
    
    # 测试配置适配器
    adapter = get_config_adapter()
    assert adapter.save_classes(["class1", "class2"])
    classes = adapter.load_classes()
    assert classes == ["class1", "class2"]
    
    # 清理测试项目
    manager.delete_project("test_project", force=True)
```

## 性能优化

### 1. 懒加载
- 项目配置按需加载
- 减少启动时间
- 优化内存使用

### 2. 缓存策略
- 缓存常用配置
- 减少文件I/O操作
- 智能刷新机制

### 3. 异步操作
- 项目切换异步处理
- 大文件操作使用后台线程
- UI响应性优化

## 错误处理

### 1. 项目损坏恢复
- 自动检测项目完整性
- 提供修复建议
- 备份恢复机制

### 2. 配置错误处理
- 配置文件格式验证
- 默认配置回退
- 用户友好的错误信息

### 3. 迁移错误处理
- 迁移过程错误捕获
- 回滚机制
- 详细的错误日志

这个集成方案确保了：
1. 现有功能完全兼容
2. 渐进式升级路径
3. 用户体验平滑过渡
4. 系统稳定性和可维护性