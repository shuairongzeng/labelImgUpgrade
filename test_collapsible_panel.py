#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试可折叠AI助手面板功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from libs.ai_assistant_panel import CollapsibleAIPanel

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试可折叠AI助手面板")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建左侧内容区域
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #e0e0e0;")
        left_label = QLabel("主内容区域\n\n点击右侧AI助手面板的按钮\n测试折叠/展开功能")
        left_label.setAlignment(Qt.AlignCenter)
        left_label.setStyleSheet("font-size: 16px; color: #333;")
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(left_label)
        
        # 创建可折叠AI助手面板
        self.ai_panel = CollapsibleAIPanel(self)
        
        # 添加到布局
        layout.addWidget(left_widget, 1)  # 左侧占据剩余空间
        layout.addWidget(self.ai_panel, 0)  # AI面板固定宽度
        
        # 添加测试按钮
        self.create_test_buttons()
    
    def create_test_buttons(self):
        """创建测试按钮"""
        # 创建工具栏
        toolbar = self.addToolBar("测试工具")
        
        # 折叠按钮
        collapse_action = QAction("折叠AI面板", self)
        collapse_action.triggered.connect(self.ai_panel.collapse)
        toolbar.addAction(collapse_action)
        
        # 展开按钮
        expand_action = QAction("展开AI面板", self)
        expand_action.triggered.connect(self.ai_panel.expand)
        toolbar.addAction(expand_action)
        
        # 切换按钮
        toggle_action = QAction("切换AI面板", self)
        toggle_action.triggered.connect(self.ai_panel.toggle_collapse)
        toolbar.addAction(toggle_action)
        
        # 显示当前状态
        self.status_label = QLabel("AI面板状态: 展开")
        self.statusBar().addWidget(self.status_label)
        
        # 连接状态更新
        self.ai_panel.width_animation.valueChanged.connect(self.update_status)
    
    def update_status(self, width):
        """更新状态显示"""
        if width <= 50:
            status = "折叠"
        elif width >= 300:
            status = "展开"
        else:
            status = f"动画中 ({width}px)"
        
        self.status_label.setText(f"AI面板状态: {status} | 当前宽度: {width}px")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("=== 可折叠AI助手面板测试 ===")
    print("1. 点击AI面板左侧的按钮测试折叠/展开")
    print("2. 使用工具栏按钮测试功能")
    print("3. 观察状态栏显示的宽度变化")
    print("4. 验证折叠时面板宽度确实缩小到按钮宽度")
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
