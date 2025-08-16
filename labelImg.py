#!/usr/bin/env python
# -*- coding: utf-8 -*-
from libs.utils import *
from libs.yolo_export_dialog import YOLOExportDialog
from libs.model_export_dialog import ModelExportDialog
from libs.pinyin_utils import process_label_text, has_chinese
from libs.hashableQListWidgetItem import HashableQListWidgetItem
from libs.ustr import ustr
from libs.create_ml_io import JSON_EXT
from libs.create_ml_io import CreateMLReader
from libs.yolo_io import TXT_EXT
from libs.yolo_io import YoloReader
from libs.pascal_voc_io import XML_EXT
from libs.pascal_voc_io import PascalVocReader
from libs.toolBar import ToolBar
from libs.labelFile import LabelFile, LabelFileError, LabelFileFormat
from libs.colorDialog import ColorDialog
from libs.labelDialog import LabelDialog
from libs.lightWidget import LightWidget
from libs.zoomWidget import ZoomWidget
from libs.canvas import Canvas
from libs.stringBundle import StringBundle
from libs.shape import Shape, DEFAULT_LINE_COLOR, DEFAULT_FILL_COLOR
from libs.settings import Settings
import argparse
import codecs
import os.path
import platform
import shutil
import sys
import time
import webbrowser as wb
from functools import partial

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    # needed for py3+qt4
    # Ref:
    # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
    # http://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.combobox import ComboBox
from libs.default_label_combobox import DefaultLabelComboBox
from libs.delete_confirmation_dialog import DeleteConfirmationDialog, SimpleDeleteConfirmationDialog
from libs.resources import *
from libs.constants import *

# AI助手相关导入
from libs.ai_assistant_panel import AIAssistantPanel, CollapsibleAIPanel
from libs.class_manager import ClassConfigManager
from libs.ai_assistant import YOLOPredictor, ModelManager, BatchProcessor, ConfidenceFilter
from libs.batch_operations import BatchOperations, BatchOperationsDialog
from libs.shortcut_manager import ShortcutManager, ShortcutConfigDialog


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
        print(f"[DEBUG] PyInstaller环境检测到，使用_MEIPASS路径: {base_path}")
    except AttributeError:
        # 开发环境中使用当前文件的目录
        base_path = os.path.dirname(__file__)
        print(f"[DEBUG] 开发环境检测到，使用当前文件目录: {base_path}")

    full_path = os.path.join(base_path, relative_path)
    print(f"[DEBUG] 资源文件完整路径: {full_path}")
    print(f"[DEBUG] 资源文件是否存在: {os.path.exists(full_path)}")

    return full_path


def get_persistent_predefined_classes_path():
    """获取持久化的预设类文件路径，用于保存用户自定义的标签"""
    try:
        # 获取用户应用数据目录
        if os.name == 'nt':  # Windows
            app_data_dir = os.path.join(
                os.environ.get('APPDATA', ''), 'labelImg')
        else:  # Linux/Mac
            app_data_dir = os.path.join(os.path.expanduser('~'), '.labelImg')

        # 确保目录存在
        os.makedirs(app_data_dir, exist_ok=True)

        persistent_file = os.path.join(app_data_dir, 'predefined_classes.txt')
        print(f"[DEBUG] 持久化预设类文件路径: {persistent_file}")
        return persistent_file
    except Exception as e:
        print(f"[DEBUG] 获取持久化路径失败: {e}")
        # 如果失败，回退到当前目录
        fallback_path = os.path.join(os.getcwd(), 'predefined_classes.txt')
        print(f"[DEBUG] 使用回退路径: {fallback_path}")
        return fallback_path


def get_initial_predefined_classes_path():
    """获取初始预设类文件路径（从资源中读取默认标签）"""
    return get_resource_path(os.path.join("data", "predefined_classes.txt"))


__appname__ = 'labelImg'

# Material Design样式表
MATERIAL_STYLE = """
/* 主窗口样式 */
QMainWindow {
    background-color: #fafafa;
    color: #212121;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

/* 工具栏样式 */
QToolBar {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f5f5f5);
    border: none;
    border-bottom: 1px solid #e0e0e0;
    spacing: 8px;
    padding: 8px;
}

QToolBar::separator {
    background-color: #e0e0e0;
    width: 1px;
    margin: 4px;
}

/* 工具按钮样式 */
QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px;
    margin: 2px;
    min-width: 60px;
    min-height: 40px;
    color: #424242;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #e3f2fd;
    color: #1976d2;
}

QToolButton:pressed {
    background-color: #bbdefb;
}

QToolButton:checked {
    background-color: #2196f3;
    color: white;
}

/* 停靠窗口样式 */
QDockWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin: 4px;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}

QDockWidget::title {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #2196f3, stop: 1 #1976d2);
    color: white;
    padding: 10px 12px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
    text-align: left;
}

/* 列表控件样式 */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 8px;
    margin: 2px;
    color: #424242;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

QListWidget::item:selected {
    background-color: #e3f2fd;
    color: #1976d2;
    border: 1px solid #2196f3;
}

/* 按钮样式 */
QPushButton {
    background-color: #2196f3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1976d2;
}

QPushButton:pressed {
    background-color: #0d47a1;
}

QPushButton:disabled {
    background-color: #bdbdbd;
    color: #757575;
}

/* 复选框样式 */
QCheckBox {
    color: #424242;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #9e9e9e;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:hover {
    border-color: #2196f3;
}

QCheckBox::indicator:checked {
    background-color: #2196f3;
    border-color: #2196f3;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

/* 组合框样式 */
QComboBox {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 20px;
    color: #424242;
}

QComboBox:hover {
    border-color: #2196f3;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzQyNDI0MiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
}

/* 状态栏样式 */
QStatusBar {
    background-color: #f5f5f5;
    border-top: 1px solid #e0e0e0;
    color: #757575;
    font-size: 12px;
    padding: 4px;
}

/* 菜单栏样式 */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    color: #424242;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #e3f2fd;
    color: #1976d2;
}

/* 菜单样式 */
QMenu {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 4px;
    color: #424242;
}

QMenu::item:selected {
    background-color: #e3f2fd;
    color: #1976d2;
}

QMenu::separator {
    height: 1px;
    background-color: #e0e0e0;
    margin: 4px 8px;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #bdbdbd;
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9e9e9e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #bdbdbd;
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9e9e9e;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* 输入框样式 */
QLineEdit {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 8px 12px;
    color: #424242;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #2196f3;
}

/* 标签样式 */
QLabel {
    color: #424242;
    font-size: 13px;
}

/* 分组框样式 */
QGroupBox {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin: 8px 0;
    padding-top: 16px;
    font-weight: 600;
    color: #424242;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    background-color: white;
}
"""


class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            add_actions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # 设置现代化的工具栏样式
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(24, 24))

        if actions:
            add_actions(toolbar, actions)
        self.addToolBar(Qt.TopToolBarArea, toolbar)  # 改为顶部工具栏
        return toolbar


class MainWindow(QMainWindow, WindowMixin):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, default_filename=None, default_prefdef_class_file=None, default_save_dir=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        # 应用Material Design样式
        self.setStyleSheet(MATERIAL_STYLE)

        # Load setting in the main thread
        self.settings = Settings()
        self.settings.load()
        settings = self.settings

        self.os_name = platform.system()

        # Load string bundle for i18n
        self.string_bundle = StringBundle.get_bundle()
        def get_str(str_id): return self.string_bundle.get_string(str_id)

        # Save as Pascal voc xml
        self.default_save_dir = default_save_dir

        # 强制使用XML格式作为默认格式，确保标注文件以XML格式保存
        # 这样可以确保与YOLO导出功能的兼容性
        self.label_file_format = LabelFileFormat.PASCAL_VOC

        # 如果用户之前保存了其他格式设置，我们仍然强制使用XML格式
        # 因为大多数功能（如YOLO导出）都依赖XML格式
        saved_format = settings.get(SETTING_LABEL_FILE_FORMAT, LabelFileFormat.PASCAL_VOC)
        if saved_format != LabelFileFormat.PASCAL_VOC:
            print(f"注意：检测到之前保存的标注格式为 {saved_format}，已重置为XML格式以确保兼容性")
            self.label_file_format = LabelFileFormat.PASCAL_VOC

        # For loading all image under a directory
        self.m_img_list = []
        self.dir_name = None
        self.label_hist = []
        self.last_open_dir = None
        self.cur_img_idx = 0
        self.img_count = len(self.m_img_list)

        # Load last opened directory from settings
        self.last_opened_dir = settings.get(SETTING_LAST_OPENED_DIR, None)

        # Whether we need to save or not.
        self.dirty = False

        self._no_selection_slot = False
        self._beginner = True
        self.screencast = "https://youtu.be/p0nR2YsCY_U"

        # 智能预测相关变量
        self.smart_predict_timer = None
        self.last_smart_predict_path = None
        
        # 初始化类别配置管理器
        try:
            self.class_manager = ClassConfigManager("configs")
            self.class_manager.load_class_config()
            print("[DEBUG] 类别配置管理器初始化成功")
        except Exception as e:
            print(f"[WARNING] 类别配置管理器初始化失败: {e}")
            self.class_manager = None
            
        # 性能优化：标注状态缓存系统
        self.annotation_cache = {}  # 缓存 {image_path: is_annotated}
        self.cache_dirty = True     # 标记缓存是否需要重建
        self.annotation_stats_cache = {
            'total': 0,
            'annotated': 0,
            'cache_valid': False
        }
        print("[DEBUG] 标注状态缓存系统初始化成功")
        
        # 性能优化：延迟状态栏更新系统
        self.status_update_timer = QTimer()
        self.status_update_timer.setSingleShot(True)
        self.status_update_timer.timeout.connect(self._do_update_status_bar_info)
        print("[DEBUG] 延迟状态栏更新系统初始化成功")
        
        # 性能优化：样式缓存系统
        self.style_cache = {
            'format_status_xml': "QLabel { color: #2e7d32; font-weight: bold; background-color: #e8f5e8; padding: 4px 8px; border-radius: 3px; }",
            'format_status_json': "QLabel { color: #1565c0; font-weight: bold; background-color: #e3f2fd; padding: 4px 8px; border-radius: 3px; }",
            'format_status_txt': "QLabel { color: #ef6c00; font-weight: bold; background-color: #fff3e0; padding: 4px 8px; border-radius: 3px; }",
            'progress_bar_normal': "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4caf50, stop:0.5 #66bb6a, stop:1 #81c784); border-radius: 8px; margin: 1px; }",
            'progress_bar_complete': "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2e7d32, stop:0.5 #4caf50, stop:1 #66bb6a); border-radius: 8px; margin: 1px; }",
            'status_annotated': "QLabel { font-weight: 600; padding: 2px 8px; border-radius: 4px; background-color: #e8f5e8; color: #2e7d32; }",
            'status_unannotated': "QLabel { font-weight: 600; padding: 2px 8px; border-radius: 4px; background-color: #fff3e0; color: #f57c00; }",
            'auto_save_enabled': "QLabel { color: #4caf50; font-size: 12px; padding: 4px 8px; background-color: #e8f5e8; border-radius: 4px; border: 1px solid #4caf50; }",
            'auto_save_disabled': "QLabel { color: #757575; font-size: 12px; padding: 4px 8px; background-color: #f5f5f5; border-radius: 4px; }"
        }
        print("[DEBUG] 样式缓存系统初始化成功")

        # Store predefined classes file path for saving
        print(f"[DEBUG] 初始化预设类文件路径...")
        print(
            f"[DEBUG] default_prefdef_class_file参数: {default_prefdef_class_file}")

        # 如果用户指定了自定义文件，则使用用户指定的文件
        if default_prefdef_class_file and not default_prefdef_class_file.endswith(os.path.join("data", "predefined_classes.txt")):
            self.predefined_classes_file = default_prefdef_class_file
            print(f"[DEBUG] 使用用户指定的预设类文件: {self.predefined_classes_file}")
        else:
            # 使用持久化路径保存用户自定义标签
            self.predefined_classes_file = get_persistent_predefined_classes_path()
            print(f"[DEBUG] 使用持久化预设类文件路径: {self.predefined_classes_file}")

        # Load predefined classes to the list
        print(f"[DEBUG] 开始加载预设类文件...")
        self.load_predefined_classes(self.predefined_classes_file)

        print(f"[DEBUG] 检查标签历史记录...")
        if self.label_hist:
            print(f"[DEBUG] 标签历史记录包含 {len(self.label_hist)} 个标签")
            print(f"[DEBUG] 第一个标签: {self.label_hist[0]}")
            self.default_label = self.label_hist[0]
        else:
            print("[DEBUG] 标签历史记录为空")
            print("Not find:/data/predefined_classes.txt (optional)")

        # Main widgets and related state.
        self.label_dialog = LabelDialog(parent=self, list_item=self.label_hist)

        self.items_to_shapes = {}
        self.shapes_to_items = {}
        self.prev_label_text = ''

        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(8, 8, 8, 8)
        list_layout.setSpacing(6)

        # Create a widget for using default label
        self.use_default_label_checkbox = QCheckBox(get_str('useDefaultLabel'))
        self.use_default_label_checkbox.setChecked(False)
        self.default_label_combo_box = DefaultLabelComboBox(
            self, items=self.label_hist)

        use_default_label_qhbox_layout = QHBoxLayout()
        use_default_label_qhbox_layout.setContentsMargins(8, 4, 8, 4)
        use_default_label_qhbox_layout.setSpacing(8)
        use_default_label_qhbox_layout.addWidget(
            self.use_default_label_checkbox)
        use_default_label_qhbox_layout.addWidget(self.default_label_combo_box)
        use_default_label_container = QWidget()
        use_default_label_container.setLayout(use_default_label_qhbox_layout)

        # Create clear predefined labels button
        self.clear_labels_button = QPushButton('🗑️ 清空预设标签')
        self.clear_labels_button.setToolTip('清空所有预设标签（危险操作，不可撤销）')
        self.clear_labels_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border: 2px solid #e64a19;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 11px;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #e64a19;
                border-color: #d84315;
                box-shadow: 0 2px 4px rgba(255, 87, 34, 0.3);
            }
            QPushButton:pressed {
                background-color: #d84315;
                border-color: #bf360c;
            }
        """)
        self.clear_labels_button.clicked.connect(
            self.clear_predefined_classes_with_confirmation)

        # Create switch to unannotated image button
        self.switch_unannotated_button = QPushButton('🎯 切换到未标注图片')
        self.switch_unannotated_button.setToolTip('快速跳转到下一张未标注的图片（最常用功能）')
        self.switch_unannotated_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #4caf50);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb85c, stop:1 #449d44);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #449d44, stop:1 #388e3c);
                transform: translateY(0px);
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        self.switch_unannotated_button.clicked.connect(
            self.switch_to_next_unannotated_image)
        # 初始状态下禁用按钮，直到加载图片列表
        self.switch_unannotated_button.setEnabled(False)

        # Create delete current image button
        self.delete_current_image_button = QPushButton('🗑️ 删除当前图片')
        self.delete_current_image_button.setToolTip(
            '⚠️ 危险操作：删除当前图片\n\n'
            '• 将永久删除图片文件\n'
            '• 同时删除相关标注文件\n'
            '• 此操作不可撤销！\n\n'
            '💡 提示：可在工具菜单中重置删除确认设置'
        )
        self.delete_current_image_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: 2px solid #d32f2f;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
                min-height: 20px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border-color: #c62828;
                box-shadow: 0 4px 8px rgba(244, 67, 54, 0.6);
                transform: translateY(-1px);
                font-size: 13px;
            }
            QPushButton:pressed {
                background-color: #c62828;
                border-color: #b71c1c;
                box-shadow: 0 2px 4px rgba(244, 67, 54, 0.8);
                transform: translateY(0px);
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
                border-color: #bdbdbd;
                box-shadow: none;
            }
        """)
        self.delete_current_image_button.clicked.connect(
            self.delete_current_image)
        # 初始状态下禁用按钮，直到加载图片
        self.delete_current_image_button.setEnabled(False)

        # Create a widget for edit and diffc button
        self.diffc_button = QCheckBox(get_str('useDifficult'))
        self.diffc_button.setChecked(False)
        self.diffc_button.stateChanged.connect(self.button_state)
        self.edit_button = QToolButton()
        self.edit_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 创建有难度复选框的容器，确保对齐
        diffc_layout = QHBoxLayout()
        diffc_layout.setContentsMargins(8, 4, 8, 4)
        diffc_layout.setSpacing(8)
        diffc_layout.addWidget(self.diffc_button)
        diffc_layout.addStretch()  # 添加弹性空间
        diffc_container = QWidget()
        diffc_container.setLayout(diffc_layout)

        # Add some of widgets to list_layout
        list_layout.addWidget(self.edit_button)
        list_layout.addWidget(diffc_container)
        list_layout.addWidget(use_default_label_container)

        # 创建主要操作区域（常用功能）
        main_actions_group = QGroupBox("🎯 主要操作")
        main_actions_group.setStyleSheet("""
            QGroupBox {
                background-color: #f8fff8;
                border: 2px solid #4caf50;
                border-radius: 8px;
                margin: 8px 0;
                padding-top: 16px;
                font-weight: 600;
                color: #2e7d32;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: #f8fff8;
                color: #2e7d32;
            }
        """)
        main_actions_layout = QVBoxLayout(main_actions_group)
        main_actions_layout.setContentsMargins(12, 8, 12, 12)
        main_actions_layout.setSpacing(8)

        # 将切换到未标注图片按钮放在主要操作区域
        main_actions_layout.addWidget(self.switch_unannotated_button)
        list_layout.addWidget(main_actions_group)

        # 添加分隔空间
        spacer = QWidget()
        spacer.setFixedHeight(12)
        list_layout.addWidget(spacer)

        # 创建危险操作区域
        danger_actions_group = QGroupBox("⚠️ 危险操作")
        danger_actions_group.setStyleSheet("""
            QGroupBox {
                background-color: #fff8f0;
                border: 2px solid #ff9800;
                border-radius: 8px;
                margin: 8px 0;
                padding-top: 16px;
                font-weight: 600;
                color: #e65100;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: #fff8f0;
                color: #e65100;
            }
        """)
        danger_actions_layout = QVBoxLayout(danger_actions_group)
        danger_actions_layout.setContentsMargins(12, 8, 12, 12)
        danger_actions_layout.setSpacing(6)

        # 添加警告提示
        warning_label = QLabel("⚠️ 请谨慎操作，以下操作不可撤销")
        warning_label.setStyleSheet("""
            QLabel {
                color: #e65100;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 8px;
                background-color: #ffe0b2;
                border-radius: 4px;
                margin-bottom: 4px;
            }
        """)
        danger_actions_layout.addWidget(warning_label)

        # 将危险操作按钮放在危险操作区域
        danger_actions_layout.addWidget(self.clear_labels_button)
        danger_actions_layout.addWidget(self.delete_current_image_button)
        list_layout.addWidget(danger_actions_group)

        # 添加标签搜索框
        label_search_layout = QHBoxLayout()
        label_search_layout.setContentsMargins(8, 8, 8, 4)
        self.label_search_box = QLineEdit()
        self.label_search_box.setPlaceholderText('🔍 搜索标签...')
        self.label_search_box.textChanged.connect(self.filter_label_list)
        label_search_layout.addWidget(self.label_search_box)
        list_layout.addLayout(label_search_layout)

        # 添加标签统计信息
        self.label_stats_label = QLabel('📊 标签统计: 0 个')
        self.label_stats_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 12px;
                padding: 4px 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
                margin: 4px 8px;
            }
        """)
        list_layout.addWidget(self.label_stats_label)

        # Create and add combobox for showing unique labels in group
        self.combo_box = ComboBox(self)
        list_layout.addWidget(self.combo_box)

        # Create and add a widget for showing current label items
        self.label_list = QListWidget()
        self.label_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
                color: #424242;
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                border-left: 3px solid #2196f3;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border-left: 3px solid #2196f3;
                font-weight: 500;
            }
        """)

        label_list_container = QWidget()
        label_list_container.setLayout(list_layout)
        self.label_list.itemActivated.connect(self.label_selection_changed)
        self.label_list.itemSelectionChanged.connect(
            self.label_selection_changed)
        self.label_list.itemDoubleClicked.connect(self.edit_label)
        # Connect to itemChanged to detect checkbox changes.
        self.label_list.itemChanged.connect(self.label_item_changed)
        list_layout.addWidget(self.label_list)

        # 创建现代化的标签面板
        self.dock = QDockWidget('🏷️ ' + get_str('boxLabelText'), self)
        self.dock.setObjectName(get_str('labels'))
        self.dock.setWidget(label_list_container)
        self.dock.setMinimumWidth(280)

        # 创建现代化的文件列表面板
        self.file_list_widget = QListWidget()
        self.file_list_widget.itemDoubleClicked.connect(
            self.file_item_double_clicked)

        # 添加搜索框到文件列表
        file_search_layout = QHBoxLayout()
        file_search_layout.setContentsMargins(8, 8, 8, 4)
        self.file_search_box = QLineEdit()
        self.file_search_box.setPlaceholderText('🔍 搜索文件...')
        self.file_search_box.textChanged.connect(self.filter_file_list)
        file_search_layout.addWidget(self.file_search_box)

        file_list_layout = QVBoxLayout()
        file_list_layout.setContentsMargins(8, 8, 8, 8)
        file_list_layout.setSpacing(6)
        file_list_layout.addLayout(file_search_layout)
        file_list_layout.addWidget(self.file_list_widget)

        file_list_container = QWidget()
        file_list_container.setLayout(file_list_layout)
        self.file_dock = QDockWidget('📁 ' + get_str('fileList'), self)
        self.file_dock.setObjectName(get_str('files'))
        self.file_dock.setWidget(file_list_container)
        self.file_dock.setMinimumWidth(280)

        self.zoom_widget = ZoomWidget()
        self.light_widget = LightWidget(get_str('lightWidgetTitle'))
        self.color_dialog = ColorDialog(parent=self)

        # 创建主工作区域
        self.main_widget = QWidget()
        self.main_layout = QStackedLayout(self.main_widget)

        # 创建欢迎界面
        self.welcome_widget = self.create_welcome_widget()
        self.main_layout.addWidget(self.welcome_widget)

        # 创建画布
        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoom_request)
        self.canvas.lightRequest.connect(self.light_request)
        self.canvas.set_drawing_shape_to_square(
            settings.get(SETTING_DRAW_SQUARE, False))

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.main_layout.addWidget(scroll)
        self.scroll_bars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.scroll_area = scroll
        self.canvas.scrollRequest.connect(self.scroll_request)

        self.canvas.newShape.connect(self.new_shape)
        self.canvas.shapeMoved.connect(self.set_dirty)
        self.canvas.selectionChanged.connect(self.shape_selection_changed)
        self.canvas.drawingPolygon.connect(self.toggle_drawing_sensitive)

        self.setCentralWidget(self.main_widget)

        # 设置停靠窗口的现代化布局
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.file_dock)

        # 设置停靠窗口特性
        self.dock_features = QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        self.dock.setFeatures(self.dock_features)
        self.file_dock.setFeatures(self.dock_features)

        # 设置停靠窗口的标签化显示
        self.setTabPosition(Qt.RightDockWidgetArea, QTabWidget.North)
        self.tabifyDockWidget(self.dock, self.file_dock)
        # 注意：AI助手面板将在后续初始化时设置为默认显示

        # Actions
        action = partial(new_action, self)
        quit = action(get_str('quit'), self.close,
                      'Ctrl+Q', 'quit', get_str('quitApp'))

        open = action(get_str('openFile'), self.open_file,
                      'Ctrl+O', 'open', get_str('openFileDetail'))

        open_dir = action(get_str('openDir'), self.open_dir_dialog,
                          'Ctrl+u', 'open', get_str('openDir'))

        change_save_dir = action(get_str('changeSaveDir'), self.change_save_dir_dialog,
                                 'Ctrl+r', 'open', get_str('changeSavedAnnotationDir'))

        open_annotation = action(get_str('openAnnotation'), self.open_annotation_dialog,
                                 'Ctrl+Shift+O', 'open', get_str('openAnnotationDetail'))
        copy_prev_bounding = action(get_str(
            'copyPrevBounding'), self.copy_previous_bounding_boxes, 'Ctrl+v', 'copy', get_str('copyPrevBounding'))

        export_yolo = action(get_str('exportYOLO'), self.export_yolo_dataset,
                             'Ctrl+Shift+E', 'export', get_str('exportYOLODetail'))

        export_model = action(get_str('exportModel'), self.export_model,
                             'Ctrl+Shift+M', 'export', get_str('exportModelDetail'))

        open_next_image = action(get_str('nextImg'), self.open_next_image,
                                 'd', 'next', get_str('nextImgDetail'))

        open_prev_image = action(get_str('prevImg'), self.open_prev_image,
                                 'a', 'prev', get_str('prevImgDetail'))

        verify = action(get_str('verifyImg'), self.verify_image,
                        'space', 'verify', get_str('verifyImgDetail'))

        save = action(get_str('save'), self.save_file,
                      'Ctrl+S', 'save', get_str('saveDetail'), enabled=False)

        def get_format_meta(format):
            """
            returns a tuple containing (title, icon_name) of the selected format
            """
            if format == LabelFileFormat.PASCAL_VOC:
                return '&PascalVOC', 'format_voc'
            elif format == LabelFileFormat.YOLO:
                return '&YOLO', 'format_yolo'
            elif format == LabelFileFormat.CREATE_ML:
                return '&CreateML', 'format_createml'

        save_format = action(get_format_meta(self.label_file_format)[0],
                             self.change_format, 'Ctrl+Y',
                             get_format_meta(self.label_file_format)[1],
                             get_str('changeSaveFormat'), enabled=True)

        save_as = action(get_str('saveAs'), self.save_file_as,
                         'Ctrl+Shift+S', 'save-as', get_str('saveAsDetail'), enabled=False)

        close = action(get_str('closeCur'), self.close_file,
                       'Ctrl+W', 'close', get_str('closeCurDetail'))

        delete_image = action(get_str('deleteImg'), self.delete_image,
                              'Ctrl+Shift+D', 'close', get_str('deleteImgDetail'))

        # 文件列表相关的actions
        remove_from_list = action('从列表移除', self.remove_file_from_list,
                                  None, 'remove', '从列表中移除文件，但保留磁盘文件')
        delete_file_permanently = action('彻底删除', self.delete_file_permanently,
                                         None, 'delete', '从磁盘彻底删除文件')
        show_in_explorer = action('在文件管理器中显示', self.show_file_in_explorer,
                                  None, 'folder', '在文件管理器中显示文件位置')

        reset_all = action(get_str('resetAll'), self.reset_all,
                           None, 'resetall', get_str('resetAllDetail'))

        color1 = action(get_str('boxLineColor'), self.choose_color1,
                        'Ctrl+L', 'color_line', get_str('boxLineColorDetail'))

        create_mode = action(get_str('crtBox'), self.set_create_mode,
                             'w', 'new', get_str('crtBoxDetail'), enabled=False)
        edit_mode = action(get_str('editBox'), self.set_edit_mode,
                           'Ctrl+J', 'edit', get_str('editBoxDetail'), enabled=False)

        create = action(get_str('crtBox'), self.create_shape,
                        'w', 'new', get_str('crtBoxDetail'), enabled=False)
        delete = action(get_str('delBox'), self.delete_selected_shape,
                        'Delete', 'delete', get_str('delBoxDetail'), enabled=False)
        copy = action(get_str('dupBox'), self.copy_selected_shape,
                      'Ctrl+D', 'copy', get_str('dupBoxDetail'),
                      enabled=False)

        advanced_mode = action(get_str('advancedMode'), self.toggle_advanced_mode,
                               'Ctrl+Shift+A', 'expert', get_str(
                                   'advancedModeDetail'),
                               checkable=True)

        hide_all = action(get_str('hideAllBox'), partial(self.toggle_polygons, False),
                          'Ctrl+H', 'hide', get_str('hideAllBoxDetail'),
                          enabled=False)
        show_all = action(get_str('showAllBox'), partial(self.toggle_polygons, True),
                          'Ctrl+A', 'hide', get_str('showAllBoxDetail'),
                          enabled=False)

        help_default = action(get_str(
            'tutorialDefault'), self.show_default_tutorial_dialog, None, 'help', get_str('tutorialDetail'))
        show_info = action(get_str('info'), self.show_info_dialog,
                           None, 'help', get_str('info'))
        show_shortcut = action(get_str(
            'shortcut'), self.show_shortcuts_dialog, None, 'help', get_str('shortcut'))

        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoom_widget)
        self.zoom_widget.setWhatsThis(
            u"Zoom in or out of the image. Also accessible with"
            " %s and %s from the canvas." % (format_shortcut("Ctrl+[-+]"),
                                             format_shortcut("Ctrl+Wheel")))
        self.zoom_widget.setEnabled(False)

        zoom_in = action(get_str('zoomin'), partial(self.add_zoom, 10),
                         'Ctrl++', 'zoom-in', get_str('zoominDetail'), enabled=False)
        zoom_out = action(get_str('zoomout'), partial(self.add_zoom, -10),
                          'Ctrl+-', 'zoom-out', get_str('zoomoutDetail'), enabled=False)
        zoom_org = action(get_str('originalsize'), partial(self.set_zoom, 100),
                          'Ctrl+=', 'zoom', get_str('originalsizeDetail'), enabled=False)
        reset_zoom_pref = action('重置缩放偏好', self.reset_zoom_preference,
                                'Ctrl+Shift+R', 'reset', '重置到默认缩放模式', enabled=False)
        fit_window = action(get_str('fitWin'), self.set_fit_window,
                            'Ctrl+F', 'fit-window', get_str('fitWinDetail'),
                            checkable=True, enabled=False)
        fit_width = action(get_str('fitWidth'), self.set_fit_width,
                           'Ctrl+Shift+F', 'fit-width', get_str(
                               'fitWidthDetail'),
                           checkable=True, enabled=False)
        # Group zoom controls into a list for easier toggling.
        zoom_actions = (self.zoom_widget, zoom_in, zoom_out,
                        zoom_org, reset_zoom_pref, fit_window, fit_width)
        self.zoom_mode = self.MANUAL_ZOOM
        self.scalers = {
            self.FIT_WINDOW: self.scale_fit_window,
            self.FIT_WIDTH: self.scale_fit_width,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1,
        }

        light = QWidgetAction(self)
        light.setDefaultWidget(self.light_widget)
        self.light_widget.setWhatsThis(
            u"Brighten or darken current image. Also accessible with"
            " %s and %s from the canvas." % (format_shortcut("Ctrl+Shift+[-+]"),
                                             format_shortcut("Ctrl+Shift+Wheel")))
        self.light_widget.setEnabled(False)

        light_brighten = action(get_str('lightbrighten'), partial(self.add_light, 10),
                                'Ctrl+Shift++', 'light_lighten', get_str('lightbrightenDetail'), enabled=False)
        light_darken = action(get_str('lightdarken'), partial(self.add_light, -10),
                              'Ctrl+Shift+-', 'light_darken', get_str('lightdarkenDetail'), enabled=False)
        light_org = action(get_str('lightreset'), partial(self.set_light, 50),
                           'Ctrl+Shift+=', 'light_reset', get_str('lightresetDetail'), checkable=True, enabled=False)
        light_org.setChecked(True)

        # Group light controls into a list for easier toggling.
        light_actions = (self.light_widget, light_brighten,
                         light_darken, light_org)

        edit = action(get_str('editLabel'), self.edit_label,
                      'Ctrl+E', 'edit', get_str('editLabelDetail'),
                      enabled=False)
        self.edit_button.setDefaultAction(edit)

        shape_line_color = action(get_str('shapeLineColor'), self.choose_shape_line_color,
                                  icon='color_line', tip=get_str('shapeLineColorDetail'),
                                  enabled=False)
        shape_fill_color = action(get_str('shapeFillColor'), self.choose_shape_fill_color,
                                  icon='color', tip=get_str('shapeFillColorDetail'),
                                  enabled=False)

        labels = self.dock.toggleViewAction()
        labels.setText(get_str('showHide'))
        labels.setShortcut('Ctrl+Shift+T')

        # Label list context menu.
        label_menu = QMenu()
        add_actions(label_menu, (edit, delete))
        self.label_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_list.customContextMenuRequested.connect(
            self.pop_label_list_menu)

        # File list context menu.
        file_menu = QMenu()
        add_actions(file_menu, (remove_from_list,
                    delete_file_permanently, None, show_in_explorer))
        self.file_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list_widget.customContextMenuRequested.connect(
            self.pop_file_list_menu)

        # Draw squares/rectangles
        self.draw_squares_option = QAction(get_str('drawSquares'), self)
        self.draw_squares_option.setShortcut('Ctrl+Shift+R')
        self.draw_squares_option.setCheckable(True)
        self.draw_squares_option.setChecked(
            settings.get(SETTING_DRAW_SQUARE, False))
        self.draw_squares_option.triggered.connect(self.toggle_draw_square)

        # ==================== 新功能动作 ====================

        # AI助手相关动作
        # AI功能动作 - 快捷键由shortcut_manager.py管理，避免冲突
        ai_predict_current = action('🤖 AI预测当前图像', self.on_ai_predict_current,
                                    None, 'ai_predict', 'AI预测当前图像')
        ai_predict_batch = action('🔄 AI批量预测', self.on_ai_batch_predict,
                                  None, 'ai_batch', 'AI批量预测')
        ai_toggle_panel = action('🔧 切换AI面板', self.on_ai_toggle_panel,
                                 None, 'ai_panel', '显示/隐藏AI助手面板')

        # 批量操作相关动作 - 快捷键由shortcut_manager.py管理，避免冲突
        batch_operations = action('📦 批量操作', self.show_batch_operations_dialog,
                                  None, 'batch_ops', '批量操作对话框')
        batch_copy = action('📋 批量复制', self.on_batch_copy,
                            None, 'batch_copy', '批量复制标注')
        batch_delete = action('🗑️ 批量删除', self.on_batch_delete,
                              'Ctrl+Shift+D', 'batch_delete', '批量删除标注')

        # 快捷键配置动作
        shortcut_config = action('⌨️ 快捷键配置', self.show_shortcut_config_dialog,
                                 'Ctrl+K', 'shortcut_config', '配置快捷键')

        # 重置删除确认设置动作
        reset_delete_confirmation = action('🔄 重置删除确认', self.reset_delete_confirmation_settings,
                                          None, 'reset_confirmation', '恢复删除确认对话框显示')

        # Store actions for further handling.
        self.actions = Struct(save=save, save_format=save_format, saveAs=save_as, open=open, close=close, resetAll=reset_all, deleteImg=delete_image,
                              lineColor=color1, create=create, delete=delete, edit=edit, copy=copy,
                              createMode=create_mode, editMode=edit_mode, advancedMode=advanced_mode,
                              shapeLineColor=shape_line_color, shapeFillColor=shape_fill_color,
                              zoom=zoom, zoomIn=zoom_in, zoomOut=zoom_out, zoomOrg=zoom_org,
                              fitWindow=fit_window, fitWidth=fit_width,
                              zoomActions=zoom_actions,
                              lightBrighten=light_brighten, lightDarken=light_darken, lightOrg=light_org,
                              lightActions=light_actions,
                              # 新功能动作
                              aiPredictCurrent=ai_predict_current, aiPredictBatch=ai_predict_batch, aiTogglePanel=ai_toggle_panel,
                              batchOperations=batch_operations, batchCopy=batch_copy, batchDelete=batch_delete,
                              shortcutConfig=shortcut_config,
                              fileMenuActions=(
                                  open, open_dir, save, save_as, close, reset_all, quit),
                              beginner=(), advanced=(),
                              editMenu=(edit, copy, delete,
                                        None, color1, self.draw_squares_option),
                              beginnerContext=(create, edit, copy, delete),
                              advancedContext=(create_mode, edit_mode, edit, copy,
                                               delete, shape_line_color, shape_fill_color),
                              onLoadActive=(
                                  close, create, create_mode, edit_mode),
                              onShapesPresent=(save_as, hide_all, show_all))

        self.menus = Struct(
            file=self.menu(get_str('menu_file')),
            edit=self.menu(get_str('menu_edit')),
            view=self.menu(get_str('menu_view')),
            tools=self.menu('工具'),
            help=self.menu(get_str('menu_help')),
            recentFiles=QMenu(get_str('menu_openRecent')),
            labelList=label_menu,
            fileList=file_menu)

        # Auto saving : Enable auto saving if pressing next
        self.auto_saving = QAction(get_str('autoSaveMode'), self)
        self.auto_saving.setCheckable(True)
        self.auto_saving.setChecked(settings.get(SETTING_AUTO_SAVE, True))
        # Sync single class mode from PR#106
        self.single_class_mode = QAction(get_str('singleClsMode'), self)
        self.single_class_mode.setShortcut("Ctrl+Shift+S")
        self.single_class_mode.setCheckable(True)
        self.single_class_mode.setChecked(
            settings.get(SETTING_SINGLE_CLASS, False))
        self.lastLabel = None
        # Add option to enable/disable labels being displayed at the top of bounding boxes
        self.display_label_option = QAction(get_str('displayLabel'), self)
        self.display_label_option.setShortcut("Ctrl+Shift+L")
        self.display_label_option.setCheckable(True)
        self.display_label_option.setChecked(
            settings.get(SETTING_PAINT_LABEL, False))
        self.display_label_option.triggered.connect(
            self.toggle_paint_labels_option)

        add_actions(self.menus.file,
                    (open, open_dir, change_save_dir, open_annotation, copy_prev_bounding, self.menus.recentFiles, save, save_format, save_as, None, export_yolo, export_model, None, close, reset_all, delete_image, quit))
        add_actions(self.menus.help, (help_default, show_info, show_shortcut))
        add_actions(self.menus.view, (
            self.auto_saving,
            self.single_class_mode,
            self.display_label_option,
            labels, advanced_mode, None,
            hide_all, show_all, None,
            zoom_in, zoom_out, zoom_org, None,
            fit_window, fit_width, reset_zoom_pref, None,
            light_brighten, light_darken, light_org))

        # 添加工具菜单项
        add_actions(self.menus.tools, (
            ai_predict_current, ai_predict_batch, ai_toggle_panel, None,
            batch_operations, batch_copy, batch_delete, None,
            shortcut_config, reset_delete_confirmation))

        self.menus.file.aboutToShow.connect(self.update_file_menu)

        # Custom context menu for the canvas widget:
        add_actions(self.canvas.menus[0], self.actions.beginnerContext)
        add_actions(self.canvas.menus[1], (
            action('&Copy here', self.copy_shape),
            action('&Move here', self.move_shape)))

        # 创建现代化的分组工具栏
        self.create_modern_toolbars(open, open_dir, change_save_dir, open_next_image, open_prev_image,
                                    verify, save, save_format, create, copy, delete, create_mode, edit_mode,
                                    zoom_in, zoom, zoom_out, fit_window, fit_width,
                                    light_brighten, light, light_darken, light_org, hide_all, show_all,
                                    ai_predict_current, ai_predict_batch, batch_operations)

        self.actions.beginner = (
            open, open_dir, change_save_dir, open_next_image, open_prev_image, verify, save, save_format, None, create, copy, delete, None,
            zoom_in, zoom, zoom_out, fit_window, fit_width, None,
            light_brighten, light, light_darken, light_org)

        self.actions.advanced = (
            open, open_dir, change_save_dir, open_next_image, open_prev_image, save, save_format, None,
            create_mode, edit_mode, None,
            hide_all, show_all)

        self.statusBar().showMessage('%s started.' % __appname__)
        self.statusBar().show()

        # Application state.
        self.image = QImage()
        self.file_path = ustr(default_filename)
        self.last_open_dir = None
        self.recent_files = []
        self.max_recent = 7
        self.line_color = None
        self.fill_color = None
        self.zoom_level = 100
        self.fit_window = False
        # Add Chris
        self.difficult = False

        # 用户缩放偏好设置
        self.user_preferred_zoom_enabled = False  # 是否启用用户偏好缩放
        self.user_preferred_zoom_mode = self.FIT_WINDOW  # 用户偏好的缩放模式
        self.user_preferred_zoom_value = 100  # 用户偏好的缩放值（百分比）

        # Fix the compatible issue for qt4 and qt5. Convert the QStringList to python list
        if settings.get(SETTING_RECENT_FILES):
            if have_qstring():
                recent_file_qstring_list = settings.get(SETTING_RECENT_FILES)
                self.recent_files = [ustr(i) for i in recent_file_qstring_list]
            else:
                self.recent_files = recent_file_qstring_list = settings.get(
                    SETTING_RECENT_FILES)

        size = settings.get(SETTING_WIN_SIZE, QSize(1366, 768))
        position = QPoint(0, 0)
        saved_position = settings.get(SETTING_WIN_POSE, position)

        # 检查是否是重置后的首次启动（设置文件不存在或为空）
        is_fresh_start = not os.path.exists(
            settings.path) or len(settings.data) == 0

        # Check if there's a saved position and it's valid (only if not fresh start)
        has_valid_saved_position = False
        if not is_fresh_start:
            for i in range(QApplication.desktop().screenCount()):
                if QApplication.desktop().availableGeometry(i).contains(saved_position):
                    position = saved_position
                    has_valid_saved_position = True
                    break

        self.resize(size)

        # If no valid saved position or fresh start, center the window
        if not has_valid_saved_position or is_fresh_start:
            # Get the primary screen geometry
            screen = QApplication.desktop().screenGeometry()
            # Calculate center position
            x = (screen.width() - size.width()) // 2
            y = (screen.height() - size.height()) // 2
            position = QPoint(x, y)

        self.move(position)
        save_dir = ustr(settings.get(SETTING_SAVE_DIR, None))
        self.last_open_dir = ustr(settings.get(SETTING_LAST_OPEN_DIR, None))
        if self.default_save_dir is None and save_dir is not None and os.path.exists(save_dir):
            self.default_save_dir = save_dir
            self.statusBar().showMessage('%s started. Annotation will be saved to %s' %
                                         (__appname__, self.default_save_dir))
            self.statusBar().show()

        self.restoreState(settings.get(SETTING_WIN_STATE, QByteArray()))
        Shape.line_color = self.line_color = QColor(
            settings.get(SETTING_LINE_COLOR, DEFAULT_LINE_COLOR))
        Shape.fill_color = self.fill_color = QColor(
            settings.get(SETTING_FILL_COLOR, DEFAULT_FILL_COLOR))
        self.canvas.set_drawing_color(self.line_color)

        # 加载用户缩放偏好设置
        self.user_preferred_zoom_enabled = settings.get('user_preferred_zoom_enabled', False)
        self.user_preferred_zoom_mode = settings.get('user_preferred_zoom_mode', self.FIT_WINDOW)
        self.user_preferred_zoom_value = settings.get('user_preferred_zoom_value', 100)

        # 确保使用XML格式并正确设置UI
        self.set_format(FORMAT_PASCALVOC)

        # Add chris
        Shape.difficult = self.difficult

        def xbool(x):
            if isinstance(x, QVariant):
                return x.toBool()
            return bool(x)

        if xbool(settings.get(SETTING_ADVANCE_MODE, False)):
            self.actions.advancedMode.setChecked(True)
            self.toggle_advanced_mode()

        # Populate the File menu dynamically.
        self.update_file_menu()

        # Since loading the file may take some time, make sure it runs in the background.
        if self.file_path and os.path.isdir(self.file_path):
            self.queue_event(
                partial(self.import_dir_images, self.file_path or ""))
        elif self.file_path:
            self.queue_event(partial(self.load_file, self.file_path or ""))

        # Callbacks:
        self.zoom_widget.valueChanged.connect(self.paint_canvas)
        self.light_widget.valueChanged.connect(self.paint_canvas)

        self.populate_mode_actions()

        # 创建增强的状态栏
        self.setup_enhanced_status_bar()

        # 创建快捷操作面板
        self.setup_quick_actions_panel()

        # 初始化AI助手系统
        self.setup_ai_assistant()

        # 设置主窗口布局（包含AI助手面板）
        self.setup_main_layout_with_ai_panel()

        # 初始化批量操作系统
        self.setup_batch_operations()

        # 初始化快捷键管理系统
        self.setup_shortcut_manager()

        # Open Dir if default file
        if self.file_path and os.path.isdir(self.file_path):
            self.open_dir_dialog(dir_path=self.file_path, silent=True)
        # Auto-load last opened directory if no file specified
        elif self.last_opened_dir and os.path.exists(self.last_opened_dir):
            self.open_dir_dialog(dir_path=self.last_opened_dir, silent=True)

        # 最终确保状态栏可见（在所有初始化完成后）
        QTimer.singleShot(100, self.ensure_status_bar_visible)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.canvas.set_drawing_shape_to_square(False)

    def filter_file_list(self, text):
        """过滤文件列表"""
        for i in range(self.file_list_widget.count()):
            item = self.file_list_widget.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def filter_label_list(self, text):
        """过滤标签列表"""
        visible_count = 0
        for i in range(self.label_list.count()):
            item = self.label_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
                visible_count += 1
            else:
                item.setHidden(True)

        # 更新统计信息
        total_count = self.label_list.count()
        if text:
            self.label_stats_label.setText(
                f'📊 标签统计: {visible_count}/{total_count} 个 (已过滤)')
        else:
            self.label_stats_label.setText(f'📊 标签统计: {total_count} 个')

    def update_label_stats(self):
        """更新标签统计信息"""
        total_count = self.label_list.count()
        self.label_stats_label.setText(f'📊 标签统计: {total_count} 个')
        # 同时更新状态栏信息
        self.update_status_bar_info()

    def setup_quick_actions_panel(self):
        """设置快捷操作面板"""
        # 创建快捷操作面板
        self.quick_panel = QWidget()
        self.quick_panel.setFixedHeight(50)
        self.quick_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-top: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
            }
        """)

        layout = QHBoxLayout(self.quick_panel)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 快速保存按钮
        quick_save_btn = QPushButton('💾 快速保存')
        quick_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        quick_save_btn.clicked.connect(self.save_file)
        layout.addWidget(quick_save_btn)

        # 自动保存状态指示器
        self.auto_save_indicator = QLabel('🔄 自动保存: 关闭')
        self.auto_save_indicator.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 12px;
                padding: 4px 8px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.auto_save_indicator)

        # 分隔符
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet('color: #e0e0e0;')
        layout.addWidget(separator)

        # 格式选择器
        format_label = QLabel('📄 格式:')
        format_label.setStyleSheet(
            'color: #424242; font-weight: 500; font-size: 12px;')
        layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(['PASCAL VOC', 'YOLO', 'CreateML'])
        self.format_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #2196f3;
            }
        """)
        # 连接格式下拉框变更事件
        self.format_combo.currentTextChanged.connect(self.on_format_combo_changed)
        layout.addWidget(self.format_combo)

        # 弹性空间
        layout.addStretch()

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                font-size: 11px;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #2196f3;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 帮助按钮
        help_btn = QPushButton('❓ 帮助')
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        help_btn.clicked.connect(self.show_help_dialog)
        layout.addWidget(help_btn)

        # 将快捷面板添加到主窗口底部（状态栏上方）
        # 创建一个新的中央部件容器
        central_container = QWidget()
        container_layout = QVBoxLayout(central_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 添加原有的主部件
        container_layout.addWidget(self.main_widget)
        # 添加快捷面板
        container_layout.addWidget(self.quick_panel)

        # 重新设置中央部件
        self.setCentralWidget(central_container)

    def setup_main_layout_with_ai_panel(self):
        """设置包含AI助手面板的主窗口布局"""
        # 创建新的中央容器
        main_container = QWidget()
        main_container_layout = QHBoxLayout(main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)

        # 获取当前的中央部件（包含主工作区域和快捷面板）
        current_central = self.centralWidget()

        # 添加到新布局
        main_container_layout.addWidget(current_central, 1)  # 主区域占据剩余空间
        main_container_layout.addWidget(
            self.collapsible_ai_panel, 0)  # AI面板固定宽度

        # 设置新的中央部件
        self.setCentralWidget(main_container)

    def show_help_dialog(self):
        """显示帮助对话框"""
        help_text = """
        <h3>🏷️ labelImg 使用帮助</h3>

        <h4>📁 文件操作</h4>
        <ul>
        <li><b>Ctrl+O</b> - 打开图片</li>
        <li><b>Ctrl+Shift+O</b> - 打开文件夹</li>
        <li><b>Ctrl+S</b> - 保存标注</li>
        <li><b>Ctrl+D</b> - 复制当前标注框</li>
        <li><b>Ctrl+Shift+E</b> - 导出YOLO数据集</li>
        </ul>

        <h4>🎯 标注操作</h4>
        <ul>
        <li><b>W</b> - 创建标注框</li>
        <li><b>A/D</b> - 上一张/下一张图片</li>
        <li><b>Del</b> - 删除选中的标注框</li>
        <li><b>Ctrl+E</b> - 编辑标签</li>
        </ul>

        <h4>🔍 视图操作</h4>
        <ul>
        <li><b>Ctrl++/-</b> - 放大/缩小</li>
        <li><b>Ctrl+Wheel</b> - 鼠标滚轮缩放</li>
        <li><b>Ctrl+F</b> - 适应窗口</li>
        </ul>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('使用帮助')
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #424242;
            }
        """)
        msg_box.exec_()

    def setup_ai_assistant(self):
        """初始化AI助手系统"""
        try:
            # 创建可折叠AI助手面板
            self.collapsible_ai_panel = CollapsibleAIPanel(self)

            # 获取内部的AI助手面板实例
            self.ai_assistant_panel = self.collapsible_ai_panel.get_ai_panel()

            # 连接AI助手信号
            self.collapsible_ai_panel.prediction_requested.connect(
                self.on_ai_prediction_requested)
            self.collapsible_ai_panel.batch_prediction_requested.connect(
                self.on_ai_batch_prediction_requested)
            self.collapsible_ai_panel.predictions_applied.connect(
                self.on_ai_predictions_applied)
            self.collapsible_ai_panel.predictions_cleared.connect(
                self.on_ai_predictions_cleared)
            self.collapsible_ai_panel.model_changed.connect(
                self.on_ai_model_changed)

            print("[DEBUG] AI助手系统初始化完成")

        except Exception as e:
            print(f"[ERROR] AI助手初始化失败: {str(e)}")

    def setup_batch_operations(self):
        """初始化批量操作系统"""
        try:
            # 创建批量操作管理器
            self.batch_operations = BatchOperations(self)

            # 连接批量操作信号
            self.batch_operations.operation_started.connect(
                self.on_batch_operation_started)
            self.batch_operations.operation_progress.connect(
                self.on_batch_operation_progress)
            self.batch_operations.operation_completed.connect(
                self.on_batch_operation_completed)
            self.batch_operations.operation_error.connect(
                self.on_batch_operation_error)

            print("[DEBUG] 批量操作系统初始化完成")

        except Exception as e:
            print(f"[ERROR] 批量操作初始化失败: {str(e)}")

    def setup_shortcut_manager(self):
        """初始化快捷键管理系统"""
        try:
            # 创建快捷键管理器
            self.shortcut_manager = ShortcutManager(self)

            # 应用快捷键到主窗口
            self.shortcut_manager.apply_shortcuts(self)

            # 连接快捷键信号
            self.shortcut_manager.shortcut_triggered.connect(
                self.on_shortcut_triggered)
            self.shortcut_manager.shortcuts_changed.connect(
                self.on_shortcuts_changed)

            print("[DEBUG] 快捷键管理系统初始化完成")

        except Exception as e:
            print(f"[ERROR] 快捷键管理初始化失败: {str(e)}")

    def setup_enhanced_status_bar(self):
        """设置增强的状态栏"""
        status_bar = self.statusBar()

        # 清空现有的状态栏内容（如果有的话）
        status_bar.clearMessage()

        # 图片信息标签
        self.image_info_label = QLabel('📷 未加载图片')
        status_bar.addPermanentWidget(self.image_info_label)

        # 分隔符
        separator1 = QLabel('|')
        separator1.setStyleSheet('color: #bdbdbd; margin: 0 8px;')
        status_bar.addPermanentWidget(separator1)

        # 当前图片标注统计标签
        self.annotation_stats_label = QLabel('🏷️ 标注: 0')
        status_bar.addPermanentWidget(self.annotation_stats_label)

        # 分隔符
        separator2 = QLabel('|')
        separator2.setStyleSheet('color: #bdbdbd; margin: 0 8px;')
        status_bar.addPermanentWidget(separator2)

        # 缩放信息标签
        self.zoom_info_label = QLabel('🔍 缩放: 100%')
        status_bar.addPermanentWidget(self.zoom_info_label)

        # 分隔符
        separator3 = QLabel('|')
        separator3.setStyleSheet('color: #bdbdbd; margin: 0 8px;')
        status_bar.addPermanentWidget(separator3)

        # 标注进度信息（详细）
        self.annotation_progress_label = QLabel('📈 进度: 0/0 (0%)')
        self.annotation_progress_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                color: #1976d2;
                padding: 2px 6px;
                background-color: #e3f2fd;
                border-radius: 4px;
            }
        """)
        status_bar.addPermanentWidget(self.annotation_progress_label)

        # 添加进度条（增强视觉效果）
        self.annotation_progress_bar = QProgressBar()
        self.annotation_progress_bar.setMinimumWidth(120)
        self.annotation_progress_bar.setMaximumWidth(150)
        self.annotation_progress_bar.setMinimumHeight(20)
        self.annotation_progress_bar.setMaximumHeight(20)
        self.annotation_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1976d2;
                border-radius: 10px;
                text-align: center;
                font-size: 11px;
                font-weight: 700;
                color: #1976d2;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:0.5 #66bb6a, stop:1 #81c784);
                border-radius: 8px;
                margin: 1px;
            }
        """)
        status_bar.addPermanentWidget(self.annotation_progress_bar)

        # 当前图片状态指示器
        self.current_image_status = QLabel('⚪ 未标注')
        self.current_image_status.setStyleSheet("""
            QLabel {
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 4px;
            }
        """)
        status_bar.addPermanentWidget(self.current_image_status)

        # 分隔符
        separator4 = QLabel('|')
        separator4.setStyleSheet('color: #bdbdbd; margin: 0 8px;')
        status_bar.addPermanentWidget(separator4)

        # 鼠标坐标标签
        self.label_coordinates = QLabel('📍 坐标: (0, 0)')
        status_bar.addPermanentWidget(self.label_coordinates)

        # 分隔符
        separator5 = QLabel('|')
        separator5.setStyleSheet('color: #bdbdbd; margin: 0 8px;')
        status_bar.addPermanentWidget(separator5)

        # 当前位置信息标签
        self.position_label = QLabel('📊 位置: 0/0')
        status_bar.addPermanentWidget(self.position_label)

        # 分隔符
        separator6 = QLabel('|')
        separator6.setStyleSheet('color: #bdbdbd; margin: 0 8px;')
        status_bar.addPermanentWidget(separator6)

        # 保存格式状态标签
        self.format_status_label = QLabel('📄 格式: XML')
        self.format_status_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                color: #1976d2;
                padding: 2px 8px;
                background-color: #e3f2fd;
                border-radius: 4px;
                min-width: 80px;
            }
        """)
        status_bar.addPermanentWidget(self.format_status_label)

        # 初始化状态栏信息
        self.update_status_bar_info()
        
        # 初始化格式显示
        self.update_format_display()

        # 强制显示状态栏（防止restoreState隐藏状态栏）
        status_bar.setVisible(True)
        status_bar.show()

        print("[DEBUG] 状态栏设置完成，强制显示状态栏")

    def ensure_status_bar_visible(self):
        """确保状态栏可见（在初始化完成后调用）"""
        status_bar = self.statusBar()
        status_bar.setVisible(True)
        status_bar.show()
        print(f"[DEBUG] 最终确保状态栏可见: {status_bar.isVisible()}")

    def update_status_bar_info(self):
        """
        更新状态栏信息（性能优化版：延迟执行，防抖动）
        频繁调用时只执行最后一次，避免不必要的UI更新
        """
        # 取消之前的延迟更新请求
        if hasattr(self, 'status_update_timer') and self.status_update_timer.isActive():
            self.status_update_timer.stop()
        
        # 启动新的延迟更新（100ms后执行）
        if hasattr(self, 'status_update_timer'):
            self.status_update_timer.start(100)  # 100ms延迟
        else:
            # 如果定时器还未初始化，直接执行（兼容性）
            self._do_update_status_bar_info()

    def _do_update_status_bar_info(self):
        """
        实际执行状态栏更新（延迟执行版本）
        这是原来 update_status_bar_info 的重命名版本
        """
        # 更新图片信息
        if hasattr(self, 'image') and not self.image.isNull():
            width, height = self.image.width(), self.image.height()
            self.image_info_label.setText(f'📷 {width}×{height}px')
        else:
            self.image_info_label.setText('📷 未加载图片')

        # 更新当前图片标注统计
        if hasattr(self, 'label_list'):
            count = self.label_list.count()
            self.annotation_stats_label.setText(f'🏷️ 当前: {count}个')

        # 更新缩放信息
        if hasattr(self, 'zoom_widget'):
            zoom = self.zoom_widget.value()
            zoom_text = f'🔍 缩放: {zoom}%'

            # 添加用户偏好缩放的提示
            if hasattr(self, 'user_preferred_zoom_enabled') and self.user_preferred_zoom_enabled:
                if self.zoom_mode == self.MANUAL_ZOOM:
                    zoom_text += ' (自定义)'
                elif self.zoom_mode == self.FIT_WINDOW:
                    zoom_text += ' (适应窗口*)'
                elif self.zoom_mode == self.FIT_WIDTH:
                    zoom_text += ' (适应宽度*)'

            self.zoom_info_label.setText(zoom_text)

        # 使用缓存的统计信息（性能优化）
        stats = self.calculate_annotation_statistics()

        # 更新进度标签（优化显示格式）
        if stats["total"] > 0:
            progress_text = f'📈 已标注: {stats["annotated"]} | 未标注: {stats["unannotated"]} | 总计: {stats["total"]} ({stats["percentage"]:.1f}%)'
        else:
            progress_text = '📈 暂无图片'
        self.annotation_progress_label.setText(progress_text)

        # 性能优化：智能工具提示缓存系统
        # 只有当统计数据真正改变时才重建工具提示
        tooltip_cache_key = f"{stats['annotated']}_{stats['total']}_{stats['current_index']}_{stats['current_annotated']}"
        if not hasattr(self, '_tooltip_cache_key') or self._tooltip_cache_key != tooltip_cache_key:
            self._tooltip_cache_key = tooltip_cache_key
            if stats["total"] > 0:
                remaining = stats["unannotated"]
                completion_rate = stats["percentage"]

                # 创建更丰富的工具提示
                self._cached_tooltip = (
                    f'📊 标注进度详细统计\n'
                    f'{"="*30}\n\n'
                    f'✅ 已标注图片: {stats["annotated"]} 张\n'
                    f'⚪ 未标注图片: {stats["unannotated"]} 张\n'
                    f'📁 图片总数: {stats["total"]} 张\n'
                    f'📈 完成进度: {completion_rate:.1f}%\n\n'
                    f'🎯 当前位置: 第 {stats["current_index"]} 张\n'
                    f'📍 当前状态: {"✅ 已标注" if stats["current_annotated"] else "⚪ 未标注"}\n\n'
                )

                if remaining > 0:
                    self._cached_tooltip += f'💡 提示: 还需标注 {remaining} 张图片才能完成'
                    if completion_rate > 50:
                        self._cached_tooltip += f'\n🎯 加油！已经完成了一半以上'
                else:
                    self._cached_tooltip += f'🎉 恭喜！所有图片都已标注完成\n✨ 可以开始训练模型了'
            else:
                self._cached_tooltip = (
                    f'📂 尚未加载图片\n'
                    f'{"="*20}\n\n'
                    f'💡 请先打开图片目录\n'
                    f'📁 文件 → 打开目录'
                )

        self.annotation_progress_label.setToolTip(self._cached_tooltip)

        # 更新进度条 - 使用动态样式缓存
        progress_percentage = int(stats["percentage"])
        self.annotation_progress_bar.setValue(progress_percentage)
        self.annotation_progress_bar.setFormat(f'{stats["percentage"]:.1f}%')
        
        # 根据进度动态选择样式（性能优化：使用缓存）
        if hasattr(self, 'style_cache'):
            if progress_percentage >= 100:
                progress_style_key = 'progress_bar_complete'
            else:
                progress_style_key = 'progress_bar_normal'
            
            # 只有样式需要改变时才更新（避免不必要的DOM操作）
            current_style_key = getattr(self, '_current_progress_style', None)
            if current_style_key != progress_style_key:
                # 基础样式
                base_style = """
                    QProgressBar {
                        border: 2px solid #1976d2;
                        border-radius: 10px;
                        text-align: center;
                        font-size: 11px;
                        font-weight: 700;
                        color: #1976d2;
                        background-color: #f5f5f5;
                    }
                """
                full_style = base_style + self.style_cache[progress_style_key]
                self.annotation_progress_bar.setStyleSheet(full_style)
                self._current_progress_style = progress_style_key

        # 为进度条设置工具提示（使用缓存优化）
        bar_tooltip_cache_key = f"bar_{stats['percentage']:.1f}_{stats['total']}"
        if not hasattr(self, '_bar_tooltip_cache_key') or self._bar_tooltip_cache_key != bar_tooltip_cache_key:
            self._bar_tooltip_cache_key = bar_tooltip_cache_key
            
            if stats["total"] > 0:
                bar_tooltip = (
                    f'📊 可视化进度条\n'
                    f'{"="*20}\n\n'
                    f'📈 完成进度: {stats["percentage"]:.1f}%\n'
                    f'✅ 已完成: {stats["annotated"]} 张\n'
                    f'⚪ 剩余: {stats["unannotated"]} 张\n'
                    f'📁 总计: {stats["total"]} 张'
                )
                if stats["percentage"] == 100:
                    bar_tooltip += f'\n\n🎉 全部完成！'
                elif stats["percentage"] >= 75:
                    bar_tooltip += f'\n\n🎯 即将完成！'
                elif stats["percentage"] >= 50:
                    bar_tooltip += f'\n\n💪 已过半程！'
                elif stats["percentage"] >= 25:
                    bar_tooltip += f'\n\n🚀 进展顺利！'
                else:
                    bar_tooltip += f'\n\n📝 刚刚开始'
            else:
                bar_tooltip = (
                    f'📊 进度条\n'
                    f'{"="*15}\n\n'
                    f'💡 请先加载图片目录'
                )
            self._cached_bar_tooltip = bar_tooltip
        
        self.annotation_progress_bar.setToolTip(self._cached_bar_tooltip)

        # 更新当前图片状态指示器 - 使用缓存样式
        if stats["current_annotated"]:
            self.current_image_status.setText('✅ 已标注')
            if hasattr(self, 'style_cache'):
                self.current_image_status.setStyleSheet(self.style_cache['status_annotated'])
        else:
            self.current_image_status.setText('⚪ 未标注')
            if hasattr(self, 'style_cache'):
                self.current_image_status.setStyleSheet(self.style_cache['status_unannotated'])

        # 更新位置信息
        self.position_label.setText(f'📊 位置: {stats["current_index"]}/{stats["total"]}')

        # 更新自动保存状态 - 使用缓存样式
        if hasattr(self, 'auto_save_indicator'):
            if hasattr(self, 'auto_saving') and self.auto_saving.isChecked():
                self.auto_save_indicator.setText('✅ 自动保存: 开启')
                if hasattr(self, 'style_cache'):
                    self.auto_save_indicator.setStyleSheet(self.style_cache['auto_save_enabled'])
            else:
                self.auto_save_indicator.setText('❌ 自动保存: 关闭')
                if hasattr(self, 'style_cache'):
                    self.auto_save_indicator.setStyleSheet(self.style_cache['auto_save_disabled'])
        
        print("[PERF] 状态栏更新完成")

    def update_format_display(self):
        """更新格式显示状态"""
        if not hasattr(self, 'format_status_label'):
            return
            
        format_info = {
            LabelFileFormat.PASCAL_VOC: {
                'emoji': '📄',
                'name': 'XML',
                'style_key': 'format_status_xml'
            },
            LabelFileFormat.CREATE_ML: {
                'emoji': '📋', 
                'name': 'JSON',
                'style_key': 'format_status_json'
            },
            LabelFileFormat.YOLO: {
                'emoji': '📝',
                'name': 'TXT', 
                'style_key': 'format_status_txt'
            }
        }
        
        current_format = getattr(self, 'label_file_format', LabelFileFormat.PASCAL_VOC)
        info = format_info.get(current_format, format_info[LabelFileFormat.PASCAL_VOC])
        
        # 更新状态栏显示 - 使用缓存的样式
        self.format_status_label.setText(f"{info['emoji']} 格式: {info['name']}")
        
        # 使用缓存的样式而不是重新生成CSS
        if hasattr(self, 'style_cache') and info['style_key'] in self.style_cache:
            self.format_status_label.setStyleSheet(self.style_cache[info['style_key']])
        
        # 同步下拉框选中项（避免循环调用）
        if hasattr(self, 'format_combo'):
            combo_index = {
                LabelFileFormat.PASCAL_VOC: 0,  # 'PASCAL VOC'
                LabelFileFormat.YOLO: 1,        # 'YOLO'  
                LabelFileFormat.CREATE_ML: 2    # 'CreateML'
            }.get(current_format, 0)
            
            # 临时断开信号，避免循环触发
            self.format_combo.blockSignals(True)
            self.format_combo.setCurrentIndex(combo_index)
            self.format_combo.blockSignals(False)

    def on_format_combo_changed(self, format_text):
        """处理格式下拉框变更事件"""
        format_mapping = {
            'PASCAL VOC': FORMAT_PASCALVOC,
            'YOLO': FORMAT_YOLO,
            'CreateML': FORMAT_CREATEML
        }
        
        new_format = format_mapping.get(format_text)
        if new_format and new_format != self.get_current_format_name():
            self.set_format(new_format)
            
    def get_current_format_name(self):
        """获取当前格式的名称"""
        format_names = {
            LabelFileFormat.PASCAL_VOC: FORMAT_PASCALVOC,
            LabelFileFormat.YOLO: FORMAT_YOLO,
            LabelFileFormat.CREATE_ML: FORMAT_CREATEML
        }
        return format_names.get(self.label_file_format, FORMAT_PASCALVOC)

    def create_welcome_widget(self):
        """创建欢迎界面"""
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #e3f2fd, stop: 1 #ffffff);
            }
        """)

        layout = QVBoxLayout(welcome_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # 主标题
        title_label = QLabel('🏷️ labelImg 标注工具')
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #1976d2;
                background: transparent;
                margin: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel('现代化的图像标注工具，支持多种格式')
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #424242;
                background: transparent;
                margin: 10px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # 快速操作按钮区域
        button_widget = QWidget()
        button_widget.setStyleSheet('background: transparent;')
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(20)

        # 打开图片按钮
        open_image_btn = QPushButton('📁 打开图片')
        open_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        open_image_btn.clicked.connect(self.open_file)
        button_layout.addWidget(open_image_btn)

        # 打开文件夹按钮
        open_dir_btn = QPushButton('📂 打开文件夹')
        open_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        open_dir_btn.clicked.connect(self.open_dir_dialog)
        button_layout.addWidget(open_dir_btn)

        layout.addWidget(button_widget)

        # 功能特性列表
        features_widget = QWidget()
        features_widget.setStyleSheet('background: transparent;')
        features_layout = QVBoxLayout(features_widget)

        features_title = QLabel('✨ 主要功能')
        features_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1976d2;
                background: transparent;
                margin: 20px 0 10px 0;
            }
        """)
        features_title.setAlignment(Qt.AlignCenter)
        features_layout.addWidget(features_title)

        features = [
            '🎯 支持矩形标注框绘制',
            '🏷️ 智能标签管理和分类',
            '💾 多种导出格式 (PASCAL VOC, YOLO, CreateML)',
            '🔍 图像缩放和平移功能',
            '⚡ 快捷键操作提升效率',
            '🌐 中文界面本地化支持'
        ]

        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #424242;
                    background: transparent;
                    padding: 5px;
                }
            """)
            feature_label.setAlignment(Qt.AlignCenter)
            features_layout.addWidget(feature_label)

        layout.addWidget(features_widget)

        return welcome_widget

    def create_modern_toolbars(self, open_action, open_dir, change_save_dir, open_next_image, open_prev_image,
                               verify, save, save_format, create, copy, delete, create_mode, edit_mode,
                               zoom_in, zoom, zoom_out, fit_window, fit_width,
                               light_brighten, light, light_darken, light_org, hide_all, show_all,
                               ai_predict_current, ai_predict_batch, batch_operations):
        """创建现代化的分组工具栏"""

        # 主工具栏
        main_toolbar = self.addToolBar('主要工具')
        main_toolbar.setObjectName('MainToolBar')
        main_toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        main_toolbar.setIconSize(QSize(24, 24))
        main_toolbar.setMovable(False)

        # 文件操作组
        file_group = QWidget()
        file_layout = QHBoxLayout(file_group)
        file_layout.setContentsMargins(8, 4, 8, 4)
        file_layout.setSpacing(4)

        file_label = QLabel('📁 文件')
        file_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        file_layout.addWidget(file_label)

        # 添加文件操作按钮
        file_actions = [open_action, open_dir, save, save_format]
        for action in file_actions:
            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QToolButton:hover {
                    background-color: #e3f2fd;
                }
            """)
            file_layout.addWidget(btn)

        main_toolbar.addWidget(file_group)
        main_toolbar.addSeparator()

        # 导航操作组
        nav_group = QWidget()
        nav_layout = QHBoxLayout(nav_group)
        nav_layout.setContentsMargins(8, 4, 8, 4)
        nav_layout.setSpacing(4)

        nav_label = QLabel('🔄 导航')
        nav_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        nav_layout.addWidget(nav_label)

        nav_actions = [open_prev_image, open_next_image, verify]
        for action in nav_actions:
            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QToolButton:hover {
                    background-color: #e8f5e8;
                }
            """)
            nav_layout.addWidget(btn)

        main_toolbar.addWidget(nav_group)
        main_toolbar.addSeparator()

        # 编辑操作组
        edit_group = QWidget()
        edit_layout = QHBoxLayout(edit_group)
        edit_layout.setContentsMargins(8, 4, 8, 4)
        edit_layout.setSpacing(4)

        edit_label = QLabel('✏️ 编辑')
        edit_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        edit_layout.addWidget(edit_label)

        edit_actions = [create, copy, delete]
        for action in edit_actions:
            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QToolButton:hover {
                    background-color: #fff3e0;
                }
            """)
            edit_layout.addWidget(btn)

        main_toolbar.addWidget(edit_group)
        main_toolbar.addSeparator()

        # 视图操作组
        view_group = QWidget()
        view_layout = QHBoxLayout(view_group)
        view_layout.setContentsMargins(8, 4, 8, 4)
        view_layout.setSpacing(4)

        view_label = QLabel('🔍 视图')
        view_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        view_layout.addWidget(view_label)

        view_actions = [zoom_in, zoom_out, fit_window, fit_width]
        for action in view_actions:
            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QToolButton:hover {
                    background-color: #f3e5f5;
                }
            """)
            view_layout.addWidget(btn)

        main_toolbar.addWidget(view_group)
        main_toolbar.addSeparator()

        # AI助手工具组
        ai_group = QWidget()
        ai_layout = QHBoxLayout(ai_group)
        ai_layout.setContentsMargins(8, 4, 8, 4)
        ai_layout.setSpacing(4)

        ai_label = QLabel('🤖 AI助手')
        ai_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        ai_layout.addWidget(ai_label)

        # 添加AI助手按钮
        ai_actions = [ai_predict_current, ai_predict_batch]
        for action in ai_actions:
            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QToolButton:hover {
                    background-color: #e8f5e8;
                }
            """)
            ai_layout.addWidget(btn)

        main_toolbar.addWidget(ai_group)
        main_toolbar.addSeparator()

        # 批量操作工具组
        batch_group = QWidget()
        batch_layout = QHBoxLayout(batch_group)
        batch_layout.setContentsMargins(8, 4, 8, 4)
        batch_layout.setSpacing(4)

        batch_label = QLabel('📦 批量操作')
        batch_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        batch_layout.addWidget(batch_label)

        # 添加批量操作按钮
        batch_btn = QToolButton()
        batch_btn.setDefaultAction(batch_operations)
        batch_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        batch_btn.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #fff3e0;
            }
        """)
        batch_layout.addWidget(batch_btn)

        main_toolbar.addWidget(batch_group)

        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main_toolbar.addWidget(spacer)

        # 模式切换组
        mode_group = QWidget()
        mode_layout = QHBoxLayout(mode_group)
        mode_layout.setContentsMargins(8, 4, 8, 4)
        mode_layout.setSpacing(4)

        mode_label = QLabel('⚙️ 模式')
        mode_label.setStyleSheet(
            'font-weight: 600; color: #1976d2; margin-right: 8px;')
        mode_layout.addWidget(mode_label)

        mode_actions = [create_mode, edit_mode]
        for action in mode_actions:
            btn = QToolButton()
            btn.setDefaultAction(action)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QToolButton:hover {
                    background-color: #fce4ec;
                }
                QToolButton:checked {
                    background-color: #e91e63;
                    color: white;
                }
            """)
            mode_layout.addWidget(btn)

        main_toolbar.addWidget(mode_group)

        # 保存工具栏引用
        self.tools = main_toolbar

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            # Draw rectangle if Ctrl is pressed
            self.canvas.set_drawing_shape_to_square(True)

    # Support Functions #
    def set_format(self, save_format):
        if save_format == FORMAT_PASCALVOC:
            self.actions.save_format.setText(FORMAT_PASCALVOC)
            self.actions.save_format.setIcon(new_icon("format_voc"))
            self.label_file_format = LabelFileFormat.PASCAL_VOC
            LabelFile.suffix = XML_EXT

        elif save_format == FORMAT_YOLO:
            self.actions.save_format.setText(FORMAT_YOLO)
            self.actions.save_format.setIcon(new_icon("format_yolo"))
            self.label_file_format = LabelFileFormat.YOLO
            LabelFile.suffix = TXT_EXT

        elif save_format == FORMAT_CREATEML:
            self.actions.save_format.setText(FORMAT_CREATEML)
            self.actions.save_format.setIcon(new_icon("format_createml"))
            self.label_file_format = LabelFileFormat.CREATE_ML
            LabelFile.suffix = JSON_EXT
            
        # 更新格式显示
        self.update_format_display()

    def change_format(self):
        if self.label_file_format == LabelFileFormat.PASCAL_VOC:
            self.set_format(FORMAT_YOLO)
        elif self.label_file_format == LabelFileFormat.YOLO:
            self.set_format(FORMAT_CREATEML)
        elif self.label_file_format == LabelFileFormat.CREATE_ML:
            self.set_format(FORMAT_PASCALVOC)
        else:
            raise ValueError('Unknown label file format.')
        self.set_dirty()

    def no_shapes(self):
        return not self.items_to_shapes

    def toggle_advanced_mode(self, value=True):
        self._beginner = not value
        self.canvas.set_editing(True)
        self.populate_mode_actions()
        self.edit_button.setVisible(not value)
        if value:
            self.actions.createMode.setEnabled(True)
            self.actions.editMode.setEnabled(False)
            self.dock.setFeatures(self.dock.features() | self.dock_features)
        else:
            self.dock.setFeatures(self.dock.features() ^ self.dock_features)

    def populate_mode_actions(self):
        if self.beginner():
            tool, menu = self.actions.beginner, self.actions.beginnerContext
        else:
            tool, menu = self.actions.advanced, self.actions.advancedContext
        self.tools.clear()
        add_actions(self.tools, tool)
        self.canvas.menus[0].clear()
        add_actions(self.canvas.menus[0], menu)
        self.menus.edit.clear()
        actions = (self.actions.create,) if self.beginner()\
            else (self.actions.createMode, self.actions.editMode)
        add_actions(self.menus.edit, actions + self.actions.editMenu)

    def set_beginner(self):
        self.tools.clear()
        add_actions(self.tools, self.actions.beginner)

    def set_advanced(self):
        self.tools.clear()
        add_actions(self.tools, self.actions.advanced)

    def set_dirty(self):
        self.dirty = True
        self.actions.save.setEnabled(True)

    def set_clean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.create.setEnabled(True)

    def toggle_actions(self, value=True):
        """Enable/Disable widgets which depend on an opened image."""
        for z in self.actions.zoomActions:
            z.setEnabled(value)
        for z in self.actions.lightActions:
            z.setEnabled(value)
        for action in self.actions.onLoadActive:
            action.setEnabled(value)

        # 控制删除当前图片按钮的状态
        if hasattr(self, 'delete_current_image_button'):
            self.delete_current_image_button.setEnabled(value)

    def queue_event(self, function):
        QTimer.singleShot(0, function)

    def status(self, message, delay=5000):
        self.statusBar().showMessage(message, delay)

    def reset_state(self):
        self.items_to_shapes.clear()
        self.shapes_to_items.clear()
        self.label_list.clear()
        self.file_path = None
        self.image_data = None
        self.label_file = None
        self.canvas.reset_state()
        self.label_coordinates.setText('📍 坐标: (0, 0)')
        self.combo_box.cb.clear()

        # 如果没有图片，切换回欢迎界面
        if not hasattr(self, 'image') or self.image.isNull():
            self.main_layout.setCurrentIndex(0)

    def current_item(self):
        items = self.label_list.selectedItems()
        if items:
            return items[0]
        return None

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        elif len(self.recent_files) >= self.max_recent:
            self.recent_files.pop()
        self.recent_files.insert(0, file_path)

    def beginner(self):
        return self._beginner

    def advanced(self):
        return not self.beginner()

    def show_tutorial_dialog(self, browser='default', link=None):
        if link is None:
            link = self.screencast

        if browser.lower() == 'default':
            wb.open(link, new=2)
        elif browser.lower() == 'chrome' and self.os_name == 'Windows':
            if shutil.which(browser.lower()):  # 'chrome' not in wb._browsers in windows
                wb.register('chrome', None, wb.BackgroundBrowser('chrome'))
            else:
                chrome_path = "D:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                if os.path.isfile(chrome_path):
                    wb.register('chrome', None,
                                wb.BackgroundBrowser(chrome_path))
            try:
                wb.get('chrome').open(link, new=2)
            except:
                wb.open(link, new=2)
        elif browser.lower() in wb._browsers:
            wb.get(browser.lower()).open(link, new=2)

    def show_default_tutorial_dialog(self):
        self.show_tutorial_dialog(browser='default')

    def show_info_dialog(self):
        from libs.__init__ import __version__
        msg = u'Name:{0} \nApp Version:{1} \n{2} '.format(
            __appname__, __version__, sys.version_info)
        QMessageBox.information(self, u'Information', msg)

    def show_shortcuts_dialog(self):
        self.show_tutorial_dialog(
            browser='default', link='https://github.com/tzutalin/labelImg#Hotkeys')

    def create_shape(self):
        assert self.beginner()
        self.canvas.set_editing(False)
        self.actions.create.setEnabled(False)

    def toggle_drawing_sensitive(self, drawing=True):
        """In the middle of drawing, toggling between modes should be disabled."""
        self.actions.editMode.setEnabled(not drawing)
        if not drawing and self.beginner():
            # Cancel creation.
            print('Cancel creation.')
            self.canvas.set_editing(True)
            self.canvas.restore_cursor()
            self.actions.create.setEnabled(True)

    def toggle_draw_mode(self, edit=True):
        self.canvas.set_editing(edit)
        self.actions.createMode.setEnabled(edit)
        self.actions.editMode.setEnabled(not edit)

    def set_create_mode(self):
        assert self.advanced()
        self.toggle_draw_mode(False)

    def set_edit_mode(self):
        assert self.advanced()
        self.toggle_draw_mode(True)
        self.label_selection_changed()

    def update_file_menu(self):
        curr_file_path = self.file_path

        def exists(filename):
            return os.path.exists(filename)
        menu = self.menus.recentFiles
        menu.clear()
        files = [f for f in self.recent_files if f !=
                 curr_file_path and exists(f)]
        for i, f in enumerate(files):
            icon = new_icon('labels')
            action = QAction(
                icon, '&%d %s' % (i + 1, QFileInfo(f).fileName()), self)
            action.triggered.connect(partial(self.load_recent, f))
            menu.addAction(action)

    def pop_label_list_menu(self, point):
        self.menus.labelList.exec_(self.label_list.mapToGlobal(point))

    def pop_file_list_menu(self, point):
        """显示文件列表右键菜单"""
        # 检查是否有选中的文件
        current_item = self.file_list_widget.currentItem()
        if current_item is None:
            return

        # 显示右键菜单
        self.menus.fileList.exec_(self.file_list_widget.mapToGlobal(point))

    def edit_label(self):
        if not self.canvas.editing():
            return
        item = self.current_item()
        if not item:
            return
        text = self.label_dialog.pop_up(item.text())
        if text is not None:
            item.setText(text)
            item.setBackground(generate_color_by_text(text))
            self.set_dirty()
            self.update_combo_box()

    # Tzutalin 20160906 : Add file list and dock to move faster
    def file_item_double_clicked(self, item=None):
        self.cur_img_idx = self.m_img_list.index(ustr(item.text()))
        filename = self.m_img_list[self.cur_img_idx]
        if filename:
            self.load_file(filename)

    # Add chris
    def button_state(self, item=None):
        """ Function to handle difficult examples
        Update on each object """
        if not self.canvas.editing():
            return

        item = self.current_item()
        if not item:  # If not selected Item, take the first one
            item = self.label_list.item(self.label_list.count() - 1)

        difficult = self.diffc_button.isChecked()

        try:
            shape = self.items_to_shapes[item]
        except:
            pass
        # Checked and Update
        try:
            if difficult != shape.difficult:
                shape.difficult = difficult
                self.set_dirty()
            else:  # User probably changed item visibility
                self.canvas.set_shape_visible(
                    shape, item.checkState() == Qt.Checked)
        except:
            pass

    # React to canvas signals.
    def shape_selection_changed(self, selected=False):
        if self._no_selection_slot:
            self._no_selection_slot = False
        else:
            shape = self.canvas.selected_shape
            if shape:
                self.shapes_to_items[shape].setSelected(True)
            else:
                self.label_list.clearSelection()
        self.actions.delete.setEnabled(selected)
        self.actions.copy.setEnabled(selected)
        self.actions.edit.setEnabled(selected)
        self.actions.shapeLineColor.setEnabled(selected)
        self.actions.shapeFillColor.setEnabled(selected)

    def add_label(self, shape):
        shape.paint_label = self.display_label_option.isChecked()
        item = HashableQListWidgetItem(shape.label)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        item.setBackground(generate_color_by_text(shape.label))
        self.items_to_shapes[item] = shape
        self.shapes_to_items[shape] = item
        self.label_list.addItem(item)
        for action in self.actions.onShapesPresent:
            action.setEnabled(True)
        self.update_combo_box()
        self.update_label_stats()  # 更新标签统计

    def remove_label(self, shape):
        if shape is None:
            # print('rm empty label')
            return
        item = self.shapes_to_items[shape]
        self.label_list.takeItem(self.label_list.row(item))
        del self.shapes_to_items[shape]
        del self.items_to_shapes[item]
        self.update_combo_box()
        self.update_label_stats()  # 更新标签统计

    def load_labels(self, shapes):
        s = []
        for label, points, line_color, fill_color, difficult in shapes:
            shape = Shape(label=label)
            for x, y in points:

                # Ensure the labels are within the bounds of the image. If not, fix them.
                x, y, snapped = self.canvas.snap_point_to_canvas(x, y)
                if snapped:
                    self.set_dirty()

                shape.add_point(QPointF(x, y))
            shape.difficult = difficult
            shape.close()
            s.append(shape)

            if line_color:
                shape.line_color = QColor(*line_color)
            else:
                shape.line_color = generate_color_by_text(label)

            if fill_color:
                shape.fill_color = QColor(*fill_color)
            else:
                shape.fill_color = generate_color_by_text(label)

            self.add_label(shape)
        self.update_combo_box()
        self.canvas.load_shapes(s)

    def update_combo_box(self):
        # Get the unique labels and add them to the Combobox.
        items_text_list = [str(self.label_list.item(i).text())
                           for i in range(self.label_list.count())]

        unique_text_list = list(set(items_text_list))
        # Add a null row for showing all the labels
        unique_text_list.append("")
        
        # 使用智能排序：优先按配置文件顺序，然后按字母顺序
        # 确保空字符串在最前面，作为默认选项
        unique_text_list = self.sort_labels_by_config(unique_text_list)

        self.combo_box.update_items(unique_text_list)
        
        # 确保默认选择第一项（空字符串），显示所有标签
        if unique_text_list and unique_text_list[0] == "":
            self.combo_box.cb.setCurrentIndex(0)
            print("[DEBUG] 设置下拉框默认选择第一项（空字符串）")
        else:
            print(f"[DEBUG] 警告：第一项不是空字符串: {unique_text_list[0] if unique_text_list else 'None'}")

    def sort_labels_by_config(self, labels_list):
        """
        根据类别配置文件的顺序对标签进行排序
        
        Args:
            labels_list: 需要排序的标签列表
            
        Returns:
            排序后的标签列表
        """
        if not labels_list:
            return labels_list
            
        print(f"[DEBUG] 开始排序标签: {labels_list}")
        
        # 分离出空字符串（用于显示所有标签的选项）
        empty_labels = [label for label in labels_list if label == ""]
        non_empty_labels = [label for label in labels_list if label != ""]
        
        if not self.class_manager:
            print("[DEBUG] 没有类别管理器，使用字母排序")
            non_empty_labels.sort()
            # 空字符串应该在最前面，作为默认选项
            return empty_labels + non_empty_labels
        
        try:
            # 获取配置文件中的类别顺序
            config_order = self.class_manager.get_class_list()
            print(f"[DEBUG] 配置文件类别顺序: {config_order}")
            
            if not config_order:
                print("[DEBUG] 配置文件为空，使用字母排序")
                non_empty_labels.sort()
                # 空字符串应该在最前面，作为默认选项
                return empty_labels + non_empty_labels
            
            # 创建排序键字典
            sort_keys = {}
            for i, class_name in enumerate(config_order):
                sort_keys[class_name] = i
            
            print(f"[DEBUG] 排序键映射: {sort_keys}")
            
            # 对非空标签进行排序
            def get_sort_key(label):
                if label in sort_keys:
                    return (0, sort_keys[label])  # 配置中的类别，按配置顺序
                else:
                    return (1, label)  # 其他类别，按字母顺序排在最后
            
            sorted_non_empty = sorted(non_empty_labels, key=get_sort_key)
            # 空字符串应该在最前面，作为默认选项，这样下拉框默认显示所有标签
            result = empty_labels + sorted_non_empty
            
            print(f"[DEBUG] 排序完成: {result}")
            print(f"[DEBUG] 配置顺序类别: {[l for l in sorted_non_empty if l in sort_keys]}")
            print(f"[DEBUG] 其他类别: {[l for l in sorted_non_empty if l not in sort_keys]}")
            
            return result
            
        except Exception as e:
            print(f"[WARNING] 标签排序失败，使用默认排序: {e}")
            import traceback
            traceback.print_exc()
            non_empty_labels.sort()
            # 空字符串应该在最前面，作为默认选项
            return empty_labels + non_empty_labels

    def sort_label_items_by_config(self, items_list):
        """
        根据类别配置文件的顺序对标签项目进行排序
        
        Args:
            items_list: 需要排序的QListWidgetItem列表
            
        Returns:
            排序后的items列表
        """
        if not items_list:
            return items_list
            
        print(f"[DEBUG] 开始排序标签项目: {[item.text() for item in items_list]}")
        
        if not self.class_manager:
            print("[DEBUG] 没有类别管理器，使用字母排序")
            items_list.sort(key=lambda item: item.text())
            return items_list
        
        try:
            # 获取配置文件中的类别顺序
            config_order = self.class_manager.get_class_list()
            print(f"[DEBUG] 配置文件类别顺序: {config_order}")
            
            if not config_order:
                print("[DEBUG] 配置文件为空，使用字母排序")
                items_list.sort(key=lambda item: item.text())
                return items_list
            
            # 创建排序键字典
            sort_keys = {}
            for i, class_name in enumerate(config_order):
                sort_keys[class_name] = i
            
            print(f"[DEBUG] 排序键映射: {sort_keys}")
            
            # 对标签项目进行排序
            def get_sort_key(item):
                label = item.text()
                if label in sort_keys:
                    return (0, sort_keys[label])  # 配置中的类别，按配置顺序
                else:
                    return (1, label)  # 其他类别，按字母顺序排在最后
            
            sorted_items = sorted(items_list, key=get_sort_key)
            
            print(f"[DEBUG] 标签项目排序完成: {[item.text() for item in sorted_items]}")
            print(f"[DEBUG] 配置顺序项目: {[item.text() for item in sorted_items if item.text() in sort_keys]}")
            print(f"[DEBUG] 其他项目: {[item.text() for item in sorted_items if item.text() not in sort_keys]}")
            
            return sorted_items
            
        except Exception as e:
            print(f"[WARNING] 标签项目排序失败，使用默认排序: {e}")
            import traceback
            traceback.print_exc()
            items_list.sort(key=lambda item: item.text())
            return items_list

    def refresh_annotation_cache(self):
        """
        刷新标注状态缓存
        只在必要时重建缓存，避免不必要的文件扫描
        """
        if not self.cache_dirty or not hasattr(self, 'm_img_list') or not self.m_img_list:
            return
            
        print(f"[PERF] 开始重建标注状态缓存，图片数量: {len(self.m_img_list)}")
        start_time = time.time()
        
        # 清空旧缓存
        self.annotation_cache.clear()
        annotated_count = 0
        
        # 批量扫描所有图片的标注状态
        for img_path in self.m_img_list:
            is_annotated = self._check_annotation_files_exist(img_path)
            self.annotation_cache[img_path] = is_annotated
            if is_annotated:
                annotated_count += 1
        
        # 更新统计缓存
        self.annotation_stats_cache = {
            'total': len(self.m_img_list),
            'annotated': annotated_count,
            'cache_valid': True
        }
        
        # 标记缓存已更新
        self.cache_dirty = False
        
        end_time = time.time()
        print(f"[PERF] 缓存重建完成，耗时: {end_time - start_time:.3f}秒")
        print(f"[PERF] 缓存统计: {annotated_count}/{len(self.m_img_list)} 已标注")
    
    def _check_annotation_files_exist(self, image_path):
        """
        检查标注文件是否存在（用于缓存构建）
        这是原 is_image_annotated 方法的快速版本
        """
        if not image_path or not os.path.exists(image_path):
            return False

        # 获取图片文件名（不含扩展名）
        basename = os.path.basename(os.path.splitext(image_path)[0])

        # 检查标注文件是否存在
        if self.default_save_dir is not None:
            # 如果设置了默认保存目录，在该目录中查找标注文件
            xml_path = os.path.join(self.default_save_dir, basename + XML_EXT)
            txt_path = os.path.join(self.default_save_dir, basename + TXT_EXT)
            json_path = os.path.join(self.default_save_dir, basename + JSON_EXT)
        else:
            # 否则在图片同目录下查找标注文件
            xml_path = os.path.splitext(image_path)[0] + XML_EXT
            txt_path = os.path.splitext(image_path)[0] + TXT_EXT
            json_path = os.path.splitext(image_path)[0] + JSON_EXT

        # 按优先级检查标注文件是否存在：XML > TXT > JSON
        return (os.path.isfile(xml_path) or
                os.path.isfile(txt_path) or
                os.path.isfile(json_path))
    
    def get_cached_annotation_status(self, image_path):
        """
        快速获取标注状态（使用缓存）
        替代原来的 is_image_annotated 方法
        """
        # 如果缓存失效，先刷新缓存
        if self.cache_dirty:
            self.refresh_annotation_cache()
        
        return self.annotation_cache.get(image_path, False)
    
    def update_annotation_cache(self, image_path, is_annotated):
        """
        更新单个图片的标注状态缓存
        在保存/删除标注时调用
        """
        old_status = self.annotation_cache.get(image_path, False)
        self.annotation_cache[image_path] = is_annotated
        
        # 更新统计计数
        if self.annotation_stats_cache['cache_valid']:
            if is_annotated and not old_status:
                # 新增标注
                self.annotation_stats_cache['annotated'] += 1
                print(f"[PERF] 标注缓存更新: {image_path} -> 已标注")
            elif not is_annotated and old_status:
                # 删除标注
                self.annotation_stats_cache['annotated'] -= 1
                print(f"[PERF] 标注缓存更新: {image_path} -> 未标注")
    
    def invalidate_annotation_cache(self):
        """
        使标注缓存失效
        在图片列表变更时调用
        """
        self.cache_dirty = True
        self.annotation_stats_cache['cache_valid'] = False
        print("[PERF] 标注缓存已失效，将在下次访问时重建")

    def save_labels(self, annotation_file_path):
        annotation_file_path = ustr(annotation_file_path)
        if self.label_file is None:
            self.label_file = LabelFile()
            self.label_file.verified = self.canvas.verified

        def format_shape(s):
            return dict(label=s.label,
                        line_color=s.line_color.getRgb(),
                        fill_color=s.fill_color.getRgb(),
                        points=[(p.x(), p.y()) for p in s.points],
                        # add chris
                        difficult=s.difficult)

        shapes = [format_shape(shape) for shape in self.canvas.shapes]
        # Can add different annotation formats here
        try:
            if self.label_file_format == LabelFileFormat.PASCAL_VOC:
                if annotation_file_path[-4:].lower() != ".xml":
                    annotation_file_path += XML_EXT
                self.label_file.save_pascal_voc_format(annotation_file_path, shapes, self.file_path, self.image_data,
                                                       self.line_color.getRgb(), self.fill_color.getRgb())
            elif self.label_file_format == LabelFileFormat.YOLO:
                if annotation_file_path[-4:].lower() != ".txt":
                    annotation_file_path += TXT_EXT
                self.label_file.save_yolo_format(annotation_file_path, shapes, self.file_path, self.image_data, self.label_hist,
                                                 self.line_color.getRgb(), self.fill_color.getRgb())
            elif self.label_file_format == LabelFileFormat.CREATE_ML:
                if annotation_file_path[-5:].lower() != ".json":
                    annotation_file_path += JSON_EXT
                self.label_file.save_create_ml_format(annotation_file_path, shapes, self.file_path, self.image_data,
                                                      self.label_hist, self.line_color.getRgb(), self.fill_color.getRgb())
            else:
                self.label_file.save(annotation_file_path, shapes, self.file_path, self.image_data,
                                     self.line_color.getRgb(), self.fill_color.getRgb())
            # Fix Unicode encoding error for Chinese paths
            try:
                print(
                    'Image:{0} -> Annotation:{1}'.format(self.file_path, annotation_file_path))
            except UnicodeEncodeError:
                print(
                    'Image and annotation saved successfully (contains non-ASCII characters)')
            
            # 性能优化：更新标注状态缓存
            if self.file_path:
                self.update_annotation_cache(self.file_path, True)
                print(f"[PERF] 标注保存成功，缓存已更新: {self.file_path}")
            
            return True
        except LabelFileError as e:
            self.error_message(u'Error saving label data', u'<b>%s</b>' % e)
            return False

    def copy_selected_shape(self):
        self.add_label(self.canvas.copy_selected_shape())
        # fix copy and delete
        self.shape_selection_changed(True)

    def combo_selection_changed(self, index):
        text = self.combo_box.cb.itemText(index)
        for i in range(self.label_list.count()):
            if text == "":
                self.label_list.item(i).setCheckState(2)
            elif text != self.label_list.item(i).text():
                self.label_list.item(i).setCheckState(0)
            else:
                self.label_list.item(i).setCheckState(2)

    def default_label_combo_selection_changed(self, index):
        # 检查索引是否有效，避免清空标签后的索引越界错误
        if self.label_hist and 0 <= index < len(self.label_hist):
            self.default_label = self.label_hist[index]
        else:
            self.default_label = None

    def label_selection_changed(self):
        item = self.current_item()
        if item and self.canvas.editing():
            self._no_selection_slot = True
            self.canvas.select_shape(self.items_to_shapes[item])
            shape = self.items_to_shapes[item]
            # Add Chris
            self.diffc_button.setChecked(shape.difficult)

    def label_item_changed(self, item):
        shape = self.items_to_shapes[item]
        label = item.text()
        if label != shape.label:
            shape.label = item.text()
            shape.line_color = generate_color_by_text(shape.label)
            self.set_dirty()
        else:  # User probably changed item visibility
            self.canvas.set_shape_visible(
                shape, item.checkState() == Qt.Checked)

    # Callback functions:
    def new_shape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        if not self.use_default_label_checkbox.isChecked():
            if len(self.label_hist) > 0:
                self.label_dialog = LabelDialog(
                    parent=self, list_item=self.label_hist)

            # Sync single class mode from PR#106
            if self.single_class_mode.isChecked() and self.lastLabel:
                text = self.lastLabel
            else:
                text = self.label_dialog.pop_up(text=self.prev_label_text)
                self.lastLabel = text
        else:
            # 检查是否有有效的默认标签
            if self.default_label is not None:
                text = self.default_label
            else:
                # 如果没有默认标签，回退到标签对话框
                if len(self.label_hist) > 0:
                    self.label_dialog = LabelDialog(
                        parent=self, list_item=self.label_hist)
                text = self.label_dialog.pop_up(text=self.prev_label_text)
                self.lastLabel = text

        # Add Chris
        self.diffc_button.setChecked(False)
        if text is not None:
            # 处理中文标签：如果输入的是中文，自动转换为拼音
            original_text = text
            processed_text = process_label_text(text)

            # 如果文本被转换了，显示提示信息
            if original_text != processed_text and has_chinese(original_text):
                print(
                    f"Chinese label '{original_text}' converted to pinyin: '{processed_text}'")

            # 使用处理后的文本
            text = processed_text
            self.prev_label_text = text
            generate_color = generate_color_by_text(text)
            shape = self.canvas.set_last_label(
                text, generate_color, generate_color)
            self.add_label(shape)
            if self.beginner():  # Switch to edit mode.
                self.canvas.set_editing(True)
                self.actions.create.setEnabled(True)
            else:
                self.actions.editMode.setEnabled(True)
            self.set_dirty()

            # 添加到标签历史并自动保存到预设文件
            if text not in self.label_hist:
                print(f"[DEBUG] 新标签 '{text}' 不在历史记录中，准备添加...")
                print(f"[DEBUG] 添加前标签历史记录: {self.label_hist}")
                self.label_hist.append(text)
                print(f"[DEBUG] 添加后标签历史记录: {self.label_hist}")
                print(f"[DEBUG] 准备保存到预设文件: {self.predefined_classes_file}")

                # 自动保存预设标签到文件
                self.save_predefined_classes()

                # 更新默认标签下拉框
                print(f"[DEBUG] 更新默认标签下拉框...")
                self.default_label_combo_box.cb.clear()
                self.default_label_combo_box.cb.addItems(self.label_hist)
                print(
                    f"[DEBUG] 下拉框已更新，当前项目数: {self.default_label_combo_box.cb.count()}")

                # 如果之前没有标签，现在有了，重新启用默认标签功能
                if len(self.label_hist) == 1:
                    print(f"[DEBUG] 这是第一个标签，启用默认标签功能")
                    self.use_default_label_checkbox.setEnabled(True)
                    # 设置第一个标签为默认标签
                    if self.default_label is None:
                        self.default_label = self.label_hist[0]
                        print(f"[DEBUG] 设置默认标签为: {self.default_label}")

                # 通知AI助手面板更新类别信息
                print(f"[DEBUG] 通知AI助手面板更新类别信息...")
                if hasattr(self, 'ai_assistant_panel') and self.ai_assistant_panel:
                    self.ai_assistant_panel.refresh_classes_info()
                    print(f"[DEBUG] AI助手面板类别信息已更新")
                else:
                    print(f"[DEBUG] AI助手面板未初始化，跳过类别信息更新")
            else:
                print(f"[DEBUG] 标签 '{text}' 已存在于历史记录中，跳过添加")
        else:
            # self.canvas.undoLastLine()
            self.canvas.reset_all_lines()

    def scroll_request(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scroll_bars[orientation]
        bar.setValue(int(bar.value() + bar.singleStep() * units))

    def set_zoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoom_mode = self.MANUAL_ZOOM

        # 记录用户手动调整的缩放偏好
        self.user_preferred_zoom_enabled = True
        self.user_preferred_zoom_mode = self.MANUAL_ZOOM
        self.user_preferred_zoom_value = int(value)

        # Arithmetic on scaling factor often results in float
        # Convert to int to avoid type errors
        self.zoom_widget.setValue(int(value))

    def add_zoom(self, increment=10):
        self.set_zoom(self.zoom_widget.value() + increment)

    def zoom_request(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.scroll_bars[Qt.Horizontal]
        v_bar = self.scroll_bars[Qt.Vertical]

        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()

        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)

        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()

        w = self.scroll_area.width()
        h = self.scroll_area.height()

        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)

        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)

        # zoom in
        units = delta // (8 * 15)
        scale = 10
        self.add_zoom(scale * units)

        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max

        # get the new scrollbar values
        new_h_bar_value = int(h_bar.value() + move_x * d_h_bar_max)
        new_v_bar_value = int(v_bar.value() + move_y * d_v_bar_max)

        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)

    def light_request(self, delta):
        self.add_light(5*delta // (8 * 15))

    def set_fit_window(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
            # 记录用户选择的缩放模式偏好
            self.user_preferred_zoom_enabled = True
            self.user_preferred_zoom_mode = self.FIT_WINDOW
        self.zoom_mode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjust_scale()

    def set_fit_width(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
            # 记录用户选择的缩放模式偏好
            self.user_preferred_zoom_enabled = True
            self.user_preferred_zoom_mode = self.FIT_WIDTH
        self.zoom_mode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjust_scale()

    def set_light(self, value):
        self.actions.lightOrg.setChecked(int(value) == 50)
        # Arithmetic on scaling factor often results in float
        # Convert to int to avoid type errors
        self.light_widget.setValue(int(value))

    def add_light(self, increment=10):
        self.set_light(self.light_widget.value() + increment)

    def toggle_polygons(self, value):
        for item, shape in self.items_to_shapes.items():
            item.setCheckState(Qt.Checked if value else Qt.Unchecked)

    def load_file(self, file_path=None):
        """Load the specified file, or the last opened file if None."""
        self.reset_state()
        self.canvas.setEnabled(False)
        if file_path is None:
            file_path = self.settings.get(SETTING_FILENAME)
        # Make sure that filePath is a regular python string, rather than QString
        file_path = ustr(file_path)

        # 性能优化：缓存路径计算，避免重复调用
        unicode_file_path = ustr(file_path)
        
        # 只有当文件路径真正改变时才重新计算绝对路径
        if not hasattr(self, '_cached_file_path') or self._cached_file_path != unicode_file_path:
            unicode_file_path = os.path.abspath(unicode_file_path)
            self._cached_file_path = unicode_file_path
            self._cached_basename = os.path.basename(unicode_file_path)
        else:
            unicode_file_path = self._cached_file_path
        # Tzutalin 20160906 : Add file list and dock to move faster
        # Highlight the file item
        if unicode_file_path and self.file_list_widget.count() > 0:
            if unicode_file_path in self.m_img_list:
                index = self.m_img_list.index(unicode_file_path)
                file_widget_item = self.file_list_widget.item(index)
                file_widget_item.setSelected(True)
            else:
                self.file_list_widget.clear()
                self.m_img_list.clear()

        if unicode_file_path and os.path.exists(unicode_file_path):
            if LabelFile.is_label_file(unicode_file_path):
                try:
                    self.label_file = LabelFile(unicode_file_path)
                except LabelFileError as e:
                    self.error_message(u'Error opening file',
                                       (u"<p><b>%s</b></p>"
                                        u"<p>Make sure <i>%s</i> is a valid label file.")
                                       % (e, unicode_file_path))
                    self.status("Error reading %s" % unicode_file_path)

                    return False
                self.image_data = self.label_file.image_data
                self.line_color = QColor(*self.label_file.lineColor)
                self.fill_color = QColor(*self.label_file.fillColor)
                self.canvas.verified = self.label_file.verified
            else:
                # Load image:
                # read data first and store for saving into label file.
                self.image_data = read(unicode_file_path, None)
                self.label_file = None
                self.canvas.verified = False

            if isinstance(self.image_data, QImage):
                image = self.image_data
            else:
                image = QImage.fromData(self.image_data)
            if image.isNull():
                self.error_message(u'Error opening file',
                                   u"<p>Make sure <i>%s</i> is a valid image file." % unicode_file_path)
                self.status("Error reading %s" % unicode_file_path)
                return False
            self.status("Loaded %s" % self._cached_basename)
            self.image = image
            self.file_path = unicode_file_path
            self.canvas.load_pixmap(QPixmap.fromImage(image))
            if self.label_file:
                self.load_labels(self.label_file.shapes)
            self.set_clean()
            self.canvas.setEnabled(True)

            # 延迟缩放计算，确保窗口完全初始化
            from PyQt5.QtCore import QTimer

            def delayed_scale_adjustment():
                self.adjust_scale(initial=True)
                self.paint_canvas()

            QTimer.singleShot(50, delayed_scale_adjustment)  # 50ms延迟
            self.add_recent_file(self.file_path)
            self.toggle_actions(True)
            # 只有当加载的是图片文件（而不是标注文件）时，才查找对应的标注文件
            # 这避免了重复加载同一个标注文件的问题
            if not self.label_file:
                self.show_bounding_box_from_annotation_file(self.file_path)

            # 性能优化：批量UI更新，减少重绘次数
            # 暂停状态栏自动更新
            if hasattr(self, 'status_update_timer'):
                self.status_update_timer.stop()
            
            # 批量更新UI组件
            self.update_switch_button_state()
            
            counter = self.counter_str()
            self.setWindowTitle(__appname__ + ' ' + file_path + ' ' + counter)

            # Default : select last item if there is at least one item
            if self.label_list.count():
                self.label_list.setCurrentItem(
                    self.label_list.item(self.label_list.count() - 1))
                self.label_list.item(
                    self.label_list.count() - 1).setSelected(True)

            self.canvas.setFocus(True)

            # 切换到画布视图
            self.main_layout.setCurrentIndex(1)

            # 智能预测：如果开启了智能预测且当前图片未标注，则自动执行预测
            self.trigger_smart_prediction_if_needed()

            # 延迟更新状态栏信息，避免加载过程中的频繁更新
            if hasattr(self, 'status_update_timer'):
                self.status_update_timer.start(100)  # 100ms延迟批量更新
            else:
                self.update_status_bar_info()

            return True
        return False

    def counter_str(self):
        """
        Converts image counter to string representation.
        """
        return '[{} / {}]'.format(self.cur_img_idx + 1, self.img_count)

    def is_image_annotated(self, image_path):
        """
        检查指定图片是否已经标注（性能优化版）
        使用缓存系统避免重复的文件I/O操作
        
        Args:
            image_path (str): 图片文件路径

        Returns:
            bool: True表示已标注，False表示未标注
        """
        return self.get_cached_annotation_status(image_path)

    def find_next_unannotated_image(self):
        """
        查找下一张未标注的图片
        从当前位置开始搜索，如果到末尾还没找到则从头开始搜索

        Returns:
            int: 未标注图片的索引，如果没有找到返回-1
        """
        if not self.m_img_list:
            return -1

        total_images = len(self.m_img_list)
        if total_images == 0:
            return -1

        # 从当前位置的下一张开始搜索
        start_idx = (self.cur_img_idx + 1) % total_images

        # 搜索一圈，避免无限循环
        for i in range(total_images):
            check_idx = (start_idx + i) % total_images
            image_path = self.m_img_list[check_idx]

            if not self.is_image_annotated(image_path):
                return check_idx

        # 如果所有图片都已标注，返回-1
        return -1

    def switch_to_next_unannotated_image(self):
        """
        切换到下一张未标注的图片
        """
        # 处理自动保存
        if self.auto_saving.isChecked():
            if self.default_save_dir is not None:
                if self.dirty is True:
                    self.save_file()
            else:
                self.change_save_dir_dialog()
                return

        # 检查是否需要保存当前更改
        if not self.may_continue():
            return

        if not self.m_img_list:
            self.statusBar().showMessage('📂 没有加载图片列表')
            return

        # 显示搜索进度
        self.statusBar().showMessage('🔍 正在搜索未标注图片...')

        # 查找下一张未标注的图片
        next_idx = self.find_next_unannotated_image()

        if next_idx == -1:
            # 没有找到未标注的图片
            total_count = len(self.m_img_list)
            self.statusBar().showMessage(f'✅ 恭喜！所有 {total_count} 张图片都已标注完成！')
            return

        # 如果找到了未标注的图片，切换过去
        if next_idx != self.cur_img_idx:
            old_idx = self.cur_img_idx
            self.cur_img_idx = next_idx
            filename = self.m_img_list[self.cur_img_idx]
            if filename:
                self.load_file(filename)
                # 计算跳过的图片数量
                if next_idx > old_idx:
                    skipped = next_idx - old_idx - 1
                else:
                    skipped = len(self.m_img_list) - old_idx + next_idx - 1

                if skipped > 0:
                    self.statusBar().showMessage(
                        f'🎯 已切换到未标注图片: {os.path.basename(filename)} (跳过了 {skipped} 张已标注图片)')
                else:
                    self.statusBar().showMessage(
                        f'🎯 已切换到未标注图片: {os.path.basename(filename)}')
        else:
            # 当前图片就是未标注的
            self.statusBar().showMessage('📍 当前图片尚未标注')

    def calculate_annotation_statistics(self):
        """
        计算详细的标注统计信息（性能优化版）
        使用缓存系统，避免重复遍历和文件检查

        Returns:
            dict: 包含标注统计信息的字典
        """
        if not hasattr(self, 'm_img_list') or not self.m_img_list:
            return {
                'total': 0,
                'annotated': 0,
                'unannotated': 0,
                'percentage': 0.0,
                'current_annotated': False,
                'current_index': 0
            }

        # 确保缓存是最新的
        if self.cache_dirty:
            self.refresh_annotation_cache()

        # 从缓存获取统计信息
        total_images = self.annotation_stats_cache['total']
        annotated_count = self.annotation_stats_cache['annotated']
        unannotated_count = total_images - annotated_count
        percentage = (annotated_count / total_images * 100) if total_images > 0 else 0.0

        # 检查当前图片的标注状态（使用缓存）
        current_annotated = False
        if 0 <= self.cur_img_idx < len(self.m_img_list):
            current_img_path = self.m_img_list[self.cur_img_idx]
            current_annotated = self.get_cached_annotation_status(current_img_path)

        return {
            'total': total_images,
            'annotated': annotated_count,
            'unannotated': unannotated_count,
            'percentage': percentage,
            'current_annotated': current_annotated,
            'current_index': self.cur_img_idx + 1 if total_images > 0 else 0
        }

    def update_switch_button_state(self):
        """
        更新切换到未标注图片按钮和删除当前图片按钮的状态
        """
        if hasattr(self, 'switch_unannotated_button'):
            # 如果有图片列表则启用按钮，否则禁用
            has_images = bool(self.m_img_list)
            self.switch_unannotated_button.setEnabled(has_images)

            if has_images:
                # 使用新的统计方法
                stats = self.calculate_annotation_statistics()
                unannotated_count = stats['unannotated']

                if unannotated_count > 0:
                    self.switch_unannotated_button.setToolTip(
                        f'快速跳转到下一张未标注的图片 (还有 {unannotated_count} 张未标注)')
                else:
                    self.switch_unannotated_button.setToolTip('所有图片都已标注完成')
            else:
                self.switch_unannotated_button.setToolTip('请先加载图片目录')

        # 更新删除当前图片按钮的状态
        if hasattr(self, 'delete_current_image_button'):
            # 只有当前有加载的图片时才启用删除按钮
            has_current_image = bool(
                self.file_path and os.path.exists(self.file_path))
            self.delete_current_image_button.setEnabled(has_current_image)

            if has_current_image:
                current_file = os.path.basename(self.file_path)
                self.delete_current_image_button.setToolTip(
                    f'删除当前图片: {current_file}（不可撤销）')
            else:
                self.delete_current_image_button.setToolTip('没有可删除的图片')

    def trigger_smart_prediction_if_needed(self):
        """
        智能预测：如果开启了智能预测且当前图片未标注，则自动执行预测
        使用防抖机制避免频繁切换时重复触发
        """
        try:
            # 检查是否有AI助手面板
            if not hasattr(self, 'ai_assistant_panel') or not self.ai_assistant_panel:
                return

            # 检查智能预测是否开启
            if not self.ai_assistant_panel.is_smart_predict_enabled():
                return

            # 检查是否有当前图片
            if not self.file_path:
                return

            # 防抖：如果是同一张图片，跳过
            if self.last_smart_predict_path == self.file_path:
                return

            # 更新最后预测的图片路径
            self.last_smart_predict_path = self.file_path

            # 取消之前的定时器
            if self.smart_predict_timer:
                self.smart_predict_timer.stop()
                self.smart_predict_timer = None

            # 创建新的定时器，延迟执行预测（防抖）
            self.smart_predict_timer = QTimer()
            self.smart_predict_timer.setSingleShot(True)
            self.smart_predict_timer.timeout.connect(
                self._execute_smart_prediction)
            self.smart_predict_timer.start(500)  # 延迟500ms执行

        except Exception as e:
            error_msg = f"智能预测触发失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()

    def _execute_smart_prediction(self):
        """
        执行智能预测的实际逻辑
        """
        try:
            # 检查当前图片是否已经标注
            if self.is_image_annotated(self.file_path):
                print(
                    f"[DEBUG] 智能预测: 图片已标注，跳过预测: {os.path.basename(self.file_path)}")
                return

            # 检查模型是否已加载
            if not self.ai_assistant_panel.predictor or not self.ai_assistant_panel.predictor.is_model_loaded():
                print(f"[DEBUG] 智能预测: 模型未加载，跳过预测")
                return

            # 检查是否正在预测中（包括智能预测）
            if hasattr(self.ai_assistant_panel, 'is_predicting') and self.ai_assistant_panel.is_predicting:
                print(f"[DEBUG] 智能预测: 正在预测中，跳过")
                return

            if hasattr(self.ai_assistant_panel, 'is_smart_predicting') and self.ai_assistant_panel.is_smart_predicting:
                print(f"[DEBUG] 智能预测: 智能预测正在进行中，跳过")
                return

            print(
                f"[DEBUG] 智能预测: 开始自动预测未标注图片: {os.path.basename(self.file_path)}")

            # 显示智能预测状态
            self.statusBar().showMessage(
                f'🤖 智能预测: 正在预测 {os.path.basename(self.file_path)}...')

            # 设置智能预测状态标记
            self.ai_assistant_panel.is_smart_predicting = True

            # 使用正确的信号机制触发预测，确保结果能够自动显示
            confidence = self.ai_assistant_panel.get_current_confidence()
            print(f"[DEBUG] 智能预测: 使用信号机制触发预测，置信度: {confidence}")

            # 发送预测请求信号，这样预测结果会自动应用到画布
            self.ai_assistant_panel.prediction_requested.emit(
                self.file_path, confidence)

        except Exception as e:
            error_msg = f"智能预测执行失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()

    def show_bounding_box_from_annotation_file(self, file_path):
        # 检查file_path是否为None，避免TypeError
        if file_path is None:
            return

        if self.default_save_dir is not None:
            basename = os.path.basename(os.path.splitext(file_path)[0])
            xml_path = os.path.join(self.default_save_dir, basename + XML_EXT)
            txt_path = os.path.join(self.default_save_dir, basename + TXT_EXT)
            json_path = os.path.join(
                self.default_save_dir, basename + JSON_EXT)

            """Annotation file priority:
            PascalXML > YOLO
            """
            if os.path.isfile(xml_path):
                self.load_pascal_xml_by_filename(xml_path)
            elif os.path.isfile(txt_path):
                self.load_yolo_txt_by_filename(txt_path)
            elif os.path.isfile(json_path):
                self.load_create_ml_json_by_filename(json_path, file_path)

        else:
            xml_path = os.path.splitext(file_path)[0] + XML_EXT
            txt_path = os.path.splitext(file_path)[0] + TXT_EXT
            json_path = os.path.splitext(file_path)[0] + JSON_EXT

            if os.path.isfile(xml_path):
                self.load_pascal_xml_by_filename(xml_path)
            elif os.path.isfile(txt_path):
                self.load_yolo_txt_by_filename(txt_path)
            elif os.path.isfile(json_path):
                self.load_create_ml_json_by_filename(json_path, file_path)

    def resizeEvent(self, event):
        if self.canvas and not self.image.isNull()\
           and self.zoom_mode != self.MANUAL_ZOOM:
            self.adjust_scale()
        super(MainWindow, self).resizeEvent(event)

    def paint_canvas(self):
        assert not self.image.isNull(), "cannot paint null image"

        # 缩放状态一致性检查和调试信息
        zoom_value = self.zoom_widget.value()

        # 如果缩放值异常，重新计算以保持一致性
        if self.zoom_mode != self.MANUAL_ZOOM and hasattr(self, 'canvas') and self.canvas.pixmap:
            expected_value = self.scalers[self.zoom_mode]()
            expected_zoom = int(100 * expected_value)

            # 如果当前缩放值与期望值差异较大，重新设置
            if abs(zoom_value - expected_zoom) > 5:  # 允许5%的误差
                self.zoom_widget.setValue(expected_zoom)
                zoom_value = expected_zoom

        self.canvas.scale = 0.01 * zoom_value
        self.canvas.overlay_color = self.light_widget.color()
        self.canvas.label_font_size = int(
            0.02 * max(self.image.width(), self.image.height()))
        self.canvas.adjustSize()
        self.canvas.update()

        # 性能优化：延迟更新状态栏信息，避免paint_canvas频繁调用时的重复更新
        if hasattr(self, 'status_update_timer'):
            self.status_update_timer.start(50)  # 50ms延迟，多次调用时会重置计时器
        else:
            self.update_status_bar_info()

    def adjust_scale(self, initial=False):
        # 当initial=True时，检查是否使用用户偏好缩放
        if initial:
            if self.user_preferred_zoom_enabled:
                # 使用用户偏好的缩放设置
                self.zoom_mode = self.user_preferred_zoom_mode
                if self.zoom_mode == self.FIT_WINDOW:
                    self.actions.fitWindow.setChecked(True)
                    self.actions.fitWidth.setChecked(False)
                elif self.zoom_mode == self.FIT_WIDTH:
                    self.actions.fitWindow.setChecked(False)
                    self.actions.fitWidth.setChecked(True)
                else:  # MANUAL_ZOOM
                    self.actions.fitWindow.setChecked(False)
                    self.actions.fitWidth.setChecked(False)
            else:
                # 使用默认的FIT_WINDOW模式
                self.zoom_mode = self.FIT_WINDOW
                self.actions.fitWindow.setChecked(True)
                self.actions.fitWidth.setChecked(False)

        # 计算缩放值
        if self.zoom_mode == self.MANUAL_ZOOM and self.user_preferred_zoom_enabled:
            # 对于手动缩放模式，直接使用用户偏好的缩放值
            zoom_percentage = self.user_preferred_zoom_value
        else:
            # 对于自适应模式，计算缩放值
            value = self.scalers[self.zoom_mode]()
            zoom_percentage = int(100 * value)
            # 如果用户启用了偏好且当前是自适应模式，更新偏好值
            if self.user_preferred_zoom_enabled and self.zoom_mode != self.MANUAL_ZOOM:
                self.user_preferred_zoom_value = zoom_percentage

        self.zoom_widget.setValue(zoom_percentage)

    def reset_zoom_preference(self):
        """重置用户缩放偏好到默认状态"""
        self.user_preferred_zoom_enabled = False
        self.user_preferred_zoom_mode = self.FIT_WINDOW
        self.user_preferred_zoom_value = 100
        # 重新应用默认缩放
        self.zoom_mode = self.FIT_WINDOW
        self.actions.fitWindow.setChecked(True)
        self.actions.fitWidth.setChecked(False)
        self.adjust_scale()

    def scale_fit_window(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e

        # 确保窗口尺寸有效，避免在初始化时计算错误
        if w1 <= 0 or h1 <= 0:
            return 1.0  # 返回默认缩放比例

        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0

        # 确保图片尺寸有效
        if w2 <= 0 or h2 <= 0:
            return 1.0  # 返回默认缩放比例

        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scale_fit_width(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0

        # 确保窗口宽度和图片宽度有效
        if w <= 0 or self.canvas.pixmap.width() <= 0:
            return 1.0  # 返回默认缩放比例

        return w / self.canvas.pixmap.width()

    def closeEvent(self, event):
        if not self.may_continue():
            event.ignore()
        settings = self.settings
        # If it loads images from dir, don't load it at the beginning
        if self.dir_name is None:
            settings[SETTING_FILENAME] = self.file_path if self.file_path else ''
        else:
            settings[SETTING_FILENAME] = ''

        settings[SETTING_WIN_SIZE] = self.size()
        settings[SETTING_WIN_POSE] = self.pos()
        settings[SETTING_WIN_STATE] = self.saveState()
        settings[SETTING_LINE_COLOR] = self.line_color
        settings[SETTING_FILL_COLOR] = self.fill_color
        settings[SETTING_RECENT_FILES] = self.recent_files
        settings[SETTING_ADVANCE_MODE] = not self._beginner
        if self.default_save_dir and os.path.exists(self.default_save_dir):
            settings[SETTING_SAVE_DIR] = ustr(self.default_save_dir)
        else:
            settings[SETTING_SAVE_DIR] = ''

        if self.last_open_dir and os.path.exists(self.last_open_dir):
            settings[SETTING_LAST_OPEN_DIR] = self.last_open_dir
        else:
            settings[SETTING_LAST_OPEN_DIR] = ''

        # Save last opened directory for next startup
        if self.last_opened_dir and os.path.exists(self.last_opened_dir):
            settings[SETTING_LAST_OPENED_DIR] = self.last_opened_dir
        else:
            settings[SETTING_LAST_OPENED_DIR] = ''

        settings[SETTING_AUTO_SAVE] = self.auto_saving.isChecked()
        settings[SETTING_SINGLE_CLASS] = self.single_class_mode.isChecked()
        settings[SETTING_PAINT_LABEL] = self.display_label_option.isChecked()
        settings[SETTING_DRAW_SQUARE] = self.draw_squares_option.isChecked()
        settings[SETTING_LABEL_FILE_FORMAT] = self.label_file_format

        # 保存用户缩放偏好设置
        settings['user_preferred_zoom_enabled'] = self.user_preferred_zoom_enabled
        settings['user_preferred_zoom_mode'] = self.user_preferred_zoom_mode
        settings['user_preferred_zoom_value'] = self.user_preferred_zoom_value

        settings.save()

    def load_recent(self, filename):
        if self.may_continue():
            self.load_file(filename)

    def scan_all_images(self, folder_path):
        extensions = ['.%s' % fmt.data().decode("ascii").lower()
                      for fmt in QImageReader.supportedImageFormats()]
        images = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relative_path = os.path.join(root, file)
                    path = ustr(os.path.abspath(relative_path))
                    images.append(path)
        natural_sort(images, key=lambda x: x.lower())
        return images

    def change_save_dir_dialog(self, _value=False):
        if self.default_save_dir is not None:
            path = ustr(self.default_save_dir)
        else:
            path = '.'

        dir_path = ustr(QFileDialog.getExistingDirectory(self,
                                                         '%s - Save annotations to the directory' % __appname__, path,  QFileDialog.ShowDirsOnly
                                                         | QFileDialog.DontResolveSymlinks))

        if dir_path is not None and len(dir_path) > 1:
            self.default_save_dir = dir_path

        # 只有当file_path不为None时才调用
        if self.file_path is not None:
            self.show_bounding_box_from_annotation_file(self.file_path)

        self.statusBar().showMessage('%s . Annotation will be saved to %s' %
                                     ('Change saved folder', self.default_save_dir))
        self.statusBar().show()

    def open_annotation_dialog(self, _value=False):
        if self.file_path is None:
            self.statusBar().showMessage('Please select image first')
            self.statusBar().show()
            return

        path = os.path.dirname(ustr(self.file_path))\
            if self.file_path else '.'
        if self.label_file_format == LabelFileFormat.PASCAL_VOC:
            filters = "Open Annotation XML file (%s)" % ' '.join(['*.xml'])
            filename = ustr(QFileDialog.getOpenFileName(
                self, '%s - Choose a xml file' % __appname__, path, filters))
            if filename:
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]
            self.load_pascal_xml_by_filename(filename)

        elif self.label_file_format == LabelFileFormat.CREATE_ML:

            filters = "Open Annotation JSON file (%s)" % ' '.join(['*.json'])
            filename = ustr(QFileDialog.getOpenFileName(
                self, '%s - Choose a json file' % __appname__, path, filters))
            if filename:
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]

            self.load_create_ml_json_by_filename(filename, self.file_path)

    def open_dir_dialog(self, _value=False, dir_path=None, silent=False):
        if not self.may_continue():
            return

        # Use last opened directory from settings if available
        default_open_dir_path = dir_path if dir_path else '.'
        if self.last_opened_dir and os.path.exists(self.last_opened_dir):
            default_open_dir_path = self.last_opened_dir
        elif self.last_open_dir and os.path.exists(self.last_open_dir):
            default_open_dir_path = self.last_open_dir
        else:
            default_open_dir_path = os.path.dirname(
                self.file_path) if self.file_path else '.'

        if silent != True:
            target_dir_path = ustr(QFileDialog.getExistingDirectory(self,
                                                                    '%s - Open Directory' % __appname__, default_open_dir_path,
                                                                    QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        else:
            target_dir_path = ustr(default_open_dir_path)

        if target_dir_path:
            self.last_open_dir = target_dir_path
            # Save the last opened directory to settings immediately
            self.last_opened_dir = target_dir_path
            self.settings[SETTING_LAST_OPENED_DIR] = target_dir_path
            self.settings.save()

            # 直接将选择的图片目录设为标注保存目录，不再弹出第二次对话框
            self.default_save_dir = target_dir_path

            # 更新状态栏显示
            self.statusBar().showMessage('%s . Annotation will be saved to %s' %
                                         ('Open Directory', self.default_save_dir))
            self.statusBar().show()

        self.import_dir_images(target_dir_path)
        # 移除重复调用show_bounding_box_from_annotation_file
        # 因为在load_file中已经调用过了

    def import_dir_images(self, dir_path):
        if not self.may_continue() or not dir_path:
            return

        print("[PERF] 开始导入目录图片...")
        start_time = time.time()

        self.last_open_dir = dir_path
        self.dir_name = dir_path
        self.file_path = None
        
        # 性能优化：暂停所有自动更新
        if hasattr(self, 'status_update_timer'):
            self.status_update_timer.stop()
        
        # 批量清理和设置
        self.file_list_widget.clear()
        self.m_img_list = self.scan_all_images(dir_path)
        self.img_count = len(self.m_img_list)
        
        # 性能优化：批量添加文件列表项，减少UI重绘
        self.file_list_widget.setUpdatesEnabled(False)  # 暂停UI更新
        try:
            for imgPath in self.m_img_list:
                item = QListWidgetItem(imgPath)
                self.file_list_widget.addItem(item)
        finally:
            self.file_list_widget.setUpdatesEnabled(True)  # 恢复UI更新
        
        # 性能优化：图片列表变更时使缓存失效
        self.invalidate_annotation_cache()
        
        # 延迟加载第一张图片，给UI时间完成更新
        def delayed_load_first_image():
            self.open_next_image()
            # 批量更新UI状态
            self.update_switch_button_state()
            if hasattr(self, 'status_update_timer'):
                self.status_update_timer.start(100)  # 延迟状态栏更新
            else:
                self.update_status_bar_info()
            
            end_time = time.time()
            print(f"[PERF] 目录导入完成，用时: {(end_time - start_time)*1000:.1f}ms，共{len(self.m_img_list)}张图片")
        
        # 使用QTimer异步执行，避免阻塞UI
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10, delayed_load_first_image)

    def verify_image(self, _value=False):
        # Proceeding next image without dialog if having any label
        if self.file_path is not None:
            try:
                self.label_file.toggle_verify()
            except AttributeError:
                # If the labelling file does not exist yet, create if and
                # re-save it with the verified attribute.
                self.save_file()
                if self.label_file is not None:
                    self.label_file.toggle_verify()
                else:
                    return

            self.canvas.verified = self.label_file.verified
            self.paint_canvas()
            self.save_file()

    def open_prev_image(self, _value=False):
        # Proceeding prev image without dialog if having any label
        if self.auto_saving.isChecked():
            if self.default_save_dir is not None:
                if self.dirty is True:
                    self.save_file()
            else:
                self.change_save_dir_dialog()
                return

        if not self.may_continue():
            return

        if self.img_count <= 0:
            return

        if self.file_path is None:
            return

        if self.cur_img_idx - 1 >= 0:
            self.cur_img_idx -= 1
            filename = self.m_img_list[self.cur_img_idx]
            if filename:
                self.load_file(filename)

    def open_next_image(self, _value=False):
        # Proceeding next image without dialog if having any label
        if self.auto_saving.isChecked():
            if self.default_save_dir is not None:
                if self.dirty is True:
                    self.save_file()
            else:
                self.change_save_dir_dialog()
                return

        if not self.may_continue():
            return

        if self.img_count <= 0:
            return

        if not self.m_img_list:
            return

        filename = None
        if self.file_path is None:
            filename = self.m_img_list[0]
            self.cur_img_idx = 0
        else:
            if self.cur_img_idx + 1 < self.img_count:
                self.cur_img_idx += 1
                filename = self.m_img_list[self.cur_img_idx]

        if filename:
            self.load_file(filename)

    def open_file(self, _value=False):
        if not self.may_continue():
            return
        path = os.path.dirname(ustr(self.file_path)) if self.file_path else '.'
        formats = ['*.%s' % fmt.data().decode("ascii").lower()
                   for fmt in QImageReader.supportedImageFormats()]
        filters = "Image & Label files (%s)" % ' '.join(
            formats + ['*%s' % LabelFile.suffix])
        filename, _ = QFileDialog.getOpenFileName(
            self, '%s - Choose Image or Label file' % __appname__, path, filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.cur_img_idx = 0
            self.img_count = 1
            self.load_file(filename)

    def save_file(self, _value=False):
        if self.default_save_dir is not None and len(ustr(self.default_save_dir)):
            if self.file_path:
                image_file_name = os.path.basename(self.file_path)
                saved_file_name = os.path.splitext(image_file_name)[0]
                saved_path = os.path.join(
                    ustr(self.default_save_dir), saved_file_name)
                self._save_file(saved_path)
        else:
            image_file_dir = os.path.dirname(self.file_path)
            image_file_name = os.path.basename(self.file_path)
            saved_file_name = os.path.splitext(image_file_name)[0]
            saved_path = os.path.join(image_file_dir, saved_file_name)
            self._save_file(saved_path if self.label_file
                            else self.save_file_dialog(remove_ext=False))

    def save_file_as(self, _value=False):
        assert not self.image.isNull(), "cannot save empty image"
        self._save_file(self.save_file_dialog())

    def save_file_dialog(self, remove_ext=True):
        caption = '%s - Choose File' % __appname__
        filters = 'File (*%s)' % LabelFile.suffix
        open_dialog_path = self.current_path()
        dlg = QFileDialog(self, caption, open_dialog_path, filters)
        dlg.setDefaultSuffix(LabelFile.suffix[1:])
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filename_without_extension = os.path.splitext(self.file_path)[0]
        dlg.selectFile(filename_without_extension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            full_file_path = ustr(dlg.selectedFiles()[0])
            if remove_ext:
                # Return file path without the extension.
                return os.path.splitext(full_file_path)[0]
            else:
                return full_file_path
        return ''

    def _save_file(self, annotation_file_path):
        if annotation_file_path and self.save_labels(annotation_file_path):
            self.set_clean()
            self.statusBar().showMessage('Saved to  %s' % annotation_file_path)
            self.statusBar().show()
            # 保存后更新切换按钮状态和状态栏信息
            self.update_switch_button_state()
            self.update_status_bar_info()

    def close_file(self, _value=False):
        if not self.may_continue():
            return
        self.reset_state()
        self.set_clean()
        self.toggle_actions(False)
        self.canvas.setEnabled(False)
        self.actions.saveAs.setEnabled(False)

        # 更新按钮状态
        self.update_switch_button_state()

    def delete_image(self):
        """删除当前图片（通过菜单或快捷键调用）"""
        delete_path = self.file_path
        if delete_path is not None:
            # 检查是否需要显示确认对话框
            if DeleteConfirmationDialog.should_show_confirmation("delete_menu"):
                # 显示智能确认对话框
                dialog = DeleteConfirmationDialog(
                    parent=self,
                    file_path=delete_path,
                    operation_type="delete_menu"
                )

                if dialog.exec_() != QDialog.Accepted:
                    return
            else:
                # 显示简化确认对话框
                dialog = SimpleDeleteConfirmationDialog(
                    parent=self,
                    file_path=delete_path
                )

                if dialog.exec_() != QMessageBox.Yes:
                    return

            idx = self.cur_img_idx
            current_file = os.path.basename(delete_path)
            deleted_annotations = []

            if os.path.exists(delete_path):
                os.remove(delete_path)

                # 删除对应的标注文件
                annotation_files = [
                    os.path.splitext(delete_path)[0] + '.xml',
                    os.path.splitext(delete_path)[0] + '.txt',
                    os.path.splitext(delete_path)[0] + '.json'
                ]
                for ann_file in annotation_files:
                    if os.path.exists(ann_file):
                        os.remove(ann_file)
                        deleted_annotations.append(os.path.basename(ann_file))

            self.import_dir_images(self.last_open_dir)
            if self.img_count > 0:
                self.cur_img_idx = min(idx, self.img_count - 1)
                filename = self.m_img_list[self.cur_img_idx]
                self.load_file(filename)
            else:
                self.close_file()

            # 显示增强的状态信息
            status_msg = f"✅ 已删除: {current_file}"
            if deleted_annotations:
                status_msg += f" (含标注: {', '.join(deleted_annotations)})"

            # 如果用户禁用了确认对话框，提供恢复提示
            if not DeleteConfirmationDialog.should_show_confirmation("delete_menu"):
                status_msg += " | 💡 可通过菜单恢复删除确认对话框"

            self.status(status_msg)

    def delete_current_image(self):
        """从标签面板删除当前图片（通过按钮调用）"""
        # 检查是否有当前加载的图片
        if not self.file_path or not os.path.exists(self.file_path):
            QMessageBox.information(self, '提示', '当前没有加载的图片可以删除。')
            return

        # 检查是否需要显示确认对话框
        if DeleteConfirmationDialog.should_show_confirmation("delete_current"):
            # 显示智能确认对话框
            dialog = DeleteConfirmationDialog(
                parent=self,
                file_path=self.file_path,
                operation_type="delete_current"
            )

            if dialog.exec_() != QDialog.Accepted:
                return
        else:
            # 显示简化确认对话框
            dialog = SimpleDeleteConfirmationDialog(
                parent=self,
                file_path=self.file_path
            )

            if dialog.exec_() != QMessageBox.Yes:
                return

        try:
            delete_path = self.file_path
            current_idx = self.cur_img_idx
            current_file = os.path.basename(delete_path)  # 添加这个变量定义

            # 删除图片文件
            if os.path.exists(delete_path):
                os.remove(delete_path)

                # 删除对应的标注文件
                annotation_files = [
                    os.path.splitext(delete_path)[0] + '.xml',
                    os.path.splitext(delete_path)[0] + '.txt',
                    os.path.splitext(delete_path)[0] + '.json'
                ]
                deleted_annotations = []
                for ann_file in annotation_files:
                    if os.path.exists(ann_file):
                        os.remove(ann_file)
                        deleted_annotations.append(os.path.basename(ann_file))

            # 从图片列表中移除
            if delete_path in self.m_img_list:
                self.m_img_list.remove(delete_path)
                self.img_count = len(self.m_img_list)

            # 从文件列表界面中移除
            for i in range(self.file_list_widget.count()):
                item = self.file_list_widget.item(i)
                if item and item.text() == delete_path:
                    self.file_list_widget.takeItem(i)
                    break

            # 处理删除后的图片切换
            if self.img_count > 0:
                # 如果还有图片，加载下一张
                self.cur_img_idx = min(current_idx, self.img_count - 1)
                next_filename = self.m_img_list[self.cur_img_idx]
                self.load_file(next_filename)
            else:
                # 如果没有图片了，关闭当前文件并禁用相关按钮
                self.close_file()
                self.delete_current_image_button.setEnabled(False)

            # 更新切换按钮状态和状态栏信息
            self.update_switch_button_state()
            self.update_status_bar_info()

            # 显示删除成功信息 - 增强状态栏提示
            status_msg = f"✅ 已删除: {current_file}"
            if deleted_annotations:
                status_msg += f" (含标注: {', '.join(deleted_annotations)})"

            # 如果用户禁用了确认对话框，提供恢复提示
            if not DeleteConfirmationDialog.should_show_confirmation("delete_current"):
                status_msg += " | 💡 可通过菜单恢复删除确认对话框"

            self.status(status_msg)

        except Exception as e:
            QMessageBox.critical(self, '删除失败', f'删除文件时发生错误：\n\n{str(e)}')

    def remove_file_from_list(self):
        """从列表中移除文件，但不删除磁盘文件"""
        current_item = self.file_list_widget.currentItem()
        if current_item is None:
            return

        # 获取要移除的文件路径
        file_path = current_item.text()

        # 确认对话框
        reply = QMessageBox.question(self, '确认移除',
                                     f'确定要从列表中移除文件吗？\n\n{os.path.basename(file_path)}\n\n'
                                     '注意：文件将从界面列表中移除，但不会删除磁盘文件。',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply != QMessageBox.Yes:
            return

        try:
            # 获取当前文件索引
            if file_path in self.m_img_list:
                idx = self.m_img_list.index(file_path)

                # 从列表中移除
                self.m_img_list.remove(file_path)
                self.img_count = len(self.m_img_list)

                # 从界面列表中移除
                row = self.file_list_widget.row(current_item)
                self.file_list_widget.takeItem(row)

                # 如果移除的是当前显示的文件，需要加载下一个文件
                if file_path == self.file_path:
                    if self.img_count > 0:
                        # 调整索引
                        self.cur_img_idx = min(idx, self.img_count - 1)
                        filename = self.m_img_list[self.cur_img_idx]
                        self.load_file(filename)
                    else:
                        self.close_file()
                else:
                    # 更新当前文件索引
                    if self.file_path in self.m_img_list:
                        self.cur_img_idx = self.m_img_list.index(
                            self.file_path)

                # 更新切换按钮状态
                self.update_switch_button_state()

                # 显示状态信息
                self.status(f"已从列表移除: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.warning(self, '错误', f'移除文件失败：{str(e)}')

    def reset_delete_confirmation_settings(self):
        """重置删除确认设置，恢复显示确认对话框"""
        try:
            # 显示确认对话框
            reply = QMessageBox.question(
                self,
                '🔄 重置删除确认设置',
                '确定要重置删除确认设置吗？\n\n'
                '重置后：\n'
                '• 删除图片时将重新显示完整的确认对话框\n'
                '• 之前选择的"不再提示"设置将被清除\n'
                '• 这有助于防止误删除操作\n\n'
                '是否继续？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # 调用重置方法
                success = DeleteConfirmationDialog.reset_confirmation_settings()

                if success:
                    QMessageBox.information(
                        self,
                        '✅ 重置成功',
                        '删除确认设置已重置！\n\n'
                        '现在删除图片时将重新显示完整的确认对话框，\n'
                        '帮助您避免误删除操作。'
                    )

                    # 更新状态栏
                    self.status("✅ 删除确认设置已重置")
                else:
                    QMessageBox.warning(
                        self,
                        '❌ 重置失败',
                        '重置删除确认设置时发生错误。\n\n'
                        '请检查设置文件权限或重启应用程序后重试。'
                    )

        except Exception as e:
            QMessageBox.critical(
                self,
                '错误',
                f'重置删除确认设置时发生错误：\n\n{str(e)}'
            )

    def delete_file_permanently(self):
        """彻底删除文件（从磁盘删除）"""
        current_item = self.file_list_widget.currentItem()
        if current_item is None:
            return

        # 获取要删除的文件路径
        file_path = current_item.text()

        # 确认对话框
        reply = QMessageBox.question(self, '确认删除',
                                     f'确定要彻底删除文件吗？\n\n{os.path.basename(file_path)}\n\n'
                                     '⚠️ 警告：文件将从磁盘彻底删除，此操作不可撤销！',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply != QMessageBox.Yes:
            return

        try:
            # 删除磁盘文件
            if os.path.exists(file_path):
                os.remove(file_path)

            # 删除对应的标注文件
            annotation_files = [
                os.path.splitext(file_path)[0] + '.xml',
                os.path.splitext(file_path)[0] + '.txt',
                os.path.splitext(file_path)[0] + '.json'
            ]
            for ann_file in annotation_files:
                if os.path.exists(ann_file):
                    os.remove(ann_file)

            # 从列表中移除
            if file_path in self.m_img_list:
                idx = self.m_img_list.index(file_path)
                self.m_img_list.remove(file_path)
                self.img_count = len(self.m_img_list)

                # 从界面列表中移除
                row = self.file_list_widget.row(current_item)
                self.file_list_widget.takeItem(row)

                # 如果删除的是当前显示的文件，需要加载下一个文件
                if file_path == self.file_path:
                    if self.img_count > 0:
                        self.cur_img_idx = min(idx, self.img_count - 1)
                        filename = self.m_img_list[self.cur_img_idx]
                        self.load_file(filename)
                    else:
                        self.close_file()
                else:
                    # 更新当前文件索引
                    if self.file_path in self.m_img_list:
                        self.cur_img_idx = self.m_img_list.index(
                            self.file_path)

                # 更新切换按钮状态
                self.update_switch_button_state()

                # 显示状态信息
                self.status(f"已彻底删除: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.warning(self, '错误', f'删除文件失败：{str(e)}')

    def show_file_in_explorer(self):
        """在文件管理器中显示文件"""
        current_item = self.file_list_widget.currentItem()
        if current_item is None:
            return

        file_path = current_item.text()

        try:
            import platform
            import subprocess

            if platform.system() == 'Windows':
                # Windows系统
                subprocess.run(['explorer', '/select,', file_path])
            elif platform.system() == 'Darwin':
                # macOS系统
                subprocess.run(['open', '-R', file_path])
            else:
                # Linux系统
                subprocess.run(['xdg-open', os.path.dirname(file_path)])

        except Exception as e:
            QMessageBox.warning(self, '错误', f'无法打开文件管理器：{str(e)}')

    def reset_all(self):
        """重置所有设置并自动重启程序"""
        # 显示确认对话框
        reply = QMessageBox.question(self, '确认重置',
                                     '确定要重置所有设置吗？程序将自动重启。',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 重置设置
            self.settings.reset()

            # 获取当前程序的启动参数
            import sys
            current_args = sys.argv[:]

            # 关闭当前程序
            self.close()

            # 启动新的程序实例
            process = QProcess()
            if current_args[0].endswith('.py'):
                # 如果是Python脚本，使用Python解释器启动
                python_exe = sys.executable
                process.startDetached(python_exe, current_args)
            else:
                # 如果是可执行文件，直接启动
                process.startDetached(current_args[0], current_args[1:])

    def may_continue(self):
        if not self.dirty:
            return True
        else:
            discard_changes = self.discard_changes_dialog()
            if discard_changes == QMessageBox.No:
                return True
            elif discard_changes == QMessageBox.Yes:
                self.save_file()
                return True
            else:
                return False

    def discard_changes_dialog(self):
        yes, no, cancel = QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel
        msg = u'You have unsaved changes, would you like to save them and proceed?\nClick "No" to undo all changes.'
        return QMessageBox.warning(self, u'Attention', msg, yes | no | cancel)

    def error_message(self, title, message):
        return QMessageBox.critical(self, title,
                                    '<p><b>%s</b></p>%s' % (title, message))

    def current_path(self):
        return os.path.dirname(self.file_path) if self.file_path else '.'

    def choose_color1(self):
        color = self.color_dialog.getColor(self.line_color, u'Choose line color',
                                           default=DEFAULT_LINE_COLOR)
        if color:
            self.line_color = color
            Shape.line_color = color
            self.canvas.set_drawing_color(color)
            self.canvas.update()
            self.set_dirty()

    def delete_selected_shape(self):
        self.remove_label(self.canvas.delete_selected())
        self.set_dirty()
        if self.no_shapes():
            for action in self.actions.onShapesPresent:
                action.setEnabled(False)

    def choose_shape_line_color(self):
        color = self.color_dialog.getColor(self.line_color, u'Choose Line Color',
                                           default=DEFAULT_LINE_COLOR)
        if color:
            self.canvas.selected_shape.line_color = color
            self.canvas.update()
            self.set_dirty()

    def choose_shape_fill_color(self):
        color = self.color_dialog.getColor(self.fill_color, u'Choose Fill Color',
                                           default=DEFAULT_FILL_COLOR)
        if color:
            self.canvas.selected_shape.fill_color = color
            self.canvas.update()
            self.set_dirty()

    def copy_shape(self):
        if self.canvas.selected_shape is None:
            # True if one accidentally touches the left mouse button before releasing
            return
        self.canvas.end_move(copy=True)
        self.add_label(self.canvas.selected_shape)
        self.set_dirty()

    def move_shape(self):
        self.canvas.end_move(copy=False)
        self.set_dirty()

    def load_predefined_classes(self, predef_classes_file):
        print(f"[DEBUG] ========== 开始加载预设标签 ==========")
        print(f"[DEBUG] load_predefined_classes被调用")
        print(f"[DEBUG] 传入的文件路径: {predef_classes_file}")
        print(f"[DEBUG] 文件路径类型: {type(predef_classes_file)}")
        print(f"[DEBUG] 当前工作目录: {os.getcwd()}")

        if predef_classes_file is None:
            print(f"[DEBUG] 错误：文件路径为None")
            return

        # 初始化label_hist如果为None
        if self.label_hist is None:
            self.label_hist = []
            print(f"[DEBUG] 初始化空的标签历史记录")

        # 检查持久化文件是否存在
        print(f"[DEBUG] 检查持久化文件是否存在: {predef_classes_file}")
        if os.path.exists(predef_classes_file):
            print(f"[DEBUG] 持久化文件存在，开始读取...")
            self._load_classes_from_file(predef_classes_file)
        else:
            print(f"[DEBUG] 持久化文件不存在，尝试从初始资源文件加载默认标签...")
            # 尝试从初始资源文件加载默认标签
            initial_file = get_initial_predefined_classes_path()
            print(f"[DEBUG] 初始资源文件路径: {initial_file}")

            if os.path.exists(initial_file):
                print(f"[DEBUG] 初始资源文件存在，加载默认标签...")
                self._load_classes_from_file(initial_file)
                # 将默认标签保存到持久化文件中
                print(f"[DEBUG] 将默认标签保存到持久化文件...")
                self.save_predefined_classes()
            else:
                print(f"[DEBUG] 初始资源文件也不存在，使用空的标签列表")

        print(f"[DEBUG] 最终标签历史记录: {self.label_hist}")
        print(f"[DEBUG] 标签数量: {len(self.label_hist)}")
        print(f"[DEBUG] ========== 加载预设标签完成 ==========")

    def _load_classes_from_file(self, file_path):
        """从指定文件加载预设类标签"""
        print(f"[DEBUG] 开始读取文件内容: {file_path}")
        print(f"[DEBUG] 文件大小: {os.path.getsize(file_path)} 字节")
        try:
            with codecs.open(file_path, 'r', 'utf8') as f:
                line_count = 0
                all_lines = []
                for line_num, line in enumerate(f, 1):
                    original_line = line
                    line = line.strip()
                    print(
                        f"[DEBUG] 第{line_num}行原始内容: '{original_line.rstrip()}'")
                    print(f"[DEBUG] 第{line_num}行处理后: '{line}'")
                    all_lines.append(line)
                    if line:  # 只处理非空行
                        line_count += 1
                        if line not in self.label_hist:  # 避免重复添加
                            self.label_hist.append(line)
                            print(f"[DEBUG] 添加标签到历史记录: '{line}'")
                        else:
                            print(f"[DEBUG] 标签已存在，跳过: '{line}'")
                print(f"[DEBUG] 文件总行数: {len(all_lines)}")
                print(f"[DEBUG] 有效标签行数: {line_count}")
                print(f"[DEBUG] 成功读取 {line_count} 行标签")
        except Exception as e:
            print(f"[DEBUG] 读取文件时出错: {e}")
            import traceback
            print(f"[DEBUG] 错误堆栈:")
            traceback.print_exc()

    def save_predefined_classes(self):
        """
        保存标签历史记录到预设类文件
        """
        print(f"[DEBUG] ========== 开始保存预设标签 ==========")
        print(f"[DEBUG] 目标文件路径: {self.predefined_classes_file}")
        print(f"[DEBUG] 文件路径类型: {type(self.predefined_classes_file)}")
        print(f"[DEBUG] 当前标签历史记录: {self.label_hist}")
        print(f"[DEBUG] 标签数量: {len(self.label_hist)}")

        try:
            # 检查目录
            target_dir = os.path.dirname(self.predefined_classes_file)
            print(f"[DEBUG] 目标目录: {target_dir}")
            print(f"[DEBUG] 目录是否存在: {os.path.exists(target_dir)}")

            # 确保目录存在
            os.makedirs(target_dir, exist_ok=True)
            print(f"[DEBUG] 目录创建/确认完成")

            # 去重并保持顺序
            unique_labels = []
            seen = set()
            for label in self.label_hist:
                if label and label not in seen:
                    unique_labels.append(label)
                    seen.add(label)

            print(f"[DEBUG] 去重后的标签: {unique_labels}")
            print(f"[DEBUG] 去重后标签数量: {len(unique_labels)}")

            # 检查文件写入权限
            print(f"[DEBUG] 检查文件写入权限...")
            try:
                # 尝试创建/打开文件进行写入测试
                with open(self.predefined_classes_file, 'w', encoding='utf8') as test_f:
                    test_f.write("# 测试写入权限\n")
                print(f"[DEBUG] 文件写入权限检查通过")
            except Exception as perm_e:
                print(f"[DEBUG] 文件写入权限检查失败: {perm_e}")
                raise perm_e

            # 保存到文件
            print(f"[DEBUG] 开始写入文件...")
            with codecs.open(self.predefined_classes_file, 'w', 'utf8') as f:
                for i, label in enumerate(unique_labels):
                    print(f"[DEBUG] 写入第{i+1}个标签: '{label}'")
                    f.write(label + '\n')

            print(f"[DEBUG] 文件写入完成")

            # 验证文件内容
            print(f"[DEBUG] 验证保存的文件内容...")
            if os.path.exists(self.predefined_classes_file):
                file_size = os.path.getsize(self.predefined_classes_file)
                print(f"[DEBUG] 文件大小: {file_size} 字节")

                # 读取并验证内容
                with codecs.open(self.predefined_classes_file, 'r', 'utf8') as f:
                    saved_content = f.read()
                    saved_lines = [line.strip() for line in saved_content.split(
                        '\n') if line.strip()]
                    print(f"[DEBUG] 文件中保存的标签: {saved_lines}")
                    print(f"[DEBUG] 保存的标签数量: {len(saved_lines)}")

                    if saved_lines == unique_labels:
                        print(f"[DEBUG] ✓ 文件内容验证成功")
                    else:
                        print(f"[DEBUG] ✗ 文件内容验证失败")
                        print(f"[DEBUG] 期望: {unique_labels}")
                        print(f"[DEBUG] 实际: {saved_lines}")
            else:
                print(f"[DEBUG] ✗ 文件保存后不存在!")

            print(
                f"[DEBUG] Predefined classes saved to: {self.predefined_classes_file}")
            print(f"[DEBUG] ========== 保存预设标签完成 ==========")

        except Exception as e:
            print(f"[DEBUG] ✗ 保存预设标签时发生错误: {e}")
            print(f"[DEBUG] 错误类型: {type(e)}")
            import traceback
            print(f"[DEBUG] 错误堆栈:")
            traceback.print_exc()
            print(f"[DEBUG] ========== 保存预设标签失败 ==========")
            raise e

    def clear_predefined_classes(self):
        """
        清空所有预设标签
        """
        try:
            # 清空内存中的标签历史
            self.label_hist.clear()

            # 清空文件
            with codecs.open(self.predefined_classes_file, 'w', 'utf8') as f:
                f.write('')

            # 重置默认标签
            self.default_label = None

            # 更新UI组件
            self.default_label_combo_box.cb.clear()

            # 禁用使用默认标签的复选框，因为没有可用的标签
            self.use_default_label_checkbox.setChecked(False)
            self.use_default_label_checkbox.setEnabled(False)

            if hasattr(self, 'label_dialog'):
                self.label_dialog = LabelDialog(
                    parent=self, list_item=self.label_hist)

            print("All predefined classes cleared")

        except Exception as e:
            print(f"Error clearing predefined classes: {e}")

    def clear_predefined_classes_with_confirmation(self):
        """
        带确认对话框的清空预设标签功能
        """
        # 检查是否有预设标签
        if not self.label_hist:
            QMessageBox.information(self, '提示', '当前没有预设标签需要清空。')
            return

        # 第一次确认
        labels_count = len(self.label_hist)
        reply = QMessageBox.question(
            self,
            '🗑️ 确认清空预设标签',
            f'确定要清空所有预设标签吗？\n\n'
            f'📊 当前共有 {labels_count} 个预设标签\n'
            f'📝 标签列表: {", ".join(self.label_hist[:10])}{"..." if labels_count > 10 else ""}\n\n'
            f'⚠️ 警告：\n'
            f'• 所有预设标签将被永久删除\n'
            f'• 此操作不可撤销\n'
            f'• 需要重新添加标签\n\n'
            f'确定要继续吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 第二次确认 - 需要输入确认文字
        from PyQt5.QtWidgets import QInputDialog
        confirmation_text, ok = QInputDialog.getText(
            self,
            '🚨 最终确认清空',
            f'这是最后一次确认！\n\n'
            f'即将清空 {labels_count} 个预设标签\n\n'
            f'⚠️ 此操作将永久删除所有预设标签！\n\n'
            f'请输入 "清空标签" 来继续操作：',
            QLineEdit.Normal,
            ''
        )

        if not ok or confirmation_text.strip() != '清空标签':
            QMessageBox.information(self, '操作取消', '清空操作已取消。')
            return

        # 执行清空操作
        self.clear_predefined_classes()
        QMessageBox.information(self, '操作完成', f'已成功清空 {labels_count} 个预设标签。')

    def load_pascal_xml_by_filename(self, xml_path):
        if self.file_path is None:
            return
        if os.path.isfile(xml_path) is False:
            return

        self.set_format(FORMAT_PASCALVOC)

        t_voc_parse_reader = PascalVocReader(xml_path)
        shapes = t_voc_parse_reader.get_shapes()
        self.load_labels(shapes)
        self.canvas.verified = t_voc_parse_reader.verified

    def load_yolo_txt_by_filename(self, txt_path):
        if self.file_path is None:
            return
        if os.path.isfile(txt_path) is False:
            return

        self.set_format(FORMAT_YOLO)
        t_yolo_parse_reader = YoloReader(txt_path, self.image)
        shapes = t_yolo_parse_reader.get_shapes()
        print(shapes)
        self.load_labels(shapes)
        self.canvas.verified = t_yolo_parse_reader.verified

    def load_create_ml_json_by_filename(self, json_path, file_path):
        if self.file_path is None:
            return
        if os.path.isfile(json_path) is False:
            return

        self.set_format(FORMAT_CREATEML)

        create_ml_parse_reader = CreateMLReader(json_path, file_path)
        shapes = create_ml_parse_reader.get_shapes()
        self.load_labels(shapes)
        self.canvas.verified = create_ml_parse_reader.verified

    def copy_previous_bounding_boxes(self):
        # 检查file_path是否为None
        if self.file_path is None or self.file_path not in self.m_img_list:
            return

        current_index = self.m_img_list.index(self.file_path)
        if current_index - 1 >= 0:
            prev_file_path = self.m_img_list[current_index - 1]
            self.show_bounding_box_from_annotation_file(prev_file_path)
            self.save_file()

    def export_yolo_dataset(self):
        """导出为YOLO数据集"""
        # 检查是否有打开的目录
        if not self.last_open_dir or not os.path.exists(self.last_open_dir):
            QMessageBox.warning(self, "警告", "请先打开包含图片和标注文件的目录")
            return

        # 检查目录中是否有XML文件
        xml_files = [f for f in os.listdir(
            self.last_open_dir) if f.lower().endswith('.xml')]
        if not xml_files:
            QMessageBox.warning(
                self, "警告", self.string_bundle.get_string('noAnnotations'))
            return

        # 打开导出对话框
        dialog = YOLOExportDialog(self, self.last_open_dir)
        dialog.exec_()

    def export_model(self):
        """导出模型为其他格式"""
        # 打开模型导出对话框
        dialog = ModelExportDialog(self)
        dialog.exec_()

    def toggle_paint_labels_option(self):
        for shape in self.canvas.shapes:
            shape.paint_label = self.display_label_option.isChecked()

    def toggle_draw_square(self):
        self.canvas.set_drawing_shape_to_square(
            self.draw_squares_option.isChecked())

    # ==================== 新功能动作方法 ====================

    def on_ai_predict_current(self):
        """AI预测当前图像"""
        try:
            if hasattr(self, 'ai_assistant_panel'):
                self.ai_assistant_panel.on_predict_current()
            else:
                QMessageBox.warning(self, "警告", "AI助手未初始化")
        except Exception as e:
            print(f"[ERROR] AI预测当前图像失败: {str(e)}")

    def on_ai_batch_predict(self):
        """AI批量预测"""
        try:
            if hasattr(self, 'ai_assistant_panel'):
                self.ai_assistant_panel.on_predict_batch()
            else:
                QMessageBox.warning(self, "警告", "AI助手未初始化")
        except Exception as e:
            print(f"[ERROR] AI批量预测失败: {str(e)}")

    def on_ai_toggle_panel(self):
        """切换AI面板显示"""
        try:
            if hasattr(self, 'collapsible_ai_panel'):
                self.collapsible_ai_panel.toggle_collapse()
            else:
                QMessageBox.warning(self, "警告", "AI助手面板未初始化")
        except Exception as e:
            print(f"[ERROR] 切换AI面板失败: {str(e)}")

    def on_batch_copy(self):
        """批量复制标注"""
        try:
            # 显示批量操作对话框，默认选择复制操作
            dialog = BatchOperationsDialog(self)
            dialog.operation_combo.setCurrentText("批量复制标注")
            dialog.exec_()
        except Exception as e:
            print(f"[ERROR] 批量复制失败: {str(e)}")

    def on_batch_delete(self):
        """批量删除标注"""
        try:
            # 显示批量操作对话框，默认选择删除操作
            dialog = BatchOperationsDialog(self)
            dialog.operation_combo.setCurrentText("批量删除标注")
            dialog.exec_()
        except Exception as e:
            print(f"[ERROR] 批量删除失败: {str(e)}")

    # ==================== AI助手信号处理方法 ====================

    def on_ai_prediction_requested(self, image_path, confidence):
        """处理AI预测请求"""
        try:
            print(
                f"[DEBUG] 主窗口: 收到AI预测请求，image_path='{image_path}', confidence={confidence}")

            # 如果image_path为空，使用当前图像
            if not image_path and self.file_path:
                image_path = self.file_path
                print(f"[DEBUG] 主窗口: 使用当前图像路径: {image_path}")

            if not image_path:
                error_msg = "没有当前图像，请先打开一张图片"
                print(f"[ERROR] 主窗口: {error_msg}")
                return

            if not os.path.exists(image_path):
                error_msg = f"图像文件不存在: {image_path}"
                print(f"[ERROR] 主窗口: {error_msg}")
                return

            print(f"[DEBUG] 主窗口: 准备启动AI预测，图像路径: {image_path}")

            # 启动AI预测
            if hasattr(self.ai_assistant_panel, 'start_prediction'):
                print(f"[DEBUG] 主窗口: 调用AI助手面板的start_prediction方法")
                self.ai_assistant_panel.start_prediction(image_path)
            else:
                error_msg = "AI助手面板没有start_prediction方法"
                print(f"[ERROR] 主窗口: {error_msg}")

        except Exception as e:
            error_msg = f"AI预测请求处理失败: {str(e)}"
            print(f"[ERROR] 主窗口: {error_msg}")
            import traceback
            traceback.print_exc()

    def on_ai_batch_prediction_requested(self, dir_path, confidence):
        """处理AI批量预测请求"""
        try:
            if not dir_path or not os.path.exists(dir_path):
                print("[ERROR] 无效的目录路径")
                return

            # 启动批量预测
            if hasattr(self.ai_assistant_panel, 'start_batch_prediction'):
                self.ai_assistant_panel.start_batch_prediction(dir_path)

        except Exception as e:
            print(f"[ERROR] AI批量预测请求处理失败: {str(e)}")

    def on_ai_predictions_applied(self, predictions):
        """处理AI预测结果应用"""
        try:
            print(
                f"[DEBUG] 应用预测结果: {predictions[0] if predictions else 'None'}")

            if not predictions:
                print("[INFO] 没有预测结果需要应用")
                return

            # 判断传入的是PredictionResult对象列表还是Detection对象列表
            first_item = predictions[0]
            if hasattr(first_item, 'detections'):
                # 这是PredictionResult对象，获取其中的detections
                print("[DEBUG] 接收到PredictionResult对象")
                detections = first_item.detections
                is_smart_prediction = getattr(
                    first_item, 'is_smart_prediction', False)
            else:
                # 这是Detection对象列表
                print("[DEBUG] 接收到Detection对象列表")
                detections = predictions
                is_smart_prediction = False

            print(f"[DEBUG] 开始批量应用 {len(detections)} 个检测结果到画布")
            
            # 批量处理优化：一次性添加所有形状，最后统一更新UI
            new_shapes = []
            new_items = []
            
            # 导入必要的模块
            from libs.utils import generate_color_by_text

            # 批量创建Shape对象，避免在循环中更新UI
            for i, detection in enumerate(detections):
                print(f"[DEBUG] 处理预测结果 {i+1}: {detection.class_name}")

                # 使用Detection的to_shape方法转换为Shape对象
                shape = detection.to_shape()

                # 设置标签显示
                shape.paint_label = self.display_label_option.isChecked()

                # 生成颜色
                shape.line_color = generate_color_by_text(shape.label)
                shape.fill_color = generate_color_by_text(shape.label)

                # 标记为AI生成的标注框
                shape.ai_generated = True
                shape.ai_confidence = detection.confidence

                # 创建列表项但不立即添加到UI
                item = HashableQListWidgetItem(shape.label)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setBackground(generate_color_by_text(shape.label))
                
                # 建立映射关系
                self.items_to_shapes[item] = shape
                self.shapes_to_items[shape] = item
                
                new_shapes.append(shape)
                new_items.append(item)

                print(f"[DEBUG] 成功处理检测结果 {i+1}: {detection.class_name} (置信度: {detection.confidence:.3f})")

            # 批量添加到画布和列表，避免重复UI更新
            print("[DEBUG] 批量添加形状到画布...")
            self.canvas.shapes.extend(new_shapes)
            
            print("[DEBUG] 批量添加项目到标签列表...")
            # 在添加到标签列表之前，按配置顺序排序
            sorted_items = self.sort_label_items_by_config(new_items)
            for item in sorted_items:
                self.label_list.addItem(item)
                # 调试：确认复选框状态
                print(f"[DEBUG] 项目 '{item.text()}' 复选框状态: {item.checkState()}, Qt.Checked={Qt.Checked}")
            
            # 启用相关操作
            for action in self.actions.onShapesPresent:
                action.setEnabled(True)

            # 只在最后更新一次UI组件
            print("[DEBUG] 更新UI组件...")
            self.update_combo_box()
            self.update_label_stats()

            # 更新画布显示（只调用一次）
            print("[DEBUG] 刷新画布...")
            self.canvas.repaint()

            # 设置为已修改状态
            self.set_dirty()

            # 显示成功状态
            if is_smart_prediction:
                self.statusBar().showMessage(
                    f'🎉 智能预测完成！已自动添加 {len(detections)} 个检测框到画布')
            else:
                self.statusBar().showMessage(
                    f'✅ 预测结果已应用，共添加 {len(detections)} 个检测框')

            print(f"[DEBUG] 批量应用完成，成功添加 {len(detections)} 个对象到画布")

        except Exception as e:
            error_msg = f"AI预测结果应用失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.statusBar().showMessage(f'❌ 预测结果应用失败: {str(e)}')
            import traceback
            traceback.print_exc()

    def on_ai_predictions_cleared(self):
        """处理AI预测结果清除"""
        try:
            print("[DEBUG] 主窗口: 收到清除AI预测结果信号")

            # 找到所有AI生成的标注框
            ai_shapes = []
            for shape in self.canvas.shapes[:]:  # 使用切片复制，避免在迭代时修改列表
                if hasattr(shape, 'ai_generated') and shape.ai_generated:
                    ai_shapes.append(shape)

            print(f"[DEBUG] 主窗口: 找到 {len(ai_shapes)} 个AI生成的标注框")

            # 从画布中移除AI生成的标注框
            for shape in ai_shapes:
                # 从画布shapes列表中移除
                if shape in self.canvas.shapes:
                    self.canvas.shapes.remove(shape)

                # 从标签列表中移除
                if shape in self.shapes_to_items:
                    item = self.shapes_to_items[shape]
                    # 从标签列表控件中移除
                    row = self.label_list.row(item)
                    if row >= 0:
                        self.label_list.takeItem(row)

                    # 从映射字典中移除
                    del self.shapes_to_items[shape]
                    if item in self.items_to_shapes:
                        del self.items_to_shapes[item]

                print(f"[DEBUG] 主窗口: 移除AI标注框 - {shape.label}")

            # 更新画布显示
            self.canvas.repaint()

            # 更新标签统计
            self.update_label_stats()

            # 更新组合框
            self.update_combo_box()

            # 如果没有标注框了，禁用相关操作
            if not self.canvas.shapes:
                for action in self.actions.onShapesPresent:
                    action.setEnabled(False)

            # 设置为已修改状态
            self.set_dirty()

            print(f"[DEBUG] 主窗口: 成功清除 {len(ai_shapes)} 个AI生成的标注框")

        except Exception as e:
            error_msg = f"清除AI预测结果失败: {str(e)}"
            print(f"[ERROR] 主窗口: {error_msg}")
            import traceback
            traceback.print_exc()

    def on_ai_model_changed(self, model_path):
        """处理AI模型切换"""
        try:
            print(f"[DEBUG] AI模型已切换到: {model_path}")

        except Exception as e:
            print(f"[ERROR] AI模型切换处理失败: {str(e)}")

    # ==================== 批量操作信号处理方法 ====================

    def on_batch_operation_started(self, operation_name, total_count):
        """处理批量操作开始"""
        try:
            print(f"[DEBUG] 批量操作开始: {operation_name}, 总数: {total_count}")
            # 显示进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(True)
                self.progress_bar.setMaximum(total_count)
                self.progress_bar.setValue(0)

        except Exception as e:
            print(f"[ERROR] 批量操作开始处理失败: {str(e)}")

    def on_batch_operation_progress(self, current, total, current_file):
        """处理批量操作进度"""
        try:
            print(f"[DEBUG] 批量操作进度: {current}/{total}, 当前文件: {current_file}")
            # 更新进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(current)

        except Exception as e:
            print(f"[ERROR] 批量操作进度处理失败: {str(e)}")

    def on_batch_operation_completed(self, operation_name, result_stats):
        """处理批量操作完成"""
        try:
            print(f"[DEBUG] 批量操作完成: {operation_name}, 结果: {result_stats}")
            # 隐藏进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)

            # 显示完成消息
            QMessageBox.information(self, "操作完成",
                                    f"{operation_name}已完成\n{result_stats}")

        except Exception as e:
            print(f"[ERROR] 批量操作完成处理失败: {str(e)}")

    def on_batch_operation_error(self, error_message):
        """处理批量操作错误"""
        try:
            print(f"[ERROR] 批量操作错误: {error_message}")
            # 隐藏进度条
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)

            # 显示错误消息
            QMessageBox.critical(self, "操作错误", error_message)

        except Exception as e:
            print(f"[ERROR] 批量操作错误处理失败: {str(e)}")

    # ==================== 快捷键信号处理方法 ====================

    def on_shortcut_triggered(self, action_name):
        """处理快捷键触发"""
        try:
            print(f"[DEBUG] 快捷键触发: {action_name}")

            # 根据动作名称执行相应的操作
            if action_name == "delete":
                # 处理删除标注框
                print(f"[DEBUG] 执行删除标注框操作")
                if self.canvas.selected_shape:
                    self.delete_selected_shape()
                else:
                    print(f"[DEBUG] 没有选中的标注框可删除")
            elif action_name == "copy":
                # 处理复制标注框
                print(f"[DEBUG] 执行复制标注框操作")
                if self.canvas.selected_shape:
                    self.copy_selected_shape()
                else:
                    print(f"[DEBUG] 没有选中的标注框可复制")
            elif action_name == "ai_predict_current":
                if hasattr(self, 'ai_assistant_panel'):
                    self.ai_assistant_panel.on_predict_current()
            elif action_name == "ai_predict_batch":
                if hasattr(self, 'ai_assistant_panel'):
                    self.ai_assistant_panel.on_predict_batch()
            elif action_name == "ai_toggle_panel":
                if hasattr(self, 'collapsible_ai_panel'):
                    self.collapsible_ai_panel.toggle_collapse()
            elif action_name == "batch_operations":
                self.show_batch_operations_dialog()
            elif action_name == "toggle_labels":
                if hasattr(self, 'dock'):
                    self.dock.setVisible(not self.dock.isVisible())
            elif action_name == "toggle_draw_square":
                if hasattr(self, 'draw_squares_option'):
                    self.draw_squares_option.trigger()
            elif action_name == "single_class_mode":
                if hasattr(self, 'single_class_mode'):
                    self.single_class_mode.trigger()
            elif action_name == "display_label_option":
                if hasattr(self, 'display_label_option'):
                    self.display_label_option.trigger()
            elif action_name == "next_image":
                self.open_next_image()
            elif action_name == "prev_image":
                self.open_prev_image()
            elif action_name == "first_image":
                if self.m_img_list and len(self.m_img_list) > 0:
                    self.cur_img_idx = 0
                    self.load_file(self.m_img_list[0])
            elif action_name == "last_image":
                if self.m_img_list and len(self.m_img_list) > 0:
                    self.cur_img_idx = len(self.m_img_list) - 1
                    self.load_file(self.m_img_list[-1])
            else:
                print(f"[DEBUG] 未处理的快捷键动作: {action_name}")

        except Exception as e:
            print(f"[ERROR] 快捷键触发处理失败: {str(e)}")

    def on_shortcuts_changed(self):
        """处理快捷键配置改变"""
        try:
            print("[DEBUG] 快捷键配置已改变")
            # 重新应用快捷键
            if hasattr(self, 'shortcut_manager'):
                self.shortcut_manager.apply_shortcuts(self)

        except Exception as e:
            print(f"[ERROR] 快捷键配置改变处理失败: {str(e)}")

    # ==================== 对话框显示方法 ====================

    def show_batch_operations_dialog(self):
        """显示批量操作对话框"""
        try:
            dialog = BatchOperationsDialog(self)
            dialog.exec_()

        except Exception as e:
            print(f"[ERROR] 显示批量操作对话框失败: {str(e)}")

    def show_shortcut_config_dialog(self):
        """显示快捷键配置对话框"""
        try:
            if hasattr(self, 'shortcut_manager'):
                dialog = ShortcutConfigDialog(self.shortcut_manager, self)
                dialog.exec_()

        except Exception as e:
            print(f"[ERROR] 显示快捷键配置对话框失败: {str(e)}")


def inverted(color):
    return QColor(*[255 - v for v in color.getRgb()])


def read(filename, default=None):
    try:
        reader = QImageReader(filename)
        reader.setAutoTransform(True)
        return reader.read()
    except:
        return default


def get_main_app(argv=None):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    print(f"[DEBUG] ========== labelImg 启动调试信息 ==========")
    print(f"[DEBUG] Python版本: {sys.version}")
    print(f"[DEBUG] 当前工作目录: {os.getcwd()}")
    print(f"[DEBUG] 脚本文件路径: {__file__}")
    print(f"[DEBUG] 脚本目录: {os.path.dirname(__file__)}")

    # 检查是否在PyInstaller环境
    if hasattr(sys, '_MEIPASS'):
        print(f"[DEBUG] PyInstaller环境检测到")
        print(f"[DEBUG] _MEIPASS路径: {sys._MEIPASS}")
        print(f"[DEBUG] 可执行文件路径: {sys.executable}")
    else:
        print(f"[DEBUG] 开发环境检测到")

    print(f"[DEBUG] ============================================")

    if not argv:
        argv = []
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(new_icon("app"))
    # Tzutalin 201705+: Accept extra agruments to change predefined class file
    argparser = argparse.ArgumentParser()
    argparser.add_argument("image_dir", nargs="?")
    argparser.add_argument("class_file",
                           default=get_resource_path(os.path.join(
                               "data", "predefined_classes.txt")),
                           nargs="?")
    argparser.add_argument("save_dir", nargs="?")
    args = argparser.parse_args(argv[1:])

    args.image_dir = args.image_dir and os.path.normpath(args.image_dir)
    args.class_file = args.class_file and os.path.normpath(args.class_file)
    args.save_dir = args.save_dir and os.path.normpath(args.save_dir)

    # Usage : labelImg.py image classFile saveDir
    win = MainWindow(args.image_dir,
                     args.class_file,
                     args.save_dir)
    win.show()
    return app, win


def main():
    """construct main app and run it"""
    app, _win = get_main_app(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
