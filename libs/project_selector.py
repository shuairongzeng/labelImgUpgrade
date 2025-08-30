#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目选择器组件
集成到主工具栏的项目选择和快速切换组件
"""

import sys
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QComboBox, QPushButton, QToolButton, QMenu, 
                             QFrame, QSizePolicy, QApplication, QMainWindow,
                             QMessageBox, QProgressBar, QGraphicsEffect,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter, QLinearGradient
from typing import Dict, List, Optional

from libs.project_manager import get_project_manager
from libs.project_management_dialog import ProjectManagementDialog
from libs.ui_styles import (UIColors, ButtonStyles, InteractionStyles, 
                           LabelStyles, UIRadius, UISpacing)
from libs.logger_config import get_logger

logger = get_logger(__name__)

class ProjectStatusIndicator(QLabel):
    """项目状态指示器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.status = "normal"  # normal, active, warning, error
        self.update_style()
        
    def set_status(self, status: str):
        """设置状态"""
        self.status = status
        self.update_style()
        
    def update_style(self):
        """更新样式"""
        colors = {
            "normal": UIColors.GREY_400,
            "active": UIColors.SUCCESS,
            "warning": UIColors.WARNING,
            "error": UIColors.ERROR
        }
        
        color = colors.get(self.status, UIColors.GREY_400)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
                border: 2px solid white;
            }}
        """)

class ProjectQuickSelector(QComboBox):
    """项目快速选择下拉框"""
    
    project_changed = pyqtSignal(str)  # 项目切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_projects()
        
        # 连接信号
        self.currentTextChanged.connect(self.on_selection_changed)
        
    def setup_ui(self):
        """设置界面"""
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 2px solid {UIColors.PRIMARY};
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM} {UISpacing.MD};
                min-width: 120px;
                font-size: 13px;
                font-weight: 500;
                color: {UIColors.TEXT_PRIMARY};
            }}
            QComboBox:hover {{
                border-color: {UIColors.PRIMARY_DARK};
                background-color: {UIColors.INFO_LIGHT};
            }}
            QComboBox:focus {{
                border-color: {UIColors.PRIMARY_DARK};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
                padding-right: {UISpacing.SM};
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 3px solid {UIColors.PRIMARY};
                width: 8px;
                height: 8px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid {UIColors.PRIMARY};
                border-radius: {UIRadius.MD};
                background-color: white;
                selection-background-color: {UIColors.PRIMARY_LIGHT};
                selection-color: {UIColors.PRIMARY_DARK};
                outline: none;
                padding: {UISpacing.XS};
            }}
            QComboBox QAbstractItemView::item {{
                padding: {UISpacing.SM};
                margin: {UISpacing.XS};
                border-radius: {UIRadius.SM};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {UIColors.GREY_100};
                color: {UIColors.PRIMARY};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {UIColors.PRIMARY};
                color: white;
                font-weight: 600;
            }}
        """)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def load_projects(self):
        """加载项目列表"""
        try:
            self.blockSignals(True)  # 临时阻止信号
            self.clear()
            
            manager = get_project_manager()
            projects = manager.list_projects()
            current_project = manager.get_current_project()
            
            current_index = 0
            for i, (project_name, project_info) in enumerate(projects.items()):
                display_name = project_info.get('display_name', project_name)
                self.addItem(display_name, project_name)
                
                if project_name == current_project:
                    current_index = i
            
            self.setCurrentIndex(current_index)
            self.blockSignals(False)  # 恢复信号
            
        except Exception as e:
            logger.error(f"加载项目列表失败: {e}")
    
    def on_selection_changed(self, text):
        """处理选择变化"""
        if text:
            project_name = self.currentData()
            if project_name:
                self.project_changed.emit(project_name)
    
    def refresh(self):
        """刷新项目列表"""
        self.load_projects()

class AnimatedButton(QPushButton):
    """带动画效果的按钮"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setup_animation()
        
    def setup_animation(self):
        """设置动画效果"""
        # 添加阴影效果
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setColor(QColor(0, 0, 0, 80))
        self.shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow_effect)
        
        # 动画属性
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        # 增强阴影效果
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setOffset(0, 4)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        # 恢复阴影效果
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setOffset(0, 2)

class ProjectSelector(QWidget):
    """项目选择器主组件"""
    
    project_switched = pyqtSignal(str)  # 项目切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.management_dialog = None
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """设置界面"""
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # 项目状态指示器
        self.status_indicator = ProjectStatusIndicator()
        layout.addWidget(self.status_indicator)
        
        # 项目标签
        project_label = QLabel("项目:")
        project_label.setStyleSheet(f"""
            QLabel {{
                color: {UIColors.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(project_label)
        
        # 项目选择下拉框
        self.project_selector = ProjectQuickSelector()
        self.project_selector.project_changed.connect(self.switch_project)
        layout.addWidget(self.project_selector)
        
        # 管理按钮
        self.manage_btn = AnimatedButton("管理项目")
        self.manage_btn.setStyleSheet(ButtonStyles.outline_button())
        self.manage_btn.clicked.connect(self.show_management_dialog)
        layout.addWidget(self.manage_btn)
        
        # 设置整体样式
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {UIColors.SURFACE};
                border: 1px solid {UIColors.GREY_300};
                border-radius: {UIRadius.MD};
                padding: {UISpacing.XS};
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # 初始化状态
        self.update_status()
        
    def setup_timer(self):
        """设置定时器，定期更新状态"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # 每5秒更新一次
        
    def update_status(self):
        """更新项目状态"""
        try:
            manager = get_project_manager()
            current_project = manager.get_current_project()
            
            # 检查项目状态
            if current_project == "default":
                self.status_indicator.set_status("normal")
            else:
                # 检查项目是否有最近活动
                metadata = manager.get_project_metadata(current_project)
                if metadata:
                    self.status_indicator.set_status("active")
                else:
                    self.status_indicator.set_status("warning")
                    
        except Exception as e:
            logger.error(f"更新项目状态失败: {e}")
            self.status_indicator.set_status("error")
    
    def switch_project(self, project_name: str):
        """切换项目"""
        try:
            manager = get_project_manager()
            current_project = manager.get_current_project()
            
            if project_name == current_project:
                return
            
            # 显示切换进度
            self.show_switching_progress()
            
            # 执行切换
            if manager.switch_project(project_name):
                logger.info(f"已切换到项目: {project_name}")
                self.update_status()
                self.project_switched.emit(project_name)
                self.hide_switching_progress()
            else:
                logger.error(f"切换到项目失败: {project_name}")
                self.project_selector.refresh()  # 恢复选择
                self.hide_switching_progress()
                
        except Exception as e:
            logger.error(f"切换项目失败: {e}")
            self.project_selector.refresh()
            self.hide_switching_progress()
    
    def show_switching_progress(self):
        """显示切换进度"""
        self.manage_btn.setText("切换中...")
        self.manage_btn.setEnabled(False)
        self.project_selector.setEnabled(False)
    
    def hide_switching_progress(self):
        """隐藏切换进度"""
        self.manage_btn.setText("管理项目")
        self.manage_btn.setEnabled(True)
        self.project_selector.setEnabled(True)
    
    def show_management_dialog(self):
        """显示项目管理对话框"""
        try:
            if self.management_dialog is None:
                self.management_dialog = ProjectManagementDialog(self)
                self.management_dialog.project_switched.connect(self.on_project_switched)
            
            # 刷新对话框数据
            self.management_dialog.load_data()
            self.management_dialog.show()
            self.management_dialog.raise_()
            self.management_dialog.activateWindow()
            
        except Exception as e:
            logger.error(f"显示项目管理对话框失败: {e}")
    
    def on_project_switched(self, project_name: str):
        """处理项目切换"""
        self.project_selector.refresh()
        self.update_status()
        self.project_switched.emit(project_name)
    
    def refresh(self):
        """刷新组件状态"""
        self.project_selector.refresh()
        self.update_status()

class ProjectSelectorToolBar(QWidget):
    """项目选择器工具栏版本"""
    
    project_switched = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 添加分隔符
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"color: {UIColors.GREY_300};")
        layout.addWidget(separator)
        
        # 项目选择器
        self.project_selector = ProjectSelector()
        self.project_selector.project_switched.connect(self.project_switched.emit)
        layout.addWidget(self.project_selector)
        
        # 添加分隔符
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet(f"color: {UIColors.GREY_300};")
        layout.addWidget(separator2)
        
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    
    def refresh(self):
        """刷新组件状态"""
        self.project_selector.refresh()

# 测试用的主窗口
class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("项目选择器测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        
        # 创建工具栏
        toolbar = self.addToolBar('主工具栏')
        
        # 添加一些常规工具按钮
        toolbar.addAction("打开", self.dummy_action)
        toolbar.addAction("保存", self.dummy_action)
        toolbar.addSeparator()
        
        # 添加项目选择器到工具栏
        self.project_selector = ProjectSelectorToolBar()
        self.project_selector.project_switched.connect(self.on_project_switched)
        toolbar.addWidget(self.project_selector)
        
        # 添加更多工具按钮
        toolbar.addSeparator()
        toolbar.addAction("设置", self.dummy_action)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def dummy_action(self):
        """虚拟动作"""
        pass
        
    def on_project_switched(self, project_name: str):
        """处理项目切换"""
        self.statusBar().showMessage(f"已切换到项目: {project_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试项目选择器组件
    if len(sys.argv) > 1 and sys.argv[1] == "toolbar":
        # 测试工具栏版本
        window = TestMainWindow()
        window.show()
    else:
        # 测试独立组件
        window = QWidget()
        layout = QVBoxLayout(window)
        
        selector = ProjectSelector()
        selector.project_switched.connect(
            lambda name: print(f"项目已切换到: {name}")
        )
        layout.addWidget(selector)
        
        window.setWindowTitle("项目选择器测试")
        window.resize(400, 100)
        window.show()
    
    sys.exit(app.exec_())