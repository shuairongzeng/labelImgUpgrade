#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
删除确认功能的简化测试
不依赖GUI组件，主要测试设置保存/加载逻辑
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.settings import Settings


class MockDeleteConfirmationDialog:
    """模拟删除确认对话框类，用于测试设置逻辑"""
    
    @staticmethod
    def should_show_confirmation(operation_type="delete_current"):
        """检查是否应该显示确认对话框"""
        try:
            settings = Settings()
            settings.load()
            setting_key = f'delete_confirmation_disabled_{operation_type}'
            return not settings.get(setting_key, False)
        except Exception as e:
            print(f"检查删除确认设置失败: {e}")
            return True  # 默认显示确认对话框
    
    @staticmethod
    def reset_confirmation_settings():
        """重置确认设置（恢复显示确认对话框）"""
        try:
            settings = Settings()
            settings.load()
            
            # 重置所有删除确认设置
            for operation_type in ["delete_current", "delete_menu"]:
                setting_key = f'delete_confirmation_disabled_{operation_type}'
                if setting_key in settings.data:
                    del settings.data[setting_key]
            
            settings.save()
            return True
        except Exception as e:
            print(f"重置删除确认设置失败: {e}")
            return False
    
    @staticmethod
    def save_dont_ask_setting(operation_type, dont_ask):
        """保存"不再提示"设置"""
        try:
            settings = Settings()
            settings.load()
            setting_key = f'delete_confirmation_disabled_{operation_type}'
            settings[setting_key] = dont_ask
            settings.save()
            return True
        except Exception as e:
            print(f"保存删除确认设置失败: {e}")
            return False


class TestDeleteConfirmationSettings(unittest.TestCase):
    """测试删除确认设置功能"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.cleanup_test_settings()
    
    def tearDown(self):
        """每个测试后的清理"""
        self.cleanup_test_settings()
    
    def cleanup_test_settings(self):
        """清理测试设置"""
        try:
            settings = Settings()
            settings.load()
            
            # 清理所有删除确认相关设置
            keys_to_remove = []
            for key in settings.data.keys():
                if key.startswith('delete_confirmation_disabled_'):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del settings.data[key]
            
            settings.save()
        except Exception as e:
            print(f"清理测试设置失败: {e}")
    
    def test_default_should_show_confirmation(self):
        """测试默认情况下应该显示确认对话框"""
        self.assertTrue(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertTrue(MockDeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_save_and_load_dont_ask_setting(self):
        """测试保存和加载"不再提示"设置"""
        # 保存"不再提示"设置
        success = MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
        self.assertTrue(success)
        
        # 验证设置已保存
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
        
        # 验证其他操作类型不受影响
        self.assertTrue(MockDeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_reset_confirmation_settings(self):
        """测试重置确认设置"""
        # 先禁用所有确认对话框
        MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
        MockDeleteConfirmationDialog.save_dont_ask_setting("delete_menu", True)
        
        # 验证已禁用
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_menu"))
        
        # 重置设置
        success = MockDeleteConfirmationDialog.reset_confirmation_settings()
        self.assertTrue(success)
        
        # 验证已重置
        self.assertTrue(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertTrue(MockDeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_different_operation_types(self):
        """测试不同操作类型的设置独立性"""
        # 只禁用delete_current的确认
        MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
        
        # 验证设置独立性
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertTrue(MockDeleteConfirmationDialog.should_show_confirmation("delete_menu"))
        
        # 禁用delete_menu的确认
        MockDeleteConfirmationDialog.save_dont_ask_setting("delete_menu", True)
        
        # 验证两个都被禁用
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_settings_persistence(self):
        """测试设置的持久化"""
        # 保存设置
        MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
        
        # 创建新的Settings实例来模拟重启应用
        settings = Settings()
        settings.load()
        
        # 验证设置已持久化
        self.assertTrue(settings.get('delete_confirmation_disabled_delete_current', False))
        
        # 通过新实例验证
        self.assertFalse(MockDeleteConfirmationDialog.should_show_confirmation("delete_current"))
    
    def test_error_handling(self):
        """测试错误处理 - 简化版本"""
        # 测试不存在的操作类型
        result = MockDeleteConfirmationDialog.should_show_confirmation("nonexistent_type")
        self.assertTrue(result)  # 应该返回默认值True

        # 测试保存不存在的操作类型
        result = MockDeleteConfirmationDialog.save_dont_ask_setting("nonexistent_type", True)
        self.assertTrue(result)  # 应该能正常保存


class TestSettingsIntegration(unittest.TestCase):
    """测试与Settings类的集成"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.cleanup_test_settings()
    
    def tearDown(self):
        """每个测试后的清理"""
        self.cleanup_test_settings()
    
    def cleanup_test_settings(self):
        """清理测试设置"""
        try:
            settings = Settings()
            settings.load()
            
            # 清理所有删除确认相关设置
            keys_to_remove = []
            for key in settings.data.keys():
                if key.startswith('delete_confirmation_disabled_'):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del settings.data[key]
            
            settings.save()
        except Exception as e:
            print(f"清理测试设置失败: {e}")
    
    def test_settings_file_operations(self):
        """测试设置文件操作"""
        settings = Settings()
        
        # 测试加载
        load_success = settings.load()
        # 注意：如果文件不存在，load()可能返回False，这是正常的
        
        # 测试保存
        settings['test_key'] = 'test_value'
        save_success = settings.save()
        self.assertTrue(save_success)
        
        # 测试重新加载
        new_settings = Settings()
        new_settings.load()
        self.assertEqual(new_settings.get('test_key'), 'test_value')
        
        # 清理测试数据
        del new_settings.data['test_key']
        new_settings.save()


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行删除确认功能设置测试")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDeleteConfirmationSettings))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}")
            print(f"  {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}")
            print(f"  {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n测试{'成功' if success else '失败'}！")
    
    return success


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
