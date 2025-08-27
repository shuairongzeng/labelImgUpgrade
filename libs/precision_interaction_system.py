# -*- coding: utf-8 -*-
"""
精确交互系统 - 优化标注框精度和交互响应

主要功能：
1. 高精度标注框绘制和编辑
2. 智能边缘检测和吸附
3. 亚像素级精度处理
4. 交互响应优化
5. 辅助标注工具
"""

import math
import time
from typing import Dict, List, Optional, Tuple, Any
from PyQt5.QtCore import QPointF, QRectF, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QPolygonF, QPainter, QPen, QBrush, QColor, QTransform
from PyQt5.QtWidgets import QApplication

from .logger_config import get_logger

logger = get_logger(__name__)


class InteractionMode:
    """交互模式"""
    NORMAL = "normal"
    PRECISION = "precision"
    SNAP = "snap"
    GUIDE = "guide"


class SnapTarget:
    """吸附目标"""
    EDGE = "edge"
    CORNER = "corner"
    CENTER = "center"
    GRID = "grid"
    EXISTING_SHAPE = "existing_shape"


class PrecisionSettings:
    """精度设置"""
    def __init__(self):
        # 基础设置
        self.snap_threshold = 10.0        # 吸附阈值（像素）
        self.precision_mode_threshold = 5.0  # 精度模式阈值
        self.subpixel_precision = True    # 启用亚像素精度
        self.edge_detection_enabled = True  # 启用边缘检测
        
        # 吸附设置
        self.snap_to_edges = True
        self.snap_to_corners = True
        self.snap_to_centers = True
        self.snap_to_grid = False
        self.snap_to_existing_shapes = True
        
        # 视觉反馈设置
        self.show_snap_indicators = True
        self.show_precision_guides = True
        self.show_measurement_info = True
        self.highlight_snap_targets = True
        
        # 性能设置
        self.max_snap_candidates = 20     # 最大吸附候选数
        self.update_frequency = 60        # 更新频率(FPS)
        self.enable_prediction = True     # 启用预测吸附


class SnapCandidate:
    """吸附候选"""
    def __init__(self, point: QPointF, target_type: str, distance: float, 
                 metadata: Dict[str, Any] = None):
        self.point = point
        self.target_type = target_type
        self.distance = distance
        self.metadata = metadata or {}
        self.confidence = 1.0 - (distance / 50.0)  # 基于距离的置信度


class InteractionState:
    """交互状态"""
    def __init__(self):
        self.is_drawing = False
        self.is_editing = False
        self.is_moving = False
        self.is_resizing = False
        self.current_mode = InteractionMode.NORMAL
        
        # 当前操作的形状信息
        self.active_shape = None
        self.selected_handle = None
        self.drag_start_point = None
        self.last_mouse_pos = None
        
        # 吸附状态
        self.current_snap_target = None
        self.snap_preview_point = None
        self.snap_candidates = []


class PrecisionInteractionSystem(QObject):
    """精确交互系统"""
    
    # 信号定义
    snap_target_found = pyqtSignal(object)    # 找到吸附目标
    precision_mode_changed = pyqtSignal(str)  # 精度模式改变
    measurement_updated = pyqtSignal(dict)    # 测量信息更新
    interaction_feedback = pyqtSignal(str)    # 交互反馈

    def __init__(self, canvas=None):
        super().__init__()
        
        self.canvas = canvas
        self.settings = PrecisionSettings()
        self.state = InteractionState()
        
        # 性能优化：缓存和计算限制
        self.snap_cache = {}
        self.last_update_time = 0
        self.update_interval = 1.0 / self.settings.update_frequency
        
        # 预测系统
        self.movement_history = []
        self.max_history_length = 10
        
        # 精度辅助工具
        self.grid_spacing = 10
        self.guide_lines = []
        self.measurement_info = {}
        
        # 定时器用于延迟更新
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._delayed_update)

    def set_canvas(self, canvas):
        """设置画布引用"""
        self.canvas = canvas

    def process_mouse_move(self, pos: QPointF, modifiers: int = 0) -> QPointF:
        """处理鼠标移动，返回调整后的位置"""
        try:
            current_time = time.time()
            
            # 性能控制：限制更新频率
            if current_time - self.last_update_time < self.update_interval:
                return pos
            
            self.last_update_time = current_time
            self.state.last_mouse_pos = pos
            
            # 记录移动历史用于预测
            self._record_movement(pos, current_time)
            
            # 根据修饰键确定交互模式
            new_mode = self._determine_interaction_mode(modifiers)
            if new_mode != self.state.current_mode:
                self._switch_interaction_mode(new_mode)
            
            # 计算调整后的位置
            adjusted_pos = self._calculate_adjusted_position(pos)
            
            # 更新测量信息
            self._update_measurement_info(adjusted_pos)
            
            # 触发延迟更新（减少UI重绘频率）
            if not self.update_timer.isActive():
                self.update_timer.start(16)  # ~60fps
            
            return adjusted_pos
            
        except Exception as e:
            logger.error(f"处理鼠标移动失败: {str(e)}")
            return pos

    def _record_movement(self, pos: QPointF, timestamp: float):
        """记录移动历史"""
        try:
            self.movement_history.append({
                'pos': pos,
                'timestamp': timestamp
            })
            
            # 限制历史长度
            if len(self.movement_history) > self.max_history_length:
                self.movement_history.pop(0)
                
        except Exception as e:
            logger.error(f"记录移动历史失败: {str(e)}")

    def _determine_interaction_mode(self, modifiers: int) -> str:
        """根据修饰键确定交互模式"""
        try:
            # Qt修饰键常量
            shift_pressed = bool(modifiers & 0x02000000)  # Qt.ShiftModifier
            ctrl_pressed = bool(modifiers & 0x04000000)   # Qt.ControlModifier
            alt_pressed = bool(modifiers & 0x08000000)    # Qt.AltModifier
            
            if ctrl_pressed and shift_pressed:
                return InteractionMode.PRECISION
            elif alt_pressed:
                return InteractionMode.SNAP
            elif shift_pressed:
                return InteractionMode.GUIDE
            else:
                return InteractionMode.NORMAL
                
        except Exception as e:
            logger.error(f"确定交互模式失败: {str(e)}")
            return InteractionMode.NORMAL

    def _switch_interaction_mode(self, new_mode: str):
        """切换交互模式"""
        try:
            old_mode = self.state.current_mode
            self.state.current_mode = new_mode
            
            logger.debug(f"交互模式切换: {old_mode} -> {new_mode}")
            self.precision_mode_changed.emit(new_mode)
            
            # 根据模式调整设置
            if new_mode == InteractionMode.PRECISION:
                self.settings.snap_threshold = 3.0
                self.settings.subpixel_precision = True
            elif new_mode == InteractionMode.SNAP:
                self.settings.snap_threshold = 15.0
                self.settings.snap_to_existing_shapes = True
            elif new_mode == InteractionMode.GUIDE:
                self.settings.show_precision_guides = True
            else:  # NORMAL
                self.settings.snap_threshold = 10.0
                
        except Exception as e:
            logger.error(f"切换交互模式失败: {str(e)}")

    def _calculate_adjusted_position(self, pos: QPointF) -> QPointF:
        """计算调整后的位置"""
        try:
            adjusted_pos = QPointF(pos)
            
            # 亚像素精度处理
            if self.settings.subpixel_precision:
                adjusted_pos = self._apply_subpixel_precision(adjusted_pos)
            
            # 吸附处理
            if self._should_apply_snapping():
                snap_result = self._find_snap_target(adjusted_pos)
                if snap_result:
                    adjusted_pos = snap_result.point
                    self.state.current_snap_target = snap_result
                    self.snap_target_found.emit(snap_result)
                else:
                    self.state.current_snap_target = None
            
            # 网格对齐
            if self.settings.snap_to_grid:
                adjusted_pos = self._snap_to_grid(adjusted_pos)
            
            # 运动预测（在精度模式下）
            if (self.state.current_mode == InteractionMode.PRECISION and 
                self.settings.enable_prediction):
                adjusted_pos = self._apply_movement_prediction(adjusted_pos)
            
            return adjusted_pos
            
        except Exception as e:
            logger.error(f"计算调整位置失败: {str(e)}")
            return pos

    def _apply_subpixel_precision(self, pos: QPointF) -> QPointF:
        """应用亚像素精度"""
        try:
            # 在精度模式下，保持更高的小数精度
            if self.state.current_mode == InteractionMode.PRECISION:
                # 保持0.1像素精度
                x = round(pos.x() * 10) / 10.0
                y = round(pos.y() * 10) / 10.0
            else:
                # 普通模式下，0.5像素精度
                x = round(pos.x() * 2) / 2.0
                y = round(pos.y() * 2) / 2.0
            
            return QPointF(x, y)
            
        except Exception as e:
            logger.error(f"应用亚像素精度失败: {str(e)}")
            return pos

    def _should_apply_snapping(self) -> bool:
        """判断是否应该应用吸附"""
        return (self.state.current_mode in [InteractionMode.SNAP, InteractionMode.PRECISION] or
                self.settings.snap_to_edges or
                self.settings.snap_to_corners or
                self.settings.snap_to_existing_shapes)

    def _find_snap_target(self, pos: QPointF) -> Optional[SnapCandidate]:
        """查找吸附目标"""
        try:
            candidates = []
            
            # 获取画布上的所有形状
            if not self.canvas or not hasattr(self.canvas, 'shapes'):
                return None
            
            shapes = getattr(self.canvas, 'shapes', [])
            
            # 查找边缘吸附
            if self.settings.snap_to_edges:
                candidates.extend(self._find_edge_snap_candidates(pos, shapes))
            
            # 查找角点吸附
            if self.settings.snap_to_corners:
                candidates.extend(self._find_corner_snap_candidates(pos, shapes))
            
            # 查找中心点吸附
            if self.settings.snap_to_centers:
                candidates.extend(self._find_center_snap_candidates(pos, shapes))
            
            # 查找已存在形状的吸附
            if self.settings.snap_to_existing_shapes:
                candidates.extend(self._find_shape_snap_candidates(pos, shapes))
            
            # 筛选和排序候选
            valid_candidates = [c for c in candidates if c.distance <= self.settings.snap_threshold]
            
            if not valid_candidates:
                return None
            
            # 按距离和置信度排序
            valid_candidates.sort(key=lambda c: c.distance * (2.0 - c.confidence))
            
            # 限制候选数量
            if len(valid_candidates) > self.settings.max_snap_candidates:
                valid_candidates = valid_candidates[:self.settings.max_snap_candidates]
            
            self.state.snap_candidates = valid_candidates
            
            return valid_candidates[0] if valid_candidates else None
            
        except Exception as e:
            logger.error(f"查找吸附目标失败: {str(e)}")
            return None

    def _find_edge_snap_candidates(self, pos: QPointF, shapes: List) -> List[SnapCandidate]:
        """查找边缘吸附候选"""
        candidates = []
        
        try:
            for shape in shapes:
                if shape == self.state.active_shape:  # 跳过当前编辑的形状
                    continue
                
                # 获取形状的点列表
                points = self._get_shape_points(shape)
                if len(points) < 2:
                    continue
                
                # 检查每条边
                for i in range(len(points)):
                    p1 = points[i]
                    p2 = points[(i + 1) % len(points)]
                    
                    # 计算点到线段的最短距离
                    closest_point, distance = self._point_to_line_distance(pos, p1, p2)
                    
                    if distance <= self.settings.snap_threshold:
                        candidates.append(SnapCandidate(
                            point=closest_point,
                            target_type=SnapTarget.EDGE,
                            distance=distance,
                            metadata={'shape': shape, 'edge_index': i}
                        ))
            
            return candidates
            
        except Exception as e:
            logger.error(f"查找边缘吸附候选失败: {str(e)}")
            return []

    def _find_corner_snap_candidates(self, pos: QPointF, shapes: List) -> List[SnapCandidate]:
        """查找角点吸附候选"""
        candidates = []
        
        try:
            for shape in shapes:
                if shape == self.state.active_shape:
                    continue
                
                points = self._get_shape_points(shape)
                
                for i, point in enumerate(points):
                    distance = self._calculate_distance(pos, point)
                    
                    if distance <= self.settings.snap_threshold:
                        candidates.append(SnapCandidate(
                            point=point,
                            target_type=SnapTarget.CORNER,
                            distance=distance,
                            metadata={'shape': shape, 'corner_index': i}
                        ))
            
            return candidates
            
        except Exception as e:
            logger.error(f"查找角点吸附候选失败: {str(e)}")
            return []

    def _find_center_snap_candidates(self, pos: QPointF, shapes: List) -> List[SnapCandidate]:
        """查找中心点吸附候选"""
        candidates = []
        
        try:
            for shape in shapes:
                if shape == self.state.active_shape:
                    continue
                
                center = self._get_shape_center(shape)
                if center:
                    distance = self._calculate_distance(pos, center)
                    
                    if distance <= self.settings.snap_threshold:
                        candidates.append(SnapCandidate(
                            point=center,
                            target_type=SnapTarget.CENTER,
                            distance=distance,
                            metadata={'shape': shape}
                        ))
            
            return candidates
            
        except Exception as e:
            logger.error(f"查找中心点吸附候选失败: {str(e)}")
            return []

    def _find_shape_snap_candidates(self, pos: QPointF, shapes: List) -> List[SnapCandidate]:
        """查找形状吸附候选"""
        candidates = []
        
        try:
            for shape in shapes:
                if shape == self.state.active_shape:
                    continue
                
                # 获取形状边界框
                bounds = self._get_shape_bounds(shape)
                if not bounds:
                    continue
                
                # 检查是否在形状附近
                expanded_bounds = bounds.adjusted(-self.settings.snap_threshold, 
                                                 -self.settings.snap_threshold,
                                                 self.settings.snap_threshold, 
                                                 self.settings.snap_threshold)
                
                if expanded_bounds.contains(pos):
                    # 计算到形状的最短距离
                    closest_point, distance = self._point_to_shape_distance(pos, shape)
                    
                    if distance <= self.settings.snap_threshold:
                        candidates.append(SnapCandidate(
                            point=closest_point,
                            target_type=SnapTarget.EXISTING_SHAPE,
                            distance=distance,
                            metadata={'shape': shape}
                        ))
            
            return candidates
            
        except Exception as e:
            logger.error(f"查找形状吸附候选失败: {str(e)}")
            return []

    def _get_shape_points(self, shape) -> List[QPointF]:
        """获取形状的点列表"""
        try:
            if hasattr(shape, 'points'):
                return shape.points
            elif hasattr(shape, 'rect'):
                rect = shape.rect
                return [
                    QPointF(rect.topLeft()),
                    QPointF(rect.topRight()),
                    QPointF(rect.bottomRight()),
                    QPointF(rect.bottomLeft())
                ]
            elif hasattr(shape, 'polygon'):
                polygon = shape.polygon
                return [polygon.at(i) for i in range(polygon.count())]
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取形状点失败: {str(e)}")
            return []

    def _get_shape_center(self, shape) -> Optional[QPointF]:
        """获取形状中心点"""
        try:
            bounds = self._get_shape_bounds(shape)
            if bounds:
                return bounds.center()
            
            points = self._get_shape_points(shape)
            if points:
                # 计算几何中心
                sum_x = sum(p.x() for p in points)
                sum_y = sum(p.y() for p in points)
                return QPointF(sum_x / len(points), sum_y / len(points))
            
            return None
            
        except Exception as e:
            logger.error(f"获取形状中心失败: {str(e)}")
            return None

    def _get_shape_bounds(self, shape) -> Optional[QRectF]:
        """获取形状边界框"""
        try:
            if hasattr(shape, 'boundingRect'):
                return shape.boundingRect()
            elif hasattr(shape, 'rect'):
                return shape.rect
            else:
                points = self._get_shape_points(shape)
                if points:
                    min_x = min(p.x() for p in points)
                    min_y = min(p.y() for p in points)
                    max_x = max(p.x() for p in points)
                    max_y = max(p.y() for p in points)
                    return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
            
            return None
            
        except Exception as e:
            logger.error(f"获取形状边界失败: {str(e)}")
            return None

    def _point_to_line_distance(self, point: QPointF, line_start: QPointF, 
                               line_end: QPointF) -> Tuple[QPointF, float]:
        """计算点到线段的最短距离"""
        try:
            # 向量计算
            line_vec = QPointF(line_end.x() - line_start.x(), line_end.y() - line_start.y())
            point_vec = QPointF(point.x() - line_start.x(), point.y() - line_start.y())
            
            line_length_sq = line_vec.x() ** 2 + line_vec.y() ** 2
            
            if line_length_sq == 0:
                # 线段长度为0，退化为点
                return line_start, self._calculate_distance(point, line_start)
            
            # 计算投影参数
            t = max(0, min(1, (point_vec.x() * line_vec.x() + point_vec.y() * line_vec.y()) / line_length_sq))
            
            # 计算最近点
            closest_point = QPointF(
                line_start.x() + t * line_vec.x(),
                line_start.y() + t * line_vec.y()
            )
            
            distance = self._calculate_distance(point, closest_point)
            
            return closest_point, distance
            
        except Exception as e:
            logger.error(f"计算点到线距离失败: {str(e)}")
            return point, float('inf')

    def _point_to_shape_distance(self, point: QPointF, shape) -> Tuple[QPointF, float]:
        """计算点到形状的最短距离"""
        try:
            points = self._get_shape_points(shape)
            if not points:
                return point, float('inf')
            
            min_distance = float('inf')
            closest_point = point
            
            # 检查每条边
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                
                candidate_point, distance = self._point_to_line_distance(point, p1, p2)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_point = candidate_point
            
            return closest_point, min_distance
            
        except Exception as e:
            logger.error(f"计算点到形状距离失败: {str(e)}")
            return point, float('inf')

    def _calculate_distance(self, p1: QPointF, p2: QPointF) -> float:
        """计算两点间距离"""
        try:
            dx = p1.x() - p2.x()
            dy = p1.y() - p2.y()
            return math.sqrt(dx * dx + dy * dy)
        except Exception as e:
            logger.error(f"计算距离失败: {str(e)}")
            return float('inf')

    def _snap_to_grid(self, pos: QPointF) -> QPointF:
        """网格对齐"""
        try:
            spacing = self.grid_spacing
            x = round(pos.x() / spacing) * spacing
            y = round(pos.y() / spacing) * spacing
            return QPointF(x, y)
        except Exception as e:
            logger.error(f"网格对齐失败: {str(e)}")
            return pos

    def _apply_movement_prediction(self, pos: QPointF) -> QPointF:
        """应用运动预测"""
        try:
            if len(self.movement_history) < 3:
                return pos
            
            # 计算运动趋势
            recent_movements = self.movement_history[-3:]
            
            # 计算平均速度向量
            total_dx = 0
            total_dy = 0
            total_dt = 0
            
            for i in range(1, len(recent_movements)):
                prev = recent_movements[i-1]
                curr = recent_movements[i]
                
                dt = curr['timestamp'] - prev['timestamp']
                if dt > 0:
                    dx = curr['pos'].x() - prev['pos'].x()
                    dy = curr['pos'].y() - prev['pos'].y()
                    
                    total_dx += dx / dt
                    total_dy += dy / dt
                    total_dt += 1
            
            if total_dt > 0:
                avg_velocity_x = total_dx / total_dt
                avg_velocity_y = total_dy / total_dt
                
                # 预测未来位置（短期预测）
                prediction_time = 0.05  # 50ms预测
                predicted_x = pos.x() + avg_velocity_x * prediction_time
                predicted_y = pos.y() + avg_velocity_y * prediction_time
                
                return QPointF(predicted_x, predicted_y)
            
            return pos
            
        except Exception as e:
            logger.error(f"运动预测失败: {str(e)}")
            return pos

    def _update_measurement_info(self, pos: QPointF):
        """更新测量信息"""
        try:
            info = {
                'position': (pos.x(), pos.y()),
                'mode': self.state.current_mode,
                'snap_target': None
            }
            
            if self.state.current_snap_target:
                info['snap_target'] = {
                    'type': self.state.current_snap_target.target_type,
                    'distance': self.state.current_snap_target.distance,
                    'confidence': self.state.current_snap_target.confidence
                }
            
            # 如果正在绘制或编辑，添加尺寸信息
            if self.state.is_drawing and self.state.drag_start_point:
                dx = pos.x() - self.state.drag_start_point.x()
                dy = pos.y() - self.state.drag_start_point.y()
                distance = math.sqrt(dx * dx + dy * dy)
                angle = math.degrees(math.atan2(dy, dx))
                
                info['drawing_info'] = {
                    'width': abs(dx),
                    'height': abs(dy),
                    'distance': distance,
                    'angle': angle
                }
            
            self.measurement_info = info
            self.measurement_updated.emit(info)
            
        except Exception as e:
            logger.error(f"更新测量信息失败: {str(e)}")

    def _delayed_update(self):
        """延迟更新处理"""
        try:
            # 这里可以进行一些非关键性的UI更新
            pass
        except Exception as e:
            logger.error(f"延迟更新失败: {str(e)}")

    def start_drawing(self, start_point: QPointF):
        """开始绘制"""
        try:
            self.state.is_drawing = True
            self.state.drag_start_point = start_point
            logger.debug(f"开始绘制于: ({start_point.x():.1f}, {start_point.y():.1f})")
        except Exception as e:
            logger.error(f"开始绘制失败: {str(e)}")

    def stop_drawing(self):
        """停止绘制"""
        try:
            self.state.is_drawing = False
            self.state.drag_start_point = None
            self.state.current_snap_target = None
            logger.debug("停止绘制")
        except Exception as e:
            logger.error(f"停止绘制失败: {str(e)}")

    def start_editing(self, shape, handle_index: int = -1):
        """开始编辑形状"""
        try:
            self.state.is_editing = True
            self.state.active_shape = shape
            self.state.selected_handle = handle_index
            logger.debug(f"开始编辑形状，句柄索引: {handle_index}")
        except Exception as e:
            logger.error(f"开始编辑失败: {str(e)}")

    def stop_editing(self):
        """停止编辑"""
        try:
            self.state.is_editing = False
            self.state.active_shape = None
            self.state.selected_handle = None
            self.state.current_snap_target = None
            logger.debug("停止编辑")
        except Exception as e:
            logger.error(f"停止编辑失败: {str(e)}")

    def get_visual_feedback_data(self) -> Dict[str, Any]:
        """获取视觉反馈数据"""
        try:
            feedback_data = {
                'snap_indicators': [],
                'guide_lines': [],
                'measurement_overlay': self.measurement_info,
                'mode_indicator': self.state.current_mode
            }
            
            # 吸附指示器
            if (self.settings.show_snap_indicators and 
                self.state.current_snap_target):
                feedback_data['snap_indicators'].append({
                    'position': self.state.current_snap_target.point,
                    'type': self.state.current_snap_target.target_type,
                    'confidence': self.state.current_snap_target.confidence
                })
            
            # 辅助线
            if self.settings.show_precision_guides:
                feedback_data['guide_lines'] = self._generate_guide_lines()
            
            return feedback_data
            
        except Exception as e:
            logger.error(f"获取视觉反馈数据失败: {str(e)}")
            return {}

    def _generate_guide_lines(self) -> List[Dict[str, Any]]:
        """生成辅助线"""
        guide_lines = []
        
        try:
            if not self.state.last_mouse_pos:
                return guide_lines
            
            mouse_pos = self.state.last_mouse_pos
            
            # 十字辅助线
            if self.state.current_mode == InteractionMode.GUIDE:
                # 水平线
                guide_lines.append({
                    'type': 'horizontal',
                    'position': mouse_pos.y(),
                    'style': 'dashed'
                })
                
                # 垂直线
                guide_lines.append({
                    'type': 'vertical',
                    'position': mouse_pos.x(),
                    'style': 'dashed'
                })
            
            # 对齐辅助线（与其他形状对齐）
            if self.settings.snap_to_existing_shapes and hasattr(self.canvas, 'shapes'):
                shapes = getattr(self.canvas, 'shapes', [])
                for shape in shapes:
                    if shape == self.state.active_shape:
                        continue
                    
                    center = self._get_shape_center(shape)
                    if center:
                        # 检查水平对齐
                        if abs(center.y() - mouse_pos.y()) < self.settings.snap_threshold:
                            guide_lines.append({
                                'type': 'horizontal',
                                'position': center.y(),
                                'style': 'solid',
                                'color': 'blue'
                            })
                        
                        # 检查垂直对齐
                        if abs(center.x() - mouse_pos.x()) < self.settings.snap_threshold:
                            guide_lines.append({
                                'type': 'vertical',
                                'position': center.x(),
                                'style': 'solid',
                                'color': 'blue'
                            })
            
            return guide_lines
            
        except Exception as e:
            logger.error(f"生成辅助线失败: {str(e)}")
            return []

    def configure_settings(self, **kwargs):
        """配置系统设置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
                    logger.debug(f"设置配置: {key} = {value}")
            
            # 重新计算相关参数
            self.update_interval = 1.0 / self.settings.update_frequency
            
        except Exception as e:
            logger.error(f"配置设置失败: {str(e)}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            return {
                'update_frequency': 1.0 / self.update_interval if self.update_interval > 0 else 0,
                'snap_candidates_count': len(self.state.snap_candidates),
                'movement_history_length': len(self.movement_history),
                'current_mode': self.state.current_mode,
                'cache_size': len(self.snap_cache),
                'last_update_time': self.last_update_time
            }
        except Exception as e:
            logger.error(f"获取性能指标失败: {str(e)}")
            return {}

    def reset(self):
        """重置系统状态"""
        try:
            self.state = InteractionState()
            self.movement_history.clear()
            self.snap_cache.clear()
            self.guide_lines.clear()
            self.measurement_info.clear()
            logger.info("精确交互系统已重置")
        except Exception as e:
            logger.error(f"重置系统失败: {str(e)}")