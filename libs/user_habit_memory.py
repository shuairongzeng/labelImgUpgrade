# -*- coding: utf-8 -*-
"""
用户操作习惯记忆系统

主要功能：
1. 操作模式学习 - 学习用户的标注模式和偏好
2. 工作流优化 - 基于习惯优化工作流程
3. 智能预测 - 预测用户接下来可能的操作
4. 个性化建议 - 提供个性化的工具建议
5. 适应性界面 - 根据使用习惯调整界面布局
"""

import json
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from .logger_config import get_logger

logger = get_logger(__name__)


class OperationType(Enum):
    """操作类型"""
    ANNOTATION = "annotation"       # 标注操作
    NAVIGATION = "navigation"       # 导航操作  
    EDITING = "editing"            # 编辑操作
    VIEW = "view"                  # 视图操作
    FILE = "file"                  # 文件操作
    TOOL = "tool"                  # 工具操作


class WorkflowPattern(Enum):
    """工作流模式"""
    SEQUENTIAL = "sequential"       # 顺序标注
    RANDOM = "random"              # 随机标注
    BATCH_FOCUSED = "batch_focused" # 批量处理为主
    DETAIL_FOCUSED = "detail_focused" # 精细标注为主
    MIXED = "mixed"                # 混合模式


@dataclass
class OperationRecord:
    """操作记录"""
    timestamp: float
    operation_type: OperationType
    action: str
    context: Dict[str, Any]
    duration: float = 0.0
    success: bool = True


@dataclass
class HabitPattern:
    """习惯模式"""
    pattern_id: str
    description: str
    frequency: float
    confidence: float
    last_occurrence: float
    triggers: List[str]
    actions: List[str]
    context_requirements: Dict[str, Any]


@dataclass
class UserPreference:
    """用户偏好"""
    preference_id: str
    category: str
    value: Any
    confidence: float
    learning_sessions: int
    last_updated: float


class UserHabitMemory(QObject):
    """用户习惯记忆系统"""
    
    # 信号定义
    habit_learned = pyqtSignal(dict)      # 学到新习惯
    prediction_ready = pyqtSignal(dict)   # 预测就绪
    preference_updated = pyqtSignal(dict) # 偏好更新
    workflow_detected = pyqtSignal(str)   # 工作流检测

    def __init__(self, memory_file: str = "config/user_habits.json"):
        super().__init__()
        
        self.memory_file = memory_file
        
        # 操作历史记录
        self.operation_history = deque(maxlen=1000)  # 保留最近1000个操作
        self.session_operations = []  # 当前会话操作
        
        # 习惯模式
        self.habit_patterns: Dict[str, HabitPattern] = {}
        
        # 用户偏好
        self.user_preferences: Dict[str, UserPreference] = {}
        
        # 学习配置
        self.learning_config = {
            'min_pattern_frequency': 3,      # 最小模式频率
            'pattern_confidence_threshold': 0.7,  # 模式置信度阈值
            'session_timeout': 1800,        # 会话超时（30分钟）
            'habit_decay_rate': 0.95,       # 习惯衰减率
            'learning_rate': 0.1,           # 学习率
            'prediction_window': 5,         # 预测窗口大小
        }
        
        # 当前会话信息
        self.session_start_time = time.time()
        self.current_workflow = WorkflowPattern.MIXED
        self.last_operation_time = time.time()
        
        # 预测缓存
        self.prediction_cache = {}
        self.last_prediction_time = 0
        
        # 加载已保存的习惯数据
        self.load_memory()
        
        # 定期分析和学习
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.periodic_analysis)
        self.analysis_timer.start(60000)  # 每分钟分析一次
        
        # 会话保存定时器
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_memory)
        self.save_timer.start(300000)  # 每5分钟保存一次

    def record_operation(self, operation_type: OperationType, action: str, 
                        context: Dict[str, Any] = None, duration: float = 0.0, 
                        success: bool = True):
        """记录用户操作"""
        try:
            current_time = time.time()
            
            operation = OperationRecord(
                timestamp=current_time,
                operation_type=operation_type,
                action=action,
                context=context or {},
                duration=duration,
                success=success
            )
            
            # 添加到历史记录
            self.operation_history.append(operation)
            self.session_operations.append(operation)
            
            # 更新最后操作时间
            self.last_operation_time = current_time
            
            logger.debug(f"记录操作: {operation_type.value}/{action}")
            
            # 实时学习（简单模式）
            self._quick_learning_update(operation)
            
        except Exception as e:
            logger.error(f"记录操作失败: {str(e)}")

    def _quick_learning_update(self, operation: OperationRecord):
        """快速学习更新"""
        try:
            # 更新操作频率偏好
            pref_id = f"action_frequency_{operation.action}"
            if pref_id in self.user_preferences:
                pref = self.user_preferences[pref_id]
                pref.value = pref.value + 1
                pref.last_updated = operation.timestamp
                pref.learning_sessions += 1
            else:
                self.user_preferences[pref_id] = UserPreference(
                    preference_id=pref_id,
                    category="action_frequency",
                    value=1,
                    confidence=0.5,
                    learning_sessions=1,
                    last_updated=operation.timestamp
                )
            
            # 检测简单的顺序模式
            if len(self.operation_history) >= 2:
                prev_op = self.operation_history[-2]
                pattern_id = f"sequence_{prev_op.action}_{operation.action}"
                
                if pattern_id in self.habit_patterns:
                    pattern = self.habit_patterns[pattern_id]
                    pattern.frequency += 1
                    pattern.last_occurrence = operation.timestamp
                    pattern.confidence = min(0.95, pattern.confidence + 0.05)
                else:
                    # 创建新的顺序模式
                    self.habit_patterns[pattern_id] = HabitPattern(
                        pattern_id=pattern_id,
                        description=f"从 {prev_op.action} 到 {operation.action}",
                        frequency=1,
                        confidence=0.3,
                        last_occurrence=operation.timestamp,
                        triggers=[prev_op.action],
                        actions=[operation.action],
                        context_requirements={}
                    )
            
        except Exception as e:
            logger.error(f"快速学习更新失败: {str(e)}")

    def predict_next_action(self, current_context: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """预测下一个可能的操作"""
        try:
            current_time = time.time()
            
            # 检查预测缓存
            if (current_time - self.last_prediction_time < 5 and 
                self.prediction_cache):
                return self.prediction_cache.get('predictions', [])
            
            predictions = []
            current_context = current_context or {}
            
            # 基于最近操作预测
            if self.operation_history:
                recent_ops = list(self.operation_history)[-self.learning_config['prediction_window']:]
                
                # 基于习惯模式预测
                for pattern in self.habit_patterns.values():
                    if pattern.confidence > self.learning_config['pattern_confidence_threshold']:
                        match_score = self._calculate_pattern_match(pattern, recent_ops, current_context)
                        if match_score > 0.5:
                            for action in pattern.actions:
                                predictions.append((action, match_score * pattern.confidence))
                
                # 基于频率预测
                action_frequencies = defaultdict(int)
                for op in recent_ops:
                    action_frequencies[op.action] += 1
                
                # 归一化频率
                total_ops = len(recent_ops)
                for action, freq in action_frequencies.items():
                    freq_score = freq / total_ops * 0.7  # 频率权重
                    predictions.append((action, freq_score))
            
            # 合并和排序预测
            action_scores = defaultdict(float)
            for action, score in predictions:
                action_scores[action] = max(action_scores[action], score)
            
            final_predictions = sorted(
                [(action, score) for action, score in action_scores.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]  # 返回前5个预测
            
            # 缓存预测结果
            self.prediction_cache = {
                'predictions': final_predictions,
                'timestamp': current_time
            }
            self.last_prediction_time = current_time
            
            if final_predictions:
                logger.debug(f"预测下一操作: {final_predictions[0][0]} (置信度: {final_predictions[0][1]:.2f})")
                self.prediction_ready.emit({
                    'predictions': final_predictions,
                    'context': current_context
                })
            
            return final_predictions
            
        except Exception as e:
            logger.error(f"预测下一操作失败: {str(e)}")
            return []

    def _calculate_pattern_match(self, pattern: HabitPattern, recent_ops: List[OperationRecord], 
                                context: Dict[str, Any]) -> float:
        """计算模式匹配度"""
        try:
            if not recent_ops or not pattern.triggers:
                return 0.0
            
            match_score = 0.0
            
            # 检查触发条件
            recent_actions = [op.action for op in recent_ops[-len(pattern.triggers):]]
            
            # 计算触发序列匹配度
            if len(recent_actions) >= len(pattern.triggers):
                matching_triggers = 0
                for i, trigger in enumerate(pattern.triggers):
                    if i < len(recent_actions) and recent_actions[-(len(pattern.triggers)-i)] == trigger:
                        matching_triggers += 1
                
                trigger_match = matching_triggers / len(pattern.triggers)
                match_score += trigger_match * 0.7
            
            # 检查上下文匹配
            context_match = self._calculate_context_match(pattern.context_requirements, context)
            match_score += context_match * 0.3
            
            # 时间衰减因子
            time_since_last = time.time() - pattern.last_occurrence
            time_decay = max(0.1, 1.0 - (time_since_last / 86400))  # 24小时衰减
            match_score *= time_decay
            
            return min(1.0, match_score)
            
        except Exception as e:
            logger.error(f"计算模式匹配度失败: {str(e)}")
            return 0.0

    def _calculate_context_match(self, required_context: Dict[str, Any], 
                               current_context: Dict[str, Any]) -> float:
        """计算上下文匹配度"""
        try:
            if not required_context:
                return 1.0
            
            if not current_context:
                return 0.0
            
            matches = 0
            total_requirements = len(required_context)
            
            for key, required_value in required_context.items():
                if key in current_context:
                    current_value = current_context[key]
                    if isinstance(required_value, (int, float)) and isinstance(current_value, (int, float)):
                        # 数值类型：计算相似度
                        if required_value == 0:
                            similarity = 1.0 if current_value == 0 else 0.0
                        else:
                            similarity = 1.0 - abs(required_value - current_value) / abs(required_value)
                            similarity = max(0.0, similarity)
                        matches += similarity
                    elif required_value == current_value:
                        matches += 1.0
                    else:
                        # 部分匹配检查
                        if isinstance(required_value, str) and isinstance(current_value, str):
                            if required_value.lower() in current_value.lower():
                                matches += 0.5
            
            return matches / total_requirements if total_requirements > 0 else 0.0
            
        except Exception as e:
            logger.error(f"计算上下文匹配度失败: {str(e)}")
            return 0.0

    def detect_workflow_pattern(self) -> WorkflowPattern:
        """检测工作流模式"""
        try:
            if len(self.session_operations) < 10:
                return WorkflowPattern.MIXED
            
            recent_ops = self.session_operations[-20:]  # 最近20个操作
            
            # 分析操作类型分布
            type_counts = defaultdict(int)
            for op in recent_ops:
                type_counts[op.operation_type] += 1
            
            # 分析操作顺序
            navigation_ops = sum(1 for op in recent_ops if op.operation_type == OperationType.NAVIGATION)
            annotation_ops = sum(1 for op in recent_ops if op.operation_type == OperationType.ANNOTATION)
            
            # 检测顺序模式
            navigation_ratio = navigation_ops / len(recent_ops)
            annotation_ratio = annotation_ops / len(recent_ops)
            
            # 分析操作间隔
            intervals = []
            for i in range(1, len(recent_ops)):
                interval = recent_ops[i].timestamp - recent_ops[i-1].timestamp
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            
            # 判断工作流模式
            if navigation_ratio > 0.3 and avg_interval < 5:
                pattern = WorkflowPattern.SEQUENTIAL
            elif annotation_ratio > 0.6 and avg_interval > 10:
                pattern = WorkflowPattern.DETAIL_FOCUSED
            elif 'batch' in str([op.action for op in recent_ops]):
                pattern = WorkflowPattern.BATCH_FOCUSED
            elif navigation_ratio < 0.1:
                pattern = WorkflowPattern.DETAIL_FOCUSED
            else:
                pattern = WorkflowPattern.MIXED
            
            # 更新当前工作流（如果发生变化）
            if pattern != self.current_workflow:
                self.current_workflow = pattern
                logger.info(f"检测到工作流模式变化: {pattern.value}")
                self.workflow_detected.emit(pattern.value)
            
            return pattern
            
        except Exception as e:
            logger.error(f"检测工作流模式失败: {str(e)}")
            return WorkflowPattern.MIXED

    def get_personalized_suggestions(self, current_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取个性化建议"""
        try:
            suggestions = []
            current_context = current_context or {}
            
            # 基于使用频率的工具建议
            tool_usage = defaultdict(int)
            for op in self.operation_history:
                if op.operation_type == OperationType.TOOL:
                    tool_usage[op.action] += 1
            
            # 获取最常用的工具
            top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for tool, usage_count in top_tools:
                suggestions.append({
                    'type': 'tool_suggestion',
                    'action': tool,
                    'reason': f'您经常使用此工具 ({usage_count} 次)',
                    'confidence': min(0.9, usage_count / 50),
                    'priority': 1
                })
            
            # 基于工作流的建议
            workflow = self.detect_workflow_pattern()
            if workflow == WorkflowPattern.SEQUENTIAL:
                suggestions.append({
                    'type': 'workflow_suggestion',
                    'action': 'enable_auto_next',
                    'reason': '检测到您倾向于顺序标注，建议启用自动下一张',
                    'confidence': 0.8,
                    'priority': 2
                })
            elif workflow == WorkflowPattern.BATCH_FOCUSED:
                suggestions.append({
                    'type': 'workflow_suggestion',
                    'action': 'show_batch_panel',
                    'reason': '检测到您经常使用批量操作，建议显示批量操作面板',
                    'confidence': 0.8,
                    'priority': 2
                })
            
            # 基于时间模式的建议
            current_hour = time.localtime().tm_hour
            if 9 <= current_hour <= 11 or 14 <= current_hour <= 16:
                # 工作时间
                suggestions.append({
                    'type': 'efficiency_suggestion',
                    'action': 'enable_shortcuts',
                    'reason': '当前为高效工作时段，建议启用更多快捷键',
                    'confidence': 0.6,
                    'priority': 3
                })
            
            # 按优先级和置信度排序
            suggestions.sort(key=lambda x: (x['priority'], -x['confidence']))
            
            return suggestions[:5]  # 返回前5个建议
            
        except Exception as e:
            logger.error(f"获取个性化建议失败: {str(e)}")
            return []

    def adapt_interface_layout(self) -> Dict[str, Any]:
        """自适应界面布局建议"""
        try:
            adaptations = {}
            
            # 分析面板使用频率
            panel_usage = defaultdict(int)
            for op in self.operation_history:
                if 'panel' in op.context:
                    panel_usage[op.context['panel']] += 1
            
            # 建议显示/隐藏面板
            if panel_usage.get('ai_panel', 0) > 10:
                adaptations['ai_panel_visible'] = True
            
            if panel_usage.get('batch_panel', 0) > 5:
                adaptations['batch_panel_visible'] = True
            
            # 分析工具栏使用
            toolbar_usage = defaultdict(int)
            for op in self.operation_history:
                if op.operation_type == OperationType.TOOL:
                    toolbar_usage[op.action] += 1
            
            # 建议工具栏布局
            if toolbar_usage:
                most_used_tools = sorted(toolbar_usage.items(), key=lambda x: x[1], reverse=True)[:8]
                adaptations['preferred_toolbar_tools'] = [tool for tool, _ in most_used_tools]
            
            # 分析缩放偏好
            zoom_ops = [op for op in self.operation_history if 'zoom' in op.action]
            if zoom_ops:
                # 计算平均缩放使用
                zoom_types = defaultdict(int)
                for op in zoom_ops:
                    zoom_types[op.action] += 1
                
                if zoom_types.get('zoom_fit', 0) > zoom_types.get('zoom_original', 0):
                    adaptations['default_zoom_mode'] = 'fit_window'
                else:
                    adaptations['default_zoom_mode'] = 'original'
            
            return adaptations
            
        except Exception as e:
            logger.error(f"自适应界面布局失败: {str(e)}")
            return {}

    def periodic_analysis(self):
        """定期分析和学习"""
        try:
            current_time = time.time()
            
            # 检查会话是否超时
            if current_time - self.last_operation_time > self.learning_config['session_timeout']:
                self._end_session_analysis()
                self._start_new_session()
            
            # 深度学习分析（每10分钟一次）
            if hasattr(self, '_last_deep_analysis'):
                if current_time - self._last_deep_analysis > 600:
                    self._deep_pattern_analysis()
                    self._last_deep_analysis = current_time
            else:
                self._last_deep_analysis = current_time
            
            # 习惯衰减
            self._apply_habit_decay()
            
        except Exception as e:
            logger.error(f"定期分析失败: {str(e)}")

    def _end_session_analysis(self):
        """会话结束分析"""
        try:
            if len(self.session_operations) < 5:
                return
            
            session_duration = time.time() - self.session_start_time
            
            # 分析会话模式
            workflow = self.detect_workflow_pattern()
            
            # 记录会话统计
            session_stats = {
                'duration': session_duration,
                'operation_count': len(self.session_operations),
                'workflow_pattern': workflow.value,
                'efficiency_score': self._calculate_session_efficiency()
            }
            
            logger.info(f"会话结束分析: {session_stats}")
            
            # 保存重要的习惯模式
            self._consolidate_session_patterns()
            
        except Exception as e:
            logger.error(f"会话结束分析失败: {str(e)}")

    def _start_new_session(self):
        """开始新会话"""
        try:
            self.session_start_time = time.time()
            self.session_operations = []
            self.current_workflow = WorkflowPattern.MIXED
            logger.info("开始新的学习会话")
            
        except Exception as e:
            logger.error(f"开始新会话失败: {str(e)}")

    def _deep_pattern_analysis(self):
        """深度模式分析"""
        try:
            # 分析长期习惯模式
            operation_sequences = []
            
            # 提取操作序列
            for i in range(len(self.operation_history) - 2):
                seq = [
                    self.operation_history[i].action,
                    self.operation_history[i+1].action,
                    self.operation_history[i+2].action
                ]
                operation_sequences.append(seq)
            
            # 寻找重复的三元组模式
            pattern_counts = defaultdict(int)
            for seq in operation_sequences:
                pattern_key = '->'.join(seq)
                pattern_counts[pattern_key] += 1
            
            # 创建或更新习惯模式
            for pattern_key, count in pattern_counts.items():
                if count >= self.learning_config['min_pattern_frequency']:
                    actions = pattern_key.split('->')
                    
                    pattern_id = f"deep_pattern_{hash(pattern_key) % 10000}"
                    
                    if pattern_id in self.habit_patterns:
                        pattern = self.habit_patterns[pattern_id]
                        pattern.frequency = count
                        pattern.confidence = min(0.95, pattern.confidence + 0.1)
                    else:
                        self.habit_patterns[pattern_id] = HabitPattern(
                            pattern_id=pattern_id,
                            description=f"深度模式: {' -> '.join(actions)}",
                            frequency=count,
                            confidence=0.6,
                            last_occurrence=time.time(),
                            triggers=actions[:-1],
                            actions=[actions[-1]],
                            context_requirements={}
                        )
            
            logger.debug(f"深度分析发现 {len([p for p in pattern_counts.values() if p >= 3])} 个重要模式")
            
        except Exception as e:
            logger.error(f"深度模式分析失败: {str(e)}")

    def _calculate_session_efficiency(self) -> float:
        """计算会话效率分数"""
        try:
            if not self.session_operations:
                return 0.0
            
            total_operations = len(self.session_operations)
            successful_operations = sum(1 for op in self.session_operations if op.success)
            
            # 基础成功率
            success_rate = successful_operations / total_operations
            
            # 操作密度（操作/分钟）
            session_duration = time.time() - self.session_start_time
            if session_duration > 0:
                operation_density = total_operations / (session_duration / 60)
                density_score = min(1.0, operation_density / 10)  # 假设10操作/分钟为满分
            else:
                density_score = 0.0
            
            # 综合效率分数
            efficiency = success_rate * 0.7 + density_score * 0.3
            return efficiency
            
        except Exception as e:
            logger.error(f"计算会话效率失败: {str(e)}")
            return 0.0

    def _consolidate_session_patterns(self):
        """整理会话模式"""
        try:
            # 移除低置信度的模式
            patterns_to_remove = []
            for pattern_id, pattern in self.habit_patterns.items():
                if pattern.confidence < 0.3 and pattern.frequency < 2:
                    patterns_to_remove.append(pattern_id)
            
            for pattern_id in patterns_to_remove:
                del self.habit_patterns[pattern_id]
            
            if patterns_to_remove:
                logger.debug(f"清理了 {len(patterns_to_remove)} 个低质量模式")
            
        except Exception as e:
            logger.error(f"整理会话模式失败: {str(e)}")

    def _apply_habit_decay(self):
        """应用习惯衰减"""
        try:
            current_time = time.time()
            decay_rate = self.learning_config['habit_decay_rate']
            
            for pattern in self.habit_patterns.values():
                # 根据时间距离应用衰减
                time_since_last = current_time - pattern.last_occurrence
                if time_since_last > 86400:  # 超过24小时
                    days_passed = time_since_last / 86400
                    pattern.confidence *= (decay_rate ** days_passed)
                    
                    # 确保置信度不低于最小值
                    pattern.confidence = max(0.1, pattern.confidence)
            
        except Exception as e:
            logger.error(f"应用习惯衰减失败: {str(e)}")

    def save_memory(self) -> bool:
        """保存习惯记忆到文件"""
        try:
            # 确保目录存在
            memory_dir = os.path.dirname(self.memory_file)
            if memory_dir:
                os.makedirs(memory_dir, exist_ok=True)
            
            # 准备保存数据
            memory_data = {
                'version': '1.0',
                'last_updated': time.time(),
                'session_info': {
                    'session_start': self.session_start_time,
                    'current_workflow': self.current_workflow.value,
                    'operations_count': len(self.session_operations)
                },
                'habit_patterns': {},
                'user_preferences': {},
                'learning_config': self.learning_config
            }
            
            # 序列化习惯模式
            for pattern_id, pattern in self.habit_patterns.items():
                memory_data['habit_patterns'][pattern_id] = asdict(pattern)
            
            # 序列化用户偏好
            for pref_id, preference in self.user_preferences.items():
                memory_data['user_preferences'][pref_id] = asdict(preference)
            
            # 保存到文件
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"用户习惯记忆已保存到: {self.memory_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存习惯记忆失败: {str(e)}")
            return False

    def load_memory(self) -> bool:
        """从文件加载习惯记忆"""
        try:
            if not os.path.exists(self.memory_file):
                logger.info("习惯记忆文件不存在，使用默认设置")
                return True
            
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            # 加载习惯模式
            patterns_data = memory_data.get('habit_patterns', {})
            for pattern_id, pattern_dict in patterns_data.items():
                # 转换枚举类型
                self.habit_patterns[pattern_id] = HabitPattern(**pattern_dict)
            
            # 加载用户偏好
            preferences_data = memory_data.get('user_preferences', {})
            for pref_id, pref_dict in preferences_data.items():
                self.user_preferences[pref_id] = UserPreference(**pref_dict)
            
            # 加载学习配置
            if 'learning_config' in memory_data:
                self.learning_config.update(memory_data['learning_config'])
            
            # 恢复会话信息
            session_info = memory_data.get('session_info', {})
            if 'current_workflow' in session_info:
                try:
                    self.current_workflow = WorkflowPattern(session_info['current_workflow'])
                except ValueError:
                    self.current_workflow = WorkflowPattern.MIXED
            
            logger.info(f"用户习惯记忆已从 {self.memory_file} 加载")
            logger.debug(f"加载了 {len(self.habit_patterns)} 个习惯模式和 {len(self.user_preferences)} 个用户偏好")
            
            return True
            
        except Exception as e:
            logger.error(f"加载习惯记忆失败: {str(e)}")
            return False

    def get_habit_report(self) -> Dict[str, Any]:
        """获取习惯分析报告"""
        try:
            current_time = time.time()
            
            # 统计信息
            total_patterns = len(self.habit_patterns)
            active_patterns = len([p for p in self.habit_patterns.values() if p.confidence > 0.5])
            total_preferences = len(self.user_preferences)
            
            # 最常见的习惯
            top_habits = sorted(
                [(p.description, p.frequency, p.confidence) for p in self.habit_patterns.values()],
                key=lambda x: x[1] * x[2],
                reverse=True
            )[:10]
            
            # 当前会话统计
            session_duration = current_time - self.session_start_time
            session_ops = len(self.session_operations)
            
            # 预测准确性（如果有的话）
            prediction_accuracy = getattr(self, '_prediction_accuracy', 0.0)
            
            report = {
                'summary': {
                    'total_patterns': total_patterns,
                    'active_patterns': active_patterns,
                    'total_preferences': total_preferences,
                    'current_workflow': self.current_workflow.value,
                    'session_duration_minutes': session_duration / 60,
                    'session_operations': session_ops,
                    'prediction_accuracy': prediction_accuracy
                },
                'top_habits': top_habits,
                'recent_operations': [
                    {
                        'action': op.action,
                        'type': op.operation_type.value,
                        'timestamp': op.timestamp,
                        'success': op.success
                    }
                    for op in list(self.operation_history)[-10:]
                ],
                'learning_effectiveness': self._calculate_learning_effectiveness(),
                'adaptation_suggestions': self.get_personalized_suggestions(),
                'interface_adaptations': self.adapt_interface_layout(),
                'timestamp': current_time
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成习惯报告失败: {str(e)}")
            return {}

    def _calculate_learning_effectiveness(self) -> float:
        """计算学习效果评分"""
        try:
            if not self.habit_patterns:
                return 0.0
            
            # 基于模式数量和质量
            pattern_quality = sum(p.confidence * p.frequency for p in self.habit_patterns.values())
            pattern_count = len(self.habit_patterns)
            
            # 归一化分数
            effectiveness = min(1.0, pattern_quality / (pattern_count * 10))
            
            return effectiveness
            
        except Exception as e:
            logger.error(f"计算学习效果失败: {str(e)}")
            return 0.0

    def clear_habits(self, confirm: bool = False):
        """清除所有习惯数据"""
        if confirm:
            try:
                self.habit_patterns.clear()
                self.user_preferences.clear()
                self.operation_history.clear()
                self.session_operations.clear()
                
                # 重置会话
                self._start_new_session()
                
                logger.info("用户习惯数据已清除")
                return True
                
            except Exception as e:
                logger.error(f"清除习惯数据失败: {str(e)}")
                return False
        else:
            logger.warning("清除习惯数据需要确认")
            return False