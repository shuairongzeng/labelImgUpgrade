#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI助手面板的GPU/CPU训练功能

测试内容:
1. 硬件信息检测
2. GPU/CPU设备选择
3. PyTorch环境检查
4. 训练环境配置
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


class TestGPUCPUTraining(unittest.TestCase):
    """测试GPU/CPU训练功能"""
    
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
    
    def test_hardware_info_initialization(self):
        """测试硬件信息初始化"""
        print("\n=== 测试硬件信息初始化 ===")
        
        # 检查硬件信息结构是否存在
        self.assertTrue(hasattr(self.ai_panel, 'hardware_info'))
        self.assertTrue(hasattr(self.ai_panel, 'device_status'))
        
        # 检查硬件信息字段
        required_fields = ['gpu_available', 'gpu_name', 'cuda_version', 'pytorch_version', 'recommended_device']
        for field in required_fields:
            self.assertIn(field, self.ai_panel.hardware_info)
        
        print("✅ 硬件信息初始化成功")
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_name')
    @patch('torch.version.cuda')
    @patch('torch.__version__')
    def test_gpu_detection(self, mock_torch_version, mock_cuda_version, mock_gpu_name, mock_cuda_available):
        """测试GPU检测功能"""
        print("\n=== 测试GPU检测功能 ===")
        
        # 模拟有GPU的情况
        mock_cuda_available.return_value = True
        mock_gpu_name.return_value = "NVIDIA GeForce RTX 3080"
        mock_cuda_version = "11.8"
        mock_torch_version = "2.0.0"
        
        # 执行硬件检测
        self.ai_panel.detect_hardware_info()
        
        # 验证GPU检测结果
        self.assertTrue(self.ai_panel.hardware_info['gpu_available'])
        self.assertEqual(self.ai_panel.hardware_info['recommended_device'], 'cuda')
        
        print("✅ GPU检测功能正常")
    
    @patch('torch.cuda.is_available')
    def test_cpu_fallback(self, mock_cuda_available):
        """测试CPU回退功能"""
        print("\n=== 测试CPU回退功能 ===")
        
        # 模拟没有GPU的情况
        mock_cuda_available.return_value = False
        
        # 执行硬件检测
        self.ai_panel.detect_hardware_info()
        
        # 验证CPU回退
        self.assertFalse(self.ai_panel.hardware_info['gpu_available'])
        self.assertEqual(self.ai_panel.hardware_info['recommended_device'], 'cpu')
        
        print("✅ CPU回退功能正常")
    
    def test_pytorch_install_command_generation(self):
        """测试PyTorch安装命令生成"""
        print("\n=== 测试PyTorch安装命令生成 ===")
        
        # 测试GPU版本命令
        self.ai_panel.hardware_info['gpu_available'] = True
        self.ai_panel.hardware_info['cuda_version'] = '11.8'
        
        gpu_command = self.ai_panel.get_pytorch_install_command()
        self.assertIn("cu118", gpu_command)
        
        print(f"GPU命令: {gpu_command}")
        
        # 测试CPU版本命令
        self.ai_panel.hardware_info['gpu_available'] = False
        self.ai_panel.hardware_info['nvidia_driver'] = 'Not Found'
        
        cpu_command = self.ai_panel.get_pytorch_install_command()
        self.assertIn("torch", cpu_command)
        
        print(f"CPU命令: {cpu_command}")
        print("✅ PyTorch安装命令生成正常")
    
    def test_training_environment_methods(self):
        """测试训练环境相关方法"""
        print("\n=== 测试训练环境相关方法 ===")
        
        # 检查方法是否存在
        self.assertTrue(hasattr(self.ai_panel, 'detect_hardware_info'))
        self.assertTrue(hasattr(self.ai_panel, 'check_training_environment'))
        self.assertTrue(hasattr(self.ai_panel, 'show_pytorch_install_dialog'))
        self.assertTrue(hasattr(self.ai_panel, 'get_pytorch_install_command'))
        
        print("✅ 训练环境相关方法存在")


def run_hardware_detection_test():
    """运行硬件检测测试"""
    print("\n🔍 硬件检测测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建AI助手面板
    main_window = QMainWindow()
    ai_panel = AIAssistantPanel(main_window)
    
    # 执行硬件检测
    ai_panel.detect_hardware_info()
    
    # 显示检测结果
    print("\n📊 硬件检测结果:")
    print("=" * 40)
    
    hardware_info = ai_panel.hardware_info
    
    print(f"🖥️  系统: {hardware_info.get('system', 'Unknown')}")
    print(f"🐍 Python: {hardware_info.get('python_version', 'Unknown')}")
    print(f"🔥 PyTorch: {hardware_info.get('pytorch_version', 'Unknown')}")
    
    if hardware_info['gpu_available']:
        print(f"✅ GPU: {hardware_info['gpu_name']}")
        print(f"✅ CUDA: {hardware_info['cuda_version']}")
        print(f"🎯 推荐设备: {hardware_info['recommended_device'].upper()}")
    else:
        print("❌ GPU: 未检测到可用GPU")
        print(f"🎯 推荐设备: {hardware_info['recommended_device'].upper()}")
    
    # 显示安装命令
    install_cmd = ai_panel.get_pytorch_install_command()
    print(f"\n📦 推荐安装命令:")
    print(f"   {install_cmd}")
    
    return ai_panel


def run_gpu_cpu_gui_test():
    """运行GPU/CPU训练GUI测试"""
    print("\n🖥️ 运行GPU/CPU训练GUI测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("GPU/CPU训练功能测试")
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
    
    print("✅ GPU/CPU训练功能GUI测试窗口已显示")
    print("🎓 GPU/CPU训练功能特性:")
    print("   - 自动检测GPU和CUDA环境")
    print("   - 智能推荐训练设备（GPU/CPU）")
    print("   - 显示硬件信息和状态")
    print("   - 点击'🚀 开始训练'查看设备选择")
    print("   - 点击'⚙️ 配置'中的'🔍 检查环境'查看详细报告")
    print("   - 点击'📦 安装PyTorch'获取安装指导")
    
    return main_window


def analyze_gpu_cpu_design():
    """分析GPU/CPU训练设计"""
    print("\n📊 GPU/CPU训练功能设计分析:")
    print("=" * 50)
    
    print("🎯 设计目标:")
    print("   - 自动检测用户硬件环境")
    print("   - 智能推荐最佳训练设备")
    print("   - 简化PyTorch环境配置")
    print("   - 提供清晰的性能预期")
    
    print("\n🔍 硬件检测策略:")
    print("   - PyTorch CUDA可用性检测")
    print("   - GPU型号和CUDA版本识别")
    print("   - NVIDIA驱动程序检测")
    print("   - 系统平台兼容性检查")
    
    print("\n⚙️ 环境配置功能:")
    print("   - 根据硬件生成安装命令")
    print("   - 支持GPU和CPU版本选择")
    print("   - 提供详细的安装指导")
    print("   - 环境检查和验证工具")
    
    print("\n🎨 用户体验设计:")
    print("   - 设备状态实时显示")
    print("   - 智能设备推荐")
    print("   - 一键环境检查")
    print("   - 傻瓜式安装指导")
    
    print("\n🚀 性能优化:")
    print("   - GPU训练: 速度快，适合大数据集")
    print("   - CPU训练: 兼容性好，适合小数据集")
    print("   - 自动设备回退机制")
    print("   - 训练参数智能调整")


def main():
    """主函数"""
    print("🧪 GPU/CPU训练功能测试")
    print("=" * 50)
    
    # 运行硬件检测测试
    ai_panel = run_hardware_detection_test()
    
    # 运行单元测试
    print("\n📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 显示设计分析
    analyze_gpu_cpu_design()
    
    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_gpu_cpu_gui_test()
        
        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
