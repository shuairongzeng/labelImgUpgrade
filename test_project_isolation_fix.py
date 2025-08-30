#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试项目隔离修复是否生效
确保在项目管理系统存在时不使用全局配置路径
"""

import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_project_isolation():
    """测试项目隔离是否正确工作"""
    print("========== 测试项目隔离修复 ==========")
    
    # 创建临时目录作为项目基础路径
    temp_dir = tempfile.mkdtemp()
    print(f"创建临时目录: {temp_dir}")
    
    try:
        # 模拟项目管理器和配置适配器
        mock_project_manager = MagicMock()
        mock_project_manager.get_current_project.return_value = "test_project"
        mock_project_manager.get_project_config_path.return_value = os.path.join(temp_dir, "test_project", "configs")
        
        mock_config_adapter = MagicMock()
        mock_config_adapter.load_classes.return_value = ["person", "car", "bike"]
        mock_config_adapter.save_classes.return_value = True
        
        # 使用patch模拟项目管理系统
        with patch('libs.project_manager.get_project_manager', return_value=mock_project_manager):
            with patch('libs.project_config_adapter.get_config_adapter', return_value=mock_config_adapter):
                # 导入MainWindow（这会触发初始化）
                from labelImg import MainWindow
                
                # 测试初始化过程
                print("\n[测试] 模拟MainWindow初始化...")
                
                # 模拟Qt应用
                from PyQt5.QtWidgets import QApplication
                if not QApplication.instance():
                    app = QApplication([])
                else:
                    app = QApplication.instance()
                
                # 创建MainWindow实例（传入测试参数）
                main_window = MainWindow(
                    default_filename=None,
                    default_prefdef_class_file=None,  # 不指定默认文件
                    default_save_dir=None
                )
                
                # 验证结果
                print(f"\n[验证] predefined_classes_file: {main_window.predefined_classes_file}")
                print(f"[验证] config_adapter存在: {main_window.config_adapter is not None}")
                print(f"[验证] label_hist: {main_window.label_hist}")
                
                # 检查关键条件
                success = True
                
                if main_window.config_adapter is not None:
                    if main_window.predefined_classes_file is not None:
                        print("❌ 错误：项目模式下仍设置了全局预设类文件路径")
                        success = False
                    else:
                        print("✅ 正确：项目模式下未设置全局预设类文件路径")
                    
                    if main_window.label_hist == ["person", "car", "bike"]:
                        print("✅ 正确：从项目配置加载了标签")
                    else:
                        print(f"❌ 错误：未正确加载项目标签，实际标签: {main_window.label_hist}")
                        success = False
                else:
                    print("⚠️  警告：配置适配器未初始化")
                
                # 测试保存功能
                print(f"\n[测试] 测试标签保存功能...")
                main_window.label_hist = ["test1", "test2"]
                
                # 调用保存方法
                main_window.save_predefined_classes()
                
                # 验证是否通过配置适配器保存
                if mock_config_adapter.save_classes.called:
                    print("✅ 正确：通过配置适配器保存标签")
                    saved_classes = mock_config_adapter.save_classes.call_args[0][0]
                    print(f"✅ 保存的标签: {saved_classes}")
                else:
                    print("❌ 错误：未通过配置适配器保存标签")
                    success = False
                
                app.quit()
                
                return success
                
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"清理临时目录: {temp_dir}")

def test_fallback_mode():
    """测试回退模式（无项目管理系统时）"""
    print("\n========== 测试回退模式 ==========")
    
    try:
        # 使用patch确保没有项目管理系统
        with patch('libs.project_manager.get_project_manager', side_effect=Exception("项目管理系统不可用")):
            with patch('libs.project_config_adapter.get_config_adapter', side_effect=Exception("配置适配器不可用")):
                # 导入MainWindow
                from labelImg import MainWindow
                
                print("\n[测试] 模拟无项目管理系统的初始化...")
                
                # 模拟Qt应用
                from PyQt5.QtWidgets import QApplication
                if not QApplication.instance():
                    app = QApplication([])
                else:
                    app = QApplication.instance()
                
                # 创建MainWindow实例
                main_window = MainWindow(
                    default_filename=None,
                    default_prefdef_class_file=None,
                    default_save_dir=None
                )
                
                # 验证结果
                print(f"\n[验证] predefined_classes_file: {main_window.predefined_classes_file}")
                print(f"[验证] config_adapter: {main_window.config_adapter}")
                
                success = True
                
                if main_window.config_adapter is None:
                    if main_window.predefined_classes_file is not None:
                        print("✅ 正确：无项目系统时设置了全局预设类文件路径")
                    else:
                        print("❌ 错误：无项目系统时未设置全局预设类文件路径")
                        success = False
                else:
                    print("❌ 错误：配置适配器不应该存在")
                    success = False
                
                app.quit()
                
                return success
                
    except Exception as e:
        print(f"回退模式测试出现异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试项目隔离修复...")
    
    # 测试项目隔离
    isolation_success = test_project_isolation()
    
    # 测试回退模式
    fallback_success = test_fallback_mode()
    
    # 总结结果
    print(f"\n========== 测试结果 ==========")
    print(f"项目隔离测试: {'✅ 通过' if isolation_success else '❌ 失败'}")
    print(f"回退模式测试: {'✅ 通过' if fallback_success else '❌ 失败'}")
    
    if isolation_success and fallback_success:
        print(f"\n🎉 所有测试通过！项目隔离修复成功。")
        sys.exit(0)
    else:
        print(f"\n❌ 部分测试失败，需要进一步检查。")
        sys.exit(1)