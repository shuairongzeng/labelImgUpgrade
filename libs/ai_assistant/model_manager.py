#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型管理器模块

管理多个YOLO模型，支持模型切换、验证和信息获取
"""

import os
import logging
import yaml
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    from PyQt5.QtCore import QObject, pyqtSignal
except ImportError:
    from PyQt4.QtCore import QObject, pyqtSignal

# 导入YOLO相关库
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# 设置日志
logger = logging.getLogger(__name__)


class ModelManager(QObject):
    """模型管理器"""

    # 信号定义
    models_updated = pyqtSignal(list)       # 模型列表更新
    model_validated = pyqtSignal(str, bool)  # 模型验证完成
    error_occurred = pyqtSignal(str)        # 错误发生

    # 支持的模型格式
    SUPPORTED_FORMATS = ['.pt', '.onnx', '.engine']

    # 预训练模型信息
    PRETRAINED_MODELS = {
        'yolov8n.pt': {
            'name': 'YOLOv8 Nano',
            'size': '6.2MB',
            'description': '最快速度，适合快速预标注',
            'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt'
        },
        'yolov8s.pt': {
            'name': 'YOLOv8 Small',
            'size': '21.5MB',
            'description': '平衡性能，推荐使用',
            'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8s.pt'
        },
        'yolov8m.pt': {
            'name': 'YOLOv8 Medium',
            'size': '49.7MB',
            'description': '高精度，适合专业标注',
            'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt'
        },
        'yolov8l.pt': {
            'name': 'YOLOv8 Large',
            'size': '83.7MB',
            'description': '更高精度，速度较慢',
            'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8l.pt'
        },
        'yolov8x.pt': {
            'name': 'YOLOv8 Extra Large',
            'size': '136.7MB',
            'description': '最高精度，速度最慢',
            'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8x.pt'
        }
    }

    def __init__(self, models_dir: str = "models", config_path: str = "config/ai_settings.yaml"):
        """
        初始化模型管理器

        Args:
            models_dir: 模型存储目录
            config_path: 配置文件路径
        """
        super().__init__()

        self.models_dir = Path(models_dir)
        self.config_path = config_path
        self.current_model = None
        self.available_models = []
        self.model_info_cache = {}

        # 创建模型目录
        self.models_dir.mkdir(exist_ok=True)

        # 创建自定义模型子目录
        (self.models_dir / "custom").mkdir(exist_ok=True)

        # 加载配置
        self.config = self._load_config()

        # 扫描可用模型
        self.scan_models()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    return config.get('ai_assistant', {})
            else:
                logger.warning(f"配置文件不存在: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def scan_models(self) -> List[str]:
        """
        扫描可用模型

        Returns:
            List[str]: 可用模型路径列表
        """
        try:
            models = []

            # 1. 扫描模型目录
            for format_ext in self.SUPPORTED_FORMATS:
                # 扫描根目录
                models.extend(self.models_dir.glob(f"*{format_ext}"))
                # 扫描custom子目录
                models.extend(self.models_dir.glob(f"custom/*{format_ext}"))

            # 2. 扫描训练结果目录
            runs_dir = Path("runs/train")
            if runs_dir.exists():
                logger.info("正在扫描训练结果目录...")
                training_models = self._scan_training_results(runs_dir)
                models.extend(training_models)
                logger.info(f"在训练结果中找到 {len(training_models)} 个模型")

            # 转换为字符串路径并排序
            self.available_models = sorted([str(model) for model in models])

            logger.info(f"总共扫描到 {len(self.available_models)} 个模型文件")

            # 发送更新信号
            self.models_updated.emit(self.available_models)

            return self.available_models

        except Exception as e:
            error_msg = f"扫描模型失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []

    def _scan_training_results(self, runs_dir: Path) -> List[Path]:
        """
        扫描训练结果目录中的模型文件

        Args:
            runs_dir: 训练结果根目录 (runs/train)

        Returns:
            List[Path]: 找到的训练模型路径列表
        """
        training_models = []

        try:
            # 遍历所有训练结果子目录
            for training_dir in runs_dir.iterdir():
                if not training_dir.is_dir():
                    continue

                # 检查weights子目录
                weights_dir = training_dir / "weights"
                if not weights_dir.exists():
                    continue

                # 查找best.pt和last.pt文件
                for model_file in ["best.pt", "last.pt"]:
                    model_path = weights_dir / model_file
                    if model_path.exists():
                        training_models.append(model_path)
                        logger.debug(f"找到训练模型: {model_path}")

        except Exception as e:
            logger.error(f"扫描训练结果目录失败: {str(e)}")

        return training_models

    def validate_model(self, model_path: str) -> bool:
        """
        验证模型有效性

        Args:
            model_path: 模型文件路径

        Returns:
            bool: 模型是否有效
        """
        try:
            logger.info(f"验证模型: {model_path}")

            # 检查文件是否存在
            if not os.path.exists(model_path):
                logger.error(f"模型文件不存在: {model_path}")
                self.model_validated.emit(model_path, False)
                return False

            # 检查文件格式
            file_ext = Path(model_path).suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                logger.error(f"不支持的模型格式: {file_ext}")
                self.model_validated.emit(model_path, False)
                return False

            # 检查YOLO库是否可用
            if not YOLO_AVAILABLE:
                logger.error("YOLO库不可用")
                self.model_validated.emit(model_path, False)
                return False

            # 尝试加载模型
            try:
                model = YOLO(model_path)

                # 基本验证
                if not hasattr(model, 'model'):
                    logger.error("模型结构无效")
                    self.model_validated.emit(model_path, False)
                    return False

                # 获取模型信息并缓存
                model_info = self._extract_model_info(model, model_path)
                self.model_info_cache[model_path] = model_info

                logger.info(f"模型验证成功: {model_path}")
                self.model_validated.emit(model_path, True)

                # 清理模型对象
                del model

                return True

            except Exception as e:
                logger.error(f"模型加载失败: {str(e)}")
                self.model_validated.emit(model_path, False)
                return False

        except Exception as e:
            error_msg = f"模型验证失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.model_validated.emit(model_path, False)
            return False

    def _extract_model_info(self, model, model_path: str) -> Dict:
        """提取模型信息"""
        try:
            info = {
                'path': model_path,
                'name': os.path.basename(model_path),
                'format': Path(model_path).suffix.lower(),
                'size': self._get_file_size(model_path),
                'classes': {},
                'class_count': 0,
                'is_pretrained': os.path.basename(model_path) in self.PRETRAINED_MODELS
            }

            # 获取类别信息
            if hasattr(model, 'model') and hasattr(model.model, 'names'):
                info['classes'] = model.model.names
                info['class_count'] = len(model.model.names)
            elif hasattr(model, 'names'):
                info['classes'] = model.names
                info['class_count'] = len(model.names)

            # 添加预训练模型信息
            if info['is_pretrained']:
                pretrained_info = self.PRETRAINED_MODELS[info['name']]
                info.update(pretrained_info)

            return info

        except Exception as e:
            logger.error(f"提取模型信息失败: {str(e)}")
            return {'path': model_path, 'error': str(e)}

    def _get_file_size(self, file_path: str) -> str:
        """获取文件大小的可读格式"""
        try:
            size_bytes = os.path.getsize(file_path)

            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

        except Exception:
            return "Unknown"

    def get_model_classes(self, model_path: str) -> Dict[int, str]:
        """
        获取模型类别列表

        Args:
            model_path: 模型文件路径

        Returns:
            Dict[int, str]: 类别ID到类别名称的映射
        """
        try:
            # 先检查缓存
            if model_path in self.model_info_cache:
                return self.model_info_cache[model_path].get('classes', {})

            # 验证模型并获取信息
            if self.validate_model(model_path):
                return self.model_info_cache.get(model_path, {}).get('classes', {})
            else:
                return {}

        except Exception as e:
            logger.error(f"获取模型类别失败: {str(e)}")
            return {}

    def get_model_info(self, model_path: str) -> Dict:
        """
        获取模型详细信息

        Args:
            model_path: 模型文件路径

        Returns:
            Dict: 模型信息
        """
        try:
            # 先检查缓存
            if model_path in self.model_info_cache:
                return self.model_info_cache[model_path]

            # 验证模型并获取信息
            if self.validate_model(model_path):
                return self.model_info_cache.get(model_path, {})
            else:
                return {'error': '模型验证失败'}

        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return {'error': str(e)}

    def switch_model(self, model_path: str) -> bool:
        """
        切换当前模型

        Args:
            model_path: 模型文件路径

        Returns:
            bool: 切换是否成功
        """
        try:
            # 验证模型
            if not self.validate_model(model_path):
                return False

            self.current_model = model_path
            logger.info(f"切换到模型: {model_path}")

            return True

        except Exception as e:
            error_msg = f"切换模型失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def get_available_models(self) -> List[Dict]:
        """
        获取可用模型列表（包含详细信息）

        Returns:
            List[Dict]: 模型信息列表
        """
        models_info = []

        for model_path in self.available_models:
            info = self.get_model_info(model_path)
            models_info.append(info)

        return models_info

    def get_pretrained_models(self) -> Dict:
        """获取预训练模型信息"""
        return self.PRETRAINED_MODELS.copy()

    def get_current_model(self) -> Optional[str]:
        """获取当前选中的模型路径"""
        return self.current_model

    def refresh_models(self):
        """刷新模型列表"""
        self.model_info_cache.clear()
        self.scan_models()
