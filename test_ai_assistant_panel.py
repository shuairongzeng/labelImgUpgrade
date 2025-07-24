#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI助手界面面板测试脚本

测试AI助手界面面板的功能和界面
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from libs.ai_assistant_panel import AIAssistantPanel

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("AI助手面板测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：模拟的图像显示区域
        left_widget = QWidget()
        left_widget.setMinimumWidth(600)
        left_layout = QVBoxLayout(left_widget)
        
        # 图像显示标签
        self.image_label = QLabel("图像显示区域")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                background-color: #f9f9f9;
                font-size: 18px;
                color: #666666;
                min-height: 400px;
            }
        """)
        left_layout.addWidget(self.image_label)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.load_image_btn = QPushButton("📁 加载图像")
        self.load_image_btn.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_image_btn)
        
        self.current_image_path = ""
        self.image_path_label = QLabel("未选择图像")
        control_layout.addWidget(self.image_path_label)
        
        control_layout.addStretch()
        left_layout.addLayout(control_layout)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setPlainText("=== AI助手面板测试日志 ===\n")
        left_layout.addWidget(self.log_text)
        
        main_layout.addWidget(left_widget)
        
        # 右侧：AI助手面板
        self.ai_panel = AIAssistantPanel(self)
        self.ai_panel.setMinimumWidth(350)
        self.ai_panel.setMaximumWidth(400)
        main_layout.addWidget(self.ai_panel)
        
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
    
    def setup_connections(self):
        """设置信号连接"""
        # 连接AI助手面板信号
        self.ai_panel.prediction_requested.connect(self.on_prediction_requested)
        self.ai_panel.batch_prediction_requested.connect(self.on_batch_prediction_requested)
        self.ai_panel.predictions_applied.connect(self.on_predictions_applied)
        self.ai_panel.model_changed.connect(self.on_model_changed)
    
    def load_image(self):
        """加载图像"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择图像文件", "", 
                "图像文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp)"
            )
            
            if file_path:
                self.current_image_path = file_path
                self.image_path_label.setText(f"当前图像: {os.path.basename(file_path)}")
                
                # 加载并显示图像
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 缩放图像以适应显示区域
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    
                    self.log_message(f"✓ 图像加载成功: {os.path.basename(file_path)}")
                else:
                    self.log_message(f"✗ 图像加载失败: {file_path}")
                    
        except Exception as e:
            self.log_message(f"✗ 加载图像异常: {str(e)}")
    
    def on_prediction_requested(self, image_path: str, confidence: float):
        """处理预测请求"""
        try:
            self.log_message(f"🎯 收到预测请求，置信度: {confidence}")
            
            if not self.current_image_path:
                self.log_message("⚠️  请先加载图像")
                return
            
            # 使用AI面板进行预测
            success = self.ai_panel.predict_image(self.current_image_path)
            if success:
                self.log_message(f"✓ 开始预测图像: {os.path.basename(self.current_image_path)}")
            else:
                self.log_message("✗ 预测启动失败")
                
        except Exception as e:
            self.log_message(f"✗ 预测请求处理异常: {str(e)}")
    
    def on_batch_prediction_requested(self, dir_path: str, confidence: float):
        """处理批量预测请求"""
        try:
            self.log_message(f"📁 收到批量预测请求: {dir_path}")
            self.log_message(f"   置信度阈值: {confidence}")
            
            # 使用AI面板进行批量预测
            success = self.ai_panel.start_batch_prediction(dir_path)
            if success:
                self.log_message(f"✓ 开始批量预测目录: {dir_path}")
            else:
                self.log_message("✗ 批量预测启动失败")
                
        except Exception as e:
            self.log_message(f"✗ 批量预测请求处理异常: {str(e)}")
    
    def on_predictions_applied(self, detections: list):
        """处理预测结果应用"""
        try:
            self.log_message(f"✅ 应用预测结果: {len(detections)} 个检测框")
            
            # 在这里可以将检测结果绘制到图像上
            for i, detection in enumerate(detections):
                self.log_message(
                    f"   {i+1}. {detection.class_name} "
                    f"(置信度: {detection.confidence:.3f})"
                )
            
        except Exception as e:
            self.log_message(f"✗ 预测结果应用处理异常: {str(e)}")
    
    def on_model_changed(self, model_path: str):
        """处理模型切换"""
        try:
            model_name = os.path.basename(model_path)
            self.log_message(f"🔄 模型已切换: {model_name}")
            
        except Exception as e:
            self.log_message(f"✗ 模型切换处理异常: {str(e)}")
    
    def log_message(self, message: str):
        """添加日志消息"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            
            self.log_text.append(log_entry)
            
            # 自动滚动到底部
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.End)
            self.log_text.setTextCursor(cursor)
            
            # 同时输出到控制台
            print(log_entry)
            
        except Exception as e:
            print(f"日志记录失败: {str(e)}")


def test_ai_panel_standalone():
    """独立测试AI助手面板"""
    print("=" * 60)
    print("独立测试 AI助手面板")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建独立的AI助手面板
    panel = AIAssistantPanel()
    panel.setWindowTitle("AI助手面板 - 独立测试")
    panel.resize(400, 800)
    panel.show()
    
    print("✓ AI助手面板创建成功")
    print("✓ 面板已显示，请在界面中测试功能")
    
    return app.exec_()


def test_ai_panel_integrated():
    """集成测试AI助手面板"""
    print("=" * 60)
    print("集成测试 AI助手面板")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试主窗口
    window = TestMainWindow()
    window.show()
    
    print("✓ 测试主窗口创建成功")
    print("✓ AI助手面板已集成到主窗口")
    print("✓ 请在界面中测试以下功能：")
    print("   1. 加载图像")
    print("   2. 选择模型")
    print("   3. 调整预测参数")
    print("   4. 执行单图预测")
    print("   5. 执行批量预测")
    print("   6. 应用预测结果")
    
    return app.exec_()


def main():
    """主测试函数"""
    print("AI助手界面面板测试")
    print("=" * 80)
    
    # 检查必要的目录
    if not os.path.exists("models"):
        os.makedirs("models")
        print("✓ 创建models目录")
    
    if not os.path.exists("config"):
        os.makedirs("config")
        print("✓ 创建config目录")
    
    # 选择测试模式
    print("\n请选择测试模式：")
    print("1. 独立测试AI助手面板")
    print("2. 集成测试AI助手面板")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            return test_ai_panel_standalone()
        elif choice == "2":
            return test_ai_panel_integrated()
        else:
            print("无效选择，默认使用集成测试")
            return test_ai_panel_integrated()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 0
    except Exception as e:
        print(f"测试异常: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
