#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快捷键管理器模块

提供快捷键的注册、管理和自定义功能
"""

import os
import json
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class ShortcutAction:
    """快捷键动作数据类"""
    name: str                    # 动作名称
    description: str             # 动作描述
    default_key: str            # 默认快捷键
    current_key: str            # 当前快捷键
    category: str               # 分类
    callback: Optional[Callable] = None  # 回调函数
    enabled: bool = True        # 是否启用


class ShortcutManager(QObject):
    """快捷键管理器"""

    # 信号定义
    shortcut_triggered = pyqtSignal(str)  # 快捷键触发 (动作名称)
    shortcuts_changed = pyqtSignal()      # 快捷键配置改变

    def __init__(self, parent=None, config_file: str = "config/shortcuts.json"):
        """
        初始化快捷键管理器

        Args:
            parent: 父对象
            config_file: 配置文件路径
        """
        super().__init__(parent)

        self.config_file = config_file
        self.shortcuts = {}  # 快捷键映射 {key_sequence: action_name}
        self.actions = {}    # 动作映射 {action_name: ShortcutAction}
        self.qt_shortcuts = {}  # Qt快捷键对象 {action_name: QShortcut}

        # 初始化默认快捷键
        self.init_default_shortcuts()

        # 加载用户配置
        self.load_shortcuts()

    def init_default_shortcuts(self):
        """初始化默认快捷键"""
        # 文件操作
        self.register_action("open_file", "打开文件", "Ctrl+O", "文件操作")
        self.register_action("save_file", "保存文件", "Ctrl+S", "文件操作")
        self.register_action("save_as", "另存为", "Ctrl+Shift+S", "文件操作")
        self.register_action("close_file", "关闭文件", "Ctrl+W", "文件操作")
        self.register_action("quit", "退出程序", "Ctrl+Q", "文件操作")

        # 编辑操作
        self.register_action("undo", "撤销", "Ctrl+Z", "编辑操作")
        self.register_action("redo", "重做", "Ctrl+Y", "编辑操作")
        self.register_action("copy", "复制", "Ctrl+C", "编辑操作")
        self.register_action("paste", "粘贴", "Ctrl+V", "编辑操作")
        self.register_action("delete", "删除", "Delete", "编辑操作")
        self.register_action("select_all", "全选", "Ctrl+A", "编辑操作")

        # 视图操作
        self.register_action("zoom_in", "放大", "Ctrl+Plus", "视图操作")
        self.register_action("zoom_out", "缩小", "Ctrl+Minus", "视图操作")
        self.register_action("zoom_fit", "适应窗口", "Ctrl+0", "视图操作")
        self.register_action("zoom_original", "原始大小", "Ctrl+1", "视图操作")
        self.register_action("toggle_fullscreen", "全屏切换", "F11", "视图操作")
        self.register_action("toggle_labels", "切换标签面板", "Ctrl+Shift+T", "视图操作")
        self.register_action("toggle_draw_square",
                             "切换矩形绘制", "Ctrl+Shift+R", "视图操作")
        self.register_action("single_class_mode", "单类模式",
                             "Ctrl+Shift+S", "视图操作")
        self.register_action("display_label_option",
                             "显示标签选项", "Ctrl+Shift+L", "视图操作")

        # 导航操作 (注意：A/D键由原有系统处理，避免冲突)
        self.register_action("next_image", "下一张图像", "Ctrl+Right", "导航操作")
        self.register_action("prev_image", "上一张图像", "Ctrl+Left", "导航操作")
        self.register_action("first_image", "第一张图像", "Home", "导航操作")
        self.register_action("last_image", "最后一张图像", "End", "导航操作")

        # 标注操作
        self.register_action("create_rect", "创建矩形", "R", "标注操作")
        self.register_action("create_polygon", "创建多边形", "P", "标注操作")
        self.register_action("create_circle", "创建圆形", "C", "标注操作")
        self.register_action("create_line", "创建线条", "L", "标注操作")
        self.register_action("edit_mode", "编辑模式", "E", "标注操作")
        self.register_action("duplicate_shape", "复制形状", "Ctrl+D", "标注操作")

        # AI助手操作
        self.register_action("ai_predict_current",
                             "AI预测当前图像", "Ctrl+P", "AI助手")
        self.register_action("ai_predict_batch", "AI批量预测",
                             "Ctrl+Shift+P", "AI助手")
        self.register_action("ai_toggle_panel", "切换AI面板", "F9", "AI助手")
        self.register_action("ai_increase_confidence",
                             "提高置信度", "Ctrl+Up", "AI助手")
        self.register_action("ai_decrease_confidence",
                             "降低置信度", "Ctrl+Down", "AI助手")
        self.register_action("ai_apply_predictions",
                             "应用预测结果", "Ctrl+Enter", "AI助手")
        self.register_action("ai_clear_predictions",
                             "清除预测结果", "Ctrl+Delete", "AI助手")

        # 批量操作
        self.register_action("batch_operations", "批量操作", "Ctrl+B", "批量操作")
        self.register_action("batch_copy", "批量复制", "Ctrl+Shift+C", "批量操作")
        self.register_action("batch_delete", "批量删除", "Ctrl+Shift+D", "批量操作")
        self.register_action("batch_convert", "批量转换", "Ctrl+Shift+T", "批量操作")

        # 工具操作
        self.register_action("toggle_labels", "切换标签显示", "T", "工具操作")
        self.register_action("toggle_shapes", "切换形状显示", "S", "工具操作")
        self.register_action("toggle_grid", "切换网格", "G", "工具操作")
        self.register_action("color_dialog", "颜色选择", "Ctrl+Shift+L", "工具操作")

        # 帮助操作
        self.register_action("show_help", "显示帮助", "F1", "帮助操作")
        self.register_action("show_shortcuts", "显示快捷键", "Ctrl+H", "帮助操作")
        self.register_action("about", "关于", "Ctrl+Shift+A", "帮助操作")

    def register_action(self, name: str, description: str, default_key: str,
                        category: str, callback: Callable = None) -> bool:
        """
        注册快捷键动作

        Args:
            name: 动作名称
            description: 动作描述
            default_key: 默认快捷键
            category: 分类
            callback: 回调函数

        Returns:
            bool: 注册是否成功
        """
        try:
            action = ShortcutAction(
                name=name,
                description=description,
                default_key=default_key,
                current_key=default_key,
                category=category,
                callback=callback
            )

            self.actions[name] = action
            logger.debug(f"注册快捷键动作: {name} ({default_key})")

            return True

        except Exception as e:
            logger.error(f"注册快捷键动作失败: {str(e)}")
            return False

    def set_callback(self, action_name: str, callback: Callable) -> bool:
        """
        设置动作回调函数

        Args:
            action_name: 动作名称
            callback: 回调函数

        Returns:
            bool: 设置是否成功
        """
        try:
            if action_name in self.actions:
                self.actions[action_name].callback = callback

                # 如果已经创建了Qt快捷键，更新回调
                if action_name in self.qt_shortcuts:
                    self.qt_shortcuts[action_name].activated.disconnect()
                    self.qt_shortcuts[action_name].activated.connect(callback)

                return True
            else:
                logger.warning(f"动作不存在: {action_name}")
                return False

        except Exception as e:
            logger.error(f"设置回调函数失败: {str(e)}")
            return False

    def create_qt_shortcuts(self, parent_widget: QWidget):
        """
        创建Qt快捷键对象

        Args:
            parent_widget: 父窗口部件
        """
        try:
            # 清除现有快捷键
            for shortcut in self.qt_shortcuts.values():
                shortcut.setParent(None)
                shortcut.deleteLater()
            self.qt_shortcuts.clear()
            self.shortcuts.clear()

            # 创建新的快捷键
            for action_name, action in self.actions.items():
                if action.enabled and action.current_key:
                    try:
                        shortcut = QShortcut(QKeySequence(
                            action.current_key), parent_widget)

                        # 连接信号
                        if action.callback:
                            shortcut.activated.connect(action.callback)
                        else:
                            shortcut.activated.connect(
                                lambda name=action_name: self.shortcut_triggered.emit(name))

                        self.qt_shortcuts[action_name] = shortcut
                        self.shortcuts[action.current_key] = action_name

                        logger.debug(
                            f"创建快捷键: {action.current_key} -> {action_name}")

                    except Exception as e:
                        logger.warning(f"创建快捷键失败 {action_name}: {str(e)}")

            logger.info(f"创建了 {len(self.qt_shortcuts)} 个快捷键")

        except Exception as e:
            logger.error(f"创建Qt快捷键失败: {str(e)}")

    def apply_shortcuts(self, parent_widget: QWidget):
        """
        应用快捷键到指定的父窗口部件

        Args:
            parent_widget: 父窗口部件
        """
        self.create_qt_shortcuts(parent_widget)

    def update_shortcut(self, action_name: str, new_key: str) -> bool:
        """
        更新快捷键

        Args:
            action_name: 动作名称
            new_key: 新的快捷键

        Returns:
            bool: 更新是否成功
        """
        try:
            if action_name not in self.actions:
                logger.warning(f"动作不存在: {action_name}")
                return False

            # 检查快捷键冲突
            if new_key and new_key in self.shortcuts and self.shortcuts[new_key] != action_name:
                conflicting_action = self.shortcuts[new_key]
                logger.warning(f"快捷键冲突: {new_key} 已被 {conflicting_action} 使用")
                return False

            action = self.actions[action_name]
            old_key = action.current_key

            # 更新动作
            action.current_key = new_key

            # 更新快捷键映射
            if old_key in self.shortcuts:
                del self.shortcuts[old_key]

            if new_key:
                self.shortcuts[new_key] = action_name

            # 更新Qt快捷键
            if action_name in self.qt_shortcuts:
                self.qt_shortcuts[action_name].setKey(
                    QKeySequence(new_key) if new_key else QKeySequence())

            logger.info(f"更新快捷键: {action_name} {old_key} -> {new_key}")

            # 发送变更信号
            self.shortcuts_changed.emit()

            return True

        except Exception as e:
            logger.error(f"更新快捷键失败: {str(e)}")
            return False

    def enable_action(self, action_name: str, enabled: bool = True) -> bool:
        """
        启用/禁用动作

        Args:
            action_name: 动作名称
            enabled: 是否启用

        Returns:
            bool: 操作是否成功
        """
        try:
            if action_name not in self.actions:
                logger.warning(f"动作不存在: {action_name}")
                return False

            self.actions[action_name].enabled = enabled

            # 更新Qt快捷键
            if action_name in self.qt_shortcuts:
                self.qt_shortcuts[action_name].setEnabled(enabled)

            logger.debug(f"{'启用' if enabled else '禁用'}动作: {action_name}")

            return True

        except Exception as e:
            logger.error(f"启用/禁用动作失败: {str(e)}")
            return False

    def get_actions_by_category(self) -> Dict[str, List[ShortcutAction]]:
        """按分类获取动作列表"""
        categories = {}

        for action in self.actions.values():
            if action.category not in categories:
                categories[action.category] = []
            categories[action.category].append(action)

        # 按名称排序
        for category_actions in categories.values():
            category_actions.sort(key=lambda x: x.name)

        return categories

    def get_action(self, action_name: str) -> Optional[ShortcutAction]:
        """获取指定动作"""
        return self.actions.get(action_name)

    def find_conflicts(self, key_sequence: str, exclude_action: str = None) -> List[str]:
        """
        查找快捷键冲突

        Args:
            key_sequence: 快捷键序列
            exclude_action: 排除的动作名称

        Returns:
            List[str]: 冲突的动作名称列表
        """
        conflicts = []

        for action_name, action in self.actions.items():
            if (action_name != exclude_action and
                action.current_key == key_sequence and
                    action.enabled):
                conflicts.append(action_name)

        return conflicts

    def save_shortcuts(self) -> bool:
        """保存快捷键配置到文件"""
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)

            # 准备保存数据
            config_data = {
                'version': '1.0',
                'shortcuts': {}
            }

            for action_name, action in self.actions.items():
                config_data['shortcuts'][action_name] = {
                    'current_key': action.current_key,
                    'enabled': action.enabled
                }

            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"快捷键配置已保存到: {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"保存快捷键配置失败: {str(e)}")
            return False

    def load_shortcuts(self) -> bool:
        """从文件加载快捷键配置"""
        try:
            if not os.path.exists(self.config_file):
                logger.info("快捷键配置文件不存在，使用默认配置")
                return True

            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            shortcuts_config = config_data.get('shortcuts', {})

            # 应用配置
            for action_name, config in shortcuts_config.items():
                if action_name in self.actions:
                    action = self.actions[action_name]

                    # 更新快捷键
                    new_key = config.get('current_key', action.default_key)
                    if new_key != action.current_key:
                        action.current_key = new_key

                    # 更新启用状态
                    enabled = config.get('enabled', True)
                    action.enabled = enabled

            logger.info(f"快捷键配置已从 {self.config_file} 加载")
            return True

        except Exception as e:
            logger.error(f"加载快捷键配置失败: {str(e)}")
            return False

    def reset_to_defaults(self) -> bool:
        """重置为默认快捷键"""
        try:
            for action in self.actions.values():
                action.current_key = action.default_key
                action.enabled = True

            # 重新创建快捷键映射
            self.shortcuts.clear()
            for action_name, action in self.actions.items():
                if action.current_key:
                    self.shortcuts[action.current_key] = action_name

            logger.info("快捷键已重置为默认配置")

            # 发送变更信号
            self.shortcuts_changed.emit()

            return True

        except Exception as e:
            logger.error(f"重置快捷键失败: {str(e)}")
            return False

    def export_shortcuts(self, file_path: str) -> bool:
        """导出快捷键配置"""
        try:
            export_data = {
                'version': '1.0',
                'export_time': QDateTime.currentDateTime().toString(Qt.ISODate),
                'shortcuts': {}
            }

            for action_name, action in self.actions.items():
                export_data['shortcuts'][action_name] = {
                    'name': action.name,
                    'description': action.description,
                    'category': action.category,
                    'default_key': action.default_key,
                    'current_key': action.current_key,
                    'enabled': action.enabled
                }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"快捷键配置已导出到: {file_path}")
            return True

        except Exception as e:
            logger.error(f"导出快捷键配置失败: {str(e)}")
            return False

    def import_shortcuts(self, file_path: str) -> bool:
        """导入快捷键配置"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"导入文件不存在: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            shortcuts_config = import_data.get('shortcuts', {})

            # 验证并应用配置
            conflicts = []
            for action_name, config in shortcuts_config.items():
                if action_name in self.actions:
                    new_key = config.get('current_key', '')
                    if new_key:
                        existing_conflicts = self.find_conflicts(
                            new_key, action_name)
                        if existing_conflicts:
                            conflicts.extend(existing_conflicts)

            if conflicts:
                logger.warning(f"导入配置存在冲突: {conflicts}")
                # 可以选择是否继续导入

            # 应用配置
            for action_name, config in shortcuts_config.items():
                if action_name in self.actions:
                    action = self.actions[action_name]
                    action.current_key = config.get(
                        'current_key', action.default_key)
                    action.enabled = config.get('enabled', True)

            # 重建快捷键映射
            self.shortcuts.clear()
            for action_name, action in self.actions.items():
                if action.current_key and action.enabled:
                    self.shortcuts[action.current_key] = action_name

            logger.info(f"快捷键配置已从 {file_path} 导入")

            # 发送变更信号
            self.shortcuts_changed.emit()

            return True

        except Exception as e:
            logger.error(f"导入快捷键配置失败: {str(e)}")
            return False


class ShortcutConfigDialog(QDialog):
    """快捷键配置对话框"""

    def __init__(self, shortcut_manager: ShortcutManager, parent=None):
        super().__init__(parent)
        self.shortcut_manager = shortcut_manager
        self.setup_ui()
        self.setup_connections()
        self.load_shortcuts()

    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("快捷键配置")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入动作名称或快捷键...")
        search_layout.addWidget(self.search_edit)

        layout.addLayout(search_layout)

        # 分类选择
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))

        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        category_layout.addWidget(self.category_combo)

        category_layout.addStretch()
        layout.addLayout(category_layout)

        # 快捷键列表
        self.shortcuts_tree = QTreeWidget()
        self.shortcuts_tree.setHeaderLabels(["动作", "描述", "快捷键", "状态"])
        self.shortcuts_tree.setAlternatingRowColors(True)
        self.shortcuts_tree.setSortingEnabled(True)
        layout.addWidget(self.shortcuts_tree)

        # 编辑区域
        edit_group = QGroupBox("编辑快捷键")
        edit_layout = QFormLayout(edit_group)

        self.action_label = QLabel("未选择")
        edit_layout.addRow("动作:", self.action_label)

        self.key_edit = QKeySequenceEdit()
        edit_layout.addRow("快捷键:", self.key_edit)

        self.enabled_check = QCheckBox("启用")
        edit_layout.addRow("", self.enabled_check)

        edit_button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("应用")
        self.apply_btn.setEnabled(False)
        edit_button_layout.addWidget(self.apply_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setEnabled(False)
        edit_button_layout.addWidget(self.reset_btn)

        edit_button_layout.addStretch()
        edit_layout.addRow("", edit_button_layout)

        layout.addWidget(edit_group)

        # 按钮
        button_layout = QHBoxLayout()

        self.import_btn = QPushButton("导入...")
        button_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("导出...")
        button_layout.addWidget(self.export_btn)

        self.reset_all_btn = QPushButton("重置全部")
        button_layout.addWidget(self.reset_all_btn)

        button_layout.addStretch()

        self.ok_btn = QPushButton("确定")
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("取消")
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        """设置信号连接"""

        # 搜索和过滤
        self.search_edit.textChanged.connect(self.filter_shortcuts)
        self.category_combo.currentTextChanged.connect(self.filter_shortcuts)

        # 快捷键选择
        self.shortcuts_tree.itemSelectionChanged.connect(
            self.on_shortcut_selected)

        # 编辑操作
        self.key_edit.keySequenceChanged.connect(self.on_key_sequence_changed)
        self.enabled_check.toggled.connect(self.on_enabled_changed)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.reset_btn.clicked.connect(self.reset_current)

        # 按钮操作
        self.import_btn.clicked.connect(self.import_shortcuts)
        self.export_btn.clicked.connect(self.export_shortcuts)
        self.reset_all_btn.clicked.connect(self.reset_all_shortcuts)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def load_shortcuts(self):
        """加载快捷键到界面"""
        try:
            # 清空树形列表
            self.shortcuts_tree.clear()

            # 获取分类
            categories = self.shortcut_manager.get_actions_by_category()

            # 更新分类下拉框
            self.category_combo.clear()
            self.category_combo.addItem("全部")
            for category in sorted(categories.keys()):
                self.category_combo.addItem(category)

            # 添加快捷键到树形列表
            for category, actions in categories.items():
                category_item = QTreeWidgetItem([category, "", "", ""])
                category_item.setData(0, Qt.UserRole, "category")
                self.shortcuts_tree.addTopLevelItem(category_item)

                for action in actions:
                    action_item = QTreeWidgetItem([
                        action.description,
                        action.description,
                        action.current_key,
                        "启用" if action.enabled else "禁用"
                    ])
                    action_item.setData(0, Qt.UserRole, action.name)
                    category_item.addChild(action_item)

                category_item.setExpanded(True)

            # 调整列宽
            for i in range(4):
                self.shortcuts_tree.resizeColumnToContents(i)

        except Exception as e:
            logger.error(f"加载快捷键失败: {str(e)}")

    def filter_shortcuts(self):
        """过滤快捷键显示"""
        try:
            search_text = self.search_edit.text().lower()
            selected_category = self.category_combo.currentText()

            for i in range(self.shortcuts_tree.topLevelItemCount()):
                category_item = self.shortcuts_tree.topLevelItem(i)
                category_name = category_item.text(0)

                # 检查分类过滤
                category_visible = (selected_category == "全部" or
                                    selected_category == category_name)

                if not category_visible:
                    category_item.setHidden(True)
                    continue

                # 检查搜索过滤
                category_has_visible_children = False

                for j in range(category_item.childCount()):
                    action_item = category_item.child(j)
                    action_name = action_item.text(0).lower()
                    action_key = action_item.text(2).lower()

                    action_visible = (not search_text or
                                      search_text in action_name or
                                      search_text in action_key)

                    action_item.setHidden(not action_visible)

                    if action_visible:
                        category_has_visible_children = True

                category_item.setHidden(not category_has_visible_children)

        except Exception as e:
            logger.error(f"过滤快捷键失败: {str(e)}")

    def on_shortcut_selected(self):
        """快捷键选择处理"""
        try:
            selected_items = self.shortcuts_tree.selectedItems()

            if not selected_items:
                self.clear_edit_area()
                return

            item = selected_items[0]
            action_name = item.data(0, Qt.UserRole)

            if action_name == "category":
                self.clear_edit_area()
                return

            # 获取动作信息
            action = self.shortcut_manager.get_action(action_name)
            if not action:
                self.clear_edit_area()
                return

            # 更新编辑区域
            self.action_label.setText(action.description)
            self.key_edit.setKeySequence(QKeySequence(action.current_key))
            self.enabled_check.setChecked(action.enabled)

            # 启用编辑按钮
            self.apply_btn.setEnabled(False)  # 初始时禁用
            self.reset_btn.setEnabled(True)

            # 保存当前编辑的动作
            self.current_action = action_name

        except Exception as e:
            logger.error(f"快捷键选择处理失败: {str(e)}")

    def clear_edit_area(self):
        """清空编辑区域"""
        self.action_label.setText("未选择")
        self.key_edit.clear()
        self.enabled_check.setChecked(False)
        self.apply_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.current_action = None

    def on_key_sequence_changed(self, key_sequence):
        """快捷键序列改变处理"""
        try:
            if hasattr(self, 'current_action') and self.current_action:
                # 检查是否有变化
                current_action = self.shortcut_manager.get_action(
                    self.current_action)
                if current_action:
                    new_key = key_sequence.toString()
                    has_changes = (new_key != current_action.current_key or
                                   self.enabled_check.isChecked() != current_action.enabled)

                    self.apply_btn.setEnabled(has_changes)

                    # 检查冲突
                    if new_key:
                        conflicts = self.shortcut_manager.find_conflicts(
                            new_key, self.current_action)
                        if conflicts:
                            self.action_label.setText(
                                f"{current_action.description} (冲突: {', '.join(conflicts)})"
                            )
                        else:
                            self.action_label.setText(
                                current_action.description)

        except Exception as e:
            logger.error(f"快捷键序列改变处理失败: {str(e)}")

    def on_enabled_changed(self, enabled):
        """启用状态改变处理"""
        self.on_key_sequence_changed(self.key_edit.keySequence())

    def apply_changes(self):
        """应用更改"""
        try:
            if not hasattr(self, 'current_action') or not self.current_action:
                return

            new_key = self.key_edit.keySequence().toString()
            new_enabled = self.enabled_check.isChecked()

            # 更新快捷键
            success = self.shortcut_manager.update_shortcut(
                self.current_action, new_key)
            if success:
                # 更新启用状态
                self.shortcut_manager.enable_action(
                    self.current_action, new_enabled)

                # 刷新显示
                self.load_shortcuts()

                # 禁用应用按钮
                self.apply_btn.setEnabled(False)

                QMessageBox.information(self, "成功", "快捷键更新成功")
            else:
                QMessageBox.warning(self, "失败", "快捷键更新失败")

        except Exception as e:
            logger.error(f"应用更改失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"应用更改失败: {str(e)}")

    def reset_current(self):
        """重置当前快捷键"""
        try:
            if not hasattr(self, 'current_action') or not self.current_action:
                return

            action = self.shortcut_manager.get_action(self.current_action)
            if action:
                self.key_edit.setKeySequence(QKeySequence(action.default_key))
                self.enabled_check.setChecked(True)
                self.apply_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"重置当前快捷键失败: {str(e)}")

    def import_shortcuts(self):
        """导入快捷键配置"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入快捷键配置", "", "JSON文件 (*.json)"
            )

            if file_path:
                success = self.shortcut_manager.import_shortcuts(file_path)
                if success:
                    self.load_shortcuts()
                    QMessageBox.information(self, "成功", "快捷键配置导入成功")
                else:
                    QMessageBox.warning(self, "失败", "快捷键配置导入失败")

        except Exception as e:
            logger.error(f"导入快捷键配置失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def export_shortcuts(self):
        """导出快捷键配置"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出快捷键配置", "shortcuts_export.json", "JSON文件 (*.json)"
            )

            if file_path:
                success = self.shortcut_manager.export_shortcuts(file_path)
                if success:
                    QMessageBox.information(
                        self, "成功", f"快捷键配置已导出到: {file_path}")
                else:
                    QMessageBox.warning(self, "失败", "快捷键配置导出失败")

        except Exception as e:
            logger.error(f"导出快捷键配置失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def reset_all_shortcuts(self):
        """重置所有快捷键"""
        try:
            reply = QMessageBox.question(
                self, "确认重置",
                "确定要重置所有快捷键为默认设置吗？\n此操作不可撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.shortcut_manager.reset_to_defaults()
                if success:
                    self.load_shortcuts()
                    self.clear_edit_area()
                    QMessageBox.information(self, "成功", "所有快捷键已重置为默认设置")
                else:
                    QMessageBox.warning(self, "失败", "重置快捷键失败")

        except Exception as e:
            logger.error(f"重置所有快捷键失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"重置失败: {str(e)}")

    def accept(self):
        """确定按钮处理"""
        try:
            # 保存配置
            self.shortcut_manager.save_shortcuts()
            super().accept()

        except Exception as e:
            logger.error(f"保存快捷键配置失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
            super().accept()  # 即使保存失败也关闭对话框
