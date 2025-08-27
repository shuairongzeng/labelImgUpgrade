# -*- coding: utf-8 -*-
"""
智能快捷键冲突检测和修复系统

主要功能：
1. 智能冲突检测 - 检测潜在和实际的快捷键冲突
2. 自动修复建议 - 提供智能的修复方案
3. 使用习惯分析 - 基于用户使用频率优化快捷键分配
4. 动态优化 - 根据使用情况动态调整快捷键优先级
"""

import json
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QDateTime
from PyQt5.QtWidgets import QKeySequenceEdit
from PyQt5.QtGui import QKeySequence

from .logger_config import get_logger

logger = get_logger(__name__)


class ConflictType(Enum):
    """冲突类型"""
    EXACT = "exact"           # 完全相同的快捷键
    SUBSET = "subset"         # 子集冲突 (如 Ctrl+A 与 Ctrl+Alt+A)
    SUPERSET = "superset"     # 超集冲突
    SIMILAR = "similar"       # 相似冲突 (如 Ctrl+S 与 Ctrl+Shift+S)
    CONTEXTUAL = "contextual" # 上下文冲突 (同一上下文中使用)


class ConflictSeverity(Enum):
    """冲突严重程度"""
    CRITICAL = "critical"     # 严重冲突，必须解决
    HIGH = "high"            # 高优先级冲突
    MEDIUM = "medium"        # 中等冲突
    LOW = "low"              # 低优先级冲突
    INFO = "info"            # 信息性冲突


@dataclass
class UsageStats:
    """使用统计"""
    total_uses: int = 0
    last_used: float = 0.0
    avg_interval: float = 0.0
    recent_uses: List[float] = None
    frequency_score: float = 0.0
    
    def __post_init__(self):
        if self.recent_uses is None:
            self.recent_uses = []


@dataclass
class ConflictInfo:
    """冲突信息"""
    action1: str
    action2: str
    key_sequence: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    suggested_fixes: List[str]
    auto_fixable: bool = False


@dataclass
class FixSuggestion:
    """修复建议"""
    action_name: str
    current_key: str
    suggested_key: str
    reason: str
    confidence: float
    priority: int


class SmartShortcutOptimizer(QObject):
    """智能快捷键优化器"""
    
    # 信号定义
    conflicts_detected = pyqtSignal(list)  # 检测到冲突
    optimization_ready = pyqtSignal(list)  # 优化建议就绪
    stats_updated = pyqtSignal(dict)       # 统计更新

    def __init__(self, shortcut_manager, stats_file: str = "config/shortcut_stats.json"):
        super().__init__()
        
        self.shortcut_manager = shortcut_manager
        self.stats_file = stats_file
        
        # 使用统计
        self.usage_stats: Dict[str, UsageStats] = {}
        
        # 冲突缓存
        self.conflict_cache: Dict[str, List[ConflictInfo]] = {}
        self.last_conflict_check = 0.0
        
        # 智能分析配置
        self.analysis_config = {
            'recent_uses_window': 100,     # 最近使用记录窗口大小
            'frequency_weight': 0.4,       # 使用频率权重
            'recency_weight': 0.3,         # 最近使用权重
            'pattern_weight': 0.3,         # 模式匹配权重
            'min_confidence': 0.6,         # 最小置信度
            'auto_fix_threshold': 0.8,     # 自动修复置信度阈值
        }
        
        # 常见快捷键模式
        self.common_patterns = {
            'file_ops': ['Ctrl+O', 'Ctrl+S', 'Ctrl+N', 'Ctrl+W'],
            'edit_ops': ['Ctrl+C', 'Ctrl+V', 'Ctrl+X', 'Ctrl+Z', 'Ctrl+Y'],
            'view_ops': ['Ctrl+Plus', 'Ctrl+Minus', 'Ctrl+0', 'F11'],
            'nav_ops': ['Ctrl+Left', 'Ctrl+Right', 'Home', 'End'],
            'tool_ops': ['F1', 'F2', 'F9', 'F12'],
        }
        
        # 加载统计数据
        self.load_stats()
        
        # 定期优化检查
        self.optimization_timer = QTimer()
        self.optimization_timer.timeout.connect(self.periodic_optimization)
        self.optimization_timer.start(300000)  # 5分钟检查一次

    def record_usage(self, action_name: str):
        """记录快捷键使用"""
        try:
            current_time = time.time()
            
            if action_name not in self.usage_stats:
                self.usage_stats[action_name] = UsageStats()
            
            stats = self.usage_stats[action_name]
            
            # 更新统计
            stats.total_uses += 1
            stats.last_used = current_time
            
            # 更新最近使用记录
            stats.recent_uses.append(current_time)
            max_window = self.analysis_config['recent_uses_window']
            if len(stats.recent_uses) > max_window:
                stats.recent_uses = stats.recent_uses[-max_window:]
            
            # 计算平均间隔
            if len(stats.recent_uses) > 1:
                intervals = [stats.recent_uses[i] - stats.recent_uses[i-1] 
                           for i in range(1, len(stats.recent_uses))]
                stats.avg_interval = sum(intervals) / len(intervals)
            
            # 计算频率分数
            stats.frequency_score = self._calculate_frequency_score(stats)
            
            logger.debug(f"记录快捷键使用: {action_name}, 总使用次数: {stats.total_uses}")
            
            # 发送统计更新信号
            self.stats_updated.emit({action_name: asdict(stats)})
            
        except Exception as e:
            logger.error(f"记录使用统计失败: {str(e)}")

    def _calculate_frequency_score(self, stats: UsageStats) -> float:
        """计算频率分数"""
        try:
            current_time = time.time()
            
            # 基础频率分数
            base_score = min(stats.total_uses / 100.0, 1.0)
            
            # 最近使用加权
            if stats.last_used > 0:
                hours_since_last = (current_time - stats.last_used) / 3600
                recency_factor = max(0.1, 1.0 - (hours_since_last / 168))  # 一周衰减
            else:
                recency_factor = 0.1
            
            # 使用密度加权
            if len(stats.recent_uses) > 10:
                recent_period = stats.recent_uses[-1] - stats.recent_uses[-10]
                if recent_period > 0:
                    density_factor = min(10.0 / (recent_period / 3600), 2.0)  # 每小时使用次数
                else:
                    density_factor = 1.0
            else:
                density_factor = 1.0
            
            # 综合计算
            weights = self.analysis_config
            score = (base_score * weights['frequency_weight'] +
                    recency_factor * weights['recency_weight'] +
                    density_factor * weights['pattern_weight'])
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"计算频率分数失败: {str(e)}")
            return 0.0

    def detect_conflicts(self, force_check: bool = False) -> List[ConflictInfo]:
        """检测快捷键冲突"""
        try:
            current_time = time.time()
            
            # 检查缓存
            if (not force_check and 
                current_time - self.last_conflict_check < 30 and
                'all' in self.conflict_cache):
                return self.conflict_cache['all']
            
            conflicts = []
            actions = self.shortcut_manager.actions
            
            # 构建快捷键映射
            key_to_actions = defaultdict(list)
            for action_name, action in actions.items():
                if action.enabled and action.current_key:
                    key_to_actions[action.current_key].append(action_name)
            
            # 检测完全相同的冲突
            for key_seq, action_list in key_to_actions.items():
                if len(action_list) > 1:
                    for i in range(len(action_list)):
                        for j in range(i + 1, len(action_list)):
                            conflict = ConflictInfo(
                                action1=action_list[i],
                                action2=action_list[j],
                                key_sequence=key_seq,
                                conflict_type=ConflictType.EXACT,
                                severity=ConflictSeverity.CRITICAL,
                                description=f"完全相同的快捷键: {key_seq}",
                                suggested_fixes=self._generate_fix_suggestions(
                                    action_list[i], action_list[j], key_seq
                                ),
                                auto_fixable=True
                            )
                            conflicts.append(conflict)
            
            # 检测模式冲突
            conflicts.extend(self._detect_pattern_conflicts(actions))
            
            # 检测上下文冲突
            conflicts.extend(self._detect_contextual_conflicts(actions))
            
            # 缓存结果
            self.conflict_cache['all'] = conflicts
            self.last_conflict_check = current_time
            
            logger.info(f"检测到 {len(conflicts)} 个快捷键冲突")
            
            # 发送冲突检测信号
            if conflicts:
                self.conflicts_detected.emit(conflicts)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"检测快捷键冲突失败: {str(e)}")
            return []

    def _detect_pattern_conflicts(self, actions: Dict) -> List[ConflictInfo]:
        """检测模式冲突"""
        conflicts = []
        
        try:
            # 分析按键序列的相似性
            key_sequences = [(name, action.current_key) for name, action in actions.items() 
                           if action.enabled and action.current_key]
            
            for i, (name1, key1) in enumerate(key_sequences):
                for j, (name2, key2) in enumerate(key_sequences[i+1:], i+1):
                    similarity = self._calculate_key_similarity(key1, key2)
                    
                    if similarity > 0.7:  # 高相似度
                        severity = ConflictSeverity.HIGH if similarity > 0.9 else ConflictSeverity.MEDIUM
                        
                        conflict = ConflictInfo(
                            action1=name1,
                            action2=name2,
                            key_sequence=f"{key1} / {key2}",
                            conflict_type=ConflictType.SIMILAR,
                            severity=severity,
                            description=f"相似的快捷键模式 (相似度: {similarity:.1%})",
                            suggested_fixes=self._generate_similarity_fixes(name1, name2, key1, key2),
                            auto_fixable=similarity > 0.9
                        )
                        conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"检测模式冲突失败: {str(e)}")
            return []

    def _detect_contextual_conflicts(self, actions: Dict) -> List[ConflictInfo]:
        """检测上下文冲突"""
        conflicts = []
        
        try:
            # 按类别分组
            category_groups = defaultdict(list)
            for name, action in actions.items():
                if action.enabled and action.current_key:
                    category_groups[action.category].append((name, action))
            
            # 检测同类别内的潜在冲突
            for category, action_list in category_groups.items():
                if len(action_list) < 2:
                    continue
                
                # 检查功能相似的操作是否使用了差异过大的快捷键
                for i, (name1, action1) in enumerate(action_list):
                    for j, (name2, action2) in enumerate(action_list[i+1:], i+1):
                        
                        # 检查是否是互斥操作
                        if self._are_mutually_exclusive(name1, name2):
                            continue
                        
                        # 计算逻辑距离
                        logical_distance = self._calculate_logical_distance(name1, name2)
                        key_distance = self._calculate_key_distance(action1.current_key, action2.current_key)
                        
                        # 如果逻辑上相近但快捷键差异很大
                        if logical_distance < 0.3 and key_distance > 0.8:
                            conflict = ConflictInfo(
                                action1=name1,
                                action2=name2,
                                key_sequence=f"{action1.current_key} / {action2.current_key}",
                                conflict_type=ConflictType.CONTEXTUAL,
                                severity=ConflictSeverity.LOW,
                                description=f"功能相近但快捷键差异较大 (类别: {category})",
                                suggested_fixes=self._generate_contextual_fixes(name1, name2, action1.current_key, action2.current_key),
                                auto_fixable=False
                            )
                            conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"检测上下文冲突失败: {str(e)}")
            return []

    def _calculate_key_similarity(self, key1: str, key2: str) -> float:
        """计算快捷键相似度"""
        try:
            if not key1 or not key2:
                return 0.0
            
            # 解析按键序列
            seq1_parts = self._parse_key_sequence(key1)
            seq2_parts = self._parse_key_sequence(key2)
            
            # 计算修饰键相似度
            mod1 = set(seq1_parts['modifiers'])
            mod2 = set(seq2_parts['modifiers'])
            
            if mod1 and mod2:
                mod_similarity = len(mod1 & mod2) / len(mod1 | mod2)
            elif not mod1 and not mod2:
                mod_similarity = 1.0
            else:
                mod_similarity = 0.0
            
            # 计算主键相似度
            key_similarity = 1.0 if seq1_parts['key'] == seq2_parts['key'] else 0.0
            
            # 综合相似度
            return mod_similarity * 0.7 + key_similarity * 0.3
            
        except Exception as e:
            logger.error(f"计算快捷键相似度失败: {str(e)}")
            return 0.0

    def _parse_key_sequence(self, key_sequence: str) -> Dict[str, Any]:
        """解析快捷键序列"""
        try:
            parts = key_sequence.split('+')
            
            # 常见修饰键
            modifiers = []
            main_key = parts[-1] if parts else ''
            
            for part in parts[:-1]:
                if part.lower() in ['ctrl', 'alt', 'shift', 'meta']:
                    modifiers.append(part.lower())
            
            return {
                'modifiers': modifiers,
                'key': main_key.lower(),
                'full': key_sequence
            }
            
        except Exception as e:
            logger.error(f"解析快捷键序列失败: {str(e)}")
            return {'modifiers': [], 'key': '', 'full': key_sequence}

    def _calculate_logical_distance(self, action1: str, action2: str) -> float:
        """计算动作的逻辑距离"""
        try:
            # 功能分组相似度
            groups = [
                ['zoom_in', 'zoom_out', 'zoom_fit', 'zoom_original'],
                ['next_image', 'prev_image', 'first_image', 'last_image'],
                ['create_rect', 'create_polygon', 'create_circle', 'create_line'],
                ['ai_predict_current', 'ai_predict_batch', 'ai_apply_predictions'],
                ['batch_copy', 'batch_delete', 'batch_convert'],
            ]
            
            # 检查是否在同一功能组
            for group in groups:
                if action1 in group and action2 in group:
                    return 0.1  # 同组内逻辑距离很小
            
            # 名称相似度
            name_similarity = self._calculate_name_similarity(action1, action2)
            
            return 1.0 - name_similarity
            
        except Exception as e:
            logger.error(f"计算逻辑距离失败: {str(e)}")
            return 1.0

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """计算名称相似度"""
        try:
            # 简单的字符串相似度计算
            words1 = set(name1.lower().split('_'))
            words2 = set(name2.lower().split('_'))
            
            if not words1 and not words2:
                return 1.0
            elif not words1 or not words2:
                return 0.0
            
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            return intersection / union
            
        except Exception as e:
            logger.error(f"计算名称相似度失败: {str(e)}")
            return 0.0

    def _calculate_key_distance(self, key1: str, key2: str) -> float:
        """计算快捷键距离"""
        try:
            seq1 = self._parse_key_sequence(key1)
            seq2 = self._parse_key_sequence(key2)
            
            # 修饰键差异
            mod1 = set(seq1['modifiers'])
            mod2 = set(seq2['modifiers'])
            mod_diff = len(mod1.symmetric_difference(mod2))
            
            # 主键差异
            key_diff = 0 if seq1['key'] == seq2['key'] else 1
            
            # 综合距离
            return (mod_diff * 0.5 + key_diff * 0.5) / 2.0
            
        except Exception as e:
            logger.error(f"计算快捷键距离失败: {str(e)}")
            return 1.0

    def _are_mutually_exclusive(self, action1: str, action2: str) -> bool:
        """检查两个动作是否互斥"""
        # 一些互斥的操作对
        exclusive_pairs = [
            ('zoom_in', 'zoom_out'),
            ('next_image', 'prev_image'),
            ('first_image', 'last_image'),
        ]
        
        for pair in exclusive_pairs:
            if (action1 in pair and action2 in pair):
                return True
        
        return False

    def _generate_fix_suggestions(self, action1: str, action2: str, conflict_key: str) -> List[str]:
        """生成修复建议"""
        try:
            suggestions = []
            
            # 基于使用频率决定保留哪个
            stats1 = self.usage_stats.get(action1, UsageStats())
            stats2 = self.usage_stats.get(action2, UsageStats())
            
            if stats1.frequency_score > stats2.frequency_score:
                primary_action = action1
                secondary_action = action2
            else:
                primary_action = action2
                secondary_action = action1
            
            suggestions.append(f"保留 {primary_action} 的快捷键 {conflict_key}")
            
            # 为次要动作建议新的快捷键
            new_key = self._suggest_alternative_key(secondary_action, conflict_key)
            if new_key:
                suggestions.append(f"将 {secondary_action} 改为 {new_key}")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成修复建议失败: {str(e)}")
            return []

    def _generate_similarity_fixes(self, action1: str, action2: str, key1: str, key2: str) -> List[str]:
        """生成相似性冲突修复建议"""
        suggestions = []
        
        suggestions.append(f"考虑使用更不同的快捷键模式")
        
        # 建议使用不同的修饰键组合
        alt_key1 = self._suggest_different_modifiers(key1)
        alt_key2 = self._suggest_different_modifiers(key2)
        
        if alt_key1:
            suggestions.append(f"将 {action1} 改为 {alt_key1}")
        if alt_key2:
            suggestions.append(f"将 {action2} 改为 {alt_key2}")
        
        return suggestions

    def _generate_contextual_fixes(self, action1: str, action2: str, key1: str, key2: str) -> List[str]:
        """生成上下文冲突修复建议"""
        suggestions = []
        
        suggestions.append("考虑使用相近的快捷键模式来反映功能关联性")
        
        # 建议使用顺序的快捷键
        base_key = self._find_common_base(key1, key2)
        if base_key:
            suggestions.append(f"使用 {base_key}+1, {base_key}+2 等顺序键")
        
        return suggestions

    def _suggest_alternative_key(self, action_name: str, current_key: str) -> Optional[str]:
        """为动作建议替代快捷键"""
        try:
            # 解析当前快捷键
            current_parts = self._parse_key_sequence(current_key)
            
            # 尝试不同的修饰键组合
            alternatives = [
                f"Ctrl+Alt+{current_parts['key']}",
                f"Ctrl+Shift+{current_parts['key']}",
                f"Alt+{current_parts['key']}",
                f"Shift+{current_parts['key']}",
            ]
            
            # 检查哪些键还没被占用
            used_keys = set()
            for action in self.shortcut_manager.actions.values():
                if action.current_key:
                    used_keys.add(action.current_key)
            
            for alt in alternatives:
                if alt not in used_keys:
                    return alt
            
            # 如果常见组合都被占用，尝试功能键
            for i in range(1, 13):
                f_key = f"F{i}"
                if f_key not in used_keys:
                    return f_key
            
            return None
            
        except Exception as e:
            logger.error(f"建议替代快捷键失败: {str(e)}")
            return None

    def _suggest_different_modifiers(self, key_sequence: str) -> Optional[str]:
        """建议不同的修饰键组合"""
        try:
            parts = self._parse_key_sequence(key_sequence)
            main_key = parts['key']
            current_mods = set(parts['modifiers'])
            
            # 可用的修饰键组合
            mod_combinations = [
                ['ctrl'],
                ['alt'],
                ['shift'],
                ['ctrl', 'alt'],
                ['ctrl', 'shift'],
                ['alt', 'shift'],
                ['ctrl', 'alt', 'shift'],
            ]
            
            # 找到与当前最不同的组合
            for mods in mod_combinations:
                mod_set = set(mods)
                if mod_set != current_mods:
                    new_key = '+'.join(mods + [main_key])
                    return new_key.title()
            
            return None
            
        except Exception as e:
            logger.error(f"建议不同修饰键失败: {str(e)}")
            return None

    def _find_common_base(self, key1: str, key2: str) -> Optional[str]:
        """找到两个快捷键的共同基础"""
        try:
            parts1 = self._parse_key_sequence(key1)
            parts2 = self._parse_key_sequence(key2)
            
            # 找到共同的修饰键
            common_mods = set(parts1['modifiers']) & set(parts2['modifiers'])
            
            if common_mods:
                return '+'.join(sorted(common_mods))
            
            return None
            
        except Exception as e:
            logger.error(f"查找共同基础失败: {str(e)}")
            return None

    def generate_optimization_suggestions(self) -> List[FixSuggestion]:
        """生成优化建议"""
        try:
            suggestions = []
            
            # 检测冲突
            conflicts = self.detect_conflicts()
            
            # 为每个冲突生成修复建议
            for conflict in conflicts:
                if conflict.auto_fixable and conflict.severity in [ConflictSeverity.CRITICAL, ConflictSeverity.HIGH]:
                    
                    # 基于使用统计决定优化方案
                    stats1 = self.usage_stats.get(conflict.action1, UsageStats())
                    stats2 = self.usage_stats.get(conflict.action2, UsageStats())
                    
                    if stats1.frequency_score < stats2.frequency_score:
                        target_action = conflict.action1
                        keep_action = conflict.action2
                    else:
                        target_action = conflict.action2
                        keep_action = conflict.action1
                    
                    # 生成建议的新快捷键
                    new_key = self._suggest_alternative_key(target_action, conflict.key_sequence)
                    
                    if new_key:
                        suggestion = FixSuggestion(
                            action_name=target_action,
                            current_key=conflict.key_sequence,
                            suggested_key=new_key,
                            reason=f"解决与 {keep_action} 的冲突",
                            confidence=self._calculate_fix_confidence(target_action, new_key),
                            priority=self._get_severity_priority(conflict.severity)
                        )
                        suggestions.append(suggestion)
            
            # 基于使用模式的优化建议
            suggestions.extend(self._generate_usage_based_suggestions())
            
            # 按优先级排序
            suggestions.sort(key=lambda x: (x.priority, -x.confidence))
            
            logger.info(f"生成了 {len(suggestions)} 个优化建议")
            
            if suggestions:
                self.optimization_ready.emit(suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {str(e)}")
            return []

    def _calculate_fix_confidence(self, action_name: str, new_key: str) -> float:
        """计算修复方案的置信度"""
        try:
            confidence = 0.5  # 基础置信度
            
            # 检查新快捷键是否符合常见模式
            for pattern_name, pattern_keys in self.common_patterns.items():
                if new_key in pattern_keys:
                    confidence += 0.2
                    break
            
            # 检查是否与动作名称匹配
            if self._key_matches_action_name(action_name, new_key):
                confidence += 0.2
            
            # 检查使用频率（高频动作应该有简单快捷键）
            stats = self.usage_stats.get(action_name, UsageStats())
            if stats.frequency_score > 0.7 and len(new_key.split('+')) <= 2:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"计算修复置信度失败: {str(e)}")
            return 0.5

    def _key_matches_action_name(self, action_name: str, key: str) -> bool:
        """检查快捷键是否与动作名称匹配"""
        try:
            # 简单的启发式匹配
            action_words = action_name.lower().split('_')
            key_lower = key.lower()
            
            for word in action_words:
                if len(word) > 0 and word[0] in key_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查快捷键匹配失败: {str(e)}")
            return False

    def _get_severity_priority(self, severity: ConflictSeverity) -> int:
        """获取严重程度对应的优先级"""
        priority_map = {
            ConflictSeverity.CRITICAL: 1,
            ConflictSeverity.HIGH: 2,
            ConflictSeverity.MEDIUM: 3,
            ConflictSeverity.LOW: 4,
            ConflictSeverity.INFO: 5,
        }
        return priority_map.get(severity, 5)

    def _generate_usage_based_suggestions(self) -> List[FixSuggestion]:
        """基于使用模式生成建议"""
        suggestions = []
        
        try:
            # 找出高频但复杂的快捷键
            for action_name, stats in self.usage_stats.items():
                if stats.frequency_score > 0.7:
                    action = self.shortcut_manager.get_action(action_name)
                    if action and action.current_key:
                        key_complexity = len(action.current_key.split('+'))
                        
                        # 高频动作应该有简单快捷键
                        if key_complexity > 2:
                            simple_key = self._suggest_simple_key(action_name)
                            if simple_key:
                                suggestion = FixSuggestion(
                                    action_name=action_name,
                                    current_key=action.current_key,
                                    suggested_key=simple_key,
                                    reason=f"高频操作 (频率分数: {stats.frequency_score:.2f}) 应使用简单快捷键",
                                    confidence=0.8,
                                    priority=2
                                )
                                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成基于使用的建议失败: {str(e)}")
            return []

    def _suggest_simple_key(self, action_name: str) -> Optional[str]:
        """为动作建议简单的快捷键"""
        try:
            # 简单的单键快捷键
            simple_keys = [
                'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
                'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
                'Z', 'X', 'C', 'V', 'B', 'N', 'M'
            ]
            
            # 检查已使用的键
            used_keys = set()
            for action in self.shortcut_manager.actions.values():
                if action.current_key and '+' not in action.current_key:
                    used_keys.add(action.current_key.upper())
            
            # 尝试使用与动作名称相关的键
            action_words = action_name.lower().split('_')
            for word in action_words:
                if word and word[0].upper() in simple_keys and word[0].upper() not in used_keys:
                    return word[0].upper()
            
            # 如果没有相关的键，使用任何可用的简单键
            for key in simple_keys:
                if key not in used_keys:
                    return key
            
            return None
            
        except Exception as e:
            logger.error(f"建议简单快捷键失败: {str(e)}")
            return None

    def apply_optimization(self, suggestion: FixSuggestion) -> bool:
        """应用优化建议"""
        try:
            success = self.shortcut_manager.update_shortcut(
                suggestion.action_name,
                suggestion.suggested_key
            )
            
            if success:
                logger.info(f"应用优化: {suggestion.action_name} {suggestion.current_key} -> {suggestion.suggested_key}")
                
                # 清除冲突缓存
                self.conflict_cache.clear()
                
                return True
            else:
                logger.warning(f"应用优化失败: {suggestion.action_name}")
                return False
                
        except Exception as e:
            logger.error(f"应用优化失败: {str(e)}")
            return False

    def periodic_optimization(self):
        """定期优化检查"""
        try:
            # 生成优化建议
            suggestions = self.generate_optimization_suggestions()
            
            # 自动应用高置信度的建议
            auto_applied = 0
            for suggestion in suggestions:
                if (suggestion.confidence >= self.analysis_config['auto_fix_threshold'] and
                    suggestion.priority <= 2):
                    
                    if self.apply_optimization(suggestion):
                        auto_applied += 1
            
            if auto_applied > 0:
                logger.info(f"自动应用了 {auto_applied} 个优化建议")
                
                # 保存配置
                self.shortcut_manager.save_shortcuts()
                
        except Exception as e:
            logger.error(f"定期优化检查失败: {str(e)}")

    def save_stats(self) -> bool:
        """保存统计数据"""
        try:
            # 确保目录存在
            stats_dir = os.path.dirname(self.stats_file)
            if stats_dir:
                os.makedirs(stats_dir, exist_ok=True)
            
            # 准备保存数据
            stats_data = {
                'version': '1.0',
                'last_updated': time.time(),
                'stats': {}
            }
            
            for action_name, stats in self.usage_stats.items():
                stats_data['stats'][action_name] = asdict(stats)
            
            # 保存到文件
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"使用统计已保存到: {self.stats_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存统计数据失败: {str(e)}")
            return False

    def load_stats(self) -> bool:
        """加载统计数据"""
        try:
            if not os.path.exists(self.stats_file):
                logger.info("统计文件不存在，使用空统计")
                return True
            
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
            
            stats_dict = stats_data.get('stats', {})
            
            # 加载统计数据
            for action_name, stats_dict_item in stats_dict.items():
                stats = UsageStats(**stats_dict_item)
                self.usage_stats[action_name] = stats
            
            logger.info(f"使用统计已从 {self.stats_file} 加载")
            return True
            
        except Exception as e:
            logger.error(f"加载统计数据失败: {str(e)}")
            return False

    def get_usage_report(self) -> Dict[str, Any]:
        """获取使用报告"""
        try:
            # 统计摘要
            total_actions = len(self.usage_stats)
            total_uses = sum(stats.total_uses for stats in self.usage_stats.values())
            active_actions = len([stats for stats in self.usage_stats.values() if stats.total_uses > 0])
            
            # 最常用的动作
            top_actions = sorted(
                [(name, stats) for name, stats in self.usage_stats.items()],
                key=lambda x: x[1].frequency_score,
                reverse=True
            )[:10]
            
            # 最近使用的动作
            recent_actions = sorted(
                [(name, stats) for name, stats in self.usage_stats.items() if stats.last_used > 0],
                key=lambda x: x[1].last_used,
                reverse=True
            )[:10]
            
            # 当前冲突
            conflicts = self.detect_conflicts()
            
            report = {
                'summary': {
                    'total_actions': total_actions,
                    'active_actions': active_actions,
                    'total_uses': total_uses,
                    'conflicts_count': len(conflicts),
                },
                'top_actions': [(name, stats.frequency_score, stats.total_uses) for name, stats in top_actions],
                'recent_actions': [(name, stats.last_used, stats.total_uses) for name, stats in recent_actions],
                'conflicts': [
                    {
                        'actions': [conflict.action1, conflict.action2],
                        'key': conflict.key_sequence,
                        'type': conflict.conflict_type.value,
                        'severity': conflict.severity.value
                    }
                    for conflict in conflicts
                ],
                'timestamp': time.time()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成使用报告失败: {str(e)}")
            return {}