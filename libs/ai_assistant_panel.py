#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI助手界面面板

提供YOLO模型管理和预测功能的用户界面
"""

import os
import logging
from typing import Optional, List, Dict

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from .ai_assistant import YOLOPredictor, ModelManager, BatchProcessor, ConfidenceFilter
from .ai_assistant.yolo_trainer import YOLOTrainer, TrainingConfig

# 设置日志
logger = logging.getLogger(__name__)


class CollapsibleGroupBox(QGroupBox):
    """可折叠的GroupBox组件"""

    def __init__(self, title="", collapsed=True, parent=None):
        super().__init__(title, parent)
        self.collapsed = collapsed
        self.content_widget = None
        self.animation = None
        self.original_height = 0

        # 设置样式，使标题栏可点击
        self.setStyleSheet("""
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox:hover {
                border-color: #3498db;
            }
        """)

        # 设置鼠标指针
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # 初始化动画
        self.setup_animation()

        # 设置初始状态
        if self.collapsed:
            self.setMaximumHeight(30)  # 只显示标题栏
            self.setMinimumHeight(30)  # 固定高度

    def setup_animation(self):
        """设置动画"""
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def set_content_widget(self, widget):
        """设置内容组件"""
        self.content_widget = widget

        # 创建布局并添加内容
        layout = QVBoxLayout(self)
        layout.addWidget(widget)

        # 获取原始高度（使用估算值避免显示widget导致状态重置）
        self.original_height = 200  # 使用估算的展开高度

        # 强制应用当前的折叠状态
        if self.collapsed:
            self._apply_collapsed_state()
        else:
            self._apply_expanded_state()

    def _apply_collapsed_state(self):
        """应用折叠状态"""
        print(f"[DEBUG] _apply_collapsed_state: 开始应用")
        if self.content_widget:
            self.content_widget.hide()
            print(f"[DEBUG] _apply_collapsed_state: 隐藏内容")
        self.setMaximumHeight(30)
        self.setMinimumHeight(30)
        print(f"[DEBUG] _apply_collapsed_state: 设置高度限制30px")

    def _apply_expanded_state(self):
        """应用展开状态"""
        if self.content_widget:
            self.content_widget.show()
        self.setMaximumHeight(self.original_height)
        self.setMinimumHeight(0)  # 恢复最小高度限制

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            # 检查点击位置是否在标题区域
            title_rect = QRect(0, 0, self.width(), 30)
            if title_rect.contains(event.pos()):
                self.toggle_collapsed()
        super().mousePressEvent(event)

    def toggle_collapsed(self):
        """切换折叠状态"""
        self.collapsed = not self.collapsed

        if self.collapsed:
            self.collapse()
        else:
            self.expand()

        # 保存用户偏好
        self.save_collapsed_state()

    def collapse(self):
        """折叠"""
        # 更新标题以显示摘要信息
        self.update_title_for_collapsed_state()

        # 动画到折叠高度
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(30)
        self.animation.finished.connect(self._on_collapse_finished)
        self.animation.start()

    def expand(self):
        """展开"""
        # 恢复原始标题
        self.update_title_for_expanded_state()

        # 动画到展开高度
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(self.original_height)
        self.animation.finished.connect(self._on_expand_finished)
        self.animation.start()

    def _on_collapse_finished(self):
        """折叠动画完成"""
        if self.content_widget:
            self.content_widget.hide()
        self.setMinimumHeight(30)
        self.animation.finished.disconnect()

    def _on_expand_finished(self):
        """展开动画完成"""
        if self.content_widget:
            self.content_widget.show()
        self.setMinimumHeight(0)
        self.animation.finished.disconnect()

    def update_title_for_collapsed_state(self):
        """更新折叠状态的标题"""
        # 子类可以重写此方法来自定义折叠状态的标题
        pass

    def update_title_for_expanded_state(self):
        """更新展开状态的标题"""
        # 子类可以重写此方法来自定义展开状态的标题
        pass

    def save_collapsed_state(self):
        """保存折叠状态到设置"""
        try:
            from libs.settings import Settings
            settings = Settings()
            settings.load()
            settings[f'ai_assistant/classes_info_collapsed'] = self.collapsed
            settings.save()
        except Exception as e:
            logger.error(f"保存折叠状态失败: {str(e)}")


class CollapsibleClassesInfoGroup(CollapsibleGroupBox):
    """可折叠的类别信息组"""

    def __init__(self, parent=None):
        # 加载保存的折叠状态
        saved_collapsed = self.load_collapsed_state()

        # 调用父类初始化，使用加载的状态
        super().__init__("📋 类别信息", collapsed=saved_collapsed, parent=parent)

        self.parent_panel = parent
        self.model_classes_count = None
        self.user_classes_count = None

    def update_title_for_collapsed_state(self):
        """更新折叠状态的标题，显示摘要信息"""
        model_count = "未加载"
        user_count = "未加载"

        if self.model_classes_count:
            model_text = self.model_classes_count.text()
            # 提取数字部分，如果是"X 个"格式
            if " 个" in model_text:
                model_count = model_text.replace(" 个", "")
            else:
                model_count = model_text

        if self.user_classes_count:
            user_text = self.user_classes_count.text()
            # 提取数字部分，如果是"X 个"格式
            if " 个" in user_text:
                user_count = user_text.replace(" 个", "")
            else:
                user_count = user_text

        # 创建更简洁的摘要标题
        summary_title = f"▶ 📋 类别信息 (模型:{model_count} 用户:{user_count})"
        self.setTitle(summary_title)

    def update_title_for_expanded_state(self):
        """更新展开状态的标题"""
        self.setTitle("▼ 📋 类别信息")

    def load_collapsed_state(self):
        """从设置加载折叠状态"""
        try:
            from libs.settings import Settings
            settings = Settings()
            settings.load()

            # 检查是否有保存的状态
            saved_state = settings.get(
                'ai_assistant/classes_info_collapsed', None)
            print(f"[DEBUG] load_collapsed_state: saved_state={saved_state}")

            # 如果没有保存的状态，使用默认折叠状态
            # 这确保了新用户的默认体验是折叠的（节省空间）
            if saved_state is None:
                # 第一次使用，保存默认折叠状态
                settings['ai_assistant/classes_info_collapsed'] = True
                settings.save()
                print(f"[DEBUG] load_collapsed_state: 保存并返回默认True")
                return True
            else:
                # 强制返回True来确保默认折叠
                print(
                    f"[DEBUG] load_collapsed_state: 强制返回True（忽略保存的{saved_state}）")
                return True

        except Exception as e:
            logger.error(f"加载折叠状态失败: {str(e)}")
            return True  # 默认折叠


class InstallThread(QThread):
    """PyTorch安装线程"""
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    installation_finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, install_cmd, log_text, progress_bar):
        super().__init__()
        self.install_cmd = install_cmd
        self.log_text = log_text
        self.progress_bar = progress_bar

    def run(self):
        """执行安装"""
        try:
            import subprocess

            # 启动安装进程
            process = subprocess.Popen(
                self.install_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 模拟进度更新
            progress = 0

            # 读取输出
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    self.log_updated.emit(f"📦 {line}")

                    # 简单的进度估算
                    if progress < 90:
                        progress += 2
                        self.progress_updated.emit(progress)

            # 等待进程完成
            return_code = process.poll()

            # 完成进度
            self.progress_updated.emit(100)

            if return_code == 0:
                self.installation_finished.emit(True, "安装成功")
            else:
                error_msg = "\n".join(output_lines[-10:])  # 最后10行错误信息
                self.installation_finished.emit(False, error_msg)

        except Exception as e:
            self.installation_finished.emit(False, str(e))


class CollapsibleAIPanel(QWidget):
    """可折叠的AI助手面板"""

    # 信号定义
    prediction_requested = pyqtSignal(str, float)      # 预测请求 (图像路径, 置信度)
    batch_prediction_requested = pyqtSignal(str, float)  # 批量预测请求 (目录路径, 置信度)
    predictions_applied = pyqtSignal(list)             # 应用预测结果 (检测列表)
    predictions_cleared = pyqtSignal()                 # 清除预测结果
    model_changed = pyqtSignal(str)                    # 模型切换 (模型路径)

    def __init__(self, parent=None):
        """
        初始化可折叠AI助手面板

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        # 面板状态
        self.is_collapsed = False
        self.expanded_width = 320
        self.collapsed_width = 40

        # 初始化AI助手面板
        self.ai_panel = AIAssistantPanel(self)

        # 创建宽度动画
        self.width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation.setDuration(300)  # 300ms动画时长
        self.width_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 连接动画值变化信号，同时更新minimumWidth
        self.width_animation.valueChanged.connect(self._on_width_changed)

        # 设置界面
        self.setup_ui()
        self.setup_connections()
        self.setup_style()

        # 连接AI助手面板的信号
        self.connect_ai_panel_signals()

    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建折叠按钮区域
        self.collapse_button = QPushButton("🤖")
        self.collapse_button.setFixedSize(40, 40)
        self.collapse_button.setToolTip("点击展开/折叠AI助手")
        self.collapse_button.clicked.connect(self.toggle_collapse)

        # 创建内容区域
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.addWidget(self.ai_panel)

        # 添加到主布局
        main_layout.addWidget(self.collapse_button)
        main_layout.addWidget(self.content_widget)

        # 设置初始大小
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(400)
        self.setMaximumWidth(self.expanded_width)

    def setup_connections(self):
        """设置信号连接"""
        pass

    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            CollapsibleAIPanel {
                background-color: #fafafa;
                border-left: 3px solid #2196F3;
                border-radius: 0px;
            }

            CollapsibleAIPanel QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }

            CollapsibleAIPanel QPushButton:hover {
                background-color: #1976D2;
                border: 2px solid #1565C0;
            }

            CollapsibleAIPanel QPushButton:pressed {
                background-color: #0D47A1;
                border: 2px solid #0277BD;
            }

            /* 为内容区域添加阴影效果 */
            QWidget#content_widget {
                background-color: white;
                border-radius: 8px;
                margin: 2px;
            }
        """)

    def connect_ai_panel_signals(self):
        """连接AI助手面板的信号"""
        self.ai_panel.prediction_requested.connect(self.prediction_requested)
        self.ai_panel.batch_prediction_requested.connect(
            self.batch_prediction_requested)
        self.ai_panel.predictions_applied.connect(self.predictions_applied)
        self.ai_panel.predictions_cleared.connect(self.predictions_cleared)
        self.ai_panel.model_changed.connect(self.model_changed)

    def toggle_collapse(self):
        """切换折叠状态"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()

    def collapse(self):
        """折叠面板"""
        if not self.is_collapsed:
            self.is_collapsed = True

            # 立即隐藏内容，避免动画过程中的视觉问题
            self.content_widget.hide()

            # 设置宽度动画 - 从展开宽度缩小到按钮宽度
            self.width_animation.setStartValue(self.expanded_width)
            self.width_animation.setEndValue(self.collapsed_width)

            # 立即更新按钮
            self.collapse_button.setText("▶")
            self.collapse_button.setToolTip("点击展开AI助手")

            # 开始动画
            self.width_animation.start()

    def expand(self):
        """展开面板"""
        if self.is_collapsed:
            self.is_collapsed = False

            # 设置宽度动画 - 从按钮宽度扩展到完整宽度
            self.width_animation.setStartValue(self.collapsed_width)
            self.width_animation.setEndValue(self.expanded_width)

            # 动画完成后显示内容
            self.width_animation.finished.connect(self._on_expand_finished)

            # 立即更新按钮
            self.collapse_button.setText("◀")
            self.collapse_button.setToolTip("点击折叠AI助手")

            # 开始动画
            self.width_animation.start()

    def _on_width_changed(self, value):
        """宽度动画值变化回调"""
        # 同时更新minimumWidth，确保面板真正改变大小
        self.setMinimumWidth(value)
        self.setFixedWidth(value)

    def _on_expand_finished(self):
        """展开动画完成回调"""
        if not self.is_collapsed:
            self.content_widget.show()
        # 断开信号连接，避免重复调用
        try:
            self.width_animation.finished.disconnect(self._on_expand_finished)
        except:
            pass

    def get_ai_panel(self):
        """获取AI助手面板实例"""
        return self.ai_panel


class AIAssistantPanel(QWidget):
    """AI助手界面面板"""

    # 信号定义
    prediction_requested = pyqtSignal(str, float)      # 预测请求 (图像路径, 置信度)
    batch_prediction_requested = pyqtSignal(str, float)  # 批量预测请求 (目录路径, 置信度)
    predictions_applied = pyqtSignal(list)             # 应用预测结果 (检测列表)
    predictions_cleared = pyqtSignal()                 # 清除预测结果
    model_changed = pyqtSignal(str)                    # 模型切换 (模型路径)

    def __init__(self, parent=None):
        """
        初始化AI助手面板

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        # 初始化组件
        self.predictor = None
        self.model_manager = None
        self.batch_processor = None
        self.confidence_filter = None
        self.trainer = None

        # 界面状态
        self.current_predictions = []
        self.is_predicting = False
        self.is_smart_predicting = False  # 智能预测状态标记

        # 设置界面
        self.setup_ui()
        self.setup_connections()
        self.setup_style()

        # 加载智能预测设置
        self.load_and_apply_smart_predict_setting()

        # 初始化AI组件
        self.initialize_ai_components()

        # 初始化类别数据
        self.model_classes_data = {}
        self.user_classes_data = []

        # 初始化类别信息显示
        self.refresh_classes_info()

        # 初始化训练数据
        self.training_data_stats = {
            'total_images': 0,
            'total_annotations': 0,
            'classes_count': 0,
            'min_samples_per_class': 10  # 最少样本数要求
        }

        # 初始化硬件信息
        self.hardware_info = {
            'gpu_available': False,
            'gpu_name': 'Unknown',
            'cuda_version': 'Unknown',
            'pytorch_version': 'Unknown',
            'recommended_device': 'cpu'
        }

        # 初始化类别信息
        self.refresh_classes_info()

        # 初始化硬件信息
        self.detect_hardware_info()

        # 初始化训练信息
        self.refresh_training_info()

    def setup_ui(self):
        """设置用户界面"""
        # 主布局 - 优化间距以适应可折叠组件
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)  # 减少间距，为内容腾出更多空间

        # 标题
        title_label = QLabel("🤖 AI 助手")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # 模型选择区域
        model_group = self.create_model_selection_group()
        main_layout.addWidget(model_group)

        # 类别信息区域 (新增)
        self.classes_group = self.create_classes_info_group()
        main_layout.addWidget(self.classes_group)

        # 训练信息区域 (新增)
        training_group = self.create_training_info_group()
        main_layout.addWidget(training_group)

        # 预测参数区域
        params_group = self.create_prediction_params_group()
        main_layout.addWidget(params_group)

        # 预测控制区域
        control_group = self.create_prediction_control_group()
        main_layout.addWidget(control_group)

        # 结果显示区域
        results_group = self.create_results_display_group()
        main_layout.addWidget(results_group)

        # 状态显示区域
        status_group = self.create_status_group()
        main_layout.addWidget(status_group)

        # 添加弹性空间
        main_layout.addStretch()

    def create_model_selection_group(self) -> QGroupBox:
        """创建模型选择组"""
        group = QGroupBox("📦 模型选择")
        layout = QVBoxLayout(group)

        # 模型下拉框
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(32)
        layout.addWidget(self.model_combo)

        # 模型信息显示
        self.model_info_label = QLabel("未选择模型")
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setObjectName("modelInfoLabel")
        layout.addWidget(self.model_info_label)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新模型")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.clicked.connect(self.refresh_models)
        layout.addWidget(refresh_btn)

        return group

    def create_classes_info_group(self) -> CollapsibleClassesInfoGroup:
        """创建可折叠的类别信息组"""
        # 创建可折叠组件
        group = CollapsibleClassesInfoGroup(self)

        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(6)  # 减少间距

        # 第一行：类别统计信息 + 操作按钮
        top_layout = QHBoxLayout()

        # 左侧：类别统计
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(2)

        # 模型类别统计
        model_layout = QHBoxLayout()
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_label = QLabel("模型:")
        model_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        model_label.setFixedWidth(35)
        self.model_classes_count = QLabel("未加载")
        self.model_classes_count.setStyleSheet(
            "color: #7f8c8d; font-size: 11px;")
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_classes_count)
        model_layout.addStretch()

        # 用户类别统计
        user_layout = QHBoxLayout()
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_label = QLabel("用户:")
        user_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        user_label.setFixedWidth(35)
        self.user_classes_count = QLabel("未加载")
        self.user_classes_count.setStyleSheet(
            "color: #7f8c8d; font-size: 11px;")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_classes_count)
        user_layout.addStretch()

        stats_layout.addLayout(model_layout)
        stats_layout.addLayout(user_layout)

        # 右侧：操作按钮
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(2)

        # 查看按钮
        view_btn = QPushButton("👁️ 查看")
        view_btn.setMaximumHeight(20)
        view_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        view_btn.clicked.connect(self.show_classes_detail_dialog)

        # 配置按钮
        config_btn = QPushButton("⚙️ 配置")
        config_btn.setMaximumHeight(20)
        config_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        config_btn.setToolTip("管理固定类别配置")
        config_btn.clicked.connect(self.show_class_config_dialog)

        # 验证按钮
        validate_btn = QPushButton("✅ 验证")
        validate_btn.setMaximumHeight(20)
        validate_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        validate_btn.setToolTip("验证类别顺序一致性")
        validate_btn.clicked.connect(self.validate_class_consistency)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setMaximumHeight(20)
        refresh_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_classes_info)

        buttons_layout.addWidget(view_btn)
        buttons_layout.addWidget(config_btn)
        buttons_layout.addWidget(validate_btn)
        buttons_layout.addWidget(refresh_btn)

        top_layout.addLayout(stats_layout)
        top_layout.addStretch()
        top_layout.addLayout(buttons_layout)

        layout.addLayout(top_layout)

        # 设置内容到可折叠组件
        group.set_content_widget(content_widget)

        # 保存引用以便更新标题
        group.model_classes_count = self.model_classes_count
        group.user_classes_count = self.user_classes_count

        # 确保正确应用折叠状态和标题
        print(
            f"[DEBUG] create_classes_info_group 最终: collapsed={group.collapsed}")
        print(f"[DEBUG] create_classes_info_group 最终: height={group.height()}")
        print(
            f"[DEBUG] create_classes_info_group 最终: maxHeight={group.maximumHeight()}")
        print(
            f"[DEBUG] create_classes_info_group 最终: minHeight={group.minimumHeight()}")

        if group.collapsed:
            group.update_title_for_collapsed_state()
        else:
            group.update_title_for_expanded_state()

        return group

    def create_training_info_group(self) -> QGroupBox:
        """创建训练信息组 - 紧凑设计"""
        group = QGroupBox("🎓 模型训练")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        # 训练状态和统计信息
        status_layout = QHBoxLayout()

        # 左侧：数据统计
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(2)

        # 标注数据统计
        data_layout = QHBoxLayout()
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_label = QLabel("数据:")
        data_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        data_label.setFixedWidth(35)
        self.training_data_count = QLabel("0 张")
        self.training_data_count.setStyleSheet(
            "color: #7f8c8d; font-size: 11px;")
        data_layout.addWidget(data_label)
        data_layout.addWidget(self.training_data_count)
        data_layout.addStretch()

        # 训练状态
        status_layout_inner = QHBoxLayout()
        status_layout_inner.setContentsMargins(0, 0, 0, 0)
        status_label = QLabel("状态:")
        status_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        status_label.setFixedWidth(35)
        self.training_status = QLabel("未开始")
        self.training_status.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        status_layout_inner.addWidget(status_label)
        status_layout_inner.addWidget(self.training_status)
        status_layout_inner.addStretch()

        # 硬件信息
        device_layout = QHBoxLayout()
        device_layout.setContentsMargins(0, 0, 0, 0)
        device_label = QLabel("设备:")
        device_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        device_label.setFixedWidth(35)
        self.device_status = QLabel("检测中...")
        self.device_status.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_status)
        device_layout.addStretch()

        stats_layout.addLayout(data_layout)
        stats_layout.addLayout(status_layout_inner)
        stats_layout.addLayout(device_layout)

        # 右侧：训练按钮
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(2)

        # 训练按钮
        self.train_btn = QPushButton("🚀 开始训练")
        self.train_btn.setMaximumHeight(20)
        self.train_btn.setEnabled(False)  # 默认禁用
        self.train_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover:enabled {
                background-color: #d5dbdb;
            }
            QPushButton:disabled {
                color: #95a5a6;
                background-color: #ecf0f1;
            }
        """)
        self.train_btn.clicked.connect(self.show_complete_training_dialog)

        # 配置按钮
        config_btn = QPushButton("⚙️ 配置")
        config_btn.setMaximumHeight(20)
        config_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        config_btn.clicked.connect(self.show_training_config_dialog)

        # 环境检查按钮
        self.env_check_btn = QPushButton("🔍 环境")
        self.env_check_btn.setMaximumHeight(20)
        self.env_check_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #3498db;
                border-radius: 3px;
                background-color: #ebf3fd;
                color: #3498db;
            }
            QPushButton:hover {
                background-color: #d6eafd;
            }
        """)
        self.env_check_btn.clicked.connect(self.show_environment_check_dialog)

        # PyTorch安装按钮（根据需要显示）
        self.pytorch_install_btn = QPushButton("📦 安装")
        self.pytorch_install_btn.setMaximumHeight(20)
        self.pytorch_install_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                padding: 2px 6px;
                border: 1px solid #e74c3c;
                border-radius: 3px;
                background-color: #fdf2f2;
                color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #fce4e4;
            }
        """)
        self.pytorch_install_btn.clicked.connect(
            self.show_pytorch_install_dialog)
        self.pytorch_install_btn.setVisible(False)  # 默认隐藏

        buttons_layout.addWidget(self.train_btn)
        buttons_layout.addWidget(config_btn)
        buttons_layout.addWidget(self.env_check_btn)
        buttons_layout.addWidget(self.pytorch_install_btn)

        status_layout.addLayout(stats_layout)
        status_layout.addStretch()
        status_layout.addLayout(buttons_layout)

        layout.addLayout(status_layout)

        return group

    def create_prediction_params_group(self) -> QGroupBox:
        """创建预测参数组 - 优化布局"""
        group = QGroupBox("⚙️ 预测参数")
        layout = QFormLayout(group)
        layout.setSpacing(4)  # 减少行间距
        layout.setContentsMargins(8, 8, 8, 8)  # 优化边距

        # 置信度阈值
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 95)  # 0.1 到 0.95
        self.confidence_slider.setValue(25)      # 默认 0.25
        self.confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(10)

        self.confidence_label = QLabel("0.25")
        self.confidence_label.setMinimumWidth(40)

        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)

        layout.addRow("置信度阈值:", confidence_layout)

        # NMS阈值
        self.nms_slider = QSlider(Qt.Horizontal)
        self.nms_slider.setRange(30, 80)  # 0.3 到 0.8
        self.nms_slider.setValue(45)     # 默认 0.45
        self.nms_slider.setTickPosition(QSlider.TicksBelow)
        self.nms_slider.setTickInterval(10)

        self.nms_label = QLabel("0.45")
        self.nms_label.setMinimumWidth(40)

        nms_layout = QHBoxLayout()
        nms_layout.addWidget(self.nms_slider)
        nms_layout.addWidget(self.nms_label)

        layout.addRow("NMS阈值:", nms_layout)

        # 最大检测数
        self.max_det_spin = QSpinBox()
        self.max_det_spin.setRange(1, 1000)
        self.max_det_spin.setValue(100)
        layout.addRow("最大检测数:", self.max_det_spin)

        return group

    def create_prediction_control_group(self) -> QGroupBox:
        """创建预测控制组 - 优化布局"""
        group = QGroupBox("🎯 预测控制")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)  # 减少间距
        layout.setContentsMargins(8, 8, 8, 8)  # 优化边距

        # 智能预测复选框
        self.smart_predict_checkbox = QCheckBox("🤖 智能预测未标注图片")
        self.smart_predict_checkbox.setObjectName("smartPredictCheckbox")
        self.smart_predict_checkbox.setToolTip(
            "开启后，切换到未标注图片时将自动执行预测\n"
            "大幅提升标注效率，无需手动点击预测按钮"
        )
        # 默认开启智能预测功能
        self.smart_predict_checkbox.setChecked(True)
        layout.addWidget(self.smart_predict_checkbox)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # 单图预测按钮
        self.predict_current_btn = QPushButton("🖼️ 预测当前图像")
        self.predict_current_btn.setObjectName("predictCurrentButton")
        self.predict_current_btn.setMinimumHeight(32)  # 减少高度
        layout.addWidget(self.predict_current_btn)

        # 批量预测按钮
        self.predict_batch_btn = QPushButton("📁 批量预测")
        self.predict_batch_btn.setObjectName("predictBatchButton")
        self.predict_batch_btn.setMinimumHeight(32)  # 减少高度
        layout.addWidget(self.predict_batch_btn)

        # 取消按钮
        self.cancel_btn = QPushButton("❌ 取消预测")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)

        return group

    def create_results_display_group(self) -> QGroupBox:
        """创建结果显示组"""
        group = QGroupBox("📊 预测结果")
        layout = QVBoxLayout(group)

        # 结果统计
        self.results_stats_label = QLabel("暂无预测结果")
        self.results_stats_label.setObjectName("resultsStatsLabel")
        layout.addWidget(self.results_stats_label)

        # 结果列表
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(120)
        layout.addWidget(self.results_list)

        # 结果操作按钮   
        results_btn_layout = QHBoxLayout()

        self.apply_btn = QPushButton("✅ 应用")
        self.apply_btn.setObjectName("applyButton")
        self.apply_btn.setEnabled(False)
        results_btn_layout.addWidget(self.apply_btn)

        self.clear_btn = QPushButton("🗑️ 清除")
        self.clear_btn.setObjectName("clearButton")
        self.clear_btn.setEnabled(False)
        results_btn_layout.addWidget(self.clear_btn)

        layout.addLayout(results_btn_layout)

        return group

    def create_status_group(self) -> QGroupBox:
        """创建状态显示组"""
        group = QGroupBox("📈 状态信息")
        layout = QVBoxLayout(group)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 性能信息
        self.performance_label = QLabel("")
        self.performance_label.setObjectName("performanceLabel")
        layout.addWidget(self.performance_label)

        return group

    def setup_connections(self):
        """设置信号连接"""
        # 参数控制连接
        self.confidence_slider.valueChanged.connect(
            self.update_confidence_label)
        self.nms_slider.valueChanged.connect(self.update_nms_label)

        # 模型选择连接
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # 预测控制连接
        self.predict_current_btn.clicked.connect(self.on_predict_current)
        self.predict_batch_btn.clicked.connect(self.on_predict_batch)
        self.cancel_btn.clicked.connect(self.on_cancel_prediction)
        self.smart_predict_checkbox.stateChanged.connect(
            self.on_smart_predict_changed)

        # 结果操作连接
        self.apply_btn.clicked.connect(self.on_apply_results)
        self.clear_btn.clicked.connect(self.on_clear_results)
        self.results_list.itemDoubleClicked.connect(
            self.on_result_item_double_clicked)

    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            /* 主面板样式 */
            AIAssistantPanel {
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            
            /* 标题样式 */
            QLabel#titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1976d2;
                padding: 8px;
                background-color: #e3f2fd;
                border-radius: 6px;
                border: 1px solid #bbdefb;
            }
            
            /* 分组框样式 */
            QGroupBox {
                font-weight: 600;
                color: #424242;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
            
            /* 按钮样式 */
            QPushButton#predictCurrentButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 8px;
            }
            
            QPushButton#predictCurrentButton:hover {
                background-color: #45a049;
            }
            
            QPushButton#predictCurrentButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QPushButton#predictBatchButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 8px;
            }
            
            QPushButton#predictBatchButton:hover {
                background-color: #1976d2;
            }
            
            QPushButton#cancelButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 8px;
            }
            
            QPushButton#cancelButton:hover {
                background-color: #d32f2f;
            }
            
            QPushButton#applyButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 6px 12px;
            }
            
            QPushButton#applyButton:hover {
                background-color: #f57c00;
            }
            
            QPushButton#clearButton {
                background-color: #9e9e9e;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 6px 12px;
            }
            
            QPushButton#clearButton:hover {
                background-color: #757575;
            }
            
            QPushButton#refreshButton {
                background-color: #607d8b;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                padding: 6px 12px;
            }
            
            QPushButton#refreshButton:hover {
                background-color: #546e7a;
            }

            /* 智能预测复选框样式 */
            QCheckBox#smartPredictCheckbox {
                font-weight: 600;
                color: #424242;
                spacing: 8px;
                padding: 8px;
                background-color: #f0f8ff;
                border: 1px solid #2196F3;
                border-radius: 6px;
            }

            QCheckBox#smartPredictCheckbox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #2196F3;
                background-color: white;
            }

            QCheckBox#smartPredictCheckbox::indicator:checked {
                background-color: #2196F3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }

            QCheckBox#smartPredictCheckbox::indicator:hover {
                border-color: #1976d2;
                background-color: #e3f2fd;
            }

            QCheckBox#smartPredictCheckbox::indicator:checked:hover {
                background-color: #1976d2;
            }

            /* 信息标签样式 */
            QLabel#modelInfoLabel {
                background-color: #fff3e0;
                border: 1px solid #ffcc02;
                border-radius: 4px;
                padding: 6px;
                color: #e65100;
                font-size: 11px;
            }
            
            QLabel#resultsStatsLabel {
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 6px;
                color: #2e7d32;
                font-weight: 600;
            }
            
            QLabel#statusLabel {
                background-color: #f3e5f5;
                border: 1px solid #9c27b0;
                border-radius: 4px;
                padding: 6px;
                color: #7b1fa2;
                font-weight: 600;
            }
            
            QLabel#performanceLabel {
                color: #666666;
                font-size: 11px;
                font-style: italic;
            }
            
            /* 滑块样式 */
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #1976d2;
                border: 1px solid #1976d2;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #1565c0;
            }
            
            /* 列表样式 */
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
            
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            
            /* 进度条样式 */
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: #f5f5f5;
            }
            
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 3px;
            }
        """)

    def initialize_ai_components(self):
        """初始化AI组件"""
        try:
            # 创建AI组件
            self.model_manager = ModelManager()
            self.predictor = YOLOPredictor()
            self.batch_processor = BatchProcessor(self.predictor)
            self.confidence_filter = ConfidenceFilter()
            self.trainer = YOLOTrainer()

            # 连接AI组件信号
            self.model_manager.models_updated.connect(self.update_model_list)
            self.model_manager.model_validated.connect(self.on_model_validated)
            self.model_manager.error_occurred.connect(self.on_ai_error)

            self.predictor.model_loaded.connect(self.on_model_loaded)
            self.predictor.prediction_completed.connect(
                self.on_prediction_completed)
            self.predictor.error_occurred.connect(self.on_ai_error)

            self.batch_processor.batch_started.connect(self.on_batch_started)
            self.batch_processor.progress_updated.connect(
                self.on_batch_progress)
            self.batch_processor.batch_completed.connect(
                self.on_batch_completed)
            self.batch_processor.batch_cancelled.connect(
                self.on_batch_cancelled)
            self.batch_processor.error_occurred.connect(self.on_ai_error)

            # 连接训练器信号
            self.trainer.training_started.connect(self.on_training_started)
            self.trainer.training_progress.connect(self.on_training_progress)
            self.trainer.training_completed.connect(self.on_training_completed)
            self.trainer.training_error.connect(self.on_training_error)
            self.trainer.training_stopped.connect(self.on_training_stopped)
            self.trainer.log_message.connect(self.on_training_log)

            # 初始化模型列表
            self.refresh_models()

            logger.info("AI组件初始化成功")

        except Exception as e:
            error_msg = f"AI组件初始化失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def refresh_models(self):
        """刷新模型列表"""
        try:
            self.update_status("正在扫描模型...")
            models = self.model_manager.scan_models()

            if not models:
                self.update_status("未找到可用模型", is_error=True)
            else:
                self.update_status(f"找到 {len(models)} 个模型")

        except Exception as e:
            error_msg = f"刷新模型失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def update_model_list(self, models: List[str]):
        """更新模型下拉列表（优化版，支持智能推荐）"""
        try:
            self.model_combo.clear()

            if not models:
                self.model_combo.addItem("无可用模型")
                self.model_combo.setEnabled(False)
                self.predict_current_btn.setEnabled(False)
                self.predict_batch_btn.setEnabled(False)
                return

            self.model_combo.setEnabled(True)

            # 分类模型
            training_models = []
            custom_models = []
            official_models = ['yolov8n.pt', 'yolov8s.pt',
                               'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']

            for model_path in models:
                model_name = os.path.basename(model_path)
                if model_name in official_models:
                    # 官方模型直接添加
                    self.model_combo.addItem(model_name, model_path)
                elif 'runs/train' in model_path.replace('\\', '/'):
                    training_models.append(model_path)
                else:
                    custom_models.append(model_path)

            # 获取推荐模型
            recommended_path = ""
            if training_models:
                # 获取所有训练模型的详细信息
                training_models_info = []
                for model_path in training_models:
                    model_info = self._get_model_detailed_info(model_path)
                    training_models_info.append(model_info)

                # 获取推荐信息
                recommendation = self._get_model_recommendation(
                    training_models_info)
                if recommendation:
                    recommended_path = recommendation.get(
                        'model_info', {}).get('path', '')

            # 按训练时间排序（最新的在前）
            training_models.sort(
                key=lambda x: self._get_training_time(x), reverse=True)

            # 添加训练结果模型
            for model_path in training_models:
                display_name = self._format_training_model_name(model_path)

                # 为推荐模型添加标记
                if model_path == recommended_path:
                    display_name += " 🌟推荐"

                # 创建工具提示
                tooltip = self._create_model_tooltip(model_path)

                # 添加项目
                self.model_combo.addItem(display_name, model_path)

                # 设置工具提示
                item_index = self.model_combo.count() - 1
                self.model_combo.setItemData(
                    item_index, tooltip, 3)  # Qt.ToolTipRole = 3

            # 添加其他自定义模型
            for model_path in custom_models:
                model_name = f"📄 {os.path.basename(model_path)}"
                self.model_combo.addItem(model_name, model_path)

            # 智能默认选择
            self._select_recommended_model(recommended_path)

        except Exception as e:
            logger.error(f"更新模型列表失败: {str(e)}")

    def _select_recommended_model(self, recommended_path: str):
        """智能选择推荐模型作为默认选项"""
        try:
            if recommended_path:
                # 查找推荐模型在下拉框中的位置
                for i in range(self.model_combo.count()):
                    item_data = self.model_combo.itemData(i)
                    if item_data == recommended_path:
                        self.model_combo.setCurrentIndex(i)
                        logger.info(
                            f"自动选择推荐模型: {os.path.basename(recommended_path)}")
                        return

            # 如果没有推荐模型，尝试选择默认模型
            default_models = ["yolov8n.pt", "best.pt"]
            for default_model in default_models:
                for i in range(self.model_combo.count()):
                    if default_model in self.model_combo.itemText(i):
                        self.model_combo.setCurrentIndex(i)
                        logger.info(f"选择默认模型: {default_model}")
                        return

            # 如果都没有，选择第一个可用模型
            if self.model_combo.count() > 0:
                self.model_combo.setCurrentIndex(0)
                logger.info("选择第一个可用模型")

        except Exception as e:
            logger.error(f"选择推荐模型失败: {str(e)}")

    def refresh_classes_info(self):
        """刷新类别信息"""
        try:
            # 更新模型类别信息
            self.update_model_classes_info()

            # 更新用户类别信息
            self.update_user_classes_info()

        except Exception as e:
            logger.error(f"刷新类别信息失败: {str(e)}")

    def update_model_classes_info(self):
        """更新模型类别信息"""
        try:
            if self.predictor and self.predictor.is_model_loaded():
                # 获取模型类别
                class_names = getattr(self.predictor, 'class_names', {})

                # 更新计数
                self.model_classes_count.setText(f"{len(class_names)} 个")
                self.model_classes_count.setStyleSheet(
                    "color: #27ae60; font-weight: bold; font-size: 11px;")

                # 保存类别信息供详情对话框使用
                self.model_classes_data = class_names

            else:
                self.model_classes_count.setText("未加载")
                self.model_classes_count.setStyleSheet(
                    "color: #7f8c8d; font-size: 11px;")
                self.model_classes_data = {}

            # 更新可折叠组件的标题
            if hasattr(self, 'classes_group') and self.classes_group.collapsed:
                self.classes_group.update_title_for_collapsed_state()

        except Exception as e:
            logger.error(f"更新模型类别信息失败: {str(e)}")

    def update_user_classes_info(self):
        """更新用户类别信息"""
        try:
            # 从父窗口获取用户类别信息
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'label_hist'):
                parent_window = parent_window.parent()

            if parent_window and hasattr(parent_window, 'label_hist'):
                user_classes = parent_window.label_hist

                # 更新计数
                self.user_classes_count.setText(f"{len(user_classes)} 个")
                self.user_classes_count.setStyleSheet(
                    "color: #27ae60; font-weight: bold; font-size: 11px;")

                # 保存类别信息供详情对话框使用
                self.user_classes_data = user_classes

            else:
                self.user_classes_count.setText("未加载")
                self.user_classes_count.setStyleSheet(
                    "color: #7f8c8d; font-size: 11px;")
                self.user_classes_data = []

            # 更新可折叠组件的标题
            if hasattr(self, 'classes_group') and self.classes_group.collapsed:
                self.classes_group.update_title_for_collapsed_state()

        except Exception as e:
            logger.error(f"更新用户类别信息失败: {str(e)}")

    def show_classes_detail_dialog(self):
        """显示类别详情对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QTabWidget

            dialog = QDialog(self)
            dialog.setWindowTitle("类别详情")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("📋 类别详细信息")
            title_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 5px;")
            layout.addWidget(title_label)

            # 标签页
            tab_widget = QTabWidget()

            # 模型类别标签页
            model_tab = QListWidget()
            model_classes = getattr(self, 'model_classes_data', {})
            for class_id, class_name in model_classes.items():
                item_text = f"{class_id}: {class_name}"
                model_tab.addItem(item_text)
            tab_widget.addTab(model_tab, f"模型类别 ({len(model_classes)})")

            # 用户类别标签页
            user_tab = QListWidget()
            user_classes = getattr(self, 'user_classes_data', [])
            for i, class_name in enumerate(user_classes):
                item_text = f"{i}: {class_name}"
                user_tab.addItem(item_text)
            tab_widget.addTab(user_tab, f"用户类别 ({len(user_classes)})")

            layout.addWidget(tab_widget)

            # 按钮
            buttons_layout = QHBoxLayout()

            # 映射配置按钮
            mapping_btn = QPushButton("🔗 配置映射")
            mapping_btn.clicked.connect(
                lambda: self.show_class_mapping_dialog())
            buttons_layout.addWidget(mapping_btn)

            buttons_layout.addStretch()

            # 关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示类别详情对话框失败: {str(e)}")

    def show_class_mapping_dialog(self):
        """显示类别映射对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox

            dialog = QDialog(self)
            dialog.setWindowTitle("类别映射配置")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # 说明文本
            info_label = QLabel("配置YOLO模型类别到用户类别的映射关系:")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            # 映射配置文本框
            mapping_text = QTextEdit()
            mapping_text.setPlainText(
                "# 格式: YOLO类别名 -> 用户类别名\n# 示例:\n# person -> 人\n# car -> 汽车\n# bicycle -> 自行车")
            layout.addWidget(mapping_text)

            # 按钮
            buttons_layout = QHBoxLayout()

            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_class_mapping(
                mapping_text.toPlainText(), dialog))
            buttons_layout.addWidget(save_btn)

            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示类别映射对话框失败: {str(e)}")

    def save_class_mapping(self, mapping_text: str, dialog):
        """保存类别映射配置"""
        try:
            # 这里可以实现类别映射的保存逻辑
            # 暂时只显示消息
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", "类别映射功能将在后续版本中实现")
            dialog.accept()

        except Exception as e:
            logger.error(f"保存类别映射失败: {str(e)}")

    def detect_hardware_info(self):
        """检测硬件信息"""
        try:
            import platform
            import subprocess

            # 检测PyTorch和CUDA
            try:
                import torch
                self.hardware_info['pytorch_version'] = torch.__version__

                if torch.cuda.is_available():
                    self.hardware_info['gpu_available'] = True
                    self.hardware_info['gpu_name'] = torch.cuda.get_device_name(
                        0)
                    self.hardware_info['cuda_version'] = torch.version.cuda
                    self.hardware_info['recommended_device'] = 'cuda'

                    # 更新设备状态显示
                    gpu_name = self.hardware_info['gpu_name']
                    if len(gpu_name) > 15:
                        gpu_name = gpu_name[:12] + "..."
                    self.device_status.setText(f"GPU: {gpu_name}")
                    self.device_status.setStyleSheet(
                        "color: #27ae60; font-weight: bold; font-size: 11px;")
                else:
                    self.hardware_info['gpu_available'] = False
                    self.hardware_info['recommended_device'] = 'cpu'
                    self.device_status.setText("CPU 模式")
                    self.device_status.setStyleSheet(
                        "color: #f39c12; font-weight: bold; font-size: 11px;")

                    # 检查是否有NVIDIA驱动但PyTorch是CPU版本
                    if (hasattr(self, 'pytorch_install_btn') and
                        self.hardware_info.get('nvidia_driver') != 'Not Found' and
                            self.hardware_info['pytorch_version'].endswith('+cpu')):
                        self.pytorch_install_btn.setVisible(True)
                        self.device_status.setText("CPU模式 (可升级)")
                        self.device_status.setStyleSheet(
                            "color: #e67e22; font-weight: bold; font-size: 11px;")

            except ImportError:
                # PyTorch未安装
                self.hardware_info['pytorch_version'] = 'Not Installed'
                self.device_status.setText("需要安装PyTorch")
                self.device_status.setStyleSheet(
                    "color: #e74c3c; font-weight: bold; font-size: 11px;")
                # 显示安装按钮
                if hasattr(self, 'pytorch_install_btn'):
                    self.pytorch_install_btn.setVisible(True)

            # 检测系统信息
            self.hardware_info['system'] = platform.system()
            self.hardware_info['python_version'] = platform.python_version()

            # 检测NVIDIA驱动（Windows）
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                                            capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.hardware_info['nvidia_driver'] = result.stdout.strip(
                        )
                    else:
                        self.hardware_info['nvidia_driver'] = 'Not Found'
                except:
                    self.hardware_info['nvidia_driver'] = 'Not Found'

            print(f"[DEBUG] 硬件信息检测完成: {self.hardware_info}")

        except Exception as e:
            logger.error(f"硬件信息检测失败: {str(e)}")
            self.device_status.setText("检测失败")
            self.device_status.setStyleSheet(
                "color: #e74c3c; font-size: 11px;")

    def get_pytorch_install_command(self):
        """获取PyTorch安装命令"""
        try:
            import platform

            system = platform.system().lower()
            python_version = platform.python_version()

            # 基础URL
            base_url = "https://pytorch.org/get-started/locally/"

            if self.hardware_info['gpu_available'] or self.hardware_info['nvidia_driver'] != 'Not Found':
                # 有GPU的情况
                if system == "windows":
                    if self.hardware_info['cuda_version'] and self.hardware_info['cuda_version'] != 'Unknown':
                        cuda_version = self.hardware_info['cuda_version']
                        if cuda_version.startswith('11'):
                            return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                        elif cuda_version.startswith('12'):
                            return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
                    else:
                        return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                else:
                    return "pip install torch torchvision torchaudio"
            else:
                # CPU版本
                if system == "windows":
                    return "pip install torch torchvision torchaudio"
                else:
                    return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"

        except Exception as e:
            logger.error(f"获取PyTorch安装命令失败: {str(e)}")
            return "pip install torch torchvision torchaudio"

    def refresh_training_info(self):
        """刷新训练信息"""
        try:
            # 更新训练数据统计
            self.update_training_data_stats()

            # 检查是否可以开始训练
            self.check_training_readiness()

        except Exception as e:
            logger.error(f"刷新训练信息失败: {str(e)}")

    def update_training_data_stats(self):
        """更新训练数据统计"""
        try:
            # 从父窗口获取标注数据统计
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'label_hist'):
                parent_window = parent_window.parent()

            if parent_window and hasattr(parent_window, 'label_hist'):
                # 这里应该实现实际的数据统计逻辑
                # 暂时使用模拟数据
                user_classes = parent_window.label_hist

                # 模拟统计数据（实际应该扫描标注文件）
                estimated_images = len(user_classes) * 15  # 假设每个类别平均15张图

                self.training_data_stats.update({
                    'total_images': estimated_images,
                    'total_annotations': estimated_images * 2,  # 假设每张图平均2个标注
                    'classes_count': len(user_classes)
                })

                # 更新显示
                self.training_data_count.setText(f"{estimated_images} 张")
                if estimated_images >= self.training_data_stats['min_samples_per_class'] * len(user_classes):
                    self.training_data_count.setStyleSheet(
                        "color: #27ae60; font-weight: bold; font-size: 11px;")
                else:
                    self.training_data_count.setStyleSheet(
                        "color: #e74c3c; font-weight: bold; font-size: 11px;")

            else:
                self.training_data_count.setText("0 张")
                self.training_data_count.setStyleSheet(
                    "color: #7f8c8d; font-size: 11px;")

        except Exception as e:
            logger.error(f"更新训练数据统计失败: {str(e)}")

    def check_training_readiness(self):
        """检查训练准备状态"""
        try:
            stats = self.training_data_stats
            min_required = stats['min_samples_per_class'] * \
                stats['classes_count']

            if stats['total_images'] >= min_required and stats['classes_count'] >= 2:
                # 数据充足，可以训练
                self.train_btn.setEnabled(True)
                self.training_status.setText("就绪")
                self.training_status.setStyleSheet(
                    "color: #27ae60; font-weight: bold; font-size: 11px;")
                self.train_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 10px;
                        padding: 2px 6px;
                        border: 1px solid #27ae60;
                        border-radius: 3px;
                        background-color: #d5f4e6;
                        color: #27ae60;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #a8e6cf;
                    }
                """)
            else:
                # 数据不足
                self.train_btn.setEnabled(False)
                if stats['classes_count'] < 2:
                    self.training_status.setText("需要≥2类")
                else:
                    needed = min_required - stats['total_images']
                    self.training_status.setText(f"需要+{needed}张")
                self.training_status.setStyleSheet(
                    "color: #e74c3c; font-weight: bold; font-size: 11px;")

        except Exception as e:
            logger.error(f"检查训练准备状态失败: {str(e)}")

    def show_complete_training_dialog(self):
        """显示完整的训练配置对话框"""
        try:
            from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                                         QProgressBar, QTextEdit, QGroupBox, QFormLayout, QSpinBox,
                                         QDoubleSpinBox, QComboBox, QLineEdit, QFileDialog,
                                         QCheckBox, QTabWidget, QWidget, QSlider)

            dialog = QDialog(self)
            dialog.setWindowTitle("🎓 YOLO模型训练配置")
            dialog.setModal(True)
            dialog.resize(800, 700)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("🎓 YOLO模型训练配置")
            title_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)

            # 创建标签页
            tab_widget = QTabWidget()
            # 保存标签页控件引用，用于训练时切换
            self.training_tab_widget = tab_widget

            # 第一个标签页：数据配置
            data_tab = self.create_data_config_tab()
            tab_widget.addTab(data_tab, "📁 数据配置")

            # 第二个标签页：训练参数
            params_tab = self.create_training_params_tab()
            tab_widget.addTab(params_tab, "⚙️ 训练参数")

            # 第三个标签页：训练监控
            monitor_tab = self.create_training_monitor_tab()
            tab_widget.addTab(monitor_tab, "📈 训练监控")

            layout.addWidget(tab_widget)

            # 底部按钮
            buttons_layout = QHBoxLayout()

            # 验证配置按钮
            validate_btn = QPushButton("✅ 验证配置")
            validate_btn.clicked.connect(
                lambda: self.validate_training_config(dialog))
            buttons_layout.addWidget(validate_btn)

            buttons_layout.addStretch()

            # 开始训练按钮
            start_btn = QPushButton("🚀 开始训练")
            start_btn.clicked.connect(
                lambda: self.start_complete_training(dialog))
            buttons_layout.addWidget(start_btn)

            # 取消按钮
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)

            layout.addLayout(buttons_layout)

            # 初始化数据
            self.initialize_training_dialog_data()

            # 初始化类别源选择
            if hasattr(self, 'classes_source_combo'):
                self.on_classes_source_changed(
                    self.classes_source_combo.currentText())

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示完整训练对话框失败: {str(e)}")

    def create_data_config_tab(self):
        """创建数据配置标签页"""
        try:
            from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QComboBox, QLineEdit, QPushButton, QSlider, QCheckBox, QLabel
            from PyQt5.QtCore import Qt

            tab = QWidget()
            layout = QVBoxLayout(tab)

            # 数据集配置组
            dataset_group = QGroupBox("📁 数据集配置")
            dataset_layout = QFormLayout(dataset_group)

            # 数据集配置文件
            dataset_config_layout = QHBoxLayout()
            self.dataset_config_edit = QLineEdit()
            self.dataset_config_edit.setPlaceholderText("选择data.yaml配置文件")
            self.dataset_config_edit.textChanged.connect(
                self.on_dataset_config_changed)
            dataset_config_layout.addWidget(self.dataset_config_edit)

            config_browse_btn = QPushButton("📁")
            config_browse_btn.setMaximumWidth(40)
            config_browse_btn.clicked.connect(lambda: self.browse_yaml_file(
                self.dataset_config_edit, "选择YOLO数据集配置文件"))
            dataset_config_layout.addWidget(config_browse_btn)

            config_info_btn = QPushButton("📋")
            config_info_btn.setMaximumWidth(40)
            config_info_btn.clicked.connect(self.show_dataset_config_info)
            dataset_config_layout.addWidget(config_info_btn)
            dataset_layout.addRow("📄 数据集配置:", dataset_config_layout)

            # 显示配置信息
            self.config_info_label = QLabel("请选择或生成data.yaml配置文件")
            self.config_info_label.setStyleSheet(
                "color: #7f8c8d; font-style: italic; padding: 5px;")
            self.config_info_label.setWordWrap(True)
            dataset_layout.addRow("", self.config_info_label)

            # 数据集路径显示（只读）
            self.dataset_path_label = QLabel("从data.yaml配置文件中读取")
            self.dataset_path_label.setStyleSheet(
                "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;")
            dataset_layout.addRow("📁 数据集路径:", self.dataset_path_label)

            # 训练集路径显示（只读）
            self.train_path_label = QLabel("从data.yaml配置文件中读取")
            self.train_path_label.setStyleSheet(
                "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;")
            dataset_layout.addRow("📸 训练集:", self.train_path_label)

            # 验证集路径显示（只读）
            self.val_path_label = QLabel("从data.yaml配置文件中读取")
            self.val_path_label.setStyleSheet(
                "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;")
            dataset_layout.addRow("🔍 验证集:", self.val_path_label)

            # 类别信息显示（只读）
            self.classes_info_label = QLabel("从data.yaml配置文件中读取")
            self.classes_info_label.setStyleSheet(
                "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;")
            dataset_layout.addRow("🏷️ 训练类别:", self.classes_info_label)

            layout.addWidget(dataset_group)

            # 类别源选择组
            classes_source_group = QGroupBox("🏷️ 类别源选择")
            classes_source_layout = QFormLayout(classes_source_group)

            # 类别源选择下拉框
            classes_source_layout_h = QHBoxLayout()
            self.classes_source_combo = QComboBox()
            self.classes_source_combo.addItems([
                "使用当前标注类别",
                "使用预设类别文件",
                "使用类别配置文件"
            ])
            self.classes_source_combo.currentTextChanged.connect(
                self.on_classes_source_changed)
            classes_source_layout_h.addWidget(self.classes_source_combo)

            # 查看类别信息按钮
            view_classes_btn = QPushButton("📋 查看类别")
            view_classes_btn.clicked.connect(
                self.show_classes_info_in_training)
            classes_source_layout_h.addWidget(view_classes_btn)

            classes_source_layout.addRow("类别来源:", classes_source_layout_h)

            # 类别数量显示
            self.selected_classes_count_label = QLabel("未选择类别源")
            self.selected_classes_count_label.setStyleSheet(
                "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;")
            classes_source_layout.addRow(
                "类别数量:", self.selected_classes_count_label)

            layout.addWidget(classes_source_group)

            # 数据统计信息
            stats_group = QGroupBox("📊 数据统计")
            stats_layout = QFormLayout(stats_group)

            self.stats_images_label = QLabel("未扫描")
            self.stats_labels_label = QLabel("未扫描")
            self.stats_classes_label = QLabel("未扫描")
            self.stats_train_label = QLabel("未计算")
            self.stats_val_label = QLabel("未计算")

            stats_layout.addRow("图片数量:", self.stats_images_label)
            stats_layout.addRow("标注数量:", self.stats_labels_label)
            stats_layout.addRow("类别数量:", self.stats_classes_label)
            stats_layout.addRow("训练集:", self.stats_train_label)
            stats_layout.addRow("验证集:", self.stats_val_label)

            # 按钮布局
            buttons_layout = QHBoxLayout()

            # 一键配置按钮
            auto_config_btn = QPushButton("🚀 一键配置")
            auto_config_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            auto_config_btn.clicked.connect(
                self.auto_configure_training_dataset)
            buttons_layout.addWidget(auto_config_btn)

            # 扫描按钮
            scan_btn = QPushButton("🔍 扫描数据集")
            scan_btn.clicked.connect(self.scan_dataset)
            buttons_layout.addWidget(scan_btn)

            stats_layout.addRow("", buttons_layout)

            layout.addWidget(stats_group)

            # 数据配置日志显示区域
            log_group = QGroupBox("📋 数据配置日志")
            log_layout = QVBoxLayout(log_group)

            # 日志文本区域
            from PyQt5.QtWidgets import QTextEdit
            self.data_config_log_text = QTextEdit()
            self.data_config_log_text.setMaximumHeight(200)
            self.data_config_log_text.setReadOnly(True)
            self.data_config_log_text.setStyleSheet("""
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
            self.data_config_log_text.setPlaceholderText("数据配置操作日志将在这里显示...")
            log_layout.addWidget(self.data_config_log_text)

            # 日志控制按钮
            log_buttons_layout = QHBoxLayout()

            clear_log_btn = QPushButton("🗑️ 清空日志")
            clear_log_btn.clicked.connect(
                lambda: self.data_config_log_text.clear())
            log_buttons_layout.addWidget(clear_log_btn)

            log_buttons_layout.addStretch()

            refresh_btn = QPushButton("🔄 刷新配置")
            refresh_btn.clicked.connect(self.refresh_dataset_config)
            log_buttons_layout.addWidget(refresh_btn)

            log_layout.addLayout(log_buttons_layout)

            layout.addWidget(log_group)
            layout.addStretch()

            return tab

        except Exception as e:
            logger.error(f"创建数据配置标签页失败: {str(e)}")
            return QWidget()

    def create_training_params_tab(self):
        """创建训练参数标签页"""
        try:
            from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout,
                                         QSpinBox, QDoubleSpinBox, QComboBox, QPushButton,
                                         QHBoxLayout, QLineEdit, QFileDialog, QLabel)

            tab = QWidget()
            layout = QVBoxLayout(tab)

            # 训练参数配置
            params_group = QGroupBox("⚙️ 训练参数")
            params_layout = QFormLayout(params_group)

            # 训练轮数
            self.epochs_spin = QSpinBox()
            self.epochs_spin.setRange(10, 1000)
            self.epochs_spin.setValue(100)
            params_layout.addRow("训练轮数:", self.epochs_spin)

            # 批次大小
            self.batch_spin = QSpinBox()
            self.batch_spin.setRange(1, 64)
            self.batch_spin.setValue(16)
            params_layout.addRow("批次大小:", self.batch_spin)

            # 学习率
            self.lr_spin = QDoubleSpinBox()
            self.lr_spin.setRange(0.0001, 0.1)
            self.lr_spin.setValue(0.01)
            self.lr_spin.setDecimals(4)
            params_layout.addRow("学习率:", self.lr_spin)

            # 模型选择组
            model_group = QGroupBox("🤖 基础模型选择")
            model_layout = QVBoxLayout(model_group)

            # 模型类型选择
            model_type_layout = QHBoxLayout()
            self.model_type_combo = QComboBox()
            self.model_type_combo.addItems(["预训练模型", "自定义模型", "手动指定"])
            self.model_type_combo.currentTextChanged.connect(
                self.on_model_type_changed)
            model_type_layout.addWidget(QLabel("模型类型:"))
            model_type_layout.addWidget(self.model_type_combo)
            model_layout.addLayout(model_type_layout)

            # 预训练模型选择
            self.pretrained_combo = QComboBox()
            self.pretrained_combo.addItems(
                ["yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x"])
            self.pretrained_combo.setCurrentText("yolov8n")
            model_layout.addWidget(self.pretrained_combo)

            # 自定义模型选择
            self.custom_combo = QComboBox()
            self.custom_combo.setVisible(False)
            model_layout.addWidget(self.custom_combo)

            # 手动指定模型路径
            manual_layout = QHBoxLayout()
            self.manual_model_edit = QLineEdit()
            self.manual_model_edit.setPlaceholderText("请选择模型文件路径...")
            self.manual_model_edit.setVisible(False)
            manual_browse_btn = QPushButton("📁 浏览")
            manual_browse_btn.clicked.connect(self.browse_manual_model)
            manual_browse_btn.setVisible(False)
            manual_layout.addWidget(self.manual_model_edit)
            manual_layout.addWidget(manual_browse_btn)
            self.manual_layout_widget = QWidget()
            self.manual_layout_widget.setLayout(manual_layout)
            self.manual_layout_widget.setVisible(False)
            model_layout.addWidget(self.manual_layout_widget)

            # 刷新自定义模型按钮
            refresh_layout = QHBoxLayout()
            self.refresh_models_btn = QPushButton("🔄 刷新模型列表")
            self.refresh_models_btn.clicked.connect(
                self.refresh_training_models)
            self.refresh_models_btn.setVisible(False)
            refresh_layout.addWidget(self.refresh_models_btn)
            refresh_layout.addStretch()
            model_layout.addLayout(refresh_layout)

            params_layout.addRow(model_group)

            # 训练设备选择
            self.device_combo = QComboBox()
            if self.hardware_info['gpu_available']:
                self.device_combo.addItems(["GPU (推荐)", "CPU"])
                self.device_combo.setCurrentText("GPU (推荐)")
            else:
                self.device_combo.addItems(["CPU", "GPU (不可用)"])
                self.device_combo.setCurrentText("CPU")
            params_layout.addRow("训练设备:", self.device_combo)

            layout.addWidget(params_group)

            # 添加模型详情面板
            model_details_group = self.create_model_details_panel()
            layout.addWidget(model_details_group)

            layout.addStretch()

            # 初始化自定义模型列表
            self.refresh_training_models()

            # 连接模型选择变化事件
            self.custom_combo.currentTextChanged.connect(
                self.on_training_model_changed)

            return tab

        except Exception as e:
            logger.error(f"创建训练参数标签页失败: {str(e)}")
            return QWidget()

    def create_model_details_panel(self):
        """创建模型详情面板"""
        try:
            from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout,
                                         QLabel, QProgressBar, QFrame)
            from PyQt5.QtCore import Qt

            # 主面板
            details_group = QGroupBox("📊 模型详情")
            details_layout = QVBoxLayout(details_group)

            # 模型名称和推荐标记
            self.model_name_label = QLabel("请选择自定义模型查看详情")
            self.model_name_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: #2c3e50;")
            details_layout.addWidget(self.model_name_label)

            # 分隔线
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            details_layout.addWidget(line)

            # 主要信息区域
            main_info_layout = QHBoxLayout()

            # 左侧：性能指标
            perf_layout = QVBoxLayout()
            perf_title = QLabel("📈 性能指标")
            perf_title.setStyleSheet("font-weight: bold; color: #27ae60;")
            perf_layout.addWidget(perf_title)

            # mAP50 进度条
            self.map50_layout = QHBoxLayout()
            self.map50_label = QLabel("mAP50:")
            self.map50_bar = QProgressBar()
            self.map50_bar.setMaximum(100)
            self.map50_bar.setTextVisible(True)
            self.map50_value = QLabel("--")
            self.map50_layout.addWidget(self.map50_label)
            self.map50_layout.addWidget(self.map50_bar)
            self.map50_layout.addWidget(self.map50_value)
            perf_layout.addLayout(self.map50_layout)

            # 精确度进度条
            self.precision_layout = QHBoxLayout()
            self.precision_label = QLabel("精确度:")
            self.precision_bar = QProgressBar()
            self.precision_bar.setMaximum(100)
            self.precision_bar.setTextVisible(True)
            self.precision_value = QLabel("--")
            self.precision_layout.addWidget(self.precision_label)
            self.precision_layout.addWidget(self.precision_bar)
            self.precision_layout.addWidget(self.precision_value)
            perf_layout.addLayout(self.precision_layout)

            # 召回率进度条
            self.recall_layout = QHBoxLayout()
            self.recall_label = QLabel("召回率:")
            self.recall_bar = QProgressBar()
            self.recall_bar.setMaximum(100)
            self.recall_bar.setTextVisible(True)
            self.recall_value = QLabel("--")
            self.recall_layout.addWidget(self.recall_label)
            self.recall_layout.addWidget(self.recall_bar)
            self.recall_layout.addWidget(self.recall_value)
            perf_layout.addLayout(self.recall_layout)

            main_info_layout.addLayout(perf_layout)

            # 右侧：基本信息和配置
            info_layout = QVBoxLayout()

            # 基本信息
            basic_title = QLabel("📁 基本信息")
            basic_title.setStyleSheet("font-weight: bold; color: #3498db;")
            info_layout.addWidget(basic_title)

            self.model_size_label = QLabel("大小: --")
            self.model_type_label = QLabel("类型: --")
            self.model_path_label = QLabel("路径: --")
            self.model_path_label.setWordWrap(True)

            info_layout.addWidget(self.model_size_label)
            info_layout.addWidget(self.model_type_label)
            info_layout.addWidget(self.model_path_label)

            # 训练配置
            config_title = QLabel("⚙️ 训练配置")
            config_title.setStyleSheet("font-weight: bold; color: #e67e22;")
            info_layout.addWidget(config_title)

            self.config_epochs_label = QLabel("轮数: --")
            self.config_batch_label = QLabel("批次: --")
            self.config_dataset_label = QLabel("数据集: --")

            info_layout.addWidget(self.config_epochs_label)
            info_layout.addWidget(self.config_batch_label)
            info_layout.addWidget(self.config_dataset_label)

            main_info_layout.addLayout(info_layout)
            details_layout.addLayout(main_info_layout)

            # 推荐理由
            self.recommendation_label = QLabel("")
            self.recommendation_label.setStyleSheet(
                "background-color: #f8f9fa; padding: 8px; border-radius: 4px; "
                "border-left: 4px solid #28a745; color: #155724;"
            )
            self.recommendation_label.setWordWrap(True)
            details_layout.addWidget(self.recommendation_label)

            # 初始状态下隐藏详情
            self.hide_model_details()

            return details_group

        except Exception as e:
            logger.error(f"创建模型详情面板失败: {str(e)}")
            return QGroupBox("模型详情")

    def hide_model_details(self):
        """隐藏模型详情"""
        try:
            # 隐藏所有进度条和标签
            widgets_to_hide = [
                self.map50_bar, self.map50_value,
                self.precision_bar, self.precision_value,
                self.recall_bar, self.recall_value,
                self.model_size_label, self.model_type_label, self.model_path_label,
                self.config_epochs_label, self.config_batch_label, self.config_dataset_label,
                self.recommendation_label
            ]

            for widget in widgets_to_hide:
                widget.setVisible(False)

        except Exception as e:
            logger.debug(f"隐藏模型详情失败: {str(e)}")

    def show_model_details(self):
        """显示模型详情"""
        try:
            # 显示所有进度条和标签
            widgets_to_show = [
                self.map50_bar, self.map50_value,
                self.precision_bar, self.precision_value,
                self.recall_bar, self.recall_value,
                self.model_size_label, self.model_type_label, self.model_path_label,
                self.config_epochs_label, self.config_batch_label, self.config_dataset_label,
                self.recommendation_label
            ]

            for widget in widgets_to_show:
                widget.setVisible(True)

        except Exception as e:
            logger.debug(f"显示模型详情失败: {str(e)}")

    def on_training_model_changed(self):
        """处理训练模型选择变化"""
        try:
            current_text = self.custom_combo.currentText()
            current_data = self.custom_combo.currentData()

            if not current_data or not current_text or "无" in current_text:
                # 没有选择有效模型
                self.model_name_label.setText("请选择自定义模型查看详情")
                self.hide_model_details()
                return

            # 检查是否是训练结果模型
            if 'runs/train' not in current_data.replace('\\', '/'):
                # 不是训练结果模型，显示简单信息
                self.model_name_label.setText(
                    f"📄 {os.path.basename(current_data)}")
                self.hide_model_details()
                return

            # 获取模型详细信息
            model_info = self._get_model_detailed_info(current_data)
            self.update_model_details_display(model_info)

        except Exception as e:
            logger.error(f"处理训练模型选择变化失败: {str(e)}")

    def update_model_details_display(self, model_info: dict):
        """更新模型详情显示"""
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

            model_name = f"{icon} {training_dir}/{model_type} {stars} ({rating})"

            # 检查是否是推荐模型
            current_text = self.custom_combo.currentText()
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

    def update_performance_bars(self, performance: dict):
        """更新性能指标进度条"""
        try:
            # 更新mAP50
            mAP50 = performance.get('mAP50', 0)
            mAP50_percent = int(mAP50 * 100)
            self.map50_bar.setValue(mAP50_percent)
            self.map50_value.setText(f"{mAP50:.3f}")

            # 设置进度条颜色
            if mAP50 >= 0.6:
                color = "#27ae60"  # 绿色
            elif mAP50 >= 0.4:
                color = "#f39c12"  # 橙色
            else:
                color = "#e74c3c"  # 红色

            self.map50_bar.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)

            # 更新精确度
            precision = performance.get('precision', 0)
            precision_percent = int(precision * 100)
            self.precision_bar.setValue(precision_percent)
            self.precision_value.setText(f"{precision:.3f}")

            # 更新召回率
            recall = performance.get('recall', 0)
            recall_percent = int(recall * 100)
            self.recall_bar.setValue(recall_percent)
            self.recall_value.setText(f"{recall:.3f}")

        except Exception as e:
            logger.debug(f"更新性能指标进度条失败: {str(e)}")

    def update_recommendation_display(self, model_info: dict):
        """更新推荐理由显示"""
        try:
            # 获取推荐信息
            models_info = [model_info]  # 单个模型的推荐分析
            recommendation = self._get_model_recommendation(models_info)

            if recommendation:
                recommendation_text = recommendation.get(
                    'recommendation_text', '')
                score = recommendation.get('score', 0)

                # 构建推荐显示文本
                display_text = f"💡 {recommendation_text} (评分: {score:.1f})"
                self.recommendation_label.setText(display_text)
                self.recommendation_label.setVisible(True)
            else:
                # 生成基本推荐理由
                performance = model_info.get('performance', {})
                mAP50 = performance.get('mAP50', 0)

                if mAP50 > 0.6:
                    reason = "性能优秀，推荐使用"
                elif mAP50 > 0.4:
                    reason = "性能良好，可以使用"
                elif mAP50 > 0.2:
                    reason = "性能一般，建议继续训练"
                else:
                    reason = "性能较低，需要优化训练参数"

                self.recommendation_label.setText(f"💡 {reason}")
                self.recommendation_label.setVisible(True)

        except Exception as e:
            logger.debug(f"更新推荐理由显示失败: {str(e)}")

    def on_model_type_changed(self, model_type: str):
        """处理模型类型切换"""
        try:
            self._safe_append_log(f"🔄 切换模型类型: {model_type}")

            # 隐藏所有模型选择控件
            self.pretrained_combo.setVisible(False)
            self.custom_combo.setVisible(False)
            self.manual_layout_widget.setVisible(False)
            self.refresh_models_btn.setVisible(False)

            if model_type == "预训练模型":
                self.pretrained_combo.setVisible(True)
                self._safe_append_log("📦 显示预训练模型选择")

            elif model_type == "自定义模型":
                self.custom_combo.setVisible(True)
                self.refresh_models_btn.setVisible(True)
                self._safe_append_log("🎯 显示自定义模型选择")
                # 刷新自定义模型列表
                self.refresh_training_models()

            elif model_type == "手动指定":
                self.manual_layout_widget.setVisible(True)
                self._safe_append_log("📁 显示手动模型路径选择")

        except Exception as e:
            logger.error(f"切换模型类型失败: {str(e)}")
            self._safe_append_log(f"❌ 切换模型类型失败: {str(e)}")

    def refresh_training_models(self):
        """刷新训练用的自定义模型列表"""
        try:
            self._safe_append_log("🔍 正在扫描自定义模型...")

            # 清空当前列表
            self.custom_combo.clear()

            # 获取模型管理器实例
            if hasattr(self, 'model_manager') and self.model_manager:
                # 重新扫描模型
                models = self.model_manager.scan_models()

                # 过滤出自定义模型（非官方预训练模型）
                custom_models = []
                training_models = []
                official_models = ['yolov8n.pt', 'yolov8s.pt',
                                   'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']

                for model_path in models:
                    model_name = os.path.basename(model_path)
                    # 如果不是官方模型，则认为是自定义模型
                    if model_name not in official_models:
                        if 'runs/train' in model_path.replace('\\', '/'):
                            training_models.append(model_path)
                        else:
                            custom_models.append(model_path)

                # 按类型分组显示模型
                total_models = len(custom_models) + len(training_models)

                if total_models > 0:
                    # 首先添加训练结果模型（优先显示）
                    if training_models:
                        # 获取所有训练模型的详细信息
                        training_models_info = []
                        for model_path in training_models:
                            model_info = self._get_model_detailed_info(
                                model_path)
                            training_models_info.append(model_info)

                        # 获取推荐信息
                        recommendation = self._get_model_recommendation(
                            training_models_info)
                        recommended_path = recommendation.get(
                            'model_info', {}).get('path', '')

                        # 按训练时间排序（最新的在前）
                        training_models.sort(
                            key=lambda x: self._get_training_time(x), reverse=True)

                        for model_path in training_models:
                            display_name = self._format_training_model_name(
                                model_path)

                            # 为推荐模型添加标记
                            if model_path == recommended_path:
                                display_name += " 🌟推荐"

                            tooltip = self._create_model_tooltip(model_path)

                            # 添加项目
                            self.custom_combo.addItem(display_name, model_path)

                            # 设置工具提示（需要在添加后设置）
                            item_index = self.custom_combo.count() - 1
                            self.custom_combo.setItemData(
                                item_index, tooltip, 3)  # Qt.ToolTipRole = 3

                    # 然后添加其他自定义模型
                    if custom_models:
                        for model_path in custom_models:
                            model_name = os.path.basename(model_path)
                            if 'custom' in model_path:
                                display_name = f"📄 [自定义] {model_name}"
                            else:
                                display_name = f"👤 [用户] {model_name}"

                            # 创建简单的工具提示
                            try:
                                size_mb = round(os.path.getsize(
                                    model_path) / (1024 * 1024), 2)
                                tooltip = f"📁 路径: {model_path}\n📊 大小: {size_mb} MB"
                            except Exception:
                                tooltip = f"📁 路径: {model_path}"

                            # 添加项目和工具提示
                            self.custom_combo.addItem(display_name, model_path)
                            item_index = self.custom_combo.count() - 1
                            self.custom_combo.setItemData(
                                item_index, tooltip, 3)

                    self._safe_append_log(f"✅ 找到 {total_models} 个可用模型")
                    if training_models:
                        self._safe_append_log(
                            f"   🎯 训练结果模型: {len(training_models)} 个")
                    if custom_models:
                        self._safe_append_log(
                            f"   📄 自定义模型: {len(custom_models)} 个")
                else:
                    self.custom_combo.addItem("无自定义模型")
                    self._safe_append_log("⚠️ 未找到自定义模型")
            else:
                self.custom_combo.addItem("模型管理器未初始化")
                self._safe_append_log("❌ 模型管理器未初始化")

        except Exception as e:
            logger.error(f"刷新自定义模型列表失败: {str(e)}")
            self._safe_append_log(f"❌ 刷新模型列表失败: {str(e)}")
            self.custom_combo.clear()
            self.custom_combo.addItem("刷新失败")

    def _get_training_time(self, model_path: str) -> float:
        """获取训练模型的时间戳（用于排序）"""
        try:
            # 从模型文件的修改时间获取时间戳
            return os.path.getmtime(model_path)
        except Exception:
            return 0.0

    def _format_training_model_name(self, model_path: str) -> str:
        """格式化训练模型的显示名称（优化版）"""
        try:
            import time

            # 获取模型详细信息
            info = self._get_model_detailed_info(model_path)

            # 提取关键信息
            training_dir = info.get('training_dir', 'unknown')
            model_type = info.get('model_type', 'unknown.pt')
            performance = info.get('performance', {})

            # 简化训练目录名称（去掉yolo_training前缀）
            short_dir = training_dir.replace('yolo_training', 'T') if training_dir.startswith(
                'yolo_training') else training_dir

            # 选择图标
            if 'best' in model_type:
                icon = "🏆"  # 最佳模型
            elif 'last' in model_type:
                icon = "📝"  # 最新模型
            else:
                icon = "🎯"  # 其他训练模型

            # 获取时间（简化格式）
            try:
                mtime = os.path.getmtime(model_path)
                time_str = time.strftime("%m-%d %H:%M", time.localtime(mtime))
            except Exception:
                time_str = "未知"

            # 获取性能指标
            mAP50 = performance.get('mAP50', 0)

            # 构建显示名称
            model_name = model_type.replace('.pt', '')

            if mAP50 > 0:
                # 包含性能指标的格式：🏆 T7-best (07-17 08:44) mAP:0.485
                return f"{icon} {short_dir}-{model_name} ({time_str}) mAP:{mAP50}"
            else:
                # 不包含性能指标的格式：🏆 T7-best (07-17 08:44)
                return f"{icon} {short_dir}-{model_name} ({time_str})"

        except Exception as e:
            logger.error(f"格式化训练模型名称失败: {str(e)}")
            return f"🎯 {os.path.basename(model_path)}"

    def _create_model_tooltip(self, model_path: str) -> str:
        """创建模型的详细工具提示"""
        try:
            info = self._get_model_detailed_info(model_path)

            tooltip_lines = [
                f"📁 完整路径: {info.get('path', model_path)}",
                f"📊 文件大小: {info.get('size_mb', 0)} MB",
                f"🕒 训练时间: {info.get('modified_time', '未知')}",
                ""
            ]

            # 添加训练配置信息
            config = info.get('config', {})
            if config:
                tooltip_lines.extend([
                    "⚙️ 训练配置:",
                    f"   轮数: {config.get('epochs', '?')} epochs",
                    f"   批次: {config.get('batch', '?')}",
                    f"   数据集: {config.get('dataset', '未知')}",
                    ""
                ])

            # 添加性能指标
            performance = info.get('performance', {})
            if performance and performance.get('mAP50', 0) > 0:
                tooltip_lines.extend([
                    "📈 性能指标:",
                    f"   mAP50: {performance.get('mAP50', 0)}",
                    f"   mAP50-95: {performance.get('mAP50_95', 0)}",
                    f"   精确度: {performance.get('precision', 0)}",
                    f"   召回率: {performance.get('recall', 0)}",
                    f"   完成轮数: {performance.get('final_epoch', 0)}"
                ])

            return "\n".join(tooltip_lines)

        except Exception as e:
            logger.error(f"创建模型工具提示失败: {str(e)}")
            return f"模型路径: {model_path}"

    def _calculate_model_score(self, model_info: dict) -> float:
        """计算模型综合评分（用于智能推荐）"""
        try:
            score = 0.0

            # 性能权重 (40%) - 基于mAP50
            performance = model_info.get('performance', {})
            mAP50 = performance.get('mAP50', 0)
            score += mAP50 * 40

            # 时间权重 (30%) - 越新越好
            import time
            try:
                model_path = model_info.get('path', '')
                if os.path.exists(model_path):
                    mtime = os.path.getmtime(model_path)
                    days_old = (time.time() - mtime) / (24 * 3600)  # 转换为天数
                    time_score = max(0, 30 - days_old * 2)  # 每天减2分，最多30分
                    score += time_score
            except Exception:
                pass

            # 模型类型权重 (20%) - best > last
            model_type = model_info.get('model_type', '')
            if 'best' in model_type.lower():
                score += 20
            elif 'last' in model_type.lower():
                score += 10

            # 完整性权重 (10%) - 有完整训练信息的加分
            if (model_info.get('config') and
                model_info.get('performance') and
                    performance.get('mAP50', 0) > 0):
                score += 10

            return round(score, 2)

        except Exception as e:
            logger.debug(f"计算模型评分失败: {str(e)}")
            return 0.0

    def _get_model_recommendation(self, models_info: list) -> dict:
        """获取模型推荐信息"""
        try:
            if not models_info:
                return {}

            # 计算每个模型的评分
            scored_models = []
            for model_info in models_info:
                score = self._calculate_model_score(model_info)
                scored_models.append({
                    'info': model_info,
                    'score': score
                })

            # 按评分排序
            scored_models.sort(key=lambda x: x['score'], reverse=True)

            if not scored_models:
                return {}

            # 获取最佳模型
            best_model = scored_models[0]
            best_info = best_model['info']
            best_score = best_model['score']

            # 生成推荐理由
            reasons = []
            performance = best_info.get('performance', {})
            mAP50 = performance.get('mAP50', 0)

            if mAP50 > 0.6:
                reasons.append("性能优秀")
            elif mAP50 > 0.4:
                reasons.append("性能良好")
            elif mAP50 > 0.2:
                reasons.append("性能一般")

            if 'best' in best_info.get('model_type', '').lower():
                reasons.append("最佳模型")

            # 检查是否是最新的
            try:
                import time
                model_path = best_info.get('path', '')
                if os.path.exists(model_path):
                    mtime = os.path.getmtime(model_path)
                    days_old = (time.time() - mtime) / (24 * 3600)
                    if days_old < 1:
                        reasons.append("最新训练")
                    elif days_old < 7:
                        reasons.append("近期训练")
            except Exception:
                pass

            recommendation = {
                'model_info': best_info,
                'score': best_score,
                'reasons': reasons,
                'recommendation_text': f"推荐理由: {', '.join(reasons) if reasons else '综合评分最高'}"
            }

            return recommendation

        except Exception as e:
            logger.error(f"获取模型推荐失败: {str(e)}")
            return {}

    def _get_performance_rating(self, mAP50: float) -> tuple:
        """获取性能评级（星级和描述）"""
        if mAP50 >= 0.8:
            return "⭐⭐⭐⭐⭐", "优秀"
        elif mAP50 >= 0.6:
            return "⭐⭐⭐⭐", "良好"
        elif mAP50 >= 0.4:
            return "⭐⭐⭐", "一般"
        elif mAP50 >= 0.2:
            return "⭐⭐", "较差"
        elif mAP50 > 0:
            return "⭐", "很差"
        else:
            return "", "未知"

    def _get_training_config_info(self, model_path: str) -> str:
        """获取训练配置信息"""
        try:
            # 获取训练目录
            training_dir = os.path.dirname(os.path.dirname(model_path))
            args_file = os.path.join(training_dir, "args.yaml")

            if os.path.exists(args_file):
                import yaml
                with open(args_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                epochs = config.get('epochs', '?')
                batch = config.get('batch', '?')
                return f"E{epochs}/B{batch}"

        except Exception as e:
            logger.debug(f"获取训练配置信息失败: {str(e)}")

        return ""

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

    def _get_model_detailed_info(self, model_path: str) -> dict:
        """获取模型详细信息"""
        try:
            info = {
                'path': model_path,
                'size_mb': 0,
                'modified_time': '',
                'training_dir': '',
                'model_type': os.path.basename(model_path),
                'config': {},
                'performance': {}
            }

            # 获取文件大小
            if os.path.exists(model_path):
                info['size_mb'] = round(os.path.getsize(
                    model_path) / (1024 * 1024), 2)

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
                with open(args_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    info['config'] = {
                        'epochs': config.get('epochs', '?'),
                        'batch': config.get('batch', '?'),
                        'dataset': os.path.basename(config.get('data', '未知数据集'))
                    }

            # 获取性能指标
            info['performance'] = self._get_training_performance(model_path)

            return info

        except Exception as e:
            logger.error(f"获取模型详细信息失败: {str(e)}")
            return {}

    def browse_manual_model(self):
        """浏览选择手动指定的模型文件"""
        try:
            from PyQt5.QtWidgets import QFileDialog

            self._safe_append_log("📁 打开模型文件选择对话框...")

            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择模型文件",
                "",
                "模型文件 (*.pt *.onnx *.engine);;所有文件 (*.*)"
            )

            if file_path:
                self.manual_model_edit.setText(file_path)
                self._safe_append_log(f"✅ 选择模型文件: {file_path}")

                # 验证模型文件
                if os.path.exists(file_path):
                    file_size = os.path.getsize(
                        file_path) / (1024 * 1024)  # MB
                    self._safe_append_log(f"📊 模型文件大小: {file_size:.2f} MB")
                else:
                    self._safe_append_log("⚠️ 警告: 选择的文件不存在")
            else:
                self._safe_append_log("❌ 未选择模型文件")

        except Exception as e:
            logger.error(f"浏览模型文件失败: {str(e)}")
            self._safe_append_log(f"❌ 浏览模型文件失败: {str(e)}")

    def get_selected_training_model(self):
        """获取当前选择的训练模型信息"""
        try:
            model_type = self.model_type_combo.currentText()
            self._safe_append_log(f"🔍 获取选择的模型类型: {model_type}")

            if model_type == "预训练模型":
                model_name = self.pretrained_combo.currentText()
                model_path = f"{model_name}.pt"
                self._safe_append_log(f"📦 选择预训练模型: {model_name}")
                return {
                    'type': 'pretrained',
                    'name': model_name,
                    'path': model_path
                }

            elif model_type == "自定义模型":
                if self.custom_combo.count() == 0 or self.custom_combo.currentText() in ["无自定义模型", "模型管理器未初始化", "刷新失败"]:
                    self._safe_append_log("❌ 没有可用的自定义模型")
                    return None

                current_index = self.custom_combo.currentIndex()
                model_path = self.custom_combo.itemData(current_index)
                model_name = self.custom_combo.currentText()

                if model_path:
                    self._safe_append_log(f"🎯 选择自定义模型: {model_name}")
                    self._safe_append_log(f"📄 模型路径: {model_path}")
                    return {
                        'type': 'custom',
                        'name': model_name,
                        'path': model_path
                    }
                else:
                    self._safe_append_log("❌ 自定义模型路径无效")
                    return None

            elif model_type == "手动指定":
                model_path = self.manual_model_edit.text().strip()
                if not model_path:
                    self._safe_append_log("❌ 未指定模型路径")
                    return None

                if not os.path.exists(model_path):
                    self._safe_append_log(f"❌ 模型文件不存在: {model_path}")
                    return None

                model_name = os.path.basename(model_path)
                self._safe_append_log(f"📁 手动指定模型: {model_name}")
                self._safe_append_log(f"📄 模型路径: {model_path}")
                return {
                    'type': 'manual',
                    'name': model_name,
                    'path': model_path
                }

            else:
                self._safe_append_log(f"❌ 未知的模型类型: {model_type}")
                return None

        except Exception as e:
            logger.error(f"获取选择的训练模型失败: {str(e)}")
            self._safe_append_log(f"❌ 获取模型信息失败: {str(e)}")
            return None

    def create_training_monitor_tab(self):
        """创建训练监控标签页"""
        try:
            from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QProgressBar, QTextEdit, QHBoxLayout, QLabel

            tab = QWidget()
            layout = QVBoxLayout(tab)

            # 训练进度组
            progress_group = QGroupBox("📈 训练进度")
            progress_layout = QVBoxLayout(progress_group)

            # 进度条和状态
            progress_info_layout = QHBoxLayout()

            self.training_progress_bar = QProgressBar()
            self.training_progress_bar.setValue(0)
            self.training_progress_bar.setFormat("等待开始训练... (%p%)")
            progress_info_layout.addWidget(self.training_progress_bar)

            # 训练状态标签
            self.training_status_label = QLabel("🔄 准备就绪")
            self.training_status_label.setStyleSheet(
                "color: #3498db; font-weight: bold;")
            progress_info_layout.addWidget(self.training_status_label)

            progress_layout.addLayout(progress_info_layout)

            # 训练指标显示
            metrics_layout = QHBoxLayout()

            # 损失值
            loss_label = QLabel("📉 损失值: --")
            loss_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
            metrics_layout.addWidget(loss_label)
            self.loss_label = loss_label

            # mAP值
            map_label = QLabel("🎯 mAP50: --")
            map_label.setStyleSheet("color: #27ae60; font-size: 12px;")
            metrics_layout.addWidget(map_label)
            self.map_label = map_label

            # 学习率
            lr_label = QLabel("📊 学习率: --")
            lr_label.setStyleSheet("color: #f39c12; font-size: 12px;")
            metrics_layout.addWidget(lr_label)
            self.lr_label = lr_label

            progress_layout.addLayout(metrics_layout)
            layout.addWidget(progress_group)

            # 训练日志组
            log_group = QGroupBox("📋 训练日志")
            log_layout = QVBoxLayout(log_group)

            self.monitor_log_text = QTextEdit()
            self.monitor_log_text.setPlainText("点击'开始训练'启动训练过程...")
            self.monitor_log_text.setMaximumHeight(600)
            log_layout.addWidget(self.monitor_log_text)

            # 训练控制按钮
            control_layout = QHBoxLayout()

            self.stop_training_btn = QPushButton("🛑 停止训练")
            self.stop_training_btn.setEnabled(False)
            self.stop_training_btn.clicked.connect(self.stop_training)
            self.stop_training_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
            """)
            control_layout.addWidget(self.stop_training_btn)
            control_layout.addStretch()

            log_layout.addLayout(control_layout)
            layout.addWidget(log_group)

            # 为了向后兼容，保留原来的log_text引用
            self.log_text = self.monitor_log_text

            return tab

        except Exception as e:
            logger.error(f"创建训练监控标签页失败: {str(e)}")
            return QWidget()

    def initialize_training_dialog_data(self):
        """初始化训练对话框数据"""
        try:
            self._safe_append_log("🔍 初始化训练对话框数据...")

            # 尝试自动检测当前工作目录的data.yaml文件
            import os
            current_dir = os.getcwd()
            self._safe_append_log(f"📂 当前工作目录: {current_dir}")

            # 常见的数据集文件夹
            dataset_folders = ['datasets', 'data', 'training_dataset']
            self._safe_append_log(f"🔍 搜索数据集文件夹: {dataset_folders}")

            for folder in dataset_folders:
                folder_path = os.path.join(current_dir, folder)
                self._safe_append_log(f"📁 检查文件夹: {folder_path}")

                if os.path.exists(folder_path):
                    self._safe_append_log(f"✅ 文件夹存在: {folder_path}")

                    # 查找data.yaml文件
                    for root, dirs, files in os.walk(folder_path):
                        self._safe_append_log(f"🔍 搜索目录: {root}")
                        self._safe_append_log(f"📄 找到文件: {files}")

                        for file in files:
                            if file in ['data.yaml', 'data.yml']:
                                yaml_path = os.path.join(root, file)
                                self._safe_append_log(
                                    f"🎯 找到数据集配置文件: {yaml_path}")

                                if hasattr(self, 'dataset_config_edit'):
                                    self.dataset_config_edit.setText(yaml_path)
                                    self._safe_append_log(
                                        f"✅ 已设置数据集配置路径: {yaml_path}")
                                    self.load_dataset_config(yaml_path)
                                return
                else:
                    self._safe_append_log(f"❌ 文件夹不存在: {folder_path}")

            self._safe_append_log("⚠️ 未找到数据集配置文件，请手动选择")

        except Exception as e:
            error_msg = f"初始化训练对话框数据失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_log(f"❌ {error_msg}")

    def browse_folder(self, line_edit, title):
        """浏览文件夹"""
        try:
            from PyQt5.QtWidgets import QFileDialog

            folder = QFileDialog.getExistingDirectory(self, title)
            if folder:
                line_edit.setText(folder)

        except Exception as e:
            logger.error(f"浏览文件夹失败: {str(e)}")

    def update_split_labels(self, value):
        """更新数据划分标签"""
        try:
            # 这个方法现在不需要了，因为数据划分信息从data.yaml中读取
            pass

        except Exception as e:
            logger.error(f"更新数据划分标签失败: {str(e)}")

    def calculate_split_counts(self):
        """计算训练集和验证集数量"""
        try:
            # 这个方法现在不需要了，因为数据划分信息从data.yaml中读取
            pass

        except Exception as e:
            logger.error(f"计算数据划分数量失败: {str(e)}")

    def scan_dataset(self):
        """扫描数据集"""
        try:
            self._safe_append_data_log("🔍 开始扫描数据集...")

            # 从data.yaml配置中获取路径信息
            config_path = getattr(self, 'dataset_config_edit', None)
            if not config_path or not config_path.text().strip():
                error_msg = "⚠️ 请先选择data.yaml配置文件"
                self._safe_append_data_log(error_msg)
                if hasattr(self, 'stats_images_label'):
                    self.stats_images_label.setText("请先选择data.yaml配置文件")
                return

            yaml_path = config_path.text().strip()
            self._safe_append_data_log(f"📄 配置文件路径: {yaml_path}")

            if not os.path.exists(yaml_path):
                error_msg = f"❌ 配置文件不存在: {yaml_path}"
                self._safe_append_data_log(error_msg)
                if hasattr(self, 'stats_images_label'):
                    self.stats_images_label.setText("配置文件不存在")
                return

            self._safe_append_data_log("✅ 配置文件存在，开始重新加载...")

            # 重新加载配置文件以更新统计信息
            self.load_dataset_config(yaml_path)

            self._safe_append_data_log("✅ 数据集扫描完成")

        except Exception as e:
            error_msg = f"扫描数据集失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_data_log(f"❌ {error_msg}")
            if hasattr(self, 'stats_images_label'):
                self.stats_images_label.setText("扫描失败")

    def on_classes_source_changed(self, text):
        """类别源改变时的处理"""
        try:
            # 根据选择的类别源更新类别数量显示
            if hasattr(self, 'selected_classes_count_label'):
                if text == "使用当前标注类别":
                    # 从父窗口获取标注历史
                    parent_window = self.parent()
                    while parent_window and not hasattr(parent_window, 'label_hist'):
                        parent_window = parent_window.parent()

                    if parent_window and hasattr(parent_window, 'label_hist'):
                        classes_count = len(parent_window.label_hist)
                        self.selected_classes_count_label.setText(
                            f"{classes_count} 个类别")
                        self.selected_classes_count_label.setStyleSheet(
                            "color: #27ae60; padding: 5px; border: 1px solid #27ae60; border-radius: 3px; background-color: #d5f4e6;")
                    else:
                        self.selected_classes_count_label.setText("未找到标注类别")
                        self.selected_classes_count_label.setStyleSheet(
                            "color: #e74c3c; padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; background-color: #fadbd8;")

                elif text == "使用预设类别文件":
                    # 读取预设类别文件
                    try:
                        import os
                        from labelImg import get_persistent_predefined_classes_path
                        predefined_file = get_persistent_predefined_classes_path()

                        if os.path.exists(predefined_file):
                            with open(predefined_file, 'r', encoding='utf-8') as f:
                                lines = [line.strip()
                                         for line in f.readlines() if line.strip()]
                            classes_count = len(lines)
                            self.selected_classes_count_label.setText(
                                f"{classes_count} 个类别")
                            self.selected_classes_count_label.setStyleSheet(
                                "color: #27ae60; padding: 5px; border: 1px solid #27ae60; border-radius: 3px; background-color: #d5f4e6;")
                        else:
                            self.selected_classes_count_label.setText(
                                "预设类别文件不存在")
                            self.selected_classes_count_label.setStyleSheet(
                                "color: #e74c3c; padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; background-color: #fadbd8;")
                    except Exception as e:
                        self.selected_classes_count_label.setText(
                            f"读取失败: {str(e)}")
                        self.selected_classes_count_label.setStyleSheet(
                            "color: #e74c3c; padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; background-color: #fadbd8;")

                elif text == "使用类别配置文件":
                    # 读取类别配置文件
                    try:
                        import sys
                        import os
                        sys.path.insert(0, os.path.join(
                            os.path.dirname(__file__), '..'))
                        from libs.class_manager import ClassConfigManager

                        manager = ClassConfigManager("configs")
                        config = manager.load_class_config()
                        classes = config.get('classes', [])
                        classes_count = len(classes)

                        if classes_count > 0:
                            self.selected_classes_count_label.setText(
                                f"{classes_count} 个类别")
                            self.selected_classes_count_label.setStyleSheet(
                                "color: #27ae60; padding: 5px; border: 1px solid #27ae60; border-radius: 3px; background-color: #d5f4e6;")
                        else:
                            self.selected_classes_count_label.setText(
                                "类别配置文件为空")
                            self.selected_classes_count_label.setStyleSheet(
                                "color: #f39c12; padding: 5px; border: 1px solid #f39c12; border-radius: 3px; background-color: #fef9e7;")
                    except Exception as e:
                        self.selected_classes_count_label.setText(
                            f"读取失败: {str(e)}")
                        self.selected_classes_count_label.setStyleSheet(
                            "color: #e74c3c; padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; background-color: #fadbd8;")

                else:
                    self.selected_classes_count_label.setText("未知类别源")
                    self.selected_classes_count_label.setStyleSheet(
                        "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;")

        except Exception as e:
            logger.error(f"处理类别源改变失败: {str(e)}")

    def _get_classes_from_source(self, source):
        """根据类别源获取类别列表"""
        try:
            if source == "使用当前标注类别":
                # 从父窗口获取标注历史
                parent_window = self.parent()
                while parent_window and not hasattr(parent_window, 'label_hist'):
                    parent_window = parent_window.parent()

                if parent_window and hasattr(parent_window, 'label_hist'):
                    return list(parent_window.label_hist)
                else:
                    return []

            elif source == "使用预设类别文件":
                # 读取预设类别文件
                import os
                from labelImg import get_persistent_predefined_classes_path
                predefined_file = get_persistent_predefined_classes_path()

                if os.path.exists(predefined_file):
                    with open(predefined_file, 'r', encoding='utf-8') as f:
                        lines = [line.strip()
                                 for line in f.readlines() if line.strip()]
                    return lines
                else:
                    return []

            elif source == "使用类别配置文件":
                # 读取类别配置文件
                import sys
                import os
                sys.path.insert(0, os.path.join(
                    os.path.dirname(__file__), '..'))
                from libs.class_manager import ClassConfigManager

                manager = ClassConfigManager("configs")
                config = manager.load_class_config()
                return config.get('classes', [])

            else:
                return []

        except Exception as e:
            logger.error(f"获取类别列表失败: {str(e)}")
            return []

    def _update_class_config_from_source(self, source, classes):
        """根据类别源更新类别配置文件"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from libs.class_manager import ClassConfigManager
            from datetime import datetime

            manager = ClassConfigManager("configs")
            config = manager.load_class_config()

            # 更新类别列表
            config['classes'] = classes
            config['updated_at'] = datetime.now().isoformat()
            config['description'] = f"从{source}更新的类别配置 - 确保YOLO训练时类别顺序一致"

            # 更新类别元数据
            config['class_metadata'] = {}
            for idx, class_name in enumerate(classes):
                config['class_metadata'][class_name] = {
                    'description': f"从{source}导入的类别",
                    'added_at': datetime.now().isoformat(),
                    'usage_count': 0,
                    'original_id': idx,
                    'source': source
                }

            # 保存配置
            manager.class_config = config
            success = manager.save_class_config()

            if success:
                logger.info(f"✅ 成功更新类别配置: {len(classes)} 个类别")
                return True
            else:
                logger.error("❌ 保存类别配置失败")
                return False

        except Exception as e:
            logger.error(f"更新类别配置失败: {str(e)}")
            return False

    def _check_existing_dataset_info(self):
        """检查现有数据集信息并更新显示"""
        try:
            from libs.pascal_to_yolo_converter import PascalToYOLOConverter
            import os

            # 获取配置参数
            target_dir = self.output_dir_edit.text() if hasattr(
                self, 'output_dir_edit') else "./datasets"
            dataset_name = self.dataset_name_edit.text() if hasattr(
                self, 'dataset_name_edit') else "training_dataset"

            # 创建临时转换器实例来检查现有文件
            temp_converter = PascalToYOLOConverter(
                source_dir=".",  # 临时值
                target_dir=target_dir,
                dataset_name=dataset_name
            )

            # 获取现有文件信息
            existing_info = temp_converter.get_existing_files_info()

            # 更新显示
            if hasattr(self, 'existing_data_info_label'):
                if existing_info['dataset_exists'] and existing_info['total_files'] > 0:
                    info_text = (
                        f"发现 {existing_info['total_files']} 个现有文件:\n"
                        f"训练图片: {existing_info['train_images']}, "
                        f"验证图片: {existing_info['val_images']}\n"
                        f"训练标签: {existing_info['train_labels']}, "
                        f"验证标签: {existing_info['val_labels']}"
                    )
                    self.existing_data_info_label.setText(info_text)
                    self.existing_data_info_label.setStyleSheet(
                        "color: #e67e22; padding: 5px; border: 1px solid #e67e22; border-radius: 3px; background-color: #fef5e7;"
                    )

                    # 如果有现有文件，建议用户清空
                    if hasattr(self, 'clean_existing_checkbox'):
                        self.clean_existing_checkbox.setChecked(True)
                else:
                    self.existing_data_info_label.setText("目标目录为空，无现有文件")
                    self.existing_data_info_label.setStyleSheet(
                        "color: #27ae60; padding: 5px; border: 1px solid #27ae60; border-radius: 3px; background-color: #d5f4e6;"
                    )

        except Exception as e:
            logger.error(f"检查现有数据集信息失败: {str(e)}")
            if hasattr(self, 'existing_data_info_label'):
                self.existing_data_info_label.setText("检查现有文件失败")
                self.existing_data_info_label.setStyleSheet(
                    "color: #e74c3c; padding: 5px; border: 1px solid #e74c3c; border-radius: 3px; background-color: #fadbd8;"
                )

    def on_data_path_changed(self):
        """数据路径改变时的处理"""
        try:
            # 路径改变时重置统计信息
            if hasattr(self, 'stats_images_label'):
                self.stats_images_label.setText("未扫描")
            if hasattr(self, 'stats_labels_label'):
                self.stats_labels_label.setText("未扫描")
            if hasattr(self, 'stats_classes_label'):
                self.stats_classes_label.setText("未扫描")
            if hasattr(self, 'stats_train_label'):
                self.stats_train_label.setText("未计算")
            if hasattr(self, 'stats_val_label'):
                self.stats_val_label.setText("未计算")
        except Exception as e:
            logger.error(f"处理数据路径改变失败: {str(e)}")

    def show_classes_info_in_training(self):
        """在训练对话框中显示类别信息"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            # 获取当前选择的类别源
            source = self.classes_source_combo.currentText()

            if source == "使用当前标注类别":
                # 从父窗口获取标注历史
                parent_window = self.parent()
                while parent_window and not hasattr(parent_window, 'label_hist'):
                    parent_window = parent_window.parent()

                if parent_window and hasattr(parent_window, 'label_hist'):
                    classes = parent_window.label_hist
                    classes_text = "\n".join(
                        [f"{i}: {cls}" for i, cls in enumerate(classes)])
                    QMessageBox.information(
                        self, "当前标注类别", f"类别列表:\n\n{classes_text}")
                else:
                    QMessageBox.warning(self, "提示", "未找到标注类别信息")

            elif source == "使用预设类别文件":
                # 显示预设类别文件内容
                try:
                    # 获取正确的预设类别文件路径
                    import os
                    from labelImg import get_persistent_predefined_classes_path
                    predefined_file = get_persistent_predefined_classes_path()

                    if os.path.exists(predefined_file):
                        with open(predefined_file, 'r', encoding='utf-8') as f:
                            classes_text = f.read()
                        QMessageBox.information(
                            self, "预设类别", f"预设类别:\n\n{classes_text}")
                    else:
                        QMessageBox.warning(
                            self, "提示", f"未找到预设类别文件: {predefined_file}")
                except Exception as e:
                    QMessageBox.warning(self, "提示", f"读取预设类别文件失败: {str(e)}")

            elif source == "使用类别配置文件":
                # 显示类别配置文件内容
                try:
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(
                        os.path.dirname(__file__), '..'))
                    from libs.class_manager import ClassConfigManager

                    manager = ClassConfigManager("configs")
                    config = manager.load_class_config()
                    classes = config.get('classes', [])

                    if classes:
                        classes_text = "\n".join(
                            [f"{i}: {cls}" for i, cls in enumerate(classes)])
                        QMessageBox.information(
                            self, "类别配置文件", f"类别列表:\n\n{classes_text}")
                    else:
                        QMessageBox.warning(self, "提示", "类别配置文件为空")
                except Exception as e:
                    QMessageBox.warning(self, "提示", f"读取类别配置文件失败: {str(e)}")

            else:
                QMessageBox.information(self, "提示", "请先配置自定义类别")

        except Exception as e:
            logger.error(f"显示类别信息失败: {str(e)}")

    def validate_training_config(self, dialog):
        """验证训练配置"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            import os

            self._safe_append_data_log("🔍 开始验证训练配置...")
            errors = []

            # 检查data.yaml配置文件
            config_path = getattr(self, 'dataset_config_edit', None)
            if not config_path or not config_path.text().strip():
                error_msg = "请选择data.yaml配置文件"
                errors.append(error_msg)
                self._safe_append_data_log(f"❌ {error_msg}")
            else:
                yaml_path = config_path.text().strip()
                self._safe_append_data_log(f"📄 检查配置文件: {yaml_path}")

                if not os.path.exists(yaml_path):
                    error_msg = "data.yaml配置文件不存在"
                    errors.append(error_msg)
                    self._safe_append_data_log(f"❌ {error_msg}")
                else:
                    self._safe_append_data_log("✅ 配置文件存在，开始验证内容...")

                    # 验证配置文件内容
                    try:
                        import yaml
                        with open(yaml_path, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)

                        self._safe_append_data_log(f"📋 配置文件内容: {config}")

                        if 'names' not in config:
                            error_msg = "配置文件中缺少类别信息"
                            errors.append(error_msg)
                            self._safe_append_data_log(f"❌ {error_msg}")
                        elif len(config['names']) == 0:
                            error_msg = "配置文件中没有定义任何类别"
                            errors.append(error_msg)
                            self._safe_append_data_log(f"❌ {error_msg}")
                        else:
                            self._safe_append_data_log(
                                f"✅ 类别信息正常，共 {len(config['names'])} 个类别")

                        if 'train' not in config:
                            error_msg = "配置文件中缺少训练集路径"
                            errors.append(error_msg)
                            self._safe_append_data_log(f"❌ {error_msg}")
                        else:
                            self._safe_append_data_log(
                                f"✅ 训练集路径: {config['train']}")

                        if 'val' not in config:
                            error_msg = "配置文件中缺少验证集路径"
                            errors.append(error_msg)
                            self._safe_append_data_log(f"❌ {error_msg}")
                        else:
                            self._safe_append_data_log(
                                f"✅ 验证集路径: {config['val']}")

                        # 验证实际路径是否存在
                        if 'path' in config and config['path']:
                            base_path = config['path']
                            config_dir = os.path.dirname(yaml_path)

                            if not os.path.isabs(base_path):
                                if base_path == '.':
                                    # 如果是当前目录，直接使用配置文件目录
                                    base_path = config_dir
                                    self._safe_append_data_log(
                                        f"🔗 使用配置文件目录作为基础路径")
                                elif base_path.startswith('datasets/'):
                                    # 如果是相对于项目根目录的datasets路径，检查是否存在重复拼接
                                    # 检查config_dir是否已经包含了base_path
                                    config_dir_normalized = os.path.normpath(
                                        config_dir)
                                    base_path_normalized = os.path.normpath(
                                        base_path)

                                    if config_dir_normalized.endswith(base_path_normalized.replace('/', os.sep)):
                                        # 如果配置文件目录已经包含了path路径，直接使用配置文件目录
                                        base_path = config_dir
                                        self._safe_append_data_log(
                                            f"🔧 检测到路径重复，使用配置文件目录: {config_dir}")
                                    else:
                                        # 否则相对于项目根目录解析
                                        project_root = os.getcwd()
                                        base_path = os.path.join(
                                            project_root, base_path)
                                        self._safe_append_data_log(
                                            f"🔗 相对于项目根目录解析: {base_path}")
                                else:
                                    # 其他相对路径正常拼接
                                    base_path = os.path.join(
                                        config_dir, base_path)
                                    self._safe_append_data_log(
                                        f"🔗 相对于配置文件目录解析: {base_path}")

                            base_path = os.path.abspath(base_path)
                            self._safe_append_data_log(
                                f"📂 数据集基础路径: {base_path}")

                            if 'train' in config:
                                train_path = os.path.join(
                                    base_path, config['train'])
                                if os.path.exists(train_path):
                                    self._safe_append_data_log(
                                        f"✅ 训练集路径存在: {train_path}")
                                else:
                                    error_msg = f"训练集路径不存在: {train_path}"
                                    errors.append(error_msg)
                                    self._safe_append_data_log(
                                        f"❌ {error_msg}")

                            if 'val' in config:
                                val_path = os.path.join(
                                    base_path, config['val'])
                                if os.path.exists(val_path):
                                    self._safe_append_data_log(
                                        f"✅ 验证集路径存在: {val_path}")
                                else:
                                    error_msg = f"验证集路径不存在: {val_path}"
                                    errors.append(error_msg)
                                    self._safe_append_data_log(
                                        f"❌ {error_msg}")

                    except Exception as e:
                        error_msg = f"配置文件格式错误: {str(e)}"
                        errors.append(error_msg)
                        self._safe_append_data_log(f"❌ {error_msg}")

            if errors:
                self._safe_append_data_log(f"❌ 验证失败，发现 {len(errors)} 个错误")
                for error in errors:
                    self._safe_append_data_log(f"   • {error}")
                QMessageBox.warning(dialog, "配置验证失败", "\n".join(errors))
                return False
            else:
                self._safe_append_data_log("✅ 训练配置验证通过！")
                QMessageBox.information(dialog, "配置验证成功", "训练配置验证通过，可以开始训练！")
                return True

        except Exception as e:
            error_msg = f"验证训练配置失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_data_log(f"❌ {error_msg}")
            return False

    def start_complete_training(self, dialog):
        """开始完整训练"""
        try:
            # 先验证配置
            if not self.validate_training_config(dialog):
                return

            from PyQt5.QtWidgets import QMessageBox

            # 收集训练配置
            self._safe_append_log("📋 收集训练配置参数...")

            config_path = getattr(self, 'dataset_config_edit', None)
            yaml_path = config_path.text().strip() if config_path else ""

            self._safe_append_log(f"📁 数据集配置路径: {yaml_path}")
            self._safe_append_log(f"📂 当前工作目录: {os.getcwd()}")

            # 检查路径是否为绝对路径
            if yaml_path:
                if os.path.isabs(yaml_path):
                    self._safe_append_log("✅ 使用绝对路径")
                else:
                    abs_path = os.path.abspath(yaml_path)
                    self._safe_append_log(f"🔗 相对路径转换为绝对路径: {abs_path}")

            # 获取选择的模型
            model_info = self.get_selected_training_model()
            if not model_info:
                self._safe_append_log("❌ 未选择有效的训练模型")
                QMessageBox.warning(self, "配置错误", "请选择有效的训练模型")
                return

            config = {
                'dataset_config': yaml_path,
                'epochs': self.epochs_spin.value(),
                'batch_size': self.batch_spin.value(),
                'learning_rate': self.lr_spin.value(),
                'model_type': model_info['type'],
                'model_path': model_info['path'],
                'model_name': model_info['name'],
                'device': self.device_combo.currentText()
            }

            self._safe_append_log("📊 训练配置参数:")
            for key, value in config.items():
                self._safe_append_log(f"   {key}: {value}")

            # 显示配置摘要
            summary = f"""训练配置摘要:

📁 数据配置:
   配置文件: {config['dataset_config']}

🤖 模型配置:
   模型类型: {config['model_type']}
   模型名称: {config['model_name']}
   模型路径: {config['model_path']}

⚙️ 训练参数:
   训练轮数: {config['epochs']}
   批次大小: {config['batch_size']}
   学习率: {config['learning_rate']}
   训练设备: {config['device']}

确认开始训练吗？"""

            reply = QMessageBox.question(dialog, "确认训练配置", summary,
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                # 不关闭配置对话框，而是切换到训练监控标签页
                self._switch_to_training_monitor()

                # 标准化设备字符串
                device_str = str(config['device']).lower()
                if "gpu" in device_str or "cuda" in device_str:
                    device = 'cuda'
                else:
                    device = 'cpu'

                # 创建训练配置
                training_config = TrainingConfig(
                    dataset_config=config['dataset_config'],
                    epochs=config['epochs'],
                    batch_size=config['batch_size'],
                    learning_rate=config['learning_rate'],
                    model_type=config['model_type'],
                    model_path=config['model_path'],
                    model_name=config['model_name'],
                    device=device,
                    output_dir=os.path.join(os.getcwd(), 'runs', 'train')
                )

                # 保存对话框引用，以便训练完成后关闭
                self.training_dialog = dialog

                # 启动真实训练
                self.trainer.start_training(training_config)

        except Exception as e:
            logger.error(f"开始完整训练失败: {str(e)}")

    def _switch_to_training_monitor(self):
        """切换到训练监控标签页"""
        try:
            # 查找训练对话框中的标签页控件
            if hasattr(self, 'training_tab_widget') and self.training_tab_widget is not None:
                try:
                    # 切换到训练监控标签页（索引为2）
                    self.training_tab_widget.setCurrentIndex(2)
                    self._safe_append_log("🔄 已切换到训练监控界面")
                except RuntimeError:
                    pass
        except Exception as e:
            logger.error(f"切换到训练监控标签页失败: {str(e)}")

    def stop_training(self):
        """停止训练"""
        try:
            if hasattr(self, 'trainer') and self.trainer:
                self.trainer.stop_training()
                self._safe_append_log("🛑 用户请求停止训练...")

                # 更新按钮状态
                if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                    try:
                        self.stop_training_btn.setEnabled(False)
                    except RuntimeError:
                        pass
            else:
                self._safe_append_log("❌ 训练器未初始化，无法停止训练")
        except Exception as e:
            logger.error(f"停止训练失败: {str(e)}")

    def auto_configure_training_dataset(self):
        """一键配置训练数据集"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox, QProgressBar, QTextEdit

            # 创建一键配置对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("🚀 一键配置训练数据集")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("🚀 一键配置训练数据集")
            title_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)

            # 说明文本
            info_label = QLabel("""
此功能将自动调用labelImg的YOLO导出功能，生成标准的训练数据集，
然后自动配置训练路径。这样可以确保训练数据与您的标注完全一致。

工作流程：
1. 检查当前工作目录是否有标注文件
2. 调用YOLO导出功能生成训练数据集
3. 自动配置训练对话框的路径设置
4. 返回训练配置界面继续设置参数
            """)
            info_label.setWordWrap(True)
            info_label.setStyleSheet(
                "padding: 10px; background-color: #f0f8ff; border-radius: 5px;")
            layout.addWidget(info_label)

            # 配置选项
            config_group = QGroupBox("📁 导出配置")
            config_layout = QFormLayout(config_group)

            # 数据集名称
            self.dataset_name_edit = QLineEdit()
            self.dataset_name_edit.setText("training_dataset")
            self.dataset_name_edit.setPlaceholderText("输入数据集名称")
            config_layout.addRow("数据集名称:", self.dataset_name_edit)

            # 训练集比例
            self.train_ratio_spin = QSpinBox()
            self.train_ratio_spin.setRange(60, 90)
            self.train_ratio_spin.setValue(80)
            self.train_ratio_spin.setSuffix("%")
            config_layout.addRow("训练集比例:", self.train_ratio_spin)

            # 输出目录
            output_layout = QHBoxLayout()
            self.output_dir_edit = QLineEdit()
            self.output_dir_edit.setText("./datasets")
            self.output_dir_edit.setPlaceholderText("选择输出目录")
            output_layout.addWidget(self.output_dir_edit)

            browse_output_btn = QPushButton("📁")
            browse_output_btn.setMaximumWidth(40)
            browse_output_btn.clicked.connect(
                lambda: self.browse_folder(self.output_dir_edit, "选择输出目录"))
            output_layout.addWidget(browse_output_btn)
            config_layout.addRow("输出目录:", output_layout)

            # 是否打乱数据
            self.shuffle_checkbox = QCheckBox()
            self.shuffle_checkbox.setChecked(True)
            config_layout.addRow("随机打乱数据:", self.shuffle_checkbox)

            layout.addWidget(config_group)

            # 数据处理选项组
            data_options_group = QGroupBox("🗂️ 数据处理选项")
            data_options_layout = QFormLayout(data_options_group)

            # 清空现有数据选项
            self.clean_existing_checkbox = QCheckBox()
            self.clean_existing_checkbox.setChecked(True)  # 默认清空，避免数据污染
            self.clean_existing_checkbox.setToolTip(
                "清空目标文件夹中的现有文件，避免数据累积和污染。\n"
                "建议勾选此选项以确保数据的纯净性。"
            )
            data_options_layout.addRow("清空现有数据:", self.clean_existing_checkbox)

            # 备份现有数据选项
            self.backup_existing_checkbox = QCheckBox()
            self.backup_existing_checkbox.setChecked(False)  # 默认不备份，节省空间
            self.backup_existing_checkbox.setToolTip(
                "在清空前备份现有数据，以防需要恢复。\n"
                "备份文件将保存在同级目录中。"
            )
            data_options_layout.addRow(
                "备份现有数据:", self.backup_existing_checkbox)

            # 显示现有数据信息
            self.existing_data_info_label = QLabel("点击'检查数据'查看现有文件信息")
            self.existing_data_info_label.setStyleSheet(
                "color: #7f8c8d; padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #f8f9fa;"
            )
            data_options_layout.addRow("现有数据:", self.existing_data_info_label)

            layout.addWidget(data_options_group)

            # 进度显示
            self.auto_progress_bar = QProgressBar()
            self.auto_progress_bar.setVisible(False)
            layout.addWidget(self.auto_progress_bar)

            self.auto_log_text = QTextEdit()
            self.auto_log_text.setMaximumHeight(150)
            self.auto_log_text.setVisible(False)
            layout.addWidget(self.auto_log_text)

            # 按钮
            buttons_layout = QHBoxLayout()

            # 检查数据按钮
            check_btn = QPushButton("🔍 检查数据")
            check_btn.clicked.connect(
                lambda: self.check_current_data_for_export(dialog))
            buttons_layout.addWidget(check_btn)

            buttons_layout.addStretch()

            # 开始配置按钮
            self.start_config_btn = QPushButton("🚀 开始配置")
            self.start_config_btn.clicked.connect(
                lambda: self.execute_auto_configuration(dialog))
            buttons_layout.addWidget(self.start_config_btn)

            # 取消按钮
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)

            layout.addLayout(buttons_layout)

            # 自动检查当前数据
            self.check_current_data_for_export(dialog, silent=True)

            dialog.exec_()

        except Exception as e:
            logger.error(f"一键配置训练数据集失败: {str(e)}")

    def check_current_data_for_export(self, dialog, silent=False):
        """检查当前数据是否可以导出"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            import os

            # 获取当前工作目录
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'last_open_dir'):
                parent_window = parent_window.parent()

            if not parent_window or not hasattr(parent_window, 'last_open_dir'):
                if not silent:
                    QMessageBox.warning(dialog, "检查失败", "未找到当前工作目录信息")
                return False

            current_dir = parent_window.last_open_dir
            if not current_dir or not os.path.exists(current_dir):
                if not silent:
                    QMessageBox.warning(dialog, "检查失败", "当前工作目录不存在")
                return False

            # 检查目标数据集的现有文件信息
            self._check_existing_dataset_info()

            # 检查是否有XML标注文件
            xml_files = [f for f in os.listdir(
                current_dir) if f.lower().endswith('.xml')]
            if not xml_files:
                if not silent:
                    QMessageBox.warning(
                        dialog, "检查失败", "当前目录中没有找到XML标注文件\n请确保已经完成标注工作")
                return False

            # 检查是否有对应的图片文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            image_files = [f for f in os.listdir(current_dir)
                           if any(f.lower().endswith(ext) for ext in image_extensions)]

            if not image_files:
                if not silent:
                    QMessageBox.warning(dialog, "检查失败", "当前目录中没有找到图片文件")
                return False

            # 检查图片和标注的对应关系
            xml_basenames = {os.path.splitext(f)[0] for f in xml_files}
            image_basenames = {os.path.splitext(f)[0] for f in image_files}

            matched_files = xml_basenames & image_basenames
            if len(matched_files) == 0:
                if not silent:
                    QMessageBox.warning(dialog, "检查失败", "图片文件和标注文件名称不匹配")
                return False

            # 显示检查结果
            if not silent:
                QMessageBox.information(dialog, "检查成功",
                                        f"数据检查通过！\n\n"
                                        f"📁 工作目录: {current_dir}\n"
                                        f"📸 图片文件: {len(image_files)} 个\n"
                                        f"🏷️ 标注文件: {len(xml_files)} 个\n"
                                        f"✅ 匹配文件: {len(matched_files)} 对\n\n"
                                        f"可以开始配置训练数据集！")

            return True

        except Exception as e:
            logger.error(f"检查当前数据失败: {str(e)}")
            if not silent:
                QMessageBox.critical(dialog, "检查失败", f"检查过程出错: {str(e)}")
            return False

    def execute_auto_configuration(self, dialog):
        """执行自动配置"""
        try:
            # 先检查数据
            if not self.check_current_data_for_export(dialog, silent=True):
                return

            from PyQt5.QtWidgets import QMessageBox

            # 确认开始配置
            reply = QMessageBox.question(dialog, "确认配置",
                                         "即将开始自动配置训练数据集：\n\n"
                                         f"1. 导出YOLO格式数据集\n"
                                         f"2. 数据集名称: {self.dataset_name_edit.text()}\n"
                                         f"3. 训练集比例: {self.train_ratio_spin.value()}%\n"
                                         f"4. 输出目录: {self.output_dir_edit.text()}\n"
                                         f"5. 训练集路径: images/train (固定)\n"
                                         f"6. 验证集路径: images/val (固定)\n\n"
                                         "确认开始吗？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply != QMessageBox.Yes:
                return

            # 禁用按钮，显示进度
            self.start_config_btn.setEnabled(False)
            self.auto_progress_bar.setVisible(True)
            self.auto_log_text.setVisible(True)
            self.auto_log_text.clear()

            # 调用YOLO导出功能
            self.call_yolo_export_and_configure(dialog)

        except Exception as e:
            logger.error(f"执行自动配置失败: {str(e)}")

    def call_yolo_export_and_configure(self, dialog):
        """调用YOLO导出功能并配置训练路径"""
        try:
            import os
            from PyQt5.QtWidgets import QMessageBox

            # 获取当前工作目录
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'last_open_dir'):
                parent_window = parent_window.parent()

            if not parent_window:
                QMessageBox.critical(dialog, "错误", "无法获取当前工作目录")
                return

            source_dir = parent_window.last_open_dir
            target_dir = self.output_dir_edit.text()
            dataset_name = self.dataset_name_edit.text()
            train_ratio = self.train_ratio_spin.value() / 100.0

            self._safe_append_auto_log("🚀 开始自动配置训练数据集...")
            self._safe_append_auto_log(f"📁 源目录: {source_dir}")
            self._safe_append_auto_log(f"📁 输出目录: {target_dir}")
            self._safe_append_auto_log(f"📊 数据集名称: {dataset_name}")
            self._safe_append_auto_log(f"📊 训练集比例: {train_ratio*100:.0f}%")

            # 获取用户选择的类别源
            selected_classes_source = None
            selected_classes = []
            if hasattr(self, 'classes_source_combo'):
                selected_classes_source = self.classes_source_combo.currentText()
                self._safe_append_auto_log(
                    f"🏷️ 类别源: {selected_classes_source}")

                # 根据类别源获取类别列表
                selected_classes = self._get_classes_from_source(
                    selected_classes_source)
                if selected_classes:
                    self._safe_append_auto_log(f"🏷️ 类别列表: {selected_classes}")
                    self._safe_append_auto_log(
                        f"🏷️ 类别数量: {len(selected_classes)}")
                else:
                    self._safe_append_auto_log("⚠️ 未能获取类别列表，将使用动态发现模式")

            # 创建输出目录
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                self._safe_append_auto_log(f"📁 创建输出目录: {target_dir}")

            # 导入并使用YOLO转换器
            try:
                from libs.pascal_to_yolo_converter import PascalToYOLOConverter

                self._safe_append_auto_log("📦 初始化YOLO转换器...")

                # 根据类别源决定转换器配置
                if selected_classes and selected_classes_source != "使用类别配置文件":
                    # 使用用户选择的类别源，先更新类别配置文件
                    self._safe_append_auto_log("🔄 根据选择的类别源更新配置...")
                    self._update_class_config_from_source(
                        selected_classes_source, selected_classes)

                # 创建转换器 - 使用固定类别配置
                converter = PascalToYOLOConverter(
                    source_dir=source_dir,
                    target_dir=target_dir,
                    dataset_name=dataset_name,
                    train_ratio=train_ratio,
                    use_class_config=True,      # 启用固定类别配置
                    class_config_dir="configs"  # 配置文件目录
                )

                # 进度回调函数
                def progress_callback(current, total, message):
                    self.auto_progress_bar.setValue(current)
                    self._safe_append_auto_log(f"[{current:3d}%] {message}")
                    QApplication.processEvents()  # 更新UI

                self._safe_append_auto_log("🔄 开始转换...")
                self.auto_progress_bar.setValue(0)

                # 获取用户选择的清空和备份选项
                clean_existing = self.clean_existing_checkbox.isChecked(
                ) if hasattr(self, 'clean_existing_checkbox') else False
                backup_existing = self.backup_existing_checkbox.isChecked(
                ) if hasattr(self, 'backup_existing_checkbox') else False

                if clean_existing:
                    self._safe_append_auto_log("🗑️ 将清空现有数据文件")
                if backup_existing:
                    self._safe_append_auto_log("📋 将备份现有数据文件")

                # 执行转换
                success, message = converter.convert(
                    progress_callback=progress_callback,
                    clean_existing=clean_existing,
                    backup_existing=backup_existing
                )

                if success:
                    self._safe_append_auto_log("✅ YOLO数据集导出成功!")
                    self._safe_append_auto_log(f"📊 {message}")

                    # 自动配置data.yaml路径
                    dataset_path = os.path.join(target_dir, dataset_name)
                    data_yaml_path = os.path.join(dataset_path, "data.yaml")

                    self._safe_append_auto_log("🔧 自动配置data.yaml路径...")

                    # 配置训练对话框的data.yaml路径
                    if hasattr(self, 'dataset_config_edit'):
                        self.dataset_config_edit.setText(data_yaml_path)
                        self._safe_append_auto_log(
                            f"📄 数据集配置: {data_yaml_path}")

                        # 自动加载配置文件
                        self.load_dataset_config(data_yaml_path)

                    # 自动扫描数据集
                    self._safe_append_auto_log("🔍 扫描生成的数据集...")
                    self.scan_generated_dataset(dataset_path)

                    self._safe_append_auto_log("🎉 一键配置完成!")

                    # 显示成功消息
                    QMessageBox.information(dialog, "配置成功",
                                            f"训练数据集配置完成！\n\n"
                                            f"📁 数据集路径: {dataset_path}\n"
                                            f"📄 配置文件: {data_yaml_path}\n"
                                            f"📊 数据划分: {train_ratio*100:.0f}% 训练, {(1-train_ratio)*100:.0f}% 验证\n"
                                            f"🚂 训练集路径: images/train (固定)\n"
                                            f"✅ 验证集路径: images/val (固定)\n\n"
                                            f"现在可以关闭此对话框，继续配置训练参数！")

                    # 重新启用按钮
                    self.start_config_btn.setEnabled(True)

                else:
                    self._safe_append_auto_log(f"❌ 导出失败: {message}")
                    QMessageBox.critical(
                        dialog, "导出失败", f"YOLO数据集导出失败:\n\n{message}")
                    self.start_config_btn.setEnabled(True)

            except ImportError as e:
                self._safe_append_auto_log(f"❌ 导入转换器失败: {str(e)}")
                QMessageBox.critical(
                    dialog, "导入失败", f"无法导入YOLO转换器:\n\n{str(e)}\n\n请确保相关模块已正确安装。")
                self.start_config_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"调用YOLO导出功能失败: {str(e)}")
            self._safe_append_auto_log(f"❌ 配置失败: {str(e)}")
            QMessageBox.critical(dialog, "配置失败", f"自动配置过程出错:\n\n{str(e)}")
            if hasattr(self, 'start_config_btn'):
                self.start_config_btn.setEnabled(True)

    def show_class_config_dialog(self):
        """显示类别配置对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QTabWidget, QTextEdit, QMessageBox

            dialog = QDialog(self)
            dialog.setWindowTitle("类别配置管理")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("⚙️ 固定类别配置管理")
            title_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 5px;")
            layout.addWidget(title_label)

            # 说明文本
            info_label = QLabel("管理YOLO训练中的固定类别顺序，确保每次训练的类别ID映射都相同。")
            info_label.setWordWrap(True)
            info_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
            layout.addWidget(info_label)

            # 标签页
            tab_widget = QTabWidget()

            # 当前配置标签页
            current_tab = QListWidget()
            try:
                import sys
                import os
                sys.path.insert(0, os.path.join(
                    os.path.dirname(__file__), '..'))
                from libs.class_manager import ClassConfigManager

                manager = ClassConfigManager("configs")
                config = manager.load_class_config()
                classes = config.get('classes', [])

                if classes:
                    for i, class_name in enumerate(classes):
                        item_text = f"{i}: {class_name}"
                        current_tab.addItem(item_text)
                else:
                    current_tab.addItem("未找到类别配置")

            except Exception as e:
                current_tab.addItem(f"加载配置失败: {e}")

            tab_widget.addTab(current_tab, f"当前配置 ({current_tab.count()})")

            # 数据集分析标签页
            analysis_tab = QTextEdit()
            analysis_tab.setReadOnly(True)
            analysis_tab.setPlainText("点击'分析数据集'按钮来分析现有数据集的类别使用情况...")
            tab_widget.addTab(analysis_tab, "数据集分析")

            layout.addWidget(tab_widget)

            # 按钮布局
            buttons_layout = QHBoxLayout()

            # 分析数据集按钮
            analyze_btn = QPushButton("🔍 分析数据集")
            analyze_btn.clicked.connect(
                lambda: self.analyze_dataset_classes(analysis_tab))
            buttons_layout.addWidget(analyze_btn)

            # 验证一致性按钮
            validate_btn = QPushButton("✅ 验证一致性")
            validate_btn.clicked.connect(
                lambda: self.validate_class_consistency())
            buttons_layout.addWidget(validate_btn)

            buttons_layout.addStretch()

            # 关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示类别配置对话框失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"显示类别配置对话框失败:\n\n{str(e)}")

    def analyze_dataset_classes(self, text_widget):
        """分析数据集类别"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from libs.class_manager import ClassConfigManager

            manager = ClassConfigManager("configs")
            dataset_path = "datasets/training_dataset"

            if not os.path.exists(dataset_path):
                text_widget.setPlainText("❌ 数据集路径不存在: " + dataset_path)
                return

            text_widget.setPlainText("🔍 正在分析数据集...")
            QApplication.processEvents()

            analysis = manager.analyze_dataset_classes(dataset_path)

            if analysis:
                report_lines = [
                    "📊 数据集类别分析报告",
                    "=" * 40,
                    f"📂 数据集路径: {analysis['dataset_path']}",
                    f"📄 data.yaml存在: {'是' if analysis['data_yaml_path'] else '否'}",
                    f"📄 classes.txt存在: {'是' if analysis['classes_txt_path'] else '否'}",
                    "",
                    "🏷️ 类别信息:",
                    f"  YAML类别: {analysis['yaml_classes']}",
                    f"  TXT类别: {analysis['txt_classes']}",
                    f"  标签文件中的类别ID: {analysis['label_files_classes']}",
                    "",
                    "⚠️ 发现的问题:",
                ]

                if analysis['inconsistencies']:
                    for issue in analysis['inconsistencies']:
                        report_lines.append(f"  - {issue}")
                else:
                    report_lines.append("  无问题")

                report_lines.extend([
                    "",
                    "💡 建议:",
                ])

                for rec in analysis['recommendations']:
                    report_lines.append(f"  - {rec}")

                text_widget.setPlainText("\n".join(report_lines))
            else:
                text_widget.setPlainText("❌ 分析失败")

        except Exception as e:
            text_widget.setPlainText(f"❌ 分析过程中出现错误: {str(e)}")

    def validate_class_consistency(self):
        """验证类别一致性"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            import subprocess
            import os

            # 运行验证脚本
            script_path = "class_order_validator.py"
            if os.path.exists(script_path):
                QMessageBox.information(self, "验证中", "正在验证类别一致性，请查看控制台输出...")
                # 这里可以集成验证逻辑，或者提示用户查看控制台
            else:
                QMessageBox.warning(
                    self, "提示", "验证脚本不存在，请确保 class_order_validator.py 文件存在")

        except Exception as e:
            logger.error(f"验证类别一致性失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"验证失败:\n\n{str(e)}")

    def scan_generated_dataset(self, dataset_path):
        """扫描生成的数据集"""
        try:
            import os

            # 扫描训练集
            train_images_path = os.path.join(dataset_path, "images", "train")
            train_labels_path = os.path.join(dataset_path, "labels", "train")
            val_images_path = os.path.join(dataset_path, "images", "val")
            val_labels_path = os.path.join(dataset_path, "labels", "val")

            train_images = 0
            train_labels = 0
            val_images = 0
            val_labels = 0

            if os.path.exists(train_images_path):
                train_images = len([f for f in os.listdir(train_images_path)
                                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])

            if os.path.exists(train_labels_path):
                train_labels = len([f for f in os.listdir(train_labels_path)
                                    if f.lower().endswith('.txt')])

            if os.path.exists(val_images_path):
                val_images = len([f for f in os.listdir(val_images_path)
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])

            if os.path.exists(val_labels_path):
                val_labels = len([f for f in os.listdir(val_labels_path)
                                  if f.lower().endswith('.txt')])

            # 更新统计信息
            total_images = train_images + val_images
            total_labels = train_labels + val_labels

            if hasattr(self, 'stats_images_label'):
                self.stats_images_label.setText(f"{total_images} 张")
            if hasattr(self, 'stats_labels_label'):
                self.stats_labels_label.setText(f"{total_labels} 个")
            if hasattr(self, 'stats_train_label'):
                self.stats_train_label.setText(f"{train_images} 张")
            if hasattr(self, 'stats_val_label'):
                self.stats_val_label.setText(f"{val_images} 张")

            # 读取类别信息
            classes_file = os.path.join(dataset_path, "classes.txt")
            if os.path.exists(classes_file):
                with open(classes_file, 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f if line.strip()]
                if hasattr(self, 'stats_classes_label'):
                    self.stats_classes_label.setText(f"{len(classes)} 类")

                self._safe_append_auto_log(f"📊 扫描结果:")
                self._safe_append_auto_log(
                    f"   训练集: {train_images} 张图片, {train_labels} 个标注")
                self._safe_append_auto_log(
                    f"   验证集: {val_images} 张图片, {val_labels} 个标注")
                self._safe_append_auto_log(f"   类别数: {len(classes)} 类")
                self._safe_append_auto_log(f"   类别: {', '.join(classes)}")

        except Exception as e:
            logger.error(f"扫描生成的数据集失败: {str(e)}")
            self._safe_append_auto_log(f"⚠️ 扫描数据集时出错: {str(e)}")

    def browse_yaml_file(self, line_edit, title):
        """浏览YAML文件"""
        try:
            from PyQt5.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getOpenFileName(
                self, title, "", "YAML files (*.yaml *.yml);;All files (*.*)")
            if file_path:
                line_edit.setText(file_path)

        except Exception as e:
            logger.error(f"浏览YAML文件失败: {str(e)}")

    def on_dataset_config_changed(self):
        """数据集配置文件改变时的处理"""
        try:
            config_path = self.dataset_config_edit.text().strip()
            self._safe_append_data_log(f"📝 数据集配置文件路径改变: {config_path}")

            if config_path and os.path.exists(config_path):
                self._safe_append_data_log("✅ 配置文件存在，开始加载...")
                self.load_dataset_config(config_path)
            else:
                if config_path:
                    self._safe_append_data_log(f"❌ 配置文件不存在: {config_path}")
                else:
                    self._safe_append_data_log("⚠️ 配置文件路径为空")
                self.reset_dataset_config_display()

        except Exception as e:
            error_msg = f"处理数据集配置改变失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_data_log(f"❌ {error_msg}")

    def load_dataset_config(self, config_path):
        """加载数据集配置文件"""
        try:
            self._safe_append_log(f"📋 加载数据集配置文件: {config_path}")
            self._safe_append_data_log(f"📋 加载数据集配置文件: {config_path}")

            import yaml
            import os

            # 检查配置文件是否存在
            if not os.path.exists(config_path):
                error_msg = f"❌ 配置文件不存在: {config_path}"
                self._safe_append_log(error_msg)
                self._safe_append_data_log(error_msg)
                raise FileNotFoundError(error_msg)

            self._safe_append_data_log(f"✅ 配置文件存在，开始解析...")

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self._safe_append_log(f"📄 配置文件内容: {config}")
            self._safe_append_data_log(f"📄 配置文件内容: {config}")

            # 获取配置文件所在目录
            config_dir = os.path.dirname(config_path)
            config_dir_abs = os.path.abspath(config_dir)
            self._safe_append_log(f"📂 配置文件目录: {config_dir}")
            self._safe_append_data_log(f"📂 配置文件目录: {config_dir}")
            self._safe_append_data_log(f"📂 配置文件绝对目录: {config_dir_abs}")

            # 更新显示信息
            # 首先确定数据集基础路径
            if 'path' in config and config['path']:
                dataset_base_path = config['path']
                self._safe_append_log(f"🗂️ 原始path字段: {dataset_base_path}")
                self._safe_append_data_log(f"🗂️ 原始path字段: {dataset_base_path}")

                if not os.path.isabs(dataset_base_path):
                    if dataset_base_path == '.':
                        # 如果是当前目录，直接使用配置文件目录
                        dataset_base_path = config_dir_abs
                        self._safe_append_log("🔗 使用配置文件目录作为基础路径")
                        self._safe_append_data_log(
                            f"🔗 使用配置文件目录作为基础路径: {dataset_base_path}")
                    elif dataset_base_path.startswith('datasets/'):
                        # 如果是相对于项目根目录的datasets路径，使用项目根目录作为基础
                        project_root = os.getcwd()
                        dataset_base_path = os.path.join(
                            project_root, dataset_base_path)
                        dataset_base_path = os.path.abspath(dataset_base_path)
                        self._safe_append_log(
                            f"🔗 相对于项目根目录解析: {dataset_base_path}")
                        self._safe_append_data_log(
                            f"🔗 项目根目录: {project_root}")
                        self._safe_append_data_log(
                            f"🔗 相对于项目根目录解析: {dataset_base_path}")
                    else:
                        # 其他相对路径相对于配置文件目录拼接
                        dataset_base_path = os.path.join(
                            config_dir_abs, dataset_base_path)
                        dataset_base_path = os.path.abspath(dataset_base_path)
                        self._safe_append_log(
                            f"🔗 相对于配置文件目录解析: {dataset_base_path}")
                        self._safe_append_data_log(
                            f"🔗 相对于配置文件目录解析: {dataset_base_path}")
                else:
                    self._safe_append_data_log(
                        f"🔗 使用绝对路径: {dataset_base_path}")
            else:
                # 如果没有path字段，使用配置文件所在目录
                dataset_base_path = config_dir_abs
                self._safe_append_log("📁 使用配置文件目录作为基础路径")
                self._safe_append_data_log(
                    f"📁 使用配置文件目录作为基础路径: {dataset_base_path}")

            # 检查数据集基础路径是否存在
            if not os.path.exists(dataset_base_path):
                error_msg = f"❌ 数据集基础路径不存在: {dataset_base_path}"
                self._safe_append_log(error_msg)
                self._safe_append_data_log(error_msg)
            else:
                self._safe_append_data_log(f"✅ 数据集基础路径存在: {dataset_base_path}")

            # 显示数据集基础路径
            if hasattr(self, 'dataset_path_label'):
                self.dataset_path_label.setText(dataset_base_path)

            # 构建训练和验证路径
            if 'train' in config:
                train_relative = config['train']
                train_path = os.path.join(dataset_base_path, train_relative)
                train_path = os.path.abspath(train_path)
                self._safe_append_log(
                    f"🚂 训练路径: {train_relative} -> {train_path}")
                self._safe_append_data_log(
                    f"🚂 训练相对路径: {train_relative}")
                self._safe_append_data_log(
                    f"🚂 训练绝对路径: {train_path}")

                # 检查训练路径是否存在
                if os.path.exists(train_path):
                    self._safe_append_data_log(f"✅ 训练路径存在")
                    # 统计训练图片数量
                    try:
                        train_images = [f for f in os.listdir(train_path)
                                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                        self._safe_append_data_log(
                            f"📊 训练图片数量: {len(train_images)}")
                    except Exception as e:
                        self._safe_append_data_log(f"⚠️ 无法统计训练图片: {str(e)}")
                else:
                    self._safe_append_data_log(f"❌ 训练路径不存在: {train_path}")

                if hasattr(self, 'train_path_label'):
                    # 显示固定的相对路径，而不是绝对路径
                    self.train_path_label.setText(
                        f"{train_relative} (相对于数据集路径)")

            if 'val' in config:
                val_relative = config['val']
                val_path = os.path.join(dataset_base_path, val_relative)
                val_path = os.path.abspath(val_path)
                self._safe_append_log(f"✅ 验证路径: {val_relative} -> {val_path}")
                self._safe_append_data_log(
                    f"✅ 验证相对路径: {val_relative}")
                self._safe_append_data_log(
                    f"✅ 验证绝对路径: {val_path}")

                # 检查验证路径是否存在
                if os.path.exists(val_path):
                    self._safe_append_data_log(f"✅ 验证路径存在")
                    # 统计验证图片数量
                    try:
                        val_images = [f for f in os.listdir(val_path)
                                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                        self._safe_append_data_log(
                            f"📊 验证图片数量: {len(val_images)}")
                    except Exception as e:
                        self._safe_append_data_log(f"⚠️ 无法统计验证图片: {str(e)}")
                else:
                    self._safe_append_data_log(f"❌ 验证路径不存在: {val_path}")

                if hasattr(self, 'val_path_label'):
                    # 显示固定的相对路径，而不是绝对路径
                    self.val_path_label.setText(f"{val_relative} (相对于数据集路径)")

            # 显示类别信息
            if 'names' in config:
                names = config['names']
                if isinstance(names, dict):
                    # 字典格式: {0: 'class1', 1: 'class2'}
                    classes_list = [names[i] for i in sorted(names.keys())]
                elif isinstance(names, list):
                    # 列表格式: ['class1', 'class2']
                    classes_list = names
                else:
                    classes_list = []

                classes_text = f"{len(classes_list)} 类: {', '.join(classes_list[:5])}"
                if len(classes_list) > 5:
                    classes_text += f" 等..."
                self.classes_info_label.setText(classes_text)

            # 更新配置信息
            nc = config.get('nc', len(classes_list)
                            if 'names' in config else 0)
            self.config_info_label.setText(f"✅ 已加载配置文件 - {nc} 个类别")
            self.config_info_label.setStyleSheet(
                "color: #27ae60; font-style: italic; padding: 5px;")

            # 自动扫描数据集
            if hasattr(self, 'dataset_path_label') and self.dataset_path_label.text() != "从data.yaml配置文件中读取":
                self.scan_yaml_dataset(config, config_dir)

        except Exception as e:
            logger.error(f"加载数据集配置失败: {str(e)}")
            self.config_info_label.setText(f"❌ 配置文件加载失败: {str(e)}")
            self.config_info_label.setStyleSheet(
                "color: #e74c3c; font-style: italic; padding: 5px;")

    def reset_dataset_config_display(self):
        """重置数据集配置显示"""
        try:
            self.dataset_path_label.setText("从data.yaml配置文件中读取")
            self.train_path_label.setText("images/train (固定值)")
            self.val_path_label.setText("images/val (固定值)")
            self.classes_info_label.setText("从data.yaml配置文件中读取")
            self.config_info_label.setText("请选择或生成data.yaml配置文件")
            self.config_info_label.setStyleSheet(
                "color: #7f8c8d; font-style: italic; padding: 5px;")

        except Exception as e:
            logger.error(f"重置数据集配置显示失败: {str(e)}")

    def scan_yaml_dataset(self, config, config_dir):
        """扫描YAML配置的数据集"""
        try:
            import os

            # 获取路径
            dataset_path = config.get('path', '')
            train_path = config.get('train', '')
            val_path = config.get('val', '')

            if not os.path.isabs(dataset_path):
                dataset_path = os.path.join(config_dir, dataset_path)
            if not os.path.isabs(train_path):
                train_path = os.path.join(dataset_path, train_path)
            if not os.path.isabs(val_path):
                val_path = os.path.join(dataset_path, val_path)

            # 扫描训练集
            train_images = 0
            val_images = 0

            if os.path.exists(train_path):
                train_images = len([f for f in os.listdir(train_path)
                                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])

            if os.path.exists(val_path):
                val_images = len([f for f in os.listdir(val_path)
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])

            # 更新统计信息
            total_images = train_images + val_images
            nc = config.get('nc', 0)

            if hasattr(self, 'stats_images_label'):
                self.stats_images_label.setText(f"{total_images} 张")
            if hasattr(self, 'stats_labels_label'):
                self.stats_labels_label.setText(f"{total_images} 个")
            if hasattr(self, 'stats_classes_label'):
                self.stats_classes_label.setText(f"{nc} 类")
            if hasattr(self, 'stats_train_label'):
                self.stats_train_label.setText(f"{train_images} 张")
            if hasattr(self, 'stats_val_label'):
                self.stats_val_label.setText(f"{val_images} 张")

        except Exception as e:
            logger.error(f"扫描YAML数据集失败: {str(e)}")

    def show_dataset_config_info(self):
        """显示数据集配置信息"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            config_path = self.dataset_config_edit.text().strip()
            if not config_path or not os.path.exists(config_path):
                QMessageBox.warning(self, "提示", "请先选择有效的data.yaml配置文件")
                return

            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 格式化配置信息
            info_text = "📄 数据集配置信息:\n\n"

            if 'path' in config:
                info_text += f"📁 数据集路径: {config['path']}\n"
            if 'train' in config:
                info_text += f"📸 训练集: {config['train']}\n"
            if 'val' in config:
                info_text += f"🔍 验证集: {config['val']}\n"
            if 'nc' in config:
                info_text += f"🔢 类别数量: {config['nc']}\n"

            if 'names' in config:
                names = config['names']
                if isinstance(names, dict):
                    classes_list = [names[i] for i in sorted(names.keys())]
                elif isinstance(names, list):
                    classes_list = names
                else:
                    classes_list = []

                info_text += f"\n🏷️ 训练类别:\n"
                for i, class_name in enumerate(classes_list):
                    info_text += f"   {i}: {class_name}\n"

            QMessageBox.information(self, "数据集配置信息", info_text)

        except Exception as e:
            logger.error(f"显示数据集配置信息失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"读取配置文件失败:\n\n{str(e)}")

    def show_training_dialog(self):
        """显示训练对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox

            dialog = QDialog(self)
            dialog.setWindowTitle("🎓 模型训练")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("🎓 YOLO模型训练")
            title_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)

            # 数据统计信息
            stats_group = QGroupBox("📊 数据统计")
            stats_layout = QFormLayout(stats_group)

            stats = self.training_data_stats
            stats_layout.addRow("训练图片:", QLabel(f"{stats['total_images']} 张"))
            stats_layout.addRow("标注数量:", QLabel(
                f"{stats['total_annotations']} 个"))
            stats_layout.addRow("类别数量:", QLabel(f"{stats['classes_count']} 类"))

            layout.addWidget(stats_group)

            # 训练参数配置
            params_group = QGroupBox("⚙️ 训练参数")
            params_layout = QFormLayout(params_group)

            # 训练轮数
            epochs_spin = QSpinBox()
            epochs_spin.setRange(10, 1000)
            epochs_spin.setValue(100)
            params_layout.addRow("训练轮数:", epochs_spin)

            # 批次大小
            batch_spin = QSpinBox()
            batch_spin.setRange(1, 64)
            batch_spin.setValue(16)
            params_layout.addRow("批次大小:", batch_spin)

            # 学习率
            lr_spin = QDoubleSpinBox()
            lr_spin.setRange(0.0001, 0.1)
            lr_spin.setValue(0.01)
            lr_spin.setDecimals(4)
            params_layout.addRow("学习率:", lr_spin)

            # 模型大小
            model_combo = QComboBox()
            model_combo.addItems(["yolov8n", "yolov8s", "yolov8m", "yolov8l"])
            model_combo.setCurrentText("yolov8n")
            params_layout.addRow("模型大小:", model_combo)

            # 训练设备选择
            device_combo = QComboBox()
            if self.hardware_info['gpu_available']:
                device_combo.addItems(["GPU (推荐)", "CPU"])
                device_combo.setCurrentText("GPU (推荐)")
            else:
                device_combo.addItems(["CPU", "GPU (不可用)"])
                device_combo.setCurrentText("CPU")
            params_layout.addRow("训练设备:", device_combo)

            layout.addWidget(params_group)

            # 硬件信息组
            hardware_group = QGroupBox("🖥️ 硬件信息")
            hardware_layout = QFormLayout(hardware_group)

            # 显示硬件信息
            gpu_info = self.hardware_info['gpu_name'] if self.hardware_info['gpu_available'] else "未检测到GPU"
            hardware_layout.addRow("GPU:", QLabel(gpu_info))

            cuda_info = self.hardware_info['cuda_version'] if self.hardware_info['cuda_version'] != 'Unknown' else "未安装"
            hardware_layout.addRow("CUDA:", QLabel(cuda_info))

            pytorch_info = self.hardware_info['pytorch_version'] if self.hardware_info[
                'pytorch_version'] != 'Unknown' else "未安装"
            hardware_layout.addRow("PyTorch:", QLabel(pytorch_info))

            # 环境检查按钮
            env_buttons_layout = QHBoxLayout()

            check_env_btn = QPushButton("🔍 检查环境")
            check_env_btn.clicked.connect(
                lambda: self.check_training_environment(dialog))
            env_buttons_layout.addWidget(check_env_btn)

            install_pytorch_btn = QPushButton("📦 安装PyTorch")
            install_pytorch_btn.clicked.connect(
                lambda: self.show_pytorch_install_dialog())
            env_buttons_layout.addWidget(install_pytorch_btn)

            env_buttons_layout.addStretch()
            hardware_layout.addRow("", env_buttons_layout)

            layout.addWidget(hardware_group)

            # 训练进度
            progress_group = QGroupBox("📈 训练进度")
            progress_layout = QVBoxLayout(progress_group)

            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            progress_layout.addWidget(progress_bar)

            log_text = QTextEdit()
            log_text.setMaximumHeight(100)
            log_text.setPlainText("点击'开始训练'启动训练过程...")
            progress_layout.addWidget(log_text)

            layout.addWidget(progress_group)

            # 按钮
            buttons_layout = QHBoxLayout()

            start_btn = QPushButton("🚀 开始训练")
            # 获取设备选择
            selected_device = "cuda" if device_combo.currentText().startswith("GPU") else "cpu"

            start_btn.clicked.connect(lambda: self.start_training(
                epochs_spin.value(),
                batch_spin.value(),
                lr_spin.value(),
                model_combo.currentText(),
                selected_device,
                progress_bar,
                log_text
            ))
            buttons_layout.addWidget(start_btn)

            buttons_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示训练对话框失败: {str(e)}")

    def show_training_config_dialog(self):
        """显示训练配置对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QSpinBox, QLineEdit, QCheckBox, QMessageBox

            dialog = QDialog(self)
            dialog.setWindowTitle("⚙️ 训练配置")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # 数据要求配置
            data_group = QGroupBox("📊 数据要求")
            data_layout = QFormLayout(data_group)

            min_samples_spin = QSpinBox()
            min_samples_spin.setRange(5, 100)
            min_samples_spin.setValue(
                self.training_data_stats['min_samples_per_class'])
            data_layout.addRow("每类最少样本:", min_samples_spin)

            layout.addWidget(data_group)

            # 输出配置
            output_group = QGroupBox("📁 输出配置")
            output_layout = QFormLayout(output_group)

            output_dir = QLineEdit()
            output_dir.setText("./trained_models")
            output_layout.addRow("输出目录:", output_dir)

            model_name = QLineEdit()
            model_name.setText("custom_model")
            output_layout.addRow("模型名称:", model_name)

            layout.addWidget(output_group)

            # 高级选项
            advanced_group = QGroupBox("🔧 高级选项")
            advanced_layout = QFormLayout(advanced_group)

            auto_split = QCheckBox()
            auto_split.setChecked(True)
            advanced_layout.addRow("自动数据集划分:", auto_split)

            save_best = QCheckBox()
            save_best.setChecked(True)
            advanced_layout.addRow("保存最佳模型:", save_best)

            layout.addWidget(advanced_group)

            # 按钮
            buttons_layout = QHBoxLayout()

            save_btn = QPushButton("保存配置")
            save_btn.clicked.connect(lambda: self.save_training_config(
                min_samples_spin.value(),
                output_dir.text(),
                model_name.text(),
                auto_split.isChecked(),
                save_best.isChecked(),
                dialog
            ))
            buttons_layout.addWidget(save_btn)

            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示训练配置对话框失败: {str(e)}")

    def save_training_config(self, min_samples, output_dir, model_name, auto_split, save_best, dialog):
        """保存训练配置"""
        try:
            self.training_data_stats['min_samples_per_class'] = min_samples

            # 重新检查训练准备状态
            self.check_training_readiness()

            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", "训练配置已保存")
            dialog.accept()

        except Exception as e:
            logger.error(f"保存训练配置失败: {str(e)}")

    def check_training_environment(self, parent_dialog):
        """检查训练环境"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            # 重新检测硬件信息
            self.detect_hardware_info()

            # 生成环境报告
            report = "🔍 训练环境检查报告\n\n"

            # 系统信息
            report += f"💻 系统: {self.hardware_info.get('system', 'Unknown')}\n"
            report += f"🐍 Python: {self.hardware_info.get('python_version', 'Unknown')}\n\n"

            # GPU信息
            if self.hardware_info['gpu_available']:
                report += f"✅ GPU: {self.hardware_info['gpu_name']}\n"
                report += f"✅ CUDA: {self.hardware_info['cuda_version']}\n"
                report += f"✅ 推荐使用GPU训练 (速度快)\n\n"
            else:
                report += f"❌ GPU: 未检测到可用GPU\n"
                if self.hardware_info.get('nvidia_driver') == 'Not Found':
                    report += f"❌ NVIDIA驱动: 未安装\n"
                report += f"⚠️  将使用CPU训练 (速度较慢)\n\n"

            # PyTorch信息
            if self.hardware_info['pytorch_version'] != 'Not Installed':
                report += f"✅ PyTorch: {self.hardware_info['pytorch_version']}\n"
                report += f"✅ 训练环境就绪\n"
            else:
                report += f"❌ PyTorch: 未安装\n"
                report += f"⚠️  需要安装PyTorch才能开始训练\n"

            # 建议
            report += "\n💡 建议:\n"
            if not self.hardware_info['gpu_available']:
                report += "• 安装NVIDIA GPU和驱动以获得更快的训练速度\n"
            if self.hardware_info['pytorch_version'] == 'Not Installed':
                report += "• 点击'安装PyTorch'按钮安装训练依赖\n"

            QMessageBox.information(parent_dialog, "环境检查", report)

        except Exception as e:
            logger.error(f"环境检查失败: {str(e)}")

    def show_environment_check_dialog(self):
        """显示环境检查对话框（主面板版本）"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox

            dialog = QDialog(self)
            dialog.setWindowTitle("🔍 训练环境检查")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("🔍 训练环境检查报告")
            title_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)

            # 重新检测硬件信息
            self.detect_hardware_info()

            # 环境报告
            report_group = QGroupBox("📊 环境状态")
            report_layout = QVBoxLayout(report_group)

            report_text = QTextEdit()
            report_text.setReadOnly(True)

            # 生成详细报告
            report = self.generate_environment_report()
            report_text.setPlainText(report)

            report_layout.addWidget(report_text)
            layout.addWidget(report_group)

            # 操作按钮
            buttons_layout = QHBoxLayout()

            # 根据环境状态显示不同按钮
            if self.hardware_info['pytorch_version'] == 'Not Installed':
                install_btn = QPushButton("📦 安装PyTorch")
                install_btn.clicked.connect(
                    lambda: [dialog.accept(), self.show_pytorch_install_dialog()])
                buttons_layout.addWidget(install_btn)
            elif (self.hardware_info.get('nvidia_driver') != 'Not Found' and
                  self.hardware_info['pytorch_version'].endswith('+cpu')):
                upgrade_btn = QPushButton("⬆️ 升级到GPU版本")
                upgrade_btn.clicked.connect(
                    lambda: [dialog.accept(), self.show_pytorch_install_dialog()])
                buttons_layout.addWidget(upgrade_btn)

            refresh_btn = QPushButton("🔄 重新检测")
            refresh_btn.clicked.connect(
                lambda: self.refresh_environment_report(report_text))
            buttons_layout.addWidget(refresh_btn)

            buttons_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示环境检查对话框失败: {str(e)}")

    def generate_environment_report(self):
        """生成环境报告"""
        try:
            report = "🔍 训练环境检查报告\n"
            report += "=" * 40 + "\n\n"

            # 系统信息
            report += "💻 系统信息:\n"
            report += f"   操作系统: {self.hardware_info.get('system', 'Unknown')}\n"
            report += f"   Python版本: {self.hardware_info.get('python_version', 'Unknown')}\n\n"

            # GPU信息
            report += "🖥️ 硬件信息:\n"
            if self.hardware_info['gpu_available']:
                report += f"   ✅ GPU: {self.hardware_info['gpu_name']}\n"
                report += f"   ✅ CUDA: {self.hardware_info['cuda_version']}\n"
            else:
                report += f"   ❌ GPU: 未检测到可用GPU\n"
                if self.hardware_info.get('nvidia_driver') != 'Not Found':
                    report += f"   ⚠️  NVIDIA驱动: {self.hardware_info['nvidia_driver']} (已安装)\n"
                else:
                    report += f"   ❌ NVIDIA驱动: 未安装\n"

            # PyTorch信息
            report += "\n🔥 PyTorch环境:\n"
            if self.hardware_info['pytorch_version'] != 'Not Installed':
                report += f"   ✅ PyTorch: {self.hardware_info['pytorch_version']}\n"
                if self.hardware_info['pytorch_version'].endswith('+cpu'):
                    report += f"   ⚠️  当前为CPU版本\n"
                    if self.hardware_info.get('nvidia_driver') != 'Not Found':
                        report += f"   💡 建议: 升级到GPU版本以获得更快训练速度\n"
            else:
                report += f"   ❌ PyTorch: 未安装\n"
                report += f"   ⚠️  需要安装PyTorch才能开始训练\n"

            # 训练建议
            report += "\n🎯 训练建议:\n"
            if self.hardware_info['gpu_available']:
                report += f"   ✅ 推荐使用GPU训练 (速度快)\n"
                report += f"   📊 预计训练速度: 快速\n"
            else:
                report += f"   ⚠️  将使用CPU训练 (速度较慢)\n"
                report += f"   📊 预计训练速度: 较慢，请耐心等待\n"
                if self.hardware_info.get('nvidia_driver') != 'Not Found':
                    report += f"   💡 建议: 安装GPU版本PyTorch以提升速度\n"

            # 推荐安装命令
            if (self.hardware_info['pytorch_version'] == 'Not Installed' or
                (self.hardware_info.get('nvidia_driver') != 'Not Found' and
                 self.hardware_info['pytorch_version'].endswith('+cpu'))):
                report += "\n📦 推荐安装命令:\n"
                install_cmd = self.get_pytorch_install_command()
                report += f"   {install_cmd}\n"

            return report

        except Exception as e:
            logger.error(f"生成环境报告失败: {str(e)}")
            return "环境报告生成失败"

    def refresh_environment_report(self, report_text):
        """刷新环境报告"""
        try:
            self.detect_hardware_info()
            report = self.generate_environment_report()
            report_text.setPlainText(report)

        except Exception as e:
            logger.error(f"刷新环境报告失败: {str(e)}")

    def show_pytorch_install_dialog(self):
        """显示PyTorch安装对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar, QGroupBox

            dialog = QDialog(self)
            dialog.setWindowTitle("📦 PyTorch 安装")
            dialog.setModal(True)
            dialog.resize(600, 400)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("📦 PyTorch 环境安装")
            title_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)

            # 硬件信息
            info_group = QGroupBox("🖥️ 检测到的硬件")
            info_layout = QVBoxLayout(info_group)

            hardware_info = ""
            if self.hardware_info['gpu_available']:
                hardware_info += f"✅ GPU: {self.hardware_info['gpu_name']}\n"
                hardware_info += f"✅ CUDA: {self.hardware_info['cuda_version']}\n"
                hardware_info += "推荐安装GPU版本PyTorch"
            else:
                hardware_info += "❌ 未检测到GPU\n"
                hardware_info += "将安装CPU版本PyTorch"

            info_label = QLabel(hardware_info)
            info_layout.addWidget(info_label)
            layout.addWidget(info_group)

            # 安装命令
            cmd_group = QGroupBox("📋 安装命令")
            cmd_layout = QVBoxLayout(cmd_group)

            install_cmd = self.get_pytorch_install_command()
            cmd_text = QTextEdit()
            cmd_text.setPlainText(install_cmd)
            cmd_text.setMaximumHeight(60)
            cmd_layout.addWidget(cmd_text)

            # 复制按钮
            copy_btn = QPushButton("📋 复制命令")
            copy_btn.clicked.connect(
                lambda: self.copy_to_clipboard(install_cmd))
            cmd_layout.addWidget(copy_btn)

            layout.addWidget(cmd_group)

            # 安装进度
            progress_group = QGroupBox("📈 安装进度")
            progress_layout = QVBoxLayout(progress_group)

            progress_bar = QProgressBar()
            progress_layout.addWidget(progress_bar)

            log_text = QTextEdit()
            log_text.setMaximumHeight(100)
            log_text.setPlainText("点击'开始安装'或手动执行上述命令...")
            progress_layout.addWidget(log_text)

            layout.addWidget(progress_group)

            # 按钮
            buttons_layout = QHBoxLayout()

            install_btn = QPushButton("🚀 开始安装")
            install_btn.clicked.connect(lambda: self.install_pytorch(
                install_cmd, progress_bar, log_text))
            buttons_layout.addWidget(install_btn)

            manual_btn = QPushButton("📖 手动安装")
            manual_btn.clicked.connect(
                lambda: self.show_manual_install_guide())
            buttons_layout.addWidget(manual_btn)

            buttons_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示PyTorch安装对话框失败: {str(e)}")

    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", "命令已复制到剪贴板")

        except Exception as e:
            logger.error(f"复制到剪贴板失败: {str(e)}")

    def install_pytorch(self, command, progress_bar, log_text):
        """安装PyTorch（真实安装）"""
        try:
            import subprocess
            import sys
            import threading
            from PyQt5.QtCore import QTimer

            self._append_log_with_scroll(log_text, "🚀 开始安装PyTorch...")
            self._append_log_with_scroll(log_text, f"📋 执行命令: {command}")
            self._append_log_with_scroll(log_text, "⚠️  正在进行真实安装，请耐心等待...")

            # 确认用户是否要继续
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "确认安装",
                f"即将执行以下安装命令:\n\n{command}\n\n这将修改您的Python环境。是否继续？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                self._append_log_with_scroll(log_text, "❌ 用户取消安装")
                return

            # 准备安装命令
            install_cmd = command.split()

            # 使用当前Python解释器
            if install_cmd[0] == 'pip':
                install_cmd = [sys.executable, '-m', 'pip'] + install_cmd[1:]

            self._append_log_with_scroll(
                log_text, f"🔧 实际执行: {' '.join(install_cmd)}")

            # 创建安装线程
            self.install_thread = InstallThread(
                install_cmd, log_text, progress_bar)
            self.install_thread.progress_updated.connect(progress_bar.setValue)
            self.install_thread.log_updated.connect(log_text.append)
            self.install_thread.installation_finished.connect(
                lambda success, message: self.on_installation_finished(
                    success, message, log_text)
            )

            # 启动安装
            self.install_thread.start()
            self._append_log_with_scroll(log_text, "📦 安装进程已启动...")

        except Exception as e:
            logger.error(f"PyTorch安装失败: {str(e)}")
            self._append_log_with_scroll(log_text, f"❌ 安装失败: {str(e)}")

    def on_installation_finished(self, success, message, log_text):
        """安装完成回调"""
        try:
            if success:
                self._append_log_with_scroll(log_text, "✅ PyTorch安装完成!")
                self._append_log_with_scroll(log_text, "🔄 正在重新检测环境...")

                # 重新检测硬件环境
                self.detect_hardware_info()

                self._append_log_with_scroll(
                    log_text, "💡 建议重启labelImg以确保新环境生效")

                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "安装成功",
                    "PyTorch安装成功！\n\n建议重启labelImg以确保新环境完全生效。"
                )
            else:
                log_text.append(f"❌ 安装失败: {message}")

                # 分析失败原因并提供补偿方案
                self.handle_installation_failure(message, log_text)

        except Exception as e:
            logger.error(f"安装完成处理失败: {str(e)}")

    def handle_installation_failure(self, error_message, log_text):
        """处理安装失败，提供补偿机制"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit

            # 分析错误类型
            failure_type = self.analyze_failure_type(error_message)

            log_text.append(f"🔍 错误分析: {failure_type['type']}")
            log_text.append(f"💡 建议解决方案: {failure_type['solution']}")

            # 创建失败处理对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("🔧 安装失败处理")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # 标题
            title_label = QLabel("🔧 PyTorch安装失败 - 补偿方案")
            title_label.setStyleSheet(
                "font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title_label)

            # 错误信息
            error_text = QTextEdit()
            error_text.setPlainText(
                f"错误类型: {failure_type['type']}\n\n错误详情:\n{error_message}")
            error_text.setMaximumHeight(150)
            error_text.setReadOnly(True)
            layout.addWidget(error_text)

            # 补偿方案
            solutions_label = QLabel("🛠️ 可用的解决方案:")
            solutions_label.setStyleSheet(
                "font-weight: bold; margin-top: 10px;")
            layout.addWidget(solutions_label)

            # 解决方案按钮
            solutions_layout = QVBoxLayout()

            for solution in failure_type['solutions']:
                btn = QPushButton(solution['name'])
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 8px;
                        margin: 2px;
                        border: 1px solid #bdc3c7;
                        border-radius: 5px;
                        background-color: #f8f9fa;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                    }
                """)
                btn.clicked.connect(
                    lambda checked, s=solution: self.execute_solution(s, dialog, log_text))
                solutions_layout.addWidget(btn)

            layout.addLayout(solutions_layout)

            # 底部按钮
            buttons_layout = QHBoxLayout()

            manual_btn = QPushButton("📖 手动安装指南")
            manual_btn.clicked.connect(
                lambda: self.show_manual_install_guide())
            buttons_layout.addWidget(manual_btn)

            buttons_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"处理安装失败失败: {str(e)}")

    def analyze_failure_type(self, error_message):
        """分析失败类型"""
        try:
            error_lower = error_message.lower()

            # 网络相关错误
            if any(keyword in error_lower for keyword in ['network', 'connection', 'timeout', 'unreachable', 'dns']):
                return {
                    'type': '网络连接问题',
                    'solution': '尝试更换下载源或检查网络连接',
                    'solutions': [
                        {
                            'name': '🌍 使用清华大学镜像源 (推荐)',
                            'action': 'tsinghua_mirror',
                            'command': 'pip install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple'
                        },
                        {
                            'name': '🌏 使用阿里云镜像源',
                            'action': 'aliyun_mirror',
                            'command': 'pip install torch torchvision torchaudio -i https://mirrors.aliyun.com/pypi/simple'
                        },
                        {
                            'name': '🔄 重试原始安装',
                            'action': 'retry_original',
                            'command': self.get_pytorch_install_command()
                        },
                        {
                            'name': '💾 下载离线安装包',
                            'action': 'offline_download',
                            'command': 'manual'
                        }
                    ]
                }

            # 权限相关错误
            elif any(keyword in error_lower for keyword in ['permission', 'access', 'denied', 'administrator']):
                return {
                    'type': '权限不足',
                    'solution': '使用管理员权限或用户目录安装',
                    'solutions': [
                        {
                            'name': '👤 安装到用户目录 (推荐)',
                            'action': 'user_install',
                            'command': self.get_pytorch_install_command() + ' --user'
                        },
                        {
                            'name': '🔧 使用管理员权限重试',
                            'action': 'admin_retry',
                            'command': 'manual'
                        }
                    ]
                }

            # 磁盘空间不足
            elif any(keyword in error_lower for keyword in ['space', 'disk', 'storage', 'no space']):
                return {
                    'type': '磁盘空间不足',
                    'solution': '清理磁盘空间或更换安装位置',
                    'solutions': [
                        {
                            'name': '🧹 清理pip缓存',
                            'action': 'clear_cache',
                            'command': 'pip cache purge'
                        },
                        {
                            'name': '💾 安装CPU版本 (体积更小)',
                            'action': 'cpu_version',
                            'command': 'pip install torch torchvision torchaudio'
                        }
                    ]
                }

            # 版本冲突
            elif any(keyword in error_lower for keyword in ['conflict', 'incompatible', 'version']):
                return {
                    'type': '版本冲突',
                    'solution': '强制重新安装或升级相关包',
                    'solutions': [
                        {
                            'name': '🔄 强制重新安装',
                            'action': 'force_reinstall',
                            'command': self.get_pytorch_install_command() + ' --force-reinstall'
                        },
                        {
                            'name': '⬆️ 升级pip工具',
                            'action': 'upgrade_pip',
                            'command': 'python -m pip install --upgrade pip'
                        }
                    ]
                }

            # 默认通用错误
            else:
                return {
                    'type': '未知错误',
                    'solution': '尝试多种解决方案',
                    'solutions': [
                        {
                            'name': '🌍 使用国内镜像源',
                            'action': 'tsinghua_mirror',
                            'command': 'pip install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple'
                        },
                        {
                            'name': '👤 用户目录安装',
                            'action': 'user_install',
                            'command': self.get_pytorch_install_command() + ' --user'
                        },
                        {
                            'name': '💾 安装CPU版本',
                            'action': 'cpu_version',
                            'command': 'pip install torch torchvision torchaudio'
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"分析失败类型失败: {str(e)}")
            return {
                'type': '分析失败',
                'solution': '请手动安装',
                'solutions': []
            }

    def execute_solution(self, solution, dialog, log_text):
        """执行解决方案"""
        try:
            if solution['action'] == 'manual':
                # 手动操作，显示指导
                self.show_manual_solution_guide(solution)
                return

            if solution['action'] == 'offline_download':
                # 离线下载指导
                self.show_offline_download_guide()
                return

            if solution['action'] == 'admin_retry':
                # 管理员权限指导
                self.show_admin_retry_guide()
                return

            # 自动执行的解决方案
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                dialog,
                "确认执行",
                f"即将执行解决方案:\n\n{solution['name']}\n\n命令: {solution['command']}\n\n是否继续？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                dialog.accept()
                log_text.append(f"🔧 执行解决方案: {solution['name']}")
                log_text.append(f"📋 命令: {solution['command']}")

                # 重新启动安装
                self.retry_installation_with_command(
                    solution['command'], log_text)

        except Exception as e:
            logger.error(f"执行解决方案失败: {str(e)}")

    def retry_installation_with_command(self, command, log_text):
        """使用新命令重试安装"""
        try:
            import sys

            log_text.append("🔄 开始重试安装...")

            # 准备新的安装命令
            install_cmd = command.split()
            if install_cmd[0] == 'pip':
                install_cmd = [sys.executable, '-m', 'pip'] + install_cmd[1:]
            elif install_cmd[0] == 'python':
                install_cmd[0] = sys.executable

            # 创建新的安装线程
            # 注意：这里需要获取进度条，可能需要重新打开安装对话框
            log_text.append("💡 请重新点击安装按钮以使用新的解决方案")

        except Exception as e:
            logger.error(f"重试安装失败: {str(e)}")
            log_text.append(f"❌ 重试失败: {str(e)}")

    def show_offline_download_guide(self):
        """显示离线下载指导"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            guide = """💾 离线安装指南

如果网络连接不稳定，可以尝试离线安装：

1. 访问PyTorch官网: https://pytorch.org/get-started/locally/

2. 选择您的配置:
   - OS: Windows
   - Package: Pip
   - Language: Python
   - Compute Platform: CUDA 11.8 (如果有GPU)

3. 下载whl文件到本地

4. 使用命令安装:
   pip install 下载的文件路径.whl

5. 或者使用国内镜像源:
   pip install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
"""

            QMessageBox.information(self, "离线安装指南", guide)

        except Exception as e:
            logger.error(f"显示离线下载指南失败: {str(e)}")

    def show_admin_retry_guide(self):
        """显示管理员权限重试指导"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            guide = """🔧 管理员权限安装指南

如果遇到权限问题，请尝试以下方法：

方法1: 以管理员身份运行
1. 关闭当前labelImg
2. 右键点击labelImg图标
3. 选择"以管理员身份运行"
4. 重新尝试安装

方法2: 使用用户目录安装
1. 打开命令提示符
2. 执行: pip install torch torchvision torchaudio --user
3. 重启labelImg

方法3: 使用虚拟环境
1. 创建虚拟环境: python -m venv pytorch_env
2. 激活环境: pytorch_env\\Scripts\\activate
3. 安装PyTorch: pip install torch torchvision torchaudio
4. 在虚拟环境中运行labelImg
"""

            QMessageBox.information(self, "管理员权限指南", guide)

        except Exception as e:
            logger.error(f"显示管理员权限指南失败: {str(e)}")

    def show_manual_solution_guide(self, solution):
        """显示手动解决方案指导"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            guide = f"""📖 手动解决方案

解决方案: {solution['name']}

请手动执行以下步骤:
1. 打开命令提示符 (Windows) 或终端 (Linux/Mac)
2. 执行命令: {solution['command']}
3. 等待安装完成
4. 重启labelImg

如果仍然失败，请检查:
- 网络连接是否正常
- 是否有足够的磁盘空间
- 是否有必要的权限
- Python版本是否兼容
"""

            QMessageBox.information(self, "手动解决方案", guide)

        except Exception as e:
            logger.error(f"显示手动解决方案指导失败: {str(e)}")

    def show_manual_install_guide(self):
        """显示手动安装指南"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            guide = """📖 PyTorch 手动安装指南

1. 打开命令提示符 (Windows) 或终端 (Linux/Mac)

2. 执行以下命令之一:

GPU版本 (推荐，如果有NVIDIA GPU):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

CPU版本 (兼容性好):
pip install torch torchvision torchaudio

3. 安装完成后重启labelImg

4. 更多信息请访问: https://pytorch.org/get-started/locally/
"""

            QMessageBox.information(self, "手动安装指南", guide)

        except Exception as e:
            logger.error(f"显示手动安装指南失败: {str(e)}")

    def start_training(self, epochs, batch_size, learning_rate, model_size, device, progress_bar, log_text):
        """开始训练（模拟实现）"""
        try:
            # 这里应该实现实际的训练逻辑
            # 暂时只是模拟训练过程

            log_text.append("🚀 开始准备训练...")
            log_text.append(
                f"📊 训练参数: epochs={epochs}, batch={batch_size}, lr={learning_rate}")
            log_text.append(f"🤖 模型: {model_size}")
            log_text.append(f"🖥️  训练设备: {device.upper()}")

            # 设备特定的提示
            if device == "cuda":
                if self.hardware_info['gpu_available']:
                    log_text.append(
                        f"✅ 使用GPU训练: {self.hardware_info['gpu_name']}")
                    log_text.append("⚡ GPU训练速度更快，预计时间较短")
                else:
                    log_text.append("❌ GPU不可用，自动切换到CPU训练")
                    device = "cpu"

            if device == "cpu":
                log_text.append("🔄 使用CPU训练")
                log_text.append("⏰ CPU训练速度较慢，请耐心等待")

            log_text.append("📁 正在准备数据集...")
            log_text.append("⚠️  注意: 这是模拟训练，实际训练功能需要进一步开发")

            # 模拟进度更新
            for i in range(0, 101, 10):
                progress_bar.setValue(i)
                QApplication.processEvents()  # 更新界面
                import time
                time.sleep(0.1)

            log_text.append("✅ 模拟训练完成!")

            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "训练完成", "模拟训练已完成！\n实际训练功能将在后续版本中实现。")

        except Exception as e:
            logger.error(f"训练过程失败: {str(e)}")
            log_text.append(f"❌ 训练失败: {str(e)}")

    def update_confidence_label(self, value: int):
        """更新置信度标签"""
        confidence = value / 100.0
        self.confidence_label.setText(f"{confidence:.2f}")

    def update_nms_label(self, value: int):
        """更新NMS标签"""
        nms = value / 100.0
        self.nms_label.setText(f"{nms:.2f}")

    def get_current_confidence(self) -> float:
        """获取当前置信度阈值"""
        return self.confidence_slider.value() / 100.0

    def get_current_nms(self) -> float:
        """获取当前NMS阈值"""
        return self.nms_slider.value() / 100.0

    def get_current_max_det(self) -> int:
        """获取当前最大检测数"""
        return self.max_det_spin.value()

    def on_model_changed(self, model_name: str):
        """模型选择改变处理（优化版）"""
        try:
            if model_name == "无可用模型":
                self.model_info_label.setText("未选择模型")
                return

            # 获取模型路径
            current_index = self.model_combo.currentIndex()
            if current_index >= 0:
                model_path = self.model_combo.itemData(current_index)
                if model_path:
                    # 显示加载状态
                    display_name = model_name
                    if "🌟推荐" in model_name:
                        display_name = model_name.replace(" 🌟推荐", "")

                    self.update_status(f"🔄 正在加载模型: {display_name}")
                    self.model_info_label.setText("⏳ 正在加载模型...")

                    # 暂时禁用预测按钮
                    self.predict_current_btn.setEnabled(False)
                    self.predict_batch_btn.setEnabled(False)

                    # 加载模型
                    success = self.predictor.load_model(model_path)
                    if success:
                        # 获取模型信息
                        model_info = self.model_manager.get_model_info(
                            model_path)
                        self.update_model_info(model_info)

                        # 启用预测按钮
                        self.predict_current_btn.setEnabled(True)
                        self.predict_batch_btn.setEnabled(True)

                        # 显示成功状态
                        if "🌟推荐" in model_name:
                            self.update_status(f"✅ 已加载推荐模型: {display_name}")
                        else:
                            self.update_status(f"✅ 模型加载成功: {display_name}")

                        # 发送模型切换信号
                        self.model_changed.emit(model_path)

                        logger.info(f"模型切换成功: {model_path}")
                    else:
                        self.update_status("❌ 模型加载失败", is_error=True)
                        self.model_info_label.setText("❌ 模型加载失败")
                        self.predict_current_btn.setEnabled(False)
                        self.predict_batch_btn.setEnabled(False)

        except Exception as e:
            error_msg = f"模型切换失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)
            self.model_info_label.setText("❌ 模型切换失败")

    def on_smart_predict_changed(self, state):
        """智能预测复选框状态改变处理"""
        try:
            is_enabled = state == 2  # Qt.Checked = 2
            if is_enabled:
                status_text = "✅ 智能预测已开启 - 切换到未标注图片时将自动预测"
            else:
                status_text = "⏸️ 智能预测已关闭 - 需要手动点击预测按钮"

            self.update_status(status_text)

            # 保存设置到配置文件
            self.save_smart_predict_setting(is_enabled)

            logger.info(f"智能预测状态改变: {'开启' if is_enabled else '关闭'}")

        except Exception as e:
            error_msg = f"智能预测状态改变处理失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def save_smart_predict_setting(self, enabled: bool):
        """保存智能预测设置"""
        try:
            from libs.settings import Settings
            settings = Settings()
            settings.load()  # 先加载现有设置
            settings['ai_assistant/smart_predict_enabled'] = enabled
            settings.save()  # 保存设置
            logger.debug(f"智能预测设置已保存: {enabled}")
        except Exception as e:
            logger.error(f"保存智能预测设置失败: {str(e)}")

    def load_smart_predict_setting(self) -> bool:
        """加载智能预测设置"""
        try:
            from libs.settings import Settings
            settings = Settings()
            settings.load()  # 加载设置
            # 默认开启智能预测
            return settings.get('ai_assistant/smart_predict_enabled', True)
        except Exception as e:
            logger.error(f"加载智能预测设置失败: {str(e)}")
            return True  # 默认开启

    def is_smart_predict_enabled(self) -> bool:
        """检查智能预测是否开启"""
        try:
            return self.smart_predict_checkbox.isChecked()
        except Exception as e:
            logger.error(f"检查智能预测状态失败: {str(e)}")
            return False

    def load_and_apply_smart_predict_setting(self):
        """加载并应用智能预测设置"""
        try:
            enabled = self.load_smart_predict_setting()
            self.smart_predict_checkbox.setChecked(enabled)
            logger.debug(f"智能预测设置已加载并应用: {enabled}")
        except Exception as e:
            logger.error(f"加载智能预测设置失败: {str(e)}")
            # 默认开启
            self.smart_predict_checkbox.setChecked(True)

    def update_model_info(self, model_info: Dict):
        """更新模型信息显示（优化版，支持性能预览）"""
        try:
            if 'error' in model_info:
                self.model_info_label.setText(f"错误: {model_info['error']}")
                return

            # 获取当前选中的模型路径
            current_index = self.model_combo.currentIndex()
            if current_index >= 0:
                model_path = self.model_combo.itemData(current_index)

                # 检查是否是训练结果模型
                if model_path and 'runs/train' in model_path.replace('\\', '/'):
                    # 显示训练模型的详细性能信息
                    self._update_training_model_info(model_path)
                    return

            # 显示基本模型信息
            info_text = []

            if 'name' in model_info:
                info_text.append(f"📄 {model_info['name']}")

            if 'class_count' in model_info:
                info_text.append(f"🏷️ {model_info['class_count']}类")

            if 'size' in model_info:
                info_text.append(f"📊 {model_info['size']}")

            if 'is_pretrained' in model_info and model_info['is_pretrained']:
                info_text.append("🎯 预训练模型")

            self.model_info_label.setText(" | ".join(info_text))

            # 更新类别信息
            self.update_model_classes_info()

        except Exception as e:
            logger.error(f"更新模型信息失败: {str(e)}")
            self.model_info_label.setText("模型信息获取失败")

    def _update_training_model_info(self, model_path: str):
        """更新训练模型的详细信息显示"""
        try:
            # 获取模型详细信息
            model_info = self._get_model_detailed_info(model_path)

            if not model_info:
                self.model_info_label.setText("📄 训练模型 | 信息获取失败")
                return

            # 构建信息显示
            info_parts = []

            # 基本信息
            model_type = model_info.get('model_type', 'unknown.pt')
            if 'best' in model_type.lower():
                info_parts.append("🏆 最佳模型")
            elif 'last' in model_type.lower():
                info_parts.append("📝 最新模型")
            else:
                info_parts.append("🎯 训练模型")

            # 文件大小
            size_mb = model_info.get('size_mb', 0)
            if size_mb > 0:
                info_parts.append(f"📊 {size_mb}MB")

            # 性能指标
            performance = model_info.get('performance', {})
            mAP50 = performance.get('mAP50', 0)
            if mAP50 > 0:
                info_parts.append(f"📈 mAP:{mAP50:.3f}")

                # 性能评级
                stars, rating = self._get_performance_rating(mAP50)
                if stars:
                    info_parts.append(f"{stars} ({rating})")

            # 训练配置
            config = model_info.get('config', {})
            epochs = config.get('epochs', '')
            if epochs:
                info_parts.append(f"⚙️ {epochs}轮")

            # 推荐标记
            current_text = self.model_combo.currentText()
            if "🌟推荐" in current_text:
                info_parts.append("🌟 推荐")

            self.model_info_label.setText(" | ".join(info_parts))

            # 更新类别信息
            self.update_model_classes_info()

        except Exception as e:
            logger.error(f"更新训练模型信息失败: {str(e)}")
            self.model_info_label.setText("📄 训练模型 | 信息获取失败")

    def on_predict_current(self):
        """预测当前图像"""
        try:
            print("[DEBUG] AI助手: 开始预测当前图像")

            # 检查模型是否加载
            if not self.predictor or not self.predictor.is_model_loaded():
                error_msg = "模型未加载，请先选择并加载模型"
                print(f"[ERROR] AI助手: {error_msg}")
                self.update_status(error_msg, is_error=True)
                return

            # 这里需要从父窗口获取当前图像路径
            # 暂时发送信号，由父窗口处理
            confidence = self.get_current_confidence()
            print(f"[DEBUG] AI助手: 置信度设置为 {confidence}")
            print(f"[DEBUG] AI助手: 发送预测请求信号")
            self.prediction_requested.emit("", confidence)

        except Exception as e:
            error_msg = f"预测请求失败: {str(e)}"
            print(f"[ERROR] AI助手: {error_msg}")
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def start_prediction(self, image_path):
        """开始预测指定图像"""
        try:
            print(f"[DEBUG] AI助手: start_prediction被调用，图像路径: {image_path}")

            # 检查模型是否加载
            if not self.predictor or not self.predictor.is_model_loaded():
                error_msg = "模型未加载，请先选择并加载模型"
                print(f"[ERROR] AI助手: {error_msg}")
                self.update_status(error_msg, is_error=True)
                return

            # 检查图像文件
            if not os.path.exists(image_path):
                error_msg = f"图像文件不存在: {image_path}"
                print(f"[ERROR] AI助手: {error_msg}")
                self.update_status(error_msg, is_error=True)
                return

            print(f"[DEBUG] AI助手: 开始执行预测...")
            self.update_status("正在预测...")

            # 获取当前参数
            confidence = self.get_current_confidence()
            iou_threshold = self.get_current_nms()
            max_detections = self.get_current_max_det()

            print(
                f"[DEBUG] AI助手: 预测参数 - confidence: {confidence}, iou: {iou_threshold}, max_det: {max_detections}")

            # 执行预测（异步，结果将通过prediction_completed信号处理）
            print(f"[DEBUG] AI助手: 启动预测，等待prediction_completed信号...")
            result = self.predictor.predict_single(
                image_path=image_path,
                conf_threshold=confidence,
                iou_threshold=iou_threshold,
                max_det=max_detections
            )

            # 注意：结果处理现在完全在on_prediction_completed中进行
            # 这里不再处理结果，避免重复处理

        except Exception as e:
            error_msg = f"预测执行失败: {str(e)}"
            print(f"[ERROR] AI助手: {error_msg}")
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)
            import traceback
            traceback.print_exc()

    def on_predict_batch(self):
        """批量预测"""
        try:
            # 选择目录
            dir_path = QFileDialog.getExistingDirectory(
                self, "选择图像目录", "", QFileDialog.ShowDirsOnly
            )

            if dir_path:
                confidence = self.get_current_confidence()
                self.batch_prediction_requested.emit(dir_path, confidence)

        except Exception as e:
            error_msg = f"批量预测请求失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def on_cancel_prediction(self):
        """取消预测"""
        try:
            # 取消正在进行的批量预测
            if self.batch_processor and self.batch_processor.is_busy():
                self.batch_processor.cancel_processing()
                self.update_status("正在取消预测...")

            # 清除当前预测结果
            self.clear_prediction_results()

            print("[DEBUG] AI助手: 预测已取消，结果已清除")

        except Exception as e:
            error_msg = f"取消预测失败: {str(e)}"
            print(f"[ERROR] AI助手: {error_msg}")
            logger.error(error_msg)

    def on_apply_results(self):
        """应用预测结果"""
        try:
            if self.current_predictions:
                # 应用置信度过滤
                filtered_predictions = self.confidence_filter.filter_detections(
                    self.current_predictions, self.get_current_confidence()
                )

                # 应用标注优化
                optimized_predictions = self.confidence_filter.optimize_for_annotation(
                    filtered_predictions
                )

                # 发送应用信号
                self.predictions_applied.emit(optimized_predictions)

                self.update_status(f"已应用 {len(optimized_predictions)} 个预测结果")

        except Exception as e:
            error_msg = f"应用预测结果失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def on_clear_results(self):
        """清除预测结果"""
        try:
            self.clear_prediction_results()
            print("[DEBUG] AI助手: 预测结果已清除")

        except Exception as e:
            error_msg = f"清除预测结果失败: {str(e)}"
            print(f"[ERROR] AI助手: {error_msg}")
            logger.error(error_msg)

    def clear_prediction_results(self):
        """清除预测结果的内部方法"""
        try:
            # 清除面板显示
            self.current_predictions.clear()
            self.results_list.clear()
            self.results_stats_label.setText("暂无预测结果")
            self.apply_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)

            # 发送清除信号，通知主窗口清除图片上的标注框
            self.predictions_cleared.emit()

            self.update_status("已清除预测结果")

        except Exception as e:
            error_msg = f"清除预测结果失败: {str(e)}"
            print(f"[ERROR] AI助手: {error_msg}")
            logger.error(error_msg)

    def on_result_item_double_clicked(self, item):
        """结果项双击处理"""
        try:
            # 可以在这里实现跳转到对应检测框等功能
            text = item.text()
            logger.info(f"双击结果项: {text}")

        except Exception as e:
            logger.error(f"结果项双击处理失败: {str(e)}")

    def update_status(self, message: str, is_error: bool = False):
        """更新状态显示"""
        try:
            self.status_label.setText(message)

            if is_error:
                self.status_label.setStyleSheet("""
                    QLabel#statusLabel {
                        background-color: #ffebee;
                        border: 1px solid #f44336;
                        border-radius: 4px;
                        padding: 6px;
                        color: #c62828;
                        font-weight: 600;
                    }
                """)
            else:
                self.status_label.setStyleSheet("""
                    QLabel#statusLabel {
                        background-color: #f3e5f5;
                        border: 1px solid #9c27b0;
                        border-radius: 4px;
                        padding: 6px;
                        color: #7b1fa2;
                        font-weight: 600;
                    }
                """)

            logger.info(f"状态更新: {message}")

        except Exception as e:
            logger.error(f"更新状态失败: {str(e)}")

    # AI组件事件处理方法
    def on_model_validated(self, model_path: str, is_valid: bool):
        """模型验证完成处理"""
        try:
            model_name = os.path.basename(model_path)
            if is_valid:
                self.update_status(f"模型验证成功: {model_name}")
            else:
                self.update_status(f"模型验证失败: {model_name}", is_error=True)

        except Exception as e:
            logger.error(f"模型验证处理失败: {str(e)}")

    def on_model_loaded(self, model_name: str):
        """模型加载完成处理"""
        try:
            self.update_status(f"模型加载成功: {model_name}")

        except Exception as e:
            logger.error(f"模型加载处理失败: {str(e)}")

    def on_prediction_completed(self, result):
        """单图预测完成处理"""
        try:
            self.current_predictions = result.detections
            self.update_prediction_results(result)

            # 更新性能信息
            self.performance_label.setText(
                f"推理时间: {result.inference_time:.3f}秒 | "
                f"检测数量: {len(result.detections)}"
            )

            # 根据预测类型显示不同的状态信息
            if self.is_smart_predicting:
                if result.detections:
                    print(
                        f"[DEBUG] 智能预测完成，自动应用 {len(result.detections)} 个检测结果")
                    self.predictions_applied.emit([result])
                    self.update_status(
                        f"🤖 智能预测完成，已自动应用 {len(result.detections)} 个检测结果")
                else:
                    print(f"[DEBUG] 智能预测完成，未检测到对象")
                    self.update_status("🤖 智能预测完成，未检测到对象")

                # 重置智能预测状态
                self.is_smart_predicting = False
            else:
                # 手动预测：显示结果但不自动应用
                self.update_status(f"预测完成，检测到 {len(result.detections)} 个目标")
                if result.detections:
                    print(f"[DEBUG] 手动预测完成，发送应用信号")
                    self.predictions_applied.emit([result])
                else:
                    print(f"[DEBUG] 手动预测完成，未检测到对象")

        except Exception as e:
            error_msg = f"预测完成处理失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)
            self.is_smart_predicting = False

    def on_batch_started(self, total_files: int):
        """批量预测开始处理"""
        try:
            self.is_predicting = True
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, total_files)
            self.progress_bar.setValue(0)

            self.cancel_btn.setEnabled(True)
            self.predict_current_btn.setEnabled(False)
            self.predict_batch_btn.setEnabled(False)

            self.update_status(f"开始批量预测 {total_files} 个文件")

        except Exception as e:
            logger.error(f"批量预测开始处理失败: {str(e)}")

    def on_batch_progress(self, current: int, total: int, current_file: str):
        """批量预测进度更新处理"""
        try:
            self.progress_bar.setValue(current)

            progress_percent = (current / total * 100) if total > 0 else 0
            self.update_status(
                f"批量预测进度: {current}/{total} ({progress_percent:.1f}%) - {os.path.basename(current_file)}"
            )

        except Exception as e:
            logger.error(f"批量预测进度处理失败: {str(e)}")

    def on_batch_completed(self, summary: Dict):
        """批量预测完成处理"""
        try:
            self.is_predicting = False
            self.progress_bar.setVisible(False)

            self.cancel_btn.setEnabled(False)
            self.predict_current_btn.setEnabled(True)
            self.predict_batch_btn.setEnabled(True)

            # 更新统计信息
            total_files = summary.get('total_files', 0)
            successful_files = summary.get('successful_files', 0)
            failed_files = summary.get('failed_files', 0)
            total_time = summary.get('total_time', 0)

            self.performance_label.setText(
                f"批量预测完成 | 成功: {successful_files}/{total_files} | "
                f"总耗时: {total_time:.2f}秒"
            )

            self.update_status(
                f"批量预测完成: 成功 {successful_files}/{total_files} 个文件"
            )

        except Exception as e:
            error_msg = f"批量预测完成处理失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)

    def on_batch_cancelled(self):
        """批量预测取消处理"""
        try:
            self.is_predicting = False
            self.progress_bar.setVisible(False)

            self.cancel_btn.setEnabled(False)
            self.predict_current_btn.setEnabled(True)
            self.predict_batch_btn.setEnabled(True)

            self.update_status("批量预测已取消")

        except Exception as e:
            logger.error(f"批量预测取消处理失败: {str(e)}")

    def on_ai_error(self, error_message: str):
        """AI组件错误处理"""
        try:
            self.update_status(f"AI错误: {error_message}", is_error=True)

            # 重置预测状态
            if self.is_predicting:
                self.is_predicting = False
                self.progress_bar.setVisible(False)
                self.cancel_btn.setEnabled(False)
                self.predict_current_btn.setEnabled(True)
                self.predict_batch_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"AI错误处理失败: {str(e)}")

    def update_prediction_results(self, result):
        """更新预测结果显示"""
        try:
            detections = result.detections

            # 更新统计信息
            if detections:
                # 计算置信度分布
                confidences = [det.confidence for det in detections]
                avg_confidence = sum(confidences) / len(confidences)
                max_confidence = max(confidences)
                min_confidence = min(confidences)

                stats_text = (
                    f"检测数量: {len(detections)} | "
                    f"平均置信度: {avg_confidence:.3f} | "
                    f"范围: {min_confidence:.3f}-{max_confidence:.3f}"
                )
            else:
                stats_text = "未检测到目标"

            self.results_stats_label.setText(stats_text)

            # 更新结果列表
            self.results_list.clear()
            for i, detection in enumerate(detections):
                item_text = (
                    f"{i+1}. {detection.class_name} "
                    f"(置信度: {detection.confidence:.3f})"
                )

                item = QListWidgetItem(item_text)

                # 根据置信度设置颜色
                if detection.confidence >= 0.7:
                    item.setBackground(QColor(200, 255, 200))  # 高置信度 - 绿色
                elif detection.confidence >= 0.4:
                    item.setBackground(QColor(255, 255, 200))  # 中等置信度 - 黄色
                else:
                    item.setBackground(QColor(255, 220, 220))  # 低置信度 - 红色

                self.results_list.addItem(item)

            # 启用操作按钮
            if detections:
                self.apply_btn.setEnabled(True)
                self.clear_btn.setEnabled(True)
            else:
                self.apply_btn.setEnabled(False)
                self.clear_btn.setEnabled(False)

        except Exception as e:
            logger.error(f"更新预测结果显示失败: {str(e)}")

    # 公共接口方法
    def predict_image(self, image_path: str) -> bool:
        """
        预测指定图像

        Args:
            image_path: 图像文件路径

        Returns:
            bool: 预测是否成功启动
        """
        try:
            if not self.predictor or not self.predictor.is_model_loaded():
                self.update_status("模型未加载", is_error=True)
                return False

            if not os.path.exists(image_path):
                self.update_status(f"图像文件不存在: {image_path}", is_error=True)
                return False

            self.update_status(f"正在预测: {os.path.basename(image_path)}")

            # 执行预测
            result = self.predictor.predict_single(
                image_path,
                conf_threshold=self.get_current_confidence(),
                iou_threshold=self.get_current_nms(),
                max_det=self.get_current_max_det()
            )

            if result:
                self.on_prediction_completed(result)
                return True
            else:
                self.update_status("预测失败", is_error=True)
                return False

        except Exception as e:
            error_msg = f"预测图像失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)
            return False

    def start_batch_prediction(self, dir_path: str) -> bool:
        """
        开始批量预测

        Args:
            dir_path: 图像目录路径

        Returns:
            bool: 批量预测是否成功启动
        """
        try:
            if not self.predictor or not self.predictor.is_model_loaded():
                self.update_status("模型未加载", is_error=True)
                return False

            if not os.path.exists(dir_path):
                self.update_status(f"目录不存在: {dir_path}", is_error=True)
                return False

            # 启动批量预测
            self.batch_processor.process_directory(
                dir_path,
                conf_threshold=self.get_current_confidence(),
                iou_threshold=self.get_current_nms(),
                max_det=self.get_current_max_det()
            )

            return True

        except Exception as e:
            error_msg = f"启动批量预测失败: {str(e)}"
            logger.error(error_msg)
            self.update_status(error_msg, is_error=True)
            return False

    def get_current_predictions(self) -> List:
        """获取当前预测结果"""
        return self.current_predictions.copy()

    def is_busy(self) -> bool:
        """检查是否正在处理"""
        return self.is_predicting

    def get_predictor(self) -> Optional[YOLOPredictor]:
        """获取预测器实例"""
        return self.predictor

    # ==================== 训练器回调方法 ====================

    def on_training_started(self):
        """训练开始回调"""
        try:
            # 安全更新日志
            self._safe_append_log("🚀 训练已开始...")

            # 确保切换到训练监控标签页
            self._switch_to_training_monitor()

            # 更新训练状态
            if hasattr(self, 'training_status_label') and self.training_status_label is not None:
                try:
                    self.training_status_label.setText("🚀 正在启动...")
                    self.training_status_label.setStyleSheet(
                        "color: #f39c12; font-weight: bold;")
                except RuntimeError:
                    pass

            # 重置进度条
            if hasattr(self, 'training_progress_bar') and self.training_progress_bar is not None:
                try:
                    self.training_progress_bar.setValue(0)
                    self.training_progress_bar.setFormat("正在启动训练... (%p%)")
                except RuntimeError:
                    pass

            # 启用停止按钮，禁用开始按钮
            if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                try:
                    self.stop_training_btn.setEnabled(True)
                except RuntimeError:
                    pass
            if hasattr(self, 'start_training_btn') and self.start_training_btn is not None:
                try:
                    self.start_training_btn.setEnabled(False)
                except RuntimeError:
                    pass

            # 禁用训练按钮，启用停止按钮
            if hasattr(self, 'start_training_btn') and self.start_training_btn is not None:
                try:
                    self.start_training_btn.setEnabled(False)
                except RuntimeError:
                    pass
            if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                try:
                    self.stop_training_btn.setEnabled(True)
                except RuntimeError:
                    pass

            # 自动切换到训练监控标签页
            self._switch_to_training_monitor()

        except Exception as e:
            logger.error(f"训练开始回调失败: {str(e)}")

    def on_training_progress(self, metrics):
        """训练进度回调"""
        try:
            # 更新进度条
            if hasattr(self, 'training_progress_bar') and self.training_progress_bar is not None:
                try:
                    progress = int(
                        (metrics.epoch / metrics.total_epochs) * 100)
                    self.training_progress_bar.setValue(progress)
                    self.training_progress_bar.setFormat(
                        f"Epoch {metrics.epoch}/{metrics.total_epochs} (%p%)")
                except RuntimeError:
                    pass

            # 更新训练状态
            if hasattr(self, 'training_status_label') and self.training_status_label is not None:
                try:
                    self.training_status_label.setText("🔥 训练中...")
                    self.training_status_label.setStyleSheet(
                        "color: #e74c3c; font-weight: bold;")
                except RuntimeError:
                    pass

            # 更新训练指标
            if hasattr(self, 'loss_label') and self.loss_label is not None:
                try:
                    self.loss_label.setText(f"📉 损失值: {metrics.train_loss:.4f}")
                except RuntimeError:
                    pass

            if hasattr(self, 'map_label') and self.map_label is not None:
                try:
                    self.map_label.setText(f"🎯 mAP50: {metrics.map50:.4f}")
                except RuntimeError:
                    pass

            if hasattr(self, 'lr_label') and self.lr_label is not None:
                try:
                    self.lr_label.setText(f"📊 学习率: {metrics.lr:.6f}")
                except RuntimeError:
                    pass

            # 更新训练监控标签页的内容
            if hasattr(self, 'monitor_log_text') and self.monitor_log_text is not None:
                try:
                    log_msg = (f"Epoch {metrics.epoch}/{metrics.total_epochs} - "
                               f"Loss: {metrics.train_loss:.4f}, "
                               f"Val Loss: {metrics.val_loss:.4f}, "
                               f"mAP50: {metrics.map50:.4f}, "
                               f"Precision: {metrics.precision:.4f}, "
                               f"Recall: {metrics.recall:.4f}")
                    self.monitor_log_text.append(log_msg)
                    # 自动滚动到底部
                    self.monitor_log_text.moveCursor(
                        self.monitor_log_text.textCursor().End)
                except RuntimeError:
                    pass

        except Exception as e:
            logger.error(f"训练进度回调失败: {str(e)}")

    def on_training_completed(self, model_path):
        """训练完成回调"""
        try:
            self._safe_append_log(f"✅ 训练完成！模型已保存到: {model_path}")

            # 复制模型到 models 文件夹
            copied_model_path = self._copy_model_to_models_folder(model_path)

            # 更新训练状态
            if hasattr(self, 'training_status_label') and self.training_status_label is not None:
                try:
                    self.training_status_label.setText("✅ 训练完成")
                    self.training_status_label.setStyleSheet(
                        "color: #27ae60; font-weight: bold;")
                except RuntimeError:
                    pass

            # 更新进度条
            if hasattr(self, 'training_progress_bar') and self.training_progress_bar is not None:
                try:
                    self.training_progress_bar.setValue(100)
                    self.training_progress_bar.setFormat("训练完成！ (100%)")
                except RuntimeError:
                    pass

            # 重新启用训练按钮，禁用停止按钮
            if hasattr(self, 'start_training_btn') and self.start_training_btn is not None:
                try:
                    self.start_training_btn.setEnabled(True)
                except RuntimeError:
                    pass
            if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                try:
                    self.stop_training_btn.setEnabled(False)
                except RuntimeError:
                    pass

            # 显示完成对话框并询问是否加载新模型
            from PyQt5.QtWidgets import QMessageBox

            # 构建完成消息
            completion_message = f"🎉 YOLO模型训练成功完成！\n\n"
            completion_message += f"📁 原始模型路径:\n{model_path}\n\n"

            if copied_model_path:
                completion_message += f"📂 已复制到 models 文件夹:\n{copied_model_path}\n\n"
                completion_message += f"是否立即加载新训练的模型用于预测？"
                use_model_path = copied_model_path
            else:
                completion_message += f"⚠️ 复制到 models 文件夹失败，将使用原始路径\n\n"
                completion_message += f"是否立即加载新训练的模型用于预测？"
                use_model_path = model_path

            reply = QMessageBox.question(
                self, "训练完成", completion_message,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # 自动加载新训练的模型
                self.load_trained_model(use_model_path)

            # 关闭训练对话框
            if hasattr(self, 'training_dialog') and self.training_dialog is not None:
                try:
                    self.training_dialog.accept()
                    self.training_dialog = None
                except RuntimeError:
                    pass

        except Exception as e:
            logger.error(f"训练完成回调失败: {str(e)}")

    def _copy_model_to_models_folder(self, model_path):
        """将训练好的模型复制到 models 文件夹"""
        try:
            import shutil
            from datetime import datetime

            # 确保 models 文件夹存在
            models_dir = os.path.join(os.getcwd(), "models")
            custom_models_dir = os.path.join(models_dir, "custom")
            os.makedirs(custom_models_dir, exist_ok=True)

            # 生成新的模型文件名（包含时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = os.path.basename(model_path)
            name_without_ext = os.path.splitext(original_name)[0]
            new_model_name = f"trained_model_{timestamp}.pt"

            # 目标路径
            target_path = os.path.join(custom_models_dir, new_model_name)

            # 复制模型文件
            shutil.copy2(model_path, target_path)

            self._safe_append_log(f"📂 模型已复制到: {target_path}")

            # 刷新模型列表
            self.refresh_models()

            return target_path

        except Exception as e:
            error_msg = f"复制模型到 models 文件夹失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_log(f"❌ {error_msg}")
            return None

    def on_training_error(self, error_msg):
        """训练错误回调"""
        try:
            self._safe_append_log(f"❌ 训练错误: {error_msg}")

            # 更新训练状态
            if hasattr(self, 'training_status_label') and self.training_status_label is not None:
                try:
                    self.training_status_label.setText("❌ 训练失败")
                    self.training_status_label.setStyleSheet(
                        "color: #e74c3c; font-weight: bold;")
                except RuntimeError:
                    pass

            # 更新进度条
            if hasattr(self, 'training_progress_bar') and self.training_progress_bar is not None:
                try:
                    self.training_progress_bar.setFormat("训练失败！")
                except RuntimeError:
                    pass

            # 重新启用训练按钮，禁用停止按钮
            if hasattr(self, 'start_training_btn') and self.start_training_btn is not None:
                try:
                    self.start_training_btn.setEnabled(True)
                except RuntimeError:
                    pass
            if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                try:
                    self.stop_training_btn.setEnabled(False)
                except RuntimeError:
                    pass

            # 显示错误对话框
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, "训练错误",
                f"训练过程中发生错误:\n\n{error_msg}\n\n"
                f"请检查配置和数据集，然后重试。"
            )

        except Exception as e:
            logger.error(f"训练错误回调失败: {str(e)}")

    def on_training_stopped(self):
        """训练停止回调"""
        try:
            self._safe_append_log("🛑 训练已停止")

            # 更新训练状态
            if hasattr(self, 'training_status_label') and self.training_status_label is not None:
                try:
                    self.training_status_label.setText("🛑 训练停止")
                    self.training_status_label.setStyleSheet(
                        "color: #f39c12; font-weight: bold;")
                except RuntimeError:
                    pass

            # 更新进度条
            if hasattr(self, 'training_progress_bar') and self.training_progress_bar is not None:
                try:
                    self.training_progress_bar.setFormat("训练已停止")
                except RuntimeError:
                    pass

            # 重新启用训练按钮，禁用停止按钮
            if hasattr(self, 'start_training_btn') and self.start_training_btn is not None:
                try:
                    self.start_training_btn.setEnabled(True)
                except RuntimeError:
                    pass
            if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                try:
                    self.stop_training_btn.setEnabled(False)
                except RuntimeError:
                    pass

        except Exception as e:
            logger.error(f"训练停止回调失败: {str(e)}")

    def on_training_log(self, message):
        """训练日志回调"""
        try:
            self._safe_append_log(message)
        except Exception as e:
            logger.error(f"训练日志回调失败: {str(e)}")

    def load_trained_model(self, model_path):
        """加载训练好的模型"""
        try:
            if os.path.exists(model_path):
                # 使用预测器加载新模型
                if self.predictor:
                    success = self.predictor.load_model(model_path)
                    if success:
                        self._safe_append_log(f"✅ 已加载新训练的模型: {model_path}")
                        # 更新模型列表
                        self.refresh_models()
                        # 发送模型切换信号
                        self.model_changed.emit(model_path)
                    else:
                        self._safe_append_log(f"❌ 加载模型失败: {model_path}")
                else:
                    self._safe_append_log("❌ 预测器未初始化，无法加载模型")
            else:
                self._safe_append_log(f"❌ 模型文件不存在: {model_path}")

        except Exception as e:
            error_msg = f"加载训练模型失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_log(f"❌ {error_msg}")

    def show_training_results(self, model_path):
        """显示训练结果详情"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

            dialog = QDialog(self)
            dialog.setWindowTitle("训练结果")
            dialog.setFixedSize(600, 400)

            layout = QVBoxLayout(dialog)

            # 结果文本
            results_text = QTextEdit()
            results_text.setReadOnly(True)

            # 读取训练结果
            results_dir = Path(model_path).parent.parent
            results_content = f"🎉 训练完成！\n\n"
            results_content += f"📁 模型路径: {model_path}\n"
            results_content += f"📊 结果目录: {results_dir}\n\n"

            # 尝试读取训练日志
            log_file = results_dir / "train" / "results.csv"
            if log_file.exists():
                results_content += "📈 训练结果摘要:\n"
                # 这里可以解析CSV文件显示最终指标
                results_content += "详细结果请查看results.csv文件\n"

            results_text.setPlainText(results_content)
            layout.addWidget(results_text)

            # 按钮
            buttons_layout = QHBoxLayout()

            load_btn = QPushButton("加载模型")
            load_btn.clicked.connect(
                lambda: self.load_trained_model(model_path))
            load_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(load_btn)

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            dialog.exec_()

        except Exception as e:
            logger.error(f"显示训练结果失败: {str(e)}")

    def stop_training(self):
        """停止训练"""
        try:
            if self.trainer and self.trainer.is_training:
                self.trainer.stop_training()
                self._safe_append_log("🛑 正在停止训练...")

                # 禁用停止按钮
                if hasattr(self, 'stop_training_btn') and self.stop_training_btn is not None:
                    try:
                        self.stop_training_btn.setEnabled(False)
                    except RuntimeError:
                        pass
            else:
                self._safe_append_log("⚠️ 当前没有正在进行的训练")

        except Exception as e:
            error_msg = f"停止训练失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_log(f"❌ {error_msg}")

    def _safe_append_log(self, message):
        """安全地添加日志消息"""
        try:
            if hasattr(self, 'log_text') and self.log_text is not None:
                try:
                    self.log_text.append(message)
                    # 自动滚动到底部
                    self.log_text.moveCursor(self.log_text.textCursor().End)
                except RuntimeError:
                    # UI对象已被删除，使用logger记录
                    logger.info(f"训练日志: {message}")
            else:
                logger.info(f"训练日志: {message}")
        except Exception as e:
            logger.error(f"安全日志更新失败: {str(e)}")

    def _safe_append_data_log(self, message):
        """安全地添加数据配置日志消息"""
        try:
            if hasattr(self, 'data_config_log_text') and self.data_config_log_text is not None:
                try:
                    self.data_config_log_text.append(message)
                    # 自动滚动到底部
                    self.data_config_log_text.moveCursor(
                        self.data_config_log_text.textCursor().End)
                except RuntimeError:
                    # UI对象已被删除，使用logger记录
                    logger.info(f"数据配置日志: {message}")
            else:
                logger.info(f"数据配置日志: {message}")
        except Exception as e:
            logger.error(f"安全数据配置日志更新失败: {str(e)}")

    def _safe_append_auto_log(self, message):
        """安全地添加自动配置日志消息"""
        try:
            if hasattr(self, 'auto_log_text') and self.auto_log_text is not None:
                try:
                    self.auto_log_text.append(message)
                    # 自动滚动到底部
                    self.auto_log_text.moveCursor(
                        self.auto_log_text.textCursor().End)
                except RuntimeError:
                    # UI对象已被删除，使用logger记录
                    logger.info(f"自动配置日志: {message}")
            else:
                logger.info(f"自动配置日志: {message}")
        except Exception as e:
            logger.error(f"安全自动配置日志更新失败: {str(e)}")

    def _append_log_with_scroll(self, log_text_widget, message):
        """向指定的日志文本框添加消息并自动滚动"""
        try:
            if log_text_widget is not None:
                try:
                    log_text_widget.append(message)
                    # 自动滚动到底部
                    log_text_widget.moveCursor(
                        log_text_widget.textCursor().End)
                except RuntimeError:
                    # UI对象已被删除，使用logger记录
                    logger.info(f"日志: {message}")
            else:
                logger.info(f"日志: {message}")
        except Exception as e:
            logger.error(f"日志更新失败: {str(e)}")

    def refresh_dataset_config(self):
        """刷新数据集配置"""
        try:
            self._safe_append_data_log("🔄 开始刷新数据集配置...")

            config_path = self.dataset_config_edit.text().strip()
            if not config_path:
                self._safe_append_data_log("⚠️ 未选择配置文件")
                return

            if not os.path.exists(config_path):
                self._safe_append_data_log(f"❌ 配置文件不存在: {config_path}")
                return

            # 重新加载配置文件
            self.load_dataset_config(config_path)
            self._safe_append_data_log("✅ 数据集配置刷新完成")

        except Exception as e:
            error_msg = f"刷新数据集配置失败: {str(e)}"
            logger.error(error_msg)
            self._safe_append_data_log(f"❌ {error_msg}")

    def _switch_to_training_monitor(self):
        """切换到训练监控标签页"""
        try:
            # 查找训练对话框中的标签页控件
            if hasattr(self, 'training_tab_widget') and self.training_tab_widget is not None:
                try:
                    # 切换到训练监控标签页（通常是第3个标签页，索引为2）
                    self.training_tab_widget.setCurrentIndex(2)
                except RuntimeError:
                    pass
            else:
                # 如果没有找到标签页控件，尝试查找父窗口中的标签页
                parent = self.parent()
                while parent:
                    for child in parent.findChildren(QTabWidget):
                        if child.objectName() == 'training_tab_widget' or child.count() >= 3:
                            try:
                                child.setCurrentIndex(2)
                                return
                            except RuntimeError:
                                pass
                    parent = parent.parent()
        except Exception as e:
            logger.error(f"切换到训练监控标签页失败: {str(e)}")

    def get_model_manager(self) -> Optional[ModelManager]:
        """获取模型管理器实例"""
        return self.model_manager
