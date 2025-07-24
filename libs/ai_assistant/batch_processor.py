#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量处理器模块

处理批量预测任务，支持进度跟踪和取消操作
"""

import os
import time
import logging
from typing import List, Dict, Optional, Callable
from pathlib import Path
from threading import Thread, Event

try:
    from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
except ImportError:
    from PyQt4.QtCore import QObject, pyqtSignal, QThread, QTimer

from .yolo_predictor import YOLOPredictor, PredictionResult

# 设置日志
logger = logging.getLogger(__name__)


class BatchProcessor(QObject):
    """批量处理器"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, int, str)  # 当前进度, 总数, 当前文件
    batch_started = pyqtSignal(int)               # 批量开始, 总数
    batch_completed = pyqtSignal(dict)            # 批量完成, 结果字典
    batch_cancelled = pyqtSignal()                # 批量取消
    error_occurred = pyqtSignal(str)              # 错误发生
    file_processed = pyqtSignal(str, object)      # 单文件处理完成
    
    # 支持的图像格式
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']
    
    def __init__(self, predictor: YOLOPredictor):
        """
        初始化批量处理器
        
        Args:
            predictor: YOLO预测器实例
        """
        super().__init__()
        
        self.predictor = predictor
        self.is_processing = False
        self.is_cancelled = False
        self.current_thread = None
        self.cancel_event = Event()
        
        # 处理统计
        self.total_files = 0
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.start_time = 0
        
        # 结果存储
        self.results = {}
        self.errors = {}
    
    def process_directory(self, dir_path: str, conf_threshold: float = 0.25,
                         iou_threshold: float = 0.45, max_det: int = 100,
                         recursive: bool = True, save_results: bool = False):
        """
        处理目录中的所有图像
        
        Args:
            dir_path: 目录路径
            conf_threshold: 置信度阈值
            iou_threshold: IoU阈值
            max_det: 最大检测数量
            recursive: 是否递归处理子目录
            save_results: 是否保存结果到文件
        """
        if self.is_processing:
            self.error_occurred.emit("批量处理正在进行中")
            return
        
        try:
            # 扫描图像文件
            image_files = self._scan_images(dir_path, recursive)
            
            if not image_files:
                self.error_occurred.emit(f"目录中没有找到支持的图像文件: {dir_path}")
                return
            
            # 开始批量处理
            self._start_batch_processing(
                image_files, conf_threshold, iou_threshold, 
                max_det, save_results
            )
            
        except Exception as e:
            error_msg = f"处理目录失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def process_files(self, file_paths: List[str], conf_threshold: float = 0.25,
                     iou_threshold: float = 0.45, max_det: int = 100,
                     save_results: bool = False):
        """
        处理指定的图像文件列表
        
        Args:
            file_paths: 图像文件路径列表
            conf_threshold: 置信度阈值
            iou_threshold: IoU阈值
            max_det: 最大检测数量
            save_results: 是否保存结果到文件
        """
        if self.is_processing:
            self.error_occurred.emit("批量处理正在进行中")
            return
        
        try:
            # 过滤有效的图像文件
            valid_files = []
            for file_path in file_paths:
                if os.path.exists(file_path) and self._is_image_file(file_path):
                    valid_files.append(file_path)
            
            if not valid_files:
                self.error_occurred.emit("没有找到有效的图像文件")
                return
            
            # 开始批量处理
            self._start_batch_processing(
                valid_files, conf_threshold, iou_threshold,
                max_det, save_results
            )
            
        except Exception as e:
            error_msg = f"处理文件列表失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _scan_images(self, dir_path: str, recursive: bool = True) -> List[str]:
        """扫描目录中的图像文件"""
        image_files = []
        
        try:
            dir_path = Path(dir_path)
            
            if not dir_path.exists() or not dir_path.is_dir():
                return image_files
            
            # 扫描模式
            pattern = "**/*" if recursive else "*"
            
            for format_ext in self.SUPPORTED_FORMATS:
                # 扫描指定格式的文件
                files = dir_path.glob(f"{pattern}{format_ext}")
                image_files.extend([str(f) for f in files if f.is_file()])
                
                # 同时扫描大写格式
                files = dir_path.glob(f"{pattern}{format_ext.upper()}")
                image_files.extend([str(f) for f in files if f.is_file()])
            
            # 去重并排序
            image_files = sorted(list(set(image_files)))
            
            logger.info(f"扫描到 {len(image_files)} 个图像文件")
            
        except Exception as e:
            logger.error(f"扫描图像文件失败: {str(e)}")
        
        return image_files
    
    def _is_image_file(self, file_path: str) -> bool:
        """检查是否为支持的图像文件"""
        try:
            ext = Path(file_path).suffix.lower()
            return ext in self.SUPPORTED_FORMATS
        except Exception:
            return False
    
    def _start_batch_processing(self, file_paths: List[str], conf_threshold: float,
                               iou_threshold: float, max_det: int, save_results: bool):
        """启动批量处理线程"""
        try:
            # 重置状态
            self.is_processing = True
            self.is_cancelled = False
            self.cancel_event.clear()
            
            self.total_files = len(file_paths)
            self.processed_files = 0
            self.successful_files = 0
            self.failed_files = 0
            self.start_time = time.time()
            
            self.results.clear()
            self.errors.clear()
            
            # 发送开始信号
            self.batch_started.emit(self.total_files)
            
            # 创建处理线程
            self.current_thread = Thread(
                target=self._process_batch_worker,
                args=(file_paths, conf_threshold, iou_threshold, max_det, save_results),
                daemon=True
            )
            self.current_thread.start()
            
        except Exception as e:
            error_msg = f"启动批量处理失败: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.is_processing = False
    
    def _process_batch_worker(self, file_paths: List[str], conf_threshold: float,
                             iou_threshold: float, max_det: int, save_results: bool):
        """批量处理工作线程"""
        try:
            logger.info(f"开始批量处理 {len(file_paths)} 个文件")
            
            for i, file_path in enumerate(file_paths):
                # 检查是否取消
                if self.cancel_event.is_set():
                    logger.info("批量处理被取消")
                    self.batch_cancelled.emit()
                    return
                
                try:
                    # 更新进度
                    self.progress_updated.emit(i + 1, self.total_files, os.path.basename(file_path))
                    
                    # 执行预测
                    result = self.predictor.predict_single(
                        file_path, conf_threshold, iou_threshold, max_det
                    )
                    
                    if result is not None:
                        self.results[file_path] = result
                        self.successful_files += 1
                        
                        # 发送单文件完成信号
                        self.file_processed.emit(file_path, result)
                        
                        # 保存结果（如果需要）
                        if save_results:
                            self._save_result(result)
                    else:
                        self.errors[file_path] = "预测失败"
                        self.failed_files += 1
                    
                    self.processed_files += 1
                    
                except Exception as e:
                    error_msg = f"处理文件失败 {file_path}: {str(e)}"
                    logger.error(error_msg)
                    self.errors[file_path] = str(e)
                    self.failed_files += 1
                    self.processed_files += 1
            
            # 处理完成
            total_time = time.time() - self.start_time
            
            summary = {
                'total_files': self.total_files,
                'successful_files': self.successful_files,
                'failed_files': self.failed_files,
                'total_time': total_time,
                'average_time': total_time / self.total_files if self.total_files > 0 else 0,
                'results': self.results,
                'errors': self.errors
            }
            
            logger.info(f"批量处理完成: 成功 {self.successful_files}/{self.total_files}, "
                       f"耗时 {total_time:.2f}秒")
            
            self.batch_completed.emit(summary)
            
        except Exception as e:
            error_msg = f"批量处理工作线程异常: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        
        finally:
            self.is_processing = False
    
    def _save_result(self, result: PredictionResult):
        """保存预测结果到文件"""
        try:
            # 这里可以实现保存逻辑，比如保存为JSON或XML格式
            # 暂时只记录日志
            logger.debug(f"保存预测结果: {result.image_path}, 检测数量: {len(result.detections)}")
            
        except Exception as e:
            logger.error(f"保存预测结果失败: {str(e)}")
    
    def cancel_processing(self):
        """取消当前处理"""
        if self.is_processing:
            logger.info("请求取消批量处理")
            self.is_cancelled = True
            self.cancel_event.set()
    
    def is_busy(self) -> bool:
        """检查是否正在处理"""
        return self.is_processing
    
    def get_progress(self) -> Dict:
        """获取当前进度信息"""
        return {
            'is_processing': self.is_processing,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'progress_percent': (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0,
            'elapsed_time': time.time() - self.start_time if self.start_time > 0 else 0
        }
    
    def get_results(self) -> Dict[str, PredictionResult]:
        """获取处理结果"""
        return self.results.copy()
    
    def get_errors(self) -> Dict[str, str]:
        """获取错误信息"""
        return self.errors.copy()
    
    def clear_results(self):
        """清除结果缓存"""
        self.results.clear()
        self.errors.clear()
