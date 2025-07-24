#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI助手面板的安装失败补偿机制

测试内容:
1. 失败类型分析
2. 补偿方案生成
3. 解决方案执行
4. 用户指导功能
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


class TestFailureCompensation(unittest.TestCase):
    """测试安装失败补偿机制"""
    
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
    
    def test_failure_analysis_methods_exist(self):
        """测试失败分析方法是否存在"""
        print("\n=== 测试失败分析方法存在性 ===")
        
        # 检查补偿机制相关方法
        self.assertTrue(hasattr(self.ai_panel, 'handle_installation_failure'))
        self.assertTrue(hasattr(self.ai_panel, 'analyze_failure_type'))
        self.assertTrue(hasattr(self.ai_panel, 'execute_solution'))
        self.assertTrue(hasattr(self.ai_panel, 'retry_installation_with_command'))
        
        print("✅ 失败分析方法存在")
    
    def test_network_failure_analysis(self):
        """测试网络失败分析"""
        print("\n=== 测试网络失败分析 ===")
        
        # 模拟网络错误消息
        network_errors = [
            "Network connection timeout",
            "Could not reach download server",
            "DNS resolution failed",
            "Connection refused"
        ]
        
        for error in network_errors:
            result = self.ai_panel.analyze_failure_type(error)
            self.assertEqual(result['type'], '网络连接问题')
            self.assertIn('solutions', result)
            self.assertGreater(len(result['solutions']), 0)
            
            # 检查是否包含镜像源解决方案
            solution_names = [s['name'] for s in result['solutions']]
            self.assertTrue(any('镜像源' in name for name in solution_names))
            
        print("✅ 网络失败分析正确")
    
    def test_permission_failure_analysis(self):
        """测试权限失败分析"""
        print("\n=== 测试权限失败分析 ===")
        
        # 模拟权限错误消息
        permission_errors = [
            "Permission denied",
            "Access is denied",
            "Administrator privileges required",
            "Could not install packages due to an EnvironmentError"
        ]
        
        for error in permission_errors:
            result = self.ai_panel.analyze_failure_type(error)
            self.assertEqual(result['type'], '权限不足')
            self.assertIn('solutions', result)
            
            # 检查是否包含用户目录安装解决方案
            solution_names = [s['name'] for s in result['solutions']]
            self.assertTrue(any('用户目录' in name for name in solution_names))
            
        print("✅ 权限失败分析正确")
    
    def test_disk_space_failure_analysis(self):
        """测试磁盘空间失败分析"""
        print("\n=== 测试磁盘空间失败分析 ===")
        
        # 模拟磁盘空间错误消息
        space_errors = [
            "No space left on device",
            "Disk full",
            "Not enough storage space",
            "Insufficient disk space"
        ]
        
        for error in space_errors:
            result = self.ai_panel.analyze_failure_type(error)
            self.assertEqual(result['type'], '磁盘空间不足')
            self.assertIn('solutions', result)
            
            # 检查是否包含清理缓存解决方案
            solution_names = [s['name'] for s in result['solutions']]
            self.assertTrue(any('清理' in name for name in solution_names))
            
        print("✅ 磁盘空间失败分析正确")
    
    def test_version_conflict_analysis(self):
        """测试版本冲突分析"""
        print("\n=== 测试版本冲突分析 ===")
        
        # 模拟版本冲突错误消息
        conflict_errors = [
            "Version conflict detected",
            "Incompatible package versions",
            "Could not find a version that satisfies",
            "Package version incompatible"
        ]
        
        for error in conflict_errors:
            result = self.ai_panel.analyze_failure_type(error)
            self.assertEqual(result['type'], '版本冲突')
            self.assertIn('solutions', result)
            
            # 检查是否包含强制重装解决方案
            solution_names = [s['name'] for s in result['solutions']]
            self.assertTrue(any('重新安装' in name for name in solution_names))
            
        print("✅ 版本冲突分析正确")
    
    def test_unknown_error_analysis(self):
        """测试未知错误分析"""
        print("\n=== 测试未知错误分析 ===")
        
        # 模拟未知错误消息
        unknown_error = "Some random error message that doesn't match any pattern"
        
        result = self.ai_panel.analyze_failure_type(unknown_error)
        self.assertEqual(result['type'], '未知错误')
        self.assertIn('solutions', result)
        self.assertGreater(len(result['solutions']), 0)
        
        print("✅ 未知错误分析正确")
    
    def test_solution_command_generation(self):
        """测试解决方案命令生成"""
        print("\n=== 测试解决方案命令生成 ===")
        
        # 测试网络错误的解决方案
        result = self.ai_panel.analyze_failure_type("Network timeout")
        
        # 检查镜像源解决方案
        tsinghua_solution = None
        for solution in result['solutions']:
            if 'tsinghua_mirror' in solution['action']:
                tsinghua_solution = solution
                break
        
        self.assertIsNotNone(tsinghua_solution)
        self.assertIn('tuna.tsinghua.edu.cn', tsinghua_solution['command'])
        
        print("✅ 解决方案命令生成正确")
    
    def test_guide_methods_exist(self):
        """测试指导方法是否存在"""
        print("\n=== 测试指导方法存在性 ===")
        
        # 检查各种指导方法
        self.assertTrue(hasattr(self.ai_panel, 'show_offline_download_guide'))
        self.assertTrue(hasattr(self.ai_panel, 'show_admin_retry_guide'))
        self.assertTrue(hasattr(self.ai_panel, 'show_manual_solution_guide'))
        
        print("✅ 指导方法存在")


def run_failure_compensation_gui_test():
    """运行失败补偿机制GUI测试"""
    print("\n🖥️ 运行失败补偿机制GUI测试...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("安装失败补偿机制测试")
    main_window.resize(400, 800)
    
    # 创建AI助手面板
    ai_panel = AIAssistantPanel(main_window)
    main_window.setCentralWidget(ai_panel)
    
    # 模拟训练数据
    main_window.label_hist = ['cat', 'dog', 'bird', 'car', 'person']
    
    def mock_update_training_data_stats():
        try:
            user_classes = main_window.label_hist
            estimated_images = len(user_classes) * 25
            
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
    ai_panel.refresh_training_info()
    
    # 显示窗口
    main_window.show()
    
    print("✅ 失败补偿机制GUI测试窗口已显示")
    print("🔧 补偿机制功能特性:")
    print("   - 智能分析安装失败原因")
    print("   - 提供多种解决方案选择")
    print("   - 支持一键重试安装")
    print("   - 详细的手动安装指导")
    print("   - 针对不同错误类型的专门解决方案")
    
    # 演示失败分析功能
    print(f"\n🔍 失败分析演示:")
    
    # 网络错误示例
    network_result = ai_panel.analyze_failure_type("Network connection timeout")
    print(f"   网络错误 → {network_result['type']}")
    print(f"   解决方案数量: {len(network_result['solutions'])}")
    
    # 权限错误示例
    permission_result = ai_panel.analyze_failure_type("Permission denied")
    print(f"   权限错误 → {permission_result['type']}")
    print(f"   解决方案数量: {len(permission_result['solutions'])}")
    
    # 磁盘空间错误示例
    space_result = ai_panel.analyze_failure_type("No space left on device")
    print(f"   空间错误 → {space_result['type']}")
    print(f"   解决方案数量: {len(space_result['solutions'])}")
    
    return main_window


def analyze_compensation_mechanisms():
    """分析补偿机制特性"""
    print("\n📊 补偿机制特性分析:")
    print("=" * 50)
    
    print("🎯 智能错误分析:")
    print("   - 网络连接问题 → 镜像源、重试、离线安装")
    print("   - 权限不足 → 用户目录安装、管理员权限")
    print("   - 磁盘空间不足 → 清理缓存、CPU版本")
    print("   - 版本冲突 → 强制重装、升级pip")
    print("   - 未知错误 → 通用解决方案组合")
    
    print("\n🛠️ 解决方案类型:")
    print("   - 自动重试: 使用不同参数重新安装")
    print("   - 镜像源切换: 国内镜像源加速下载")
    print("   - 权限调整: 用户目录或管理员权限")
    print("   - 环境清理: 清理缓存、解决冲突")
    print("   - 手动指导: 详细的操作步骤说明")
    
    print("\n🎨 用户体验:")
    print("   - 失败原因自动分析")
    print("   - 多种解决方案可选")
    print("   - 一键执行解决方案")
    print("   - 详细的错误信息展示")
    print("   - 专业的手动指导")
    
    print("\n🔄 补偿流程:")
    print("   1. 安装失败 → 自动分析错误类型")
    print("   2. 错误分析 → 生成针对性解决方案")
    print("   3. 方案选择 → 用户选择合适的解决方案")
    print("   4. 自动执行 → 系统自动重试安装")
    print("   5. 手动指导 → 提供详细操作步骤")


def main():
    """主函数"""
    print("🧪 安装失败补偿机制测试")
    print("=" * 50)
    
    # 运行单元测试
    print("📋 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 显示补偿机制分析
    analyze_compensation_mechanisms()
    
    # 运行GUI测试
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        window = run_failure_compensation_gui_test()
        
        # 保持窗口打开
        app = QApplication.instance()
        if app:
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
