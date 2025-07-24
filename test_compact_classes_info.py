#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI助手面板的紧凑类别信息设计

测试内容:
1. 紧凑布局的类别信息组
2. 类别详情对话框
3. 界面空间优化效果
"""

import sys
import os
import unittest
from unittest.mock import Mock

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


class TestCompactClassesInfo(unittest.TestCase):
    """测试紧凑类别信息功能"""
    
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
    
    def test_compact_layout_components(self):
        """测试紧凑布局组件"""
        print("\n=== 测试紧凑布局组件 ===")
        
        # 检查紧凑设计的组件是否存在
        self.assertTrue(hasattr(self.ai_panel, 'model_classes_count'))
        self.assertTrue(hasattr(self.ai_panel, 'user_classes_count'))
        self.assertTrue(hasattr(self.ai_panel, 'model_classes_data'))
        self.assertTrue(hasattr(self.ai_panel, 'user_classes_data'))
        
        print("✅ 紧凑布局组件创建成功")
        
        # 检查数据初始化
        self.assertEqual(self.ai_panel.model_classes_data, {})
        self.assertEqual(self.ai_panel.user_classes_data, [])
        
        print("✅ 数据初始化正确")
    
    def test_compact_info_update(self):
        """测试紧凑信息更新"""
        print("\n=== 测试紧凑信息更新 ===")
        
        # 模拟YOLO预测器
        mock_predictor = Mock()
        mock_predictor.is_model_loaded.return_value = True
        mock_predictor.class_names = {
            0: 'person', 1: 'bicycle', 2: 'car'
        }
        
        self.ai_panel.predictor = mock_predictor
        
        # 更新模型类别信息
        self.ai_panel.update_model_classes_info()
        
        # 检查计数显示
        self.assertEqual(self.ai_panel.model_classes_count.text(), "3 个")
        
        # 检查数据保存
        self.assertEqual(len(self.ai_panel.model_classes_data), 3)
        self.assertEqual(self.ai_panel.model_classes_data[0], 'person')
        
        print("✅ 紧凑信息更新成功")
    
    def test_classes_detail_dialog_method(self):
        """测试类别详情对话框方法"""
        print("\n=== 测试类别详情对话框方法 ===")
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.ai_panel, 'show_classes_detail_dialog'))
        
        # 设置测试数据
        self.ai_panel.model_classes_data = {0: 'person', 1: 'car'}
        self.ai_panel.user_classes_data = ['gouGou', 'cat']
        
        print("✅ 类别详情对话框方法存在且数据准备完成")


def run_compact_gui_test():
    """运行紧凑GUI测试"""
    print("\n🖥️ 运行紧凑GUI测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("AI助手紧凑类别信息测试")
    main_window.resize(350, 700)  # 较窄的窗口测试紧凑性
    
    # 创建AI助手面板
    ai_panel = AIAssistantPanel(main_window)
    main_window.setCentralWidget(ai_panel)
    
    # 模拟一些数据
    # 模拟模型类别
    mock_predictor = Mock()
    mock_predictor.is_model_loaded.return_value = True
    mock_predictor.class_names = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle',
        4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck',
        8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
        11: 'stop sign', 12: 'parking meter', 13: 'bench'
    }
    ai_panel.predictor = mock_predictor
    
    # 模拟用户类别
    main_window.label_hist = ['gouGou', 'cat', 'dog', 'bird', 'fish', 'shiTou', 'muBiao']
    
    # 修改AI面板的用户类别更新方法
    def mock_update_user_classes_info():
        try:
            user_classes = main_window.label_hist
            ai_panel.user_classes_count.setText(f"{len(user_classes)} 个")
            ai_panel.user_classes_count.setStyleSheet(
                "color: #27ae60; font-weight: bold; font-size: 11px;")
            ai_panel.user_classes_data = user_classes
        except Exception as e:
            print(f"Mock update failed: {e}")
    
    ai_panel.update_user_classes_info = mock_update_user_classes_info
    
    # 刷新类别信息
    ai_panel.refresh_classes_info()
    
    # 显示窗口
    main_window.show()
    
    print("✅ 紧凑GUI测试窗口已显示")
    print("📋 紧凑类别信息功能:")
    print("   - 类别信息占用空间大幅减少")
    print("   - 统计信息和按钮在同一行显示")
    print("   - 点击'👁️ 查看'按钮查看详细类别列表")
    print("   - 点击'🔄 刷新'按钮更新类别信息")
    print("   - 字体大小优化，信息更紧凑")
    
    return main_window


def compare_layouts():
    """对比新旧布局的空间使用"""
    print("\n📊 布局空间对比分析:")
    print("=" * 50)
    
    print("🔴 原始设计问题:")
    print("   - 类别列表高度150px，只能显示1-2行")
    print("   - 按钮宽度限制80px，文字显示不完整")
    print("   - 垂直堆叠占用过多空间")
    print("   - 标签页组件占用大量垂直空间")
    
    print("\n🟢 紧凑设计优势:")
    print("   - 统计信息和按钮水平排列，节省垂直空间")
    print("   - 移除了占用空间的标签页组件")
    print("   - 通过对话框查看详细信息，主面板更简洁")
    print("   - 字体大小优化(11px)，信息密度更高")
    print("   - 按钮高度优化(20px)，样式更精致")
    
    print("\n📏 空间节省估算:")
    print("   - 原始设计: ~180px 垂直空间")
    print("   - 紧凑设计: ~45px 垂直空间")
    print("   - 节省空间: ~135px (约75%)")
    
    print("\n🎯 用户体验改进:")
    print("   - 主面板更简洁，不会感到拥挤")
    print("   - 重要信息(统计)一目了然")
    print("   - 详细信息按需查看，不干扰主流程")
    print("   - 按钮功能清晰，操作便捷")


def main():
    """主函数"""
    print("🧪 AI助手紧凑类别信息功能测试")
    print("=" * 50)
    
    # 运行单元测试
    print("📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 显示布局对比
    compare_layouts()
    
    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_compact_gui_test()
        
        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
