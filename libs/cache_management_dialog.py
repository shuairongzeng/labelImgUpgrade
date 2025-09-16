"""
缓存管理对话框
提供训练数据缓存的查看、统计和清理功能
"""

import os
from datetime import datetime
from typing import Dict, List

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from libs.cache_manager import cache_manager


class CacheManagementDialog(QDialog):
    """缓存管理对话框"""

    def __init__(self, parent=None):
        super(CacheManagementDialog, self).__init__(parent)
        self.parent = parent
        self.current_project = None
        self.cache_directories = []

        self.setWindowTitle("缓存管理")
        self.setModal(True)
        self.resize(800, 600)

        self.init_ui()
        self.get_current_project()
        self.refresh_cache_info()

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)

        # 顶部信息栏
        info_group = QGroupBox("缓存概览")
        info_layout = QGridLayout(info_group)

        # 当前项目显示
        self.project_label = QLabel("当前项目: 加载中...")
        info_layout.addWidget(QLabel("项目:"), 0, 0)
        info_layout.addWidget(self.project_label, 0, 1)

        # 总缓存大小
        self.total_size_label = QLabel("总大小: 计算中...")
        info_layout.addWidget(QLabel("总缓存:"), 1, 0)
        info_layout.addWidget(self.total_size_label, 1, 1)

        # 文件数量
        self.total_files_label = QLabel("文件数: 计算中...")
        info_layout.addWidget(QLabel("文件总数:"), 2, 0)
        info_layout.addWidget(self.total_files_label, 2, 1)

        layout.addWidget(info_group)

        # 缓存目录列表
        list_group = QGroupBox("缓存目录详情")
        list_layout = QVBoxLayout(list_group)

        # 刷新按钮
        refresh_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.refresh_cache_info)
        refresh_layout.addWidget(self.refresh_btn)
        refresh_layout.addStretch()
        list_layout.addLayout(refresh_layout)

        # 缓存目录表格
        self.cache_table = QTableWidget()
        self.cache_table.setColumnCount(6)
        self.cache_table.setHorizontalHeaderLabels([
            "项目", "类型", "目录名", "大小", "创建时间", "天数"
        ])

        # 设置表格属性
        header = self.cache_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 项目
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # 目录名
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 大小
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 创建时间
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 天数

        self.cache_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cache_table.setAlternatingRowColors(True)
        self.cache_table.setSortingEnabled(True)

        list_layout.addWidget(self.cache_table)
        layout.addWidget(list_group)

        # 操作按钮区域
        action_group = QGroupBox("清理操作")
        action_layout = QVBoxLayout(action_group)

        # 选择性清理
        selective_layout = QHBoxLayout()
        self.clean_selected_btn = QPushButton("🗑️ 清理选中目录")
        self.clean_selected_btn.clicked.connect(self.clean_selected_directories)
        self.clean_selected_btn.setEnabled(False)
        selective_layout.addWidget(self.clean_selected_btn)

        self.clean_old_btn = QPushButton("⏰ 清理7天前缓存")
        self.clean_old_btn.clicked.connect(self.clean_old_cache)
        selective_layout.addWidget(self.clean_old_btn)

        selective_layout.addStretch()
        action_layout.addLayout(selective_layout)

        # 项目清理
        project_layout = QHBoxLayout()
        self.clean_current_project_btn = QPushButton("🧹 清理当前项目缓存")
        self.clean_current_project_btn.clicked.connect(self.clean_current_project_cache)
        project_layout.addWidget(self.clean_current_project_btn)

        self.clean_all_btn = QPushButton("🚮 清理所有项目缓存")
        self.clean_all_btn.clicked.connect(self.clean_all_cache)
        self.clean_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        project_layout.addWidget(self.clean_all_btn)

        project_layout.addStretch()
        action_layout.addLayout(project_layout)

        layout.addWidget(action_group)

        # 底部按钮
        button_layout = QHBoxLayout()
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        # 连接表格选择信号
        self.cache_table.itemSelectionChanged.connect(self.on_selection_changed)

    def get_current_project(self):
        """获取当前项目"""
        try:
            from libs.project_manager import get_project_manager
            project_name = get_project_manager().get_current_project()
            self.current_project = project_name or "默认项目"
        except Exception:
            self.current_project = "默认项目"

        self.project_label.setText(f"当前项目: {self.current_project}")

    def refresh_cache_info(self):
        """刷新缓存信息"""
        try:
            # 获取统计信息
            stats = cache_manager.get_cache_statistics()

            # 更新概览信息
            self.total_size_label.setText(f"总大小: {cache_manager.format_size(stats['total_size'])}")
            self.total_files_label.setText(f"文件总数: {stats['total_files']} 个")

            # 获取缓存目录详情
            self.cache_directories = cache_manager.get_cache_directories()

            # 更新表格
            self.update_cache_table()

        except Exception as e:
            QMessageBox.warning(self, "错误", f"刷新缓存信息失败:\n{str(e)}")

    def update_cache_table(self):
        """更新缓存表格"""
        self.cache_table.setRowCount(len(self.cache_directories))

        for row, cache_dir in enumerate(self.cache_directories):
            # 项目名
            project_item = QTableWidgetItem(cache_dir['project'])
            self.cache_table.setItem(row, 0, project_item)

            # 类型
            type_text = "筛选数据集" if cache_dir['type'] == "filtered_datasets" else "临时文件"
            type_item = QTableWidgetItem(type_text)
            self.cache_table.setItem(row, 1, type_item)

            # 目录名
            name_item = QTableWidgetItem(cache_dir['name'])
            self.cache_table.setItem(row, 2, name_item)

            # 大小
            size_item = QTableWidgetItem(cache_dir['formatted_size'])
            size_item.setData(Qt.UserRole, cache_dir['size'])  # 存储原始大小用于排序
            self.cache_table.setItem(row, 3, size_item)

            # 创建时间
            time_text = cache_dir['modified_time'].strftime("%Y-%m-%d %H:%M:%S")
            time_item = QTableWidgetItem(time_text)
            time_item.setData(Qt.UserRole, cache_dir['modified_time'])  # 存储时间对象用于排序
            self.cache_table.setItem(row, 4, time_item)

            # 天数
            age_days = int(cache_dir['age_days'])
            age_item = QTableWidgetItem(f"{age_days} 天")
            age_item.setData(Qt.UserRole, age_days)  # 存储数值用于排序

            # 根据天数设置颜色
            if age_days > 30:
                age_item.setBackground(QColor(255, 235, 235))  # 浅红色
            elif age_days > 7:
                age_item.setBackground(QColor(255, 248, 235))  # 浅黄色
            else:
                age_item.setBackground(QColor(235, 255, 235))  # 浅绿色

            self.cache_table.setItem(row, 5, age_item)

        # 默认按创建时间降序排序
        self.cache_table.sortItems(4, Qt.DescendingOrder)

    def on_selection_changed(self):
        """表格选择改变"""
        selected_rows = set()
        for item in self.cache_table.selectedItems():
            selected_rows.add(item.row())

        self.clean_selected_btn.setEnabled(len(selected_rows) > 0)

    def clean_selected_directories(self):
        """清理选中的目录"""
        selected_rows = set()
        for item in self.cache_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要清理的缓存目录")
            return

        selected_dirs = [self.cache_directories[row] for row in selected_rows]

        # 确认对话框
        total_size = sum(d['size'] for d in selected_dirs)
        formatted_size = cache_manager.format_size(total_size)

        reply = QMessageBox.question(
            self, "确认清理",
            f"确定要清理选中的 {len(selected_dirs)} 个缓存目录吗？\n\n"
            f"将释放空间: {formatted_size}\n\n"
            f"此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 执行清理
        self.perform_cleanup(selected_dirs, "选中的缓存目录")

    def clean_old_cache(self):
        """清理7天前的缓存"""
        reply = QMessageBox.question(
            self, "确认清理",
            "确定要清理7天前的所有缓存吗？\n\n"
            "此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            result = cache_manager.clean_old_cache(days_old=7)
            self.show_cleanup_result(result, "7天前的缓存")
            self.refresh_cache_info()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理过期缓存失败:\n{str(e)}")

    def clean_current_project_cache(self):
        """清理当前项目缓存"""
        reply = QMessageBox.question(
            self, "确认清理",
            f"确定要清理项目 '{self.current_project}' 的所有缓存吗？\n\n"
            f"此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            project_name = None if self.current_project == "默认项目" else self.current_project
            result = cache_manager.clean_all_cache(project_name)
            self.show_cleanup_result(result, f"项目 '{self.current_project}' 的缓存")
            self.refresh_cache_info()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理项目缓存失败:\n{str(e)}")

    def clean_all_cache(self):
        """清理所有缓存"""
        reply = QMessageBox.question(
            self, "⚠️ 危险操作",
            "确定要清理所有项目的缓存吗？\n\n"
            "这将删除所有训练数据筛选的临时文件！\n"
            "此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 二次确认
        reply2 = QMessageBox.question(
            self, "最终确认",
            "这是最后一次确认！\n\n"
            "真的要删除所有缓存吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply2 != QMessageBox.Yes:
            return

        try:
            result = cache_manager.clean_all_cache()
            self.show_cleanup_result(result, "所有缓存")
            self.refresh_cache_info()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理所有缓存失败:\n{str(e)}")

    def perform_cleanup(self, directories: List[Dict], operation_name: str):
        """执行清理操作"""
        try:
            total_freed = 0
            total_files = 0
            total_dirs = 0
            errors = []

            for cache_dir in directories:
                result = cache_manager.clean_specific_directory(cache_dir['path'])
                total_freed += result['freed_size']
                total_files += result['cleaned_files']
                total_dirs += result['cleaned_dirs']
                errors.extend(result['errors'])

            # 构建结果字典
            result = {
                'freed_size': total_freed,
                'cleaned_files': total_files,
                'cleaned_dirs': total_dirs,
                'errors': errors
            }

            self.show_cleanup_result(result, operation_name)
            self.refresh_cache_info()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理操作失败:\n{str(e)}")

    def show_cleanup_result(self, result: Dict, operation_name: str):
        """显示清理结果"""
        freed_size = cache_manager.format_size(result['freed_size'])

        message = f"清理 {operation_name} 完成！\n\n"
        message += f"📊 清理统计:\n"
        message += f"• 释放空间: {freed_size}\n"
        message += f"• 删除文件: {result['cleaned_files']} 个\n"
        message += f"• 删除目录: {result['cleaned_dirs']} 个\n"

        if result['errors']:
            message += f"\n⚠️ 发生 {len(result['errors'])} 个错误:\n"
            for error in result['errors'][:3]:  # 只显示前3个错误
                message += f"• {error}\n"
            if len(result['errors']) > 3:
                message += f"• ... 还有 {len(result['errors']) - 3} 个错误\n"

        QMessageBox.information(self, "清理完成", message)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dialog = CacheManagementDialog()
    dialog.show()
    sys.exit(app.exec_())