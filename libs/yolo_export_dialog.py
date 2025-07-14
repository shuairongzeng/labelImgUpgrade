#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QProgressBar,
                             QTextEdit, QGroupBox, QSpinBox, QMessageBox,
                             QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
from libs.pascal_to_yolo_converter import PascalToYOLOConverter
from libs.stringBundle import StringBundle
from libs.settings import Settings
from libs.constants import SETTING_YOLO_EXPORT_DIR

class ConvertThread(QThread):
    """转换线程"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    conversion_finished = pyqtSignal(bool, str)   # success, message
    
    def __init__(self, converter):
        super().__init__()
        self.converter = converter
        
    def run(self):
        """执行转换"""
        try:
            success, message = self.converter.convert(self.progress_callback)
            self.conversion_finished.emit(success, message)
        except Exception as e:
            self.conversion_finished.emit(False, str(e))
    
    def progress_callback(self, current, total, message):
        """进度回调"""
        self.progress_updated.emit(current, total, message)

class YOLOExportDialog(QDialog):
    """YOLO数据集导出对话框"""
    
    def __init__(self, parent=None, source_dir=None):
        super().__init__(parent)
        self.source_dir = source_dir or "."
        self.string_bundle = StringBundle.get_bundle()
        self.get_str = lambda str_id: self.string_bundle.get_string(str_id)

        # 加载设置
        self.settings = Settings()
        self.settings.load()

        self.init_ui()
        self.setup_style()

        # 加载上次的目标目录
        self.load_last_export_dir()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(self.get_str('exportYOLODialog'))
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel(self.get_str('exportYOLODialog'))
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 配置组
        config_group = QGroupBox("导出配置")
        config_layout = QVBoxLayout(config_group)
        
        # 源目录显示
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("源目录:"))
        self.source_label = QLabel(self.source_dir)
        self.source_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc; }")
        source_layout.addWidget(self.source_label)
        config_layout.addLayout(source_layout)
        
        # 目标目录选择
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标目录:"))
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("选择导出目录...")
        target_layout.addWidget(self.target_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_target_directory)
        target_layout.addWidget(self.browse_btn)
        config_layout.addLayout(target_layout)
        
        # 数据集名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(self.get_str('datasetName') + ":"))
        self.name_edit = QLineEdit("dataset")
        name_layout.addWidget(self.name_edit)
        config_layout.addLayout(name_layout)
        
        # 训练集比例
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel(self.get_str('trainRatio') + ":"))
        self.ratio_spinbox = QSpinBox()
        self.ratio_spinbox.setRange(50, 95)
        self.ratio_spinbox.setValue(80)
        self.ratio_spinbox.setSuffix("%")
        ratio_layout.addWidget(self.ratio_spinbox)
        ratio_layout.addStretch()
        config_layout.addLayout(ratio_layout)
        
        # 选项
        self.shuffle_checkbox = QCheckBox("随机打乱数据")
        self.shuffle_checkbox.setChecked(True)
        config_layout.addWidget(self.shuffle_checkbox)
        
        main_layout.addWidget(config_group)
        
        # 进度组
        progress_group = QGroupBox(self.get_str('exportProgress'))
        progress_layout = QVBoxLayout(progress_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备导出...")
        progress_layout.addWidget(self.status_label)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setVisible(False)
        progress_layout.addWidget(self.log_text)
        
        main_layout.addWidget(progress_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_btn = QPushButton("开始导出")
        self.export_btn.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # 转换线程
        self.convert_thread = None
        
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
            QSpinBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 4px;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            QCheckBox {
                font-size: 12px;
            }
        """)

    def load_last_export_dir(self):
        """加载上次的导出目录"""
        last_export_dir = self.settings.get(SETTING_YOLO_EXPORT_DIR, "")
        if last_export_dir and os.path.exists(last_export_dir):
            self.target_edit.setText(last_export_dir)

    def save_export_dir(self, directory):
        """保存导出目录到设置"""
        if directory and os.path.exists(directory):
            self.settings[SETTING_YOLO_EXPORT_DIR] = directory
            self.settings.save()

    def browse_target_directory(self):
        """浏览目标目录"""
        # 使用上次保存的目录作为起始目录，如果没有则使用当前输入框的内容或用户主目录
        start_dir = self.target_edit.text() or self.settings.get(SETTING_YOLO_EXPORT_DIR, os.path.expanduser("~"))

        directory = QFileDialog.getExistingDirectory(
            self,
            self.get_str('selectExportDir'),
            start_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if directory:
            self.target_edit.setText(directory)
            # 保存选择的目录到设置
            self.save_export_dir(directory)
    
    def validate_inputs(self):
        """验证输入"""
        if not self.target_edit.text().strip():
            QMessageBox.warning(self, "警告", "请选择目标目录")
            return False
            
        if not os.path.exists(self.target_edit.text()):
            QMessageBox.warning(self, "警告", "目标目录不存在")
            return False
            
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入数据集名称")
            return False
            
        # 检查源目录是否有XML文件
        xml_files = [f for f in os.listdir(self.source_dir) if f.lower().endswith('.xml')]
        if not xml_files:
            QMessageBox.warning(self, "警告", self.get_str('noAnnotations'))
            return False
            
        return True
    
    def start_export(self):
        """开始导出"""
        if not self.validate_inputs():
            return
            
        # 禁用控件
        self.export_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.target_edit.setEnabled(False)
        self.name_edit.setEnabled(False)
        self.ratio_spinbox.setEnabled(False)
        self.shuffle_checkbox.setEnabled(False)
        
        # 显示进度控件
        self.progress_bar.setVisible(True)
        self.log_text.setVisible(True)
        self.log_text.clear()
        
        # 创建转换器
        train_ratio = self.ratio_spinbox.value() / 100.0
        converter = PascalToYOLOConverter(
            source_dir=self.source_dir,
            target_dir=self.target_edit.text(),
            dataset_name=self.name_edit.text(),
            train_ratio=train_ratio
        )
        
        # 启动转换线程
        self.convert_thread = ConvertThread(converter)
        self.convert_thread.progress_updated.connect(self.update_progress)
        self.convert_thread.conversion_finished.connect(self.conversion_finished)
        self.convert_thread.start()
        
        self.status_label.setText("正在导出...")
        self.cancel_btn.setText("停止")
    
    def update_progress(self, current, total, message):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.progress_bar.setMaximum(total)
        self.status_label.setText(message)
        self.log_text.append(f"[{current}%] {message}")
        
        # 滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def conversion_finished(self, success, message):
        """转换完成"""
        # 恢复控件
        self.export_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.target_edit.setEnabled(True)
        self.name_edit.setEnabled(True)
        self.ratio_spinbox.setEnabled(True)
        self.shuffle_checkbox.setEnabled(True)
        self.cancel_btn.setText("关闭")
        
        if success:
            self.status_label.setText(self.get_str('exportComplete'))
            self.log_text.append(f"\n✅ {self.get_str('exportSuccess')}")
            self.log_text.append(f"详细信息:\n{message}")
            # 导出成功后保存目标目录
            self.save_export_dir(self.target_edit.text())
            
            # 显示成功消息
            QMessageBox.information(self, self.get_str('exportComplete'), 
                                  f"{self.get_str('exportSuccess')}\n\n{message}")
        else:
            self.status_label.setText(self.get_str('exportError'))
            self.log_text.append(f"\n❌ {self.get_str('exportError')}: {message}")
            
            # 显示错误消息
            QMessageBox.critical(self, self.get_str('exportError'), 
                               f"{self.get_str('exportError')}:\n{message}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.convert_thread and self.convert_thread.isRunning():
            reply = QMessageBox.question(self, "确认", "转换正在进行中，确定要关闭吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.convert_thread.terminate()
                self.convert_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def reject(self):
        """取消/关闭对话框"""
        if self.convert_thread and self.convert_thread.isRunning():
            reply = QMessageBox.question(self, "确认", "转换正在进行中，确定要取消吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.convert_thread.terminate()
                self.convert_thread.wait()
                super().reject()
        else:
            super().reject()
