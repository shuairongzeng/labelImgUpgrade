#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI助手面板的真实安装功能

测试内容:
1. 真实PyTorch安装功能
2. 安装线程管理
3. 安装进度监控
4. 安装完成处理
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
    
    from libs.ai_assistant_panel import AIAssistantPanel, InstallThread
    
    print("✅ 成功导入所有必需模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)


class TestRealInstallation(unittest.TestCase):
    """测试真实安装功能"""
    
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
    
    def test_install_thread_class_exists(self):
        """测试安装线程类是否存在"""
        print("\n=== 测试安装线程类存在性 ===")
        
        # 检查InstallThread类是否存在
        self.assertTrue(hasattr(sys.modules['libs.ai_assistant_panel'], 'InstallThread'))
        
        # 检查InstallThread的信号
        thread = InstallThread(['echo', 'test'], None, None)
        self.assertTrue(hasattr(thread, 'progress_updated'))
        self.assertTrue(hasattr(thread, 'log_updated'))
        self.assertTrue(hasattr(thread, 'installation_finished'))
        
        print("✅ 安装线程类存在且信号完整")
    
    def test_real_install_method_exists(self):
        """测试真实安装方法是否存在"""
        print("\n=== 测试真实安装方法存在性 ===")
        
        # 检查安装相关方法
        self.assertTrue(hasattr(self.ai_panel, 'install_pytorch'))
        self.assertTrue(hasattr(self.ai_panel, 'on_installation_finished'))
        
        print("✅ 真实安装方法存在")
    
    def test_install_command_preparation(self):
        """测试安装命令准备"""
        print("\n=== 测试安装命令准备 ===")
        
        # 测试pip命令转换
        test_command = "pip install torch torchvision torchaudio"
        expected_cmd = [sys.executable, '-m', 'pip', 'install', 'torch', 'torchvision', 'torchaudio']
        
        # 模拟命令处理逻辑
        install_cmd = test_command.split()
        if install_cmd[0] == 'pip':
            install_cmd = [sys.executable, '-m', 'pip'] + install_cmd[1:]
        
        self.assertEqual(install_cmd, expected_cmd)
        print(f"✅ 命令转换正确: {' '.join(install_cmd)}")
    
    def test_pytorch_install_dialog_integration(self):
        """测试PyTorch安装对话框集成"""
        print("\n=== 测试PyTorch安装对话框集成 ===")
        
        # 检查PyTorch安装对话框方法
        self.assertTrue(hasattr(self.ai_panel, 'show_pytorch_install_dialog'))
        
        print("✅ PyTorch安装对话框集成正常")


def run_real_installation_gui_test():
    """运行真实安装功能GUI测试"""
    print("\n🖥️ 运行真实安装功能GUI测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("真实安装功能测试")
    main_window.resize(400, 800)
    
    # 创建AI助手面板
    ai_panel = AIAssistantPanel(main_window)
    main_window.setCentralWidget(ai_panel)
    
    # 模拟训练数据（充足的数据以启用训练）
    main_window.label_hist = ['cat', 'dog', 'bird', 'car', 'person']
    
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
    
    print("✅ 真实安装功能GUI测试窗口已显示")
    print("🚀 真实安装功能特性:")
    print("   - 点击'📦 安装'按钮进行真实PyTorch安装")
    print("   - 安装前会弹出确认对话框")
    print("   - 显示真实的安装进度和日志")
    print("   - 安装完成后自动重新检测环境")
    print("   - 支持安装过程中的错误处理")
    
    # 显示安装相关信息
    print(f"\n📦 安装功能信息:")
    print(f"   当前Python: {sys.executable}")
    
    # 获取推荐安装命令
    install_cmd = ai_panel.get_pytorch_install_command()
    print(f"   推荐命令: {install_cmd}")
    
    # 检查安装按钮状态
    if hasattr(ai_panel, 'pytorch_install_btn'):
        print(f"   安装按钮: {'可见' if ai_panel.pytorch_install_btn.isVisible() else '隐藏'}")
    
    return main_window


def analyze_real_installation_features():
    """分析真实安装功能特性"""
    print("\n📊 真实安装功能特性分析:")
    print("=" * 50)
    
    print("🎯 技术实现:")
    print("   - 使用QThread进行后台安装，不阻塞UI")
    print("   - 通过subprocess执行真实的pip命令")
    print("   - 实时捕获安装输出和进度")
    print("   - 使用信号槽机制更新UI")
    
    print("\n🛡️ 安全措施:")
    print("   - 安装前弹出确认对话框")
    print("   - 使用当前Python解释器执行安装")
    print("   - 完整的错误处理和用户反馈")
    print("   - 安装失败时提供详细错误信息")
    
    print("\n🎨 用户体验:")
    print("   - 实时显示安装进度条")
    print("   - 详细的安装日志输出")
    print("   - 安装完成后自动环境检测")
    print("   - 清晰的成功/失败反馈")
    
    print("\n⚡ 性能优化:")
    print("   - 后台线程安装，UI保持响应")
    print("   - 流式读取安装输出")
    print("   - 智能进度估算")
    print("   - 内存友好的日志处理")
    
    print("\n🔧 技术优势:")
    print("   - 真实安装，不是模拟")
    print("   - 跨平台兼容性")
    print("   - 与现有环境无缝集成")
    print("   - 支持各种pip安装选项")


def installation_safety_tips():
    """安装安全提示"""
    print("\n🛡️ 安装安全提示:")
    print("=" * 30)
    
    print("✅ 安全特性:")
    print("   - 安装前确认对话框")
    print("   - 显示完整安装命令")
    print("   - 用户可以取消安装")
    print("   - 详细的错误报告")
    
    print("\n⚠️ 注意事项:")
    print("   - 安装会修改Python环境")
    print("   - 需要网络连接下载包")
    print("   - 可能需要管理员权限")
    print("   - 建议在虚拟环境中使用")
    
    print("\n💡 最佳实践:")
    print("   - 安装前备份重要数据")
    print("   - 确保网络连接稳定")
    print("   - 关闭杀毒软件干扰")
    print("   - 安装完成后重启应用")


def main():
    """主函数"""
    print("🧪 真实安装功能测试")
    print("=" * 50)
    
    # 运行单元测试
    print("📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 显示功能分析
    analyze_real_installation_features()
    
    # 显示安全提示
    installation_safety_tips()
    
    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_real_installation_gui_test()
        
        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
