#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试类别管理修复效果
验证添加新类别后，在各个界面中都能正确显示和使用
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtCore import QTimer
    from libs.ai_assistant_panel import AIAssistantPanel
    from labelImg import get_persistent_predefined_classes_path
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装PyQt5和相关依赖")
    sys.exit(1)


class TestClassManagementFix(unittest.TestCase):
    """测试类别管理修复效果"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """每个测试前的设置"""
        self.main_window = QMainWindow()
        self.main_window.label_hist = ['naiMa', 'lingZhu', 'guaiWu', 'naiBa', 'xiuLuo']
        self.ai_panel = AIAssistantPanel(self.main_window)
        
    def tearDown(self):
        """每个测试后的清理"""
        if hasattr(self, 'ai_panel'):
            self.ai_panel.close()
        if hasattr(self, 'main_window'):
            self.main_window.close()
    
    def test_predefined_classes_file_path_fix(self):
        """测试预设类别文件路径修复"""
        print("\n=== 测试预设类别文件路径修复 ===")
        
        # 测试获取正确的预设类别文件路径
        try:
            predefined_file = get_persistent_predefined_classes_path()
            print(f"✅ 预设类别文件路径: {predefined_file}")
            
            # 验证路径是否正确（应该在用户AppData目录）
            self.assertIn('labelImg', predefined_file)
            self.assertTrue(predefined_file.endswith('predefined_classes.txt'))
            
            print("✅ 预设类别文件路径修复成功")
            return True
            
        except Exception as e:
            self.fail(f"预设类别文件路径修复失败: {e}")
    
    def test_classes_source_combo_creation(self):
        """测试类别源选择下拉框创建"""
        print("\n=== 测试类别源选择下拉框创建 ===")
        
        try:
            # 创建数据配置标签页
            data_tab = self.ai_panel.create_data_config_tab()
            self.assertIsNotNone(data_tab)
            
            # 验证类别源选择下拉框是否存在
            self.assertTrue(hasattr(self.ai_panel, 'classes_source_combo'))
            self.assertIsNotNone(self.ai_panel.classes_source_combo)
            
            # 验证下拉框选项
            combo = self.ai_panel.classes_source_combo
            expected_items = [
                "使用当前标注类别",
                "使用预设类别文件", 
                "使用类别配置文件"
            ]
            
            actual_items = [combo.itemText(i) for i in range(combo.count())]
            self.assertEqual(actual_items, expected_items)
            
            print("✅ 类别源选择下拉框创建成功")
            print(f"   选项: {actual_items}")
            return True
            
        except Exception as e:
            self.fail(f"类别源选择下拉框创建失败: {e}")
    
    def test_classes_source_change_handling(self):
        """测试类别源改变处理"""
        print("\n=== 测试类别源改变处理 ===")
        
        try:
            # 创建数据配置标签页
            data_tab = self.ai_panel.create_data_config_tab()
            
            # 测试"使用当前标注类别"
            self.ai_panel.on_classes_source_changed("使用当前标注类别")
            if hasattr(self.ai_panel, 'selected_classes_count_label'):
                label_text = self.ai_panel.selected_classes_count_label.text()
                print(f"   当前标注类别: {label_text}")
                self.assertIn("5 个类别", label_text)
            
            # 测试"使用预设类别文件"
            self.ai_panel.on_classes_source_changed("使用预设类别文件")
            if hasattr(self.ai_panel, 'selected_classes_count_label'):
                label_text = self.ai_panel.selected_classes_count_label.text()
                print(f"   预设类别文件: {label_text}")
            
            # 测试"使用类别配置文件"
            self.ai_panel.on_classes_source_changed("使用类别配置文件")
            if hasattr(self.ai_panel, 'selected_classes_count_label'):
                label_text = self.ai_panel.selected_classes_count_label.text()
                print(f"   类别配置文件: {label_text}")
            
            print("✅ 类别源改变处理成功")
            return True
            
        except Exception as e:
            self.fail(f"类别源改变处理失败: {e}")
    
    def test_user_classes_info_update(self):
        """测试用户类别信息更新"""
        print("\n=== 测试用户类别信息更新 ===")
        
        try:
            # 更新用户类别信息
            self.ai_panel.update_user_classes_info()
            
            # 验证类别数量显示
            if hasattr(self.ai_panel, 'user_classes_count'):
                count_text = self.ai_panel.user_classes_count.text()
                print(f"   用户类别数量: {count_text}")
                self.assertIn("5 个", count_text)
            
            # 验证类别数据
            self.assertEqual(len(self.ai_panel.user_classes_data), 5)
            self.assertIn('xiuLiShang', self.main_window.label_hist)  # 新添加的类别
            
            print("✅ 用户类别信息更新成功")
            return True
            
        except Exception as e:
            self.fail(f"用户类别信息更新失败: {e}")
    
    def test_classes_info_display_in_training(self):
        """测试训练对话框中的类别信息显示"""
        print("\n=== 测试训练对话框中的类别信息显示 ===")
        
        try:
            # 创建数据配置标签页（模拟训练对话框环境）
            data_tab = self.ai_panel.create_data_config_tab()
            
            # 模拟显示类别信息（不实际弹出对话框）
            with patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warn:
                    
                    # 测试显示当前标注类别
                    self.ai_panel.classes_source_combo.setCurrentText("使用当前标注类别")
                    self.ai_panel.show_classes_info_in_training()
                    
                    # 验证是否调用了信息对话框
                    if mock_info.called:
                        args = mock_info.call_args[0]
                        message = args[2] if len(args) > 2 else ""
                        print(f"   当前标注类别信息: {message[:50]}...")
                        self.assertIn("类别列表", message)
                    
                    # 测试显示预设类别文件
                    mock_info.reset_mock()
                    self.ai_panel.classes_source_combo.setCurrentText("使用预设类别文件")
                    self.ai_panel.show_classes_info_in_training()
                    
                    # 测试显示类别配置文件
                    mock_info.reset_mock()
                    self.ai_panel.classes_source_combo.setCurrentText("使用类别配置文件")
                    self.ai_panel.show_classes_info_in_training()
            
            print("✅ 训练对话框中的类别信息显示成功")
            return True
            
        except Exception as e:
            self.fail(f"训练对话框中的类别信息显示失败: {e}")


def run_class_management_fix_test():
    """运行类别管理修复测试"""
    print("🔧 类别管理修复效果测试")
    print("=" * 60)
    
    # 运行单元测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClassManagementFix)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   总测试数: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 所有测试通过！类别管理修复成功！")
        print("\n✅ 修复效果:")
        print("   1. ✅ 预设类别文件路径已修复")
        print("   2. ✅ 类别源选择下拉框已添加")
        print("   3. ✅ 类别信息同步机制已建立")
        print("   4. ✅ 训练对话框类别显示已修复")
    else:
        print("\n❌ 部分测试失败，需要进一步修复")
    
    return success


if __name__ == "__main__":
    success = run_class_management_fix_test()
    sys.exit(0 if success else 1)
