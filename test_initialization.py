#!/usr/bin/env python3
"""测试初始化和项目隔离"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, '.')

def test_initialization():
    """测试初始化过程"""
    try:
        print("开始测试初始化...")
        
        # 导入必要模块
        from labelImg import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        # 创建QApplication实例
        app = QApplication([])
        
        # 测试MainWindow初始化
        print("创建MainWindow实例...")
        window = MainWindow()
        print("✅ MainWindow初始化成功")
        
        # 检查项目隔离
        if hasattr(window, 'config_adapter') and window.config_adapter:
            print("✅ 项目配置适配器已正确初始化")
            
            if window.predefined_classes_file is None:
                print("✅ 项目模式下正确避免了全局路径")
            else:
                print(f"❌ 项目模式下仍在使用全局路径: {window.predefined_classes_file}")
                
            # 检查项目管理器
            if hasattr(window, 'project_manager') and window.project_manager:
                current_project = window.project_manager.get_current_project()
                print(f"✅ 当前项目: {current_project}")
            else:
                print("❌ 项目管理器未初始化")
                
        else:
            print("❌ 项目配置适配器未初始化，使用全局模式")
            if hasattr(window, 'predefined_classes_file'):
                print(f"全局模式路径: {window.predefined_classes_file}")
        
        # 检查性能监控系统
        if hasattr(window, 'performance_manager') and window.performance_manager:
            print("✅ 性能监控系统初始化成功")
        else:
            print("❌ 性能监控系统未初始化")
            
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ 初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_initialization()
    sys.exit(0 if success else 1)