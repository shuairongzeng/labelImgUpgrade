#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
labelImg AI助手模块

提供基于YOLO的智能预标注功能，包括：
- YOLO模型预测器
- 模型管理器  
- 批量处理器
- 置信度过滤器

作者: labelImg AI Team
版本: 1.0.0
"""

from .yolo_predictor import YOLOPredictor, Detection, PredictionResult
from .model_manager import ModelManager
from .batch_processor import BatchProcessor
from .confidence_filter import ConfidenceFilter

__version__ = "1.0.0"
__author__ = "labelImg AI Team"

# 导出的公共接口
__all__ = [
    'YOLOPredictor',
    'ModelManager', 
    'BatchProcessor',
    'ConfidenceFilter',
    'Detection',
    'PredictionResult'
]

# 模块级别的配置
DEFAULT_CONFIG = {
    'default_confidence': 0.25,
    'nms_threshold': 0.45,
    'max_detections': 100,
    'image_size': 640
}

def get_version():
    """获取AI助手模块版本"""
    return __version__

def get_default_config():
    """获取默认配置"""
    return DEFAULT_CONFIG.copy()
