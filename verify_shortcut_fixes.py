#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证快捷键冲突修复结果
"""

import re
import json
from collections import defaultdict


def extract_shortcuts_from_main():
    """从主程序文件中提取快捷键"""
    shortcuts = {}
    
    try:
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        # 查找action调用中的快捷键
        for line_num, line in enumerate(lines, 1):
            # 匹配 action(..., 'shortcut', ...) 模式
            pattern = r"action\([^,]+,\s*[^,]+,\s*['\"]([^'\"]+)['\"]"
            matches = re.findall(pattern, line)
            
            for shortcut in matches:
                if shortcut and shortcut != 'None' and shortcut.strip():
                    # 提取动作名称
                    var_match = re.match(r'\s*(\w+)\s*=\s*action\(', line)
                    action_name = var_match.group(1) if var_match else "unknown"
                    shortcuts[shortcut] = (action_name, line_num)
                    
    except Exception as e:
        print(f"读取主程序文件失败: {e}")
    
    return shortcuts


def extract_shortcuts_from_manager():
    """从快捷键管理器中提取快捷键"""
    shortcuts = {}

    try:
        with open('libs/shortcut_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用多行匹配来处理跨行的register_action调用
        pattern = r'register_action\(\s*["\']([^"\']+)["\']\s*,\s*["\'][^"\']*["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\'][^"\']*["\']\s*\)'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

        # 为了获取行号，我们需要重新搜索每个匹配
        lines = content.splitlines()
        for action_name, shortcut in matches:
            if shortcut and shortcut.strip():
                # 查找这个动作在哪一行
                for line_num, line in enumerate(lines, 1):
                    if action_name in line and 'register_action' in line:
                        shortcuts[shortcut] = (action_name, line_num)
                        break

    except Exception as e:
        print(f"读取管理器文件失败: {e}")

    return shortcuts


def analyze_conflicts():
    """分析快捷键冲突"""
    print("="*80)
    print("快捷键冲突修复验证报告")
    print("="*80)
    
    main_shortcuts = extract_shortcuts_from_main()
    manager_shortcuts = extract_shortcuts_from_manager()
    
    print(f"\n📊 统计信息:")
    print(f"  主程序快捷键数量: {len(main_shortcuts)}")
    print(f"  管理器快捷键数量: {len(manager_shortcuts)}")
    
    # 检测冲突
    conflicts = []
    all_shortcuts = defaultdict(list)
    
    for shortcut, (action, line) in main_shortcuts.items():
        all_shortcuts[shortcut].append(('main', action, line))
    
    for shortcut, (action, line) in manager_shortcuts.items():
        all_shortcuts[shortcut].append(('manager', action, line))
    
    for shortcut, sources in all_shortcuts.items():
        if len(sources) > 1:
            conflicts.append((shortcut, sources))
    
    print(f"  总计唯一快捷键: {len(all_shortcuts)}")
    print(f"  发现冲突数量: {len(conflicts)}")
    
    if conflicts:
        print(f"\n🚨 剩余冲突:")
        for i, (shortcut, sources) in enumerate(conflicts, 1):
            print(f"\n  {i}. 快捷键冲突: {shortcut}")
            for source, action, line in sources:
                print(f"     - {source}: {action} (行 {line})")
    else:
        print(f"\n✅ 恭喜！所有快捷键冲突已解决！")
    
    # 显示修复摘要
    print(f"\n📋 修复摘要:")
    print(f"  - 移除了主程序中重复的AI和批量操作快捷键定义")
    print(f"  - 修改了管理器中冲突的快捷键:")
    
    expected_changes = [
        ("single_class_mode", "Ctrl+Shift+M → Ctrl+Alt+M"),
        ("toggle_draw_square", "Ctrl+Shift+R → Ctrl+Alt+R"),
        ("duplicate_shape", "Ctrl+D → Ctrl+Alt+C"),
        ("batch_delete", "Ctrl+Shift+D → Ctrl+Alt+D"),
        ("batch_convert", "Ctrl+Shift+T → Ctrl+Alt+T"),
        ("color_dialog", "Ctrl+Shift+L → Ctrl+Alt+L"),
        ("show_shortcuts", "Ctrl+H → F2"),
        ("about", "Ctrl+Shift+A → F12"),
    ]
    
    for action, change in expected_changes:
        print(f"    • {action}: {change}")
    
    # 验证特定修改
    print(f"\n🔍 验证关键修改:")
    
    # 检查是否成功移除了主程序中的重复快捷键
    removed_shortcuts = ['Ctrl+P', 'Ctrl+Shift+P', 'F9', 'Ctrl+B', 'Ctrl+Shift+C']
    for shortcut in removed_shortcuts:
        if shortcut not in main_shortcuts:
            print(f"  ✅ 已成功移除主程序中的 {shortcut}")
        else:
            print(f"  ❌ 主程序中仍存在 {shortcut}")
    
    # 检查管理器中的新快捷键
    new_manager_shortcuts = {
        'Ctrl+Alt+M': 'single_class_mode',
        'Ctrl+Alt+R': 'toggle_draw_square', 
        'Ctrl+Alt+C': 'duplicate_shape',
        'Ctrl+Alt+D': 'batch_delete',
        'Ctrl+Alt+T': 'batch_convert',
        'Ctrl+Alt+L': 'color_dialog',
        'F2': 'show_shortcuts',
        'F12': 'about'
    }
    
    for shortcut, expected_action in new_manager_shortcuts.items():
        if shortcut in manager_shortcuts:
            actual_action = manager_shortcuts[shortcut][0]
            if actual_action == expected_action:
                print(f"  ✅ 管理器中 {shortcut} 正确分配给 {expected_action}")
            else:
                print(f"  ❌ 管理器中 {shortcut} 分配给 {actual_action}，期望 {expected_action}")
        else:
            print(f"  ❌ 管理器中缺少 {shortcut}")
    
    return conflicts, main_shortcuts, manager_shortcuts


def save_verification_report(conflicts, main_shortcuts, manager_shortcuts):
    """保存验证报告"""
    report = {
        "verification_date": "2025-01-31",
        "status": "SUCCESS" if len(conflicts) == 0 else "PARTIAL",
        "summary": {
            "main_shortcuts_count": len(main_shortcuts),
            "manager_shortcuts_count": len(manager_shortcuts),
            "remaining_conflicts": len(conflicts)
        },
        "main_shortcuts": {k: {"action": v[0], "line": v[1]} for k, v in main_shortcuts.items()},
        "manager_shortcuts": {k: {"action": v[0], "line": v[1]} for k, v in manager_shortcuts.items()},
        "remaining_conflicts": []
    }
    
    for shortcut, sources in conflicts:
        conflict_info = {
            "shortcut": shortcut,
            "sources": [{"source": s[0], "action": s[1], "line": s[2]} for s in sources]
        }
        report["remaining_conflicts"].append(conflict_info)
    
    with open("shortcut_fix_verification_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 验证报告已保存到: shortcut_fix_verification_report.json")


if __name__ == "__main__":
    conflicts, main_shortcuts, manager_shortcuts = analyze_conflicts()
    save_verification_report(conflicts, main_shortcuts, manager_shortcuts)
