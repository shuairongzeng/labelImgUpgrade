#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目管理GUI组件集成测试
测试项目管理对话框和项目选择器组件的功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt

from libs.project_management_dialog import ProjectManagementDialog
from libs.project_selector import ProjectSelector, ProjectSelectorToolBar
from libs.project_manager import get_project_manager
from libs.ui_styles import ButtonStyles

class TestWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("项目管理系统测试")
        self.setGeometry(100, 100, 1000, 700)
        
        # 应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
                color: #212121;
                font-family: 'Microsoft YaHei', sans-serif;
            }
        """)
        
        self.setup_ui()
        self.setup_test_data()
        
    def setup_ui(self):
        """设置界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QWidget()
        title_layout = QHBoxLayout(title_label)
        
        title_text = QPushButton("🏗️ 项目管理系统功能测试")
        title_text.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 24px;
                font-weight: bold;
                color: #1976d2;
                text-align: left;
                padding: 10px;
            }
        """)
        title_text.setEnabled(False)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        layout.addWidget(title_label)
        
        # 项目选择器测试区域
        selector_group = QWidget()
        selector_layout = QVBoxLayout(selector_group)
        
        selector_title = QPushButton("📋 项目选择器组件测试")
        selector_title.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                border: 2px solid #1976d2;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: 600;
                color: #1976d2;
                text-align: left;
            }
        """)
        selector_title.setEnabled(False)
        selector_layout.addWidget(selector_title)
        
        # 独立项目选择器
        self.project_selector = ProjectSelector()
        self.project_selector.project_switched.connect(self.on_project_switched)
        selector_layout.addWidget(self.project_selector)
        
        # 工具栏版本项目选择器
        self.toolbar_selector = ProjectSelectorToolBar()
        self.toolbar_selector.project_switched.connect(self.on_project_switched)
        selector_layout.addWidget(self.toolbar_selector)
        
        layout.addWidget(selector_group)
        
        # 控制按钮区域
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(12)
        
        # 项目管理对话框按钮
        self.management_btn = QPushButton("🗂️ 打开项目管理对话框")
        self.management_btn.setStyleSheet(ButtonStyles.primary_button())
        self.management_btn.clicked.connect(self.show_project_management)
        button_layout.addWidget(self.management_btn)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新项目列表")
        self.refresh_btn.setStyleSheet(ButtonStyles.secondary_button())
        self.refresh_btn.clicked.connect(self.refresh_projects)
        button_layout.addWidget(self.refresh_btn)
        
        # 创建测试项目按钮
        self.test_project_btn = QPushButton("🧪 创建测试项目")
        self.test_project_btn.setStyleSheet(ButtonStyles.outline_button())
        self.test_project_btn.clicked.connect(self.create_test_projects)
        button_layout.addWidget(self.test_project_btn)
        
        button_layout.addStretch()
        
        # 项目信息显示按钮
        self.info_btn = QPushButton("ℹ️ 显示项目信息")
        self.info_btn.setStyleSheet(ButtonStyles.outline_button())
        self.info_btn.clicked.connect(self.show_project_info)
        button_layout.addWidget(self.info_btn)
        
        layout.addWidget(button_group)
        
        # 状态显示区域
        self.status_label = QPushButton("✅ 项目管理系统已就绪")
        self.status_label.setStyleSheet("""
            QPushButton {
                background-color: #e8f5e8;
                border: 2px solid #4caf50;
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 500;
                color: #2e7d32;
                text-align: left;
            }
        """)
        self.status_label.setEnabled(False)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def setup_test_data(self):
        """设置测试数据"""
        try:
            manager = get_project_manager()
            
            # 显示当前项目信息
            current_project = manager.get_current_project()
            projects = manager.list_projects()
            
            status_text = f"📊 当前项目: {current_project} | 总项目数: {len(projects)}"
            self.status_label.setText(status_text)
            
            print(f"[TEST] 当前项目: {current_project}")
            print(f"[TEST] 可用项目: {list(projects.keys())}")
            
        except Exception as e:
            print(f"[TEST ERROR] 设置测试数据失败: {e}")
            self.status_label.setText(f"❌ 初始化失败: {str(e)}")
            self.status_label.setStyleSheet("""
                QPushButton {
                    background-color: #ffebee;
                    border: 2px solid #f44336;
                    border-radius: 6px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    color: #c62828;
                    text-align: left;
                }
            """)
    
    def on_project_switched(self, project_name: str):
        """处理项目切换"""
        print(f"[TEST] 项目切换事件: {project_name}")
        
        try:
            manager = get_project_manager()
            metadata = manager.get_project_metadata(project_name)
            
            if metadata:
                display_name = metadata.display_name
                description = metadata.description[:50] + "..." if len(metadata.description) > 50 else metadata.description
                status_text = f"🔄 已切换到: {display_name}"
                if description:
                    status_text += f" | {description}"
            else:
                status_text = f"🔄 已切换到项目: {project_name}"
            
            self.status_label.setText(status_text)
            
            # 刷新其他组件
            self.refresh_projects()
            
        except Exception as e:
            print(f"[TEST ERROR] 处理项目切换失败: {e}")
            self.status_label.setText(f"❌ 项目切换失败: {str(e)}")
    
    def show_project_management(self):
        """显示项目管理对话框"""
        try:
            dialog = ProjectManagementDialog(self)
            dialog.project_switched.connect(self.on_project_switched)
            dialog.exec_()
            
            # 刷新项目列表
            self.refresh_projects()
            
        except Exception as e:
            print(f"[TEST ERROR] 显示项目管理对话框失败: {e}")
            self.status_label.setText(f"❌ 对话框打开失败: {str(e)}")
    
    def refresh_projects(self):
        """刷新项目列表"""
        try:
            self.project_selector.refresh()
            self.toolbar_selector.refresh()
            
            # 更新状态显示
            manager = get_project_manager()
            current_project = manager.get_current_project()
            projects = manager.list_projects()
            
            status_text = f"🔄 已刷新 | 当前: {current_project} | 总数: {len(projects)}"
            self.status_label.setText(status_text)
            
            print(f"[TEST] 项目列表已刷新，当前项目: {current_project}")
            
        except Exception as e:
            print(f"[TEST ERROR] 刷新项目列表失败: {e}")
            self.status_label.setText(f"❌ 刷新失败: {str(e)}")
    
    def create_test_projects(self):
        """创建测试项目"""
        try:
            manager = get_project_manager()
            
            test_projects = [
                {
                    "name": "demo_cats_dogs", 
                    "display_name": "猫狗识别演示项目",
                    "description": "用于演示宠物识别功能的示例项目，包含猫和狗的标注数据",
                    "author": "测试用户",
                    "tags": ["演示", "宠物", "分类"]
                },
                {
                    "name": "vehicle_detection",
                    "display_name": "车辆检测项目", 
                    "description": "交通场景中的车辆检测和分类，支持多种车型识别",
                    "author": "AI团队",
                    "tags": ["交通", "检测", "车辆"]
                },
                {
                    "name": "medical_xray",
                    "display_name": "医学X光片分析",
                    "description": "医学影像AI辅助诊断项目，专门用于X光片异常检测",
                    "author": "医学AI实验室",
                    "tags": ["医学", "影像", "诊断"]
                }
            ]
            
            created_count = 0
            for project_data in test_projects:
                if manager.create_project(**project_data):
                    created_count += 1
                    print(f"[TEST] 创建测试项目成功: {project_data['name']}")
                else:
                    print(f"[TEST] 测试项目已存在或创建失败: {project_data['name']}")
            
            if created_count > 0:
                self.status_label.setText(f"🧪 已创建 {created_count} 个测试项目")
                self.refresh_projects()
            else:
                self.status_label.setText("ℹ️ 测试项目已存在，无需重复创建")
                
        except Exception as e:
            print(f"[TEST ERROR] 创建测试项目失败: {e}")
            self.status_label.setText(f"❌ 创建测试项目失败: {str(e)}")
    
    def show_project_info(self):
        """显示当前项目详细信息"""
        try:
            manager = get_project_manager()
            current_project = manager.get_current_project()
            metadata = manager.get_project_metadata(current_project)
            projects = manager.list_projects()
            
            info_text = f"📋 项目详情\n"
            info_text += f"{'=' * 30}\n\n"
            
            if metadata:
                info_text += f"🏷️ 项目名称: {metadata.name}\n"
                info_text += f"📖 显示名称: {metadata.display_name}\n"
                info_text += f"📝 描述: {metadata.description}\n"
                info_text += f"👤 作者: {metadata.author}\n"
                info_text += f"🏷️ 标签: {', '.join(metadata.tags)}\n"
                info_text += f"📅 创建时间: {metadata.created_at}\n"
                info_text += f"🔄 更新时间: {metadata.updated_at}\n"
                info_text += f"📌 版本: {metadata.version}\n\n"
            
            info_text += f"📊 系统统计\n"
            info_text += f"{'-' * 20}\n"
            info_text += f"总项目数: {len(projects)}\n"
            info_text += f"当前项目: {current_project}\n"
            
            # 显示所有项目
            info_text += f"\n🗂️ 所有项目:\n"
            for name, info in projects.items():
                marker = "👉 " if name == current_project else "   "
                info_text += f"{marker}{info.get('display_name', name)}\n"
            
            print(info_text)
            self.status_label.setText("ℹ️ 项目信息已输出到控制台")
            
        except Exception as e:
            print(f"[TEST ERROR] 显示项目信息失败: {e}")
            self.status_label.setText(f"❌ 获取项目信息失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("项目管理系统测试")
    app.setApplicationVersion("1.0")
    
    try:
        # 创建测试窗口
        window = TestWindow()
        window.show()
        
        print("[TEST] 项目管理系统测试启动成功")
        print("[TEST] 可以通过界面测试以下功能：")
        print("[TEST] 1. 项目选择器组件（独立版本和工具栏版本）")
        print("[TEST] 2. 项目管理对话框")
        print("[TEST] 3. 项目创建、切换、删除功能")
        print("[TEST] 4. 项目配置管理")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"[TEST ERROR] 测试启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()