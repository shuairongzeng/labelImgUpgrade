"""
缓存管理对话框
提供训练数据缓存的查看、统计和清理功能
"""

import os
import time
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


class CacheDataLoader(QThread):
    """
    缓存数据异步加载器
    分阶段加载缓存数据，避免UI线程阻塞
    """

    # 信号定义
    project_info_loaded = pyqtSignal(str)  # 项目信息加载完成
    basic_stats_loaded = pyqtSignal(dict)  # 基本统计信息加载完成
    directories_batch_loaded = pyqtSignal(list, int, int)  # (目录批次, 当前总数, 预估总数)
    loading_completed = pyqtSignal(list)  # 所有目录加载完成
    progress_updated = pyqtSignal(str)  # 进度更新消息
    error_occurred = pyqtSignal(str)  # 错误信号

    def __init__(self, project_name=None):
        super().__init__()
        self.project_name = project_name
        self.should_stop = False
        self.batch_size = 20  # 每批处理的目录数量

        # 设置低优先级，避免影响用户体验
        self.setPriority(QThread.LowPriority)

    def stop_loading(self):
        """停止加载"""
        self.should_stop = True

    def run(self):
        """异步加载主逻辑"""
        try:
            # 阶段1: 快速加载项目信息
            self.progress_updated.emit("正在获取项目信息...")
            project_info = self._load_project_info()
            if self.should_stop:
                return
            self.project_info_loaded.emit(project_info)

            # 短暂休息，避免CPU占用过高
            self.msleep(10)

            # 阶段2: 加载基本统计信息
            self.progress_updated.emit("正在计算缓存统计信息...")
            stats = self._load_basic_stats()
            if self.should_stop:
                return
            self.basic_stats_loaded.emit(stats)

            # 短暂休息
            self.msleep(20)

            # 阶段3: 分批加载缓存目录详情
            self.progress_updated.emit("正在扫描缓存目录...")
            all_directories = self._load_directories_in_batches()
            if self.should_stop:
                return
            self.loading_completed.emit(all_directories)

            self.progress_updated.emit("缓存信息加载完成")

        except Exception as e:
            self.error_occurred.emit(f"加载缓存数据时发生错误: {str(e)}")

    def _load_project_info(self):
        """加载项目信息"""
        try:
            from libs.project_manager import get_project_manager
            project_name = get_project_manager().get_current_project()
            return project_name or "默认项目"
        except Exception:
            return "默认项目"

    def _load_basic_stats(self):
        """加载基本统计信息"""
        try:
            return cache_manager.get_cache_statistics(self.project_name)
        except Exception as e:
            return {
                'total_size': 0,
                'total_files': 0,
                'total_dirs': 0,
                'error': str(e)
            }

    def _load_directories_in_batches(self):
        """分批加载缓存目录"""
        all_directories = []

        try:
            # 获取所有目录（这个操作可能比较慢）
            directories = cache_manager.get_cache_directories(self.project_name)
            total_dirs = len(directories)

            # 分批处理目录
            for i in range(0, len(directories), self.batch_size):
                if self.should_stop:
                    break

                batch = directories[i:i + self.batch_size]
                all_directories.extend(batch)

                        # 发送批次数据
                self.directories_batch_loaded.emit(batch, len(all_directories), total_dirs)

                # 更新进度
                progress_msg = f"正在加载缓存目录... ({len(all_directories)}/{total_dirs})"
                self.progress_updated.emit(progress_msg)

                # 适当休息，避免CPU占用过高
                if i + self.batch_size < len(directories):
                    self.msleep(50)  # 批次间50ms休息

            return all_directories

        except Exception as e:
            self.error_occurred.emit(f"加载缓存目录失败: {str(e)}")
            return all_directories


class CacheManagementDialog(QDialog):
    """缓存管理对话框"""

    def __init__(self, parent=None):
        super(CacheManagementDialog, self).__init__(parent)
        self.parent = parent
        self.current_project = None
        self.cache_directories = []
        self.data_loader = None
        self.loading_in_progress = False

        self.setWindowTitle("缓存管理")
        self.setModal(True)
        self.resize(800, 600)

        self.init_ui()

        # 异步加载数据
        self.start_async_loading()

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

        # 加载进度区域
        self.progress_widget = QWidget()
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(10, 10, 10, 10)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        # 状态文本
        self.progress_label = QLabel("正在初始化...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
                background-color: transparent;
            }
        """)
        progress_layout.addWidget(self.progress_label)

        # 取消按钮
        cancel_layout = QHBoxLayout()
        self.cancel_loading_btn = QPushButton("⛔ 取消加载")
        self.cancel_loading_btn.clicked.connect(self.cancel_loading)
        self.cancel_loading_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_layout.addStretch()
        cancel_layout.addWidget(self.cancel_loading_btn)
        cancel_layout.addStretch()
        progress_layout.addLayout(cancel_layout)

        # 设置进度区域样式
        self.progress_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin: 5px 0;
            }
        """)
        layout.addWidget(self.progress_widget)

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

        # 初始状态下禁用操作按钮
        self._set_loading_state(True)


    def refresh_cache_info(self):
        """刷新缓存信息 - 使用异步加载"""
        if self.loading_in_progress:
            return  # 如果正在加载，则忽略刷新请求

        # 清空当前数据并重新加载
        self.cache_directories.clear()
        self.cache_table.setRowCount(0)
        self.start_async_loading()

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
            # 使用异步方式刷新数据
            QTimer.singleShot(1000, self.refresh_cache_info)  # 1秒后刷新，给用户时间看清理结果
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
            # 使用异步方式刷新数据
            QTimer.singleShot(1000, self.refresh_cache_info)
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
            # 使用异步方式刷新数据
            QTimer.singleShot(1000, self.refresh_cache_info)
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
            # 使用异步方式刷新数据
            QTimer.singleShot(1000, self.refresh_cache_info)

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

    def start_async_loading(self):
        """开始异步加载数据"""
        if self.loading_in_progress:
            return

        self.loading_in_progress = True
        self._set_loading_state(True)

        # 停止之前的加载器
        if self.data_loader and self.data_loader.isRunning():
            self.data_loader.stop_loading()
            self.data_loader.wait(2000)

        # 创建新的数据加载器
        self.data_loader = CacheDataLoader(self.current_project)

        # 连接信号
        self.data_loader.project_info_loaded.connect(self.on_project_info_loaded)
        self.data_loader.basic_stats_loaded.connect(self.on_basic_stats_loaded)
        self.data_loader.directories_batch_loaded.connect(self.on_directories_batch_loaded)
        self.data_loader.loading_completed.connect(self.on_loading_completed)
        self.data_loader.progress_updated.connect(self.on_progress_updated)
        self.data_loader.error_occurred.connect(self.on_error_occurred)

        # 开始加载
        self.data_loader.start()

    def _set_loading_state(self, loading):
        """设置加载状态"""
        # 控制按钮的启用/禁用状态
        self.refresh_btn.setEnabled(not loading)
        self.clean_old_btn.setEnabled(not loading)
        self.clean_current_project_btn.setEnabled(not loading)
        self.clean_all_btn.setEnabled(not loading)

        # 选中清理按钮需要根据选中状态决定
        if not loading:
            self.on_selection_changed()  # 重新检查选中状态
        else:
            self.clean_selected_btn.setEnabled(False)

        # 显示/隐藏进度指示器
        if hasattr(self, 'progress_widget'):
            self.progress_widget.setVisible(loading)
            if loading and hasattr(self, 'progress_bar'):
                self.progress_bar.setRange(0, 0)  # 不确定进度模式
            elif hasattr(self, 'progress_bar'):
                self.progress_bar.setRange(0, 1)
                self.progress_bar.setValue(1)

    def on_project_info_loaded(self, project_name):
        """项目信息加载完成"""
        self.current_project = project_name
        self.project_label.setText(f"当前项目: {project_name}")

    def on_basic_stats_loaded(self, stats):
        """基本统计信息加载完成"""
        if 'error' in stats:
            self.total_size_label.setText(f"总大小: 加载失败")
            self.total_files_label.setText(f"文件数: 加载失败")
        else:
            self.total_size_label.setText(f"总大小: {cache_manager.format_size(stats['total_size'])}")
            self.total_files_label.setText(f"文件总数: {stats['total_files']} 个")

    def on_directories_batch_loaded(self, batch, current_total, estimated_total):
        """目录批次加载完成"""
        # 将批次数据添加到列表中
        for cache_dir in batch:
            if cache_dir not in self.cache_directories:  # 避免重复
                self.cache_directories.append(cache_dir)

        # 更新表格（只更新新添加的部分）
        self._update_cache_table_incremental(batch)

        # 更新进度条（如果有确定的总数）
        if estimated_total > 0 and hasattr(self, 'progress_bar'):
            self.progress_bar.setRange(0, estimated_total)
            self.progress_bar.setValue(current_total)

    def on_loading_completed(self, all_directories):
        """所有数据加载完成"""
        self.cache_directories = all_directories
        self.loading_in_progress = False
        self._set_loading_state(False)

        # 最终排序表格
        self.cache_table.sortItems(4, Qt.DescendingOrder)  # 按创建时间降序排序

    def on_progress_updated(self, message):
        """更新进度信息"""
        if hasattr(self, 'progress_label'):
            self.progress_label.setText(message)

        # 根据消息内容调整进度条状态
        if hasattr(self, 'progress_bar'):
            if "加载完成" in message:
                self.progress_bar.setRange(0, 1)
                self.progress_bar.setValue(1)
            elif "计算" in message or "扫描" in message:
                self.progress_bar.setRange(0, 0)  # 动画模式

    def on_error_occurred(self, error_message):
        """处理加载错误"""
        self.loading_in_progress = False
        self._set_loading_state(False)

        if hasattr(self, 'progress_label'):
            self.progress_label.setText(f"加载失败: {error_message}")
            self.progress_label.setStyleSheet("""
                QLabel {
                    color: #d32f2f;
                    font-style: italic;
                    padding: 5px;
                    background-color: transparent;
                }
            """)

        if hasattr(self, 'progress_widget'):
            self.progress_widget.setStyleSheet("""
                QWidget {
                    background-color: #ffebee;
                    border: 1px solid #f44336;
                    border-radius: 6px;
                    margin: 5px 0;
                }
            """)

        if hasattr(self, 'cancel_loading_btn'):
            # 更改取消按钮为重试按钮
            self.cancel_loading_btn.setText("🔄 重试")
            self.cancel_loading_btn.clicked.disconnect()
            self.cancel_loading_btn.clicked.connect(self.retry_loading)

        # 显示错误对话框并提供重试选项
        reply = QMessageBox.question(
            self, "加载失败",
            f"{error_message}\n\n是否重试加载？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self.retry_loading()

    def _update_cache_table_incremental(self, new_directories):
        """增量更新缓存表格"""
        current_row_count = self.cache_table.rowCount()
        new_row_count = current_row_count + len(new_directories)

        self.cache_table.setRowCount(new_row_count)

        for i, cache_dir in enumerate(new_directories):
            row = current_row_count + i

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

    def closeEvent(self, event):
        """关闭事件 - 停止数据加载"""
        if self.data_loader and self.data_loader.isRunning():
            self.data_loader.stop_loading()
            self.data_loader.wait(2000)
        super().closeEvent(event)

    def cancel_loading(self):
        """取消加载操作"""
        if self.data_loader and self.data_loader.isRunning():
            self.data_loader.stop_loading()
            self.progress_label.setText("加载已取消")
            self.loading_in_progress = False
            self._set_loading_state(False)

            # 恢复取消按钮状态
            if hasattr(self, 'cancel_loading_btn'):
                self.cancel_loading_btn.setText("🔄 重新加载")
                self.cancel_loading_btn.clicked.disconnect()
                self.cancel_loading_btn.clicked.connect(self.retry_loading)

    def retry_loading(self):
        """重试加载操作"""
        # 恢复按钮和样式
        if hasattr(self, 'cancel_loading_btn'):
            self.cancel_loading_btn.setText("⛔ 取消加载")
            self.cancel_loading_btn.clicked.disconnect()
            self.cancel_loading_btn.clicked.connect(self.cancel_loading)

        if hasattr(self, 'progress_widget'):
            self.progress_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    margin: 5px 0;
                }
            """)

        # 清空当前数据并重新加载
        self.cache_directories.clear()
        self.cache_table.setRowCount(0)
        self.start_async_loading()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dialog = CacheManagementDialog()
    dialog.show()
    sys.exit(app.exec_())