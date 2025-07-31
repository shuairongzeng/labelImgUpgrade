#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的快捷键冲突分析
手动收集并分析所有快捷键定义
"""

import json
from collections import defaultdict
from typing import Dict, List, Tuple


class CompleteShortcutAnalyzer:
    """完整的快捷键分析器"""
    
    def __init__(self):
        # 主程序中的快捷键定义（从labelImg.py手动收集）
        self.main_shortcuts = {
            # 文件操作
            'Ctrl+Q': ('quit', 801, '退出程序'),
            'Ctrl+O': ('open', 804, '打开文件'),
            'Ctrl+u': ('open_dir', 807, '打开目录'),
            'Ctrl+r': ('change_save_dir', 810, '更改保存目录'),
            'Ctrl+Shift+O': ('open_annotation', 813, '打开标注文件'),
            'Ctrl+v': ('copy_prev_bounding', 815, '复制上一个边界框'),
            'Ctrl+Shift+E': ('export_yolo', 818, '导出YOLO格式'),
            'Ctrl+Shift+M': ('export_model', 821, '导出模型'),
            'Ctrl+S': ('save', 833, '保存'),
            'Ctrl+Y': ('save_format', 847, '更改保存格式'),
            'Ctrl+Shift+S': ('save_as', 852, '另存为'),
            'Ctrl+W': ('close', 855, '关闭当前文件'),
            'Ctrl+Shift+D': ('delete_image', 858, '删除图像'),
            
            # 导航操作
            'd': ('open_next_image', 824, '下一张图像'),
            'a': ('open_prev_image', 827, '上一张图像'),
            'space': ('verify', 830, '验证图像'),
            
            # 编辑操作
            'Ctrl+L': ('color1', 872, '选择边框颜色'),
            'w': ('create_mode', 875, '创建模式'),
            'Ctrl+J': ('edit_mode', 877, '编辑模式'),
            'Delete': ('delete', 882, '删除选中形状'),
            'Ctrl+D': ('copy', 884, '复制选中形状'),
            'Ctrl+Shift+A': ('advanced_mode', 888, '高级模式'),
            'Ctrl+H': ('hide_all', 893, '隐藏所有框'),
            'Ctrl+A': ('show_all', 896, '显示所有框'),
            'Ctrl+E': ('edit', 959, '编辑标签'),
            
            # 视图操作
            'Ctrl++': ('zoom_in', 915, '放大'),
            'Ctrl+-': ('zoom_out', 917, '缩小'),
            'Ctrl+=': ('zoom_org', 919, '原始大小'),
            'Ctrl+F': ('fit_window', 921, '适应窗口'),
            'Ctrl+Shift+F': ('fit_width', 924, '适应宽度'),
            'Ctrl+Shift++': ('light_brighten', 947, '增加亮度'),
            'Ctrl+Shift+-': ('light_darken', 949, '降低亮度'),
            'Ctrl+Shift+=': ('light_org', 951, '重置亮度'),
            
            # 特殊功能
            'Ctrl+Shift+T': ('labels_toggle', 972, '切换标签面板'),
            'Ctrl+Shift+R': ('draw_squares_option', 991, '绘制正方形'),
            'Ctrl+P': ('ai_predict_current', 1001, 'AI预测当前图像'),
            'Ctrl+Shift+P': ('ai_predict_batch', 1003, 'AI批量预测'),
            'F9': ('ai_toggle_panel', 1005, '切换AI面板'),
            'Ctrl+B': ('batch_operations', 1009, '批量操作'),
            'Ctrl+Shift+C': ('batch_copy', 1011, '批量复制'),
            'Ctrl+K': ('shortcut_config', 1017, '快捷键配置'),
            'Ctrl+Shift+L': ('display_label_option', 1068, '显示标签选项'),
        }
        
        # 快捷键管理器中的定义（从libs/shortcut_manager.py收集）
        self.manager_shortcuts = {
            # 视图操作
            'Ctrl+Plus': ('zoom_in', 86, '放大', '视图操作'),
            'Ctrl+Minus': ('zoom_out', 87, '缩小', '视图操作'),
            'Ctrl+0': ('zoom_fit', 88, '适应窗口', '视图操作'),
            'Ctrl+1': ('zoom_original', 89, '原始大小', '视图操作'),
            'F11': ('toggle_fullscreen', 90, '全屏切换', '视图操作'),
            'Ctrl+Shift+T': ('toggle_labels', 91, '切换标签面板', '视图操作'),
            'Ctrl+Shift+R': ('toggle_draw_square', 93, '切换矩形绘制', '视图操作'),
            'Ctrl+Shift+M': ('single_class_mode', 95, '单类模式', '视图操作'),
            'Ctrl+Shift+L': ('display_label_option', 97, '显示标签选项', '视图操作'),
            
            # 导航操作
            'Ctrl+Right': ('next_image', 100, '下一张图像', '导航操作'),
            'Ctrl+Left': ('prev_image', 101, '上一张图像', '导航操作'),
            'Home': ('first_image', 102, '第一张图像', '导航操作'),
            'End': ('last_image', 103, '最后一张图像', '导航操作'),
            
            # 标注操作
            'R': ('create_rect', 106, '创建矩形', '标注操作'),
            'P': ('create_polygon', 107, '创建多边形', '标注操作'),
            'C': ('create_circle', 108, '创建圆形', '标注操作'),
            'L': ('create_line', 109, '创建线条', '标注操作'),
            'E': ('edit_mode', 110, '编辑模式', '标注操作'),
            'Ctrl+D': ('duplicate_shape', 111, '复制形状', '标注操作'),
            
            # AI助手操作
            'Ctrl+P': ('ai_predict_current', 115, 'AI预测当前图像', 'AI助手'),
            'Ctrl+Shift+P': ('ai_predict_batch', 117, 'AI批量预测', 'AI助手'),
            'F9': ('ai_toggle_panel', 118, '切换AI面板', 'AI助手'),
            'Ctrl+Up': ('ai_increase_confidence', 120, '提高置信度', 'AI助手'),
            'Ctrl+Down': ('ai_decrease_confidence', 122, '降低置信度', 'AI助手'),
            'Ctrl+Enter': ('ai_apply_predictions', 124, '应用预测结果', 'AI助手'),
            'Ctrl+Delete': ('ai_clear_predictions', 126, '清除预测结果', 'AI助手'),
            
            # 批量操作
            'Ctrl+B': ('batch_operations', 129, '批量操作', '批量操作'),
            'Ctrl+Shift+C': ('batch_copy', 130, '批量复制', '批量操作'),
            'Ctrl+Shift+D': ('batch_delete', 131, '批量删除', '批量操作'),
            'Ctrl+Shift+T': ('batch_convert', 132, '批量转换', '批量操作'),
            
            # 工具操作
            'T': ('toggle_labels', 135, '切换标签显示', '工具操作'),
            'S': ('toggle_shapes', 136, '切换形状显示', '工具操作'),
            'G': ('toggle_grid', 137, '切换网格', '工具操作'),
            'Ctrl+Shift+L': ('color_dialog', 138, '颜色选择', '工具操作'),
            
            # 帮助操作
            'F1': ('show_help', 141, '显示帮助', '帮助操作'),
            'Ctrl+H': ('show_shortcuts', 142, '显示快捷键', '帮助操作'),
            'Ctrl+Shift+A': ('about', 143, '关于', '帮助操作'),
        }
    
    def analyze_conflicts(self):
        """分析快捷键冲突"""
        conflicts = []
        all_shortcuts = defaultdict(list)
        
        # 收集所有快捷键
        for shortcut, (action, line, desc) in self.main_shortcuts.items():
            all_shortcuts[shortcut].append(('main', action, line, desc))
        
        for shortcut, (action, line, desc, category) in self.manager_shortcuts.items():
            all_shortcuts[shortcut].append(('manager', action, line, desc, category))
        
        # 检测冲突
        for shortcut, sources in all_shortcuts.items():
            if len(sources) > 1:
                conflicts.append((shortcut, sources))
        
        return conflicts, all_shortcuts
    
    def generate_detailed_report(self):
        """生成详细的分析报告"""
        conflicts, all_shortcuts = self.analyze_conflicts()
        
        print("="*80)
        print("完整快捷键冲突分析报告")
        print("="*80)
        
        print(f"\n📊 统计信息:")
        print(f"  主程序快捷键数量: {len(self.main_shortcuts)}")
        print(f"  管理器快捷键数量: {len(self.manager_shortcuts)}")
        print(f"  总计唯一快捷键: {len(all_shortcuts)}")
        print(f"  发现冲突数量: {len(conflicts)}")
        
        if conflicts:
            print(f"\n🚨 冲突详情:")
            for i, (shortcut, sources) in enumerate(conflicts, 1):
                print(f"\n  {i}. 快捷键冲突: {shortcut}")
                for source_info in sources:
                    if source_info[0] == 'main':
                        source, action, line, desc = source_info
                        print(f"     - 主程序: {action} (行 {line}) - {desc}")
                    else:
                        source, action, line, desc, category = source_info
                        print(f"     - 管理器: {action} (行 {line}) - {desc} [{category}]")
        
        # 生成修复建议
        print(f"\n💡 修复建议:")
        self._generate_fix_recommendations(conflicts)
        
        # 保存详细报告
        self._save_detailed_report(conflicts, all_shortcuts)

        return conflicts, all_shortcuts

    def _generate_fix_recommendations(self, conflicts):
        """生成修复建议"""
        for i, (shortcut, sources) in enumerate(conflicts, 1):
            print(f"\n  {i}. {shortcut} 冲突修复建议:")

            main_sources = [s for s in sources if s[0] == 'main']
            manager_sources = [s for s in sources if s[0] == 'manager']

            if main_sources and manager_sources:
                print(f"     类型: 主程序与管理器冲突")
                print(f"     建议: 修改管理器中的快捷键定义，保持主程序不变")

                # 为管理器中的动作建议新的快捷键
                for source_info in manager_sources:
                    action = source_info[1]
                    category = source_info[4] if len(source_info) > 4 else "未知"
                    new_shortcut = self._suggest_alternative_shortcut(shortcut, action, category)
                    print(f"       - {action}: 建议改为 {new_shortcut}")

            elif len(manager_sources) > 1:
                print(f"     类型: 管理器内部冲突")
                print(f"     建议: 为重复的动作分配不同的快捷键")

                for j, source_info in enumerate(manager_sources[1:], 1):
                    action = source_info[1]
                    category = source_info[4] if len(source_info) > 4 else "未知"
                    new_shortcut = self._suggest_alternative_shortcut(shortcut, action, category)
                    print(f"       - {action}: 建议改为 {new_shortcut}")

    def _suggest_alternative_shortcut(self, original: str, action: str, category: str) -> str:
        """为动作建议替代的快捷键"""
        # 基于动作类型和类别建议新的快捷键
        suggestions = {
            # 视图操作
            'toggle_labels': 'Ctrl+Shift+Y',
            'batch_convert': 'Ctrl+Shift+V',
            'color_dialog': 'Ctrl+Shift+K',

            # 基于类别的通用建议
            'AI助手': {
                'ai_predict_current': 'Ctrl+Alt+P',
                'ai_predict_batch': 'Ctrl+Alt+B',
            },
            '批量操作': {
                'batch_convert': 'Ctrl+Alt+C',
                'batch_copy': 'Ctrl+Alt+V',
            },
            '工具操作': {
                'color_dialog': 'Ctrl+Alt+L',
            }
        }

        # 首先检查特定动作的建议
        if action in suggestions:
            return suggestions[action]

        # 然后检查类别的建议
        if category in suggestions and action in suggestions[category]:
            return suggestions[category][action]

        # 默认建议：在原快捷键基础上添加Alt
        if 'Ctrl+' in original and 'Alt+' not in original:
            return original.replace('Ctrl+', 'Ctrl+Alt+')
        elif 'Shift+' in original and 'Alt+' not in original:
            return original.replace('Shift+', 'Alt+Shift+')
        else:
            return f"Alt+{original}"

    def _save_detailed_report(self, conflicts, all_shortcuts):
        """保存详细报告到文件"""
        report = {
            "analysis_date": "2025-01-31",
            "summary": {
                "main_shortcuts_count": len(self.main_shortcuts),
                "manager_shortcuts_count": len(self.manager_shortcuts),
                "total_unique_shortcuts": len(all_shortcuts),
                "conflicts_count": len(conflicts)
            },
            "main_shortcuts": {},
            "manager_shortcuts": {},
            "conflicts": [],
            "fix_recommendations": []
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

        # 冲突信息
        for shortcut, sources in conflicts:
            conflict_info = {
                "shortcut": shortcut,
                "sources": []
            }
            for source_info in sources:
                if source_info[0] == 'main':
                    source, action, line, desc = source_info
                    conflict_info["sources"].append({
                        "source": source,
                        "action": action,
                        "line": line,
                        "description": desc
                    })
                else:
                    source, action, line, desc, category = source_info
                    conflict_info["sources"].append({
                        "source": source,
                        "action": action,
                        "line": line,
                        "description": desc,
                        "category": category
                    })
            report["conflicts"].append(conflict_info)

        # 保存到文件
        with open("complete_shortcut_analysis_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n📄 详细报告已保存到: complete_shortcut_analysis_report.json")


def main():
    """主函数"""
    analyzer = CompleteShortcutAnalyzer()
    conflicts, all_shortcuts = analyzer.generate_detailed_report()
    return analyzer, conflicts, all_shortcuts


if __name__ == "__main__":
    analyzer, conflicts, all_shortcuts = main()
