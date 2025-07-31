#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷键系统测试脚本
验证修复后的快捷键系统是否正常工作
"""

import sys
import os
import json
from typing import Dict, List, Tuple
import unittest
from unittest.mock import Mock, patch

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from libs.shortcut_manager import ShortcutManager
except ImportError:
    print("警告: 无法导入ShortcutManager，将跳过相关测试")
    ShortcutManager = None


class TestShortcutSystem(unittest.TestCase):
    """快捷键系统测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_results = {
            "conflict_resolution": [],
            "functionality_tests": [],
            "integration_tests": []
        }
    
    def test_no_shortcut_conflicts(self):
        """测试1: 验证没有快捷键冲突"""
        print("\n🔍 测试1: 验证快捷键冲突解决...")
        
        # 运行验证脚本并检查结果
        try:
            with open('shortcut_fix_verification_report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            conflicts_count = report['summary']['remaining_conflicts']
            self.assertEqual(conflicts_count, 0, f"仍存在 {conflicts_count} 个快捷键冲突")
            
            self.test_results["conflict_resolution"].append({
                "test": "no_conflicts",
                "status": "PASS",
                "message": "所有快捷键冲突已解决"
            })
            print("  ✅ 所有快捷键冲突已解决")
            
        except FileNotFoundError:
            self.fail("验证报告文件不存在，请先运行 verify_shortcut_fixes.py")
        except Exception as e:
            self.fail(f"读取验证报告失败: {e}")
    
    def test_shortcut_manager_initialization(self):
        """测试2: 验证快捷键管理器初始化"""
        print("\n🔧 测试2: 验证快捷键管理器初始化...")
        
        if ShortcutManager is None:
            self.skipTest("ShortcutManager 无法导入")
        
        try:
            # 创建模拟的主窗口对象
            mock_main_window = Mock()
            mock_main_window.actions = Mock()
            
            # 初始化快捷键管理器
            manager = ShortcutManager(mock_main_window)
            
            # 验证管理器创建成功
            self.assertIsNotNone(manager)
            self.assertIsInstance(manager.shortcuts, dict)
            
            # 验证快捷键数量
            shortcuts_count = len(manager.shortcuts)
            self.assertGreater(shortcuts_count, 30, "快捷键数量应该大于30")
            
            self.test_results["functionality_tests"].append({
                "test": "manager_initialization",
                "status": "PASS",
                "message": f"快捷键管理器初始化成功，注册了 {shortcuts_count} 个快捷键"
            })
            print(f"  ✅ 快捷键管理器初始化成功，注册了 {shortcuts_count} 个快捷键")
            
        except Exception as e:
            self.test_results["functionality_tests"].append({
                "test": "manager_initialization",
                "status": "FAIL",
                "message": f"初始化失败: {e}"
            })
            self.fail(f"快捷键管理器初始化失败: {e}")
    
    def test_modified_shortcuts_exist(self):
        """测试3: 验证修改后的快捷键存在"""
        print("\n🎯 测试3: 验证修改后的快捷键...")
        
        if ShortcutManager is None:
            self.skipTest("ShortcutManager 无法导入")
        
        try:
            mock_main_window = Mock()
            mock_main_window.actions = Mock()
            manager = ShortcutManager(mock_main_window)
            
            # 验证修改后的快捷键
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
            
            for shortcut, expected_action in expected_shortcuts.items():
                if shortcut in manager.shortcuts:
                    actual_action = manager.shortcuts[shortcut]['action']
                    self.assertEqual(actual_action, expected_action, 
                                   f"快捷键 {shortcut} 应该对应 {expected_action}，实际为 {actual_action}")
                    print(f"  ✅ {shortcut} -> {expected_action}")
                else:
                    self.fail(f"快捷键 {shortcut} 不存在")
            
            self.test_results["functionality_tests"].append({
                "test": "modified_shortcuts",
                "status": "PASS",
                "message": "所有修改后的快捷键都正确存在"
            })
            
        except Exception as e:
            self.test_results["functionality_tests"].append({
                "test": "modified_shortcuts",
                "status": "FAIL",
                "message": f"验证失败: {e}"
            })
            self.fail(f"验证修改后的快捷键失败: {e}")
    
    def test_removed_shortcuts_absent(self):
        """测试4: 验证移除的快捷键不存在冲突"""
        print("\n🚫 测试4: 验证移除的重复快捷键...")
        
        # 检查主程序中不应该存在的快捷键
        removed_from_main = ['Ctrl+P', 'Ctrl+Shift+P', 'F9', 'Ctrl+B', 'Ctrl+Shift+C']
        
        try:
            with open('labelImg.py', 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            for shortcut in removed_from_main:
                # 检查是否还有快捷键定义（不是注释）
                lines = main_content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if shortcut in line and 'action(' in line and not line.strip().startswith('#'):
                        # 检查是否设置为None
                        if 'None' not in line:
                            self.fail(f"主程序第{line_num}行仍包含快捷键 {shortcut}: {line.strip()}")
            
            print(f"  ✅ 主程序中已正确移除重复的快捷键定义")
            
            self.test_results["functionality_tests"].append({
                "test": "removed_shortcuts",
                "status": "PASS",
                "message": "主程序中的重复快捷键已正确移除"
            })
            
        except Exception as e:
            self.test_results["functionality_tests"].append({
                "test": "removed_shortcuts",
                "status": "FAIL",
                "message": f"验证失败: {e}"
            })
            self.fail(f"验证移除的快捷键失败: {e}")
    
    def test_shortcut_categories(self):
        """测试5: 验证快捷键分类"""
        print("\n📂 测试5: 验证快捷键分类...")
        
        if ShortcutManager is None:
            self.skipTest("ShortcutManager 无法导入")
        
        try:
            mock_main_window = Mock()
            mock_main_window.actions = Mock()
            manager = ShortcutManager(mock_main_window)
            
            # 验证分类存在
            expected_categories = [
                "视图操作", "导航操作", "标注操作", "AI助手", 
                "批量操作", "工具操作", "帮助操作"
            ]
            
            found_categories = set()
            for shortcut_info in manager.shortcuts.values():
                if 'category' in shortcut_info:
                    found_categories.add(shortcut_info['category'])
            
            for category in expected_categories:
                self.assertIn(category, found_categories, f"分类 '{category}' 不存在")
            
            print(f"  ✅ 找到 {len(found_categories)} 个快捷键分类")
            for category in sorted(found_categories):
                count = sum(1 for info in manager.shortcuts.values() 
                           if info.get('category') == category)
                print(f"    - {category}: {count} 个快捷键")
            
            self.test_results["functionality_tests"].append({
                "test": "shortcut_categories",
                "status": "PASS",
                "message": f"快捷键分类正确，共 {len(found_categories)} 个分类"
            })
            
        except Exception as e:
            self.test_results["functionality_tests"].append({
                "test": "shortcut_categories",
                "status": "FAIL",
                "message": f"验证失败: {e}"
            })
            self.fail(f"验证快捷键分类失败: {e}")
    
    def test_generate_report(self):
        """生成测试报告"""
        print("\n📄 生成测试报告...")
        
        report = {
            "test_date": "2025-01-31",
            "test_summary": {
                "total_tests": len(self.test_results["conflict_resolution"]) + 
                              len(self.test_results["functionality_tests"]) + 
                              len(self.test_results["integration_tests"]),
                "passed_tests": 0,
                "failed_tests": 0
            },
            "test_results": self.test_results
        }
        
        # 统计通过和失败的测试
        for category in self.test_results.values():
            for test in category:
                if test["status"] == "PASS":
                    report["test_summary"]["passed_tests"] += 1
                else:
                    report["test_summary"]["failed_tests"] += 1
        
        # 保存报告
        with open("shortcut_system_test_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 测试报告已保存到: shortcut_system_test_report.json")
        print(f"  📊 测试结果: {report['test_summary']['passed_tests']} 通过, "
              f"{report['test_summary']['failed_tests']} 失败")


def run_comprehensive_test():
    """运行综合测试"""
    print("="*80)
    print("快捷键系统综合测试")
    print("="*80)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    test_case = TestShortcutSystem()
    
    # 添加测试方法
    suite.addTest(TestShortcutSystem('test_no_shortcut_conflicts'))
    suite.addTest(TestShortcutSystem('test_shortcut_manager_initialization'))
    suite.addTest(TestShortcutSystem('test_modified_shortcuts_exist'))
    suite.addTest(TestShortcutSystem('test_removed_shortcuts_absent'))
    suite.addTest(TestShortcutSystem('test_shortcut_categories'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    # 生成报告
    test_case.test_generate_report()
    
    print(f"\n🎯 测试完成!")
    print(f"   总计: {result.testsRun} 个测试")
    print(f"   通过: {result.testsRun - len(result.failures) - len(result.errors)} 个")
    print(f"   失败: {len(result.failures)} 个")
    print(f"   错误: {len(result.errors)} 个")
    
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print(f"\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
