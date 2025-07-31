#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的快捷键系统测试脚本
"""

import sys
import os
import json
import re
from typing import Dict, List

def test_conflict_resolution():
    """测试1: 验证快捷键冲突解决"""
    print("🔍 测试1: 验证快捷键冲突解决...")
    
    try:
        with open('shortcut_fix_verification_report.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        conflicts_count = report['summary']['remaining_conflicts']
        if conflicts_count == 0:
            print("  ✅ 所有快捷键冲突已解决")
            return True
        else:
            print(f"  ❌ 仍存在 {conflicts_count} 个快捷键冲突")
            return False
            
    except FileNotFoundError:
        print("  ❌ 验证报告文件不存在")
        return False
    except Exception as e:
        print(f"  ❌ 读取验证报告失败: {e}")
        return False

def test_shortcut_manager_import():
    """测试2: 验证快捷键管理器可以导入"""
    print("🔧 测试2: 验证快捷键管理器导入...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from libs.shortcut_manager import ShortcutManager
        print("  ✅ 快捷键管理器导入成功")
        return True, ShortcutManager
    except ImportError as e:
        print(f"  ❌ 快捷键管理器导入失败: {e}")
        return False, None
    except Exception as e:
        print(f"  ❌ 导入时发生错误: {e}")
        return False, None

def test_modified_shortcuts():
    """测试3: 验证修改后的快捷键"""
    print("🎯 测试3: 验证修改后的快捷键...")
    
    try:
        with open('libs/shortcut_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查修改后的快捷键
        expected_shortcuts = {
            'Ctrl+Alt+M': 'single_class_mode',
            'Ctrl+Alt+R': 'toggle_draw_square',
            'Ctrl+Alt+C': 'duplicate_shape',
            'Ctrl+Alt+D': 'batch_delete',
            'Ctrl+Alt+T': 'batch_convert',
            'Ctrl+Alt+L': 'color_dialog',
            'F2': 'show_shortcuts',
            'F12': 'about'
        }
        
        all_found = True
        for shortcut, action in expected_shortcuts.items():
            if shortcut in content and action in content:
                print(f"  ✅ {shortcut} -> {action}")
            else:
                print(f"  ❌ 未找到 {shortcut} -> {action}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False

def test_removed_shortcuts():
    """测试4: 验证移除的重复快捷键"""
    print("🚫 测试4: 验证移除的重复快捷键...")
    
    try:
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查应该移除的快捷键
        removed_shortcuts = ['Ctrl+P', 'Ctrl+Shift+P', 'F9', 'Ctrl+B', 'Ctrl+Shift+C']
        
        all_removed = True
        for shortcut in removed_shortcuts:
            # 查找包含快捷键的行
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if shortcut in line and 'action(' in line and not line.strip().startswith('#'):
                    # 检查是否设置为None
                    if 'None' in line:
                        print(f"  ✅ {shortcut} 已正确设置为 None")
                    else:
                        print(f"  ❌ {shortcut} 仍在第{line_num}行: {line.strip()}")
                        all_removed = False
                        break
        
        if all_removed:
            print("  ✅ 所有重复快捷键已正确移除")
        
        return all_removed
        
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False

def test_file_integrity():
    """测试5: 验证文件完整性"""
    print("📁 测试5: 验证文件完整性...")
    
    required_files = [
        'labelImg.py',
        'libs/shortcut_manager.py',
        'shortcut_conflict_resolution_plan.md',
        'shortcut_fix_verification_report.json'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def generate_test_report(results: Dict[str, bool]):
    """生成测试报告"""
    print("\n📄 生成测试报告...")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    report = {
        "test_date": "2025-01-31",
        "test_summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
        },
        "test_results": {
            test_name: "PASS" if result else "FAIL" 
            for test_name, result in results.items()
        },
        "recommendations": []
    }
    
    # 添加建议
    if failed_tests == 0:
        report["recommendations"].append("✅ 所有测试通过！快捷键系统修复成功。")
    else:
        report["recommendations"].append("❌ 部分测试失败，需要进一步检查和修复。")
        
        if not results.get("conflict_resolution", True):
            report["recommendations"].append("- 重新运行冲突检测和修复脚本")
        if not results.get("shortcut_manager_import", True):
            report["recommendations"].append("- 检查快捷键管理器模块的导入路径")
        if not results.get("modified_shortcuts", True):
            report["recommendations"].append("- 验证快捷键修改是否正确应用")
        if not results.get("removed_shortcuts", True):
            report["recommendations"].append("- 检查主程序中的重复快捷键是否正确移除")
    
    # 保存报告
    with open("shortcut_system_test_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 测试报告已保存到: shortcut_system_test_report.json")
    return report

def main():
    """主函数"""
    print("="*80)
    print("快捷键系统测试")
    print("="*80)
    
    # 运行所有测试
    results = {}
    
    results["conflict_resolution"] = test_conflict_resolution()
    results["shortcut_manager_import"], _ = test_shortcut_manager_import()
    results["modified_shortcuts"] = test_modified_shortcuts()
    results["removed_shortcuts"] = test_removed_shortcuts()
    results["file_integrity"] = test_file_integrity()
    
    # 生成报告
    report = generate_test_report(results)
    
    # 显示总结
    print(f"\n🎯 测试完成!")
    print(f"   总计: {report['test_summary']['total_tests']} 个测试")
    print(f"   通过: {report['test_summary']['passed_tests']} 个")
    print(f"   失败: {report['test_summary']['failed_tests']} 个")
    print(f"   成功率: {report['test_summary']['success_rate']}")
    
    # 显示建议
    print(f"\n💡 建议:")
    for recommendation in report["recommendations"]:
        print(f"   {recommendation}")
    
    # 返回是否所有测试都通过
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
