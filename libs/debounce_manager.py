# -*- coding: utf-8 -*-
"""
防抖管理器
用于优化频繁触发的操作，减少不必要的更新
"""

import time
from typing import Dict, Callable, Any, Optional
from enum import Enum

try:
    from PyQt5.QtCore import QTimer, QObject, pyqtSignal
except ImportError:
    from PyQt4.QtCore import QTimer, QObject, pyqtSignal


class DebounceStrategy(Enum):
    """防抖策略"""
    LEADING = "leading"      # 立即执行，然后防抖
    TRAILING = "trailing"    # 延迟执行（默认）
    BOTH = "both"           # 首次立即执行，后续延迟执行


class DebounceEntry:
    """防抖条目"""
    
    def __init__(self, func: Callable, delay: int, strategy: DebounceStrategy):
        self.func = func
        self.delay = delay
        self.strategy = strategy
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.last_call_time = 0
        self.is_first_call = True
        self.pending_args = None
        self.pending_kwargs = None
        
        # 连接定时器信号
        self.timer.timeout.connect(self._execute_trailing)
        
    def call(self, *args, **kwargs):
        """执行防抖调用"""
        current_time = time.time()
        self.last_call_time = current_time
        self.pending_args = args
        self.pending_kwargs = kwargs
        
        if self.strategy == DebounceStrategy.LEADING:
            if self.is_first_call:
                self._execute_now()
                self.is_first_call = False
            self.timer.start(self.delay)
            
        elif self.strategy == DebounceStrategy.TRAILING:
            self.timer.start(self.delay)
            
        elif self.strategy == DebounceStrategy.BOTH:
            if self.is_first_call:
                self._execute_now()
                self.is_first_call = False
            self.timer.start(self.delay)
            
    def _execute_now(self):
        """立即执行函数"""
        try:
            if self.pending_args is not None or self.pending_kwargs is not None:
                self.func(*(self.pending_args or ()), **(self.pending_kwargs or {}))
            else:
                self.func()
        except Exception as e:
            print(f"[防抖执行错误] 立即执行函数时出错: {e}")
            
    def _execute_trailing(self):
        """延迟执行函数"""
        try:
            if self.pending_args is not None or self.pending_kwargs is not None:
                self.func(*(self.pending_args or ()), **(self.pending_kwargs or {}))
            else:
                self.func()
            # 重置首次调用标记
            self.is_first_call = True
        except Exception as e:
            print(f"[防抖执行错误] 延迟执行函数时出错: {e}")
            
    def cancel(self):
        """取消待执行的调用"""
        self.timer.stop()
        self.is_first_call = True
        
    def flush(self):
        """立即执行待执行的调用"""
        if self.timer.isActive():
            self.timer.stop()
            self._execute_trailing()


class DebounceManager(QObject):
    """
    防抖管理器
    
    功能特性：
    - 多种防抖策略
    - 智能延迟调整
    - 性能监控
    - 批量管理
    """
    
    # 信号定义
    function_executed = pyqtSignal(str, float)  # function_name, execution_time
    
    def __init__(self):
        super().__init__()
        
        # 防抖条目存储
        self.entries: Dict[str, DebounceEntry] = {}
        
        # 统计信息
        self.stats = {
            'total_calls': 0,
            'debounced_calls': 0,
            'executed_calls': 0,
            'functions': {}
        }
        
        # 默认配置
        self.default_delay = 100  # 默认延迟100ms
        self.default_strategy = DebounceStrategy.TRAILING
        
        print("[防抖管理器] 初始化完成")
        
    def debounce(self, 
                func: Callable,
                delay: Optional[int] = None,
                strategy: DebounceStrategy = None,
                key: Optional[str] = None) -> Callable:
        """
        创建防抖函数
        
        Args:
            func: 要防抖的函数
            delay: 延迟时间（毫秒）
            strategy: 防抖策略
            key: 自定义键名
            
        Returns:
            防抖后的函数
        """
        if delay is None:
            delay = self.default_delay
        if strategy is None:
            strategy = self.default_strategy
        if key is None:
            key = f"{func.__module__}.{func.__name__}"
            
        # 创建防抖条目
        entry = DebounceEntry(func, delay, strategy)
        self.entries[key] = entry
        
        # 初始化统计
        if key not in self.stats['functions']:
            self.stats['functions'][key] = {
                'total_calls': 0,
                'executed_calls': 0,
                'avg_execution_time': 0.0
            }
        
        def debounced_func(*args, **kwargs):
            # 更新统计
            self.stats['total_calls'] += 1
            self.stats['functions'][key]['total_calls'] += 1
            
            # 记录执行时间
            start_time = time.time()
            
            # 包装原函数以记录执行统计
            original_func = entry.func
            def wrapped_func(*f_args, **f_kwargs):
                result = original_func(*f_args, **f_kwargs)
                execution_time = time.time() - start_time
                self._update_execution_stats(key, execution_time)
                self.function_executed.emit(key, execution_time)
                return result
            
            # 临时替换函数
            entry.func = wrapped_func
            entry.call(*args, **kwargs)
            entry.func = original_func  # 恢复原函数
            
        return debounced_func
        
    def create_status_bar_debouncer(self, update_func: Callable, delay: int = 50) -> Callable:
        """
        创建专门用于状态栏更新的防抖器
        
        Args:
            update_func: 状态栏更新函数
            delay: 延迟时间（毫秒）
            
        Returns:
            防抖后的更新函数
        """
        return self.debounce(
            func=update_func,
            delay=delay,
            strategy=DebounceStrategy.TRAILING,
            key="status_bar_update"
        )
        
    def create_canvas_render_debouncer(self, render_func: Callable, delay: int = 16) -> Callable:
        """
        创建专门用于Canvas渲染的防抖器（60FPS = 16ms）
        
        Args:
            render_func: 渲染函数
            delay: 延迟时间（毫秒）
            
        Returns:
            防抖后的渲染函数
        """
        return self.debounce(
            func=render_func,
            delay=delay,
            strategy=DebounceStrategy.LEADING,
            key="canvas_render"
        )
        
    def create_file_operation_debouncer(self, operation_func: Callable, delay: int = 200) -> Callable:
        """
        创建专门用于文件操作的防抖器
        
        Args:
            operation_func: 文件操作函数
            delay: 延迟时间（毫秒）
            
        Returns:
            防抖后的操作函数
        """
        return self.debounce(
            func=operation_func,
            delay=delay,
            strategy=DebounceStrategy.TRAILING,
            key="file_operation"
        )
        
    def create_search_debouncer(self, search_func: Callable, delay: int = 300) -> Callable:
        """
        创建专门用于搜索的防抖器
        
        Args:
            search_func: 搜索函数
            delay: 延迟时间（毫秒）
            
        Returns:
            防抖后的搜索函数
        """
        return self.debounce(
            func=search_func,
            delay=delay,
            strategy=DebounceStrategy.TRAILING,
            key="search_operation"
        )
        
    def cancel(self, key: str):
        """取消指定防抖函数的待执行调用"""
        if key in self.entries:
            self.entries[key].cancel()
            
    def cancel_all(self):
        """取消所有待执行的调用"""
        for entry in self.entries.values():
            entry.cancel()
            
    def flush(self, key: str):
        """立即执行指定防抖函数的待执行调用"""
        if key in self.entries:
            self.entries[key].flush()
            
    def flush_all(self):
        """立即执行所有待执行的调用"""
        for entry in self.entries.values():
            entry.flush()
            
    def set_delay(self, key: str, delay: int):
        """设置指定防抖函数的延迟时间"""
        if key in self.entries:
            self.entries[key].delay = delay
            
    def remove(self, key: str):
        """移除防抖函数"""
        if key in self.entries:
            self.entries[key].cancel()
            del self.entries[key]
            
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 计算防抖率
        if stats['total_calls'] > 0:
            stats['debounce_rate'] = (stats['total_calls'] - stats['executed_calls']) / stats['total_calls']
        else:
            stats['debounce_rate'] = 0.0
            
        # 添加活跃防抖器数量
        stats['active_debouncers'] = len([e for e in self.entries.values() if e.timer.isActive()])
        stats['total_debouncers'] = len(self.entries)
        
        return stats
        
    def _update_execution_stats(self, key: str, execution_time: float):
        """更新执行统计信息"""
        self.stats['executed_calls'] += 1
        
        if key in self.stats['functions']:
            func_stats = self.stats['functions'][key]
            func_stats['executed_calls'] += 1
            
            # 计算平均执行时间（滑动平均）
            if func_stats['avg_execution_time'] == 0:
                func_stats['avg_execution_time'] = execution_time
            else:
                alpha = 0.1
                func_stats['avg_execution_time'] = (
                    alpha * execution_time + 
                    (1 - alpha) * func_stats['avg_execution_time']
                )
                
    def optimize_delays(self):
        """
        根据历史执行时间自动优化延迟设置
        """
        for key, func_stats in self.stats['functions'].items():
            if key in self.entries and func_stats['executed_calls'] > 10:
                avg_time = func_stats['avg_execution_time']
                
                # 根据平均执行时间调整延迟
                if avg_time > 0.1:  # 执行时间超过100ms
                    new_delay = max(200, int(avg_time * 1000 * 2))
                elif avg_time > 0.05:  # 执行时间超过50ms
                    new_delay = max(100, int(avg_time * 1000 * 1.5))
                else:
                    new_delay = max(50, int(avg_time * 1000))
                    
                # 限制最大延迟
                new_delay = min(new_delay, 1000)
                
                if self.entries[key].delay != new_delay:
                    print(f"[防抖优化] {key}: {self.entries[key].delay}ms -> {new_delay}ms")
                    self.entries[key].delay = new_delay
                    
    def clear_stats(self):
        """清空统计信息"""
        self.stats = {
            'total_calls': 0,
            'debounced_calls': 0,
            'executed_calls': 0,
            'functions': {}
        }
        
    def shutdown(self):
        """关闭防抖管理器"""
        print("[防抖管理器] 开始关闭...")
        
        # 取消所有待执行的调用
        self.cancel_all()
        
        # 清空条目
        self.entries.clear()
        
        print("[防抖管理器] 关闭完成")


# 全局防抖管理器实例（可选）
_global_debounce_manager = None

def get_global_debounce_manager() -> DebounceManager:
    """获取全局防抖管理器实例"""
    global _global_debounce_manager
    if _global_debounce_manager is None:
        _global_debounce_manager = DebounceManager()
    return _global_debounce_manager


# 便利装饰器
def debounce(delay: int = 100, strategy: DebounceStrategy = DebounceStrategy.TRAILING):
    """
    防抖装饰器
    
    Args:
        delay: 延迟时间（毫秒）
        strategy: 防抖策略
    """
    def decorator(func):
        manager = get_global_debounce_manager()
        return manager.debounce(func, delay, strategy)
    return decorator