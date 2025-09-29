#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后台图片加载器
用于大数据集的分批异步加载，显著提升启动速度
"""

import os
import time
import struct
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker, QTimer
from PyQt5.QtGui import QImage, QImageReader
from libs.ustr import ustr
from libs.utils import natural_sort
from libs.constants import SETTING_LAST_DIR_IMAGE_COUNT

# 尝试导入psutil，如果没有则使用简化版本
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("[WARNING] psutil 不可用，系统监控功能将被禁用")
    PSUTIL_AVAILABLE = False

    # 创建psutil的简化替代
    class FakePSUtil:
        @staticmethod
        def cpu_percent(interval=1):
            return 50.0  # 默认假设50%使用率

        @staticmethod
        def virtual_memory():
            class Memory:
                percent = 50.0
            return Memory()

    psutil = FakePSUtil()


def calculate_optimal_thread_count(performance_mode="balanced"):
    """
    计算最优线程数量，考虑系统负载和性能模式

    Args:
        performance_mode: 性能模式 ("conservative", "balanced", "aggressive")

    Returns:
        int: 推荐的线程数量
    """
    try:
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()

        # 获取当前CPU使用率
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
        except:
            cpu_percent = 50  # 默认假设50%使用率

        # 根据性能模式和系统状态计算线程数
        if performance_mode == "conservative":
            # 保守模式：最多使用一半的CPU核心
            base_threads = max(1, cpu_count // 2)
        elif performance_mode == "balanced":
            # 平衡模式：根据CPU核心数适度并行
            if cpu_count <= 2:
                base_threads = 1
            elif cpu_count <= 4:
                base_threads = 2
            elif cpu_count <= 8:
                base_threads = 3
            else:
                base_threads = 4  # 最多4个线程
        else:  # aggressive
            # 激进模式：使用更多线程，但仍有限制
            base_threads = min(6, max(2, cpu_count // 2))

        # 根据当前CPU使用率调整
        if cpu_percent > 80:
            base_threads = max(1, base_threads // 2)  # CPU繁忙时减少线程
        elif cpu_percent > 60:
            base_threads = max(1, int(base_threads * 0.75))

        return base_threads

    except Exception as e:
        print(f"[WARNING] 计算最优线程数失败: {e}")
        return 2  # 安全的默认值


class SystemResourceMonitor(QThread):
    """系统资源监控器"""

    resource_warning = pyqtSignal(str)  # 资源警告信号
    should_reduce_load = pyqtSignal()   # 建议减少负载信号

    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.check_interval = 2.0  # 检查间隔（秒）

    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self.start()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.wait(3000)

    def run(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 检查CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent

                # CPU使用率过高时发出警告
                if cpu_percent > 85:
                    self.resource_warning.emit(f"CPU使用率过高: {cpu_percent:.1f}%")
                    self.should_reduce_load.emit()

                # 内存使用率过高时发出警告
                if memory_percent > 90:
                    self.resource_warning.emit(f"内存使用率过高: {memory_percent:.1f}%")
                    self.should_reduce_load.emit()

                # 休眠
                time.sleep(self.check_interval)

            except Exception as e:
                print(f"[WARNING] 资源监控异常: {e}")
                time.sleep(5)  # 出错时增加休眠时间


def validate_image_fast(image_path):
    """
    快速验证图片文件有效性
    使用文件头检查，避免完全加载图片

    Returns:
        tuple: (is_valid, should_delete, error_msg)
    """
    try:
        if not os.path.exists(image_path):
            return False, True, "文件不存在"

        file_size = os.path.getsize(image_path)
        if file_size < 10:  # 太小的文件肯定不是有效图片
            return False, True, "文件太小"

        # 检查文件扩展名
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp']:
            return False, False, "不支持的格式"

        # 快速文件头检查
        with open(image_path, 'rb') as f:
            header = f.read(16)

        if len(header) < 8:
            return False, True, "文件头不完整"

        # 检查常见图片格式的文件头
        if header.startswith(b'\xFF\xD8\xFF'):  # JPEG
            return True, False, ""
        elif header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
            return True, False, ""
        elif header.startswith(b'BM'):  # BMP
            return True, False, ""
        elif header.startswith(b'GIF8'):  # GIF
            return True, False, ""
        elif header.startswith(b'RIFF') and b'WEBP' in header:  # WebP
            return True, False, ""
        elif header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):  # TIFF
            return True, False, ""
        else:
            # 如果文件头检查失败，使用Qt进行更深度验证
            try:
                test_image = QImage()
                if not test_image.load(image_path):
                    return False, True, "无法加载"
                if test_image.isNull() or test_image.width() <= 0 or test_image.height() <= 0:
                    return False, True, "图片数据无效"
                return True, False, ""
            except Exception as e:
                return False, True, f"验证异常: {str(e)}"

    except Exception as e:
        return False, True, f"文件访问异常: {str(e)}"


class MultiThreadImageLoader(QThread):
    """多线程图片加载器 - 高性能版本"""

    # 信号定义
    batch_loaded = pyqtSignal(list, int, int)  # (images_batch, current_total, estimated_total)
    progress_updated = pyqtSignal(int, int, str)  # (current, total, status_text)
    loading_completed = pyqtSignal(list, int)  # (all_images, corrupted_count)
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, folder_path, initial_batch_size=20, batch_size=100, max_workers=None, performance_mode="balanced"):
        super().__init__()
        self.folder_path = folder_path
        self.initial_batch_size = initial_batch_size
        self.batch_size = batch_size
        self.should_stop = False
        self.mutex = QMutex()
        self.performance_mode = performance_mode

        # 智能设置工作线程数
        if max_workers is None:
            self.max_workers = calculate_optimal_thread_count(performance_mode)
            print(f"[DEBUG] 智能计算线程数: {self.max_workers} (模式: {performance_mode})")
        else:
            self.max_workers = max_workers

        # 初始化资源监控器
        self.resource_monitor = None
        self.current_workers = self.max_workers  # 当前活跃的工作线程数

        # 支持的图片格式
        self.extensions = ['.%s' % fmt.data().decode("ascii").lower()
                          for fmt in QImageReader.supportedImageFormats()]

        # 统计信息
        self.stats = {
            'processed': 0,
            'valid': 0,
            'corrupted': 0,
            'errors': [],
            'thread_adjustments': 0
        }

    def stop_loading(self):
        """停止加载"""
        with QMutexLocker(self.mutex):
            self.should_stop = True

        # 停止资源监控
        if self.resource_monitor:
            self.resource_monitor.stop_monitoring()
            self.resource_monitor = None

    def on_resource_warning(self, warning_msg):
        """处理资源警告"""
        print(f"[WARNING] {warning_msg}")

    def on_should_reduce_load(self):
        """降低系统负载"""
        with QMutexLocker(self.mutex):
            if self.current_workers > 1:
                self.current_workers = max(1, self.current_workers - 1)
                self.stats['thread_adjustments'] += 1
                print(f"[INFO] 由于系统负载过高，降低并发度至 {self.current_workers} 线程")

    def run(self):
        """主运行逻辑 - 智能多线程版本"""
        try:
            # 启动资源监控
            if self.performance_mode != "conservative":
                try:
                    self.resource_monitor = SystemResourceMonitor()
                    self.resource_monitor.resource_warning.connect(self.on_resource_warning)
                    self.resource_monitor.should_reduce_load.connect(self.on_should_reduce_load)
                    self.resource_monitor.start_monitoring()
                except Exception as e:
                    print(f"[WARNING] 资源监控启动失败: {e}")

            # 阶段1: 快速文件发现
            self.progress_updated.emit(0, 0, "正在扫描目录...")

            file_paths = []
            for root, dirs, files in os.walk(self.folder_path):
                if self.should_stop:
                    return

                for file in files:
                    if file.lower().endswith(tuple(self.extensions)):
                        full_path = os.path.abspath(os.path.join(root, file))
                        file_paths.append(ustr(full_path))

            if not file_paths:
                self.loading_completed.emit([], 0)
                return

            # 自然排序
            file_paths = sorted(file_paths, key=lambda x: x.lower())
            total_files = len(file_paths)

            self.progress_updated.emit(0, total_files, f"发现 {total_files} 个图片文件，开始智能验证...")

            # 阶段2: 智能多线程并行验证
            valid_images = []
            corrupted_files = []
            processed_count = 0
            current_batch = []

            # 实现渐进式并发控制
            self.current_workers = min(self.max_workers, max(1, len(file_paths) // 100))  # 根据文件数量调整初始线程数
            print(f"[DEBUG] 使用 {self.current_workers} 个工作线程处理 {total_files} 个文件")

            # 使用智能分批处理策略
            batch_size_for_processing = self.current_workers * 10  # 每批处理的文件数量

            with ThreadPoolExecutor(max_workers=self.current_workers, thread_name_prefix="ImgLoader") as executor:
                # 分批提交任务，避免一次性占用过多内存
                for i in range(0, len(file_paths), batch_size_for_processing):
                    if self.should_stop:
                        return

                    # 获取当前批次的文件
                    current_batch_files = file_paths[i:i + batch_size_for_processing]

                    # 提交当前批次的验证任务
                    future_to_path = {
                        executor.submit(validate_image_fast, path): path
                        for path in current_batch_files
                    }

                    # 处理当前批次的完成任务
                    for future in as_completed(future_to_path):
                        if self.should_stop:
                            # 取消所有未完成的任务
                            for f in future_to_path:
                                f.cancel()
                            return

                        path = future_to_path[future]

                        try:
                            is_valid, should_delete, error_msg = future.result()
                            processed_count += 1

                            if should_delete:
                                # 记录需要删除的文件
                                corrupted_files.append(path)
                                self._remove_corrupted_files(path)
                            elif is_valid:
                                valid_images.append(path)
                                current_batch.append(path)

                            # 更新进度
                            status_text = f"智能验证中... ({processed_count}/{total_files})"
                            if corrupted_files:
                                status_text += f" | 已清理 {len(corrupted_files)} 个损坏文件"
                            if self.stats['thread_adjustments'] > 0:
                                status_text += f" | 已调整并发度 {self.stats['thread_adjustments']} 次"

                            self.progress_updated.emit(processed_count, total_files, status_text)

                            # 检查是否需要发射批次
                            batch_threshold = self.initial_batch_size if len(valid_images) <= self.initial_batch_size else self.batch_size

                            if len(current_batch) >= batch_threshold:
                                # 发送批次数据
                                self.batch_loaded.emit(current_batch.copy(), len(valid_images), total_files)
                                current_batch.clear()

                            # 适当的处理间隔，给系统喘息时间
                            if processed_count % 50 == 0:
                                time.sleep(0.01)  # 10ms间隔

                        except Exception as e:
                            self.stats['errors'].append(f"{path}: {str(e)}")
                            processed_count += 1

                    # 批次间的短暂休息，让系统缓冲
                    if not self.should_stop:
                        time.sleep(0.05)  # 50ms批次间隔

            # 发送剩余批次
            if current_batch and not self.should_stop:
                self.batch_loaded.emit(current_batch.copy(), len(valid_images), total_files)

            if not self.should_stop:
                # 最终排序
                natural_sort(valid_images, key=lambda x: x.lower())

                # 完成信号
                final_status = f"✅ 多线程加载完成！共 {len(valid_images)} 张图片"
                if corrupted_files:
                    final_status += f"，已清理 {len(corrupted_files)} 个损坏文件"
                if self.stats['errors']:
                    final_status += f"，{len(self.stats['errors'])} 个文件处理异常"

                self.progress_updated.emit(len(valid_images), total_files, final_status)
                self.loading_completed.emit(valid_images, len(corrupted_files))

        except Exception as e:
            error_msg = f"多线程加载图片时发生错误: {str(e)}"
            self.error_occurred.emit(error_msg)

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

    def __init__(self, main_window, use_multithreading=True, performance_mode="balanced"):
        self.main_window = main_window
        self.background_loader = None
        self.all_images = []
        self.initial_batch_loaded = False
        self.use_multithreading = use_multithreading
        self.performance_mode = performance_mode  # "conservative", "balanced", "aggressive"

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

        # 根据配置选择加载器
        try:
            if self.use_multithreading:
                # 使用智能多线程加载器
                self.background_loader = MultiThreadImageLoader(
                    folder_path,
                    initial_batch_size,
                    performance_mode=self.performance_mode
                )
                if hasattr(self.main_window, 'status'):
                    mode_name = {
                        "conservative": "保守模式",
                        "balanced": "平衡模式",
                        "aggressive": "激进模式"
                    }.get(self.performance_mode, "平衡模式")
                    self.main_window.status(f"使用智能多线程加载器 ({mode_name})...")
            else:
                # 使用原有的单线程加载器作为备用
                self.background_loader = BackgroundImageLoader(folder_path, initial_batch_size)
                if hasattr(self.main_window, 'status'):
                    self.main_window.status("使用单线程加载器...")
        except Exception as e:
            # 如果多线程加载器创建失败，回退到单线程版本
            print(f"[WARNING] 多线程加载器初始化失败，回退到单线程版本: {e}")
            self.background_loader = BackgroundImageLoader(folder_path, initial_batch_size)
            if hasattr(self.main_window, 'status'):
                self.main_window.status("回退到单线程加载器...")

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

        # 写回目录图片数量统计，供下次启动提示使用
        try:
            if hasattr(self.main_window, 'settings') and self.main_window.settings:
                self.main_window.settings[SETTING_LAST_DIR_IMAGE_COUNT] = len(all_images)
                self.main_window.settings.save()
        except Exception as e:
            print(f"[WARNING] 写入上次目录图片数量失败: {e}")

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
