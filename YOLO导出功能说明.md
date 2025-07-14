# labelImg YOLO导出功能说明

## 功能概述

为labelImg标注工具新增了Pascal VOC到YOLO格式的数据集导出功能，可以将现有的Pascal VOC XML标注文件转换为YOLO训练格式，并自动生成标准的数据集目录结构。

## 新增功能

### 1. 菜单项
- 在"文件"菜单中新增"导出为YOLO数据集"选项
- 快捷键：Ctrl+E
- 支持中英文界面

### 2. 导出对话框
- 现代化的Material Design风格界面
- 可选择目标导出目录
- 可自定义数据集名称
- 可调整训练集/验证集比例（默认8:2）
- 实时进度显示和日志输出

### 3. 数据集结构
生成符合YOLO官方标准的目录结构：
```
datasets/
└── [数据集名称]/
    ├── images/
    │   ├── train/          # 训练集图片
    │   └── val/            # 验证集图片
    ├── labels/
    │   ├── train/          # 训练集标注
    │   └── val/            # 验证集标注
    ├── classes.txt         # 类别列表
    └── data.yaml          # YOLO训练配置
```

### 4. 自动生成配置文件

#### classes.txt
包含所有检测类别的列表，每行一个类别名称。

#### data.yaml
YOLO训练配置文件，包含：
- 数据集路径
- 训练集和验证集路径
- 类别名称映射

示例：
```yaml
path: ../datasets/dataset_name
train: images/train
val: images/val
test: 

names:
  0: person
  1: car
  2: bicycle
```

## 使用方法

### 1. 准备数据
确保工作目录中包含：
- 图片文件（.jpg, .png, .bmp等）
- 对应的Pascal VOC XML标注文件

### 2. 打开目录
在labelImg中打开包含图片和标注文件的目录。

### 3. 导出数据集
1. 点击"文件" → "导出为YOLO数据集"
2. 在对话框中选择目标导出目录
3. 设置数据集名称和训练集比例
4. 点击"开始导出"

### 4. 查看结果
导出完成后，可以在目标目录中找到生成的YOLO格式数据集。

## 技术特性

### 1. 格式转换
- 自动将Pascal VOC的绝对坐标转换为YOLO的相对坐标
- 支持多类别检测
- 保持标注精度

### 2. 数据分割
- 随机分割训练集和验证集
- 可自定义分割比例
- 确保图片和标注文件的对应关系

### 3. 错误处理
- 检查文件完整性
- 验证标注格式
- 提供详细的错误信息

### 4. 进度监控
- 实时显示转换进度
- 详细的操作日志
- 支持取消操作

## 依赖要求

新增依赖：
- PyYAML >= 5.1

已在以下文件中更新：
- `setup.py`
- `requirements/requirements-linux-python3.txt`

## 文件结构

新增文件：
```
libs/
├── pascal_to_yolo_converter.py    # 核心转换器
└── yolo_export_dialog.py          # 导出对话框

resources/strings/
├── strings.properties             # 英文字符串资源
└── strings-zh-CN.properties       # 中文字符串资源

test_yolo_export.py                # 功能测试脚本
simple_yolo_test.py               # 简单测试脚本
demo_yolo_export.py               # 演示脚本
```

## 测试验证

### 1. 单元测试
运行 `python simple_yolo_test.py` 进行基础功能测试。

### 2. 演示测试
运行 `python demo_yolo_export.py` 查看完整的转换演示。

### 3. 集成测试
运行 `python test_yolo_export.py` 进行全面的功能测试。

## 使用示例

### 1. 基本使用
```python
from libs.pascal_to_yolo_converter import PascalToYOLOConverter

converter = PascalToYOLOConverter(
    source_dir="./annotations",
    target_dir="./output", 
    dataset_name="my_dataset",
    train_ratio=0.8
)

success, message = converter.convert()
```

### 2. 带进度回调
```python
def progress_callback(current, total, message):
    print(f"[{current}%] {message}")

success, message = converter.convert(progress_callback)
```

## 注意事项

1. **文件命名**：确保图片文件和XML文件有相同的基础名称
2. **目录权限**：确保对目标目录有写入权限
3. **磁盘空间**：转换过程会复制图片文件，需要足够的磁盘空间
4. **中文路径**：支持包含中文字符的文件路径
5. **大数据集**：对于大型数据集，转换可能需要较长时间

## 故障排除

### 常见问题

1. **"未找到标注文件"**
   - 检查目录中是否有.xml文件
   - 确保XML文件格式正确

2. **"无效的目录路径"**
   - 检查目标目录是否存在
   - 确保有写入权限

3. **转换失败**
   - 检查XML文件格式是否符合Pascal VOC标准
   - 确保图片文件存在且可读取

### 日志信息
导出过程中的详细日志会显示在对话框中，可以帮助诊断问题。

## 更新历史

- v1.0: 初始版本，支持基本的Pascal VOC到YOLO转换
- 支持中英文界面
- 支持自定义数据集配置
- 支持进度监控和错误处理

## 贡献

如有问题或建议，请提交Issue或Pull Request。
