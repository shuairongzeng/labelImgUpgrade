# labelImg项目概览

## 项目目的
labelImg是一个图像标注工具，支持多种标注格式（XML、JSON、YOLO等），主要用于计算机视觉和机器学习项目的数据准备。

## 技术栈
- **主要语言**: Python
- **GUI框架**: PyQt5/PyQt4
- **图像处理**: PIL, OpenCV (可选)
- **数据格式**: XML (Pascal VOC), JSON (CreateML), YOLO txt
- **配置管理**: YAML

## 代码结构
- `labelImg.py` - 主入口文件
- `libs/` - 核心库文件
  - `ai_assistant_panel.py` - AI助手面板，包含一键配置功能
  - `pascal_to_yolo_converter.py` - YOLO格式转换器
  - `class_manager.py` - 类别配置管理
  - `canvas.py` - 图像画布
  - `labelFile.py` - 标注文件处理
- `configs/` - 配置文件目录
  - `class_config.yaml` - 类别配置文件

## 关键功能
1. **图像标注**: 支持矩形框标注
2. **格式转换**: XML ↔ JSON ↔ YOLO
3. **一键配置**: 自动生成训练数据集
4. **AI助手**: 智能预测和训练功能
5. **类别管理**: 统一的类别配置系统