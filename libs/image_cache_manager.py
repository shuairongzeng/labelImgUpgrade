# -*- coding: utf-8 -*-
"""
图像缓存管理器
提供智能的图像预加载和缓存功能，优化图片浏览性能
"""

import os
import time
import threading
from collections import OrderedDict
from typing import Optional, Dict, List, Tuple, Any
import weakref

try:
    from PyQt5.QtGui import QPixmap, QImage
    from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker
except ImportError:
    from PyQt4.QtGui import QPixmap, QImage
    from PyQt4.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker


class ImageCacheEntry:
    """图像缓存条目"""
    
    def __init__(self, image: QImage, file_path: str):
        self.image = image
        self.file_path = file_path
        self.access_time = time.time()
        self.access_count = 1
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
    def update_access(self):
        """更新访问时间和计数"""
        self.access_time = time.time()
        self.access_count += 1


class ImagePreloader(QThread):
    """图像预加载线程"""
    
    image_loaded = pyqtSignal(str, QImage)  # 图像路径, 图像对象
    preload_progress = pyqtSignal(int, int)  # 当前进度, 总数
    
    def __init__(self, cache_manager):
        super().__init__()
        self.cache_manager = weakref.ref(cache_manager)
        self.preload_queue = []
        self.mutex = QMutex()
        self.running = True
        
    def add_preload_task(self, file_paths: List[str], priority: int = 1):
        """
        添加预加载任务
        
        Args:
            file_paths: 要预加载的图像文件路径列表
            priority: 优先级 (1=高, 2=中, 3=低)
        """
        with QMutexLocker(self.mutex):
            for path in file_paths:
                if path and os.path.exists(path):
                    self.preload_queue.append((priority, path))
            # 按优先级排序
            self.preload_queue.sort(key=lambda x: x[0])
            
    def clear_queue(self):
        """清空预加载队列"""
        with QMutexLocker(self.mutex):
            self.preload_queue.clear()
            
    def stop(self):
        """停止预加载线程"""
        self.running = False
        self.quit()
        self.wait()
        
    def run(self):
        """运行预加载任务"""
        while self.running:
            task = None
            
            with QMutexLocker(self.mutex):
                if self.preload_queue:
                    task = self.preload_queue.pop(0)
                    
            if task:
                priority, file_path = task
                cache_manager = self.cache_manager()
                
                if cache_manager and not cache_manager.is_cached(file_path):
                    try:
                        image = QImage(file_path)
                        if not image.isNull():
                            self.image_loaded.emit(file_path, image)
                            
                        # 发送进度信号
                        remaining = len(self.preload_queue)
                        total = remaining + 1
                        self.preload_progress.emit(1, total)
                        
                    except Exception as e:
                        print(f"[预加载错误] 无法加载图像 {file_path}: {e}")
                        
            else:
                # 没有任务时休眠
                self.msleep(100)


class ImageCacheManager(QObject):
    """
    智能图像缓存管理器
    
    功能特性:
    - LRU缓存策略
    - 智能预加载
    - 内存使用监控
    - 多线程安全
    """
    
    cache_updated = pyqtSignal(str)  # 缓存更新信号
    memory_warning = pyqtSignal(float)  # 内存警告信号 (使用率)
    
    def __init__(self, max_cache_size: int = 50, max_memory_mb: int = 512):
        super().__init__()
        
        # 配置参数
        self.max_cache_size = max_cache_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        # 缓存存储 (LRU)
        self.cache: OrderedDict[str, ImageCacheEntry] = OrderedDict()
        self.cache_mutex = QMutex()
        
        # 预加载器
        self.preloader = ImagePreloader(self)
        self.preloader.image_loaded.connect(self.on_image_preloaded)
        self.preloader.start()
        
        # 统计信息
        self.cache_hits = 0
        self.cache_misses = 0
        self.current_memory_usage = 0
        
        # 内存监控定时器
        self.memory_monitor = QTimer()
        self.memory_monitor.timeout.connect(self.check_memory_usage)
        self.memory_monitor.start(5000)  # 每5秒检查一次
        
    def get_image(self, file_path: str) -> Optional[QImage]:
        """
        获取图像，优先从缓存获取
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            QImage对象或None
        """
        if not file_path or not os.path.exists(file_path):
            return None
            
        with QMutexLocker(self.cache_mutex):
            # 检查缓存
            if file_path in self.cache:
                entry = self.cache[file_path]
                entry.update_access()
                # 移到末尾 (LRU)
                self.cache.move_to_end(file_path)
                self.cache_hits += 1
                return entry.image.copy()
                
        # 缓存未命中，直接加载
        self.cache_misses += 1
        return self.load_and_cache_image(file_path)
        
    def load_and_cache_image(self, file_path: str) -> Optional[QImage]:
        """
        加载图像并添加到缓存
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            QImage对象或None
        """
        try:
            image = QImage(file_path)
            if not image.isNull():
                self.add_to_cache(file_path, image)
                return image
        except Exception as e:
            print(f"[缓存管理器] 加载图像失败 {file_path}: {e}")
            
        return None
        
    def add_to_cache(self, file_path: str, image: QImage):
        """
        添加图像到缓存
        
        Args:
            file_path: 图像文件路径
            image: QImage对象
        """
        with QMutexLocker(self.cache_mutex):
            # 检查是否已存在
            if file_path in self.cache:
                self.cache.move_to_end(file_path)
                return
                
            # 创建缓存条目
            entry = ImageCacheEntry(image.copy(), file_path)
            
            # 检查内存使用
            image_size = self._estimate_image_memory(image)
            
            # 如果超过内存限制，清理缓存
            while (self.current_memory_usage + image_size > self.max_memory_bytes and 
                   len(self.cache) > 0):
                self._remove_oldest_entry()
                
            # 如果超过数量限制，清理缓存
            while len(self.cache) >= self.max_cache_size:
                self._remove_oldest_entry()
                
            # 添加到缓存
            self.cache[file_path] = entry
            self.current_memory_usage += image_size
            
            self.cache_updated.emit(file_path)
            
    def _remove_oldest_entry(self):
        """移除最旧的缓存条目"""
        if not self.cache:
            return
            
        # 获取最旧的条目 (LRU的第一个)
        oldest_path = next(iter(self.cache))
        oldest_entry = self.cache[oldest_path]
        
        # 估算释放的内存
        released_memory = self._estimate_image_memory(oldest_entry.image)
        self.current_memory_usage -= released_memory
        
        # 移除条目
        del self.cache[oldest_path]
        
    def _estimate_image_memory(self, image: QImage) -> int:
        """估算图像占用内存大小"""
        if image.isNull():
            return 0
        return image.width() * image.height() * (image.depth() // 8)
        
    def is_cached(self, file_path: str) -> bool:
        """检查图像是否在缓存中"""
        with QMutexLocker(self.cache_mutex):
            return file_path in self.cache
            
    def preload_adjacent_images(self, current_path: str, image_list: List[str], 
                              preload_count: int = 3):
        """
        预加载相邻图像
        
        Args:
            current_path: 当前图像路径
            image_list: 图像列表
            preload_count: 预加载数量 (前后各几张)
        """
        if current_path not in image_list:
            return
            
        current_idx = image_list.index(current_path)
        preload_paths = []
        
        # 后面的图像 (高优先级)
        for i in range(1, preload_count + 1):
            if current_idx + i < len(image_list):
                path = image_list[current_idx + i]
                if not self.is_cached(path):
                    preload_paths.append(path)
                    
        # 前面的图像 (中优先级)  
        for i in range(1, preload_count + 1):
            if current_idx - i >= 0:
                path = image_list[current_idx - i]
                if not self.is_cached(path):
                    preload_paths.append(path)
                    
        if preload_paths:
            # 高优先级给后面的图像，中优先级给前面的
            high_priority = preload_paths[:preload_count]
            mid_priority = preload_paths[preload_count:]
            
            self.preloader.add_preload_task(high_priority, priority=1)
            self.preloader.add_preload_task(mid_priority, priority=2)
            
    def on_image_preloaded(self, file_path: str, image: QImage):
        """处理预加载完成的图像"""
        self.add_to_cache(file_path, image)
        
    def check_memory_usage(self):
        """检查内存使用情况"""
        usage_ratio = self.current_memory_usage / self.max_memory_bytes
        
        if usage_ratio > 0.9:  # 超过90%发出警告
            self.memory_warning.emit(usage_ratio)
            
        # 如果超过限制，强制清理
        if usage_ratio > 1.0:
            self.cleanup_cache(target_ratio=0.7)
            
    def cleanup_cache(self, target_ratio: float = 0.5, auto: bool = False):
        """
        清理缓存到目标使用率
        
        Args:
            target_ratio: 目标内存使用率 (0.0-1.0)
            auto: 是否为自动清理（向后兼容参数）
        
        Returns:
            float: 释放的内存大小(MB)
        """
        target_memory = self.max_memory_bytes * target_ratio
        freed_memory = 0
        
        with QMutexLocker(self.cache_mutex):
            initial_memory = self.current_memory_usage
            while (self.current_memory_usage > target_memory and 
                   len(self.cache_times) > 0):
                oldest_key = min(self.cache_times.keys(), 
                               key=self.cache_times.get)
                if oldest_key in self.cache:
                    # 计算要释放的内存
                    if oldest_key in self.memory_usage:
                        freed_memory += self.memory_usage[oldest_key]
                    
                    del self.cache[oldest_key]
                    del self.cache_times[oldest_key]
                    if oldest_key in self.memory_usage:
                        self.current_memory_usage -= self.memory_usage[oldest_key]
                        del self.memory_usage[oldest_key]
        
        # 转换为MB返回
        return freed_memory / (1024 * 1024)
                
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) 
                   if (self.cache_hits + self.cache_misses) > 0 else 0)
        
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'memory_usage_mb': self.current_memory_usage / (1024 * 1024),
            'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
            'memory_usage_ratio': self.current_memory_usage / self.max_memory_bytes,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'preload_queue_size': len(self.preloader.preload_queue)
        }
        
    def clear_cache(self):
        """清空所有缓存"""
        with QMutexLocker(self.cache_mutex):
            self.cache.clear()
            self.current_memory_usage = 0
            
        self.preloader.clear_queue()
        
    def shutdown(self):
        """关闭缓存管理器"""
        self.memory_monitor.stop()
        self.preloader.stop()
        self.clear_cache()