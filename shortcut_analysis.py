#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷键冲突分析工具
分析项目中的所有快捷键定义，检测冲突并生成报告
"""

import re
import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class ShortcutAnalyzer:
    """快捷键分析器"""
    
    def __init__(self):
        self.main_shortcuts = {}  # 主程序快捷键 {shortcut: (action_name, line_number, description)}
        self.manager_shortcuts = {}  # 快捷键管理器快捷键
        self.conflicts = []  # 冲突列表
        self.all_shortcuts = defaultdict(list)  # 所有快捷键 {shortcut: [(source, action, line)]}
    
    def analyze_main_file(self, file_path: str = "labelImg.py"):
        """分析主程序文件中的快捷键定义"""
        print(f"正在分析主程序文件: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()

            # 更全面的快捷键匹配模式
            patterns = [
                # action(..., 'Ctrl+X', ...)  - 匹配action函数调用中的快捷键
                (r"(\w+)\s*=\s*action\([^,]+,\s*[^,]+,\s*['\"]([^'\"]+)['\"]", "action_assignment"),
                # setShortcut('Ctrl+X')
                (r"(\w+)\.setShortcut\(['\"]([^'\"]+)['\"]\)", "setShortcut_call"),
                # self.xxx.setShortcut('Ctrl+X')
                (r"self\.(\w+)\.setShortcut\(['\"]([^'\"]+)['\"]\)", "self_setShortcut"),
                # 直接在action调用中的快捷键（无变量赋值）
                (r"action\(['\"]([^'\"]+)['\"][^,]*,[^,]*,[^,]*['\"]([^'\"]+)['\"]", "direct_action")
            ]

            for line_num, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                for pattern, pattern_type in patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if pattern_type == "action_assignment":
                            action_name, shortcut = match
                            description = self._extract_description_from_line(original_line)
                        elif pattern_type in ["setShortcut_call", "self_setShortcut"]:
                            action_name, shortcut = match
                            description = f"setShortcut for {action_name}"
                        elif pattern_type == "direct_action":
                            description, shortcut = match
                            action_name = self._extract_action_name_from_context(lines, line_num)
                        else:
                            continue

                        if shortcut and self._is_valid_shortcut(shortcut):
                            # 避免重复添加相同的快捷键
                            if shortcut not in self.main_shortcuts:
                                self.main_shortcuts[shortcut] = (action_name, line_num, description)
                                self.all_shortcuts[shortcut].append(("main", action_name, line_num))
                                print(f"  发现快捷键: {shortcut} -> {action_name} (行 {line_num})")

            print(f"主程序文件分析完成，共发现 {len(self.main_shortcuts)} 个快捷键")

        except Exception as e:
            print(f"分析主程序文件失败: {e}")

    def _is_valid_shortcut(self, shortcut: str) -> bool:
        """检查是否是有效的快捷键"""
        if not shortcut:
            return False
        # 排除一些明显不是快捷键的字符串
        invalid_patterns = ['http', 'www', '.com', '.py', '/', '\\', 'utf', 'encoding']
        return not any(pattern in shortcut.lower() for pattern in invalid_patterns)

    def _extract_action_name_from_context(self, lines: List[str], current_line: int) -> str:
        """从上下文中提取动作名称"""
        # 向上查找变量赋值
        for i in range(max(0, current_line - 5), current_line):
            if i < len(lines):
                line = lines[i].strip()
                var_match = re.match(r'\s*(\w+)\s*=\s*action\(', line)
                if var_match:
                    return var_match.group(1)
        return "unknown"

    def _extract_description_from_line(self, line: str) -> str:
        """从代码行中提取更准确的描述"""
        # 尝试从action调用中提取第一个参数（通常是描述）
        desc_patterns = [
            r"action\(['\"]([^'\"]+)['\"]",
            r"get_str\(['\"]([^'\"]+)['\"]"
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)

        return ""
    
    def analyze_manager_file(self, file_path: str = "libs/shortcut_manager.py"):
        """分析快捷键管理器文件"""
        print(f"正在分析快捷键管理器文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 匹配 register_action 调用
            pattern = r'register_action\(["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\)'
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                match = re.search(pattern, line)
                if match:
                    action_name, description, shortcut, category = match.groups()
                    
                    self.manager_shortcuts[shortcut] = (action_name, line_num, description, category)
                    self.all_shortcuts[shortcut].append(("manager", action_name, line_num))
                    
                    print(f"  发现快捷键: {shortcut} -> {action_name} (行 {line_num})")
            
            print(f"快捷键管理器分析完成，共发现 {len(self.manager_shortcuts)} 个快捷键")
            
        except Exception as e:
            print(f"分析快捷键管理器文件失败: {e}")
    
    def _extract_action_name(self, line: str) -> str:
        """从代码行中提取动作名称"""
        # 尝试从变量赋值中提取
        var_match = re.match(r'\s*(\w+)\s*=\s*action\(', line)
        if var_match:
            return var_match.group(1)
        
        # 尝试从setShortcut调用中提取
        if 'setShortcut' in line:
            # 查找self.xxx.setShortcut
            self_match = re.search(r'self\.(\w+)\.setShortcut', line)
            if self_match:
                return self_match.group(1)
        
        return "unknown"
    
    def _extract_description(self, line: str) -> str:
        """从代码行中提取描述"""
        # 尝试从action调用中提取第一个参数（通常是描述）
        desc_match = re.search(r"action\(['\"]([^'\"]+)['\"]", line)
        if desc_match:
            return desc_match.group(1)
        
        return ""
    
    def detect_conflicts(self):
        """检测快捷键冲突"""
        print("\n正在检测快捷键冲突...")
        
        for shortcut, sources in self.all_shortcuts.items():
            if len(sources) > 1:
                self.conflicts.append((shortcut, sources))
                print(f"  冲突: {shortcut}")
                for source, action, line in sources:
                    print(f"    - {source}: {action} (行 {line})")
        
        print(f"\n检测完成，共发现 {len(self.conflicts)} 个冲突")
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        report = {
            "summary": {
                "main_shortcuts_count": len(self.main_shortcuts),
                "manager_shortcuts_count": len(self.manager_shortcuts),
                "total_unique_shortcuts": len(self.all_shortcuts),
                "conflicts_count": len(self.conflicts)
            },
            "main_shortcuts": {},
            "manager_shortcuts": {},
            "conflicts": [],
            "recommendations": []
        }
        
        # 主程序快捷键
        for shortcut, (action, line, desc) in self.main_shortcuts.items():
            report["main_shortcuts"][shortcut] = {
                "action": action,
                "line": line,
                "description": desc
            }
        
        # 管理器快捷键
        for shortcut, (action, line, desc, category) in self.manager_shortcuts.items():
            report["manager_shortcuts"][shortcut] = {
                "action": action,
                "line": line,
                "description": desc,
                "category": category
            }
        
        # 冲突
        for shortcut, sources in self.conflicts:
            conflict_info = {
                "shortcut": shortcut,
                "sources": []
            }
            for source, action, line in sources:
                conflict_info["sources"].append({
                    "source": source,
                    "action": action,
                    "line": line
                })
            report["conflicts"].append(conflict_info)
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> List[Dict]:
        """生成修复建议"""
        recommendations = []
        
        for shortcut, sources in self.conflicts:
            # 分析冲突类型
            main_sources = [s for s in sources if s[0] == "main"]
            manager_sources = [s for s in sources if s[0] == "manager"]
            
            if main_sources and manager_sources:
                # 主程序和管理器之间的冲突
                rec = {
                    "type": "main_manager_conflict",
                    "shortcut": shortcut,
                    "description": f"主程序和快捷键管理器都定义了 {shortcut}",
                    "suggestion": "修改快捷键管理器中的定义，避免与主程序冲突",
                    "affected_actions": [s[1] for s in sources]
                }
                recommendations.append(rec)
            
            elif len(main_sources) > 1:
                # 主程序内部冲突
                rec = {
                    "type": "main_internal_conflict",
                    "shortcut": shortcut,
                    "description": f"主程序内部多个动作使用了相同的快捷键 {shortcut}",
                    "suggestion": "为其中一些动作分配新的快捷键",
                    "affected_actions": [s[1] for s in main_sources]
                }
                recommendations.append(rec)
            
            elif len(manager_sources) > 1:
                # 管理器内部冲突
                rec = {
                    "type": "manager_internal_conflict",
                    "shortcut": shortcut,
                    "description": f"快捷键管理器内部多个动作使用了相同的快捷键 {shortcut}",
                    "suggestion": "修改管理器中的重复定义",
                    "affected_actions": [s[1] for s in manager_sources]
                }
                recommendations.append(rec)
        
        return recommendations
    
    def save_report(self, filename: str = "shortcut_analysis_report.json"):
        """保存分析报告到文件"""
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n分析报告已保存到: {filename}")
        except Exception as e:
            print(f"保存报告失败: {e}")
        
        return report
    
    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("快捷键分析摘要")
        print("="*60)
        print(f"主程序快捷键数量: {len(self.main_shortcuts)}")
        print(f"管理器快捷键数量: {len(self.manager_shortcuts)}")
        print(f"总计唯一快捷键: {len(self.all_shortcuts)}")
        print(f"发现冲突数量: {len(self.conflicts)}")
        
        if self.conflicts:
            print("\n冲突详情:")
            for shortcut, sources in self.conflicts:
                print(f"  {shortcut}:")
                for source, action, line in sources:
                    print(f"    - {source}: {action} (行 {line})")


def main():
    """主函数"""
    print("开始快捷键冲突分析...")
    
    analyzer = ShortcutAnalyzer()
    
    # 分析主程序文件
    analyzer.analyze_main_file()
    
    # 分析快捷键管理器文件
    analyzer.analyze_manager_file()
    
    # 检测冲突
    analyzer.detect_conflicts()
    
    # 打印摘要
    analyzer.print_summary()
    
    # 保存报告
    report = analyzer.save_report()
    
    return analyzer, report


if __name__ == "__main__":
    analyzer, report = main()
