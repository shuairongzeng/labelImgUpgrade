#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YOLO预测器模块

提供YOLO模型的加载、预测和结果处理功能
"""

import os
import time
import logging
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from PyQt5.QtCore import QObject, pyqtSignal
except ImportError:
    from PyQt4.QtCore import QObject, pyqtSignal

# 导入YOLO相关库
try:
    from ultralytics import YOLO
    import torch
    import cv2
    import numpy as np
    YOLO_AVAILABLE = True
except ImportError as e:
    YOLO_AVAILABLE = False
    IMPORT_ERROR = str(e)

# 导入labelImg相关模块
from libs.shape import Shape

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """检测结果数据类"""
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2 (像素坐标)
    confidence: float                        # 置信度 [0, 1]
    class_id: int                           # 类别ID
    class_name: str                         # 类别名称
    image_width: int = 0                    # 图像宽度
    image_height: int = 0                   # 图像高度

    def to_shape(self, line_color=None, fill_color=None):
        """转换为labelImg的Shape对象"""
        from PyQt5.QtCore import QPointF
        from libs.shape import Shape

        x1, y1, x2, y2 = self.bbox

        # 创建Shape对象
        shape = Shape(label=self.class_name, line_color=line_color)

        # 添加矩形的四个顶点
        shape.add_point(QPointF(x1, y1))  # 左上
        shape.add_point(QPointF(x2, y1))  # 右上
        shape.add_point(QPointF(x2, y2))  # 右下
        shape.add_point(QPointF(x1, y2))  # 左下

        shape.close()

        # 添加置信度信息到标签
        if hasattr(shape, 'confidence'):
            shape.confidence = self.confidence

        return shape

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'bbox': self.bbox,
            'confidence': self.confidence,
            'class_id': self.class_id,
            'class_name': self.class_name,
            'image_width': self.image_width,
            'image_height': self.image_height
        }

    def get_center(self) -> Tuple[float, float]:
        """获取检测框中心点"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def get_area(self) -> float:
        """获取检测框面积"""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

    def get_width_height(self) -> Tuple[float, float]:
        """获取检测框宽高"""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1, y2 - y1)


@dataclass
class PredictionResult:
    """预测结果数据类"""
    image_path: str                         # 图像路径
    detections: List[Detection]             # 检测结果列表
    inference_time: float                   # 推理时间(秒)
    timestamp: datetime                     # 时间戳
    model_name: str = ""                    # 模型名称
    confidence_threshold: float = 0.25      # 使用的置信度阈值

    def get_high_confidence_detections(self, threshold: float = 0.5) -> List[Detection]:
        """获取高置信度检测结果"""
        return [det for det in self.detections if det.confidence >= threshold]

    def get_detections_by_class(self, class_name: str) -> List[Detection]:
        """根据类别名称获取检测结果"""
        return [det for det in self.detections if det.class_name == class_name]

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'image_path': self.image_path,
            'detections': [det.to_dict() for det in self.detections],
            'inference_time': self.inference_time,
            'timestamp': self.timestamp.isoformat(),
            'model_name': self.model_name,
            'confidence_threshold': self.confidence_threshold,
            'detection_count': len(self.detections)
        }


class YOLOPredictor(QObject):
    """YOLO模型预测器"""

    # 信号定义
    model_loaded = pyqtSignal(str)          # 模型加载完成
    prediction_completed = pyqtSignal(object)  # 预测完成
    error_occurred = pyqtSignal(str)        # 错误发生

    def __init__(self, model_path: str = None):
        """
        初始化YOLO预测器

        Args:
            model_path: 模型文件路径，如果为None则不加载模型
        """
        super().__init__()

        # 检查YOLO库是否可用
        if not YOLO_AVAILABLE:
            logger.error(f"YOLO库不可用: {IMPORT_ERROR}")
            self.error_occurred.emit(f"YOLO库不可用: {IMPORT_ERROR}")
            return

        # 初始化属性
        self.model = None
        self.model_path = None
        self.model_name = ""
        self.class_names = {}
        self.device = "cpu"
        self.is_loaded = False

        # 检测设备
        self._detect_device()

        # 如果提供了模型路径，尝试加载
        if model_path:
            self.load_model(model_path)

    def _detect_device(self):
        """检测可用的计算设备"""
        try:
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info(f"检测到CUDA设备: {torch.cuda.get_device_name()}")
            else:
                self.device = "cpu"
                logger.info("使用CPU设备")
        except Exception as e:
            logger.warning(f"设备检测失败: {e}")
            self.device = "cpu"

    def load_model(self, model_path: str) -> bool:
        """
        加载YOLO模型

        Args:
            model_path: 模型文件路径

        Returns:
            bool: 加载是否成功
        """
        print(f"[DEBUG] YOLO预测器: 开始加载模型: {model_path}")
        try:
            logger.info(f"正在加载模型: {model_path}")

            # 检查文件是否存在
            if not os.path.exists(model_path):
                # 如果是标准模型名称，尝试自动下载
                if model_path in ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']:
                    logger.info(f"自动下载模型: {model_path}")
                else:
                    error_msg = f"模型文件不存在: {model_path}"
                    logger.error(error_msg)
                    self.error_occurred.emit(error_msg)
                    return False

            # 加载模型
            start_time = time.time()
            self.model = YOLO(model_path)
            load_time = time.time() - start_time

            # 设置设备
            if hasattr(self.model, 'to'):
                self.model.to(self.device)

            # 保存模型信息
            self.model_path = model_path
            self.model_name = os.path.basename(model_path)
            self.is_loaded = True

            # 获取类别信息
            if hasattr(self.model, 'model') and hasattr(self.model.model, 'names'):
                self.class_names = self.model.model.names
            elif hasattr(self.model, 'names'):
                self.class_names = self.model.names
            else:
                logger.warning("无法获取模型类别信息")
                self.class_names = {}

            logger.info(f"模型加载成功，耗时: {load_time:.2f}秒")
            logger.info(f"模型类别数量: {len(self.class_names)}")
            logger.info(f"模型设备: {self.device}")

            # 发送加载完成信号
            self.model_loaded.emit(self.model_name)

            return True

        except Exception as e:
            error_msg = f"模型加载失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.is_loaded = False
            return False

    def predict_single(self, image_path: str, conf_threshold: float = 0.25,
                       iou_threshold: float = 0.45, max_det: int = 100) -> Optional[PredictionResult]:
        """
        单图预测

        Args:
            image_path: 图像文件路径
            conf_threshold: 置信度阈值
            iou_threshold: IoU阈值 (NMS)
            max_det: 最大检测数量

        Returns:
            PredictionResult: 预测结果，失败时返回None
        """
        print(f"[DEBUG] YOLO预测器: predict_single被调用")
        print(f"[DEBUG] YOLO预测器: 图像路径: {image_path}")
        print(
            f"[DEBUG] YOLO预测器: 参数 - conf: {conf_threshold}, iou: {iou_threshold}, max_det: {max_det}")

        if not self.is_loaded:
            error_msg = "模型未加载"
            print(f"[ERROR] YOLO预测器: {error_msg}")
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        if not os.path.exists(image_path):
            error_msg = f"图像文件不存在: {image_path}"
            print(f"[ERROR] YOLO预测器: {error_msg}")
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        try:
            print(f"[DEBUG] YOLO预测器: 开始预测图像: {image_path}")
            logger.debug(f"预测图像: {image_path}")

            # 检查模型状态
            print(
                f"[DEBUG] YOLO预测器: 模型状态 - 已加载: {self.is_loaded}, 模型名: {self.model_name}")

            # 执行预测
            print(f"[DEBUG] YOLO预测器: 调用模型进行预测...")
            start_time = time.time()
            results = self.model(
                image_path,
                conf=conf_threshold,
                iou=iou_threshold,
                max_det=max_det,
                verbose=False
            )
            inference_time = time.time() - start_time
            print(f"[DEBUG] YOLO预测器: 模型预测完成，耗时: {inference_time:.3f}秒")

            # 处理结果
            print(f"[DEBUG] YOLO预测器: 处理预测结果...")
            detections = self._process_results(results, image_path)
            print(f"[DEBUG] YOLO预测器: 结果处理完成，检测数量: {len(detections)}")

            # 创建预测结果
            result = PredictionResult(
                image_path=image_path,
                detections=detections,
                inference_time=inference_time,
                timestamp=datetime.now(),
                model_name=self.model_name,
                confidence_threshold=conf_threshold
            )

            print(
                f"[DEBUG] YOLO预测器: 预测完成，检测到 {len(detections)} 个目标，耗时: {inference_time:.3f}秒")
            logger.debug(
                f"预测完成，检测到 {len(detections)} 个目标，耗时: {inference_time:.3f}秒")

            # 发送预测完成信号
            print(f"[DEBUG] YOLO预测器: 发送预测完成信号")
            self.prediction_completed.emit(result)

            return result

        except Exception as e:
            error_msg = f"预测失败: {str(e)}"
            print(f"[ERROR] YOLO预测器: {error_msg}")
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return None

    def predict_batch(self, image_paths: List[str], conf_threshold: float = 0.25,
                      iou_threshold: float = 0.45, max_det: int = 100) -> Dict[str, PredictionResult]:
        """
        批量预测

        Args:
            image_paths: 图像文件路径列表
            conf_threshold: 置信度阈值
            iou_threshold: IoU阈值 (NMS)
            max_det: 最大检测数量

        Returns:
            Dict[str, PredictionResult]: 预测结果字典，键为图像路径
        """
        if not self.is_loaded:
            error_msg = "模型未加载"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {}

        results = {}

        try:
            logger.info(f"开始批量预测，共 {len(image_paths)} 张图像")

            # 过滤存在的图像文件
            valid_paths = [
                path for path in image_paths if os.path.exists(path)]
            if len(valid_paths) != len(image_paths):
                logger.warning(
                    f"发现 {len(image_paths) - len(valid_paths)} 个无效图像路径")

            if not valid_paths:
                logger.warning("没有有效的图像文件")
                return {}

            # 批量预测
            start_time = time.time()
            batch_results = self.model(
                valid_paths,
                conf=conf_threshold,
                iou=iou_threshold,
                max_det=max_det,
                verbose=False
            )
            total_time = time.time() - start_time

            # 处理每个结果
            for i, (image_path, result) in enumerate(zip(valid_paths, batch_results)):
                detections = self._process_results([result], image_path)

                prediction_result = PredictionResult(
                    image_path=image_path,
                    detections=detections,
                    inference_time=total_time / len(valid_paths),  # 平均时间
                    timestamp=datetime.now(),
                    model_name=self.model_name,
                    confidence_threshold=conf_threshold
                )

                results[image_path] = prediction_result

            logger.info(
                f"批量预测完成，总耗时: {total_time:.2f}秒，平均: {total_time/len(valid_paths):.3f}秒/张")

            return results

        except Exception as e:
            error_msg = f"批量预测失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {}

    def _process_results(self, results, image_path: str) -> List[Detection]:
        """
        处理YOLO预测结果

        Args:
            results: YOLO预测结果
            image_path: 图像路径

        Returns:
            List[Detection]: 检测结果列表
        """
        detections = []

        try:
            # 获取图像尺寸
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"无法读取图像: {image_path}")
                return detections

            img_height, img_width = image.shape[:2]

            # 处理每个结果
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    boxes = result.boxes

                    # 提取检测信息
                    if len(boxes) > 0:
                        # 获取边界框坐标 (xyxy格式)
                        if hasattr(boxes, 'xyxy'):
                            xyxy = boxes.xyxy.cpu().numpy()
                        else:
                            continue

                        # 获取置信度
                        if hasattr(boxes, 'conf'):
                            confidences = boxes.conf.cpu().numpy()
                        else:
                            confidences = [1.0] * len(xyxy)

                        # 获取类别ID
                        if hasattr(boxes, 'cls'):
                            class_ids = boxes.cls.cpu().numpy().astype(int)
                        else:
                            class_ids = [0] * len(xyxy)

                        # 创建Detection对象
                        for bbox, conf, cls_id in zip(xyxy, confidences, class_ids):
                            x1, y1, x2, y2 = bbox

                            # 确保坐标在图像范围内
                            x1 = max(0, min(x1, img_width))
                            y1 = max(0, min(y1, img_height))
                            x2 = max(0, min(x2, img_width))
                            y2 = max(0, min(y2, img_height))

                            # 获取类别名称
                            class_name = self.class_names.get(
                                cls_id, f"class_{cls_id}")

                            detection = Detection(
                                bbox=(float(x1), float(y1),
                                      float(x2), float(y2)),
                                confidence=float(conf),
                                class_id=int(cls_id),
                                class_name=class_name,
                                image_width=img_width,
                                image_height=img_height
                            )

                            detections.append(detection)

        except Exception as e:
            logger.error(f"处理预测结果失败: {str(e)}")

        return detections

    def get_model_info(self) -> Dict:
        """
        获取模型信息

        Returns:
            Dict: 模型信息字典
        """
        if not self.is_loaded:
            return {
                'loaded': False,
                'error': '模型未加载'
            }

        try:
            info = {
                'loaded': True,
                'model_path': self.model_path,
                'model_name': self.model_name,
                'device': self.device,
                'class_count': len(self.class_names),
                'class_names': self.class_names,
                'yolo_available': YOLO_AVAILABLE
            }

            # 添加模型特定信息
            if hasattr(self.model, 'model'):
                model_info = self.model.model
                if hasattr(model_info, 'yaml'):
                    info['model_yaml'] = str(model_info.yaml)
                if hasattr(model_info, 'nc'):
                    info['num_classes'] = model_info.nc

            return info

        except Exception as e:
            return {
                'loaded': True,
                'error': f'获取模型信息失败: {str(e)}'
            }

    def unload_model(self):
        """卸载模型，释放内存"""
        try:
            if self.model is not None:
                del self.model
                self.model = None

            # 清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self.is_loaded = False
            self.model_path = None
            self.model_name = ""
            self.class_names = {}

            logger.info("模型已卸载")

        except Exception as e:
            logger.error(f"卸载模型失败: {str(e)}")

    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.is_loaded and self.model is not None
