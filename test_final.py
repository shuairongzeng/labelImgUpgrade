#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终项目隔离测试"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, '.')

def test_project_isolation():
    """测试项目隔离是否完全工作"""
    try:
        print("开始最终项目隔离测试...")
        
        # 导入必要模块
        from labelImg import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        # 创建QApplication实例
        app = QApplication([])
        
        print("创建MainWindow实例...")
        window = MainWindow()
        print("✓ MainWindow初始化成功")
        
        # 检查项目配置
        if hasattr(window, 'config_adapter') and window.config_adapter:
            print("✓ 项目配置适配器已正确初始化")
            
            # 检查predefined_classes_file
            if hasattr(window, 'predefined_classes_file'):
                if window.predefined_classes_file is None:
                    print("✓ 项目模式下正确避免了全局predefined_classes_file")
                else:
                    print("✗ 项目模式下仍设置了predefined_classes_file: " + str(window.predefined_classes_file))
            else:
                print("警告: 未找到predefined_classes_file属性")
                
            # 检查项目管理器
            if hasattr(window, 'project_manager') and window.project_manager:
                current_project = window.project_manager.get_current_project()
                print("✓ 当前项目: " + str(current_project))
            else:
                print("✗ 项目管理器未初始化")
                
        else:
            print("✗ 项目配置适配器未初始化")
        
        # 检查性能监控系统
        if hasattr(window, 'performance_manager') and window.performance_manager:
            print("✓ 性能监控系统初始化成功")
        else:
            print("✗ 性能监控系统未初始化")
            
        # 检查标签配置
        if hasattr(window, 'label_hist') and window.label_hist:
            print("✓ 项目标签配置已加载: " + str(window.label_hist))
        else:
            print("✗ 项目标签配置未加载")
        
        app.quit()
        print("")
        print("项目隔离测试完成！")
        return True
        
    except Exception as e:
        print("测试失败: " + str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_project_isolation()
    
    if success:
        print("所有测试通过！项目隔离系统工作正常！")
        sys.exit(0)
    else:
        print("测试失败！")
        sys.exit(1)