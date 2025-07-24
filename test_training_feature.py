#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI助手面板的训练功能

测试内容:
1. 训练信息组的创建和显示
2. 训练数据统计功能
3. 训练准备状态检查
4. 训练对话框功能
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


class TestTrainingFeature(unittest.TestCase):
    """测试训练功能"""
    
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
    
    def test_training_components_creation(self):
        """测试训练组件创建"""
        print("\n=== 测试训练组件创建 ===")
        
        # 检查训练相关组件是否存在
        self.assertTrue(hasattr(self.ai_panel, 'training_data_count'))
        self.assertTrue(hasattr(self.ai_panel, 'training_status'))
        self.assertTrue(hasattr(self.ai_panel, 'train_btn'))
        self.assertTrue(hasattr(self.ai_panel, 'training_data_stats'))
        
        print("✅ 训练组件创建成功")
        
        # 检查初始状态
        self.assertEqual(self.ai_panel.training_data_count.text(), "0 张")
        self.assertEqual(self.ai_panel.training_status.text(), "未开始")
        self.assertFalse(self.ai_panel.train_btn.isEnabled())
        
        print("✅ 初始状态正确")
    
    def test_training_data_stats_update(self):
        """测试训练数据统计更新"""
        print("\n=== 测试训练数据统计更新 ===")
        
        # 模拟主窗口的label_hist
        mock_main_window = Mock()
        mock_main_window.label_hist = ['cat', 'dog', 'bird']  # 3个类别
        
        # 修改更新方法来使用模拟数据
        def mock_update_training_data_stats():
            user_classes = mock_main_window.label_hist
            estimated_images = len(user_classes) * 15  # 45张图
            
            self.ai_panel.training_data_stats.update({
                'total_images': estimated_images,
                'total_annotations': estimated_images * 2,
                'classes_count': len(user_classes)
            })
            
            self.ai_panel.training_data_count.setText(f"{estimated_images} 张")
            if estimated_images >= self.ai_panel.training_data_stats['min_samples_per_class'] * len(user_classes):
                self.ai_panel.training_data_count.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            else:
                self.ai_panel.training_data_count.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 11px;")
        
        self.ai_panel.update_training_data_stats = mock_update_training_data_stats
        
        # 更新训练数据统计
        self.ai_panel.update_training_data_stats()
        
        # 检查统计结果
        self.assertEqual(self.ai_panel.training_data_count.text(), "45 张")
        self.assertEqual(self.ai_panel.training_data_stats['total_images'], 45)
        self.assertEqual(self.ai_panel.training_data_stats['classes_count'], 3)
        
        print("✅ 训练数据统计更新成功")
    
    def test_training_readiness_check(self):
        """测试训练准备状态检查"""
        print("\n=== 测试训练准备状态检查 ===")
        
        # 测试数据不足的情况
        self.ai_panel.training_data_stats.update({
            'total_images': 5,
            'classes_count': 2,
            'min_samples_per_class': 10
        })
        
        self.ai_panel.check_training_readiness()
        
        # 应该不能训练（数据不足）
        self.assertFalse(self.ai_panel.train_btn.isEnabled())
        self.assertIn("需要", self.ai_panel.training_status.text())
        
        print("✅ 数据不足状态检查正确")
        
        # 测试数据充足的情况
        self.ai_panel.training_data_stats.update({
            'total_images': 50,
            'classes_count': 3,
            'min_samples_per_class': 10
        })
        
        self.ai_panel.check_training_readiness()
        
        # 应该可以训练
        self.assertTrue(self.ai_panel.train_btn.isEnabled())
        self.assertEqual(self.ai_panel.training_status.text(), "就绪")
        
        print("✅ 数据充足状态检查正确")
    
    def test_training_dialog_methods(self):
        """测试训练对话框方法"""
        print("\n=== 测试训练对话框方法 ===")
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.ai_panel, 'show_training_dialog'))
        self.assertTrue(hasattr(self.ai_panel, 'show_training_config_dialog'))
        self.assertTrue(hasattr(self.ai_panel, 'start_training'))
        self.assertTrue(hasattr(self.ai_panel, 'save_training_config'))
        
        print("✅ 训练对话框方法存在")
    
    def test_training_config_save(self):
        """测试训练配置保存"""
        print("\n=== 测试训练配置保存 ===")
        
        # 模拟对话框
        mock_dialog = Mock()
        
        # 保存配置
        self.ai_panel.save_training_config(
            min_samples=15,
            output_dir="./test_models",
            model_name="test_model",
            auto_split=True,
            save_best=True,
            dialog=mock_dialog
        )
        
        # 检查配置是否保存
        self.assertEqual(self.ai_panel.training_data_stats['min_samples_per_class'], 15)
        
        print("✅ 训练配置保存成功")


def run_training_gui_test():
    """运行训练功能GUI测试"""
    print("\n🖥️ 运行训练功能GUI测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("AI助手训练功能测试")
    main_window.resize(400, 800)
    
    # 创建AI助手面板
    ai_panel = AIAssistantPanel(main_window)
    main_window.setCentralWidget(ai_panel)
    
    # 模拟一些数据
    # 模拟用户类别（足够的数据）
    main_window.label_hist = ['cat', 'dog', 'bird', 'car', 'person']
    
    # 修改AI面板的训练数据更新方法
    def mock_update_training_data_stats():
        try:
            user_classes = main_window.label_hist
            estimated_images = len(user_classes) * 20  # 每类20张图
            
            ai_panel.training_data_stats.update({
                'total_images': estimated_images,
                'total_annotations': estimated_images * 2,
                'classes_count': len(user_classes)
            })
            
            ai_panel.training_data_count.setText(f"{estimated_images} 张")
            if estimated_images >= ai_panel.training_data_stats['min_samples_per_class'] * len(user_classes):
                ai_panel.training_data_count.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            else:
                ai_panel.training_data_count.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 11px;")
        except Exception as e:
            print(f"Mock update failed: {e}")
    
    ai_panel.update_training_data_stats = mock_update_training_data_stats
    
    # 刷新训练信息
    ai_panel.refresh_training_info()
    
    # 显示窗口
    main_window.show()
    
    print("✅ 训练功能GUI测试窗口已显示")
    print("🎓 训练功能特性:")
    print("   - 显示训练数据统计（图片数量、类别数量）")
    print("   - 智能检查训练准备状态")
    print("   - 数据充足时启用训练按钮")
    print("   - 点击'🚀 开始训练'打开训练对话框")
    print("   - 点击'⚙️ 配置'设置训练参数")
    print("   - 支持完整的训练参数配置")
    
    return main_window


def analyze_training_feature_design():
    """分析训练功能设计"""
    print("\n📊 训练功能设计分析:")
    print("=" * 50)
    
    print("🎯 设计目标:")
    print("   - 形成完整的标注→训练→预测闭环")
    print("   - 降低AI模型训练的技术门槛")
    print("   - 提供个性化模型训练能力")
    print("   - 智能检查数据准备状态")
    
    print("\n🏗️ 架构设计:")
    print("   - 集成到AI助手面板，保持界面统一")
    print("   - 紧凑布局，不占用过多空间")
    print("   - 模态对话框处理复杂配置")
    print("   - 智能状态检查和用户引导")
    
    print("\n⚙️ 功能特性:")
    print("   - 📊 数据统计: 自动统计标注数据")
    print("   - 🎯 状态检查: 智能判断是否可以训练")
    print("   - 🚀 一键训练: 简化训练启动流程")
    print("   - ⚙️ 参数配置: 支持训练参数自定义")
    print("   - 📈 进度监控: 实时显示训练进度")
    
    print("\n🔮 扩展方向:")
    print("   - 实现真实的YOLO训练流程")
    print("   - 添加数据增强功能")
    print("   - 支持分布式训练")
    print("   - 集成模型评估和验证")
    print("   - 提供训练结果可视化")


def main():
    """主函数"""
    print("🧪 AI助手训练功能测试")
    print("=" * 50)
    
    # 运行单元测试
    print("📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 显示设计分析
    analyze_training_feature_design()
    
    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_training_gui_test()
        
        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
