# -*- coding: utf-8 -*-
"""
性能监控和指标统计系统

主要功能：
1. 实时性能监控 - CPU、内存、渲染性能
2. 组件性能追踪 - 各个优化组件的性能指标
3. 用户体验指标 - 响应时间、操作流畅度
4. 性能报告生成 - 详细的性能分析报告
5. 性能预警和建议 - 基于阈值的预警系统
"""

import json
import os
import psutil
import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from .logger_config import get_logger

logger = get_logger(__name__)


class MetricType(Enum):
    """指标类型"""
    SYSTEM = "system"           # 系统性能指标
    RENDERING = "rendering"     # 渲染性能指标
    INTERACTION = "interaction" # 交互性能指标
    MEMORY = "memory"          # 内存使用指标
    CACHE = "cache"            # 缓存性能指标
    USER_EXPERIENCE = "user_experience"  # 用户体验指标


class AlertLevel(Enum):
    """警告级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    category: MetricType
    component: str = "unknown"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PerformanceAlert:
    """性能警告"""
    metric_name: str
    current_value: float
    threshold_value: float
    level: AlertLevel
    message: str
    timestamp: float
    component: str
    suggestions: List[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class ComponentStats:
    """组件统计信息"""
    component_name: str
    total_operations: int = 0
    average_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    last_update: float = 0.0


class PerformanceThresholds:
    """性能阈值配置"""
    def __init__(self):
        # 系统性能阈值
        self.cpu_usage_warning = 70.0      # CPU使用率警告阈值
        self.cpu_usage_critical = 85.0     # CPU使用率严重阈值
        self.memory_usage_warning = 75.0   # 内存使用率警告阈值
        self.memory_usage_critical = 90.0  # 内存使用率严重阈值
        
        # 渲染性能阈值
        self.frame_time_warning = 33.0     # 帧时间警告阈值(ms) - 30fps
        self.frame_time_critical = 66.0    # 帧时间严重阈值(ms) - 15fps
        self.render_queue_warning = 10     # 渲染队列警告阈值
        
        # 交互响应阈值
        self.interaction_delay_warning = 100.0   # 交互延迟警告阈值(ms)
        self.interaction_delay_critical = 300.0  # 交互延迟严重阈值(ms)
        
        # 缓存性能阈值
        self.cache_hit_rate_warning = 70.0       # 缓存命中率警告阈值
        self.cache_memory_warning = 500.0        # 缓存内存警告阈值(MB)


class PerformanceMonitor(QObject):
    """性能监控系统"""
    
    # 信号定义
    metric_updated = pyqtSignal(object)     # 指标更新
    alert_triggered = pyqtSignal(object)    # 警告触发
    report_ready = pyqtSignal(dict)         # 报告就绪
    threshold_exceeded = pyqtSignal(str, float, float)  # 阈值超出

    def __init__(self, config_file: str = "config/performance_config.json"):
        super().__init__()
        
        self.config_file = config_file
        self.thresholds = PerformanceThresholds()
        
        # 数据存储
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.component_stats = {}
        self.active_alerts = []
        self.performance_sessions = []
        
        # 监控状态
        self.monitoring_enabled = True
        self.collection_interval = 1.0  # 秒
        self.last_system_check = 0
        
        # 组件引用
        self.monitored_components = {}
        
        # 统计计算缓存
        self.stats_cache = {}
        self.cache_expiry = 5.0  # 缓存过期时间(秒)
        
        # 定时器
        self.collection_timer = QTimer()
        self.collection_timer.timeout.connect(self.collect_system_metrics)
        
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.analyze_performance)
        
        # 加载配置
        self.load_configuration()
        
        # 开始监控
        self.start_monitoring()

    def start_monitoring(self):
        """开始性能监控"""
        try:
            if not self.monitoring_enabled:
                return
            
            # 启动定时器
            self.collection_timer.start(int(self.collection_interval * 1000))
            self.analysis_timer.start(5000)  # 每5秒分析一次
            
            logger.info("性能监控已开始")
            
        except Exception as e:
            logger.error(f"启动性能监控失败: {str(e)}")

    def stop_monitoring(self):
        """停止性能监控"""
        try:
            self.collection_timer.stop()
            self.analysis_timer.stop()
            
            logger.info("性能监控已停止")
            
        except Exception as e:
            logger.error(f"停止性能监控失败: {str(e)}")

    def register_component(self, component_name: str, component_instance: Any):
        """注册监控组件"""
        try:
            self.monitored_components[component_name] = component_instance
            
            if component_name not in self.component_stats:
                self.component_stats[component_name] = ComponentStats(component_name)
            
            logger.debug(f"组件已注册: {component_name}")
            
        except Exception as e:
            logger.error(f"注册组件失败: {str(e)}")

    def record_metric(self, name: str, value: float, unit: str, 
                     category: MetricType, component: str = "system", 
                     metadata: Dict[str, Any] = None):
        """记录性能指标"""
        try:
            current_time = time.time()
            
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=current_time,
                category=category,
                component=component,
                metadata=metadata or {}
            )
            
            # 存储指标
            self.metrics_history[name].append(metric)
            
            # 检查阈值
            self._check_thresholds(metric)
            
            # 发送信号
            self.metric_updated.emit(metric)
            
            # 更新组件统计
            self._update_component_stats(component, value)
            
        except Exception as e:
            logger.error(f"记录性能指标失败: {str(e)}")

    def record_operation(self, component: str, operation: str, 
                        duration: float, success: bool = True, 
                        metadata: Dict[str, Any] = None):
        """记录组件操作"""
        try:
            # 记录操作持续时间
            self.record_metric(
                name=f"{component}_{operation}_duration",
                value=duration,
                unit="ms",
                category=MetricType.INTERACTION,
                component=component,
                metadata=metadata
            )
            
            # 更新组件统计
            if component not in self.component_stats:
                self.component_stats[component] = ComponentStats(component)
            
            stats = self.component_stats[component]
            stats.total_operations += 1
            stats.last_update = time.time()
            
            if success:
                # 更新平均持续时间
                if stats.total_operations == 1:
                    stats.average_duration = duration
                else:
                    stats.average_duration = (
                        (stats.average_duration * (stats.total_operations - 1) + duration) 
                        / stats.total_operations
                    )
                
                # 更新最小最大值
                stats.min_duration = min(stats.min_duration, duration)
                stats.max_duration = max(stats.max_duration, duration)
            else:
                stats.error_count += 1
            
            # 更新成功率
            stats.success_rate = ((stats.total_operations - stats.error_count) 
                                / stats.total_operations * 100)
            
        except Exception as e:
            logger.error(f"记录组件操作失败: {str(e)}")

    def collect_system_metrics(self):
        """收集系统性能指标"""
        try:
            current_time = time.time()
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.record_metric("cpu_usage", cpu_percent, "%", MetricType.SYSTEM)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            self.record_metric("memory_usage", memory.percent, "%", MetricType.SYSTEM)
            self.record_metric("memory_available", memory.available / (1024**3), "GB", MetricType.SYSTEM)
            
            # 进程信息
            process = psutil.Process()
            process_memory = process.memory_info()
            self.record_metric("process_memory", process_memory.rss / (1024**2), "MB", MetricType.SYSTEM)
            self.record_metric("process_cpu", process.cpu_percent(), "%", MetricType.SYSTEM)
            
            # 磁盘I/O（如果需要）
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.record_metric("disk_read_rate", disk_io.read_bytes / (1024**2), "MB/s", MetricType.SYSTEM)
                self.record_metric("disk_write_rate", disk_io.write_bytes / (1024**2), "MB/s", MetricType.SYSTEM)
            
            self.last_system_check = current_time
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {str(e)}")

    def collect_component_metrics(self):
        """收集组件性能指标"""
        try:
            for component_name, component in self.monitored_components.items():
                try:
                    # 尝试获取组件的性能指标
                    if hasattr(component, 'get_performance_metrics'):
                        metrics = component.get_performance_metrics()
                        
                        for metric_name, metric_data in metrics.items():
                            if isinstance(metric_data, dict):
                                value = metric_data.get('value', 0)
                                unit = metric_data.get('unit', 'count')
                                category = MetricType.RENDERING  # 默认类别
                            else:
                                value = float(metric_data)
                                unit = 'count'
                                category = MetricType.RENDERING
                            
                            self.record_metric(
                                name=f"{component_name}_{metric_name}",
                                value=value,
                                unit=unit,
                                category=category,
                                component=component_name
                            )
                            
                except Exception as comp_error:
                    logger.debug(f"收集组件 {component_name} 指标失败: {comp_error}")
                    
        except Exception as e:
            logger.error(f"收集组件指标失败: {str(e)}")

    def _check_thresholds(self, metric: PerformanceMetric):
        """检查性能阈值"""
        try:
            alerts = []
            
            # CPU使用率检查
            if metric.name == "cpu_usage":
                if metric.value >= self.thresholds.cpu_usage_critical:
                    alerts.append(PerformanceAlert(
                        metric_name=metric.name,
                        current_value=metric.value,
                        threshold_value=self.thresholds.cpu_usage_critical,
                        level=AlertLevel.CRITICAL,
                        message=f"CPU使用率过高: {metric.value:.1f}%",
                        timestamp=metric.timestamp,
                        component=metric.component,
                        suggestions=["检查CPU密集型操作", "优化算法复杂度", "减少并发任务"]
                    ))
                elif metric.value >= self.thresholds.cpu_usage_warning:
                    alerts.append(PerformanceAlert(
                        metric_name=metric.name,
                        current_value=metric.value,
                        threshold_value=self.thresholds.cpu_usage_warning,
                        level=AlertLevel.WARNING,
                        message=f"CPU使用率较高: {metric.value:.1f}%",
                        timestamp=metric.timestamp,
                        component=metric.component,
                        suggestions=["监控CPU使用趋势", "考虑优化热点代码"]
                    ))
            
            # 内存使用率检查
            elif metric.name == "memory_usage":
                if metric.value >= self.thresholds.memory_usage_critical:
                    alerts.append(PerformanceAlert(
                        metric_name=metric.name,
                        current_value=metric.value,
                        threshold_value=self.thresholds.memory_usage_critical,
                        level=AlertLevel.CRITICAL,
                        message=f"内存使用率过高: {metric.value:.1f}%",
                        timestamp=metric.timestamp,
                        component=metric.component,
                        suggestions=["清理缓存", "释放未使用资源", "检查内存泄漏"]
                    ))
                elif metric.value >= self.thresholds.memory_usage_warning:
                    alerts.append(PerformanceAlert(
                        metric_name=metric.name,
                        current_value=metric.value,
                        threshold_value=self.thresholds.memory_usage_warning,
                        level=AlertLevel.WARNING,
                        message=f"内存使用率较高: {metric.value:.1f}%",
                        timestamp=metric.timestamp,
                        component=metric.component,
                        suggestions=["监控内存使用趋势", "优化数据结构"]
                    ))
            
            # 帧时间检查
            elif "frame_time" in metric.name or "render_time" in metric.name:
                if metric.value >= self.thresholds.frame_time_critical:
                    alerts.append(PerformanceAlert(
                        metric_name=metric.name,
                        current_value=metric.value,
                        threshold_value=self.thresholds.frame_time_critical,
                        level=AlertLevel.CRITICAL,
                        message=f"渲染性能严重下降: {metric.value:.1f}ms",
                        timestamp=metric.timestamp,
                        component=metric.component,
                        suggestions=["启用渲染缓存", "减少绘制复杂度", "优化图形算法"]
                    ))
                elif metric.value >= self.thresholds.frame_time_warning:
                    alerts.append(PerformanceAlert(
                        metric_name=metric.name,
                        current_value=metric.value,
                        threshold_value=self.thresholds.frame_time_warning,
                        level=AlertLevel.WARNING,
                        message=f"渲染性能下降: {metric.value:.1f}ms",
                        timestamp=metric.timestamp,
                        component=metric.component,
                        suggestions=["检查渲染瓶颈", "优化绘制顺序"]
                    ))
            
            # 处理警告
            for alert in alerts:
                self._handle_alert(alert)
                
        except Exception as e:
            logger.error(f"检查性能阈值失败: {str(e)}")

    def _handle_alert(self, alert: PerformanceAlert):
        """处理性能警告"""
        try:
            # 检查是否已存在相同警告
            existing_alert = None
            for existing in self.active_alerts:
                if (existing.metric_name == alert.metric_name and 
                    existing.component == alert.component and
                    existing.level == alert.level):
                    existing_alert = existing
                    break
            
            if existing_alert:
                # 更新现有警告
                existing_alert.current_value = alert.current_value
                existing_alert.timestamp = alert.timestamp
            else:
                # 添加新警告
                self.active_alerts.append(alert)
                
                # 记录警告日志
                log_level = logger.warning if alert.level == AlertLevel.WARNING else logger.error
                log_level(f"性能警告: {alert.message}")
            
            # 发送警告信号
            self.alert_triggered.emit(alert)
            self.threshold_exceeded.emit(alert.metric_name, alert.current_value, alert.threshold_value)
            
        except Exception as e:
            logger.error(f"处理性能警告失败: {str(e)}")

    def _update_component_stats(self, component: str, value: float):
        """更新组件统计信息"""
        try:
            if component not in self.component_stats:
                self.component_stats[component] = ComponentStats(component)
            
            # 这里可以添加更多的统计更新逻辑
            
        except Exception as e:
            logger.error(f"更新组件统计失败: {str(e)}")

    def analyze_performance(self):
        """分析性能趋势"""
        try:
            current_time = time.time()
            
            # 清理过期的缓存
            self._cleanup_expired_cache(current_time)
            
            # 收集组件指标
            self.collect_component_metrics()
            
            # 分析性能趋势
            trends = self._analyze_performance_trends()
            
            # 生成性能建议
            suggestions = self._generate_performance_suggestions(trends)
            
            # 清理旧的警告
            self._cleanup_old_alerts(current_time)
            
        except Exception as e:
            logger.error(f"性能分析失败: {str(e)}")

    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趋势"""
        trends = {}
        
        try:
            for metric_name, metrics in self.metrics_history.items():
                if len(metrics) < 10:  # 需要足够的数据点
                    continue
                
                # 获取最近的指标
                recent_metrics = list(metrics)[-10:]
                values = [m.value for m in recent_metrics]
                
                # 计算趋势
                if len(values) >= 2:
                    # 简单的线性趋势分析
                    avg_first_half = sum(values[:len(values)//2]) / (len(values)//2)
                    avg_second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
                    
                    trend_direction = "improving" if avg_second_half < avg_first_half else "degrading"
                    if abs(avg_second_half - avg_first_half) < avg_first_half * 0.05:  # 5%阈值
                        trend_direction = "stable"
                    
                    trends[metric_name] = {
                        'direction': trend_direction,
                        'current_avg': avg_second_half,
                        'previous_avg': avg_first_half,
                        'change_percent': ((avg_second_half - avg_first_half) / avg_first_half * 100) if avg_first_half > 0 else 0
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"分析性能趋势失败: {str(e)}")
            return {}

    def _generate_performance_suggestions(self, trends: Dict[str, Any]) -> List[str]:
        """生成性能建议"""
        suggestions = []
        
        try:
            for metric_name, trend_data in trends.items():
                if trend_data['direction'] == 'degrading':
                    change_percent = abs(trend_data['change_percent'])
                    
                    if 'cpu' in metric_name.lower():
                        if change_percent > 20:
                            suggestions.append(f"CPU性能下降 {change_percent:.1f}%，建议检查CPU密集型操作")
                        
                    elif 'memory' in metric_name.lower():
                        if change_percent > 15:
                            suggestions.append(f"内存使用增长 {change_percent:.1f}%，建议检查内存泄漏")
                        
                    elif 'render' in metric_name.lower() or 'frame' in metric_name.lower():
                        if change_percent > 25:
                            suggestions.append(f"渲染性能下降 {change_percent:.1f}%，建议优化绘制算法")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成性能建议失败: {str(e)}")
            return []

    def _cleanup_expired_cache(self, current_time: float):
        """清理过期缓存"""
        try:
            expired_keys = []
            for key, (value, timestamp) in self.stats_cache.items():
                if current_time - timestamp > self.cache_expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.stats_cache[key]
                
        except Exception as e:
            logger.error(f"清理过期缓存失败: {str(e)}")

    def _cleanup_old_alerts(self, current_time: float):
        """清理旧警告"""
        try:
            # 移除30分钟前的警告
            alert_expiry = 30 * 60  # 30分钟
            
            self.active_alerts = [
                alert for alert in self.active_alerts
                if current_time - alert.timestamp < alert_expiry
            ]
            
        except Exception as e:
            logger.error(f"清理旧警告失败: {str(e)}")

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        try:
            current_time = time.time()
            
            # 系统概况
            system_metrics = self._get_current_system_metrics()
            
            # 组件统计
            component_summary = {}
            for name, stats in self.component_stats.items():
                component_summary[name] = {
                    'total_operations': stats.total_operations,
                    'average_duration': stats.average_duration,
                    'success_rate': stats.success_rate,
                    'error_count': stats.error_count
                }
            
            # 活跃警告
            active_alerts_summary = []
            for alert in self.active_alerts:
                active_alerts_summary.append({
                    'metric': alert.metric_name,
                    'level': alert.level.value,
                    'message': alert.message,
                    'component': alert.component
                })
            
            # 性能趋势
            trends = self._analyze_performance_trends()
            
            report = {
                'timestamp': current_time,
                'system_metrics': system_metrics,
                'component_summary': component_summary,
                'active_alerts': active_alerts_summary,
                'performance_trends': trends,
                'monitoring_status': {
                    'enabled': self.monitoring_enabled,
                    'collection_interval': self.collection_interval,
                    'monitored_components': list(self.monitored_components.keys())
                },
                'recommendations': self._generate_performance_suggestions(trends)
            }
            
            self.report_ready.emit(report)
            return report
            
        except Exception as e:
            logger.error(f"生成性能报告失败: {str(e)}")
            return {}

    def _get_current_system_metrics(self) -> Dict[str, Any]:
        """获取当前系统指标"""
        try:
            metrics = {}
            
            # 获取最新的系统指标
            for metric_name in ['cpu_usage', 'memory_usage', 'process_memory', 'process_cpu']:
                if metric_name in self.metrics_history:
                    recent_metrics = list(self.metrics_history[metric_name])
                    if recent_metrics:
                        latest = recent_metrics[-1]
                        metrics[metric_name] = {
                            'value': latest.value,
                            'unit': latest.unit,
                            'timestamp': latest.timestamp
                        }
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取当前系统指标失败: {str(e)}")
            return {}

    def configure_thresholds(self, **kwargs):
        """配置性能阈值"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.thresholds, key):
                    setattr(self.thresholds, key, value)
                    logger.debug(f"阈值配置更新: {key} = {value}")
            
            self.save_configuration()
            
        except Exception as e:
            logger.error(f"配置性能阈值失败: {str(e)}")

    def save_configuration(self):
        """保存配置到文件"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            config_data = {
                'version': '1.0',
                'monitoring_enabled': self.monitoring_enabled,
                'collection_interval': self.collection_interval,
                'thresholds': {
                    'cpu_usage_warning': self.thresholds.cpu_usage_warning,
                    'cpu_usage_critical': self.thresholds.cpu_usage_critical,
                    'memory_usage_warning': self.thresholds.memory_usage_warning,
                    'memory_usage_critical': self.thresholds.memory_usage_critical,
                    'frame_time_warning': self.thresholds.frame_time_warning,
                    'frame_time_critical': self.thresholds.frame_time_critical,
                    'interaction_delay_warning': self.thresholds.interaction_delay_warning,
                    'interaction_delay_critical': self.thresholds.interaction_delay_critical,
                    'cache_hit_rate_warning': self.thresholds.cache_hit_rate_warning,
                    'cache_memory_warning': self.thresholds.cache_memory_warning
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"性能监控配置已保存到: {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")

    def load_configuration(self):
        """从文件加载配置"""
        try:
            if not os.path.exists(self.config_file):
                logger.info("性能监控配置文件不存在，使用默认配置")
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 加载基础配置
            self.monitoring_enabled = config_data.get('monitoring_enabled', True)
            self.collection_interval = config_data.get('collection_interval', 1.0)
            
            # 加载阈值配置
            thresholds_config = config_data.get('thresholds', {})
            for key, value in thresholds_config.items():
                if hasattr(self.thresholds, key):
                    setattr(self.thresholds, key, value)
            
            logger.info(f"性能监控配置已从 {self.config_file} 加载")
            
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")

    def export_metrics(self, file_path: str, time_range: Optional[Tuple[float, float]] = None):
        """导出性能指标数据"""
        try:
            export_data = {
                'version': '1.0',
                'export_timestamp': time.time(),
                'time_range': time_range,
                'metrics': {}
            }
            
            for metric_name, metrics in self.metrics_history.items():
                filtered_metrics = []
                
                for metric in metrics:
                    # 时间范围过滤
                    if time_range:
                        start_time, end_time = time_range
                        if not (start_time <= metric.timestamp <= end_time):
                            continue
                    
                    filtered_metrics.append(asdict(metric))
                
                if filtered_metrics:
                    export_data['metrics'][metric_name] = filtered_metrics
            
            # 导出组件统计
            export_data['component_stats'] = {}
            for name, stats in self.component_stats.items():
                export_data['component_stats'][name] = asdict(stats)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"性能指标已导出到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出性能指标失败: {str(e)}")
            return False

    def clear_metrics(self, older_than: Optional[float] = None):
        """清理性能指标数据"""
        try:
            if older_than is None:
                # 清空所有数据
                self.metrics_history.clear()
                self.component_stats.clear()
                self.active_alerts.clear()
                logger.info("所有性能指标数据已清理")
            else:
                # 清理指定时间之前的数据
                current_time = time.time()
                cutoff_time = current_time - older_than
                
                for metric_name in list(self.metrics_history.keys()):
                    metrics = self.metrics_history[metric_name]
                    # 保留指定时间之后的数据
                    filtered_metrics = deque(
                        [m for m in metrics if m.timestamp > cutoff_time],
                        maxlen=metrics.maxlen
                    )
                    self.metrics_history[metric_name] = filtered_metrics
                
                # 清理旧警告
                self.active_alerts = [
                    alert for alert in self.active_alerts
                    if alert.timestamp > cutoff_time
                ]
                
                logger.info(f"已清理 {older_than} 秒前的性能数据")
            
        except Exception as e:
            logger.error(f"清理性能指标失败: {str(e)}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        try:
            return {
                'enabled': self.monitoring_enabled,
                'collection_interval': self.collection_interval,
                'monitored_components_count': len(self.monitored_components),
                'active_alerts_count': len(self.active_alerts),
                'metrics_count': sum(len(metrics) for metrics in self.metrics_history.values()),
                'last_system_check': self.last_system_check,
                'cache_size': len(self.stats_cache)
            }
        except Exception as e:
            logger.error(f"获取监控状态失败: {str(e)}")
            return {}