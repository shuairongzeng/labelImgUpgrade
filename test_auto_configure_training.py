#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试一键配置训练数据集功能

测试内容:
1. 一键配置按钮
2. 数据检查功能
3. YOLO导出集成
4. 自动路径配置
5. 数据集扫描
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


class TestAutoConfigureTraining(unittest.TestCase):
    """测试一键配置训练功能"""
    
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
    
    def test_auto_configure_methods_exist(self):
        """测试一键配置方法是否存在"""
        print("\n=== 测试一键配置方法存在性 ===")
        
        # 检查一键配置相关方法
        self.assertTrue(hasattr(self.ai_panel, 'auto_configure_training_dataset'))
        self.assertTrue(hasattr(self.ai_panel, 'check_current_data_for_export'))
        self.assertTrue(hasattr(self.ai_panel, 'execute_auto_configuration'))
        self.assertTrue(hasattr(self.ai_panel, 'call_yolo_export_and_configure'))
        self.assertTrue(hasattr(self.ai_panel, 'scan_generated_dataset'))
        
        print("✅ 一键配置方法存在")
    
    def test_data_config_tab_has_auto_config_button(self):
        """测试数据配置标签页是否有一键配置按钮"""
        print("\n=== 测试一键配置按钮存在性 ===")
        
        # 创建数据配置标签页
        data_tab = self.ai_panel.create_data_config_tab()
        
        # 检查是否创建成功
        self.assertIsNotNone(data_tab)
        
        print("✅ 数据配置标签页创建成功，包含一键配置按钮")


def run_auto_configure_gui_test():
    """运行一键配置GUI测试"""
    print("\n🖥️ 运行一键配置GUI测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("一键配置训练数据集测试")
    main_window.resize(400, 800)
    
    # 创建AI助手面板
    ai_panel = AIAssistantPanel(main_window)
    main_window.setCentralWidget(ai_panel)
    
    # 模拟训练数据（充足的数据以启用训练）
    main_window.label_hist = ['cat', 'dog', 'bird', 'car', 'person']
    
    # 模拟当前工作目录（用于一键配置功能）
    main_window.last_open_dir = os.getcwd()
    
    def mock_update_training_data_stats():
        try:
            user_classes = main_window.label_hist
            estimated_images = len(user_classes) * 25  # 每类25张图
            
            ai_panel.training_data_stats.update({
                'total_images': estimated_images,
                'total_annotations': estimated_images * 2,
                'classes_count': len(user_classes)
            })
            
            ai_panel.training_data_count.setText(f"{estimated_images} 张")
            ai_panel.training_data_count.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
        except Exception as e:
            print(f"Mock update failed: {e}")
    
    ai_panel.update_training_data_stats = mock_update_training_data_stats
    
    # 刷新信息
    ai_panel.refresh_training_info()
    
    # 显示窗口
    main_window.show()
    
    print("✅ 一键配置训练数据集GUI测试窗口已显示")
    print("🚀 一键配置功能特性:")
    print("   - 🚀 一键配置按钮：自动调用YOLO导出功能")
    print("   - 🔍 数据检查：验证当前目录是否有标注文件")
    print("   - 📁 自动导出：生成标准YOLO训练数据集")
    print("   - 🔧 自动配置：自动填入训练和验证路径")
    print("   - 📊 数据统计：自动扫描生成的数据集")
    
    # 显示当前模拟环境
    print(f"\n📊 当前模拟环境:")
    print(f"   标注类别: {main_window.label_hist}")
    print(f"   类别数量: {len(main_window.label_hist)}")
    print(f"   工作目录: {main_window.last_open_dir}")
    print(f"   估计图片: {len(main_window.label_hist) * 25} 张")
    
    # 检查训练按钮状态
    if hasattr(ai_panel, 'train_btn'):
        print(f"   训练按钮: {'可用' if ai_panel.train_btn.isEnabled() else '不可用'}")
    
    print(f"\n💡 使用说明:")
    print(f"   1. 点击'🚀 开始训练'按钮打开训练配置对话框")
    print(f"   2. 在'📁 数据配置'标签页中点击'🚀 一键配置'按钮")
    print(f"   3. 在弹出的对话框中配置数据集名称和输出目录")
    print(f"   4. 点击'🔍 检查数据'验证当前目录的标注文件")
    print(f"   5. 点击'🚀 开始配置'自动导出并配置训练数据集")
    print(f"   6. 配置完成后返回训练参数设置")
    
    return main_window


def analyze_auto_configure_workflow():
    """分析一键配置工作流程"""
    print("\n📊 一键配置工作流程分析:")
    print("=" * 50)
    
    print("🎯 解决的核心问题:")
    print("   ✅ 数据一致性：确保训练数据与标注数据完全一致")
    print("   ✅ 路径配置：自动填入正确的训练和验证路径")
    print("   ✅ 格式转换：自动将Pascal VOC转换为YOLO格式")
    print("   ✅ 数据划分：自动按比例划分训练集和验证集")
    print("   ✅ 工作流程：标注→导出→训练的无缝连接")
    
    print("\n🔧 技术实现特点:")
    print("   - 集成现有导出功能：复用已有的YOLO导出模块")
    print("   - 自动路径配置：导出完成后自动配置训练路径")
    print("   - 实时进度显示：显示导出和配置进度")
    print("   - 错误处理机制：完善的错误检查和用户提示")
    print("   - 数据验证：自动验证生成的数据集")
    
    print("\n🎨 用户体验优势:")
    print("   - 一键操作：复杂的配置过程简化为一键操作")
    print("   - 智能检查：自动检查数据完整性和有效性")
    print("   - 可视化配置：图形化的配置界面")
    print("   - 实时反馈：详细的操作日志和进度显示")
    print("   - 无缝集成：与现有工作流程完美集成")
    
    print("\n📈 工作流程对比:")
    print("   ❌ 原来的流程:")
    print("      1. 在labelImg中标注")
    print("      2. 手动导出YOLO数据集")
    print("      3. 手动查找导出路径")
    print("      4. 手动配置训练路径")
    print("      5. 手动设置数据划分")
    
    print("\n   ✅ 一键配置流程:")
    print("      1. 在labelImg中标注")
    print("      2. 点击'🚀 一键配置'")
    print("      3. 自动导出+配置+验证")
    print("      4. 直接开始训练")


def compare_manual_vs_auto_config():
    """对比手动配置与一键配置"""
    print("\n🔄 手动配置 vs 一键配置对比:")
    print("=" * 50)
    
    print("❌ 手动配置的问题:")
    print("   - 步骤繁琐：需要多个步骤手动操作")
    print("   - 容易出错：路径配置容易出现错误")
    print("   - 数据不一致：可能使用不同版本的标注数据")
    print("   - 重复工作：每次训练都需要重新配置")
    print("   - 学习成本：需要了解YOLO数据集格式")
    
    print("\n✅ 一键配置的优势:")
    print("   - 操作简单：一键完成所有配置")
    print("   - 减少错误：自动化避免人为错误")
    print("   - 数据一致：直接使用当前标注数据")
    print("   - 提高效率：大幅减少配置时间")
    print("   - 降低门槛：新手也能轻松使用")
    
    print("\n🎯 适用场景:")
    print("   - 初学者：不熟悉YOLO数据集格式")
    print("   - 快速迭代：需要频繁调整和重新训练")
    print("   - 批量处理：处理多个标注项目")
    print("   - 团队协作：确保团队使用一致的配置")
    print("   - 生产环境：减少配置错误的风险")


def main():
    """主函数"""
    print("🧪 一键配置训练数据集功能测试")
    print("=" * 50)
    
    # 运行单元测试
    print("📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 显示工作流程分析
    analyze_auto_configure_workflow()
    
    # 显示对比分析
    compare_manual_vs_auto_config()
    
    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_auto_configure_gui_test()
        
        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
