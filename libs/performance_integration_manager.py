# -*- coding: utf-8 -*-
"""
性能监控集成管理器

主要功能：
1. 统一管理所有性能优化组件
2. 协调各组件之间的性能监控
3. 提供统一的性能报告和分析
4. 自动优化配置建议
5. 性能问题自动诊断和修复
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from .performance_monitor import PerformanceMonitor, MetricType
from .logger_config import get_logger

logger = get_logger(__name__)


class OptimizationLevel(str):
    """优化级别"""
    CONSERVATIVE = "conservative"  # 保守优化
    BALANCED = "balanced"         # 平衡优化
    AGGRESSIVE = "aggressive"     # 激进优化


class PerformanceIntegrationManager(QObject):
    """性能监控集成管理器"""
    
    # 信号定义
    performance_status_changed = pyqtSignal(dict)    # 性能状态变化
    optimization_applied = pyqtSignal(str, dict)     # 优化应用
    performance_report_ready = pyqtSignal(dict)      # 性能报告就绪
    auto_optimization_triggered = pyqtSignal(str)    # 自动优化触发

    def __init__(self, main_window=None):
        super().__init__()
        
        self.main_window = main_window
        
        # 初始化性能监控器
        self.performance_monitor = PerformanceMonitor()
        
        # 组件注册表
        self.registered_components = {}
        
        # 性能状态
        self.current_optimization_level = OptimizationLevel.BALANCED
        self.auto_optimization_enabled = True
        self.last_optimization_time = 0
        
        # 性能基线
        self.performance_baseline = {}
        self.baseline_established = False
        
        # 自动优化配置
        self.auto_optimization_config = {
            'cpu_threshold': 80.0,          # CPU使用率阈值
            'memory_threshold': 85.0,       # 内存使用率阈值
            'render_time_threshold': 50.0,  # 渲染时间阈值(ms)
            'cache_optimization_interval': 300,  # 缓存优化间隔(秒)
            'system_check_interval': 60,    # 系统检查间隔(秒)
        }
        
        # 连接性能监控器信号
        self.performance_monitor.alert_triggered.connect(self._handle_performance_alert)
        self.performance_monitor.metric_updated.connect(self._handle_metric_update)
        
        # 定期优化检查定时器
        self.optimization_timer = QTimer()
        self.optimization_timer.timeout.connect(self._periodic_optimization_check)
        self.optimization_timer.start(30000)  # 每30秒检查一次
        
        # 性能报告定时器
        self.report_timer = QTimer()
        self.report_timer.timeout.connect(self._generate_periodic_report)
        self.report_timer.start(300000)  # 每5分钟生成一次报告

    def register_all_components(self):
        """注册所有性能优化组件"""
        try:
            if not self.main_window:
                logger.warning("主窗口未设置，无法注册组件")
                return
            
            # 注册图像缓存管理器
            if hasattr(self.main_window, 'image_cache_manager'):
                self.register_component(
                    'image_cache_manager', 
                    self.main_window.image_cache_manager,
                    {
                        'cache_hit_rate': {'threshold': 70.0, 'unit': '%'},
                        'memory_usage': {'threshold': 512.0, 'unit': 'MB'},
                        'cache_size': {'threshold': 50, 'unit': 'items'}
                    }
                )
            
            # 注册Canvas优化渲染器
            if (hasattr(self.main_window, 'canvas') and 
                hasattr(self.main_window.canvas, 'optimized_renderer')):
                self.register_component(
                    'canvas_renderer',
                    self.main_window.canvas.optimized_renderer,
                    {
                        'render_time': {'threshold': 33.0, 'unit': 'ms'},
                        'layer_cache_hits': {'threshold': 80.0, 'unit': '%'},
                        'dirty_regions_count': {'threshold': 10, 'unit': 'count'}
                    }
                )
            
            # 注册后台任务管理器
            if hasattr(self.main_window, 'background_task_manager'):
                self.register_component(
                    'background_task_manager',
                    self.main_window.background_task_manager,
                    {
                        'queue_size': {'threshold': 20, 'unit': 'tasks'},
                        'average_task_time': {'threshold': 100.0, 'unit': 'ms'},
                        'failed_tasks_rate': {'threshold': 5.0, 'unit': '%'}
                    }
                )
            
            # 注册防抖管理器
            if hasattr(self.main_window, 'debounce_manager'):
                self.register_component(
                    'debounce_manager',
                    self.main_window.debounce_manager,
                    {
                        'active_debounces': {'threshold': 50, 'unit': 'count'},
                        'average_delay': {'threshold': 150.0, 'unit': 'ms'}
                    }
                )
            
            # 注册快捷键优化器
            if hasattr(self.main_window, 'shortcut_optimizer'):
                self.register_component(
                    'shortcut_optimizer',
                    self.main_window.shortcut_optimizer,
                    {
                        'conflicts_count': {'threshold': 3, 'unit': 'count'},
                        'optimization_suggestions': {'threshold': 10, 'unit': 'count'}
                    }
                )
            
            # 注册用户习惯记忆系统
            if hasattr(self.main_window, 'habit_memory'):
                self.register_component(
                    'habit_memory',
                    self.main_window.habit_memory,
                    {
                        'learning_effectiveness': {'threshold': 0.6, 'unit': 'score'},
                        'active_patterns': {'threshold': 50, 'unit': 'count'}
                    }
                )
            
            # 注册精确交互系统
            if (hasattr(self.main_window, 'canvas') and 
                hasattr(self.main_window.canvas, 'precision_system')):
                self.register_component(
                    'precision_system',
                    self.main_window.canvas.precision_system,
                    {
                        'snap_accuracy': {'threshold': 85.0, 'unit': '%'},
                        'interaction_delay': {'threshold': 10.0, 'unit': 'ms'}
                    }
                )
            
            logger.info(f"已注册 {len(self.registered_components)} 个性能优化组件")
            
        except Exception as e:
            logger.error(f"注册组件失败: {str(e)}")

    def register_component(self, name: str, component: Any, 
                          performance_thresholds: Dict[str, Dict[str, Any]] = None):
        """注册单个组件"""
        try:
            self.registered_components[name] = {
                'instance': component,
                'thresholds': performance_thresholds or {},
                'last_check': 0,
                'performance_history': [],
                'status': 'healthy'
            }
            
            # 在性能监控器中注册
            self.performance_monitor.register_component(name, component)
            
            logger.debug(f"组件已注册: {name}")
            
        except Exception as e:
            logger.error(f"注册组件 {name} 失败: {str(e)}")

    def _handle_performance_alert(self, alert):
        """处理性能警告"""
        try:
            logger.warning(f"性能警告: {alert.message}")
            
            # 根据警告类型自动应用优化
            if self.auto_optimization_enabled:
                optimization_applied = self._apply_automatic_optimization(alert)
                
                if optimization_applied:
                    self.auto_optimization_triggered.emit(alert.metric_name)
            
        except Exception as e:
            logger.error(f"处理性能警告失败: {str(e)}")

    def _handle_metric_update(self, metric):
        """处理指标更新"""
        try:
            # 更新组件状态
            self._update_component_status(metric)
            
            # 检查是否需要建立性能基线
            if not self.baseline_established:
                self._try_establish_baseline()
            
        except Exception as e:
            logger.error(f"处理指标更新失败: {str(e)}")

    def _apply_automatic_optimization(self, alert) -> bool:
        """应用自动优化"""
        try:
            current_time = time.time()
            
            # 防止过于频繁的优化
            if current_time - self.last_optimization_time < 60:  # 1分钟内不重复优化
                return False
            
            optimization_applied = False
            
            # 根据警告类型应用相应优化
            if 'cpu_usage' in alert.metric_name:
                optimization_applied = self._optimize_cpu_usage()
            elif 'memory_usage' in alert.metric_name:
                optimization_applied = self._optimize_memory_usage()
            elif 'render' in alert.metric_name or 'frame' in alert.metric_name:
                optimization_applied = self._optimize_rendering()
            elif 'cache' in alert.metric_name:
                optimization_applied = self._optimize_cache_settings()
            
            if optimization_applied:
                self.last_optimization_time = current_time
                self.optimization_applied.emit(alert.metric_name, {
                    'timestamp': current_time,
                    'alert_level': alert.level.value,
                    'optimization_type': 'automatic'
                })
            
            return optimization_applied
            
        except Exception as e:
            logger.error(f"应用自动优化失败: {str(e)}")
            return False

    def _optimize_cpu_usage(self) -> bool:
        """优化CPU使用率"""
        try:
            optimizations_applied = []
            
            # 减少后台任务并发数
            if 'background_task_manager' in self.registered_components:
                component = self.registered_components['background_task_manager']['instance']
                if hasattr(component, 'set_max_workers'):
                    current_workers = getattr(component, 'max_workers', 4)
                    new_workers = max(1, current_workers - 1)
                    component.set_max_workers(new_workers)
                    optimizations_applied.append(f"减少后台任务工作线程: {current_workers} -> {new_workers}")
            
            # 降低渲染质量
            if 'canvas_renderer' in self.registered_components:
                component = self.registered_components['canvas_renderer']['instance']
                if hasattr(component, 'set_quality_level'):
                    component.set_quality_level('medium')
                    optimizations_applied.append("降低渲染质量到中等")
            
            # 增加防抖延迟
            if 'debounce_manager' in self.registered_components:
                component = self.registered_components['debounce_manager']['instance']
                if hasattr(component, 'increase_global_delay'):
                    component.increase_global_delay(50)  # 增加50ms延迟
                    optimizations_applied.append("增加防抖延迟50ms")
            
            if optimizations_applied:
                logger.info(f"CPU优化应用: {'; '.join(optimizations_applied)}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"CPU优化失败: {str(e)}")
            return False

    def _optimize_memory_usage(self) -> bool:
        """优化内存使用"""
        try:
            optimizations_applied = []
            
            # 清理图像缓存
            if 'image_cache_manager' in self.registered_components:
                component = self.registered_components['image_cache_manager']['instance']
                if hasattr(component, 'cleanup_cache'):
                    freed_memory = component.cleanup_cache(force=True)
                    optimizations_applied.append(f"清理图像缓存，释放 {freed_memory:.1f}MB")
            
            # 清理渲染缓存
            if 'canvas_renderer' in self.registered_components:
                component = self.registered_components['canvas_renderer']['instance']
                if hasattr(component, 'clear_layer_cache'):
                    component.clear_layer_cache()
                    optimizations_applied.append("清理渲染层缓存")
            
            # 减少缓存大小
            if 'image_cache_manager' in self.registered_components:
                component = self.registered_components['image_cache_manager']['instance']
                if hasattr(component, 'set_max_cache_size'):
                    current_size = getattr(component, 'max_cache_size', 30)
                    new_size = max(10, int(current_size * 0.7))
                    component.set_max_cache_size(new_size)
                    optimizations_applied.append(f"减少缓存大小: {current_size} -> {new_size}")
            
            if optimizations_applied:
                logger.info(f"内存优化应用: {'; '.join(optimizations_applied)}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"内存优化失败: {str(e)}")
            return False

    def _optimize_rendering(self) -> bool:
        """优化渲染性能"""
        try:
            optimizations_applied = []
            
            # 启用分层缓存
            if 'canvas_renderer' in self.registered_components:
                component = self.registered_components['canvas_renderer']['instance']
                if hasattr(component, 'enable_layer_caching'):
                    component.enable_layer_caching(True)
                    optimizations_applied.append("启用渲染分层缓存")
                
                # 减少渲染细节
                if hasattr(component, 'set_detail_level'):
                    component.set_detail_level('low')
                    optimizations_applied.append("降低渲染细节级别")
            
            # 减少精确交互系统的更新频率
            if 'precision_system' in self.registered_components:
                component = self.registered_components['precision_system']['instance']
                if hasattr(component, 'configure_settings'):
                    component.configure_settings(update_frequency=30)  # 降到30fps
                    optimizations_applied.append("降低精确交互更新频率")
            
            if optimizations_applied:
                logger.info(f"渲染优化应用: {'; '.join(optimizations_applied)}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"渲染优化失败: {str(e)}")
            return False

    def _optimize_cache_settings(self) -> bool:
        """优化缓存设置"""
        try:
            optimizations_applied = []
            
            # 优化图像缓存策略
            if 'image_cache_manager' in self.registered_components:
                component = self.registered_components['image_cache_manager']['instance']
                if hasattr(component, 'optimize_cache_strategy'):
                    component.optimize_cache_strategy()
                    optimizations_applied.append("优化图像缓存策略")
            
            # 清理旧的缓存条目
            for comp_name, comp_data in self.registered_components.items():
                component = comp_data['instance']
                if hasattr(component, 'cleanup_old_cache'):
                    component.cleanup_old_cache()
                    optimizations_applied.append(f"清理 {comp_name} 旧缓存")
            
            if optimizations_applied:
                logger.info(f"缓存优化应用: {'; '.join(optimizations_applied)}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"缓存优化失败: {str(e)}")
            return False

    def _periodic_optimization_check(self):
        """定期优化检查"""
        try:
            current_time = time.time()
            
            # 检查各组件状态
            for comp_name, comp_data in self.registered_components.items():
                last_check = comp_data['last_check']
                
                # 每分钟检查一次组件
                if current_time - last_check > 60:
                    self._check_component_performance(comp_name)
                    comp_data['last_check'] = current_time
            
            # 自动清理缓存（每5分钟）
            if (current_time - getattr(self, '_last_cache_cleanup', 0) > 
                self.auto_optimization_config['cache_optimization_interval']):
                self._auto_cache_cleanup()
                self._last_cache_cleanup = current_time
            
        except Exception as e:
            logger.error(f"定期优化检查失败: {str(e)}")

    def _check_component_performance(self, component_name: str):
        """检查单个组件性能"""
        try:
            comp_data = self.registered_components[component_name]
            component = comp_data['instance']
            thresholds = comp_data['thresholds']
            
            # 获取组件性能指标
            if hasattr(component, 'get_performance_metrics'):
                metrics = component.get_performance_metrics()
                
                for metric_name, metric_value in metrics.items():
                    if metric_name in thresholds:
                        threshold_config = thresholds[metric_name]
                        threshold_value = threshold_config['threshold']
                        
                        # 检查阈值
                        if isinstance(metric_value, (int, float)):
                            if metric_value > threshold_value:
                                logger.warning(
                                    f"组件 {component_name} 指标 {metric_name} "
                                    f"超出阈值: {metric_value} > {threshold_value}"
                                )
                                comp_data['status'] = 'degraded'
                            else:
                                comp_data['status'] = 'healthy'
            
        except Exception as e:
            logger.error(f"检查组件 {component_name} 性能失败: {str(e)}")

    def _auto_cache_cleanup(self):
        """自动缓存清理"""
        try:
            cleanup_results = []
            
            for comp_name, comp_data in self.registered_components.items():
                component = comp_data['instance']
                
                # 尝试清理组件缓存
                if hasattr(component, 'auto_cleanup'):
                    result = component.auto_cleanup()
                    if result:
                        cleanup_results.append(f"{comp_name}: {result}")
                elif hasattr(component, 'cleanup_cache'):
                    result = component.cleanup_cache(auto=True)
                    if result:
                        cleanup_results.append(f"{comp_name}: 清理缓存")
            
            if cleanup_results:
                logger.info(f"自动缓存清理: {'; '.join(cleanup_results)}")
            
        except Exception as e:
            logger.error(f"自动缓存清理失败: {str(e)}")

    def _generate_periodic_report(self):
        """生成定期性能报告"""
        try:
            # 获取基础性能报告
            base_report = self.performance_monitor.get_performance_report()
            
            # 添加组件特定信息
            component_details = {}
            for comp_name, comp_data in self.registered_components.items():
                component_details[comp_name] = {
                    'status': comp_data['status'],
                    'last_check': comp_data['last_check'],
                    'performance_history_length': len(comp_data['performance_history'])
                }
                
                # 获取组件特定指标
                component = comp_data['instance']
                if hasattr(component, 'get_performance_metrics'):
                    try:
                        metrics = component.get_performance_metrics()
                        component_details[comp_name]['current_metrics'] = metrics
                    except Exception:
                        pass
            
            # 整合报告
            integrated_report = {
                **base_report,
                'integration_info': {
                    'registered_components': list(self.registered_components.keys()),
                    'optimization_level': self.current_optimization_level,
                    'auto_optimization_enabled': self.auto_optimization_enabled,
                    'baseline_established': self.baseline_established,
                    'last_optimization_time': self.last_optimization_time
                },
                'component_details': component_details,
                'optimization_suggestions': self._generate_optimization_suggestions()
            }
            
            self.performance_report_ready.emit(integrated_report)
            
        except Exception as e:
            logger.error(f"生成定期报告失败: {str(e)}")

    def _generate_optimization_suggestions(self) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        try:
            # 基于组件状态生成建议
            degraded_components = [
                name for name, data in self.registered_components.items()
                if data['status'] == 'degraded'
            ]
            
            if degraded_components:
                suggestions.append(f"以下组件性能下降，建议检查: {', '.join(degraded_components)}")
            
            # 基于系统资源使用情况生成建议
            current_metrics = self.performance_monitor._get_current_system_metrics()
            
            if 'cpu_usage' in current_metrics:
                cpu_usage = current_metrics['cpu_usage']['value']
                if cpu_usage > 70:
                    suggestions.append(f"CPU使用率较高 ({cpu_usage:.1f}%)，建议降低并发任务数")
            
            if 'memory_usage' in current_metrics:
                memory_usage = current_metrics['memory_usage']['value']
                if memory_usage > 75:
                    suggestions.append(f"内存使用率较高 ({memory_usage:.1f}%)，建议清理缓存")
            
            # 基于优化级别生成建议
            if self.current_optimization_level == OptimizationLevel.CONSERVATIVE:
                suggestions.append("当前使用保守优化模式，可考虑切换到平衡模式以获得更好性能")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {str(e)}")
            return []

    def _update_component_status(self, metric):
        """更新组件状态"""
        try:
            component_name = metric.component
            if component_name in self.registered_components:
                comp_data = self.registered_components[component_name]
                
                # 记录性能历史
                comp_data['performance_history'].append({
                    'timestamp': metric.timestamp,
                    'metric_name': metric.name,
                    'value': metric.value
                })
                
                # 限制历史记录长度
                if len(comp_data['performance_history']) > 100:
                    comp_data['performance_history'] = comp_data['performance_history'][-100:]
            
        except Exception as e:
            logger.error(f"更新组件状态失败: {str(e)}")

    def _try_establish_baseline(self):
        """尝试建立性能基线"""
        try:
            # 需要足够的数据点来建立基线
            total_metrics = sum(len(comp_data['performance_history']) 
                              for comp_data in self.registered_components.values())
            
            if total_metrics >= 50:  # 需要至少50个数据点
                self.performance_baseline = self._calculate_performance_baseline()
                self.baseline_established = True
                logger.info("性能基线已建立")
            
        except Exception as e:
            logger.error(f"建立性能基线失败: {str(e)}")

    def _calculate_performance_baseline(self) -> Dict[str, Any]:
        """计算性能基线"""
        baseline = {}
        
        try:
            for comp_name, comp_data in self.registered_components.items():
                history = comp_data['performance_history']
                if not history:
                    continue
                
                # 按指标分组
                metrics_by_name = {}
                for record in history:
                    metric_name = record['metric_name']
                    if metric_name not in metrics_by_name:
                        metrics_by_name[metric_name] = []
                    metrics_by_name[metric_name].append(record['value'])
                
                # 计算基线统计
                comp_baseline = {}
                for metric_name, values in metrics_by_name.items():
                    if values:
                        comp_baseline[metric_name] = {
                            'mean': sum(values) / len(values),
                            'min': min(values),
                            'max': max(values),
                            'count': len(values)
                        }
                
                baseline[comp_name] = comp_baseline
            
            return baseline
            
        except Exception as e:
            logger.error(f"计算性能基线失败: {str(e)}")
            return {}

    def set_optimization_level(self, level: str):
        """设置优化级别"""
        try:
            if level in [OptimizationLevel.CONSERVATIVE, OptimizationLevel.BALANCED, OptimizationLevel.AGGRESSIVE]:
                old_level = self.current_optimization_level
                self.current_optimization_level = level
                
                # 应用相应的优化配置
                self._apply_optimization_level_config(level)
                
                logger.info(f"优化级别已更改: {old_level} -> {level}")
                
                # 通知状态变化
                self.performance_status_changed.emit({
                    'optimization_level': level,
                    'timestamp': time.time()
                })
            else:
                logger.warning(f"无效的优化级别: {level}")
                
        except Exception as e:
            logger.error(f"设置优化级别失败: {str(e)}")

    def _apply_optimization_level_config(self, level: str):
        """应用优化级别配置"""
        try:
            if level == OptimizationLevel.CONSERVATIVE:
                # 保守模式：低性能影响，高稳定性
                self.auto_optimization_config.update({
                    'cpu_threshold': 90.0,
                    'memory_threshold': 95.0,
                    'render_time_threshold': 100.0,
                })
                
            elif level == OptimizationLevel.BALANCED:
                # 平衡模式：中等性能优化
                self.auto_optimization_config.update({
                    'cpu_threshold': 80.0,
                    'memory_threshold': 85.0,
                    'render_time_threshold': 50.0,
                })
                
            elif level == OptimizationLevel.AGGRESSIVE:
                # 激进模式：最大性能优化
                self.auto_optimization_config.update({
                    'cpu_threshold': 60.0,
                    'memory_threshold': 70.0,
                    'render_time_threshold': 25.0,
                })
            
            # 更新性能监控器的阈值
            self.performance_monitor.configure_thresholds(
                cpu_usage_critical=self.auto_optimization_config['cpu_threshold'],
                memory_usage_critical=self.auto_optimization_config['memory_threshold']
            )
            
        except Exception as e:
            logger.error(f"应用优化级别配置失败: {str(e)}")

    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        try:
            return {
                'registered_components_count': len(self.registered_components),
                'monitoring_active': self.performance_monitor.monitoring_enabled,
                'optimization_level': self.current_optimization_level,
                'auto_optimization_enabled': self.auto_optimization_enabled,
                'baseline_established': self.baseline_established,
                'component_status': {
                    name: data['status'] 
                    for name, data in self.registered_components.items()
                },
                'active_alerts_count': len(self.performance_monitor.active_alerts),
                'last_optimization_time': self.last_optimization_time
            }
        except Exception as e:
            logger.error(f"获取集成状态失败: {str(e)}")
            return {}

    def manual_optimize(self, target_component: Optional[str] = None) -> bool:
        """手动触发优化"""
        try:
            if target_component:
                # 优化特定组件
                if target_component in self.registered_components:
                    return self._optimize_specific_component(target_component)
                else:
                    logger.warning(f"组件 {target_component} 未注册")
                    return False
            else:
                # 全局优化
                optimizations_applied = 0
                
                # 尝试各种优化策略
                if self._optimize_cpu_usage():
                    optimizations_applied += 1
                if self._optimize_memory_usage():
                    optimizations_applied += 1
                if self._optimize_rendering():
                    optimizations_applied += 1
                if self._optimize_cache_settings():
                    optimizations_applied += 1
                
                if optimizations_applied > 0:
                    self.last_optimization_time = time.time()
                    self.optimization_applied.emit('manual_global', {
                        'optimizations_count': optimizations_applied,
                        'timestamp': time.time()
                    })
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"手动优化失败: {str(e)}")
            return False

    def _optimize_specific_component(self, component_name: str) -> bool:
        """优化特定组件"""
        try:
            comp_data = self.registered_components[component_name]
            component = comp_data['instance']
            
            # 尝试组件特定的优化方法
            optimization_applied = False
            
            if hasattr(component, 'optimize_performance'):
                component.optimize_performance()
                optimization_applied = True
            elif hasattr(component, 'cleanup_and_optimize'):
                component.cleanup_and_optimize()
                optimization_applied = True
            elif hasattr(component, 'reset_and_optimize'):
                component.reset_and_optimize()
                optimization_applied = True
            
            if optimization_applied:
                logger.info(f"组件 {component_name} 优化已应用")
                return True
            else:
                logger.info(f"组件 {component_name} 没有可用的优化方法")
                return False
                
        except Exception as e:
            logger.error(f"优化组件 {component_name} 失败: {str(e)}")
            return False

    def shutdown(self):
        """关闭性能监控集成管理器"""
        try:
            # 停止定时器
            self.optimization_timer.stop()
            self.report_timer.stop()
            
            # 停止性能监控
            self.performance_monitor.stop_monitoring()
            
            # 生成最终报告
            final_report = self.performance_monitor.get_performance_report()
            if final_report:
                logger.info("性能监控最终报告已生成")
            
            logger.info("性能监控集成管理器已关闭")
            
        except Exception as e:
            logger.error(f"关闭性能监控集成管理器失败: {str(e)}")