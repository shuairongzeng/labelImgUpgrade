# -*- coding: utf-8 -*-
"""
图片裁剪对话框
支持选择文件夹、设置裁剪参数、批量裁剪图片和标注文件
"""

import os
import sys
from PIL import Image
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QSpinBox, QComboBox, 
                           QFileDialog, QProgressBar, QTextEdit, QGroupBox,
                           QFormLayout, QCheckBox, QFrame, QMessageBox,
                           QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap

from libs.ui_styles import ButtonStyles, LabelStyles, InteractionStyles, SpecialGroupBoxStyles


class ImageCropWorker(QThread):
    """图片裁剪工作线程"""
    progress_updated = pyqtSignal(int, str)  # 进度, 当前文件
    finished = pyqtSignal(int, int)  # 成功数量, 总数量
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, source_dir, crop_params):
        super().__init__()
        self.source_dir = source_dir
        self.crop_params = crop_params
        self.should_stop = False
        
    def stop(self):
        self.should_stop = True
        
    def run(self):
        try:
            self._process_images()
        except Exception as e:
            self.error_occurred.emit(f"处理过程中发生错误: {str(e)}")
    
    def _process_images(self):
        """处理图片裁剪"""
        source_images_dir = os.path.join(self.source_dir, 'images')
        source_labels_dir = os.path.join(self.source_dir, 'labels')
        
        # 创建输出目录
        target_images_dir = os.path.join(self.source_dir, 'cropped_images')
        target_labels_dir = os.path.join(self.source_dir, 'cropped_labels')
        
        os.makedirs(target_images_dir, exist_ok=True)
        os.makedirs(target_labels_dir, exist_ok=True)
        
        # 如果没有images子目录，直接在source_dir中查找图片
        if not os.path.exists(source_images_dir):
            source_images_dir = self.source_dir
            source_labels_dir = self.source_dir
        
        # 获取所有图片文件
        try:
            image_files = [f for f in os.listdir(source_images_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        except FileNotFoundError:
            self.error_occurred.emit(f"找不到图片目录: {source_images_dir}")
            return
            
        if not image_files:
            self.error_occurred.emit(f"在 '{source_images_dir}' 中没有找到任何图片文件")
            return

        total_files = len(image_files)
        processed_count = 0
        
        for i, image_filename in enumerate(image_files):
            if self.should_stop:
                break
                
            # 更新进度
            self.progress_updated.emit(int((i / total_files) * 100), image_filename)
            
            # 处理单个图片
            if self._process_single_image(source_images_dir, source_labels_dir,
                                         target_images_dir, target_labels_dir,
                                         image_filename):
                processed_count += 1
                
        # 发送完成信号
        self.finished.emit(processed_count, total_files)
    
    def _process_single_image(self, source_images_dir, source_labels_dir,
                             target_images_dir, target_labels_dir, image_filename):
        """处理单个图片和对应的标注文件"""
        try:
            # 图片路径
            image_path = os.path.join(source_images_dir, image_filename)
            
            # 对应的标注文件路径
            label_filename = os.path.splitext(image_filename)[0] + '.txt'
            label_path = os.path.join(source_labels_dir, label_filename)
            
            # 1. 裁剪图片
            with Image.open(image_path) as img:
                original_w, original_h = img.size
                
                # 计算裁剪区域
                crop_box = self._calculate_crop_box(original_w, original_h)
                
                if crop_box is None:
                    return False
                    
                cropped_img = img.crop(crop_box)
                
                # 保存裁剪后的图片
                cropped_img.save(os.path.join(target_images_dir, image_filename))
            
            # 2. 处理标注文件（如果存在）
            if os.path.exists(label_path):
                self._process_label_file(label_path, target_labels_dir, label_filename,
                                       original_w, original_h, crop_box)
                
            return True
            
        except Exception as e:
            print(f"处理图片 '{image_filename}' 时出错: {e}")
            return False
    
    def _calculate_crop_box(self, original_w, original_h):
        """计算裁剪区域"""
        crop_w = self.crop_params['crop_width']
        crop_h = self.crop_params['crop_height']
        direction = self.crop_params['direction']
        
        # 检查裁剪尺寸是否合理
        if crop_w > original_w or crop_h > original_h:
            return None
            
        # 根据方向计算裁剪起始位置
        if direction == "左往右":
            left = 0
            top = 0
        elif direction == "右往左":
            left = original_w - crop_w
            top = 0
        elif direction == "居中":
            left = (original_w - crop_w) // 2
            top = (original_h - crop_h) // 2
        else:  # 默认左上角
            left = 0
            top = 0
            
        return (left, top, left + crop_w, top + crop_h)
    
    def _process_label_file(self, label_path, target_labels_dir, label_filename,
                          original_w, original_h, crop_box):
        """处理标注文件"""
        left, top, right, bottom = crop_box
        crop_w = right - left
        crop_h = bottom - top
        
        new_labels = []
        
        with open(label_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                    
                class_id = parts[0]
                # 将归一化的坐标转为绝对像素坐标
                x_center_norm = float(parts[1])
                y_center_norm = float(parts[2])
                width_norm = float(parts[3])
                height_norm = float(parts[4])
                
                abs_x_center = x_center_norm * original_w
                abs_y_center = y_center_norm * original_h
                abs_width = width_norm * original_w
                abs_height = height_norm * original_h
                
                # 将绝对坐标转换为相对于裁剪区域的新坐标
                new_abs_x_center = abs_x_center - left
                new_abs_y_center = abs_y_center - top
                
                # 检查标注框是否在裁剪区域内
                if (new_abs_x_center - abs_width/2 >= 0 and 
                    new_abs_x_center + abs_width/2 <= crop_w and
                    new_abs_y_center - abs_height/2 >= 0 and 
                    new_abs_y_center + abs_height/2 <= crop_h):
                    
                    # 重新归一化坐标（基于新的裁剪尺寸）
                    new_x_center_norm = new_abs_x_center / crop_w
                    new_y_center_norm = new_abs_y_center / crop_h
                    new_width_norm = abs_width / crop_w
                    new_height_norm = abs_height / crop_h
                    
                    # 组装成新的标注行
                    new_labels.append(f"{class_id} {new_x_center_norm:.6f} {new_y_center_norm:.6f} {new_width_norm:.6f} {new_height_norm:.6f}")
        
        # 写入新的标注文件
        target_label_path = os.path.join(target_labels_dir, label_filename)
        with open(target_label_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_labels))


class ImageCropDialog(QDialog):
    """图片裁剪对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🖼️ 图片裁剪工具")
        self.setMinimumSize(600, 700)
        self.setMaximumSize(800, 800)
        
        # 工作线程
        self.worker = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("🖼️ 图片裁剪工具")
        title.setStyleSheet(LabelStyles.title_label())
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 描述
        desc = QLabel("批量裁剪图片和对应的标注文件，支持YOLO格式标注")
        desc.setStyleSheet(LabelStyles.subtitle_label())
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # 文件夹选择组
        folder_group = QGroupBox("📁 文件夹设置")
        folder_group.setStyleSheet(SpecialGroupBoxStyles.primary_action_group())
        folder_layout = QFormLayout(folder_group)
        
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("请选择包含图片的文件夹...")
        self.folder_path_edit.setStyleSheet(InteractionStyles.animated_input_field())
        
        self.browse_btn = QPushButton("📂 浏览")
        self.browse_btn.setStyleSheet(ButtonStyles.primary_button())
        
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_path_edit, 1)
        folder_row.addWidget(self.browse_btn)
        
        folder_layout.addRow("源文件夹:", folder_row)
        layout.addWidget(folder_group)
        
        # 裁剪参数组
        crop_group = QGroupBox("✂️ 裁剪参数")
        crop_group.setStyleSheet(SpecialGroupBoxStyles.primary_action_group())
        crop_layout = QFormLayout(crop_group)
        
        # 裁剪尺寸
        size_layout = QHBoxLayout()
        
        self.crop_width_spin = QSpinBox()
        self.crop_width_spin.setRange(50, 5000)
        self.crop_width_spin.setValue(200)
        self.crop_width_spin.setSuffix(" px")
        self.crop_width_spin.setStyleSheet(InteractionStyles.animated_input_field())
        
        self.crop_height_spin = QSpinBox()
        self.crop_height_spin.setRange(50, 5000)  
        self.crop_height_spin.setValue(200)
        self.crop_height_spin.setSuffix(" px")
        self.crop_height_spin.setStyleSheet(InteractionStyles.animated_input_field())
        
        size_layout.addWidget(QLabel("宽度:"))
        size_layout.addWidget(self.crop_width_spin)
        size_layout.addWidget(QLabel("高度:"))
        size_layout.addWidget(self.crop_height_spin)
        size_layout.addStretch()
        
        crop_layout.addRow("裁剪尺寸:", size_layout)
        
        # 裁剪方向
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["左往右", "右往左", "居中"])
        self.direction_combo.setCurrentText("右往左")
        self.direction_combo.setStyleSheet(InteractionStyles.animated_combobox())
        crop_layout.addRow("裁剪方向:", self.direction_combo)
        
        # 高级选项
        self.keep_aspect_ratio = QCheckBox("保持宽高比")
        self.keep_aspect_ratio.setChecked(True)
        crop_layout.addRow("选项:", self.keep_aspect_ratio)
        
        layout.addWidget(crop_group)
        
        # 预览信息组
        preview_group = QGroupBox("👀 预览信息")
        preview_group.setStyleSheet(SpecialGroupBoxStyles.primary_action_group())
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("请先选择文件夹以查看预览信息")
        self.preview_label.setStyleSheet(LabelStyles.info_label())
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(InteractionStyles.animated_progress_bar())
        layout.addWidget(self.progress_bar)
        
        # 日志输出
        log_group = QGroupBox("📋 处理日志")
        log_group.setStyleSheet(SpecialGroupBoxStyles.primary_action_group())
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 开始裁剪")
        self.start_btn.setStyleSheet(ButtonStyles.primary_button())
        self.start_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setStyleSheet(ButtonStyles.danger_button())
        self.stop_btn.setVisible(False)
        
        self.close_btn = QPushButton("❌ 关闭")
        self.close_btn.setStyleSheet(ButtonStyles.secondary_button())
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def setup_connections(self):
        """设置信号连接"""
        self.browse_btn.clicked.connect(self.browse_folder)
        self.start_btn.clicked.connect(self.start_cropping)
        self.stop_btn.clicked.connect(self.stop_cropping)
        self.close_btn.clicked.connect(self.close)
        
        # 监听文件夹路径变化
        self.folder_path_edit.textChanged.connect(self.update_preview)
        
        # 监听裁剪参数变化
        self.crop_width_spin.valueChanged.connect(self.update_preview)
        self.crop_height_spin.valueChanged.connect(self.update_preview)
        self.direction_combo.currentTextChanged.connect(self.update_preview)
        
    def browse_folder(self):
        """浏览选择文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "选择包含图片的文件夹",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.folder_path_edit.setText(folder)
            
    def update_preview(self):
        """更新预览信息"""
        folder_path = self.folder_path_edit.text().strip()
        
        if not folder_path or not os.path.exists(folder_path):
            self.preview_label.setText("请选择有效的文件夹路径")
            self.start_btn.setEnabled(False)
            return
            
        # 检查文件夹内容
        images_dir = os.path.join(folder_path, 'images')
        if not os.path.exists(images_dir):
            images_dir = folder_path
            
        try:
            image_files = [f for f in os.listdir(images_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
                          
            labels_dir = os.path.join(folder_path, 'labels')
            if not os.path.exists(labels_dir):
                labels_dir = folder_path
                
            label_files = [f for f in os.listdir(labels_dir) 
                          if f.lower().endswith('.txt')]
                          
        except OSError:
            self.preview_label.setText("无法读取文件夹内容")
            self.start_btn.setEnabled(False)
            return
            
        # 更新预览信息
        crop_w = self.crop_width_spin.value()
        crop_h = self.crop_height_spin.value()
        direction = self.direction_combo.currentText()
        
        preview_text = f"""📊 文件夹分析:
• 图片文件: {len(image_files)} 个
• 标注文件: {len(label_files)} 个  
• 裁剪尺寸: {crop_w} × {crop_h} 像素
• 裁剪方向: {direction}
• 输出位置: {folder_path}/cropped_images 和 {folder_path}/cropped_labels

💡 提示: 裁剪后的文件将保存在源文件夹的子目录中"""

        self.preview_label.setText(preview_text)
        self.start_btn.setEnabled(len(image_files) > 0)
        
    def start_cropping(self):
        """开始裁剪"""
        folder_path = self.folder_path_edit.text().strip()
        
        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "警告", "请选择有效的文件夹路径")
            return
            
        # 准备裁剪参数
        crop_params = {
            'crop_width': self.crop_width_spin.value(),
            'crop_height': self.crop_height_spin.value(),
            'direction': self.direction_combo.currentText()
        }
        
        # 创建工作线程
        self.worker = ImageCropWorker(folder_path, crop_params)
        
        # 连接信号
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.crop_finished)
        self.worker.error_occurred.connect(self.crop_error)
        
        # 更新UI状态
        self.start_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 清空日志
        self.log_text.clear()
        self.log_text.append("🚀 开始批量裁剪...")
        
        # 启动线程
        self.worker.start()
        
    def stop_cropping(self):
        """停止裁剪"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_text.append("⏹️ 正在停止处理...")
            
    def update_progress(self, progress, filename):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.log_text.append(f"📷 处理中: {filename}")
        
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
        
    def crop_finished(self, success_count, total_count):
        """裁剪完成"""
        # 更新UI状态
        self.start_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        
        # 显示结果
        self.log_text.append("=" * 50)
        self.log_text.append(f"✅ 裁剪完成！")
        self.log_text.append(f"📊 成功处理: {success_count}/{total_count} 张图片")
        
        if success_count > 0:
            folder_path = self.folder_path_edit.text().strip()
            self.log_text.append(f"📂 裁剪后的图片保存在: {folder_path}/cropped_images")
            self.log_text.append(f"📂 转换后的标注保存在: {folder_path}/cropped_labels")
            
            # 显示成功消息
            QMessageBox.information(
                self, 
                "处理完成", 
                f"成功处理了 {success_count}/{total_count} 张图片！\n\n"
                f"裁剪后的文件已保存到:\n"
                f"• {folder_path}/cropped_images\n"
                f"• {folder_path}/cropped_labels"
            )
        
        # 清理线程
        self.worker = None
        
    def crop_error(self, error_msg):
        """处理错误"""
        # 更新UI状态
        self.start_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        
        # 显示错误
        self.log_text.append("=" * 50)
        self.log_text.append(f"❌ 处理失败: {error_msg}")
        
        QMessageBox.critical(self, "错误", f"处理过程中发生错误:\n{error_msg}")
        
        # 清理线程
        self.worker = None
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "裁剪正在进行中，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait(3000)  # 等待3秒
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()