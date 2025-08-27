# -*- coding: utf-8 -*-
"""
优化的Canvas渲染器
实现分层渲染、脏区域更新和渲染缓存等性能优化
"""

import time
from typing import List, Set, Optional, Tuple
from collections import defaultdict

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *


class RenderLayer:
    """渲染层定义"""
    BACKGROUND = 0      # 背景图像层
    SHAPES_BACKGROUND = 1  # 背景标注形状层
    SHAPES_FOREGROUND = 2  # 前景标注形状层
    CURRENT_SHAPE = 3   # 当前绘制形状层
    UI_OVERLAY = 4      # UI覆盖层（十字线等）
    
    LAYER_NAMES = {
        BACKGROUND: "背景层",
        SHAPES_BACKGROUND: "背景标注层", 
        SHAPES_FOREGROUND: "前景标注层",
        CURRENT_SHAPE: "当前绘制层",
        UI_OVERLAY: "UI覆盖层"
    }


class DirtyRegion:
    """脏区域管理"""
    
    def __init__(self):
        self.regions: List[QRect] = []
        self.full_update = False
        
    def add_region(self, rect: QRect):
        """添加需要更新的区域"""
        if self.full_update:
            return
            
        if not rect.isValid():
            return
            
        # 合并重叠的区域
        merged = False
        for i, existing in enumerate(self.regions):
            if rect.intersects(existing):
                self.regions[i] = existing.united(rect)
                merged = True
                break
                
        if not merged:
            self.regions.append(rect)
            
        # 如果区域过多，标记为全量更新
        if len(self.regions) > 10:
            self.mark_full_update()
            
    def mark_full_update(self):
        """标记为全量更新"""
        self.full_update = True
        self.regions.clear()
        
    def get_update_region(self, canvas_size: QSize) -> QRect:
        """获取需要更新的区域"""
        if self.full_update:
            return QRect(0, 0, canvas_size.width(), canvas_size.height())
            
        if not self.regions:
            return QRect()
            
        # 合并所有区域
        united = self.regions[0]
        for region in self.regions[1:]:
            united = united.united(region)
            
        return united
        
    def clear(self):
        """清空脏区域"""
        self.regions.clear()
        self.full_update = False
        
    def is_empty(self) -> bool:
        """检查是否有需要更新的区域"""
        return not self.full_update and not self.regions


class LayerCache:
    """渲染层缓存"""
    
    def __init__(self, max_cache_size: int = 5):
        self.max_cache_size = max_cache_size
        self.caches = {}  # layer_id -> QPixmap
        self.cache_keys = {}  # layer_id -> cache_key
        self.access_times = {}  # layer_id -> last_access_time
        
    def get_cache(self, layer_id: int, cache_key: str) -> Optional[QPixmap]:
        """获取层缓存"""
        if layer_id not in self.caches:
            return None
            
        if self.cache_keys.get(layer_id) != cache_key:
            # 缓存键不匹配，删除旧缓存
            self.invalidate_layer(layer_id)
            return None
            
        # 更新访问时间
        self.access_times[layer_id] = time.time()
        return self.caches[layer_id].copy()
        
    def set_cache(self, layer_id: int, cache_key: str, pixmap: QPixmap):
        """设置层缓存"""
        # 清理旧缓存
        self._cleanup_cache()
        
        self.caches[layer_id] = pixmap.copy()
        self.cache_keys[layer_id] = cache_key
        self.access_times[layer_id] = time.time()
        
    def invalidate_layer(self, layer_id: int):
        """使指定层缓存失效"""
        if layer_id in self.caches:
            del self.caches[layer_id]
        if layer_id in self.cache_keys:
            del self.cache_keys[layer_id]
        if layer_id in self.access_times:
            del self.access_times[layer_id]
            
    def invalidate_all(self):
        """使所有缓存失效"""
        self.caches.clear()
        self.cache_keys.clear()
        self.access_times.clear()
        
    def _cleanup_cache(self):
        """清理过期的缓存"""
        if len(self.caches) < self.max_cache_size:
            return
            
        # 找到最久未访问的层
        if self.access_times:
            oldest_layer = min(self.access_times.items(), key=lambda x: x[1])[0]
            self.invalidate_layer(oldest_layer)


class OptimizedCanvasRenderer:
    """
    优化的Canvas渲染器
    
    功能特性：
    - 分层渲染架构
    - 脏区域更新
    - 渲染缓存
    - 性能监控
    """
    
    def __init__(self, canvas):
        self.canvas = canvas
        
        # 脏区域管理
        self.dirty_regions = defaultdict(DirtyRegion)
        
        # 层缓存管理
        self.layer_cache = LayerCache()
        
        # 渲染统计
        self.render_stats = {
            'total_renders': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'layer_renders': defaultdict(int),
            'avg_render_time': 0.0,
            'last_render_time': 0.0
        }
        
        # 渲染选项
        self.enable_caching = True
        self.enable_dirty_regions = True
        self.enable_antialiasing = True
        self.enable_performance_monitoring = True
        
        print("[渲染器] 优化Canvas渲染器初始化完成")
        
    def mark_layer_dirty(self, layer_id: int, region: QRect = None):
        """标记层为脏状态"""
        if not self.enable_dirty_regions:
            return
            
        if region is None or not region.isValid():
            self.dirty_regions[layer_id].mark_full_update()
        else:
            self.dirty_regions[layer_id].add_region(region)
            
        # 使缓存失效
        if self.enable_caching:
            self.layer_cache.invalidate_layer(layer_id)
            
    def mark_all_dirty(self):
        """标记所有层为脏状态"""
        for layer_id in range(5):  # 所有层
            self.mark_layer_dirty(layer_id)
            
    def render(self, painter: QPainter, event: QPaintEvent) -> bool:
        """
        执行优化渲染
        
        Args:
            painter: QPainter对象
            event: 绘制事件
            
        Returns:
            是否成功渲染
        """
        start_time = time.time()
        
        try:
            # 设置渲染质量
            if self.enable_antialiasing:
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.HighQualityAntialiasing)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # 设置变换
            painter.scale(self.canvas.scale, self.canvas.scale)
            painter.translate(self.canvas.offset_to_center())
            
            # 分层渲染
            self._render_background_layer(painter)
            self._render_shapes_background_layer(painter)
            self._render_shapes_foreground_layer(painter)
            self._render_current_shape_layer(painter)
            self._render_ui_overlay_layer(painter)
            
            # 更新统计信息
            self._update_render_stats(start_time)
            
            # 清空脏区域
            if self.enable_dirty_regions:
                for dirty_region in self.dirty_regions.values():
                    dirty_region.clear()
                    
            return True
            
        except Exception as e:
            print(f"[渲染错误] 渲染过程中出现错误: {e}")
            return False
            
    def _render_background_layer(self, painter: QPainter):
        """渲染背景层"""
        layer_id = RenderLayer.BACKGROUND
        
        if not self.canvas.pixmap:
            return
            
        # 生成缓存键
        cache_key = f"bg_{id(self.canvas.pixmap)}_{self.canvas.overlay_color}"
        
        # 尝试从缓存获取
        if self.enable_caching:
            cached_pixmap = self.layer_cache.get_cache(layer_id, cache_key)
            if cached_pixmap:
                painter.drawPixmap(0, 0, cached_pixmap)
                self.render_stats['cache_hits'] += 1
                return
                
        # 渲染背景
        temp = self.canvas.pixmap
        if self.canvas.overlay_color:
            temp = QPixmap(self.canvas.pixmap)
            temp_painter = QPainter(temp)
            temp_painter.setCompositionMode(temp_painter.CompositionMode_Overlay)
            temp_painter.fillRect(temp.rect(), self.canvas.overlay_color)
            temp_painter.end()
            
        painter.drawPixmap(0, 0, temp)
        
        # 缓存结果
        if self.enable_caching and temp:
            self.layer_cache.set_cache(layer_id, cache_key, temp)
            
        self.render_stats['cache_misses'] += 1
        self.render_stats['layer_renders'][layer_id] += 1
        
    def _render_shapes_background_layer(self, painter: QPainter):
        """渲染背景标注形状层"""
        layer_id = RenderLayer.SHAPES_BACKGROUND
        
        if not self.canvas.shapes:
            return
            
        # 只渲染非选中的背景形状
        background_shapes = [
            shape for shape in self.canvas.shapes
            if not shape.selected and shape != self.canvas.h_shape
            and (not self.canvas._hide_background) and self.canvas.isVisible(shape)
        ]
        
        if not background_shapes:
            return
            
        # 设置形状渲染参数
        from libs.shape import Shape
        Shape.scale = self.canvas.scale
        Shape.label_font_size = self.canvas.label_font_size
        
        # 渲染背景形状
        for shape in background_shapes:
            shape.fill = False  # 背景形状不填充
            shape.paint(painter)
            
        self.render_stats['layer_renders'][layer_id] += 1
        
    def _render_shapes_foreground_layer(self, painter: QPainter):
        """渲染前景标注形状层"""
        layer_id = RenderLayer.SHAPES_FOREGROUND
        
        if not self.canvas.shapes:
            return
            
        # 只渲染选中的和高亮的形状
        foreground_shapes = [
            shape for shape in self.canvas.shapes
            if (shape.selected or shape == self.canvas.h_shape)
            and self.canvas.isVisible(shape)
        ]
        
        if not foreground_shapes:
            return
            
        # 设置形状渲染参数
        from libs.shape import Shape
        Shape.scale = self.canvas.scale
        Shape.label_font_size = self.canvas.label_font_size
        
        # 渲染前景形状
        for shape in foreground_shapes:
            shape.fill = True  # 前景形状填充
            shape.paint(painter)
            
        self.render_stats['layer_renders'][layer_id] += 1
        
    def _render_current_shape_layer(self, painter: QPainter):
        """渲染当前绘制形状层"""
        layer_id = RenderLayer.CURRENT_SHAPE
        
        # 渲染当前绘制的形状
        if self.canvas.current:
            self.canvas.current.paint(painter)
            self.canvas.line.paint(painter)
            
        # 渲染复制的形状
        if self.canvas.selected_shape_copy:
            self.canvas.selected_shape_copy.paint(painter)
            
        # 渲染绘制矩形
        if (self.canvas.current is not None and 
            hasattr(self.canvas, 'line') and len(self.canvas.line) == 2):
            
            left_top = self.canvas.line[0]
            right_bottom = self.canvas.line[1]
            rect_width = right_bottom.x() - left_top.x()
            rect_height = right_bottom.y() - left_top.y()
            
            painter.setPen(self.canvas.drawing_rect_color)
            brush = QBrush(Qt.BDiagPattern)
            painter.setBrush(brush)
            painter.drawRect(int(left_top.x()), int(left_top.y()), 
                           int(rect_width), int(rect_height))
            
        self.render_stats['layer_renders'][layer_id] += 1
        
    def _render_ui_overlay_layer(self, painter: QPainter):
        """渲染UI覆盖层"""
        layer_id = RenderLayer.UI_OVERLAY
        
        # 渲染十字线
        if (self.canvas.drawing() and not self.canvas.prev_point.isNull() 
            and not self.canvas.out_of_pixmap(self.canvas.prev_point) and self.canvas.pixmap):
            
            painter.setPen(QColor(0, 0, 0))
            painter.drawLine(int(self.canvas.prev_point.x()), 0, 
                           int(self.canvas.prev_point.x()), int(self.canvas.pixmap.height()))
            painter.drawLine(0, int(self.canvas.prev_point.y()), 
                           int(self.canvas.pixmap.width()), int(self.canvas.prev_point.y()))
            
        self.render_stats['layer_renders'][layer_id] += 1
        
    def _update_render_stats(self, start_time: float):
        """更新渲染统计信息"""
        if not self.enable_performance_monitoring:
            return
            
        render_time = time.time() - start_time
        self.render_stats['total_renders'] += 1
        self.render_stats['last_render_time'] = render_time
        
        # 计算平均渲染时间（使用滑动平均）
        alpha = 0.1  # 平滑因子
        if self.render_stats['avg_render_time'] == 0:
            self.render_stats['avg_render_time'] = render_time
        else:
            self.render_stats['avg_render_time'] = (
                alpha * render_time + 
                (1 - alpha) * self.render_stats['avg_render_time']
            )
            
    def get_performance_stats(self) -> dict:
        """获取性能统计信息"""
        stats = self.render_stats.copy()
        
        # 计算缓存命中率
        total_cache_requests = stats['cache_hits'] + stats['cache_misses']
        if total_cache_requests > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / total_cache_requests
        else:
            stats['cache_hit_rate'] = 0.0
            
        # 添加层渲染统计
        stats['layer_render_counts'] = dict(self.render_stats['layer_renders'])
        
        return stats
        
    def reset_stats(self):
        """重置统计信息"""
        self.render_stats = {
            'total_renders': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'layer_renders': defaultdict(int),
            'avg_render_time': 0.0,
            'last_render_time': 0.0
        }
        
    def set_render_options(self, **options):
        """设置渲染选项"""
        for key, value in options.items():
            if hasattr(self, key):
                setattr(self, key, value)
                print(f"[渲染器] 设置渲染选项 {key} = {value}")
                
    def invalidate_cache(self):
        """使所有缓存失效"""
        if self.enable_caching:
            self.layer_cache.invalidate_all()
            self.mark_all_dirty()
            print("[渲染器] 已清空所有渲染缓存")