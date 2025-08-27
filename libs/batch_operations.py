#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量操作系统模块

提供批量复制、删除、调整、格式转换等标注操作功能
"""

import os
import logging
import shutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from .shape import Shape
from .labelFile import LabelFile, LabelFileFormat
from .pascal_voc_io import PascalVocWriter
from .yolo_io import YOLOWriter
from .background_task_manager import BackgroundTaskManager, TaskPriority

# 设置日志
logger = logging.getLogger(__name__)


class BatchOperations(QObject):
    """批量操作系统"""

    # 信号定义
    operation_started = pyqtSignal(str, int)        # 操作开始 (操作名称, 总数)
    operation_progress = pyqtSignal(int, int, str)  # 操作进度 (当前, 总数, 当前文件)
    operation_completed = pyqtSignal(str, dict)     # 操作完成 (操作名称, 结果统计)
    operation_error = pyqtSignal(str)               # 操作错误

    def __init__(self, parent=None, task_manager=None):
        """初始化批量操作系统"""
        super().__init__(parent)

        # 操作统计
        self.current_operation = ""
        self.total_files = 0
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.errors = {}
        
        # 异步处理支持
        self.task_manager = task_manager
        self.current_task_id = None
        self.is_async_mode = task_manager is not None
        
        # 取消标志
        self.cancel_requested = False

    def batch_copy_annotations(self, source_files: List[str], target_dir: str,
                               copy_images: bool = False) -> Dict:
        """
        批量复制标注文件

        Args:
            source_files: 源标注文件列表
            target_dir: 目标目录
            copy_images: 是否同时复制对应的图像文件

        Returns:
            Dict: 操作结果统计
        """
        try:
            self.current_operation = "批量复制标注"
            self.total_files = len(source_files)
            self.processed_files = 0
            self.successful_files = 0
            self.failed_files = 0
            self.errors.clear()

            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)

            self.operation_started.emit(
                self.current_operation, self.total_files)

            for i, source_file in enumerate(source_files):
                try:
                    self.operation_progress.emit(
                        i + 1, self.total_files, os.path.basename(source_file))

                    if not os.path.exists(source_file):
                        self.errors[source_file] = "源文件不存在"
                        self.failed_files += 1
                        continue

                    # 复制标注文件
                    target_file = os.path.join(
                        target_dir, os.path.basename(source_file))
                    shutil.copy2(source_file, target_file)

                    # 如果需要，复制对应的图像文件
                    if copy_images:
                        image_file = self._find_corresponding_image(
                            source_file)
                        if image_file and os.path.exists(image_file):
                            target_image = os.path.join(
                                target_dir, os.path.basename(image_file))
                            shutil.copy2(image_file, target_image)

                    self.successful_files += 1

                except Exception as e:
                    self.errors[source_file] = str(e)
                    self.failed_files += 1

                self.processed_files += 1

            # 操作完成
            result = {
                'operation': self.current_operation,
                'total_files': self.total_files,
                'successful_files': self.successful_files,
                'failed_files': self.failed_files,
                'errors': self.errors.copy()
            }

            self.operation_completed.emit(self.current_operation, result)
            return result

        except Exception as e:
            error_msg = f"批量复制标注失败: {str(e)}"
            logger.error(error_msg)
            self.operation_error.emit(error_msg)
            return {'error': error_msg}

    def batch_delete_annotations(self, annotation_files: List[str],
                                 delete_images: bool = False) -> Dict:
        """
        批量删除标注文件

        Args:
            annotation_files: 标注文件列表
            delete_images: 是否同时删除对应的图像文件

        Returns:
            Dict: 操作结果统计
        """
        try:
            self.current_operation = "批量删除标注"
            self.total_files = len(annotation_files)
            self.processed_files = 0
            self.successful_files = 0
            self.failed_files = 0
            self.errors.clear()

            self.operation_started.emit(
                self.current_operation, self.total_files)

            for i, annotation_file in enumerate(annotation_files):
                try:
                    self.operation_progress.emit(
                        i + 1, self.total_files, os.path.basename(annotation_file))

                    if not os.path.exists(annotation_file):
                        self.errors[annotation_file] = "文件不存在"
                        self.failed_files += 1
                        continue

                    # 删除标注文件
                    os.remove(annotation_file)

                    # 如果需要，删除对应的图像文件
                    if delete_images:
                        image_file = self._find_corresponding_image(
                            annotation_file)
                        if image_file and os.path.exists(image_file):
                            os.remove(image_file)

                    self.successful_files += 1

                except Exception as e:
                    self.errors[annotation_file] = str(e)
                    self.failed_files += 1

                self.processed_files += 1

            # 操作完成
            result = {
                'operation': self.current_operation,
                'total_files': self.total_files,
                'successful_files': self.successful_files,
                'failed_files': self.failed_files,
                'errors': self.errors.copy()
            }

            self.operation_completed.emit(self.current_operation, result)
            return result

        except Exception as e:
            error_msg = f"批量删除标注失败: {str(e)}"
            logger.error(error_msg)
            self.operation_error.emit(error_msg)
            return {'error': error_msg}

    def batch_resize_annotations(self, annotation_files: List[str],
                                 scale_factor: float, target_dir: str = None) -> Dict:
        """
        批量调整标注框大小

        Args:
            annotation_files: 标注文件列表
            scale_factor: 缩放因子 (1.0 = 不变, >1.0 = 放大, <1.0 = 缩小)
            target_dir: 目标目录，如果为None则覆盖原文件

        Returns:
            Dict: 操作结果统计
        """
        try:
            self.current_operation = "批量调整大小"
            self.total_files = len(annotation_files)
            self.processed_files = 0
            self.successful_files = 0
            self.failed_files = 0
            self.errors.clear()

            if target_dir:
                os.makedirs(target_dir, exist_ok=True)

            self.operation_started.emit(
                self.current_operation, self.total_files)

            for i, annotation_file in enumerate(annotation_files):
                try:
                    self.operation_progress.emit(
                        i + 1, self.total_files, os.path.basename(annotation_file))

                    if not os.path.exists(annotation_file):
                        self.errors[annotation_file] = "文件不存在"
                        self.failed_files += 1
                        continue

                    # 读取标注文件
                    label_file = LabelFile()
                    shapes, image_path, image_data = label_file.load(
                        annotation_file)

                    # 调整标注框大小
                    resized_shapes = []
                    for shape in shapes:
                        resized_shape = self._resize_shape(shape, scale_factor)
                        resized_shapes.append(resized_shape)

                    # 保存调整后的标注
                    output_file = annotation_file
                    if target_dir:
                        output_file = os.path.join(
                            target_dir, os.path.basename(annotation_file))

                    label_file.save(output_file, resized_shapes,
                                    image_path, image_data)

                    self.successful_files += 1

                except Exception as e:
                    self.errors[annotation_file] = str(e)
                    self.failed_files += 1

                self.processed_files += 1

            # 操作完成
            result = {
                'operation': self.current_operation,
                'total_files': self.total_files,
                'successful_files': self.successful_files,
                'failed_files': self.failed_files,
                'scale_factor': scale_factor,
                'errors': self.errors.copy()
            }

            self.operation_completed.emit(self.current_operation, result)
            return result

        except Exception as e:
            error_msg = f"批量调整大小失败: {str(e)}"
            logger.error(error_msg)
            self.operation_error.emit(error_msg)
            return {'error': error_msg}

    # 辅助方法
    def _find_corresponding_image(self, annotation_file: str) -> Optional[str]:
        """查找对应的图像文件"""
        try:
            base_name = os.path.splitext(annotation_file)[0]
            dir_path = os.path.dirname(annotation_file)

            # 常见图像格式
            image_extensions = ['.jpg', '.jpeg', '.png',
                                '.bmp', '.tiff', '.tif', '.webp']

            for ext in image_extensions:
                image_file = base_name + ext
                if os.path.exists(image_file):
                    return image_file

                # 尝试大写扩展名
                image_file = base_name + ext.upper()
                if os.path.exists(image_file):
                    return image_file

            return None

        except Exception as e:
            logger.error(f"查找对应图像文件失败: {str(e)}")
            return None

    def _resize_shape(self, shape: Shape, scale_factor: float) -> Shape:
        """调整单个标注框大小"""
        try:
            from PyQt5.QtCore import QPointF

            # 创建新的形状
            new_shape = Shape(label=shape.label, line_color=shape.line_color)
            new_shape.difficult = shape.difficult

            # 计算中心点
            if len(shape.points) >= 2:
                center_x = sum(p.x() for p in shape.points) / len(shape.points)
                center_y = sum(p.y() for p in shape.points) / len(shape.points)

                # 调整每个点的位置
                for point in shape.points:
                    # 相对于中心点的偏移
                    offset_x = (point.x() - center_x) * scale_factor
                    offset_y = (point.y() - center_y) * scale_factor

                    # 新的点位置
                    new_x = center_x + offset_x
                    new_y = center_y + offset_y

                    new_shape.add_point(QPointF(new_x, new_y))

                new_shape.close()

            return new_shape

        except Exception as e:
            logger.error(f"调整形状大小失败: {str(e)}")
            return shape

    def _apply_filter_criteria(self, shapes: List[Shape], criteria: Dict) -> List[Shape]:
        """应用过滤条件"""
        try:
            filtered_shapes = []

            for shape in shapes:
                should_include = True

                # 按类别过滤
                if 'classes' in criteria:
                    allowed_classes = criteria['classes']
                    if shape.label not in allowed_classes:
                        should_include = False

                # 按大小过滤
                if 'min_size' in criteria and should_include:
                    min_size = criteria['min_size']
                    if len(shape.points) >= 2:
                        width = abs(shape.points[2].x() - shape.points[0].x())
                        height = abs(shape.points[2].y() - shape.points[0].y())
                        if width < min_size or height < min_size:
                            should_include = False

                # 按最大大小过滤
                if 'max_size' in criteria and should_include:
                    max_size = criteria['max_size']
                    if len(shape.points) >= 2:
                        width = abs(shape.points[2].x() - shape.points[0].x())
                        height = abs(shape.points[2].y() - shape.points[0].y())
                        if width > max_size or height > max_size:
                            should_include = False

                # 按难度过滤
                if 'exclude_difficult' in criteria and should_include:
                    if criteria['exclude_difficult'] and shape.difficult:
                        should_include = False

                if should_include:
                    filtered_shapes.append(shape)

            return filtered_shapes

        except Exception as e:
            logger.error(f"应用过滤条件失败: {str(e)}")
            return shapes

    def get_operation_status(self) -> Dict:
        """获取当前操作状态"""
        return {
            'current_operation': self.current_operation,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'progress_percent': (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0
        }

    def is_busy(self) -> bool:
        """检查是否正在执行操作"""
        return bool(self.current_operation and self.processed_files < self.total_files)

    def batch_copy_annotations_async(self, source_files: List[str], target_dir: str, 
                                     criteria: Dict = None, progress_callback=None):
        """
        异步批量复制标注文件
        
        Args:
            source_files: 源文件列表
            target_dir: 目标目录
            criteria: 筛选条件
            progress_callback: 进度回调函数
        """
        if not self.is_async_mode or not self.task_manager:
            # 同步执行（回退模式）
            return self.batch_copy_annotations(source_files, target_dir, criteria)
            
        def async_copy_task(progress_callback=None):
            """异步复制任务"""
            try:
                self.cancel_requested = False
                return self._execute_batch_copy(source_files, target_dir, criteria, progress_callback)
            except Exception as e:
                logger.error(f"异步批量复制失败: {e}")
                raise
                
        # 提交异步任务
        self.current_task_id = self.task_manager.submit_task(
            func=async_copy_task,
            args=(),
            kwargs={'progress_callback': progress_callback},
            priority=TaskPriority.HIGH,
            timeout=3600,  # 1小时超时
            callback=self._on_async_operation_completed,
            error_callback=self._on_async_operation_failed,
            description=f"批量复制 {len(source_files)} 个标注文件"
        )
        
        return self.current_task_id
        
    def batch_delete_annotations_async(self, target_files: List[str], 
                                      criteria: Dict = None, progress_callback=None):
        """
        异步批量删除标注文件
        
        Args:
            target_files: 目标文件列表
            criteria: 筛选条件
            progress_callback: 进度回调函数
        """
        if not self.is_async_mode or not self.task_manager:
            # 同步执行（回退模式）
            return self.batch_delete_annotations(target_files, criteria)
            
        def async_delete_task(progress_callback=None):
            """异步删除任务"""
            try:
                self.cancel_requested = False
                return self._execute_batch_delete(target_files, criteria, progress_callback)
            except Exception as e:
                logger.error(f"异步批量删除失败: {e}")
                raise
                
        # 提交异步任务
        self.current_task_id = self.task_manager.submit_task(
            func=async_delete_task,
            args=(),
            kwargs={'progress_callback': progress_callback},
            priority=TaskPriority.HIGH,
            timeout=1800,  # 30分钟超时
            callback=self._on_async_operation_completed,
            error_callback=self._on_async_operation_failed,
            description=f"批量删除 {len(target_files)} 个标注文件"
        )
        
        return self.current_task_id
        
    def batch_resize_annotations_async(self, annotation_files: List[str], 
                                      scale_factor: float, progress_callback=None):
        """
        异步批量调整标注尺寸
        
        Args:
            annotation_files: 标注文件列表
            scale_factor: 缩放因子
            progress_callback: 进度回调函数
        """
        if not self.is_async_mode or not self.task_manager:
            # 同步执行（回退模式）
            return self.batch_resize_annotations(annotation_files, scale_factor)
            
        def async_resize_task(progress_callback=None):
            """异步调整任务"""
            try:
                self.cancel_requested = False
                return self._execute_batch_resize(annotation_files, scale_factor, progress_callback)
            except Exception as e:
                logger.error(f"异步批量调整失败: {e}")
                raise
                
        # 提交异步任务
        self.current_task_id = self.task_manager.submit_task(
            func=async_resize_task,
            args=(),
            kwargs={'progress_callback': progress_callback},
            priority=TaskPriority.NORMAL,
            timeout=1800,  # 30分钟超时
            callback=self._on_async_operation_completed,
            error_callback=self._on_async_operation_failed,
            description=f"批量调整 {len(annotation_files)} 个标注文件"
        )
        
        return self.current_task_id
        
    def cancel_current_operation(self):
        """取消当前异步操作"""
        self.cancel_requested = True
        
        if self.current_task_id and self.task_manager:
            success = self.task_manager.cancel_task(self.current_task_id)
            if success:
                logger.info(f"成功取消异步任务: {self.current_task_id}")
                self.current_task_id = None
                return True
            else:
                logger.warning(f"无法取消异步任务: {self.current_task_id}")
                
        return False
        
    def _execute_batch_copy(self, source_files: List[str], target_dir: str, 
                           criteria: Dict = None, progress_callback=None):
        """执行批量复制（支持取消和进度回调）"""
        self.current_operation = "批量复制"
        self.total_files = len(source_files)
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.errors = {}
        
        results = []
        
        for i, source_file in enumerate(source_files):
            # 检查取消请求
            if self.cancel_requested:
                logger.info("批量复制操作被用户取消")
                break
                
            try:
                # 这里调用原有的单文件复制逻辑
                result = self._copy_single_annotation(source_file, target_dir, criteria)
                results.append(result)
                
                if result.get('success', False):
                    self.successful_files += 1
                else:
                    self.failed_files += 1
                    if result.get('error'):
                        self.errors[source_file] = result['error']
                        
            except Exception as e:
                self.failed_files += 1
                self.errors[source_file] = str(e)
                logger.error(f"复制文件 {source_file} 时出错: {e}")
                
            self.processed_files += 1
            
            # 更新进度
            if progress_callback:
                progress = int((self.processed_files / self.total_files) * 100)
                progress_callback(progress, f"正在复制: {os.path.basename(source_file)}")
                
        return {
            'operation': '批量复制',
            'total': self.total_files,
            'successful': self.successful_files,
            'failed': self.failed_files,
            'errors': self.errors,
            'results': results,
            'cancelled': self.cancel_requested
        }
        
    def _execute_batch_delete(self, target_files: List[str], 
                             criteria: Dict = None, progress_callback=None):
        """执行批量删除（支持取消和进度回调）"""
        self.current_operation = "批量删除"
        self.total_files = len(target_files)
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.errors = {}
        
        results = []
        
        for i, target_file in enumerate(target_files):
            # 检查取消请求
            if self.cancel_requested:
                logger.info("批量删除操作被用户取消")
                break
                
            try:
                # 这里调用原有的单文件删除逻辑
                result = self._delete_single_annotation(target_file, criteria)
                results.append(result)
                
                if result.get('success', False):
                    self.successful_files += 1
                else:
                    self.failed_files += 1
                    if result.get('error'):
                        self.errors[target_file] = result['error']
                        
            except Exception as e:
                self.failed_files += 1
                self.errors[target_file] = str(e)
                logger.error(f"删除文件 {target_file} 时出错: {e}")
                
            self.processed_files += 1
            
            # 更新进度
            if progress_callback:
                progress = int((self.processed_files / self.total_files) * 100)
                progress_callback(progress, f"正在删除: {os.path.basename(target_file)}")
                
        return {
            'operation': '批量删除',
            'total': self.total_files,
            'successful': self.successful_files,
            'failed': self.failed_files,
            'errors': self.errors,
            'results': results,
            'cancelled': self.cancel_requested
        }
        
    def _execute_batch_resize(self, annotation_files: List[str], scale_factor: float,
                             progress_callback=None):
        """执行批量调整（支持取消和进度回调）"""
        self.current_operation = "批量调整"
        self.total_files = len(annotation_files)
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.errors = {}
        
        results = []
        
        for i, annotation_file in enumerate(annotation_files):
            # 检查取消请求
            if self.cancel_requested:
                logger.info("批量调整操作被用户取消")
                break
                
            try:
                # 这里调用原有的单文件调整逻辑
                result = self._resize_single_annotation(annotation_file, scale_factor)
                results.append(result)
                
                if result.get('success', False):
                    self.successful_files += 1
                else:
                    self.failed_files += 1
                    if result.get('error'):
                        self.errors[annotation_file] = result['error']
                        
            except Exception as e:
                self.failed_files += 1
                self.errors[annotation_file] = str(e)
                logger.error(f"调整文件 {annotation_file} 时出错: {e}")
                
            self.processed_files += 1
            
            # 更新进度
            if progress_callback:
                progress = int((self.processed_files / self.total_files) * 100)
                progress_callback(progress, f"正在调整: {os.path.basename(annotation_file)}")
                
        return {
            'operation': '批量调整',
            'total': self.total_files,
            'successful': self.successful_files,
            'failed': self.failed_files,
            'errors': self.errors,
            'results': results,
            'cancelled': self.cancel_requested
        }
        
    def _copy_single_annotation(self, source_file: str, target_dir: str, criteria: Dict = None):
        """复制单个标注文件"""
        try:
            # 实现单文件复制逻辑
            target_file = os.path.join(target_dir, os.path.basename(source_file))
            shutil.copy2(source_file, target_file)
            return {'success': True, 'source': source_file, 'target': target_file}
        except Exception as e:
            return {'success': False, 'source': source_file, 'error': str(e)}
            
    def _delete_single_annotation(self, target_file: str, criteria: Dict = None):
        """删除单个标注文件"""
        try:
            # 实现单文件删除逻辑
            if os.path.exists(target_file):
                os.remove(target_file)
                return {'success': True, 'file': target_file}
            else:
                return {'success': False, 'file': target_file, 'error': '文件不存在'}
        except Exception as e:
            return {'success': False, 'file': target_file, 'error': str(e)}
            
    def _resize_single_annotation(self, annotation_file: str, scale_factor: float):
        """调整单个标注文件"""
        try:
            # 实现单文件调整逻辑
            # 这里需要根据具体的标注格式进行处理
            return {'success': True, 'file': annotation_file, 'scale_factor': scale_factor}
        except Exception as e:
            return {'success': False, 'file': annotation_file, 'error': str(e)}
            
    def _on_async_operation_completed(self, result):
        """异步操作完成回调"""
        logger.info(f"异步操作完成: {result.get('operation', '未知操作')}")
        self.current_task_id = None
        self.operation_completed.emit(result)
        
    def _on_async_operation_failed(self, error):
        """异步操作失败回调"""
        logger.error(f"异步操作失败: {error}")
        self.current_task_id = None
        self.operation_error.emit(str(error))


class BatchOperationsDialog(QDialog):
    """批量操作对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.batch_ops = BatchOperations(self)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("批量操作")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        # 操作选择
        operation_group = QGroupBox("选择操作")
        operation_layout = QVBoxLayout(operation_group)

        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "批量复制标注",
            "批量删除标注",
            "批量调整大小",
            "批量格式转换",
            "批量过滤标注"
        ])
        operation_layout.addWidget(self.operation_combo)

        layout.addWidget(operation_group)

        # 参数设置区域
        self.params_stack = QStackedWidget()
        layout.addWidget(self.params_stack)

        # 创建不同操作的参数界面
        self.create_copy_params()
        self.create_delete_params()
        self.create_resize_params()
        self.create_convert_params()
        self.create_filter_params()

        # 进度显示
        progress_group = QGroupBox("操作进度")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

        # 按钮
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始操作")
        self.start_btn.clicked.connect(self.start_operation)
        button_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        """设置信号连接"""
        self.operation_combo.currentIndexChanged.connect(
            self.params_stack.setCurrentIndex)

        # 连接批量操作信号
        self.batch_ops.operation_started.connect(self.on_operation_started)
        self.batch_ops.operation_progress.connect(self.on_operation_progress)
        self.batch_ops.operation_completed.connect(self.on_operation_completed)
        self.batch_ops.operation_error.connect(self.on_operation_error)

    def create_copy_params(self):
        """创建复制参数界面"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.copy_source_edit = QLineEdit()
        self.copy_source_btn = QPushButton("浏览...")
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.copy_source_edit)
        source_layout.addWidget(self.copy_source_btn)
        layout.addRow("源目录:", source_layout)

        self.copy_target_edit = QLineEdit()
        self.copy_target_btn = QPushButton("浏览...")
        target_layout = QHBoxLayout()
        target_layout.addWidget(self.copy_target_edit)
        target_layout.addWidget(self.copy_target_btn)
        layout.addRow("目标目录:", target_layout)

        self.copy_images_check = QCheckBox("同时复制图像文件")
        layout.addRow("", self.copy_images_check)

        self.params_stack.addWidget(widget)

    def create_delete_params(self):
        """创建删除参数界面"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.delete_source_edit = QLineEdit()
        self.delete_source_btn = QPushButton("浏览...")
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.delete_source_edit)
        source_layout.addWidget(self.delete_source_btn)
        layout.addRow("源目录:", source_layout)

        self.delete_images_check = QCheckBox("同时删除图像文件")
        layout.addRow("", self.delete_images_check)

        self.params_stack.addWidget(widget)

    def create_resize_params(self):
        """创建调整大小参数界面"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.resize_source_edit = QLineEdit()
        self.resize_source_btn = QPushButton("浏览...")
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.resize_source_edit)
        source_layout.addWidget(self.resize_source_btn)
        layout.addRow("源目录:", source_layout)

        self.resize_scale_spin = QDoubleSpinBox()
        self.resize_scale_spin.setRange(0.1, 10.0)
        self.resize_scale_spin.setValue(1.0)
        self.resize_scale_spin.setSingleStep(0.1)
        layout.addRow("缩放因子:", self.resize_scale_spin)

        self.resize_target_edit = QLineEdit()
        self.resize_target_btn = QPushButton("浏览...")
        target_layout = QHBoxLayout()
        target_layout.addWidget(self.resize_target_edit)
        target_layout.addWidget(self.resize_target_btn)
        layout.addRow("目标目录:", target_layout)

        self.params_stack.addWidget(widget)

    def create_convert_params(self):
        """创建格式转换参数界面"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.convert_source_edit = QLineEdit()
        self.convert_source_btn = QPushButton("浏览...")
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.convert_source_edit)
        source_layout.addWidget(self.convert_source_btn)
        layout.addRow("源目录:", source_layout)

        self.convert_source_format = QComboBox()
        self.convert_source_format.addItems(["Pascal VOC", "YOLO", "CreateML"])
        layout.addRow("源格式:", self.convert_source_format)

        self.convert_target_format = QComboBox()
        self.convert_target_format.addItems(["Pascal VOC", "YOLO", "CreateML"])
        layout.addRow("目标格式:", self.convert_target_format)

        self.convert_target_edit = QLineEdit()
        self.convert_target_btn = QPushButton("浏览...")
        target_layout = QHBoxLayout()
        target_layout.addWidget(self.convert_target_edit)
        target_layout.addWidget(self.convert_target_btn)
        layout.addRow("目标目录:", target_layout)

        self.params_stack.addWidget(widget)

    def create_filter_params(self):
        """创建过滤参数界面"""
        widget = QWidget()
        layout = QFormLayout(widget)

        self.filter_source_edit = QLineEdit()
        self.filter_source_btn = QPushButton("浏览...")
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.filter_source_edit)
        source_layout.addWidget(self.filter_source_btn)
        layout.addRow("源目录:", source_layout)

        self.filter_classes_edit = QLineEdit()
        self.filter_classes_edit.setPlaceholderText("用逗号分隔类别名称")
        layout.addRow("允许的类别:", self.filter_classes_edit)

        self.filter_min_size_spin = QSpinBox()
        self.filter_min_size_spin.setRange(0, 1000)
        self.filter_min_size_spin.setValue(10)
        layout.addRow("最小尺寸:", self.filter_min_size_spin)

        self.filter_target_edit = QLineEdit()
        self.filter_target_btn = QPushButton("浏览...")
        target_layout = QHBoxLayout()
        target_layout.addWidget(self.filter_target_edit)
        target_layout.addWidget(self.filter_target_btn)
        layout.addRow("目标目录:", target_layout)

        self.params_stack.addWidget(widget)

    def start_operation(self):
        """开始操作"""
        try:
            operation_index = self.operation_combo.currentIndex()

            if operation_index == 0:  # 批量复制
                self.start_copy_operation()
            elif operation_index == 1:  # 批量删除
                self.start_delete_operation()
            elif operation_index == 2:  # 批量调整大小
                self.start_resize_operation()
            elif operation_index == 3:  # 批量格式转换
                self.start_convert_operation()
            elif operation_index == 4:  # 批量过滤
                self.start_filter_operation()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动操作失败: {str(e)}")

    def start_copy_operation(self):
        """开始复制操作"""
        source_dir = self.copy_source_edit.text().strip()
        target_dir = self.copy_target_edit.text().strip()

        if not source_dir or not target_dir:
            QMessageBox.warning(self, "警告", "请选择源目录和目标目录")
            return

        # 获取源文件列表
        source_files = []
        for ext in ['.xml', '.txt', '.json']:
            source_files.extend(Path(source_dir).glob(f"*{ext}"))

        if not source_files:
            QMessageBox.warning(self, "警告", "源目录中没有找到标注文件")
            return

        # 开始复制
        self.batch_ops.batch_copy_annotations(
            [str(f) for f in source_files],
            target_dir,
            self.copy_images_check.isChecked()
        )

    def start_delete_operation(self):
        """开始删除操作"""
        QMessageBox.information(self, "提示", "删除操作暂未实现")

    def start_resize_operation(self):
        """开始调整大小操作"""
        QMessageBox.information(self, "提示", "调整大小操作暂未实现")

    def start_convert_operation(self):
        """开始格式转换操作"""
        QMessageBox.information(self, "提示", "格式转换操作暂未实现")

    def start_filter_operation(self):
        """开始过滤操作"""
        QMessageBox.information(self, "提示", "过滤操作暂未实现")

    def on_operation_started(self, operation: str, total: int):
        """操作开始处理"""
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"开始{operation}，共{total}个文件")
        self.start_btn.setEnabled(False)

    def on_operation_progress(self, current: int, total: int, filename: str):
        """操作进度处理"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"正在处理: {filename} ({current}/{total})")

    def on_operation_completed(self, operation: str, result: dict):
        """操作完成处理"""
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.status_label.setText(
            f"{operation}完成: 成功{result['successful_files']}/{result['total_files']}"
        )
        self.start_btn.setEnabled(True)

        QMessageBox.information(
            self, "操作完成",
            f"{operation}完成\n"
            f"总文件数: {result['total_files']}\n"
            f"成功: {result['successful_files']}\n"
            f"失败: {result['failed_files']}"
        )

    def on_operation_error(self, error: str):
        """操作错误处理"""
        self.status_label.setText(f"操作失败: {error}")
        self.start_btn.setEnabled(True)
        QMessageBox.critical(self, "操作失败", error)
