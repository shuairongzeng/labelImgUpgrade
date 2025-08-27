# -*- coding: utf-8 -*-
"""
批量操作进度显示组件
提供实时的批量操作进度反馈
"""

from typing import Optional

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


class BatchProgressWidget(QWidget):
    """
    批量操作进度显示组件
    
    功能特性：
    - 实时进度显示
    - 操作状态指示
    - 取消操作支持
    - 详细信息展示
    """
    
    # 信号定义
    cancel_requested = pyqtSignal()  # 取消请求信号
    details_requested = pyqtSignal()  # 详情请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self.is_active = False
        self.current_operation = ""
        self.start_time = None
        
        # 创建UI
        self.setup_ui()
        
        # 初始状态隐藏
        self.hide()
        
    def setup_ui(self):
        """设置UI组件"""
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 状态图标
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(24, 24)
        self.status_icon.setScaledContents(True)
        layout.addWidget(self.status_icon)
        
        # 信息区域
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # 操作描述
        self.operation_label = QLabel("批量操作进行中...")
        self.operation_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #495057;
                border: none;
            }
        """)
        info_layout.addWidget(self.operation_label)
        
        # 进度信息
        self.progress_label = QLabel("准备中...")
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                border: none;
            }
        """)
        info_layout.addWidget(self.progress_label)
        
        layout.addLayout(info_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                text-align: center;
                font-size: 11px;
                font-weight: 600;
                color: #495057;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:1 #20c997);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 操作按钮
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(60, 24)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_requested.emit)
        button_layout.addWidget(self.cancel_button)
        
        # 详情按钮
        self.details_button = QPushButton("详情")
        self.details_button.setFixedSize(60, 24)
        self.details_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        self.details_button.clicked.connect(self.details_requested.emit)
        button_layout.addWidget(self.details_button)
        
        layout.addLayout(button_layout)
        
    def start_operation(self, operation_name: str, total_items: int = 0):
        """
        开始操作
        
        Args:
            operation_name: 操作名称
            total_items: 总项目数
        """
        self.is_active = True
        self.current_operation = operation_name
        self.start_time = QTime.currentTime()
        
        # 更新UI
        self.operation_label.setText(f"🔄 {operation_name}")
        self.progress_label.setText("准备中...")
        self.progress_bar.setValue(0)
        
        if total_items > 0:
            self.progress_bar.setMaximum(total_items)
        else:
            self.progress_bar.setMaximum(100)
            
        # 设置状态图标
        self._set_status_icon("running")
        
        # 显示组件
        self.show()
        
    def update_progress(self, current: int, total: int = None, message: str = ""):
        """
        更新进度
        
        Args:
            current: 当前进度
            total: 总数（可选）
            message: 进度消息
        """
        if not self.is_active:
            return
            
        if total is not None and total > 0:
            self.progress_bar.setMaximum(total)
            percentage = int((current / total) * 100)
        else:
            percentage = current
            
        self.progress_bar.setValue(current)
        
        # 更新进度文本
        if message:
            progress_text = f"{percentage}% - {message}"
        else:
            progress_text = f"{percentage}% ({current}/{self.progress_bar.maximum()})"
            
        # 添加耗时信息
        if self.start_time:
            elapsed = self.start_time.secsTo(QTime.currentTime())
            if elapsed > 0:
                progress_text += f" - 耗时: {elapsed}秒"
                
                # 估算剩余时间
                if percentage > 0:
                    estimated_total = (elapsed * 100) / percentage
                    remaining = int(estimated_total - elapsed)
                    if remaining > 0:
                        progress_text += f" - 预计剩余: {remaining}秒"
                        
        self.progress_label.setText(progress_text)
        
    def complete_operation(self, success: bool = True, message: str = ""):
        """
        完成操作
        
        Args:
            success: 是否成功
            message: 完成消息
        """
        if not self.is_active:
            return
            
        self.is_active = False
        
        if success:
            self.operation_label.setText(f"✅ {self.current_operation} - 完成")
            self.progress_label.setText(message or "操作成功完成")
            self.progress_bar.setValue(self.progress_bar.maximum())
            self._set_status_icon("success")
        else:
            self.operation_label.setText(f"❌ {self.current_operation} - 失败")
            self.progress_label.setText(message or "操作失败")
            self._set_status_icon("error")
            
        # 禁用取消按钮
        self.cancel_button.setEnabled(False)
        
        # 3秒后自动隐藏
        QTimer.singleShot(3000, self.hide_delayed)
        
    def cancel_operation(self, message: str = ""):
        """
        取消操作
        
        Args:
            message: 取消消息
        """
        if not self.is_active:
            return
            
        self.is_active = False
        
        self.operation_label.setText(f"🚫 {self.current_operation} - 已取消")
        self.progress_label.setText(message or "操作已被用户取消")
        self._set_status_icon("cancelled")
        
        # 禁用取消按钮
        self.cancel_button.setEnabled(False)
        
        # 2秒后自动隐藏
        QTimer.singleShot(2000, self.hide_delayed)
        
    def hide_delayed(self):
        """延迟隐藏"""
        if not self.is_active:  # 只有在非活跃状态下才隐藏
            self.hide()
            # 重置状态
            self.cancel_button.setEnabled(True)
            
    def _set_status_icon(self, status: str):
        """设置状态图标"""
        icon_map = {
            "running": "🔄",
            "success": "✅", 
            "error": "❌",
            "cancelled": "🚫"
        }
        
        icon_text = icon_map.get(status, "🔄")
        self.status_icon.setText(icon_text)
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 18px;
                border: none;
                text-align: center;
            }
        """)
        
    def reset(self):
        """重置组件状态"""
        self.is_active = False
        self.current_operation = ""
        self.start_time = None
        self.cancel_button.setEnabled(True)
        self.hide()


class BatchProgressDialog(QDialog):
    """批量操作进度对话框（用于显示详细信息）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量操作详情")
        self.setFixedSize(500, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 详情文本区域
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.details_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def set_details(self, details: str):
        """设置详情文本"""
        self.details_text.setPlainText(details)
        
    def append_details(self, text: str):
        """追加详情文本"""
        self.details_text.append(text)