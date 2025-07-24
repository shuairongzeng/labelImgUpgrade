#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据配置日志功能
Test Data Configuration Logging Functionality
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDataConfigLogging(unittest.TestCase):
    """测试数据配置日志功能"""
    
    def setUp(self):
        """设置测试环境"""
        print("\n=== 设置测试环境 ===")
        
        # 模拟PyQt5环境
        self.mock_qt_modules()
        
        # 导入AI助手面板
        from libs.ai_assistant_panel import AIAssistantPanel
        
        # 创建模拟的父窗口
        self.parent_window = Mock()
        self.parent_window.last_open_dir = os.getcwd()
        
        # 创建AI助手面板实例
        self.ai_panel = AIAssistantPanel(self.parent_window)
        
        # 模拟数据配置日志文本控件
        self.ai_panel.data_config_log_text = Mock()
        self.ai_panel.data_config_log_text.append = Mock()
        self.ai_panel.data_config_log_text.moveCursor = Mock()
        self.ai_panel.data_config_log_text.textCursor = Mock()
        self.ai_panel.data_config_log_text.textCursor.return_value.End = Mock()
        
        print("✅ 测试环境设置完成")
    
    def mock_qt_modules(self):
        """模拟PyQt5模块"""
        # 创建模拟的Qt模块
        mock_qt = MagicMock()
        mock_widgets = MagicMock()
        mock_core = MagicMock()
        mock_gui = MagicMock()
        
        # 设置模拟的类和常量
        mock_widgets.QWidget = Mock
        mock_widgets.QVBoxLayout = Mock
        mock_widgets.QHBoxLayout = Mock
        mock_widgets.QFormLayout = Mock
        mock_widgets.QGroupBox = Mock
        mock_widgets.QLabel = Mock
        mock_widgets.QPushButton = Mock
        mock_widgets.QLineEdit = Mock
        mock_widgets.QTextEdit = Mock
        mock_widgets.QSpinBox = Mock
        mock_widgets.QDoubleSpinBox = Mock
        mock_widgets.QComboBox = Mock
        mock_widgets.QCheckBox = Mock
        mock_widgets.QSlider = Mock
        mock_widgets.QProgressBar = Mock
        mock_widgets.QTabWidget = Mock
        mock_widgets.QDialog = Mock
        mock_widgets.QMessageBox = Mock
        mock_widgets.QFileDialog = Mock
        mock_widgets.QApplication = Mock
        
        mock_core.Qt = Mock()
        mock_core.Qt.AlignCenter = 0x84
        mock_core.QThread = Mock
        mock_core.pyqtSignal = Mock(return_value=Mock())
        
        mock_gui.QFont = Mock
        
        # 将模拟模块添加到sys.modules
        sys.modules['PyQt5'] = mock_qt
        sys.modules['PyQt5.QtWidgets'] = mock_widgets
        sys.modules['PyQt5.QtCore'] = mock_core
        sys.modules['PyQt5.QtGui'] = mock_gui
    
    def test_safe_append_data_log_method_exists(self):
        """测试_safe_append_data_log方法是否存在"""
        print("\n=== 测试_safe_append_data_log方法存在性 ===")
        
        self.assertTrue(hasattr(self.ai_panel, '_safe_append_data_log'))
        self.assertTrue(callable(getattr(self.ai_panel, '_safe_append_data_log')))
        
        print("✅ _safe_append_data_log方法存在")
    
    def test_safe_append_data_log_functionality(self):
        """测试_safe_append_data_log方法功能"""
        print("\n=== 测试_safe_append_data_log方法功能 ===")
        
        test_message = "测试日志消息"
        
        # 调用方法
        self.ai_panel._safe_append_data_log(test_message)
        
        # 验证是否调用了append方法
        self.ai_panel.data_config_log_text.append.assert_called_with(test_message)
        
        print(f"✅ 日志消息已正确添加: {test_message}")
    
    def test_refresh_dataset_config_method_exists(self):
        """测试refresh_dataset_config方法是否存在"""
        print("\n=== 测试refresh_dataset_config方法存在性 ===")
        
        self.assertTrue(hasattr(self.ai_panel, 'refresh_dataset_config'))
        self.assertTrue(callable(getattr(self.ai_panel, 'refresh_dataset_config')))
        
        print("✅ refresh_dataset_config方法存在")
    
    def test_data_config_tab_has_log_area(self):
        """测试数据配置标签页是否有日志区域"""
        print("\n=== 测试数据配置标签页日志区域 ===")
        
        # 创建数据配置标签页
        data_tab = self.ai_panel.create_data_config_tab()
        
        # 检查是否创建成功
        self.assertIsNotNone(data_tab)
        
        # 检查是否有数据配置日志文本控件
        self.assertTrue(hasattr(self.ai_panel, 'data_config_log_text'))
        
        print("✅ 数据配置标签页包含日志区域")
    
    def test_load_dataset_config_with_logging(self):
        """测试加载数据集配置时的日志输出"""
        print("\n=== 测试加载数据集配置的日志输出 ===")
        
        # 创建测试配置文件
        test_config_path = "test_data.yaml"
        test_config_content = """
path: .
train: images/train
val: images/val
nc: 2
names:
  0: class1
  1: class2
"""
        
        try:
            with open(test_config_path, 'w', encoding='utf-8') as f:
                f.write(test_config_content)
            
            # 模拟dataset_config_edit
            self.ai_panel.dataset_config_edit = Mock()
            self.ai_panel.dataset_config_edit.text.return_value = test_config_path
            
            # 模拟其他UI控件
            self.ai_panel.dataset_path_label = Mock()
            self.ai_panel.train_path_label = Mock()
            self.ai_panel.val_path_label = Mock()
            self.ai_panel.classes_info_label = Mock()
            self.ai_panel.config_info_label = Mock()
            
            # 调用加载配置方法
            self.ai_panel.load_dataset_config(test_config_path)
            
            # 验证是否有日志输出
            self.assertTrue(self.ai_panel.data_config_log_text.append.called)
            
            # 获取所有调用的参数
            call_args_list = self.ai_panel.data_config_log_text.append.call_args_list
            log_messages = [call[0][0] for call in call_args_list]
            
            print("📋 日志消息:")
            for i, message in enumerate(log_messages, 1):
                print(f"   {i}. {message}")
            
            # 验证关键日志消息
            self.assertTrue(any("加载数据集配置文件" in msg for msg in log_messages))
            self.assertTrue(any("配置文件存在" in msg for msg in log_messages))
            self.assertTrue(any("配置文件内容" in msg for msg in log_messages))
            
            print("✅ 加载数据集配置的日志输出正常")
            
        finally:
            # 清理测试文件
            if os.path.exists(test_config_path):
                os.remove(test_config_path)
    
    def test_scan_dataset_with_logging(self):
        """测试扫描数据集时的日志输出"""
        print("\n=== 测试扫描数据集的日志输出 ===")
        
        # 模拟dataset_config_edit
        self.ai_panel.dataset_config_edit = Mock()
        self.ai_panel.dataset_config_edit.text.return_value = ""
        
        # 模拟统计标签
        self.ai_panel.stats_images_label = Mock()
        
        # 调用扫描方法
        self.ai_panel.scan_dataset()
        
        # 验证是否有日志输出
        self.assertTrue(self.ai_panel.data_config_log_text.append.called)
        
        # 获取日志消息
        call_args_list = self.ai_panel.data_config_log_text.append.call_args_list
        log_messages = [call[0][0] for call in call_args_list]
        
        print("📋 扫描日志消息:")
        for i, message in enumerate(log_messages, 1):
            print(f"   {i}. {message}")
        
        # 验证关键日志消息
        self.assertTrue(any("开始扫描数据集" in msg for msg in log_messages))
        
        print("✅ 扫描数据集的日志输出正常")
    
    def test_validate_training_config_with_logging(self):
        """测试验证训练配置时的日志输出"""
        print("\n=== 测试验证训练配置的日志输出 ===")
        
        # 模拟对话框
        mock_dialog = Mock()
        
        # 模拟dataset_config_edit为空
        self.ai_panel.dataset_config_edit = Mock()
        self.ai_panel.dataset_config_edit.text.return_value = ""
        
        # 调用验证方法
        result = self.ai_panel.validate_training_config(mock_dialog)
        
        # 验证返回False（因为没有配置文件）
        self.assertFalse(result)
        
        # 验证是否有日志输出
        self.assertTrue(self.ai_panel.data_config_log_text.append.called)
        
        # 获取日志消息
        call_args_list = self.ai_panel.data_config_log_text.append.call_args_list
        log_messages = [call[0][0] for call in call_args_list]
        
        print("📋 验证日志消息:")
        for i, message in enumerate(log_messages, 1):
            print(f"   {i}. {message}")
        
        # 验证关键日志消息
        self.assertTrue(any("开始验证训练配置" in msg for msg in log_messages))
        self.assertTrue(any("请选择data.yaml配置文件" in msg for msg in log_messages))
        
        print("✅ 验证训练配置的日志输出正常")

def main():
    """主函数"""
    print("🧪 开始测试数据配置日志功能...")
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataConfigLogging)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！数据配置日志功能正常工作。")
        return True
    else:
        print(f"\n❌ 测试失败！失败数量: {len(result.failures)}, 错误数量: {len(result.errors)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
