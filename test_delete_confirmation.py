#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
删除确认功能的单元测试
测试智能删除确认对话框的各项功能
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest
except ImportError:
    print("PyQt5 not available, skipping GUI tests")
    sys.exit(0)

from libs.delete_confirmation_dialog import DeleteConfirmationDialog, SimpleDeleteConfirmationDialog
from libs.settings import Settings


class TestDeleteConfirmationDialog(unittest.TestCase):
    """测试删除确认对话框"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """每个测试前的设置"""
        # 创建临时测试文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_file.write(b'test image data')
        self.temp_file.close()
        
        # 清理测试设置
        self.cleanup_test_settings()
    
    def tearDown(self):
        """每个测试后的清理"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        
        # 清理测试设置
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
    
    def test_dialog_creation(self):
        """测试对话框创建"""
        dialog = DeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name,
            operation_type="delete_current"
        )
        
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.file_path, self.temp_file.name)
        self.assertEqual(dialog.operation_type, "delete_current")
        self.assertFalse(dialog.dont_ask_again)
    
    def test_should_show_confirmation_default(self):
        """测试默认情况下应该显示确认对话框"""
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_settings_save_and_load(self):
        """测试设置的保存和加载"""
        # 创建对话框并模拟用户勾选"不再提示"
        dialog = DeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name,
            operation_type="delete_current"
        )
        
        # 模拟勾选复选框
        dialog.dont_ask_checkbox.setChecked(True)
        
        # 保存设置
        dialog.save_settings()
        
        # 验证设置已保存
        self.assertFalse(DeleteConfirmationDialog.should_show_confirmation("delete_current"))
        
        # 验证其他操作类型不受影响
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_reset_confirmation_settings(self):
        """测试重置确认设置"""
        # 先禁用确认对话框
        settings = Settings()
        settings.load()
        settings['delete_confirmation_disabled_delete_current'] = True
        settings['delete_confirmation_disabled_delete_menu'] = True
        settings.save()
        
        # 验证已禁用
        self.assertFalse(DeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertFalse(DeleteConfirmationDialog.should_show_confirmation("delete_menu"))
        
        # 重置设置
        success = DeleteConfirmationDialog.reset_confirmation_settings()
        self.assertTrue(success)
        
        # 验证已重置
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_current"))
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_menu"))
    
    def test_simple_dialog_creation(self):
        """测试简化对话框创建"""
        dialog = SimpleDeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name
        )
        
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.file_path, self.temp_file.name)
    
    def test_file_info_display(self):
        """测试文件信息显示"""
        dialog = DeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name,
            operation_type="delete_current"
        )
        
        # 检查文件信息组件是否正确创建
        file_info_widget = dialog.create_file_info_widget()
        self.assertIsNotNone(file_info_widget)
    
    def test_dialog_ui_components(self):
        """测试对话框UI组件"""
        dialog = DeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name,
            operation_type="delete_current"
        )
        
        # 检查关键UI组件是否存在
        self.assertIsNotNone(dialog.dont_ask_checkbox)
        self.assertIsNotNone(dialog.delete_button)
        self.assertIsNotNone(dialog.cancel_button)
        
        # 检查初始状态
        self.assertFalse(dialog.dont_ask_checkbox.isChecked())
        self.assertFalse(dialog.delete_button.isDefault())  # 删除按钮不应该是默认按钮
    
    @patch('libs.delete_confirmation_dialog.Settings')
    def test_settings_error_handling(self, mock_settings_class):
        """测试设置操作的错误处理"""
        # 模拟设置加载失败
        mock_settings = Mock()
        mock_settings.load.side_effect = Exception("Settings load error")
        mock_settings_class.return_value = mock_settings
        
        # 应该返回默认值（True）
        result = DeleteConfirmationDialog.should_show_confirmation("delete_current")
        self.assertTrue(result)
        
        # 模拟设置保存失败
        mock_settings.load.side_effect = None
        mock_settings.save.side_effect = Exception("Settings save error")
        
        dialog = DeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name,
            operation_type="delete_current"
        )
        
        # 保存设置不应该抛出异常
        try:
            dialog.save_settings()
        except Exception:
            self.fail("save_settings() raised an exception unexpectedly")


class TestDeleteConfirmationIntegration(unittest.TestCase):
    """集成测试：测试删除确认功能与主应用的集成"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """每个测试前的设置"""
        # 创建临时测试文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_file.write(b'test image data')
        self.temp_file.close()
    
    def tearDown(self):
        """每个测试后的清理"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_dialog_workflow(self):
        """测试完整的对话框工作流程"""
        # 第一次：显示完整对话框
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_current"))
        
        dialog = DeleteConfirmationDialog(
            parent=None,
            file_path=self.temp_file.name,
            operation_type="delete_current"
        )
        
        # 模拟用户勾选"不再提示"并确认
        dialog.dont_ask_checkbox.setChecked(True)
        dialog.save_settings()
        
        # 第二次：应该不显示完整对话框
        self.assertFalse(DeleteConfirmationDialog.should_show_confirmation("delete_current"))
        
        # 重置设置
        DeleteConfirmationDialog.reset_confirmation_settings()
        
        # 第三次：应该重新显示完整对话框
        self.assertTrue(DeleteConfirmationDialog.should_show_confirmation("delete_current"))


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行删除确认功能测试")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDeleteConfirmationDialog))
    suite.addTests(loader.loadTestsFromTestCase(TestDeleteConfirmationIntegration))
    
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
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n测试{'成功' if success else '失败'}！")
    
    return success


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
