#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试训练监控日志自动滚动功能修复
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, QThread, pyqtSignal


class LogTestThread(QThread):
    """模拟日志输出的线程"""
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
    
    def run(self):
        """运行日志输出"""
        self.running = True
        count = 1
        
        while self.running and count <= 50:
            # 模拟训练日志
            if count % 5 == 0:
                self.log_message.emit(f"📊 Epoch {count//5}/10 - Loss: {0.5 - count*0.01:.4f}, mAP50: {0.3 + count*0.01:.4f}")
            else:
                self.log_message.emit(f"🔄 训练步骤 {count}: 正在处理批次数据...")
            
            time.sleep(0.5)  # 每0.5秒输出一条日志
            count += 1
        
        if self.running:
            self.log_message.emit("✅ 模拟训练完成!")
    
    def stop(self):
        """停止日志输出"""
        self.running = False


class LogScrollTestWindow(QMainWindow):
    """日志滚动测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.log_thread = None
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("训练日志自动滚动测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建日志文本框（模拟训练监控日志）
        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText("训练日志将在这里显示...")
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 创建控制按钮
        self.start_btn = QPushButton("🚀 开始模拟训练日志")
        self.start_btn.clicked.connect(self.start_log_test)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("🛑 停止日志输出")
        self.stop_btn.clicked.connect(self.stop_log_test)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空日志")
        self.clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_btn)
    
    def append_log_with_scroll(self, message):
        """添加日志并自动滚动到底部"""
        try:
            self.log_text.append(message)
            # 自动滚动到底部
            self.log_text.moveCursor(self.log_text.textCursor().End)
        except Exception as e:
            print(f"日志更新失败: {e}")
    
    def start_log_test(self):
        """开始日志测试"""
        self.append_log_with_scroll("🚀 开始模拟训练日志输出...")
        self.append_log_with_scroll("📋 测试自动滚动功能...")
        
        # 创建并启动日志线程
        self.log_thread = LogTestThread()
        self.log_thread.log_message.connect(self.append_log_with_scroll)
        self.log_thread.start()
        
        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_log_test(self):
        """停止日志测试"""
        if self.log_thread and self.log_thread.isRunning():
            self.log_thread.stop()
            self.log_thread.wait()
        
        self.append_log_with_scroll("🛑 日志输出已停止")
        
        # 更新按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.append_log_with_scroll("📝 日志已清空，准备新的测试...")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.log_thread and self.log_thread.isRunning():
            self.log_thread.stop()
            self.log_thread.wait()
        event.accept()


def main():
    """主函数"""
    print("🧪 启动训练日志自动滚动测试...")
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = LogScrollTestWindow()
    window.show()
    
    print("✅ 测试窗口已启动")
    print("📋 使用说明:")
    print("   1. 点击'开始模拟训练日志'按钮开始测试")
    print("   2. 观察日志是否自动滚动到最新内容")
    print("   3. 可以点击'停止日志输出'来停止测试")
    print("   4. 可以点击'清空日志'来清空内容")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
