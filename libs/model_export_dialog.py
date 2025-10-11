#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型导出对话框模块

提供YOLO模型导出为其他格式（ONNX、TensorRT等）的用户界面
"""

import os
import sys
import time
import logging
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

# 导入项目模块
from libs.stringBundle import StringBundle
from libs.settings import Settings
from libs.constants import *
from libs.ai_assistant.model_manager import ModelManager

# 导入YOLO相关库
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# 设置日志
logger = logging.getLogger(__name__)


class ExportConfig:
    """导出配置类"""
    
    def __init__(self):
        self.model_path = ""
        self.export_format = "onnx"
        self.output_dir = ""
        self.output_name = ""
        
        # ONNX参数
        self.onnx_opset = 12
        self.onnx_dynamic = False
        self.onnx_simplify = True
        
        # TensorRT参数
        self.tensorrt_precision = "fp16"
        self.tensorrt_workspace = 4
        
        # 通用参数
        self.image_size = 640
        self.batch_size = 1
        self.device = "cpu"


class ModelExportThread(QThread):
    """模型导出线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str)  # 进度更新
    log_message = pyqtSignal(str)            # 日志消息
    export_completed = pyqtSignal(bool, str) # 导出完成
    
    def __init__(self, config: ExportConfig):
        super().__init__()
        self.config = config
        self.is_cancelled = False
    
    def cancel(self):
        """取消导出"""
        self.is_cancelled = True
    
    def run(self):
        """执行导出"""
        try:
            self.log_message.emit("开始模型导出...")
            self.progress_updated.emit(10, "正在加载模型...")
            
            if not YOLO_AVAILABLE:
                raise Exception("ultralytics库未安装，无法进行模型导出")
            
            # 检查模型文件
            if not os.path.exists(self.config.model_path):
                raise Exception(f"模型文件不存在: {self.config.model_path}")
            
            # 加载模型
            self.log_message.emit(f"加载模型: {self.config.model_path}")
            model = YOLO(self.config.model_path)
            
            if self.is_cancelled:
                return
            
            self.progress_updated.emit(30, "正在配置导出参数...")
            
            # 准备导出参数
            export_kwargs = self._prepare_export_kwargs()
            
            if self.is_cancelled:
                return
            
            self.progress_updated.emit(50, f"正在导出为{self.config.export_format.upper()}格式...")
            
            # 执行导出
            self.log_message.emit(f"开始导出为{self.config.export_format.upper()}格式...")
            
            if self.config.export_format == "onnx":
                result = model.export(format="onnx", **export_kwargs)
            elif self.config.export_format == "tensorrt":
                result = model.export(format="engine", **export_kwargs)
            elif self.config.export_format == "coreml":
                result = model.export(format="coreml", **export_kwargs)
            elif self.config.export_format == "tflite":
                result = model.export(format="tflite", **export_kwargs)
            else:
                raise Exception(f"不支持的导出格式: {self.config.export_format}")
            
            if self.is_cancelled:
                return
            
            self.progress_updated.emit(90, "正在完成导出...")
            
            # 移动文件到指定目录（如果需要）
            if self.config.output_dir and self.config.output_name:
                self._move_exported_file(result)
            
            self.progress_updated.emit(100, "导出完成")
            self.log_message.emit(f"模型导出成功: {result}")

            # 准备成功消息，包含文件路径信息
            final_path = result
            if self.config.output_dir and self.config.output_name:
                # 如果移动了文件，使用移动后的路径
                file_ext = Path(result).suffix
                final_path = os.path.join(self.config.output_dir, f"{self.config.output_name}{file_ext}")

            success_msg = f"模型导出成功!\n\n导出文件: {final_path}"
            self.export_completed.emit(True, success_msg)
            
        except Exception as e:
            error_msg = f"模型导出失败: {str(e)}"
            self.log_message.emit(error_msg)
            self.export_completed.emit(False, error_msg)
    
    def _prepare_export_kwargs(self) -> Dict:
        """准备导出参数"""
        kwargs = {
            "imgsz": self.config.image_size,
            "device": self.config.device,
        }
        
        if self.config.export_format == "onnx":
            kwargs.update({
                "opset": self.config.onnx_opset,
                "dynamic": self.config.onnx_dynamic,
                "simplify": self.config.onnx_simplify,
            })
        elif self.config.export_format == "tensorrt":
            kwargs.update({
                "half": self.config.tensorrt_precision == "fp16",
                "workspace": self.config.tensorrt_workspace,
            })
        
        return kwargs
    
    def _move_exported_file(self, exported_path: str):
        """移动导出的文件到指定目录"""
        try:
            if not os.path.exists(exported_path):
                return
            
            # 创建目标目录
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            # 构建目标文件路径
            file_ext = Path(exported_path).suffix
            target_path = os.path.join(self.config.output_dir, f"{self.config.output_name}{file_ext}")
            
            # 移动文件
            import shutil
            shutil.move(exported_path, target_path)
            self.log_message.emit(f"文件已移动到: {target_path}")
            
        except Exception as e:
            self.log_message.emit(f"移动文件失败: {str(e)}")


class ModelExportDialog(QDialog):
    """模型导出对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.string_bundle = StringBundle.get_bundle()
        self.get_str = lambda str_id: self.string_bundle.get_string(str_id)

        # 加载设置
        self.settings = Settings()
        self.settings.load()

        # 导出线程
        self.export_thread = None

        # 初始化模型管理器
        self.model_manager = ModelManager()
        self.model_manager.models_updated.connect(self.update_model_list)

        # 初始化界面
        self.init_ui()
        self.setup_style()
        self.load_settings()

        # 添加文件名智能功能
        self.add_filename_smart_features()

        # 延迟初始化模型列表，确保界面组件完全创建后再执行
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.delayed_model_initialization)

    def delayed_model_initialization(self):
        """延迟执行的模型初始化，确保界面组件已完全创建"""
        try:
            # 扫描可用模型
            self.refresh_models()
        except Exception as e:
            logger.error(f"延迟模型初始化失败: {str(e)}")

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(self.get_str('exportModelDialog'))
        self.setModal(True)
        self.resize(600, 500)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel(self.get_str('exportModelTitle'))
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)
        
        # 模型选择区域
        model_group = self.create_model_selection_group()
        main_layout.addWidget(model_group)
        
        # 导出格式选择区域
        format_group = self.create_format_selection_group()
        main_layout.addWidget(format_group)
        
        # 参数配置区域
        params_group = self.create_parameters_group()
        main_layout.addWidget(params_group)
        
        # 输出设置区域
        output_group = self.create_output_group()
        main_layout.addWidget(output_group)
        
        # 进度区域（初始隐藏）
        progress_group = self.create_progress_group()
        main_layout.addWidget(progress_group)
        
        # 按钮区域
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)
        
        # 初始隐藏进度区域
        self.progress_group.setVisible(False)

    def create_model_selection_group(self):
        """创建模型选择区域"""
        group = QGroupBox(self.get_str('selectModel'))
        layout = QVBoxLayout(group)

        # 模型下拉框选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel(self.get_str('modelPath')))

        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(32)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo, 1)

        # 刷新按钮
        self.refresh_model_btn = QPushButton("🔄")
        self.refresh_model_btn.setToolTip(self.get_str('refreshModels'))
        self.refresh_model_btn.setMaximumWidth(40)
        self.refresh_model_btn.clicked.connect(self.refresh_models)
        model_layout.addWidget(self.refresh_model_btn)

        # 浏览按钮（备用）
        self.browse_model_btn = QPushButton(self.get_str('browse'))
        self.browse_model_btn.setMaximumWidth(80)
        self.browse_model_btn.clicked.connect(self.browse_model_file)
        model_layout.addWidget(self.browse_model_btn)

        layout.addLayout(model_layout)

        # 模型信息显示区域
        self.create_model_info_display(layout)

        return group

    def create_model_info_display(self, parent_layout):
        """创建高级模型详情面板（参考训练参数界面）"""
        # 主面板
        self.model_details_group = QGroupBox("📊 模型详情")
        details_layout = QVBoxLayout(self.model_details_group)
        details_layout.setSpacing(12)

        # 模型名称和推荐标记
        self.model_name_label = QLabel("请选择模型查看详情")
        self.model_name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 6px;
                border-left: 4px solid #3498db;
            }
        """)
        details_layout.addWidget(self.model_name_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("QFrame { color: #bdc3c7; }")
        details_layout.addWidget(line)

        # 主要信息区域
        main_info_layout = QHBoxLayout()
        main_info_layout.setSpacing(20)

        # 左侧：性能指标
        self.create_performance_section(main_info_layout)

        # 右侧：基本信息和训练配置
        self.create_info_section(main_info_layout)

        details_layout.addLayout(main_info_layout)

        # 推荐理由
        self.recommendation_label = QLabel("")
        self.recommendation_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 12px;
                border-radius: 6px;
                border-left: 4px solid #28a745;
                color: #155724;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        self.recommendation_label.setWordWrap(True)
        details_layout.addWidget(self.recommendation_label)

        # 模型对比按钮
        compare_layout = QHBoxLayout()
        compare_layout.addStretch()

        self.compare_button = QPushButton("📊 模型对比")
        self.compare_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.compare_button.clicked.connect(self.show_model_comparison)
        self.compare_button.setVisible(False)  # 初始隐藏

        compare_layout.addWidget(self.compare_button)
        compare_layout.addStretch()
        details_layout.addLayout(compare_layout)

        # 初始状态下隐藏详情
        self.hide_model_details()

        parent_layout.addWidget(self.model_details_group)

    def create_performance_section(self, parent_layout):
        """创建性能指标区域"""
        perf_layout = QVBoxLayout()
        perf_title = QLabel("📈 性能指标")
        perf_title.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 13px;")
        perf_layout.addWidget(perf_title)

        # mAP50 进度条
        self.map50_layout = QHBoxLayout()
        self.map50_label = QLabel("mAP50:")
        self.map50_label.setFixedWidth(60)
        self.map50_bar = QProgressBar()
        self.map50_bar.setMaximum(100)
        self.map50_bar.setTextVisible(False)
        self.map50_bar.setFixedHeight(20)
        self.map50_value = QLabel("--")
        self.map50_value.setFixedWidth(50)
        self.map50_value.setStyleSheet("font-weight: bold; color: #27ae60;")

        self.map50_layout.addWidget(self.map50_label)
        self.map50_layout.addWidget(self.map50_bar)
        self.map50_layout.addWidget(self.map50_value)
        perf_layout.addLayout(self.map50_layout)

        # 精确度进度条
        self.precision_layout = QHBoxLayout()
        self.precision_label = QLabel("精确度:")
        self.precision_label.setFixedWidth(60)
        self.precision_bar = QProgressBar()
        self.precision_bar.setMaximum(100)
        self.precision_bar.setTextVisible(False)
        self.precision_bar.setFixedHeight(20)
        self.precision_value = QLabel("--")
        self.precision_value.setFixedWidth(50)
        self.precision_value.setStyleSheet("font-weight: bold; color: #3498db;")

        self.precision_layout.addWidget(self.precision_label)
        self.precision_layout.addWidget(self.precision_bar)
        self.precision_layout.addWidget(self.precision_value)
        perf_layout.addLayout(self.precision_layout)

        # 召回率进度条
        self.recall_layout = QHBoxLayout()
        self.recall_label = QLabel("召回率:")
        self.recall_label.setFixedWidth(60)
        self.recall_bar = QProgressBar()
        self.recall_bar.setMaximum(100)
        self.recall_bar.setTextVisible(False)
        self.recall_bar.setFixedHeight(20)
        self.recall_value = QLabel("--")
        self.recall_value.setFixedWidth(50)
        self.recall_value.setStyleSheet("font-weight: bold; color: #e74c3c;")

        self.recall_layout.addWidget(self.recall_label)
        self.recall_layout.addWidget(self.recall_bar)
        self.recall_layout.addWidget(self.recall_value)
        perf_layout.addLayout(self.recall_layout)

        parent_layout.addLayout(perf_layout)

    def create_info_section(self, parent_layout):
        """创建基本信息和训练配置区域"""
        info_layout = QVBoxLayout()

        # 基本信息
        info_title = QLabel("📋 基本信息")
        info_title.setStyleSheet("font-weight: bold; color: #3498db; font-size: 13px;")
        info_layout.addWidget(info_title)

        self.model_size_label = QLabel("大小: --")
        self.model_type_label = QLabel("类型: --")
        self.model_path_label = QLabel("路径: --")
        self.model_path_label.setWordWrap(True)

        for label in [self.model_size_label, self.model_type_label, self.model_path_label]:
            label.setStyleSheet("color: #2c3e50; font-size: 12px; margin: 2px 0px;")

        info_layout.addWidget(self.model_size_label)
        info_layout.addWidget(self.model_type_label)
        info_layout.addWidget(self.model_path_label)

        # 训练配置
        config_title = QLabel("⚙️ 训练配置")
        config_title.setStyleSheet("font-weight: bold; color: #e67e22; font-size: 13px; margin-top: 8px;")
        info_layout.addWidget(config_title)

        self.config_epochs_label = QLabel("轮数: --")
        self.config_batch_label = QLabel("批次: --")
        self.config_dataset_label = QLabel("数据集: --")

        for label in [self.config_epochs_label, self.config_batch_label, self.config_dataset_label]:
            label.setStyleSheet("color: #2c3e50; font-size: 12px; margin: 2px 0px;")

        info_layout.addWidget(self.config_epochs_label)
        info_layout.addWidget(self.config_batch_label)
        info_layout.addWidget(self.config_dataset_label)

        parent_layout.addLayout(info_layout)

    def show_model_details(self):
        """显示模型详情"""
        try:
            # 显示所有进度条和标签
            widgets_to_show = [
                self.map50_bar, self.map50_value, self.map50_label,
                self.precision_bar, self.precision_value, self.precision_label,
                self.recall_bar, self.recall_value, self.recall_label,
                self.model_size_label, self.model_type_label, self.model_path_label,
                self.config_epochs_label, self.config_batch_label, self.config_dataset_label,
                self.recommendation_label, self.compare_button
            ]

            for widget in widgets_to_show:
                widget.setVisible(True)

        except Exception as e:
            logger.debug(f"显示模型详情失败: {str(e)}")

    def hide_model_details(self):
        """隐藏模型详情"""
        try:
            # 隐藏所有进度条和标签
            widgets_to_hide = [
                self.map50_bar, self.map50_value, self.map50_label,
                self.precision_bar, self.precision_value, self.precision_label,
                self.recall_bar, self.recall_value, self.recall_label,
                self.model_size_label, self.model_type_label, self.model_path_label,
                self.config_epochs_label, self.config_batch_label, self.config_dataset_label,
                self.recommendation_label, self.compare_button
            ]

            for widget in widgets_to_hide:
                widget.setVisible(False)

        except Exception as e:
            logger.debug(f"隐藏模型详情失败: {str(e)}")

    def update_performance_bars(self, performance: dict):
        """更新性能指标进度条"""
        try:
            # mAP50
            mAP50 = performance.get('mAP50', 0)
            if mAP50 > 0:
                self.map50_bar.setValue(int(mAP50 * 100))
                self.map50_value.setText(f"{mAP50:.1%}")
                # 根据性能设置颜色
                if mAP50 >= 0.8:
                    color = "#27ae60"  # 绿色 - 优秀
                elif mAP50 >= 0.6:
                    color = "#f39c12"  # 橙色 - 良好
                else:
                    color = "#e74c3c"  # 红色 - 一般
                self.map50_bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid #bdc3c7;
                        border-radius: 10px;
                        background-color: #ecf0f1;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 9px;
                    }}
                """)
            else:
                self.map50_bar.setValue(0)
                self.map50_value.setText("--")

            # 精确度
            precision = performance.get('precision', 0)
            if precision > 0:
                self.precision_bar.setValue(int(precision * 100))
                self.precision_value.setText(f"{precision:.1%}")
                # 蓝色主题
                self.precision_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #bdc3c7;
                        border-radius: 10px;
                        background-color: #ecf0f1;
                    }
                    QProgressBar::chunk {
                        background-color: #3498db;
                        border-radius: 9px;
                    }
                """)
            else:
                self.precision_bar.setValue(0)
                self.precision_value.setText("--")

            # 召回率
            recall = performance.get('recall', 0)
            if recall > 0:
                self.recall_bar.setValue(int(recall * 100))
                self.recall_value.setText(f"{recall:.1%}")
                # 红色主题
                self.recall_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #bdc3c7;
                        border-radius: 10px;
                        background-color: #ecf0f1;
                    }
                    QProgressBar::chunk {
                        background-color: #e74c3c;
                        border-radius: 9px;
                    }
                """)
            else:
                self.recall_bar.setValue(0)
                self.recall_value.setText("--")

        except Exception as e:
            logger.error(f"更新性能指标失败: {str(e)}")

    def _get_performance_rating(self, mAP50: float) -> tuple:
        """获取性能评级（星级和文字描述）"""
        if mAP50 >= 0.9:
            return "⭐⭐⭐⭐⭐", "卓越"
        elif mAP50 >= 0.8:
            return "⭐⭐⭐⭐", "优秀"
        elif mAP50 >= 0.7:
            return "⭐⭐⭐", "良好"
        elif mAP50 >= 0.6:
            return "⭐⭐", "一般"
        elif mAP50 > 0:
            return "⭐", "较差"
        else:
            return "", "未知"

    def create_format_selection_group(self):
        """创建导出格式选择区域"""
        group = QGroupBox(self.get_str('exportFormat'))
        layout = QVBoxLayout(group)

        # 格式选择
        format_layout = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "ONNX (.onnx)",
            "TensorRT (.engine)",
            "CoreML (.mlmodel)",
            "TensorFlow Lite (.tflite)"
        ])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)

        format_layout.addWidget(QLabel(self.get_str('format')))
        format_layout.addWidget(self.format_combo, 1)
        layout.addLayout(format_layout)

        # 格式说明
        self.format_desc_label = QLabel(self.get_str('onnxDescription'))
        self.format_desc_label.setObjectName("descLabel")
        self.format_desc_label.setWordWrap(True)
        layout.addWidget(self.format_desc_label)

        return group

    def create_parameters_group(self):
        """创建参数配置区域"""
        group = QGroupBox(self.get_str('exportParameters'))
        layout = QVBoxLayout(group)

        # 创建堆叠窗口用于不同格式的参数
        self.params_stack = QStackedWidget()

        # ONNX参数页面
        onnx_widget = self.create_onnx_params_widget()
        self.params_stack.addWidget(onnx_widget)

        # TensorRT参数页面
        tensorrt_widget = self.create_tensorrt_params_widget()
        self.params_stack.addWidget(tensorrt_widget)

        # CoreML参数页面
        coreml_widget = self.create_coreml_params_widget()
        self.params_stack.addWidget(coreml_widget)

        # TensorFlow Lite参数页面
        tflite_widget = self.create_tflite_params_widget()
        self.params_stack.addWidget(tflite_widget)

        layout.addWidget(self.params_stack)

        # 通用参数
        common_layout = QHBoxLayout()

        # 图像尺寸
        common_layout.addWidget(QLabel(self.get_str('imageSize')))
        self.image_size_spin = QSpinBox()
        self.image_size_spin.setRange(320, 1280)
        self.image_size_spin.setValue(640)
        self.image_size_spin.setSingleStep(32)
        common_layout.addWidget(self.image_size_spin)

        # 设备选择
        common_layout.addWidget(QLabel(self.get_str('device')))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda:0"])
        common_layout.addWidget(self.device_combo)

        common_layout.addStretch()
        layout.addLayout(common_layout)

        return group

    def create_onnx_params_widget(self):
        """创建ONNX参数配置窗口"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Opset版本
        self.onnx_opset_spin = QSpinBox()
        self.onnx_opset_spin.setRange(9, 17)
        self.onnx_opset_spin.setValue(12)
        layout.addRow(self.get_str('onnxOpset'), self.onnx_opset_spin)

        # 动态batch
        self.onnx_dynamic_check = QCheckBox(self.get_str('onnxDynamic'))
        layout.addRow("", self.onnx_dynamic_check)

        # 简化模型
        self.onnx_simplify_check = QCheckBox(self.get_str('onnxSimplify'))
        self.onnx_simplify_check.setChecked(True)
        layout.addRow("", self.onnx_simplify_check)

        return widget

    def create_tensorrt_params_widget(self):
        """创建TensorRT参数配置窗口"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # 精度模式
        self.tensorrt_precision_combo = QComboBox()
        self.tensorrt_precision_combo.addItems(["fp16", "fp32"])
        layout.addRow(self.get_str('tensorrtPrecision'), self.tensorrt_precision_combo)

        # 工作空间大小
        self.tensorrt_workspace_spin = QSpinBox()
        self.tensorrt_workspace_spin.setRange(1, 16)
        self.tensorrt_workspace_spin.setValue(4)
        self.tensorrt_workspace_spin.setSuffix(" GB")
        layout.addRow(self.get_str('tensorrtWorkspace'), self.tensorrt_workspace_spin)

        return widget

    def create_coreml_params_widget(self):
        """创建CoreML参数配置窗口"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # CoreML特定参数可以在这里添加
        info_label = QLabel(self.get_str('coremlInfo'))
        info_label.setWordWrap(True)
        layout.addRow(info_label)

        return widget

    def create_tflite_params_widget(self):
        """创建TensorFlow Lite参数配置窗口"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # TensorFlow Lite特定参数可以在这里添加
        info_label = QLabel(self.get_str('tfliteInfo'))
        info_label.setWordWrap(True)
        layout.addRow(info_label)

        return widget

    def create_output_group(self):
        """创建输出设置区域"""
        group = QGroupBox(self.get_str('outputSettings'))
        layout = QVBoxLayout(group)

        # 输出目录
        dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText(self.get_str('selectOutputDir'))
        self.browse_output_btn = QPushButton(self.get_str('browse'))
        self.browse_output_btn.clicked.connect(self.browse_output_dir)

        dir_layout.addWidget(QLabel(self.get_str('outputDir')))
        dir_layout.addWidget(self.output_dir_edit, 1)
        dir_layout.addWidget(self.browse_output_btn)
        layout.addLayout(dir_layout)

        # 文件名模板选择
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("文件名模板:"))
        self.filename_template_combo = QComboBox()
        self.filename_template_combo.addItems([
            "智能模式 (推荐)",
            "简洁模式",
            "详细模式",
            "时间戳模式",
            "自定义模式"
        ])
        self.filename_template_combo.setCurrentIndex(0)  # 默认智能模式
        self.filename_template_combo.currentTextChanged.connect(self.on_filename_template_changed)
        template_layout.addWidget(self.filename_template_combo)

        # 添加模板说明
        self.template_desc_label = QLabel("自动生成包含模型信息、性能等级的智能文件名")
        self.template_desc_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        template_layout.addWidget(self.template_desc_label)
        template_layout.addStretch()
        layout.addLayout(template_layout)

        # 输出文件名
        name_layout = QHBoxLayout()
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("将根据选择的模板自动生成文件名")
        self.output_name_edit.textChanged.connect(self.on_filename_text_changed)

        # 添加文件名输入框样式
        self.output_name_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-family: monospace;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
        """)

        # 添加重置按钮
        self.reset_filename_btn = QPushButton("🔄")
        self.reset_filename_btn.setToolTip("重置为自动生成的文件名")
        self.reset_filename_btn.setMaximumWidth(30)
        self.reset_filename_btn.clicked.connect(self.reset_filename)

        # 添加预览标签
        self.filename_preview_label = QLabel("")
        self.filename_preview_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px;
                color: #495057;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        self.filename_preview_label.setVisible(False)

        name_layout.addWidget(QLabel("文件名:"))
        name_layout.addWidget(self.output_name_edit, 1)
        name_layout.addWidget(self.reset_filename_btn)
        layout.addLayout(name_layout)

        # 文件名预览
        layout.addWidget(self.filename_preview_label)

        return group

    def create_progress_group(self):
        """创建进度显示区域"""
        self.progress_group = QGroupBox(self.get_str('exportProgress'))
        layout = QVBoxLayout(self.progress_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel(self.get_str('ready'))
        layout.addWidget(self.status_label)

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        return self.progress_group

    def create_button_layout(self):
        """创建按钮布局"""
        layout = QHBoxLayout()
        layout.addStretch()

        # 导出按钮
        self.export_btn = QPushButton(self.get_str('startExport'))
        self.export_btn.setObjectName("primaryButton")
        self.export_btn.clicked.connect(self.start_export)
        layout.addWidget(self.export_btn)

        # 取消按钮
        self.cancel_btn = QPushButton(self.get_str('cancel'))
        self.cancel_btn.clicked.connect(self.cancel_export)
        layout.addWidget(self.cancel_btn)

        # 关闭按钮
        self.close_btn = QPushButton(self.get_str('close'))
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        return layout

    def setup_style(self):
        """设置样式（优化字体对比度）"""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
                color: #212121;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }

            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
                color: #212121;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #1976d2;
                background-color: white;
                font-weight: 600;
            }

            #titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1976d2;
                margin-bottom: 10px;
            }

            #infoLabel, #descLabel {
                color: #424242;
                font-style: italic;
                margin: 5px 0;
                background-color: transparent;
            }

            #primaryButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 20px;
            }

            #primaryButton:hover {
                background-color: #1565c0;
            }

            #primaryButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }

            QPushButton {
                padding: 6px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #212121;
                font-weight: 500;
                min-height: 16px;
            }

            QPushButton:hover {
                background-color: #e3f2fd;
                border-color: #1976d2;
                color: #1976d2;
            }

            QPushButton:pressed {
                background-color: #bbdefb;
            }

            QLineEdit, QComboBox, QSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #212121;
                font-size: 13px;
            }

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #1976d2;
                outline: none;
            }

            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox::down-arrow {
                image: none;
                border: 1px solid #666;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
            }

            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                color: #212121;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }

            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
                color: #212121;
                font-weight: 500;
            }

            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 3px;
            }

            QLabel {
                color: #212121;
            }

            QCheckBox {
                color: #212121;
                font-size: 13px;
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #9e9e9e;
                border-radius: 3px;
                background-color: white;
            }

            QCheckBox::indicator:hover {
                border-color: #1976d2;
            }

            QCheckBox::indicator:checked {
                background-color: #1976d2;
                border-color: #1976d2;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)

    def load_settings(self):
        """加载设置"""
        # 设置默认导出目录
        default_export_dir = self.get_default_export_dir()
        last_output_dir = self.settings.get(SETTING_MODEL_EXPORT_DIR, default_export_dir)

        # 确保目录存在
        if not os.path.exists(last_output_dir):
            try:
                os.makedirs(last_output_dir, exist_ok=True)
            except:
                last_output_dir = default_export_dir
                try:
                    os.makedirs(last_output_dir, exist_ok=True)
                except:
                    last_output_dir = os.path.expanduser("~")

        self.output_dir_edit.setText(last_output_dir)

        # 检测可用设备
        self.detect_available_devices()

    def get_default_export_dir(self):
        """获取默认导出目录"""
        # 优先使用项目根目录下的exports文件夹
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exports_dir = os.path.join(project_root, "exports", "models")

        # 如果项目目录不可写，使用用户文档目录
        try:
            os.makedirs(exports_dir, exist_ok=True)
            # 测试写入权限
            test_file = os.path.join(exports_dir, ".test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return exports_dir
        except:
            # 使用用户文档目录
            documents_dir = os.path.join(os.path.expanduser("~"), "Documents", "labelImg_exports", "models")
            try:
                os.makedirs(documents_dir, exist_ok=True)
                return documents_dir
            except:
                return os.path.expanduser("~")

    def detect_available_devices(self):
        """检测可用设备"""
        devices = ["cpu"]

        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    devices.append(f"cuda:{i}")
        except ImportError:
            pass

        self.device_combo.clear()
        self.device_combo.addItems(devices)

    def refresh_models(self):
        """刷新模型列表"""
        try:
            if hasattr(self, 'model_manager'):
                models = self.model_manager.scan_models()
                if not models:
                    self.model_info_label.setText(self.get_str('noModelsFound'))
        except Exception as e:
            print(f"刷新模型失败: {e}")

    def _normalize_model_entries(self, models):
        """将模型条目统一转换为(路径, 信息字典)格式。"""
        normalized = []
        try:
            for entry in models or []:
                if isinstance(entry, dict):
                    path = entry.get('path') or entry.get('model_path') or entry.get('file_path') or entry.get('file')
                    if not path:
                        logger.warning(f"模型条目缺少路径字段: {entry}")
                        continue
                    normalized.append((path, entry))
                elif isinstance(entry, str):
                    normalized.append((entry, {'path': entry}))
                else:
                    logger.warning(f"未知的模型条目类型: {type(entry)}")
            return normalized
        except Exception as e:
            logger.error(f"规范化模型条目失败: {str(e)}")
            return []

    def update_model_list(self, models):
        """更新模型选择列表和推荐逻辑"""
        try:
            self.model_combo.clear()

            normalized_models = self._normalize_model_entries(models)

            if not normalized_models:
                self.model_combo.addItem(self.get_str('noModelsAvailable'))
                self.model_combo.setEnabled(False)
                return

            self.model_combo.setEnabled(True)

            official_models = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt',
                              'yolo11n.pt', 'yolo11s.pt', 'yolo11m.pt', 'yolo11l.pt', 'yolo11x.pt']
            training_models = []
            custom_models = []

            recommended_model = self._find_recommended_model([path for path, _ in normalized_models])

            for model_path, _ in normalized_models:
                model_name = os.path.basename(model_path)
                normalized_path = model_path.replace('\\', '/')
                if model_name in official_models:
                    display_name = f"[官方] {model_name}"
                    self.model_combo.addItem(display_name, model_path)
                elif 'runs/train' in normalized_path:
                    training_models.append(model_path)
                else:
                    custom_models.append(model_path)

            training_models.sort(key=lambda x: x != recommended_model)

            for model_path in training_models:
                display_name = self._format_training_model_name(model_path)
                if model_path == recommended_model:
                    display_name += " [推荐]"
                self.model_combo.addItem(display_name, model_path)

            for model_path in custom_models:
                model_name = f"[自定义] {os.path.basename(model_path)}"
                self.model_combo.addItem(model_name, model_path)

            self._select_recommended_model(recommended_model)

        except Exception as e:
            logger.error(f"更新模型列表失败: {str(e)}")

    def _find_recommended_model(self, models):
        """寻找推荐的训练模型"""
        try:
            training_models = []
            for entry in models or []:
                if isinstance(entry, dict):
                    path = entry.get('path') or entry.get('model_path') or entry.get('file_path') or entry.get('file')
                else:
                    path = entry
                if not path or not isinstance(path, str):
                    continue
                normalized_path = path.replace('\\', '/')
                if 'runs/train' in normalized_path and 'best.pt' in normalized_path:
                    training_models.append(path)

            if not training_models:
                return None

            training_models.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
            return training_models[0] if training_models else None

        except Exception as e:
            logger.error(f"查找推荐模型失败: {str(e)}")
            return None

    def _select_recommended_model(self, recommended_model):
        """选择推荐的模型"""
        try:
            if recommended_model:
                # 查找推荐模型在下拉框中的位置
                for i in range(self.model_combo.count()):
                    if self.model_combo.itemData(i) == recommended_model:
                        self.model_combo.setCurrentIndex(i)
                        # 手动触发模型信息更新（因为程序化设置不会触发信号）
                        self.update_model_info(recommended_model)
                        return

            # 如果没有推荐模型，使用默认选择逻辑
            self._select_default_model()

        except Exception as e:
            print(f"选择推荐模型失败: {e}")

    def _format_training_model_name(self, model_path):
        """格式化训练模型名称"""
        try:
            path_parts = model_path.replace('\\', '/').split('/')
            if 'runs' in path_parts and 'train' in path_parts:
                train_idx = path_parts.index('train')
                if train_idx + 1 < len(path_parts):
                    experiment_name = path_parts[train_idx + 1]
                    return f"🎯 {experiment_name}/best.pt"
            return f"🎯 {os.path.basename(model_path)}"
        except:
            return f"🎯 {os.path.basename(model_path)}"

    def _select_default_model(self):
        """智能选择默认模型"""
        try:
            # 优先选择推荐的模型
            default_models = ["yolov8s.pt", "yolov8n.pt", "best.pt"]

            for default_model in default_models:
                for i in range(self.model_combo.count()):
                    if default_model in self.model_combo.itemText(i):
                        self.model_combo.setCurrentIndex(i)
                        # 手动触发模型信息更新
                        model_path = self.model_combo.itemData(i)
                        if model_path:
                            self.update_model_info(model_path)
                        return

            # 如果没有找到默认模型，选择第一个
            if self.model_combo.count() > 0:
                self.model_combo.setCurrentIndex(0)
                # 手动触发模型信息更新
                model_path = self.model_combo.itemData(0)
                if model_path:
                    self.update_model_info(model_path)

        except Exception as e:
            print(f"选择默认模型失败: {e}")

    def on_model_changed(self, model_text):
        """模型选择改变事件（带动画效果）"""
        try:
            current_index = self.model_combo.currentIndex()
            if current_index >= 0:
                model_path = self.model_combo.itemData(current_index)
                if model_path:
                    # 先隐藏详情，然后更新，最后显示（创建平滑过渡效果）
                    self.hide_model_details()

                    # 使用QTimer延迟更新，创建动画效果
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(100, lambda: self.update_model_info(model_path))
                else:
                    # 如果没有数据，可能是"无可用模型"等提示文本
                    self.model_name_label.setText("请选择模型查看详情")
                    self.hide_model_details()
        except Exception as e:
            logger.error(f"模型选择改变处理失败: {str(e)}")

    def get_selected_model_path(self):
        """获取当前选择的模型路径"""
        try:
            current_index = self.model_combo.currentIndex()
            if current_index >= 0:
                return self.model_combo.itemData(current_index)
            return None
        except:
            return None

    def browse_model_file(self):
        """浏览模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.get_str('selectModelFile'),
            "",
            "YOLO Models (*.pt *.onnx *.engine);;All Files (*)"
        )

        if file_path:
            # 添加到下拉框（如果不存在）
            display_name = f"📁 {os.path.basename(file_path)}"

            # 检查是否已存在
            found = False
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == file_path:
                    self.model_combo.setCurrentIndex(i)
                    found = True
                    break

            if not found:
                self.model_combo.addItem(display_name, file_path)
                self.model_combo.setCurrentIndex(self.model_combo.count() - 1)

            self.update_model_info(file_path)

    def browse_output_dir(self):
        """浏览输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            self.get_str('selectOutputDir'),
            self.output_dir_edit.text() or os.path.expanduser("~")
        )

        if directory:
            self.output_dir_edit.setText(directory)
            # 保存到设置
            self.settings[SETTING_MODEL_EXPORT_DIR] = directory
            self.settings.save()
            # 检查文件名冲突
            self.update_conflict_warning()

    def update_model_info(self, model_path):
        """更新模型信息显示（使用新的详情面板）"""
        try:
            # 检查界面组件是否已经初始化完成
            if not self._is_ui_initialized():
                logger.debug("界面组件尚未完全初始化，跳过模型信息更新")
                return

            if not model_path or not os.path.exists(model_path):
                self.model_name_label.setText("❌ 模型文件未找到")
                self.hide_model_details()
                return

            # 使用ModelManager获取详细模型信息
            model_info = self._get_model_detailed_info(model_path)

            if not model_info or 'error' in model_info:
                error_msg = model_info.get('error', '获取模型信息失败') if model_info else '获取模型信息失败'
                self.model_name_label.setText(f"❌ {error_msg}")
                self.hide_model_details()
                return

            # 更新详细信息显示
            self.update_model_details_display(model_info)

            # 智能生成输出文件名
            self.update_filename_by_template()

        except Exception as e:
            logger.error(f"更新模型信息失败: {str(e)}")
            self.model_name_label.setText(f"❌ 更新模型信息失败: {str(e)}")
            self.hide_model_details()

    def _is_ui_initialized(self):
        """检查界面组件是否已经完全初始化"""
        try:
            # 检查关键组件是否存在且可用
            required_components = [
                'model_name_label', 'map50_bar', 'precision_bar', 'recall_bar',
                'model_size_label', 'model_type_label', 'model_path_label',
                'config_epochs_label', 'config_batch_label', 'config_dataset_label',
                'recommendation_label', 'compare_button'
            ]

            for component_name in required_components:
                if not hasattr(self, component_name):
                    logger.debug(f"组件 {component_name} 尚未创建")
                    return False

                component = getattr(self, component_name)
                if component is None:
                    logger.debug(f"组件 {component_name} 为 None")
                    return False

            return True

        except Exception as e:
            logger.debug(f"检查界面初始化状态失败: {str(e)}")
            return False

    def update_model_details_display(self, model_info: dict):
        """更新模型详情显示（参考训练参数界面）"""
        try:
            if not model_info:
                self.hide_model_details()
                return

            # 显示详情面板
            self.show_model_details()

            # 更新模型名称和推荐标记
            training_dir = model_info.get('training_dir', 'unknown')
            model_type = model_info.get('model_type', 'unknown.pt')

            # 获取性能评级
            performance = model_info.get('performance', {})
            mAP50 = performance.get('mAP50', 0)
            stars, rating = self._get_performance_rating(mAP50)

            # 构建模型名称显示
            if 'best' in model_type.lower():
                icon = "🏆"
            elif 'last' in model_type.lower():
                icon = "📝"
            else:
                icon = "🎯"

            model_name = f"{icon} {training_dir}/{model_type}"
            if stars:
                model_name += f" {stars} ({rating})"

            # 检查是否是推荐模型
            current_text = self.model_combo.currentText()
            if "🌟推荐" in current_text:
                model_name += " 🌟推荐"

            self.model_name_label.setText(model_name)

            # 更新性能指标进度条
            self.update_performance_bars(performance)

            # 更新基本信息
            self.model_size_label.setText(
                f"大小: {model_info.get('size_mb', 0)} MB")
            self.model_type_label.setText(f"类型: {model_type}")

            # 简化路径显示
            full_path = model_info.get('path', '')
            if len(full_path) > 50:
                display_path = "..." + full_path[-47:]
            else:
                display_path = full_path
            self.model_path_label.setText(f"路径: {display_path}")

            # 更新训练配置
            config = model_info.get('config', {})
            self.config_epochs_label.setText(
                f"轮数: {config.get('epochs', '?')} epochs")
            self.config_batch_label.setText(f"批次: {config.get('batch', '?')}")
            self.config_dataset_label.setText(
                f"数据集: {config.get('dataset', '未知')}")

            # 更新推荐理由
            self.update_recommendation_display(model_info)

        except Exception as e:
            logger.error(f"更新模型详情显示失败: {str(e)}")
            self.hide_model_details()

    def update_recommendation_display(self, model_info: dict):
        """更新推荐理由显示"""
        try:
            # 检查是否是推荐模型
            current_text = self.model_combo.currentText()
            if "🌟推荐" not in current_text:
                self.recommendation_label.setText("")
                self.recommendation_label.setVisible(False)
                return

            # 构建推荐理由
            reasons = []

            # 性能分析
            performance = model_info.get('performance', {})
            mAP50 = performance.get('mAP50', 0)
            if mAP50 > 0:
                stars, rating = self._get_performance_rating(mAP50)
                reasons.append(f"🎯 性能{rating}：mAP50达到{mAP50:.1%}")

            # 模型类型分析
            model_type = model_info.get('model_type', '')
            if 'best' in model_type.lower():
                reasons.append("🏆 最佳模型：训练过程中性能最优的检查点")

            # 训练配置分析
            config = model_info.get('config', {})
            epochs = config.get('epochs', 0)
            if epochs >= 100:
                reasons.append(f"⚙️ 充分训练：完成{epochs}轮训练，模型收敛良好")

            # 文件大小分析
            size_mb = model_info.get('size_mb', 0)
            if size_mb > 0:
                if size_mb < 50:
                    reasons.append(f"💾 轻量化：模型大小仅{size_mb}MB，部署友好")
                elif size_mb > 200:
                    reasons.append(f"🔋 高精度：{size_mb}MB大模型，精度更高")

            # 如果没有具体理由，给出通用推荐
            if not reasons:
                reasons.append("✨ 综合评估：基于性能、训练质量等因素的智能推荐")

            # 构建最终显示文本
            recommendation_text = "🌟 推荐理由：\n" + "\n".join(f"  • {reason}" for reason in reasons)
            self.recommendation_label.setText(recommendation_text)
            self.recommendation_label.setVisible(True)

        except Exception as e:
            logger.error(f"更新推荐理由失败: {str(e)}")
            self.recommendation_label.setText("")
            self.recommendation_label.setVisible(False)

    def _get_model_detailed_info(self, model_path: str) -> dict:
        """获取模型详细信息"""
        try:
            info = {
                'path': model_path,
                'name': os.path.basename(model_path),
                'size_mb': 0,
                'modified_time': '',
                'training_dir': '',
                'model_type': os.path.basename(model_path),
                'config': {},
                'performance': {}
            }

            # 获取文件大小
            if os.path.exists(model_path):
                info['size_mb'] = round(os.path.getsize(model_path) / (1024 * 1024), 2)

            # 获取修改时间
            import time
            try:
                mtime = os.path.getmtime(model_path)
                info['modified_time'] = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(mtime))
            except Exception:
                info['modified_time'] = "未知时间"

            # 获取训练目录名称
            path_parts = model_path.replace('\\', '/').split('/')
            for i, part in enumerate(path_parts):
                if part == 'train' and i + 1 < len(path_parts):
                    info['training_dir'] = path_parts[i + 1]
                    break

            # 获取训练配置
            training_dir = os.path.dirname(os.path.dirname(model_path))
            args_file = os.path.join(training_dir, "args.yaml")
            if os.path.exists(args_file):
                import yaml
                try:
                    with open(args_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        info['config'] = {
                            'epochs': config.get('epochs', '?'),
                            'batch': config.get('batch', '?'),
                            'dataset': os.path.basename(config.get('data', '未知数据集'))
                        }
                except Exception as e:
                    logger.debug(f"读取训练配置失败: {str(e)}")

            # 获取性能指标
            info['performance'] = self._get_training_performance(model_path)

            return info

        except Exception as e:
            logger.error(f"获取模型详细信息失败: {str(e)}")
            return {}

    def _get_training_performance(self, model_path: str) -> dict:
        """获取训练性能指标"""
        try:
            # 获取训练目录
            training_dir = os.path.dirname(os.path.dirname(model_path))
            results_file = os.path.join(training_dir, "results.csv")

            if not os.path.exists(results_file):
                return {}

            import csv

            # 读取CSV文件
            with open(results_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                return {}

            # 获取最后一行的性能数据
            last_row = rows[-1]

            performance = {
                'mAP50': round(float(last_row.get('metrics/mAP50(B)', 0)), 3),
                'mAP50_95': round(float(last_row.get('metrics/mAP50-95(B)', 0)), 3),
                'precision': round(float(last_row.get('metrics/precision(B)', 0)), 3),
                'recall': round(float(last_row.get('metrics/recall(B)', 0)), 3),
                'final_epoch': int(float(last_row.get('epoch', 0)))
            }

            return performance

        except Exception as e:
            logger.debug(f"获取训练性能指标失败: {str(e)}")
            return {}

    def show_model_comparison(self):
        """显示模型对比对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
            from PyQt5.QtCore import Qt

            dialog = QDialog(self)
            dialog.setWindowTitle("模型性能对比")
            dialog.setMinimumSize(800, 600)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("📊 训练模型性能对比")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 10px;")
            layout.addWidget(title_label)

            # 获取所有训练模型
            training_models = []
            for i in range(self.model_combo.count()):
                model_path = self.model_combo.itemData(i)
                if model_path and 'runs/train' in model_path.replace('\\', '/'):
                    model_info = self._get_model_detailed_info(model_path)
                    if model_info:
                        training_models.append(model_info)

            if not training_models:
                no_models_label = QLabel("❌ 没有找到可对比的训练模型")
                no_models_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin: 20px;")
                layout.addWidget(no_models_label)
            else:
                # 创建对比表格
                table = QTableWidget()
                table.setRowCount(len(training_models))
                table.setColumnCount(8)
                table.setHorizontalHeaderLabels([
                    "模型名称", "mAP50", "精确度", "召回率", "大小(MB)", "训练轮数", "评级", "推荐"
                ])

                # 填充数据
                for row, model_info in enumerate(training_models):
                    # 模型名称
                    name = f"{model_info.get('training_dir', 'unknown')}/{model_info.get('model_type', 'unknown')}"
                    table.setItem(row, 0, QTableWidgetItem(name))

                    # 性能指标
                    performance = model_info.get('performance', {})
                    mAP50 = performance.get('mAP50', 0)
                    precision = performance.get('precision', 0)
                    recall = performance.get('recall', 0)

                    table.setItem(row, 1, QTableWidgetItem(f"{mAP50:.1%}" if mAP50 > 0 else "--"))
                    table.setItem(row, 2, QTableWidgetItem(f"{precision:.1%}" if precision > 0 else "--"))
                    table.setItem(row, 3, QTableWidgetItem(f"{recall:.1%}" if recall > 0 else "--"))

                    # 文件大小
                    size_mb = model_info.get('size_mb', 0)
                    table.setItem(row, 4, QTableWidgetItem(f"{size_mb}" if size_mb > 0 else "--"))

                    # 训练轮数
                    config = model_info.get('config', {})
                    epochs = config.get('epochs', '?')
                    table.setItem(row, 5, QTableWidgetItem(str(epochs)))

                    # 评级
                    stars, rating = self._get_performance_rating(mAP50)
                    table.setItem(row, 6, QTableWidgetItem(f"{stars} {rating}"))

                    # 推荐标记
                    model_path = model_info.get('path', '')
                    is_recommended = any("🌟推荐" in self.model_combo.itemText(i)
                                       for i in range(self.model_combo.count())
                                       if self.model_combo.itemData(i) == model_path)
                    table.setItem(row, 7, QTableWidgetItem("🌟" if is_recommended else ""))

                # 调整表格样式
                table.resizeColumnsToContents()
                table.setAlternatingRowColors(True)
                table.setSelectionBehavior(QTableWidget.SelectRows)

                layout.addWidget(table)

            # 关闭按钮
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            close_button = QPushButton("关闭")
            close_button.clicked.connect(dialog.accept)
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示模型对比失败: {str(e)}")

    def generate_smart_filename(self, model_info: dict, export_format: str = "onnx") -> str:
        """智能生成导出文件名"""
        try:
            # 基础信息提取
            model_path = model_info.get('path', '')
            model_type = model_info.get('model_type', 'model')
            training_dir = model_info.get('training_dir', 'unknown')
            performance = model_info.get('performance', {})

            # 1. 模型类型识别
            base_model = self._extract_base_model_name(model_path)

            # 2. 实验名称提取
            experiment_name = self._extract_experiment_name(training_dir)

            # 3. 性能等级
            mAP50 = performance.get('mAP50', 0)
            performance_level = self._get_performance_level_short(mAP50)

            # 4. 模型版本（best/last）
            model_version = self._extract_model_version(model_type)

            # 5. 时间戳
            timestamp = self._get_timestamp()

            # 6. 导出格式
            format_ext = self._get_format_extension_clean(export_format)

            # 构建文件名组件
            components = []

            # 基础模型名
            if base_model:
                components.append(base_model)

            # 实验名称
            if experiment_name and experiment_name != 'unknown':
                components.append(experiment_name)

            # 模型版本
            if model_version:
                components.append(model_version)

            # 性能等级
            if performance_level:
                components.append(performance_level)

            # 时间戳
            components.append(timestamp)

            # 导出格式
            if format_ext:
                components.append(format_ext)

            # 组合文件名
            filename = "_".join(components)

            # 清理文件名（移除非法字符）
            filename = self._sanitize_filename(filename)

            return filename

        except Exception as e:
            logger.debug(f"智能文件名生成失败: {str(e)}")
            # 回退到简单文件名
            return self._generate_fallback_filename(model_info, export_format)

    def _extract_base_model_name(self, model_path: str) -> str:
        """提取基础模型名称"""
        try:
            filename = os.path.basename(model_path).lower()

            # YOLO模型识别
            if 'yolov8n' in filename:
                return 'yolov8n'
            elif 'yolov8s' in filename:
                return 'yolov8s'
            elif 'yolov8m' in filename:
                return 'yolov8m'
            elif 'yolov8l' in filename:
                return 'yolov8l'
            elif 'yolov8x' in filename:
                return 'yolov8x'
            elif 'yolo11n' in filename or 'yolov11n' in filename:
                return 'yolo11n'
            elif 'yolo11s' in filename or 'yolov11s' in filename:
                return 'yolo11s'
            elif 'yolo11m' in filename or 'yolov11m' in filename:
                return 'yolo11m'
            elif 'yolo11l' in filename or 'yolov11l' in filename:
                return 'yolo11l'
            elif 'yolo11x' in filename or 'yolov11x' in filename:
                return 'yolo11x'
            elif 'yolov8' in filename:
                return 'yolov8'
            elif 'yolo11' in filename or 'yolov11' in filename:
                return 'yolo11'
            elif 'yolo' in filename:
                return 'yolo'
            else:
                # 使用文件名（去除扩展名）
                return os.path.splitext(os.path.basename(model_path))[0]

        except Exception:
            return 'model'

    def _extract_experiment_name(self, training_dir: str) -> str:
        """提取实验名称"""
        try:
            if training_dir and training_dir != 'unknown':
                # 清理实验名称
                clean_name = training_dir.replace(' ', '_').replace('-', '_')
                # 限制长度
                if len(clean_name) > 15:
                    clean_name = clean_name[:15]
                return clean_name
            return ''
        except Exception:
            return ''

    def _get_performance_level_short(self, mAP50: float) -> str:
        """获取性能等级简写"""
        try:
            if mAP50 >= 0.9:
                return 'excellent'
            elif mAP50 >= 0.8:
                return 'good'
            elif mAP50 >= 0.7:
                return 'fair'
            elif mAP50 >= 0.6:
                return 'poor'
            elif mAP50 > 0:
                return 'basic'
            else:
                return ''
        except Exception:
            return ''

    def _extract_model_version(self, model_type: str) -> str:
        """提取模型版本"""
        try:
            if 'best' in model_type.lower():
                return 'best'
            elif 'last' in model_type.lower():
                return 'last'
            else:
                return ''
        except Exception:
            return ''

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        try:
            from datetime import datetime
            return datetime.now().strftime("%Y%m%d_%H%M")
        except Exception:
            return 'export'

    def _get_format_extension_clean(self, export_format: str) -> str:
        """获取清理后的格式扩展名"""
        try:
            format_map = {
                'onnx': 'onnx',
                'tensorrt': 'trt',
                'coreml': 'coreml',
                'tflite': 'tflite'
            }
            return format_map.get(export_format.lower(), export_format.lower())
        except Exception:
            return 'export'

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        try:
            import re
            # 移除非法字符，只保留字母、数字、下划线、连字符
            clean_name = re.sub(r'[^\w\-_.]', '_', filename)
            # 移除多余的下划线
            clean_name = re.sub(r'_+', '_', clean_name)
            # 移除开头和结尾的下划线
            clean_name = clean_name.strip('_')
            return clean_name
        except Exception:
            return filename

    def _generate_fallback_filename(self, model_info: dict, export_format: str) -> str:
        """生成回退文件名"""
        try:
            model_name = model_info.get('name', 'model')
            base_name = os.path.splitext(model_name)[0]
            timestamp = self._get_timestamp()
            format_ext = self._get_format_extension_clean(export_format)
            return f"{base_name}_{timestamp}_{format_ext}"
        except Exception:
            return f"exported_model_{self._get_timestamp()}"

    def on_filename_template_changed(self, template_name: str):
        """文件名模板改变事件"""
        try:
            # 更新模板说明
            template_descriptions = {
                "智能模式 (推荐)": "自动生成包含模型信息、性能等级的智能文件名",
                "简洁模式": "仅包含基础模型名和时间戳",
                "详细模式": "包含完整的模型信息、训练配置和性能数据",
                "时间戳模式": "使用详细时间戳作为主要标识",
                "自定义模式": "手动输入文件名，不自动生成"
            }

            desc = template_descriptions.get(template_name, "")
            self.template_desc_label.setText(desc)

            # 如果不是自定义模式，重新生成文件名
            if template_name != "自定义模式":
                self.update_filename_by_template()
            else:
                # 自定义模式下清空文件名，让用户手动输入
                self.output_name_edit.setPlaceholderText("请手动输入文件名")
                self.filename_preview_label.setVisible(False)

        except Exception as e:
            logger.debug(f"文件名模板改变处理失败: {str(e)}")

    def update_filename_by_template(self):
        """根据当前模板更新文件名"""
        try:
            # 获取当前选择的模型信息
            model_path = self.get_selected_model_path()
            if not model_path:
                return

            model_info = self._get_model_detailed_info(model_path)
            if not model_info:
                return

            # 获取当前导出格式
            export_format = self._get_current_export_format()

            # 根据模板生成文件名
            template_name = self.filename_template_combo.currentText()
            filename = self.generate_filename_by_template(model_info, export_format, template_name)

            # 更新文件名输入框
            self.output_name_edit.setText(filename)

            # 显示预览
            self.show_filename_preview(filename, export_format)

        except Exception as e:
            logger.debug(f"根据模板更新文件名失败: {str(e)}")

    def generate_filename_by_template(self, model_info: dict, export_format: str, template_name: str) -> str:
        """根据模板生成文件名"""
        try:
            if template_name == "智能模式 (推荐)":
                return self.generate_smart_filename(model_info, export_format)

            elif template_name == "简洁模式":
                base_model = self._extract_base_model_name(model_info.get('path', ''))
                timestamp = self._get_timestamp()
                format_ext = self._get_format_extension_clean(export_format)
                return f"{base_model}_{timestamp}_{format_ext}"

            elif template_name == "详细模式":
                return self._generate_detailed_filename(model_info, export_format)

            elif template_name == "时间戳模式":
                from datetime import datetime
                detailed_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_model = self._extract_base_model_name(model_info.get('path', ''))
                format_ext = self._get_format_extension_clean(export_format)
                return f"{base_model}_{detailed_timestamp}_{format_ext}"

            else:
                # 默认使用智能模式
                return self.generate_smart_filename(model_info, export_format)

        except Exception as e:
            logger.debug(f"模板文件名生成失败: {str(e)}")
            return self._generate_fallback_filename(model_info, export_format)

    def _generate_detailed_filename(self, model_info: dict, export_format: str) -> str:
        """生成详细模式文件名"""
        try:
            components = []

            # 基础模型
            base_model = self._extract_base_model_name(model_info.get('path', ''))
            if base_model:
                components.append(base_model)

            # 实验名称
            training_dir = model_info.get('training_dir', '')
            if training_dir and training_dir != 'unknown':
                experiment = self._extract_experiment_name(training_dir)
                if experiment:
                    components.append(experiment)

            # 模型版本
            model_type = model_info.get('model_type', '')
            version = self._extract_model_version(model_type)
            if version:
                components.append(version)

            # 性能数据
            performance = model_info.get('performance', {})
            mAP50 = performance.get('mAP50', 0)
            if mAP50 > 0:
                components.append(f"mAP{int(mAP50*100)}")

            # 训练配置
            config = model_info.get('config', {})
            epochs = config.get('epochs')
            if epochs:
                components.append(f"ep{epochs}")

            batch_size = config.get('batch')
            if batch_size:
                components.append(f"bs{batch_size}")

            # 时间戳
            timestamp = self._get_timestamp()
            components.append(timestamp)

            # 格式
            format_ext = self._get_format_extension_clean(export_format)
            if format_ext:
                components.append(format_ext)

            filename = "_".join(components)
            return self._sanitize_filename(filename)

        except Exception as e:
            logger.debug(f"详细文件名生成失败: {str(e)}")
            return self._generate_fallback_filename(model_info, export_format)

    def _get_current_export_format(self) -> str:
        """获取当前选择的导出格式"""
        try:
            format_text = self.format_combo.currentText()
            if "ONNX" in format_text:
                return "onnx"
            elif "TensorRT" in format_text:
                return "tensorrt"
            elif "CoreML" in format_text:
                return "coreml"
            elif "TensorFlow Lite" in format_text:
                return "tflite"
            return "onnx"  # 默认
        except Exception:
            return "onnx"

    def show_filename_preview(self, filename: str, export_format: str):
        """显示文件名预览"""
        try:
            # 获取完整的文件扩展名
            ext = self._get_format_extension()
            if not ext:
                ext = ".onnx"  # 默认扩展名

            full_filename = f"{filename}{ext}"

            # 显示预览
            self.filename_preview_label.setText(f"预览: {full_filename}")
            self.filename_preview_label.setVisible(True)

        except Exception as e:
            logger.debug(f"显示文件名预览失败: {str(e)}")
            self.filename_preview_label.setVisible(False)

    def reset_filename(self):
        """重置文件名为自动生成"""
        try:
            # 重新根据当前模板生成文件名
            self.update_filename_by_template()
        except Exception as e:
            logger.debug(f"重置文件名失败: {str(e)}")

    def on_filename_text_changed(self, text: str):
        """文件名文本改变事件"""
        try:
            # 实时验证文件名
            if text:
                # 检查非法字符
                import re
                if re.search(r'[<>:"/\\|?*]', text):
                    self.output_name_edit.setStyleSheet("QLineEdit { border: 2px solid #e74c3c; }")
                    self.filename_preview_label.setText("⚠️ 文件名包含非法字符")
                    self.filename_preview_label.setStyleSheet("QLabel { color: #e74c3c; }")
                    self.filename_preview_label.setVisible(True)
                else:
                    self.output_name_edit.setStyleSheet("")
                    # 检查冲突并显示预览
                    self.update_conflict_warning()
            else:
                self.output_name_edit.setStyleSheet("")
                self.filename_preview_label.setVisible(False)

        except Exception as e:
            logger.debug(f"文件名文本改变处理失败: {str(e)}")

    def check_filename_conflict(self, filename: str, output_dir: str) -> tuple:
        """检查文件名冲突

        Returns:
            tuple: (has_conflict: bool, suggested_filename: str, conflict_info: str)
        """
        try:
            if not filename or not output_dir or not os.path.exists(output_dir):
                return False, filename, ""

            # 获取完整文件路径
            ext = self._get_format_extension()
            if not ext:
                ext = ".onnx"

            full_filename = f"{filename}{ext}"
            full_path = os.path.join(output_dir, full_filename)

            if not os.path.exists(full_path):
                return False, filename, ""

            # 文件存在，生成建议的新文件名
            base_name = filename
            counter = 1

            while True:
                suggested_name = f"{base_name}_{counter:02d}"
                suggested_path = os.path.join(output_dir, f"{suggested_name}{ext}")

                if not os.path.exists(suggested_path):
                    break

                counter += 1
                if counter > 99:  # 避免无限循环
                    # 使用时间戳
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%H%M%S")
                    suggested_name = f"{base_name}_{timestamp}"
                    break

            conflict_info = f"文件 '{full_filename}' 已存在"
            return True, suggested_name, conflict_info

        except Exception as e:
            logger.debug(f"文件名冲突检测失败: {str(e)}")
            return False, filename, ""

    def resolve_filename_conflict(self, filename: str, output_dir: str) -> str:
        """解决文件名冲突，返回可用的文件名"""
        try:
            has_conflict, suggested_name, conflict_info = self.check_filename_conflict(filename, output_dir)

            if not has_conflict:
                return filename

            # 显示冲突提示
            from PyQt5.QtWidgets import QMessageBox

            msg = QMessageBox(self)
            msg.setWindowTitle("文件名冲突")
            msg.setIcon(QMessageBox.Warning)
            msg.setText(conflict_info)
            msg.setInformativeText(f"建议使用新文件名: {suggested_name}")

            # 添加按钮
            use_suggested_btn = msg.addButton("使用建议名称", QMessageBox.AcceptRole)
            overwrite_btn = msg.addButton("覆盖现有文件", QMessageBox.DestructiveRole)
            cancel_btn = msg.addButton("取消", QMessageBox.RejectRole)

            msg.setDefaultButton(use_suggested_btn)
            msg.exec_()

            if msg.clickedButton() == use_suggested_btn:
                return suggested_name
            elif msg.clickedButton() == overwrite_btn:
                return filename
            else:
                return ""  # 用户取消

        except Exception as e:
            logger.debug(f"解决文件名冲突失败: {str(e)}")
            return filename

    def update_conflict_warning(self):
        """更新冲突警告显示"""
        try:
            filename = self.output_name_edit.text().strip()
            output_dir = self.output_dir_edit.text().strip()

            if not filename or not output_dir:
                return

            has_conflict, suggested_name, conflict_info = self.check_filename_conflict(filename, output_dir)

            if has_conflict:
                # 显示冲突警告
                warning_text = f"⚠️ {conflict_info}，建议: {suggested_name}"
                self.filename_preview_label.setText(warning_text)
                self.filename_preview_label.setStyleSheet("""
                    QLabel {
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 4px;
                        padding: 6px;
                        color: #856404;
                        font-family: monospace;
                        font-size: 11px;
                    }
                """)
                self.filename_preview_label.setVisible(True)
            else:
                # 显示正常预览
                export_format = self._get_current_export_format()
                self.show_filename_preview(filename, export_format)

        except Exception as e:
            logger.debug(f"更新冲突警告失败: {str(e)}")

    def add_filename_smart_features(self):
        """添加文件名智能功能"""
        try:
            # 添加工具提示
            tooltip_text = """
文件名生成规则：
• 智能模式：模型名_实验名_性能等级_时间戳_格式
• 简洁模式：模型名_时间戳_格式
• 详细模式：包含完整训练信息
• 时间戳模式：详细时间戳标识
• 自定义模式：手动输入

支持的字符：字母、数字、下划线、连字符
自动过滤非法字符：< > : " / \\ | ? *
            """.strip()

            self.output_name_edit.setToolTip(tooltip_text)

            # 添加右键菜单
            from PyQt5.QtWidgets import QMenu, QAction
            from PyQt5.QtCore import Qt

            def create_context_menu():
                menu = QMenu(self.output_name_edit)

                # 重新生成文件名
                regenerate_action = QAction("🔄 重新生成文件名", self)
                regenerate_action.triggered.connect(self.reset_filename)
                menu.addAction(regenerate_action)

                menu.addSeparator()

                # 切换到不同模板
                templates = ["智能模式 (推荐)", "简洁模式", "详细模式", "时间戳模式"]
                for template in templates:
                    action = QAction(f"📝 切换到{template}", self)
                    action.triggered.connect(lambda checked, t=template: self.switch_to_template(t))
                    menu.addAction(action)

                menu.addSeparator()

                # 清空文件名
                clear_action = QAction("🗑️ 清空文件名", self)
                clear_action.triggered.connect(self.output_name_edit.clear)
                menu.addAction(clear_action)

                return menu

            self.output_name_edit.setContextMenuPolicy(Qt.CustomContextMenu)
            self.output_name_edit.customContextMenuRequested.connect(
                lambda pos: create_context_menu().exec_(self.output_name_edit.mapToGlobal(pos))
            )

        except Exception as e:
            logger.debug(f"添加文件名智能功能失败: {str(e)}")

    def switch_to_template(self, template_name: str):
        """切换到指定模板"""
        try:
            # 找到模板索引
            for i in range(self.filename_template_combo.count()):
                if self.filename_template_combo.itemText(i) == template_name:
                    self.filename_template_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            logger.debug(f"切换模板失败: {str(e)}")

    def validate_filename_input(self, text: str) -> tuple:
        """验证文件名输入

        Returns:
            tuple: (is_valid: bool, error_message: str, cleaned_text: str)
        """
        try:
            if not text:
                return True, "", ""

            # 检查长度
            if len(text) > 200:
                return False, "文件名过长（最大200字符）", text[:200]

            # 检查非法字符
            import re
            illegal_chars = r'[<>:"/\\|?*]'
            if re.search(illegal_chars, text):
                cleaned_text = re.sub(illegal_chars, '_', text)
                return False, "包含非法字符，已自动替换为下划线", cleaned_text

            # 检查保留名称（Windows）
            reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + \
                           [f'COM{i}' for i in range(1, 10)] + \
                           [f'LPT{i}' for i in range(1, 10)]

            if text.upper() in reserved_names:
                return False, "文件名为系统保留名称", f"{text}_file"

            # 检查是否以点开头或结尾
            if text.startswith('.') or text.endswith('.'):
                cleaned_text = text.strip('.')
                if not cleaned_text:
                    cleaned_text = "file"
                return False, "文件名不能以点开头或结尾", cleaned_text

            return True, "", text

        except Exception as e:
            logger.debug(f"文件名验证失败: {str(e)}")
            return True, "", text

    def _detect_model_type(self, model_path):
        """检测模型类型"""
        file_name = os.path.basename(model_path).lower()

        if 'yolov8' in file_name:
            return "YOLOv8"
        elif 'yolo11' in file_name or 'yolov11' in file_name:
            return "YOLOv11"
        elif 'yolo' in file_name:
            return "YOLO"
        elif file_name.endswith('.pt'):
            return "PyTorch"
        elif file_name.endswith('.onnx'):
            return "ONNX"
        elif file_name.endswith('.engine'):
            return "TensorRT"
        else:
            return self.get_str('unknown')

    def _get_yolo_model_info(self, model_path):
        """获取YOLO模型详细信息"""
        try:
            if not YOLO_AVAILABLE:
                return None

            # 快速加载模型获取基本信息
            model = YOLO(model_path)
            info_lines = []

            # 获取类别数量
            if hasattr(model, 'model') and hasattr(model.model, 'names'):
                class_count = len(model.model.names)
                info_lines.append(f"🎯 {self.get_str('classCount')}: {class_count}")
            elif hasattr(model, 'names'):
                class_count = len(model.names)
                info_lines.append(f"🎯 {self.get_str('classCount')}: {class_count}")

            # 清理模型对象
            del model

            return info_lines
        except:
            return None

    def _get_format_extension(self):
        """获取当前选择格式的扩展名"""
        format_text = self.format_combo.currentText()
        if "ONNX" in format_text:
            return ".onnx"
        elif "TensorRT" in format_text:
            return ".engine"
        elif "CoreML" in format_text:
            return ".mlmodel"
        elif "TensorFlow Lite" in format_text:
            return ".tflite"
        return ""

    def on_format_changed(self, format_text):
        """格式改变事件"""
        format_map = {
            "ONNX (.onnx)": (0, self.get_str('onnxDescription')),
            "TensorRT (.engine)": (1, self.get_str('tensorrtDescription')),
            "CoreML (.mlmodel)": (2, self.get_str('coremlDescription')),
            "TensorFlow Lite (.tflite)": (3, self.get_str('tfliteDescription'))
        }

        if format_text in format_map:
            index, description = format_map[format_text]
            self.params_stack.setCurrentIndex(index)
            self.format_desc_label.setText(description)

            # 根据新格式更新文件名
            if self.filename_template_combo.currentText() != "自定义模式":
                self.update_filename_by_template()

    def validate_inputs(self):
        """验证输入"""
        # 检查模型文件
        model_path = self.get_selected_model_path()
        if not model_path:
            QMessageBox.warning(self, self.get_str('warning'), self.get_str('pleaseSelectModel'))
            return False

        if not os.path.exists(model_path):
            QMessageBox.warning(self, self.get_str('warning'), self.get_str('modelFileNotFound'))
            return False

        # 检查输出目录
        output_dir = self.output_dir_edit.text().strip()
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, self.get_str('warning'),
                                  f"{self.get_str('createDirFailed')}: {str(e)}")
                return False

        # 检查输出文件名
        output_name = self.output_name_edit.text().strip()
        if not output_name:
            QMessageBox.warning(self, self.get_str('warning'), "请输入输出文件名")
            return False

        # 检查并解决文件名冲突
        output_dir = self.output_dir_edit.text().strip()
        if output_dir:
            resolved_name = self.resolve_filename_conflict(output_name, output_dir)
            if not resolved_name:
                return False  # 用户取消
            elif resolved_name != output_name:
                # 更新文件名
                self.output_name_edit.setText(resolved_name)

        return True

    def get_export_config(self):
        """获取导出配置"""
        config = ExportConfig()

        # 基本设置
        config.model_path = self.get_selected_model_path() or ""
        config.output_dir = self.output_dir_edit.text().strip()
        config.output_name = self.output_name_edit.text().strip()

        # 格式设置
        format_text = self.format_combo.currentText()
        if "ONNX" in format_text:
            config.export_format = "onnx"
        elif "TensorRT" in format_text:
            config.export_format = "tensorrt"
        elif "CoreML" in format_text:
            config.export_format = "coreml"
        elif "TensorFlow Lite" in format_text:
            config.export_format = "tflite"

        # 通用参数
        config.image_size = self.image_size_spin.value()
        config.device = self.device_combo.currentText()

        # 格式特定参数
        if config.export_format == "onnx":
            config.onnx_opset = self.onnx_opset_spin.value()
            config.onnx_dynamic = self.onnx_dynamic_check.isChecked()
            config.onnx_simplify = self.onnx_simplify_check.isChecked()
        elif config.export_format == "tensorrt":
            config.tensorrt_precision = self.tensorrt_precision_combo.currentText()
            config.tensorrt_workspace = self.tensorrt_workspace_spin.value()

        return config

    def start_export(self):
        """开始导出"""
        if not self.validate_inputs():
            return

        # 获取导出配置
        config = self.get_export_config()

        # 禁用控件
        self.export_btn.setEnabled(False)
        self.browse_model_btn.setEnabled(False)
        self.browse_output_btn.setEnabled(False)
        self.refresh_model_btn.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.output_dir_edit.setEnabled(False)
        self.output_name_edit.setEnabled(False)
        self.format_combo.setEnabled(False)

        # 显示进度区域
        self.progress_group.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.status_label.setText(self.get_str('preparingExport'))

        # 创建并启动导出线程
        self.export_thread = ModelExportThread(config)
        self.export_thread.progress_updated.connect(self.on_progress_updated)
        self.export_thread.log_message.connect(self.on_log_message)
        self.export_thread.export_completed.connect(self.on_export_completed)
        self.export_thread.start()

    def cancel_export(self):
        """取消导出"""
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.cancel()
            self.export_thread.wait(3000)  # 等待3秒

            if self.export_thread.isRunning():
                self.export_thread.terminate()
                self.export_thread.wait()

            self.on_export_completed(False, self.get_str('exportCancelled'))
        else:
            self.close()

    def on_progress_updated(self, value, message):
        """进度更新"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def on_log_message(self, message):
        """日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_export_completed(self, success, message):
        """导出完成"""
        # 恢复控件状态
        self.export_btn.setEnabled(True)
        self.browse_model_btn.setEnabled(True)
        self.browse_output_btn.setEnabled(True)
        self.refresh_model_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.output_dir_edit.setEnabled(True)
        self.output_name_edit.setEnabled(True)
        self.format_combo.setEnabled(True)

        if success:
            self.status_label.setText(self.get_str('exportComplete'))

            # 创建成功对话框，包含打开文件夹选项
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.get_str('success'))
            msg_box.setText(self.get_str('exportSuccess'))
            msg_box.setDetailedText(message)
            msg_box.setIcon(QMessageBox.Information)

            # 添加按钮
            open_folder_btn = msg_box.addButton(self.get_str('openFolder'), QMessageBox.ActionRole)
            ok_btn = msg_box.addButton(self.get_str('ok'), QMessageBox.AcceptRole)

            msg_box.exec_()

            # 检查用户点击的按钮
            if msg_box.clickedButton() == open_folder_btn:
                self.open_export_folder()
        else:
            self.status_label.setText(self.get_str('exportFailed'))
            QMessageBox.critical(self, self.get_str('error'), message)

        # 清理线程
        if self.export_thread:
            self.export_thread.deleteLater()
            self.export_thread = None

    def open_export_folder(self):
        """打开导出文件夹"""
        try:
            export_dir = self.output_dir_edit.text().strip()
            if not export_dir or not os.path.exists(export_dir):
                QMessageBox.warning(self, self.get_str('warning'), self.get_str('folderNotFound'))
                return

            # 根据操作系统打开文件夹
            system = platform.system()
            if system == "Windows":
                os.startfile(export_dir)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", export_dir])
            else:  # Linux
                subprocess.run(["xdg-open", export_dir])

        except Exception as e:
            QMessageBox.warning(self, self.get_str('error'),
                              f"{self.get_str('openFolderFailed')}: {str(e)}")

    def closeEvent(self, event):
        """关闭事件"""
        if self.export_thread and self.export_thread.isRunning():
            reply = QMessageBox.question(
                self,
                self.get_str('confirmClose'),
                self.get_str('exportInProgress'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.export_thread.cancel()
                self.export_thread.wait(3000)
                if self.export_thread.isRunning():
                    self.export_thread.terminate()
                    self.export_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
