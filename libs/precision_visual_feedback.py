# -*- coding: utf-8 -*-
"""
精确交互视觉反馈渲染器

主要功能：
1. 吸附指示器渲染
2. 辅助线绘制
3. 测量信息显示
4. 交互模式指示
5. 性能优化的渲染管道
"""

import math
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QPainterPath
from PyQt5.QtWidgets import QWidget

from .logger_config import get_logger

logger = get_logger(__name__)


class VisualStyle:
    """视觉样式配置"""
    def __init__(self):
        # 吸附指示器样式
        self.snap_indicator_size = 8
        self.snap_indicator_colors = {
            'edge': QColor(0, 150, 255, 180),      # 蓝色
            'corner': QColor(255, 100, 0, 180),    # 橙色
            'center': QColor(0, 255, 100, 180),    # 绿色
            'grid': QColor(200, 200, 200, 120),    # 灰色
            'existing_shape': QColor(255, 0, 150, 180)  # 粉色
        }
        
        # 辅助线样式
        self.guide_line_color = QColor(100, 100, 255, 100)
        self.guide_line_width = 1
        self.alignment_line_color = QColor(0, 150, 255, 150)
        self.alignment_line_width = 2
        
        # 测量信息样式
        self.measurement_font = QFont("Arial", 10)
        self.measurement_bg_color = QColor(0, 0, 0, 180)
        self.measurement_text_color = QColor(255, 255, 255)
        self.measurement_padding = 4
        
        # 模式指示器样式
        self.mode_indicator_size = 100
        self.mode_indicator_position = (10, 10)  # 左上角
        self.mode_colors = {
            'normal': QColor(100, 100, 100, 100),
            'precision': QColor(255, 100, 0, 150),
            'snap': QColor(0, 150, 255, 150),
            'guide': QColor(100, 255, 0, 150)
        }
        
        # 动画设置
        self.animation_duration = 300  # ms
        self.fade_in_duration = 200
        self.fade_out_duration = 400


class AnimationState:
    """动画状态"""
    def __init__(self):
        self.snap_indicator_alpha = 0.0
        self.guide_lines_alpha = 0.0
        self.measurement_alpha = 0.0
        self.mode_indicator_alpha = 0.0
        
        # 动画时间戳
        self.last_snap_time = 0
        self.last_guide_time = 0
        self.last_measurement_time = 0
        self.last_mode_change_time = 0


class PrecisionVisualFeedback:
    """精确交互视觉反馈渲染器"""
    
    def __init__(self):
        self.style = VisualStyle()
        self.animation_state = AnimationState()
        
        # 渲染缓存
        self.render_cache = {}
        self.cache_valid = False
        
        # 性能控制
        self.max_render_fps = 60
        self.last_render_time = 0
        self.render_interval = 1.0 / self.max_render_fps
        
        # 可见性控制
        self.show_snap_indicators = True
        self.show_guide_lines = True
        self.show_measurement_info = True
        self.show_mode_indicator = True

    def render(self, painter: QPainter, canvas_rect: QRectF, feedback_data: Dict[str, Any]):
        """主渲染方法"""
        try:
            import time
            current_time = time.time()
            
            # 性能控制：限制渲染频率
            if current_time - self.last_render_time < self.render_interval:
                return
            
            self.last_render_time = current_time
            
            # 更新动画状态
            self._update_animations(current_time)
            
            # 保存画家状态
            painter.save()
            
            try:
                # 渲染各种视觉元素
                if self.show_guide_lines and feedback_data.get('guide_lines'):
                    self._render_guide_lines(painter, canvas_rect, feedback_data['guide_lines'])
                
                if self.show_snap_indicators and feedback_data.get('snap_indicators'):
                    self._render_snap_indicators(painter, feedback_data['snap_indicators'])
                
                if self.show_measurement_info and feedback_data.get('measurement_overlay'):
                    self._render_measurement_overlay(painter, canvas_rect, feedback_data['measurement_overlay'])
                
                if self.show_mode_indicator and feedback_data.get('mode_indicator'):
                    self._render_mode_indicator(painter, canvas_rect, feedback_data['mode_indicator'])
                
            finally:
                # 恢复画家状态
                painter.restore()
                
        except Exception as e:
            logger.error(f"渲染视觉反馈失败: {str(e)}")

    def _update_animations(self, current_time: float):
        """更新动画状态"""
        try:
            # 吸附指示器淡入淡出
            if hasattr(self, '_snap_target_visible') and self._snap_target_visible:
                self.animation_state.snap_indicator_alpha = min(1.0, 
                    self.animation_state.snap_indicator_alpha + 0.1)
            else:
                self.animation_state.snap_indicator_alpha = max(0.0, 
                    self.animation_state.snap_indicator_alpha - 0.05)
            
            # 辅助线淡入淡出
            if hasattr(self, '_guide_lines_visible') and self._guide_lines_visible:
                self.animation_state.guide_lines_alpha = min(1.0, 
                    self.animation_state.guide_lines_alpha + 0.08)
            else:
                self.animation_state.guide_lines_alpha = max(0.0, 
                    self.animation_state.guide_lines_alpha - 0.05)
                    
        except Exception as e:
            logger.error(f"更新动画状态失败: {str(e)}")

    def _render_snap_indicators(self, painter: QPainter, snap_indicators: List[Dict[str, Any]]):
        """渲染吸附指示器"""
        try:
            if self.animation_state.snap_indicator_alpha <= 0:
                return
            
            for indicator in snap_indicators:
                position = indicator.get('position')
                indicator_type = indicator.get('type', 'edge')
                confidence = indicator.get('confidence', 1.0)
                
                if not position:
                    continue
                
                # 获取颜色
                color = self.style.snap_indicator_colors.get(indicator_type, 
                                                           self.style.snap_indicator_colors['edge'])
                
                # 应用透明度和置信度
                alpha = int(color.alpha() * self.animation_state.snap_indicator_alpha * confidence)
                color.setAlpha(alpha)
                
                # 根据类型绘制不同的指示器
                self._draw_snap_indicator(painter, position, indicator_type, color)
                
        except Exception as e:
            logger.error(f"渲染吸附指示器失败: {str(e)}")

    def _draw_snap_indicator(self, painter: QPainter, position: QPointF, 
                           indicator_type: str, color: QColor):
        """绘制单个吸附指示器"""
        try:
            size = self.style.snap_indicator_size
            half_size = size / 2
            
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            
            if indicator_type == 'corner':
                # 角点：小正方形
                rect = QRectF(position.x() - half_size, position.y() - half_size, size, size)
                painter.drawRect(rect)
                
            elif indicator_type == 'edge':
                # 边缘：菱形
                path = QPainterPath()
                path.moveTo(position.x(), position.y() - half_size)
                path.lineTo(position.x() + half_size, position.y())
                path.lineTo(position.x(), position.y() + half_size)
                path.lineTo(position.x() - half_size, position.y())
                path.closeSubpath()
                painter.drawPath(path)
                
            elif indicator_type == 'center':
                # 中心：圆形
                painter.drawEllipse(position, half_size, half_size)
                
            elif indicator_type == 'grid':
                # 网格：十字
                painter.drawLine(position.x() - half_size, position.y(), 
                               position.x() + half_size, position.y())
                painter.drawLine(position.x(), position.y() - half_size, 
                               position.x(), position.y() + half_size)
                
            elif indicator_type == 'existing_shape':
                # 现有形状：三角形
                path = QPainterPath()
                path.moveTo(position.x(), position.y() - half_size)
                path.lineTo(position.x() - half_size, position.y() + half_size)
                path.lineTo(position.x() + half_size, position.y() + half_size)
                path.closeSubpath()
                painter.drawPath(path)
                
        except Exception as e:
            logger.error(f"绘制吸附指示器失败: {str(e)}")

    def _render_guide_lines(self, painter: QPainter, canvas_rect: QRectF, 
                          guide_lines: List[Dict[str, Any]]):
        """渲染辅助线"""
        try:
            if self.animation_state.guide_lines_alpha <= 0:
                return
            
            for guide_line in guide_lines:
                line_type = guide_line.get('type')
                position = guide_line.get('position')
                style = guide_line.get('style', 'dashed')
                color_name = guide_line.get('color', 'default')
                
                if line_type not in ['horizontal', 'vertical'] or position is None:
                    continue
                
                # 确定颜色
                if color_name == 'blue':
                    color = self.style.alignment_line_color
                    width = self.style.alignment_line_width
                else:
                    color = self.style.guide_line_color
                    width = self.style.guide_line_width
                
                # 应用透明度
                alpha = int(color.alpha() * self.animation_state.guide_lines_alpha)
                color.setAlpha(alpha)
                
                # 设置画笔样式
                pen = QPen(color, width)
                if style == 'dashed':
                    pen.setStyle(Qt.DashLine)
                else:
                    pen.setStyle(Qt.SolidLine)
                
                painter.setPen(pen)
                
                # 绘制线条
                if line_type == 'horizontal':
                    painter.drawLine(canvas_rect.left(), position, 
                                   canvas_rect.right(), position)
                elif line_type == 'vertical':
                    painter.drawLine(position, canvas_rect.top(), 
                                   position, canvas_rect.bottom())
                    
        except Exception as e:
            logger.error(f"渲染辅助线失败: {str(e)}")

    def _render_measurement_overlay(self, painter: QPainter, canvas_rect: QRectF, 
                                  measurement_data: Dict[str, Any]):
        """渲染测量信息覆盖层"""
        try:
            if not measurement_data:
                return
            
            position = measurement_data.get('position')
            mode = measurement_data.get('mode', 'normal')
            snap_target = measurement_data.get('snap_target')
            drawing_info = measurement_data.get('drawing_info')
            
            # 构建显示文本
            text_lines = []
            
            if position:
                text_lines.append(f"位置: ({position[0]:.1f}, {position[1]:.1f})")
            
            if mode != 'normal':
                text_lines.append(f"模式: {mode}")
            
            if snap_target:
                snap_type = snap_target.get('type', 'unknown')
                distance = snap_target.get('distance', 0)
                text_lines.append(f"吸附: {snap_type} (距离: {distance:.1f})")
            
            if drawing_info:
                width = drawing_info.get('width', 0)
                height = drawing_info.get('height', 0)
                distance = drawing_info.get('distance', 0)
                angle = drawing_info.get('angle', 0)
                text_lines.append(f"尺寸: {width:.1f} × {height:.1f}")
                text_lines.append(f"距离: {distance:.1f}, 角度: {angle:.1f}°")
            
            if not text_lines:
                return
            
            # 渲染文本背景和内容
            self._draw_measurement_text(painter, canvas_rect, text_lines)
            
        except Exception as e:
            logger.error(f"渲染测量覆盖层失败: {str(e)}")

    def _draw_measurement_text(self, painter: QPainter, canvas_rect: QRectF, 
                             text_lines: List[str]):
        """绘制测量文本"""
        try:
            if not text_lines:
                return
            
            painter.setFont(self.style.measurement_font)
            font_metrics = QFontMetrics(self.style.measurement_font)
            
            # 计算文本尺寸
            max_width = 0
            total_height = 0
            line_height = font_metrics.height()
            
            for line in text_lines:
                line_width = font_metrics.width(line)
                max_width = max(max_width, line_width)
                total_height += line_height
            
            # 添加内边距
            padding = self.style.measurement_padding
            bg_width = max_width + 2 * padding
            bg_height = total_height + 2 * padding
            
            # 确定位置（右下角）
            x = canvas_rect.right() - bg_width - 10
            y = canvas_rect.bottom() - bg_height - 10
            
            # 绘制背景
            bg_rect = QRectF(x, y, bg_width, bg_height)
            painter.fillRect(bg_rect, self.style.measurement_bg_color)
            
            # 绘制文本
            painter.setPen(self.style.measurement_text_color)
            text_y = y + padding + font_metrics.ascent()
            
            for line in text_lines:
                painter.drawText(x + padding, text_y, line)
                text_y += line_height
                
        except Exception as e:
            logger.error(f"绘制测量文本失败: {str(e)}")

    def _render_mode_indicator(self, painter: QPainter, canvas_rect: QRectF, mode: str):
        """渲染模式指示器"""
        try:
            if mode == 'normal':
                return  # 普通模式不显示指示器
            
            color = self.style.mode_colors.get(mode, self.style.mode_colors['normal'])
            
            # 指示器位置和大小
            indicator_size = 60
            x, y = self.style.mode_indicator_position
            
            # 确保指示器在画布范围内
            if x + indicator_size > canvas_rect.right():
                x = canvas_rect.right() - indicator_size - 10
            if y + indicator_size > canvas_rect.bottom():
                y = canvas_rect.bottom() - indicator_size - 10
            
            # 绘制圆形指示器
            center = QPointF(x + indicator_size / 2, y + indicator_size / 2)
            radius = indicator_size / 2
            
            painter.setPen(QPen(color, 3))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(center, radius, radius)
            
            # 绘制模式文本
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            
            mode_text = mode.upper()
            font_metrics = QFontMetrics(painter.font())
            text_width = font_metrics.width(mode_text)
            text_height = font_metrics.height()
            
            text_x = center.x() - text_width / 2
            text_y = center.y() + text_height / 4
            
            painter.drawText(text_x, text_y, mode_text)
            
        except Exception as e:
            logger.error(f"渲染模式指示器失败: {str(e)}")

    def set_snap_target_visible(self, visible: bool):
        """设置吸附目标可见性"""
        self._snap_target_visible = visible

    def set_guide_lines_visible(self, visible: bool):
        """设置辅助线可见性"""
        self._guide_lines_visible = visible

    def configure_style(self, **kwargs):
        """配置视觉样式"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.style, key):
                    setattr(self.style, key, value)
                    logger.debug(f"设置样式: {key} = {value}")
            
            # 标记缓存无效
            self.cache_valid = False
            
        except Exception as e:
            logger.error(f"配置样式失败: {str(e)}")

    def set_visibility(self, snap_indicators: bool = None, guide_lines: bool = None, 
                      measurement_info: bool = None, mode_indicator: bool = None):
        """设置各种元素的可见性"""
        try:
            if snap_indicators is not None:
                self.show_snap_indicators = snap_indicators
            if guide_lines is not None:
                self.show_guide_lines = guide_lines
            if measurement_info is not None:
                self.show_measurement_info = measurement_info
            if mode_indicator is not None:
                self.show_mode_indicator = mode_indicator
                
        except Exception as e:
            logger.error(f"设置可见性失败: {str(e)}")

    def get_render_stats(self) -> Dict[str, Any]:
        """获取渲染统计信息"""
        try:
            return {
                'render_fps': 1.0 / self.render_interval if self.render_interval > 0 else 0,
                'last_render_time': self.last_render_time,
                'cache_valid': self.cache_valid,
                'animation_state': {
                    'snap_alpha': self.animation_state.snap_indicator_alpha,
                    'guide_alpha': self.animation_state.guide_lines_alpha,
                    'measurement_alpha': self.animation_state.measurement_alpha,
                    'mode_alpha': self.animation_state.mode_indicator_alpha
                },
                'visibility': {
                    'snap_indicators': self.show_snap_indicators,
                    'guide_lines': self.show_guide_lines,
                    'measurement_info': self.show_measurement_info,
                    'mode_indicator': self.show_mode_indicator
                }
            }
        except Exception as e:
            logger.error(f"获取渲染统计失败: {str(e)}")
            return {}

    def reset_animations(self):
        """重置动画状态"""
        try:
            self.animation_state = AnimationState()
            self.cache_valid = False
            logger.debug("动画状态已重置")
        except Exception as e:
            logger.error(f"重置动画状态失败: {str(e)}")


class PrecisionFeedbackIntegrator:
    """精确反馈集成器 - 将精确交互系统与视觉反馈连接"""
    
    def __init__(self, precision_system, visual_feedback):
        self.precision_system = precision_system
        self.visual_feedback = visual_feedback
        
        # 连接信号
        if precision_system:
            precision_system.snap_target_found.connect(self._on_snap_target_found)
            precision_system.precision_mode_changed.connect(self._on_mode_changed)
            precision_system.measurement_updated.connect(self._on_measurement_updated)
    
    def _on_snap_target_found(self, snap_candidate):
        """处理找到的吸附目标"""
        try:
            self.visual_feedback.set_snap_target_visible(True)
        except Exception as e:
            logger.error(f"处理吸附目标失败: {str(e)}")
    
    def _on_mode_changed(self, new_mode):
        """处理模式变化"""
        try:
            # 根据模式调整视觉反馈
            if new_mode == 'precision':
                self.visual_feedback.configure_style(
                    snap_indicator_size=6,  # 更小的指示器
                    guide_line_width=1
                )
            elif new_mode == 'snap':
                self.visual_feedback.configure_style(
                    snap_indicator_size=12,  # 更大的指示器
                    guide_line_width=2
                )
            
            logger.debug(f"视觉反馈已适应模式: {new_mode}")
            
        except Exception as e:
            logger.error(f"处理模式变化失败: {str(e)}")
    
    def _on_measurement_updated(self, measurement_info):
        """处理测量信息更新"""
        try:
            # 可以在这里触发测量信息显示的动画
            pass
        except Exception as e:
            logger.error(f"处理测量信息更新失败: {str(e)}")
    
    def render_all_feedback(self, painter: QPainter, canvas_rect: QRectF):
        """渲染所有视觉反馈"""
        try:
            if not self.precision_system:
                return
            
            # 获取反馈数据
            feedback_data = self.precision_system.get_visual_feedback_data()
            
            # 渲染视觉反馈
            self.visual_feedback.render(painter, canvas_rect, feedback_data)
            
        except Exception as e:
            logger.error(f"渲染所有反馈失败: {str(e)}")