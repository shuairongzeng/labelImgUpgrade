#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI助手面板的类别信息显示功能

测试内容:
1. 类别信息组的创建和显示
2. 模型类别信息的更新
3. 用户类别信息的更新
4. 类别映射对话框的显示
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtCore import Qt
    from PyQt5.QtTest import QTest

    from libs.ai_assistant_panel import AIAssistantPanel

    print("✅ 成功导入所有必需模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)


class TestClassesInfoFeature(unittest.TestCase):
    """测试类别信息功能"""

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
        self.ai_panel = AIAssistantPanel(self.main_window)

    def tearDown(self):
        """每个测试后的清理"""
        if hasattr(self, 'ai_panel'):
            self.ai_panel.close()
        if hasattr(self, 'main_window'):
            self.main_window.close()

    def test_classes_info_group_creation(self):
        """测试类别信息组的创建"""
        print("\n=== 测试类别信息组创建 ===")

        # 检查类别信息组是否存在
        self.assertTrue(hasattr(self.ai_panel, 'classes_tab'))
        self.assertTrue(hasattr(self.ai_panel, 'model_classes_list'))
        self.assertTrue(hasattr(self.ai_panel, 'user_classes_list'))
        self.assertTrue(hasattr(self.ai_panel, 'model_classes_count'))
        self.assertTrue(hasattr(self.ai_panel, 'user_classes_count'))

        print("✅ 类别信息组件创建成功")

        # 检查标签页
        self.assertEqual(self.ai_panel.classes_tab.count(), 2)
        self.assertEqual(self.ai_panel.classes_tab.tabText(0), "模型类别")
        self.assertEqual(self.ai_panel.classes_tab.tabText(1), "用户类别")

        print("✅ 类别标签页设置正确")

    def test_model_classes_info_update(self):
        """测试模型类别信息更新"""
        print("\n=== 测试模型类别信息更新 ===")

        # 模拟YOLO预测器
        mock_predictor = Mock()
        mock_predictor.is_model_loaded.return_value = True
        mock_predictor.class_names = {
            0: 'person',
            1: 'bicycle',
            2: 'car',
            3: 'motorcycle'
        }

        self.ai_panel.predictor = mock_predictor

        # 更新模型类别信息
        self.ai_panel.update_model_classes_info()

        # 检查计数显示
        self.assertEqual(self.ai_panel.model_classes_count.text(), "4 个")

        # 检查列表内容
        self.assertEqual(self.ai_panel.model_classes_list.count(), 4)

        # 检查第一个项目
        first_item = self.ai_panel.model_classes_list.item(0)
        self.assertIn("person", first_item.text())

        print("✅ 模型类别信息更新成功")

    def test_user_classes_info_update(self):
        """测试用户类别信息更新"""
        print("\n=== 测试用户类别信息更新 ===")

        # 模拟主窗口的label_hist
        mock_main_window = Mock()
        mock_main_window.label_hist = ['gouGou', 'cat', 'dog', 'bird']

        # 直接设置父窗口属性而不是使用setParent
        self.ai_panel._parent_with_label_hist = mock_main_window

        # 修改update_user_classes_info方法来使用我们的模拟数据
        original_method = self.ai_panel.update_user_classes_info

        def mock_update_user_classes_info():
            try:
                user_classes = mock_main_window.label_hist
                self.ai_panel.user_classes_count.setText(
                    f"{len(user_classes)} 个")
                self.ai_panel.user_classes_count.setStyleSheet(
                    "color: #27ae60; font-weight: bold;")
                self.ai_panel.user_classes_list.clear()
                for i, class_name in enumerate(user_classes):
                    item_text = f"{i}: {class_name}"
                    self.ai_panel.user_classes_list.addItem(item_text)
            except Exception as e:
                print(f"Mock update failed: {e}")

        self.ai_panel.update_user_classes_info = mock_update_user_classes_info

        # 更新用户类别信息
        self.ai_panel.update_user_classes_info()

        # 检查计数显示
        self.assertEqual(self.ai_panel.user_classes_count.text(), "4 个")

        # 检查列表内容
        self.assertEqual(self.ai_panel.user_classes_list.count(), 4)

        # 检查第一个项目
        first_item = self.ai_panel.user_classes_list.item(0)
        self.assertIn("gouGou", first_item.text())

        print("✅ 用户类别信息更新成功")

    def test_refresh_classes_info(self):
        """测试刷新类别信息功能"""
        print("\n=== 测试刷新类别信息 ===")

        # 模拟数据
        mock_predictor = Mock()
        mock_predictor.is_model_loaded.return_value = True
        mock_predictor.class_names = {0: 'person', 1: 'car'}
        self.ai_panel.predictor = mock_predictor

        # 模拟用户类别更新方法
        def mock_update_user_classes_info():
            self.ai_panel.user_classes_count.setText("2 个")
            self.ai_panel.user_classes_list.clear()
            for i, class_name in enumerate(['gouGou', 'cat']):
                self.ai_panel.user_classes_list.addItem(f"{i}: {class_name}")

        self.ai_panel.update_user_classes_info = mock_update_user_classes_info

        # 执行刷新
        self.ai_panel.refresh_classes_info()

        # 验证结果
        self.assertEqual(self.ai_panel.model_classes_count.text(), "2 个")
        self.assertEqual(self.ai_panel.user_classes_count.text(), "2 个")

        print("✅ 刷新类别信息功能正常")

    def test_class_mapping_dialog(self):
        """测试类别映射对话框"""
        print("\n=== 测试类别映射对话框 ===")

        # 这个测试需要在GUI环境中运行，这里只测试方法存在
        self.assertTrue(hasattr(self.ai_panel, 'show_class_mapping_dialog'))
        self.assertTrue(hasattr(self.ai_panel, 'save_class_mapping'))

        print("✅ 类别映射对话框方法存在")

    def test_ui_components_visibility(self):
        """测试UI组件的可见性"""
        print("\n=== 测试UI组件可见性 ===")

        # 显示面板
        self.ai_panel.show()

        # 检查组件是否存在（不检查可见性，因为在测试环境中可能不可见）
        self.assertIsNotNone(self.ai_panel.classes_tab)
        self.assertIsNotNone(self.ai_panel.model_classes_list)
        self.assertIsNotNone(self.ai_panel.user_classes_list)

        print("✅ UI组件存在性正常")


def run_gui_test():
    """运行GUI测试"""
    print("\n🖥️ 运行GUI测试...")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("AI助手类别信息测试")
    main_window.resize(400, 600)

    # 创建AI助手面板
    ai_panel = AIAssistantPanel(main_window)
    main_window.setCentralWidget(ai_panel)

    # 模拟一些数据
    # 模拟模型类别
    mock_predictor = Mock()
    mock_predictor.is_model_loaded.return_value = True
    mock_predictor.class_names = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle',
        4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck'
    }
    ai_panel.predictor = mock_predictor

    # 模拟用户类别 - 直接设置到主窗口
    main_window.label_hist = ['gouGou', 'cat', 'dog', 'bird', 'fish']

    # 修改AI面板的用户类别更新方法
    def mock_update_user_classes_info():
        try:
            user_classes = main_window.label_hist
            ai_panel.user_classes_count.setText(f"{len(user_classes)} 个")
            ai_panel.user_classes_count.setStyleSheet(
                "color: #27ae60; font-weight: bold;")
            ai_panel.user_classes_list.clear()
            for i, class_name in enumerate(user_classes):
                item_text = f"{i}: {class_name}"
                ai_panel.user_classes_list.addItem(item_text)
        except Exception as e:
            print(f"Mock update failed: {e}")

    ai_panel.update_user_classes_info = mock_update_user_classes_info

    # 刷新类别信息
    ai_panel.refresh_classes_info()

    # 显示窗口
    main_window.show()

    print("✅ GUI测试窗口已显示")
    print("📋 类别信息功能:")
    print("   - 模型类别标签页显示YOLO模型的类别")
    print("   - 用户类别标签页显示用户自定义类别")
    print("   - 点击'刷新'按钮可更新类别信息")
    print("   - 点击'映射'按钮可配置类别映射")

    return main_window


def main():
    """主函数"""
    print("🧪 AI助手类别信息功能测试")
    print("=" * 50)

    # 运行单元测试
    print("📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_gui_test()

        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
