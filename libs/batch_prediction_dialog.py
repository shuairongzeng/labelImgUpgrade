"""
批量预测配置对话框
提供用户友好的批量预测配置界面
"""

import os
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QCheckBox, QSlider,
                             QProgressBar, QTextEdit, QGroupBox, QSpinBox,
                             QFileDialog, QFormLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)

class BatchPredictionDialog(QDialog):
    """批量预测配置对话框"""
    
    # 信号定义
    prediction_started = pyqtSignal(str, dict)  # 开始预测信号 (目录路径, 配置参数)
    
    def __init__(self, parent=None, default_path=""):
        super().__init__(parent)
        
        self.default_path = default_path
        self.current_path = default_path
        self.total_images = 0
        self.to_predict_images = 0
        
        # 如果默认路径为空或不存在，提示用户选择
        if not default_path or not os.path.exists(default_path):
            self.current_path = ""
        
        self.setup_ui()
        self.setup_connections()
        
        # 只有在有有效路径时才扫描目录
        if self.current_path and os.path.exists(self.current_path):
            self.scan_directory()
        else:
            self.update_stats(0, 0)
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("批量预测配置")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # 路径配置组
        path_group = self.create_path_group()
        layout.addWidget(path_group)
        
        # 预测参数组
        params_group = self.create_params_group()
        layout.addWidget(params_group)
        
        # 统计信息组
        stats_group = self.create_stats_group()
        layout.addWidget(stats_group)
        
        # 进度显示组
        progress_group = self.create_progress_group()
        layout.addWidget(progress_group)
        
        # 操作按钮
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def create_path_group(self):
        """创建路径配置组"""
        group = QGroupBox("预测目录")
        layout = QVBoxLayout()
        
        # 当前路径显示
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("当前路径:"))
        
        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("请选择图片目录...")
        path_layout.addWidget(self.path_edit)
        
        # 重新选择按钮
        self.browse_btn = QPushButton("重新选择")
        self.browse_btn.setMaximumWidth(100)
        path_layout.addWidget(self.browse_btn)
        
        layout.addLayout(path_layout)
        group.setLayout(layout)
        return group
    
    def create_params_group(self):
        """创建预测参数组"""
        group = QGroupBox("预测参数")
        layout = QFormLayout()
        
        # 置信度设置
        confidence_layout = QHBoxLayout()
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(1, 100)
        self.confidence_slider.setValue(25)
        confidence_layout.addWidget(self.confidence_slider)
        
        self.confidence_label = QLabel("0.25")
        confidence_layout.addWidget(self.confidence_label)
        layout.addRow("置信度阈值:", confidence_layout)
        
        # NMS设置
        nms_layout = QHBoxLayout()
        self.nms_slider = QSlider(Qt.Horizontal)
        self.nms_slider.setRange(1, 100)
        self.nms_slider.setValue(45)
        nms_layout.addWidget(self.nms_slider)
        
        self.nms_label = QLabel("0.45")
        nms_layout.addWidget(self.nms_label)
        layout.addRow("NMS阈值:", nms_layout)
        
        # 最大检测数
        self.max_det_spin = QSpinBox()
        self.max_det_spin.setRange(1, 1000)
        self.max_det_spin.setValue(300)
        layout.addRow("最大检测数:", self.max_det_spin)
        
        # 过滤选项
        self.skip_annotated_cb = QCheckBox("跳过已标注图片")
        self.skip_annotated_cb.setChecked(True)
        layout.addRow("", self.skip_annotated_cb)
        
        group.setLayout(layout)
        return group
    
    def create_stats_group(self):
        """创建统计信息组"""
        group = QGroupBox("统计信息")
        layout = QFormLayout()
        
        self.total_images_label = QLabel("0")
        layout.addRow("总图片数:", self.total_images_label)
        
        self.to_predict_label = QLabel("0")
        layout.addRow("待预测数:", self.to_predict_label)
        
        self.skip_count_label = QLabel("0")
        layout.addRow("跳过数量:", self.skip_count_label)
        
        group.setLayout(layout)
        return group
    
    def create_progress_group(self):
        """创建进度显示组"""
        group = QGroupBox("预测进度")
        layout = QVBoxLayout()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
    
    def create_buttons(self):
        """创建操作按钮"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        # 开始预测按钮
        self.start_btn = QPushButton("开始批量预测")
        self.start_btn.setMinimumWidth(120)
        layout.addWidget(self.start_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumWidth(80)
        layout.addWidget(self.cancel_btn)
        
        return layout
    
    def setup_connections(self):
        """设置信号连接"""
        self.browse_btn.clicked.connect(self.browse_directory)
        self.start_btn.clicked.connect(self.start_prediction)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        self.nms_slider.valueChanged.connect(self.update_nms_label)
        self.skip_annotated_cb.toggled.connect(self.scan_directory)
    
    def browse_directory(self):
        """浏览选择目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择图像目录", self.current_path, 
            QFileDialog.ShowDirsOnly
        )
        
        if dir_path:
            self.current_path = dir_path
            self.path_edit.setText(dir_path)
            self.scan_directory()
    
    def scan_directory(self):
        """扫描目录统计图片信息"""
        if not self.current_path or not os.path.exists(self.current_path):
            self.update_stats(0, 0)
            return
        
        try:
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            all_images = []
            
            # 扫描所有图片文件
            for file_name in os.listdir(self.current_path):
                file_path = os.path.join(self.current_path, file_name)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file_name.lower())
                    if ext in image_extensions:
                        all_images.append(file_name)
            
            self.total_images = len(all_images)
            
            # 计算需要预测的图片数量
            if self.skip_annotated_cb.isChecked():
                to_predict = []
                for img_name in all_images:
                    if not self.is_image_annotated(img_name):
                        to_predict.append(img_name)
                self.to_predict_images = len(to_predict)
            else:
                self.to_predict_images = self.total_images
            
            self.update_stats(self.total_images, self.to_predict_images)
            
        except Exception as e:
            logger.error(f"扫描目录失败: {e}")
            self.update_stats(0, 0)
    
    def is_image_annotated(self, image_name):
        """
        判断图片是否已经标注过
        判断规则：图片名称不包含后缀的数量大于1，就表示这个图片已经预测过
        """
        try:
            # 获取不带扩展名的文件名
            base_name = os.path.splitext(image_name)[0]
            
            # 检查目录中是否存在同名的标注文件
            dir_files = os.listdir(self.current_path)
            
            # 统计同名文件数量（不包含扩展名）
            same_name_count = 0
            for file_name in dir_files:
                file_base = os.path.splitext(file_name)[0]
                if file_base == base_name:
                    same_name_count += 1
            
            # 如果同名文件数量大于1，说明已经标注过
            return same_name_count > 1
            
        except Exception as e:
            logger.error(f"检查标注状态失败: {e}")
            return False
    
    def update_stats(self, total, to_predict):
        """更新统计信息显示"""
        self.total_images_label.setText(str(total))
        self.to_predict_label.setText(str(to_predict))
        self.skip_count_label.setText(str(total - to_predict))
        
        # 更新按钮状态和提示
        if not self.current_path or not os.path.exists(self.current_path):
            self.start_btn.setEnabled(False)
            self.start_btn.setText("请先选择目录")
        elif to_predict > 0:
            self.start_btn.setEnabled(True)
            self.start_btn.setText("开始批量预测")
        else:
            self.start_btn.setEnabled(False)
            self.start_btn.setText("无图片需要预测")
    
    def update_confidence_label(self):
        """更新置信度标签"""
        value = self.confidence_slider.value() / 100.0
        self.confidence_label.setText(f"{value:.2f}")
    
    def update_nms_label(self):
        """更新NMS标签"""
        value = self.nms_slider.value() / 100.0
        self.nms_label.setText(f"{value:.2f}")
    
    def start_prediction(self):
        """开始批量预测"""
        if self.to_predict_images == 0:
            return
        
        # 收集配置参数
        config = {
            'confidence': self.confidence_slider.value() / 100.0,
            'nms': self.nms_slider.value() / 100.0,
            'max_det': self.max_det_spin.value(),
            'skip_annotated': self.skip_annotated_cb.isChecked(),
            'total_images': self.to_predict_images
        }
        
        # 显示进度界面
        self.show_progress_ui()
        
        # 发射开始预测信号
        self.prediction_started.emit(self.current_path, config)
    
    def show_progress_ui(self):
        """显示进度界面"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(self.to_predict_images)
        
        self.log_text.setVisible(True)
        self.status_label.setText("正在进行批量预测...")
        
        # 禁用配置控件
        self.start_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        
        # 调整窗口大小
        self.resize(500, 600)
    
    def update_progress(self, current, total, current_file=""):
        """更新预测进度"""
        self.progress_bar.setValue(current)
        
        progress_percent = (current / total * 100) if total > 0 else 0
        status_text = f"预测进度: {current}/{total} ({progress_percent:.1f}%)"
        
        if current_file:
            status_text += f" - {os.path.basename(current_file)}"
        
        self.status_label.setText(status_text)
        
        # 添加日志
        if current_file:
            self.log_text.append(f"正在预测: {os.path.basename(current_file)}")
    
    def prediction_completed(self, successful, total, errors=None):
        """预测完成"""
        self.progress_bar.setValue(total)
        self.status_label.setText(f"批量预测完成: 成功 {successful}/{total}")
        
        # 添加完成日志
        self.log_text.append(f"\n批量预测完成!")
        self.log_text.append(f"成功预测: {successful}/{total} 个文件")
        
        if errors:
            self.log_text.append(f"失败: {len(errors)} 个文件")
            for error in errors[:5]:  # 只显示前5个错误
                self.log_text.append(f"  - {error}")
        
        # 重新启用按钮
        self.start_btn.setText("重新预测")
        self.start_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
    
    def prediction_cancelled(self):
        """预测取消"""
        self.status_label.setText("批量预测已取消")
        self.log_text.append("批量预测已取消")
        
        # 重新启用按钮
        self.start_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
    
    def get_prediction_config(self):
        """获取预测配置"""
        return {
            'path': self.current_path,
            'confidence': self.confidence_slider.value() / 100.0,
            'nms': self.nms_slider.value() / 100.0,
            'max_det': self.max_det_spin.value(),
            'skip_annotated': self.skip_annotated_cb.isChecked()
        }