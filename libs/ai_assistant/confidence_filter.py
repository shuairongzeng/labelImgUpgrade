#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
置信度过滤器模块

根据置信度阈值过滤和优化检测结果
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from .yolo_predictor import Detection

# 设置日志
logger = logging.getLogger(__name__)


class ConfidenceFilter:
    """置信度过滤器"""
    
    def __init__(self, default_threshold: float = 0.25):
        """
        初始化置信度过滤器
        
        Args:
            default_threshold: 默认置信度阈值
        """
        self.default_threshold = default_threshold
        self.class_thresholds = {}  # 类别特定阈值
        
        # 统计信息
        self.filter_stats = {
            'total_detections': 0,
            'filtered_detections': 0,
            'nms_removed': 0
        }
    
    def set_class_threshold(self, class_name: str, threshold: float):
        """
        设置特定类别的置信度阈值
        
        Args:
            class_name: 类别名称
            threshold: 置信度阈值
        """
        self.class_thresholds[class_name] = threshold
        logger.debug(f"设置类别 '{class_name}' 的置信度阈值为 {threshold}")
    
    def get_class_threshold(self, class_name: str) -> float:
        """
        获取特定类别的置信度阈值
        
        Args:
            class_name: 类别名称
            
        Returns:
            float: 置信度阈值
        """
        return self.class_thresholds.get(class_name, self.default_threshold)
    
    def filter_detections(self, detections: List[Detection], 
                         threshold: float = None) -> List[Detection]:
        """
        根据置信度过滤检测结果
        
        Args:
            detections: 检测结果列表
            threshold: 置信度阈值，如果为None则使用默认值
            
        Returns:
            List[Detection]: 过滤后的检测结果
        """
        if not detections:
            return []
        
        if threshold is None:
            threshold = self.default_threshold
        
        try:
            filtered = []
            
            for detection in detections:
                # 获取该类别的阈值
                class_threshold = self.get_class_threshold(detection.class_name)
                effective_threshold = max(threshold, class_threshold)
                
                # 过滤低置信度检测
                if detection.confidence >= effective_threshold:
                    filtered.append(detection)
            
            # 更新统计
            self.filter_stats['total_detections'] += len(detections)
            self.filter_stats['filtered_detections'] += len(filtered)
            
            logger.debug(f"置信度过滤: {len(detections)} -> {len(filtered)} "
                        f"(阈值: {threshold})")
            
            return filtered
            
        except Exception as e:
            logger.error(f"置信度过滤失败: {str(e)}")
            return detections
    
    def apply_nms(self, detections: List[Detection], 
                  iou_threshold: float = 0.45) -> List[Detection]:
        """
        应用非极大值抑制 (NMS)
        
        Args:
            detections: 检测结果列表
            iou_threshold: IoU阈值
            
        Returns:
            List[Detection]: NMS后的检测结果
        """
        if not detections or len(detections) <= 1:
            return detections
        
        try:
            # 按置信度排序
            sorted_detections = sorted(detections, key=lambda x: x.confidence, reverse=True)
            
            # 转换为numpy数组以便计算
            boxes = np.array([det.bbox for det in sorted_detections])
            scores = np.array([det.confidence for det in sorted_detections])
            
            # 执行NMS
            keep_indices = self._nms_numpy(boxes, scores, iou_threshold)
            
            # 保留的检测结果
            nms_detections = [sorted_detections[i] for i in keep_indices]
            
            # 更新统计
            removed_count = len(detections) - len(nms_detections)
            self.filter_stats['nms_removed'] += removed_count
            
            logger.debug(f"NMS过滤: {len(detections)} -> {len(nms_detections)} "
                        f"(IoU阈值: {iou_threshold})")
            
            return nms_detections
            
        except Exception as e:
            logger.error(f"NMS过滤失败: {str(e)}")
            return detections
    
    def _nms_numpy(self, boxes: np.ndarray, scores: np.ndarray, 
                   iou_threshold: float) -> List[int]:
        """
        使用numpy实现的NMS算法
        
        Args:
            boxes: 边界框数组 (N, 4) [x1, y1, x2, y2]
            scores: 置信度数组 (N,)
            iou_threshold: IoU阈值
            
        Returns:
            List[int]: 保留的索引列表
        """
        if len(boxes) == 0:
            return []
        
        # 计算面积
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        
        # 按置信度排序的索引
        order = scores.argsort()[::-1]
        
        keep = []
        while len(order) > 0:
            # 保留置信度最高的框
            i = order[0]
            keep.append(i)
            
            if len(order) == 1:
                break
            
            # 计算IoU
            xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
            xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
            yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            intersection = w * h
            
            iou = intersection / (areas[i] + areas[order[1:]] - intersection)
            
            # 保留IoU小于阈值的框
            indices = np.where(iou <= iou_threshold)[0]
            order = order[indices + 1]
        
        return keep
    
    def optimize_for_annotation(self, detections: List[Detection],
                               min_box_size: int = 10,
                               max_overlap_ratio: float = 0.8) -> List[Detection]:
        """
        为标注优化检测结果
        
        Args:
            detections: 检测结果列表
            min_box_size: 最小框尺寸（像素）
            max_overlap_ratio: 最大重叠比例
            
        Returns:
            List[Detection]: 优化后的检测结果
        """
        if not detections:
            return []
        
        try:
            optimized = []
            
            for detection in detections:
                # 检查框尺寸
                width, height = detection.get_width_height()
                if width < min_box_size or height < min_box_size:
                    logger.debug(f"跳过过小的检测框: {width}x{height}")
                    continue
                
                # 检查框是否在图像边界内
                x1, y1, x2, y2 = detection.bbox
                if (x1 < 0 or y1 < 0 or 
                    x2 > detection.image_width or y2 > detection.image_height):
                    # 裁剪到图像边界
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(detection.image_width, x2)
                    y2 = min(detection.image_height, y2)
                    
                    # 创建新的检测对象
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=detection.confidence,
                        class_id=detection.class_id,
                        class_name=detection.class_name,
                        image_width=detection.image_width,
                        image_height=detection.image_height
                    )
                
                optimized.append(detection)
            
            # 移除高度重叠的检测框
            optimized = self._remove_high_overlap(optimized, max_overlap_ratio)
            
            logger.debug(f"标注优化: {len(detections)} -> {len(optimized)}")
            
            return optimized
            
        except Exception as e:
            logger.error(f"标注优化失败: {str(e)}")
            return detections
    
    def _remove_high_overlap(self, detections: List[Detection],
                            max_overlap_ratio: float) -> List[Detection]:
        """移除高度重叠的检测框"""
        if len(detections) <= 1:
            return detections
        
        try:
            # 按置信度排序
            sorted_detections = sorted(detections, key=lambda x: x.confidence, reverse=True)
            
            keep = []
            for i, det1 in enumerate(sorted_detections):
                should_keep = True
                
                for det2 in keep:
                    # 计算重叠比例
                    overlap_ratio = self._calculate_overlap_ratio(det1, det2)
                    
                    if overlap_ratio > max_overlap_ratio:
                        should_keep = False
                        break
                
                if should_keep:
                    keep.append(det1)
            
            return keep
            
        except Exception as e:
            logger.error(f"移除重叠检测框失败: {str(e)}")
            return detections
    
    def _calculate_overlap_ratio(self, det1: Detection, det2: Detection) -> float:
        """计算两个检测框的重叠比例"""
        try:
            x1_1, y1_1, x2_1, y2_1 = det1.bbox
            x1_2, y1_2, x2_2, y2_2 = det2.bbox
            
            # 计算交集
            xx1 = max(x1_1, x1_2)
            yy1 = max(y1_1, y1_2)
            xx2 = min(x2_1, x2_2)
            yy2 = min(y2_1, y2_2)
            
            if xx2 <= xx1 or yy2 <= yy1:
                return 0.0
            
            intersection = (xx2 - xx1) * (yy2 - yy1)
            
            # 计算两个框的面积
            area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
            area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
            
            # 计算重叠比例（相对于较小的框）
            min_area = min(area1, area2)
            overlap_ratio = intersection / min_area if min_area > 0 else 0.0
            
            return overlap_ratio
            
        except Exception as e:
            logger.error(f"计算重叠比例失败: {str(e)}")
            return 0.0
    
    def get_statistics(self) -> Dict:
        """获取过滤统计信息"""
        stats = self.filter_stats.copy()
        
        if stats['total_detections'] > 0:
            stats['filter_rate'] = (stats['total_detections'] - stats['filtered_detections']) / stats['total_detections']
        else:
            stats['filter_rate'] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """重置统计信息"""
        self.filter_stats = {
            'total_detections': 0,
            'filtered_detections': 0,
            'nms_removed': 0
        }
    
    def get_confidence_distribution(self, detections: List[Detection]) -> Dict:
        """获取置信度分布统计"""
        if not detections:
            return {}
        
        try:
            confidences = [det.confidence for det in detections]
            
            return {
                'count': len(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'mean': sum(confidences) / len(confidences),
                'median': sorted(confidences)[len(confidences) // 2],
                'high_confidence_count': len([c for c in confidences if c >= 0.7]),
                'medium_confidence_count': len([c for c in confidences if 0.3 <= c < 0.7]),
                'low_confidence_count': len([c for c in confidences if c < 0.3])
            }
            
        except Exception as e:
            logger.error(f"计算置信度分布失败: {str(e)}")
            return {}
