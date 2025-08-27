# -*- coding: utf-8 -*-
"""
后台任务管理器
用于管理和执行耗时的后台任务，避免阻塞UI主线程
"""

import time
import threading
import traceback
from typing import Any, Callable, Dict, List, Optional, Union
from queue import Queue, PriorityQueue, Empty
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future

try:
    from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
except ImportError:
    from PyQt4.QtCore import QObject, pyqtSignal, QTimer, QThread


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1     # 关键任务（如保存文件）
    HIGH = 2         # 高优先级（如用户直接操作）
    NORMAL = 3       # 正常优先级（如预加载）
    LOW = 4          # 低优先级（如统计计算）
    BACKGROUND = 5   # 后台任务（如缓存清理）


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 等待执行
    RUNNING = "running"        # 正在执行
    COMPLETED = "completed"    # 执行完成
    FAILED = "failed"          # 执行失败
    CANCELLED = "cancelled"    # 已取消


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None


@dataclass
class BackgroundTask:
    """后台任务定义"""
    task_id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None
    progress_callback: Optional[Callable] = None
    description: str = ""
    created_time: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.priority.value < other.priority.value


class TaskWorkerThread(QThread):
    """任务执行线程"""
    
    task_started = pyqtSignal(str)  # task_id
    task_completed = pyqtSignal(str, object)  # task_id, result
    task_failed = pyqtSignal(str, Exception)  # task_id, error
    task_progress = pyqtSignal(str, int, str)  # task_id, progress, message
    
    def __init__(self, task_queue: PriorityQueue, result_queue: Queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.current_task = None
        
    def run(self):
        """线程主循环"""
        while self.running:
            try:
                # 获取任务（带超时，避免阻塞）
                priority, task = self.task_queue.get(timeout=1.0)
                
                if not self.running:
                    break
                    
                self.current_task = task
                self._execute_task(task)
                
            except Empty:
                # 队列超时，这是正常的，继续下一次循环
                continue
            except Exception as e:
                if self.running:  # 只有在非正常关闭时才报错
                    print(f"[任务工作线程] 处理任务时出错: {type(e).__name__}: {e}")
                continue
                
    def _execute_task(self, task: BackgroundTask):
        """执行单个任务"""
        result = TaskResult(task.task_id, TaskStatus.RUNNING)
        result.start_time = time.time()
        
        try:
            self.task_started.emit(task.task_id)
            
            # 创建进度回调包装器
            def progress_wrapper(progress: int, message: str = ""):
                self.task_progress.emit(task.task_id, progress, message)
                if task.progress_callback:
                    task.progress_callback(progress, message)
            
            # 如果函数支持进度回调，则添加到kwargs中
            if 'progress_callback' in task.func.__code__.co_varnames:
                task.kwargs['progress_callback'] = progress_wrapper
            
            # 执行任务
            if task.timeout:
                # 带超时的执行
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(task.func, *task.args, **task.kwargs)
                    result.result = future.result(timeout=task.timeout)
            else:
                # 正常执行
                result.result = task.func(*task.args, **task.kwargs)
            
            result.status = TaskStatus.COMPLETED
            result.end_time = time.time()
            result.execution_time = result.end_time - result.start_time
            
            # 发送完成信号
            self.task_completed.emit(task.task_id, result.result)
            
            # 调用回调函数
            if task.callback:
                try:
                    task.callback(result.result)
                except Exception as cb_error:
                    print(f"[任务回调错误] 任务 {task.task_id} 回调函数执行失败:")
                    print(f"  错误类型: {type(cb_error).__name__}")
                    print(f"  错误信息: {cb_error}")
                    print(f"  堆栈跟踪: {traceback.format_exc()}")
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = e
            result.end_time = time.time()
            result.execution_time = result.end_time - result.start_time
            
            # 发送失败信号
            self.task_failed.emit(task.task_id, e)
            
            # 调用错误回调
            if task.error_callback:
                try:
                    task.error_callback(e)
                except Exception as cb_error:
                    print(f"[任务错误回调错误] 任务 {task.task_id} 错误回调函数执行失败:")
                    print(f"  错误类型: {type(cb_error).__name__}")
                    print(f"  错误信息: {cb_error}")
                    print(f"  堆栈跟踪: {traceback.format_exc()}")
            
            # 更详细的错误日志，包含堆栈跟踪
            error_details = {
                'task_id': task.task_id,
                'function': task.func.__name__ if hasattr(task.func, '__name__') else str(task.func),
                'args': str(task.args)[:200],  # 限制长度避免日志过长
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
            print(f"[任务执行错误] 任务 {task.task_id} 执行失败:")
            print(f"  函数: {error_details['function']}")
            print(f"  参数: {error_details['args']}")
            print(f"  错误类型: {error_details['error_type']}")
            print(f"  错误信息: {error_details['error_message']}")
            print(f"  堆栈跟踪: {error_details['traceback']}")
            
        finally:
            # 将结果放入结果队列
            self.result_queue.put(result)
            self.current_task = None
            
    def stop(self):
        """停止工作线程"""
        self.running = False
        self.quit()
        self.wait()


class BackgroundTaskManager(QObject):
    """
    后台任务管理器
    
    功能特性：
    - 优先级任务队列
    - 多线程任务执行
    - 任务进度跟踪
    - 超时控制
    - 任务取消
    - 性能监控
    """
    
    # 信号定义
    task_submitted = pyqtSignal(str, str)  # task_id, description
    task_started = pyqtSignal(str)  # task_id
    task_completed = pyqtSignal(str, object)  # task_id, result
    task_failed = pyqtSignal(str, Exception)  # task_id, error
    task_progress = pyqtSignal(str, int, str)  # task_id, progress, message
    queue_status_changed = pyqtSignal(int, int)  # pending_count, running_count
    
    def __init__(self, max_workers: int = 3):
        super().__init__()
        
        self.max_workers = max_workers
        self.task_queue = PriorityQueue()
        self.result_queue = Queue()
        
        # 任务跟踪
        self.pending_tasks: Dict[str, BackgroundTask] = {}
        self.running_tasks: Dict[str, BackgroundTask] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.task_counter = 0
        
        # 工作线程池
        self.workers: List[TaskWorkerThread] = []
        self._create_workers()
        
        # 结果处理定时器
        self.result_timer = QTimer()
        self.result_timer.timeout.connect(self._process_results)
        self.result_timer.start(100)  # 每100ms处理一次结果
        
        # 统计信息
        self.stats = {
            'total_submitted': 0,
            'total_completed': 0,
            'total_failed': 0,
            'total_cancelled': 0,
            'avg_execution_time': 0.0,
            'tasks_by_priority': {p: 0 for p in TaskPriority}
        }
        
        print(f"[后台任务管理器] 初始化完成，工作线程数: {max_workers}")
        
    def _create_workers(self):
        """创建工作线程"""
        for i in range(self.max_workers):
            worker = TaskWorkerThread(self.task_queue, self.result_queue)
            worker.task_started.connect(self._on_task_started)
            worker.task_completed.connect(self._on_task_completed)
            worker.task_failed.connect(self._on_task_failed)
            worker.task_progress.connect(self._on_task_progress)
            worker.start()
            self.workers.append(worker)
            
    def submit_task(self, 
                   func: Callable,
                   args: tuple = (),
                   kwargs: dict = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   timeout: Optional[float] = None,
                   callback: Optional[Callable] = None,
                   error_callback: Optional[Callable] = None,
                   progress_callback: Optional[Callable] = None,
                   description: str = "",
                   task_id: Optional[str] = None) -> str:
        """
        提交后台任务
        
        Args:
            func: 要执行的函数
            args: 函数参数
            kwargs: 函数关键字参数
            priority: 任务优先级
            timeout: 超时时间（秒）
            callback: 成功回调函数
            error_callback: 错误回调函数
            progress_callback: 进度回调函数
            description: 任务描述
            task_id: 自定义任务ID
            
        Returns:
            任务ID
        """
        if kwargs is None:
            kwargs = {}
            
        # 生成任务ID
        if task_id is None:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}_{int(time.time())}"
        
        # 创建任务
        task = BackgroundTask(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            callback=callback,
            error_callback=error_callback,
            progress_callback=progress_callback,
            description=description or func.__name__
        )
        
        # 添加到待执行队列
        self.pending_tasks[task_id] = task
        self.task_queue.put((priority.value, task))
        
        # 更新统计
        self.stats['total_submitted'] += 1
        self.stats['tasks_by_priority'][priority] += 1
        
        # 发送信号
        self.task_submitted.emit(task_id, task.description)
        self._emit_queue_status()
        
        print(f"[任务提交] {task_id}: {task.description} (优先级: {priority.name})")
        return task_id
        
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        # 如果任务还在待执行队列中
        if task_id in self.pending_tasks:
            del self.pending_tasks[task_id]
            self.stats['total_cancelled'] += 1
            print(f"[任务取消] 成功取消待执行任务: {task_id}")
            self._emit_queue_status()
            return True
            
        # 如果任务正在执行，则比较难取消（需要线程协作）
        if task_id in self.running_tasks:
            print(f"[任务取消] 任务 {task_id} 正在执行，无法直接取消")
            return False
            
        print(f"[任务取消] 任务 {task_id} 不存在或已完成")
        return False
        
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self.pending_tasks:
            return TaskStatus.PENDING
        elif task_id in self.running_tasks:
            return TaskStatus.RUNNING
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        else:
            return None
            
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self.completed_tasks.get(task_id)
        
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            任务结果
        """
        start_time = time.time()
        
        while True:
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id]
                
            if timeout and (time.time() - start_time) > timeout:
                break
                
            time.sleep(0.1)
            
        return None
        
    def get_queue_status(self) -> Dict[str, int]:
        """获取队列状态"""
        return {
            'pending': len(self.pending_tasks),
            'running': len(self.running_tasks),
            'completed': len(self.completed_tasks)
        }
        
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 计算平均执行时间
        if self.completed_tasks:
            total_time = sum(r.execution_time for r in self.completed_tasks.values() 
                           if r.execution_time > 0)
            completed_count = len([r for r in self.completed_tasks.values() 
                                 if r.status == TaskStatus.COMPLETED])
            if completed_count > 0:
                stats['avg_execution_time'] = total_time / completed_count
                
        # 添加队列状态
        stats.update(self.get_queue_status())
        
        return stats
        
    def clear_completed_tasks(self, max_keep: int = 100):
        """清理已完成的任务记录"""
        if len(self.completed_tasks) <= max_keep:
            return
            
        # 按完成时间排序，保留最新的
        sorted_tasks = sorted(
            self.completed_tasks.items(),
            key=lambda x: x[1].end_time or 0,
            reverse=True
        )
        
        # 保留最新的max_keep个任务
        keep_tasks = dict(sorted_tasks[:max_keep])
        removed_count = len(self.completed_tasks) - len(keep_tasks)
        
        self.completed_tasks = keep_tasks
        print(f"[任务清理] 清理了 {removed_count} 个已完成的任务记录")
        
    def _process_results(self):
        """处理任务结果"""
        while not self.result_queue.empty():
            try:
                result = self.result_queue.get_nowait()
                self.completed_tasks[result.task_id] = result
                
                # 从运行队列移除
                if result.task_id in self.running_tasks:
                    del self.running_tasks[result.task_id]
                    
                # 更新统计
                if result.status == TaskStatus.COMPLETED:
                    self.stats['total_completed'] += 1
                elif result.status == TaskStatus.FAILED:
                    self.stats['total_failed'] += 1
                    
                self._emit_queue_status()
                
            except Exception as e:
                print(f"[结果处理错误] 处理任务结果时出错: {e}")
                break
                
    def _on_task_started(self, task_id: str):
        """任务开始回调"""
        if task_id in self.pending_tasks:
            task = self.pending_tasks[task_id]
            self.running_tasks[task_id] = task
            del self.pending_tasks[task_id]
            
        self.task_started.emit(task_id)
        self._emit_queue_status()
        
    def _on_task_completed(self, task_id: str, result: Any):
        """任务完成回调"""
        self.task_completed.emit(task_id, result)
        
    def _on_task_failed(self, task_id: str, error: Exception):
        """任务失败回调"""
        self.task_failed.emit(task_id, error)
        
    def _on_task_progress(self, task_id: str, progress: int, message: str):
        """任务进度回调"""
        self.task_progress.emit(task_id, progress, message)
        
    def _emit_queue_status(self):
        """发送队列状态信号"""
        self.queue_status_changed.emit(len(self.pending_tasks), len(self.running_tasks))
        
    def shutdown(self):
        """关闭任务管理器"""
        print("[后台任务管理器] 开始关闭...")
        
        # 停止结果处理定时器
        self.result_timer.stop()
        
        # 停止所有工作线程
        for worker in self.workers:
            worker.stop()
            
        # 清空队列
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except:
                break
                
        print("[后台任务管理器] 关闭完成")


# 便利函数
def run_in_background(func: Callable,
                     args: tuple = (),
                     kwargs: dict = None,
                     priority: TaskPriority = TaskPriority.NORMAL,
                     **task_options) -> str:
    """
    便利函数：在后台运行函数
    
    需要在应用中设置全局的后台任务管理器实例
    """
    # 这个函数需要配合应用中的全局task_manager使用
    # 具体实现需要在主窗口中设置
    pass