# 📐 AI助手模块架构设计

## 🎯 设计目标

基于YOLO集成技术调研结果，设计一个高效、可扩展的AI助手模块，实现智能预标注功能，提升labelImg的标注效率。

## 🏗️ 整体架构

```
labelImg AI助手模块架构
├── libs/ai_assistant/           # AI助手核心模块
│   ├── __init__.py             # 模块初始化
│   ├── yolo_predictor.py       # YOLO模型预测器
│   ├── model_manager.py        # 模型管理器
│   ├── batch_processor.py      # 批量处理器
│   └── confidence_filter.py    # 置信度过滤器
├── libs/ai_assistant_panel.py  # AI助手界面面板
├── config/ai_settings.yaml     # AI配置文件
└── models/                     # 模型存储目录
```

## 🔧 核心模块设计

### 1. YOLO预测器 (yolo_predictor.py)

**职责**: 封装YOLO模型的加载、预测和结果处理

```python
class YOLOPredictor:
    """YOLO模型预测器"""
    
    def __init__(self, model_path: str = None):
        """初始化预测器"""
        
    def load_model(self, model_path: str) -> bool:
        """加载YOLO模型"""
        
    def predict_single(self, image_path: str, conf_threshold: float = 0.25) -> List[Detection]:
        """单图预测"""
        
    def predict_batch(self, image_paths: List[str], conf_threshold: float = 0.25) -> Dict[str, List[Detection]]:
        """批量预测"""
        
    def get_model_info(self) -> Dict:
        """获取模型信息"""
```

### 2. 模型管理器 (model_manager.py)

**职责**: 管理多个YOLO模型，支持模型切换和验证

```python
class ModelManager:
    """模型管理器"""
    
    def __init__(self, models_dir: str = "models"):
        """初始化管理器"""
        
    def scan_models(self) -> List[str]:
        """扫描可用模型"""
        
    def validate_model(self, model_path: str) -> bool:
        """验证模型有效性"""
        
    def get_model_classes(self, model_path: str) -> List[str]:
        """获取模型类别列表"""
        
    def switch_model(self, model_path: str) -> bool:
        """切换当前模型"""
```

### 3. 批量处理器 (batch_processor.py)

**职责**: 处理批量预测任务，支持进度跟踪和取消操作

```python
class BatchProcessor(QObject):
    """批量处理器"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, int)  # 当前进度, 总数
    batch_completed = pyqtSignal(dict)       # 批量完成
    error_occurred = pyqtSignal(str)         # 错误发生
    
    def __init__(self, predictor: YOLOPredictor):
        """初始化处理器"""
        
    def process_directory(self, dir_path: str, conf_threshold: float = 0.25):
        """处理目录中的所有图像"""
        
    def cancel_processing(self):
        """取消当前处理"""
```

### 4. 置信度过滤器 (confidence_filter.py)

**职责**: 根据置信度阈值过滤和优化检测结果

```python
class ConfidenceFilter:
    """置信度过滤器"""
    
    def __init__(self, default_threshold: float = 0.25):
        """初始化过滤器"""
        
    def filter_detections(self, detections: List[Detection], threshold: float = None) -> List[Detection]:
        """过滤检测结果"""
        
    def apply_nms(self, detections: List[Detection], iou_threshold: float = 0.45) -> List[Detection]:
        """应用非极大值抑制"""
        
    def optimize_for_annotation(self, detections: List[Detection]) -> List[Detection]:
        """为标注优化检测结果"""
```

## 🖥️ 界面集成设计

### AI助手面板 (ai_assistant_panel.py)

```python
class AIAssistantPanel(QWidget):
    """AI助手界面面板"""
    
    def __init__(self, parent=None):
        """初始化面板"""
        
    def setup_ui(self):
        """设置界面"""
        # 模型选择区域
        # 置信度调节区域
        # 预测控制区域
        # 结果显示区域
        
    def on_model_changed(self, model_path: str):
        """模型切换处理"""
        
    def on_predict_current(self):
        """预测当前图像"""
        
    def on_predict_batch(self):
        """批量预测"""
```

## 📊 数据结构设计

### 检测结果 (Detection)

```python
@dataclass
class Detection:
    """检测结果数据类"""
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    confidence: float                        # 置信度
    class_id: int                           # 类别ID
    class_name: str                         # 类别名称
    
    def to_shape(self) -> Shape:
        """转换为labelImg的Shape对象"""
        
    def to_dict(self) -> Dict:
        """转换为字典"""
```

### 预测结果 (PredictionResult)

```python
@dataclass
class PredictionResult:
    """预测结果数据类"""
    image_path: str                         # 图像路径
    detections: List[Detection]             # 检测结果列表
    inference_time: float                   # 推理时间
    timestamp: datetime                     # 时间戳
    
    def get_high_confidence_detections(self, threshold: float = 0.5) -> List[Detection]:
        """获取高置信度检测结果"""
```

## ⚙️ 配置管理

### AI设置配置 (config/ai_settings.yaml)

```yaml
# AI助手配置
ai_assistant:
  # 默认模型设置
  default_model: "yolov8n.pt"
  models_directory: "models"
  
  # 预测参数
  prediction:
    default_confidence: 0.25
    nms_threshold: 0.45
    max_detections: 100
    
  # 批量处理设置
  batch_processing:
    max_concurrent: 4
    chunk_size: 10
    auto_save: true
    
  # 界面设置
  ui:
    show_confidence: true
    auto_apply_predictions: false
    highlight_low_confidence: true
    low_confidence_threshold: 0.3
```

## 🔄 工作流程设计

### 1. 单图预测流程

```
用户点击预测按钮
    ↓
检查模型是否加载
    ↓
执行YOLO预测
    ↓
过滤低置信度结果
    ↓
转换为Shape对象
    ↓
添加到画布显示
    ↓
用户确认或修改
```

### 2. 批量预测流程

```
用户选择批量预测
    ↓
扫描目录获取图像列表
    ↓
启动后台处理线程
    ↓
逐个处理图像
    ↓
更新进度显示
    ↓
保存预测结果
    ↓
完成通知用户
```

## 🔌 与现有系统集成

### 1. 与MainWindow集成

```python
class MainWindow(QMainWindow, WindowMixin):
    def __init__(self):
        # 现有初始化代码...
        
        # 添加AI助手
        self.ai_assistant = AIAssistantPanel(self)
        self.ai_predictor = YOLOPredictor()
        self.model_manager = ModelManager()
        
        # 集成到界面
        self.setup_ai_assistant_panel()
        
    def setup_ai_assistant_panel(self):
        """设置AI助手面板"""
        # 添加到右侧面板或独立窗口
```

### 2. 与Canvas集成

```python
class Canvas(QWidget):
    def add_predicted_shapes(self, detections: List[Detection]):
        """添加预测的标注框"""
        for detection in detections:
            shape = detection.to_shape()
            shape.predicted = True  # 标记为预测结果
            self.shapes.append(shape)
        self.update()
```

## 🚀 性能优化策略

### 1. 内存管理
- 模型延迟加载
- 预测结果缓存
- 大图像分块处理

### 2. 并发处理
- 异步预测任务
- 多线程批量处理
- 进度实时更新

### 3. 用户体验
- 预测结果预览
- 可撤销操作
- 智能置信度建议

## 📝 开发规范

### 1. 代码规范
- 使用类型提示
- 完整的文档字符串
- 单元测试覆盖

### 2. 错误处理
- 优雅的异常处理
- 用户友好的错误信息
- 日志记录

### 3. 扩展性
- 插件化架构
- 配置驱动
- 接口标准化

## 🎯 下一步实施计划

1. **第2周**: 实现核心模块
   - YOLOPredictor基础功能
   - ModelManager模型管理
   - 基础单元测试

2. **第3周**: 界面集成
   - AIAssistantPanel开发
   - 与MainWindow集成
   - 批量处理功能

3. **第4周**: 优化完善
   - 性能优化
   - 用户体验改进
   - 完整测试

---

**架构设计完成，准备开始实施！** 🚀
