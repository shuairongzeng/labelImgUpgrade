#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目管理对话框
提供完整的项目管理功能界面，包括创建、删除、编辑和切换项目
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QLineEdit, QTextEdit, QGroupBox, QSplitter,
                             QWidget, QScrollArea, QFrame, QMessageBox,
                             QInputDialog, QComboBox, QProgressBar, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter
from datetime import datetime
from typing import Dict, List, Optional

from libs.project_manager import get_project_manager, ProjectMetadata
from libs.ui_styles import (UIColors, ButtonStyles, InteractionStyles, 
                           LabelStyles, GroupBoxStyles, ListStyles)
from libs.logger_config import get_logger

logger = get_logger(__name__)

class ProjectInfoWidget(QWidget):
    """项目信息显示和编辑组件"""
    
    project_updated = pyqtSignal(str)  # 项目更新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_name = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 项目信息区域
        info_group = QGroupBox("项目信息")
        info_group.setStyleSheet(GroupBoxStyles.primary_group())
        info_layout = QGridLayout(info_group)
        info_layout.setSpacing(12)
        
        # 项目显示名称
        info_layout.addWidget(QLabel("显示名称:"), 0, 0)
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setStyleSheet(InteractionStyles.animated_input_field())
        self.display_name_edit.setPlaceholderText("输入项目的显示名称...")
        info_layout.addWidget(self.display_name_edit, 0, 1, 1, 2)
        
        # 项目描述
        info_layout.addWidget(QLabel("描述:"), 1, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                border: 2px solid {UIColors.GREY_300};
                border-radius: 6px;
                padding: 8px 12px;
                color: {UIColors.GREY_800};
                font-size: 13px;
                min-height: 80px;
            }}
            QTextEdit:hover {{
                border-color: {UIColors.PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {UIColors.PRIMARY};
            }}
        """)
        self.description_edit.setPlaceholderText("输入项目描述...")
        info_layout.addWidget(self.description_edit, 1, 1, 1, 2)
        
        # 作者
        info_layout.addWidget(QLabel("作者:"), 2, 0)
        self.author_edit = QLineEdit()
        self.author_edit.setStyleSheet(InteractionStyles.animated_input_field())
        self.author_edit.setPlaceholderText("输入作者名称...")
        info_layout.addWidget(self.author_edit, 2, 1, 1, 2)
        
        # 标签
        info_layout.addWidget(QLabel("标签:"), 3, 0)
        self.tags_edit = QLineEdit()
        self.tags_edit.setStyleSheet(InteractionStyles.animated_input_field())
        self.tags_edit.setPlaceholderText("输入标签，用逗号分隔...")
        info_layout.addWidget(self.tags_edit, 3, 1, 1, 2)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("保存修改")
        self.save_btn.setStyleSheet(ButtonStyles.primary_button())
        self.save_btn.clicked.connect(self.save_project_info)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setStyleSheet(ButtonStyles.outline_button())
        self.reset_btn.clicked.connect(self.reset_project_info)
        button_layout.addWidget(self.reset_btn)
        
        info_layout.addLayout(button_layout, 4, 0, 1, 3)
        
        layout.addWidget(info_group)
        
        # 项目统计信息
        stats_group = QGroupBox("项目统计")
        stats_group.setStyleSheet(GroupBoxStyles.warning_group())
        stats_layout = QGridLayout(stats_group)
        
        self.created_label = QLabel()
        self.created_label.setStyleSheet(LabelStyles.info_label())
        stats_layout.addWidget(QLabel("创建时间:"), 0, 0)
        stats_layout.addWidget(self.created_label, 0, 1)
        
        self.updated_label = QLabel()
        self.updated_label.setStyleSheet(LabelStyles.info_label())
        stats_layout.addWidget(QLabel("更新时间:"), 1, 0)
        stats_layout.addWidget(self.updated_label, 1, 1)
        
        self.version_label = QLabel()
        self.version_label.setStyleSheet(LabelStyles.info_label())
        stats_layout.addWidget(QLabel("版本:"), 2, 0)
        stats_layout.addWidget(self.version_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        # 初始化为空状态
        self.clear_info()
        
    def load_project_info(self, project_name: str):
        """加载项目信息"""
        try:
            self.project_name = project_name
            manager = get_project_manager()
            metadata = manager.get_project_metadata(project_name)
            
            if metadata:
                self.display_name_edit.setText(metadata.display_name)
                self.description_edit.setPlainText(metadata.description)
                self.author_edit.setText(metadata.author)
                self.tags_edit.setText(", ".join(metadata.tags))
                
                # 格式化时间显示
                created_time = datetime.fromisoformat(metadata.created_at.replace('Z', '+00:00'))
                updated_time = datetime.fromisoformat(metadata.updated_at.replace('Z', '+00:00'))
                
                self.created_label.setText(created_time.strftime("%Y-%m-%d %H:%M:%S"))
                self.updated_label.setText(updated_time.strftime("%Y-%m-%d %H:%M:%S"))
                self.version_label.setText(metadata.version)
                
                self.setEnabled(True)
            else:
                self.clear_info()
                
        except Exception as e:
            logger.error(f"加载项目信息失败: {e}")
            self.clear_info()
    
    def clear_info(self):
        """清空信息显示"""
        self.project_name = None
        self.display_name_edit.clear()
        self.description_edit.clear()
        self.author_edit.clear()
        self.tags_edit.clear()
        self.created_label.setText("--")
        self.updated_label.setText("--")
        self.version_label.setText("--")
        self.setEnabled(False)
    
    def save_project_info(self):
        """保存项目信息"""
        if not self.project_name:
            return
            
        try:
            manager = get_project_manager()
            
            # 解析标签
            tags_text = self.tags_edit.text().strip()
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()] if tags_text else []
            
            # 更新项目元数据
            success = manager.update_project_metadata(
                self.project_name,
                display_name=self.display_name_edit.text().strip(),
                description=self.description_edit.toPlainText().strip(),
                author=self.author_edit.text().strip(),
                tags=tags
            )
            
            if success:
                # 更新时间显示
                now = datetime.now()
                self.updated_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
                
                # 发送更新信号
                self.project_updated.emit(self.project_name)
                
                # 显示成功消息
                QMessageBox.information(self, "保存成功", "项目信息已成功保存！")
            else:
                QMessageBox.warning(self, "保存失败", "无法保存项目信息，请检查输入内容。")
                
        except Exception as e:
            logger.error(f"保存项目信息失败: {e}")
            QMessageBox.critical(self, "保存失败", f"保存项目信息时发生错误：{str(e)}")
    
    def reset_project_info(self):
        """重置项目信息到上次保存的状态"""
        if self.project_name:
            self.load_project_info(self.project_name)


class ProjectListWidget(QListWidget):
    """项目列表组件"""
    
    project_selected = pyqtSignal(str)  # 项目选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_projects()
        
    def setup_ui(self):
        """设置界面"""
        self.setStyleSheet(ListStyles.modern_list())
        self.setMinimumWidth(280)
        
        # 连接选择信号
        self.itemClicked.connect(self.on_item_clicked)
        
    def load_projects(self):
        """加载项目列表"""
        try:
            self.clear()
            manager = get_project_manager()
            projects = manager.list_projects()
            current_project = manager.get_current_project()
            
            for project_name, project_info in projects.items():
                item = QListWidgetItem()
                
                # 创建项目显示文本
                display_name = project_info.get('display_name', project_name)
                description = project_info.get('description', '').strip()
                
                if description:
                    if len(description) > 50:
                        description = description[:50] + "..."
                    text = f"{display_name}\n{description}"
                else:
                    text = display_name
                
                item.setText(text)
                item.setData(Qt.UserRole, project_name)
                
                # 标记当前项目
                if project_name == current_project:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    self.setCurrentItem(item)
                
                self.addItem(item)
                
        except Exception as e:
            logger.error(f"加载项目列表失败: {e}")
    
    def on_item_clicked(self, item):
        """处理项目选择"""
        project_name = item.data(Qt.UserRole)
        if project_name:
            self.project_selected.emit(project_name)
    
    def refresh(self):
        """刷新项目列表"""
        self.load_projects()
    
    def get_selected_project(self) -> Optional[str]:
        """获取当前选中的项目"""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None


class ProjectManagementDialog(QDialog):
    """项目管理对话框主类"""
    
    project_switched = pyqtSignal(str)  # 项目切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("项目管理")
        self.setModal(True)
        self.resize(900, 600)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        title_label = QLabel("项目管理")
        title_label.setStyleSheet(LabelStyles.title_label())
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 新建项目按钮
        self.create_btn = QPushButton("新建项目")
        self.create_btn.setStyleSheet(ButtonStyles.primary_button())
        self.create_btn.clicked.connect(self.create_project)
        title_layout.addWidget(self.create_btn)
        
        layout.addLayout(title_layout)
        
        # 主内容区域
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：项目列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 项目列表标题
        list_title = QLabel("项目列表")
        list_title.setStyleSheet(LabelStyles.section_title())
        left_layout.addWidget(list_title)
        
        # 项目列表
        self.project_list = ProjectListWidget()
        self.project_list.project_selected.connect(self.on_project_selected)
        left_layout.addWidget(self.project_list)
        
        # 项目操作按钮
        list_button_layout = QHBoxLayout()
        
        self.switch_btn = QPushButton("切换项目")
        self.switch_btn.setStyleSheet(ButtonStyles.secondary_button())
        self.switch_btn.clicked.connect(self.switch_project)
        self.switch_btn.setEnabled(False)
        list_button_layout.addWidget(self.switch_btn)
        
        self.delete_btn = QPushButton("删除项目")
        self.delete_btn.setStyleSheet(ButtonStyles.danger_button())
        self.delete_btn.clicked.connect(self.delete_project)
        self.delete_btn.setEnabled(False)
        list_button_layout.addWidget(self.delete_btn)
        
        left_layout.addLayout(list_button_layout)
        
        main_splitter.addWidget(left_widget)
        
        # 右侧：项目详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 项目详情标题
        detail_title = QLabel("项目详情")
        detail_title.setStyleSheet(LabelStyles.section_title())
        right_layout.addWidget(detail_title)
        
        # 项目信息组件
        self.project_info = ProjectInfoWidget()
        self.project_info.project_updated.connect(self.on_project_updated)
        right_layout.addWidget(self.project_info)
        
        main_splitter.addWidget(right_widget)
        
        # 设置分割器比例
        main_splitter.setSizes([350, 550])
        layout.addWidget(main_splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.setStyleSheet(ButtonStyles.outline_button())
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        """加载数据"""
        self.project_list.load_projects()
    
    def on_project_selected(self, project_name: str):
        """处理项目选择"""
        self.project_info.load_project_info(project_name)
        self.switch_btn.setEnabled(True)
        
        # default项目不能删除
        can_delete = project_name != "default"
        self.delete_btn.setEnabled(can_delete)
    
    def on_project_updated(self, project_name: str):
        """处理项目信息更新"""
        self.project_list.refresh()
    
    def create_project(self):
        """创建新项目"""
        dialog = CreateProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.project_list.refresh()
    
    def switch_project(self):
        """切换当前项目"""
        selected_project = self.project_list.get_selected_project()
        if not selected_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目！")
            return
        
        try:
            manager = get_project_manager()
            current_project = manager.get_current_project()
            
            if selected_project == current_project:
                QMessageBox.information(self, "提示", "已经是当前项目了！")
                return
            
            if manager.switch_project(selected_project):
                QMessageBox.information(self, "切换成功", f"已切换到项目：{selected_project}")
                self.project_list.refresh()
                self.project_switched.emit(selected_project)
            else:
                QMessageBox.critical(self, "切换失败", "切换项目失败，请重试！")
                
        except Exception as e:
            logger.error(f"切换项目失败: {e}")
            QMessageBox.critical(self, "切换失败", f"切换项目时发生错误：{str(e)}")
    
    def delete_project(self):
        """删除项目"""
        selected_project = self.project_list.get_selected_project()
        if not selected_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目！")
            return
        
        if selected_project == "default":
            QMessageBox.warning(self, "警告", "不能删除默认项目！")
            return
        
        # 确认删除
        manager = get_project_manager()
        metadata = manager.get_project_metadata(selected_project)
        display_name = metadata.display_name if metadata else selected_project
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除项目 '{display_name}' 吗？\n\n"
            "这将永久删除项目的所有数据和配置文件！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if manager.delete_project(selected_project):
                    QMessageBox.information(self, "删除成功", f"项目 '{display_name}' 已删除！")
                    self.project_list.refresh()
                    self.project_info.clear_info()
                    self.switch_btn.setEnabled(False)
                    self.delete_btn.setEnabled(False)
                else:
                    QMessageBox.critical(self, "删除失败", "删除项目失败，请重试！")
                    
            except Exception as e:
                logger.error(f"删除项目失败: {e}")
                QMessageBox.critical(self, "删除失败", f"删除项目时发生错误：{str(e)}")


class CreateProjectDialog(QDialog):
    """创建项目对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建新项目")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("创建新项目")
        title_label.setStyleSheet(LabelStyles.section_title())
        layout.addWidget(title_label)
        
        # 表单区域
        form_group = QGroupBox("项目信息")
        form_group.setStyleSheet(GroupBoxStyles.primary_group())
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(12)
        
        # 项目内部名称
        form_layout.addWidget(QLabel("项目名称*:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(InteractionStyles.animated_input_field())
        self.name_edit.setPlaceholderText("英文字母、数字和下划线，如: my_project")
        form_layout.addWidget(self.name_edit, 0, 1)
        
        # 显示名称
        form_layout.addWidget(QLabel("显示名称*:"), 1, 0)
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setStyleSheet(InteractionStyles.animated_input_field())
        self.display_name_edit.setPlaceholderText("项目的显示名称")
        form_layout.addWidget(self.display_name_edit, 1, 1)
        
        # 描述
        form_layout.addWidget(QLabel("描述:"), 2, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                border: 2px solid {UIColors.GREY_300};
                border-radius: 6px;
                padding: 8px 12px;
                color: {UIColors.GREY_800};
                font-size: 13px;
                min-height: 60px;
                max-height: 80px;
            }}
            QTextEdit:hover {{
                border-color: {UIColors.PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {UIColors.PRIMARY};
            }}
        """)
        self.description_edit.setPlaceholderText("简要描述项目内容...")
        form_layout.addWidget(self.description_edit, 2, 1)
        
        # 作者
        form_layout.addWidget(QLabel("作者:"), 3, 0)
        self.author_edit = QLineEdit()
        self.author_edit.setStyleSheet(InteractionStyles.animated_input_field())
        self.author_edit.setPlaceholderText("作者名称")
        form_layout.addWidget(self.author_edit, 3, 1)
        
        # 复制来源
        form_layout.addWidget(QLabel("复制配置:"), 4, 0)
        self.copy_from_combo = QComboBox()
        self.copy_from_combo.setStyleSheet(InteractionStyles.animated_combobox())
        self.copy_from_combo.addItem("创建空项目", "")
        
        # 加载现有项目列表
        try:
            manager = get_project_manager()
            projects = manager.list_projects()
            for project_name, project_info in projects.items():
                display_name = project_info.get('display_name', project_name)
                self.copy_from_combo.addItem(f"复制自: {display_name}", project_name)
        except Exception as e:
            logger.error(f"加载项目列表失败: {e}")
        
        form_layout.addWidget(self.copy_from_combo, 4, 1)
        
        layout.addWidget(form_group)
        
        # 提示信息
        info_label = QLabel("* 必填项目")
        info_label.setStyleSheet(f"color: {UIColors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(info_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet(ButtonStyles.outline_button())
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.create_btn = QPushButton("创建项目")
        self.create_btn.setStyleSheet(ButtonStyles.primary_button())
        self.create_btn.clicked.connect(self.create_project)
        button_layout.addWidget(self.create_btn)
        
        layout.addLayout(button_layout)
        
        # 自动生成显示名称
        self.name_edit.textChanged.connect(self.auto_generate_display_name)
        
    def auto_generate_display_name(self, text):
        """自动生成显示名称"""
        if not self.display_name_edit.text():
            # 将下划线替换为空格，首字母大写
            display_name = text.replace('_', ' ').title()
            self.display_name_edit.setText(display_name)
    
    def create_project(self):
        """创建项目"""
        # 验证输入
        name = self.name_edit.text().strip()
        display_name = self.display_name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入项目名称！")
            self.name_edit.setFocus()
            return
        
        if not display_name:
            QMessageBox.warning(self, "输入错误", "请输入显示名称！")
            self.display_name_edit.setFocus()
            return
        
        # 验证项目名称格式
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            QMessageBox.warning(
                self, "格式错误", 
                "项目名称必须以字母开头，只能包含字母、数字和下划线！"
            )
            self.name_edit.setFocus()
            return
        
        try:
            manager = get_project_manager()
            
            # 检查项目是否已存在
            projects = manager.list_projects()
            if name in projects:
                QMessageBox.warning(self, "创建失败", f"项目 '{name}' 已存在！")
                self.name_edit.setFocus()
                return
            
            # 获取其他参数
            description = self.description_edit.toPlainText().strip()
            author = self.author_edit.text().strip()
            copy_from = self.copy_from_combo.currentData()
            
            # 创建项目
            success = manager.create_project(
                name=name,
                display_name=display_name,
                description=description,
                author=author,
                copy_from=copy_from if copy_from else None
            )
            
            if success:
                QMessageBox.information(self, "创建成功", f"项目 '{display_name}' 创建成功！")
                self.accept()
            else:
                QMessageBox.critical(self, "创建失败", "创建项目失败，请检查输入信息！")
                
        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            QMessageBox.critical(self, "创建失败", f"创建项目时发生错误：{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试项目管理对话框
    dialog = ProjectManagementDialog()
    dialog.show()
    
    sys.exit(app.exec_())