#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
删除确认对话框模块
提供智能的删除确认功能，支持"不再提示"选项
"""

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from libs.settings import Settings


class DeleteConfirmationDialog(QDialog):
    """智能删除确认对话框"""
    
    def __init__(self, parent=None, file_path=None, operation_type="delete_current"):
        super().__init__(parent)
        self.file_path = file_path
        self.operation_type = operation_type  # "delete_current" 或 "delete_menu"
        self.dont_ask_again = False
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("🗑️ 确认删除操作")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
        self.setModal(True)
        self.setFixedSize(480, 320)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #e74c3c;
                border-radius: 8px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QLabel#titleLabel {
                color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#warningLabel {
                color: #e67e22;
                font-size: 12px;
                font-weight: 500;
            }
            QLabel#fileInfoLabel {
                color: #34495e;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
            QCheckBox {
                color: #2c3e50;
                font-size: 12px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
                min-height: 16px;
            }
            QPushButton#deleteButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#deleteButton:hover {
                background-color: #c0392b;
            }
            QPushButton#cancelButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton#cancelButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        # 警告图标
        icon_label = QLabel()
        icon_pixmap = self.style().standardIcon(QStyle.SP_MessageBoxWarning).pixmap(32, 32)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(32, 32)
        title_layout.addWidget(icon_label)
        
        # 标题文字
        title_label = QLabel("确认删除操作")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 文件信息区域
        if self.file_path:
            file_info = self.create_file_info_widget()
            main_layout.addWidget(file_info)
        
        # 警告信息
        warning_label = QLabel("⚠️ 警告：此操作将永久删除文件，无法撤销！")
        warning_label.setObjectName("warningLabel")
        warning_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(warning_label)
        
        # 详细说明
        detail_text = (
            "• 图片文件将从磁盘彻底删除\n"
            "• 对应的标注文件也会被删除\n"
            "• 文件将从当前项目列表中移除"
        )
        detail_label = QLabel(detail_text)
        detail_label.setWordWrap(True)
        main_layout.addWidget(detail_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #bdc3c7;")
        main_layout.addWidget(line)
        
        # "不再提示"复选框
        self.dont_ask_checkbox = QCheckBox("🔕 不再显示此确认对话框（可在设置中恢复）")
        self.dont_ask_checkbox.setToolTip(
            "勾选后，后续删除操作将直接执行，不再显示确认对话框。\n"
            "您可以通过菜单 -> 设置 -> 重置删除确认 来恢复此对话框。"
        )
        main_layout.addWidget(self.dont_ask_checkbox)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        self.cancel_button = QPushButton("❌ 取消")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 删除按钮
        self.delete_button = QPushButton("🗑️ 确认删除")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.accept)
        self.delete_button.setDefault(False)  # 不设为默认按钮，防止误操作
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置焦点到取消按钮，防止误操作
        self.cancel_button.setFocus()
        
    def create_file_info_widget(self):
        """创建文件信息显示组件"""
        file_info_widget = QWidget()
        file_info_layout = QVBoxLayout(file_info_widget)
        file_info_layout.setContentsMargins(0, 0, 0, 0)
        file_info_layout.setSpacing(4)
        
        if self.file_path and os.path.exists(self.file_path):
            filename = os.path.basename(self.file_path)
            file_dir = os.path.dirname(self.file_path)
            file_size = os.path.getsize(self.file_path)
            
            # 格式化文件大小
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            info_text = (
                f"📁 文件名: {filename}\n"
                f"📂 位置: {file_dir}\n"
                f"📏 大小: {size_str}"
            )
        else:
            info_text = "❌ 文件信息获取失败"
        
        info_label = QLabel(info_text)
        info_label.setObjectName("fileInfoLabel")
        info_label.setWordWrap(True)
        file_info_layout.addWidget(info_label)
        
        return file_info_widget
    
    def load_settings(self):
        """加载设置"""
        try:
            settings = Settings()
            settings.load()
            
            # 检查是否已禁用确认对话框
            setting_key = f'delete_confirmation_disabled_{self.operation_type}'
            self.dont_ask_again = settings.get(setting_key, False)
            
        except Exception as e:
            print(f"加载删除确认设置失败: {e}")
            self.dont_ask_again = False
    
    def save_settings(self):
        """保存设置"""
        try:
            settings = Settings()
            settings.load()
            
            # 保存"不再提示"设置
            setting_key = f'delete_confirmation_disabled_{self.operation_type}'
            settings[setting_key] = self.dont_ask_checkbox.isChecked()
            settings.save()
            
        except Exception as e:
            print(f"保存删除确认设置失败: {e}")
    
    def accept(self):
        """确认删除"""
        # 保存设置
        self.save_settings()
        super().accept()
    
    @staticmethod
    def should_show_confirmation(operation_type="delete_current"):
        """检查是否应该显示确认对话框"""
        try:
            settings = Settings()
            settings.load()
            setting_key = f'delete_confirmation_disabled_{operation_type}'
            return not settings.get(setting_key, False)
        except Exception as e:
            print(f"检查删除确认设置失败: {e}")
            return True  # 默认显示确认对话框
    
    @staticmethod
    def reset_confirmation_settings():
        """重置确认设置（恢复显示确认对话框）"""
        try:
            settings = Settings()
            settings.load()
            
            # 重置所有删除确认设置
            for operation_type in ["delete_current", "delete_menu"]:
                setting_key = f'delete_confirmation_disabled_{operation_type}'
                if setting_key in settings.data:
                    del settings.data[setting_key]
            
            settings.save()
            return True
        except Exception as e:
            print(f"重置删除确认设置失败: {e}")
            return False


class SimpleDeleteConfirmationDialog(QMessageBox):
    """简化的删除确认对话框（当用户选择不再提示时使用）"""
    
    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setup_ui()
    
    def setup_ui(self):
        """设置简化的UI"""
        self.setWindowTitle("确认删除")
        self.setIcon(QMessageBox.Warning)
        
        if self.file_path:
            filename = os.path.basename(self.file_path)
            self.setText(f"确定要删除文件 '{filename}' 吗？")
            self.setInformativeText("此操作不可撤销。")
        else:
            self.setText("确定要删除当前文件吗？")
            self.setInformativeText("此操作不可撤销。")
        
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        
        # 自定义按钮文字
        self.button(QMessageBox.Yes).setText("删除")
        self.button(QMessageBox.No).setText("取消")
