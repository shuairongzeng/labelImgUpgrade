#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试UI修改效果的脚本
验证复选框对齐和标签文字显示问题是否已解决
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from labelImg import MainWindow

def test_ui_fixes():
    """测试UI修改效果"""
    print("=" * 50)
    print("测试UI修改效果")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = MainWindow()
    
    # 显示窗口
    main_window.show()
    
    # 设置窗口大小和位置（根据用户偏好）
    main_window.resize(1366, 768)
    main_window.move(100, 100)
    
    print("✓ 主窗口已创建并显示")
    print("✓ 窗口大小设置为 1366x768")
    
    # 检查UI组件
    print("\n检查UI组件:")
    
    # 检查区块标签面板
    if hasattr(main_window, 'dock'):
        print("✓ 区块标签面板存在")
        dock_title = main_window.dock.windowTitle()
        print(f"  - 标题: {dock_title}")
    
    # 检查文件列表面板
    if hasattr(main_window, 'file_dock'):
        print("✓ 文件列表面板存在")
        file_dock_title = main_window.file_dock.windowTitle()
        print(f"  - 标题: {file_dock_title}")
    
    # 检查复选框
    if hasattr(main_window, 'use_default_label_checkbox'):
        print("✓ '使用预设标签'复选框存在")
        
    if hasattr(main_window, 'diffc_button'):
        print("✓ '有难度的'复选框存在")
    
    print("\n" + "=" * 50)
    print("UI修改验证完成")
    print("请检查以下内容:")
    print("1. QDockWidget标题栏文字是否完整显示")
    print("2. 复选框是否正确对齐")
    print("3. 整体布局间距是否合适")
    print("=" * 50)
    
    # 设置定时器自动关闭（可选）
    # timer = QTimer()
    # timer.timeout.connect(app.quit)
    # timer.start(10000)  # 10秒后自动关闭
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == '__main__':
    test_ui_fixes()
