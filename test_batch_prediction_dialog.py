#!/usr/bin/env python3
"""
测试批量预测对话框功能
"""

import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSlot

# 添加libs目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from batch_prediction_dialog import BatchPredictionDialog

class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量预测对话框测试")
        self.setGeometry(100, 100, 300, 200)
        
        # 创建测试数据
        self.create_test_data()
        
        # 设置UI
        self.setup_ui()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp(prefix="batch_test_")
        print(f"测试目录: {self.test_dir}")
        
        # 创建一些测试图片文件
        test_images = [
            "test1.jpg",  # 未标注
            "test2.png",  # 未标注
            "test3.jpg",  # 已标注 (有对应的xml文件)
            "test4.bmp",  # 未标注
        ]
        
        for img in test_images:
            img_path = os.path.join(self.test_dir, img)
            with open(img_path, 'w') as f:
                f.write("fake image content")
        
        # 为test3创建标注文件，模拟已标注状态
        xml_path = os.path.join(self.test_dir, "test3.xml")
        with open(xml_path, 'w') as f:
            f.write("<?xml version='1.0'?><annotation></annotation>")
    
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 测试按钮
        test_btn = QPushButton("测试批量预测对话框")
        test_btn.clicked.connect(self.test_batch_dialog)
        layout.addWidget(test_btn)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    @pyqtSlot()
    def test_batch_dialog(self):
        """测试批量预测对话框"""
        try:
            dialog = BatchPredictionDialog(self, self.test_dir)
            dialog.prediction_started.connect(self.on_prediction_started)
            dialog.exec_()
        except Exception as e:
            print(f"对话框测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    @pyqtSlot(str, dict)
    def on_prediction_started(self, path, config):
        """处理预测开始信号"""
        print(f"预测开始:")
        print(f"  路径: {path}")
        print(f"  配置: {config}")
        
        # 模拟预测进度
        dialog = self.sender().parent()
        if hasattr(dialog, 'update_progress'):
            # 模拟进度更新
            total = config.get('total_images', 3)
            for i in range(total + 1):
                dialog.update_progress(i, total, f"test{i}.jpg" if i < total else "")
            
            # 模拟完成
            dialog.prediction_completed(total, total)
    
    def closeEvent(self, event):
        """清理测试数据"""
        import shutil
        try:
            shutil.rmtree(self.test_dir, ignore_errors=True)
        except:
            pass
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("BatchPredictionDialog Test")
    app.setApplicationVersion("1.0")
    
    # 创建并显示主窗口
    window = TestMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()