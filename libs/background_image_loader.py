#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后台图片加载器
用于大数据集的分批异步加载，显著提升启动速度
"""

import os
import time
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt5.QtGui import QImage, QImageReader
from libs.ustr import ustr
from libs.utils import natural_sort


class BackgroundImageLoader(QThread):
    """后台图片加载线程"""

    # 信号定义
    batch_loaded = pyqtSignal(list, int, int)  # (images_batch, current_total, estimated_total)
    progress_updated = pyqtSignal(int, int, str)  # (current, total, status_text)
    loading_completed = pyqtSignal(list, int)  # (all_images, corrupted_count)
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, folder_path, initial_batch_size=20, batch_size=100):
        super().__init__()
        self.folder_path = folder_path
        self.initial_batch_size = initial_batch_size
        self.batch_size = batch_size
        self.should_stop = False
        self.mutex = QMutex()

        # 支持的图片格式
        self.extensions = ['.%s' % fmt.data().decode("ascii").lower()
                          for fmt in QImageReader.supportedImageFormats()]

    def stop_loading(self):
        """停止加载"""
        with QMutexLocker(self.mutex):
            self.should_stop = True

    def run(self):
        """主运行逻辑"""
        try:
            images = []
            corrupted_files = []
            current_batch = []
            processed_count = 0
            estimated_total = 0

            # 第一遍：快速估算总数（只统计文件数，不验证）
            self.progress_updated.emit(0, 0, "🔍 正在扫描目录...")

            for root, dirs, files in os.walk(self.folder_path):
                if self.should_stop:
                    return

                for file in files:
                    if file.lower().endswith(tuple(self.extensions)):
                        estimated_total += 1

            self.progress_updated.emit(0, estimated_total, f"📊 发现 {estimated_total} 张图片，开始处理...")

            # 第二遍：实际处理图片
            for root, dirs, files in os.walk(self.folder_path):
                if self.should_stop:
                    return

                # 对文件名进行自然排序
                files = sorted(files, key=lambda x: x.lower())

                for file in files:
                    if self.should_stop:
                        return

                    if file.lower().endswith(tuple(self.extensions)):
                        relative_path = os.path.join(root, file)
                        path = ustr(os.path.abspath(relative_path))

                        # 验证图片
                        is_valid, should_delete = self._validate_image(path)

                        if should_delete:
                            # 删除损坏的图片和对应的标注文件
                            self._remove_corrupted_files(path)
                            corrupted_files.append(os.path.basename(path))
                        elif is_valid:
                            current_batch.append(path)
                            images.append(path)

                        processed_count += 1

                        # 发射进度更新
                        status_text = f"🔄 处理中... ({processed_count}/{estimated_total})"
                        if corrupted_files:
                            status_text += f" | 🗑️ 已清理 {len(corrupted_files)} 个损坏文件"

                        self.progress_updated.emit(processed_count, estimated_total, status_text)

                        # 检查是否需要发射批次
                        batch_size_threshold = self.initial_batch_size if len(images) <= self.initial_batch_size else self.batch_size

                        if len(current_batch) >= batch_size_threshold:
                            # 确保初始批次优先发送
                            if len(images) <= self.initial_batch_size:
                                self.batch_loaded.emit(current_batch.copy(), len(images), estimated_total)
                            elif len(current_batch) >= self.batch_size:
                                self.batch_loaded.emit(current_batch.copy(), len(images), estimated_total)

                            current_batch.clear()

                            # 短暂休眠，避免过度占用CPU
                            self.msleep(1)

            # 发送剩余的批次
            if current_batch and not self.should_stop:
                self.batch_loaded.emit(current_batch.copy(), len(images), estimated_total)

            if not self.should_stop:
                # 对所有图片进行自然排序
                natural_sort(images, key=lambda x: x.lower())

                # 完成信号
                final_status = f"✅ 加载完成！共 {len(images)} 张图片"
                if corrupted_files:
                    final_status += f"，已清理 {len(corrupted_files)} 个损坏文件"

                self.progress_updated.emit(len(images), estimated_total, final_status)
                self.loading_completed.emit(images, len(corrupted_files))

        except Exception as e:
            error_msg = f"加载图片时发生错误: {str(e)}"
            self.error_occurred.emit(error_msg)

    def _validate_image(self, path):
        """
        验证图片是否有效

        Returns:
            tuple: (is_valid, should_delete)
        """
        try:
            # 使用轻量级检查
            test_image = QImage()
            if not test_image.load(path):
                return False, True  # 无法加载，应该删除

            if test_image.isNull() or test_image.width() <= 0 or test_image.height() <= 0:
                return False, True  # 图片数据无效，应该删除

            return True, False  # 图片有效

        except Exception:
            return False, True  # 异常，应该删除

    def _remove_corrupted_files(self, image_path):
        """删除损坏的图片及其标注文件"""
        try:
            # 删除图片文件
            if os.path.exists(image_path):
                os.remove(image_path)

            # 删除对应的标注文件
            base_path = os.path.splitext(image_path)[0]
            annotation_extensions = ['.xml', '.txt', '.json']

            for ext in annotation_extensions:
                ann_file = base_path + ext
                if os.path.exists(ann_file):
                    os.remove(ann_file)

        except Exception as e:
            # 删除失败时忽略错误，不影响主流程
            print(f"[WARNING] 删除损坏文件失败: {e}")


class ProgressiveImageManager:
    """渐进式图片管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.background_loader = None
        self.all_images = []
        self.initial_batch_loaded = False

    def load_directory_progressive(self, folder_path, initial_batch_size=20):
        """
        渐进式加载目录

        Args:
            folder_path: 目录路径
            initial_batch_size: 初始批次大小
        """
        # 停止之前的加载
        if self.background_loader and self.background_loader.isRunning():
            self.background_loader.stop_loading()
            self.background_loader.wait(2000)  # 等待最多2秒

        # 重置状态
        self.all_images.clear()
        self.initial_batch_loaded = False

        # 创建新的后台加载器
        self.background_loader = BackgroundImageLoader(folder_path, initial_batch_size)

        # 连接信号
        self.background_loader.batch_loaded.connect(self.on_batch_loaded)
        self.background_loader.progress_updated.connect(self.on_progress_updated)
        self.background_loader.loading_completed.connect(self.on_loading_completed)
        self.background_loader.error_occurred.connect(self.on_error_occurred)

        # 开始加载
        self.background_loader.start()

    def on_batch_loaded(self, images_batch, current_total, estimated_total):
        """处理批次加载完成"""
        self.all_images.extend(images_batch)

        # 如果是第一批，立即更新UI以快速启动
        if not self.initial_batch_loaded:
            self.initial_batch_loaded = True
            self._update_file_list_fast(images_batch)

            # 加载第一张图片
            if images_batch:
                self.main_window.file_path = None
                self.main_window.load_file(images_batch[0])

        else:
            # 后续批次，批量更新UI
            self._append_to_file_list(images_batch)

    def on_progress_updated(self, current, total, status_text):
        """更新进度"""
        if hasattr(self.main_window, 'status'):
            self.main_window.status(status_text)

    def on_loading_completed(self, all_images, corrupted_count):
        """加载完成"""
        self.all_images = all_images
        self.main_window.m_img_list = all_images
        self.main_window.img_count = len(all_images)

        # 更新UI状态
        self.main_window.update_switch_button_state()
        self.main_window.update_status_bar_info()

        # 最终状态消息
        final_msg = f"🎉 目录加载完成！共 {len(all_images)} 张图片"
        if corrupted_count > 0:
            final_msg += f"，已清理 {corrupted_count} 个损坏文件"

        self.main_window.status(final_msg)

    def on_error_occurred(self, error_message):
        """处理错误"""
        if hasattr(self.main_window, 'status'):
            self.main_window.status(f"❌ {error_message}")

    def _update_file_list_fast(self, images):
        """快速更新文件列表（初始批次）"""
        try:
            file_list = self.main_window.file_list_widget
            file_list.setUpdatesEnabled(False)
            file_list.clear()

            for img_path in images:
                item = QListWidgetItem(img_path)
                file_list.addItem(item)

        finally:
            file_list.setUpdatesEnabled(True)

    def _append_to_file_list(self, images):
        """追加到文件列表（后续批次）"""
        try:
            file_list = self.main_window.file_list_widget
            file_list.setUpdatesEnabled(False)

            for img_path in images:
                item = QListWidgetItem(img_path)
                file_list.addItem(item)

        finally:
            file_list.setUpdatesEnabled(True)

    def stop_loading(self):
        """停止加载"""
        if self.background_loader and self.background_loader.isRunning():
            self.background_loader.stop_loading()
            self.background_loader.wait(3000)  # 等待最多3秒


# 确保导入时可用
from PyQt5.QtWidgets import QListWidgetItem