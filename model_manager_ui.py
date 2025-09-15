#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
YOLO模型管理器UI界面
提供直观的模型管理和分析界面
"""

import os
import sys
from typing import List, Optional

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
                            QTabWidget, QLabel, QTextEdit, QPushButton, QCheckBox,
                            QGroupBox, QScrollArea, QMessageBox, QHeaderView,
                            QProgressBar, QComboBox, QLineEdit, QFrame)
from PyQt5.QtGui import QPixmap, QFont, QIcon

from model_manager import TrainingSessionManager, TrainingSession
from model_comparison import ModelComparisonDialog


class LoadSessionsThread(QThread):
    """异步加载训练会话的线程"""
    sessions_loaded = pyqtSignal(list)
    progress_update = pyqtSignal(int, str)
    
    def __init__(self, manager: TrainingSessionManager):
        super().__init__()
        self.manager = manager
    
    def run(self):
        try:
            self.progress_update.emit(10, "扫描训练目录...")
            sessions = self.manager.scan_sessions()
            
            if not sessions:
                self.sessions_loaded.emit([])
                return
            
            # 加载每个会话的详细数据
            for i, session in enumerate(sessions):
                progress = 10 + int((i / len(sessions)) * 80)
                self.progress_update.emit(progress, f"加载 {session.session_name}...")
                
                session.load_data()
            
            self.progress_update.emit(100, "加载完成")
            self.sessions_loaded.emit(sessions)
            
        except Exception as e:
            print(f"加载会话失败: {e}")
            self.sessions_loaded.emit([])


class SessionListWidget(QWidget):
    """训练会话列表组件"""
    session_selected = pyqtSignal(TrainingSession)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sessions = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题和筛选
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("训练会话"))
        header_layout.addStretch()
        
        # 筛选下拉框
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "优秀", "良好", "一般", "需要改进"])
        self.filter_combo.currentTextChanged.connect(self.filter_sessions)
        header_layout.addWidget(QLabel("筛选:"))
        header_layout.addWidget(self.filter_combo)
        
        layout.addLayout(header_layout)
        
        # 会话表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["会话名称", "日期", "状态", "mAP50-95", "质量评分"])
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
    
    def update_sessions(self, sessions: List[TrainingSession]):
        """更新会话列表"""
        self.sessions = sessions
        self.populate_table(sessions)
    
    def populate_table(self, sessions: List[TrainingSession]):
        """填充表格"""
        self.table.setRowCount(len(sessions))
        
        for row, session in enumerate(sessions):
            # 确保数据已加载
            if not session._loaded:
                session.load_data()
            
            # 会话名称
            name_item = QTableWidgetItem(session.session_name)
            self.table.setItem(row, 0, name_item)
            
            # 日期
            date_str = session.creation_date.strftime('%m-%d %H:%M')
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 1, date_item)
            
            # 状态
            if session.metrics:
                status = session.metrics.get_training_status()
                map_val = f"{session.metrics.best_map50_95:.3f}"
                quality = f"{session.metrics.get_quality_score():.1f}"
            else:
                status = "未知"
                map_val = "N/A"
                quality = "0.0"
            
            status_item = QTableWidgetItem(status)
            map_item = QTableWidgetItem(map_val)
            quality_item = QTableWidgetItem(quality)
            
            # 根据状态设置颜色
            color_map = {
                "优秀": "#4CAF50",
                "良好": "#FF9800", 
                "一般": "#FFC107",
                "需要改进": "#F44336"
            }
            if status in color_map:
                status_item.setData(Qt.BackgroundRole, color_map[status])
            
            self.table.setItem(row, 2, status_item)
            self.table.setItem(row, 3, map_item)
            self.table.setItem(row, 4, quality_item)
        
        # 按质量评分排序
        self.table.sortItems(4, Qt.DescendingOrder)
    
    def filter_sessions(self, filter_text: str):
        """筛选会话"""
        if filter_text == "全部":
            filtered_sessions = self.sessions
        else:
            filtered_sessions = []
            for session in self.sessions:
                if session.metrics and session.metrics.get_training_status() == filter_text:
                    filtered_sessions.append(session)
        
        self.populate_table(filtered_sessions)
    
    def on_selection_changed(self):
        """选择改变事件"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.sessions):
            session_name = self.table.item(current_row, 0).text()
            # 找到对应的session对象
            selected_session = None
            for session in self.sessions:
                if session.session_name == session_name:
                    selected_session = session
                    break
            
            if selected_session:
                self.session_selected.emit(selected_session)


class SessionDetailWidget(QWidget):
    """训练会话详细信息组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_session: Optional[TrainingSession] = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 会话标题
        self.title_label = QLabel("选择一个训练会话查看详情")
        self.title_label.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # 选项卡容器
        self.tab_widget = QTabWidget()
        
        # 概览选项卡
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "概览")
        
        # 训练曲线选项卡
        self.charts_tab = self.create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "训练曲线")
        
        # 性能分析选项卡
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "性能分析")
        
        # 数据集信息选项卡
        self.dataset_tab = self.create_dataset_tab()
        self.tab_widget.addTab(self.dataset_tab, "数据集信息")
        
        # 模型文件选项卡
        self.models_tab = self.create_models_tab()
        self.tab_widget.addTab(self.models_tab, "模型文件")
        
        layout.addWidget(self.tab_widget)
        
        # 初始状态禁用
        self.tab_widget.setEnabled(False)
    
    def create_overview_tab(self) -> QWidget:
        """创建概览选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        
        self.basic_info_text = QTextEdit()
        self.basic_info_text.setMaximumHeight(200)
        self.basic_info_text.setReadOnly(True)
        basic_layout.addWidget(self.basic_info_text)
        
        layout.addWidget(basic_group)
        
        # 性能指标组
        metrics_group = QGroupBox("关键性能指标")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_text = QTextEdit()
        self.metrics_text.setMaximumHeight(300)
        self.metrics_text.setReadOnly(True)
        metrics_layout.addWidget(self.metrics_text)
        
        layout.addWidget(metrics_group)
        
        layout.addStretch()
        return widget
    
    def create_charts_tab(self) -> QWidget:
        """创建训练曲线选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 图表选择
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(QLabel("选择图表:"))
        self.chart_combo = QComboBox()
        self.chart_combo.currentTextChanged.connect(self.load_chart)
        chart_layout.addWidget(self.chart_combo)
        chart_layout.addStretch()
        
        layout.addLayout(chart_layout)
        
        # 图表显示区域
        scroll_area = QScrollArea()
        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setText("选择要查看的图表")
        scroll_area.setWidget(self.chart_label)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        return widget
    
    def create_performance_tab(self) -> QWidget:
        """创建性能分析选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 性能评估
        eval_group = QGroupBox("性能评估")
        eval_layout = QVBoxLayout(eval_group)
        
        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        eval_layout.addWidget(self.performance_text)
        
        layout.addWidget(eval_group)
        return widget
    
    def create_dataset_tab(self) -> QWidget:
        """创建数据集信息选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 数据集信息
        dataset_group = QGroupBox("数据集配置")
        dataset_layout = QVBoxLayout(dataset_group)
        
        self.dataset_text = QTextEdit()
        self.dataset_text.setReadOnly(True)
        dataset_layout.addWidget(self.dataset_text)
        
        layout.addWidget(dataset_group)
        
        # 类别分布图
        dist_group = QGroupBox("类别分布")
        dist_layout = QVBoxLayout(dist_group)
        
        self.distribution_label = QLabel()
        self.distribution_label.setAlignment(Qt.AlignCenter)
        dist_layout.addWidget(self.distribution_label)
        
        layout.addWidget(dist_group)
        return widget
    
    def create_models_tab(self) -> QWidget:
        """创建模型文件选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 模型文件表格
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(3)
        self.models_table.setHorizontalHeaderLabels(["文件名", "大小(MB)", "路径"])
        
        header = self.models_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.models_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.copy_path_btn = QPushButton("复制路径")
        self.copy_path_btn.clicked.connect(self.copy_model_path)
        
        button_layout.addWidget(self.copy_path_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        return widget
    
    def update_session(self, session: TrainingSession):
        """更新显示的会话信息"""
        self.current_session = session
        self.title_label.setText(f"训练会话: {session.session_name}")
        self.tab_widget.setEnabled(True)
        
        # 确保数据已加载
        session.load_data()
        
        # 更新各个选项卡
        self.update_overview()
        self.update_charts()
        self.update_performance()
        self.update_dataset()
        self.update_models()
    
    def update_overview(self):
        """更新概览信息"""
        if not self.current_session:
            return
        
        session = self.current_session
        
        # 基本信息
        basic_info = f"""会话名称: {session.session_name}
创建时间: {session.creation_date.strftime('%Y年%m月%d日 %H:%M:%S')}
会话路径: {session.session_path}
"""
        
        if session.config:
            basic_info += f"""
训练配置:
- 模型: {os.path.basename(session.config.model_path)}
- 训练轮数: {session.config.epochs}
- 批次大小: {session.config.batch_size}
- 图像尺寸: {session.config.image_size}
- 设备: {session.config.device}
- 优化器: {session.config.optimizer}
- 学习率: {session.config.learning_rate}
"""
        
        self.basic_info_text.setText(basic_info)
        
        # 性能指标
        if session.metrics:
            metrics_info = f"""最佳性能指标:
• mAP50: {session.metrics.best_map50:.4f}
• mAP50-95: {session.metrics.best_map50_95:.4f}
• 精确度: {session.metrics.precision:.4f}
• 召回率: {session.metrics.recall:.4f}

训练统计:
• 总轮数: {session.metrics.total_epochs}
• 收敛轮次: {session.metrics.convergence_epoch}
• 训练时间: {session.metrics.training_time:.1f}秒
• 最终训练损失: {session.metrics.final_train_loss:.4f}
• 最终验证损失: {session.metrics.final_val_loss:.4f}

综合评估:
• 质量评分: {session.metrics.get_quality_score():.1f}/100
• 训练状态: {session.metrics.get_training_status()}
"""
        else:
            metrics_info = "无法获取性能指标数据"
        
        self.metrics_text.setText(metrics_info)
    
    def update_charts(self):
        """更新图表选项"""
        if not self.current_session:
            return
        
        charts = self.current_session.get_available_charts()
        self.chart_combo.clear()
        
        for name, path in charts:
            self.chart_combo.addItem(name, path)
        
        if charts:
            self.load_chart(charts[0][0])
    
    def load_chart(self, chart_name: str):
        """加载指定图表"""
        if not self.current_session:
            return
        
        chart_path = self.chart_combo.currentData()
        if chart_path and os.path.exists(chart_path):
            pixmap = QPixmap(chart_path)
            if not pixmap.isNull():
                # 缩放图片以适应显示
                scaled_pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.chart_label.setPixmap(scaled_pixmap)
            else:
                self.chart_label.setText("无法加载图表")
        else:
            self.chart_label.setText("图表文件不存在")
    
    def update_performance(self):
        """更新性能分析"""
        if not self.current_session or not self.current_session.metrics:
            self.performance_text.setText("无性能数据可分析")
            return
        
        session = self.current_session
        metrics = session.metrics
        
        # 生成性能分析报告
        analysis = f"""=== 模型性能分析报告 ===

1. 整体表现评估:
   • 综合质量评分: {metrics.get_quality_score():.1f}/100
   • 训练状态: {metrics.get_training_status()}
   
2. 准确性分析:
   • mAP50-95: {metrics.best_map50_95:.4f} {'(优秀)' if metrics.best_map50_95 >= 0.8 else '(良好)' if metrics.best_map50_95 >= 0.6 else '(一般)' if metrics.best_map50_95 >= 0.4 else '(待改进)'}
   • 精确度: {metrics.precision:.4f}
   • 召回率: {metrics.recall:.4f}
   
3. 训练效率分析:
   • 收敛轮次: {metrics.convergence_epoch}/{metrics.total_epochs}
   • 训练效率: {'高效' if metrics.convergence_epoch < metrics.total_epochs * 0.5 else '正常' if metrics.convergence_epoch < metrics.total_epochs * 0.8 else '缓慢'}
   
4. 过拟合检测:
   • 训练损失: {metrics.final_train_loss:.4f}
   • 验证损失: {metrics.final_val_loss:.4f}
   • 损失差异: {abs(metrics.final_val_loss - metrics.final_train_loss):.4f}
   • 过拟合风险: {'低' if abs(metrics.final_val_loss - metrics.final_train_loss) < 0.1 else '中等' if abs(metrics.final_val_loss - metrics.final_train_loss) < 0.3 else '高'}

5. 改进建议:"""
        
        # 根据指标添加建议
        if metrics.best_map50_95 < 0.6:
            analysis += "\n   • 考虑增加训练轮数或调整学习率"
            analysis += "\n   • 检查数据集质量和标注准确性"
        
        if metrics.convergence_epoch > metrics.total_epochs * 0.8:
            analysis += "\n   • 训练收敛较慢，考虑调整优化器参数"
        
        if abs(metrics.final_val_loss - metrics.final_train_loss) > 0.3:
            analysis += "\n   • 存在过拟合风险，考虑添加正则化或数据增强"
        
        if metrics.precision < 0.8:
            analysis += "\n   • 精确度较低，检查是否存在误检问题"
            
        if metrics.recall < 0.8:
            analysis += "\n   • 召回率较低，可能存在漏检问题"
        
        self.performance_text.setText(analysis)
    
    def update_dataset(self):
        """更新数据集信息"""
        if not self.current_session:
            return
        
        session = self.current_session
        
        if session.dataset_info:
            dataset_info = f"""数据集配置信息:
路径: {session.dataset_info.dataset_path}
训练集: {session.dataset_info.train_path}
验证集: {session.dataset_info.val_path}
类别数量: {session.dataset_info.num_classes}

类别列表:
"""
            for idx, name in session.dataset_info.classes.items():
                dataset_info += f"  {idx}: {name}\n"
        else:
            dataset_info = "无法获取数据集信息"
        
        self.dataset_text.setText(dataset_info)
        
        # 加载类别分布图
        if os.path.exists(session.labels_jpg_path):
            pixmap = QPixmap(session.labels_jpg_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.distribution_label.setPixmap(scaled_pixmap)
        else:
            self.distribution_label.setText("无类别分布图")
    
    def update_models(self):
        """更新模型文件信息"""
        if not self.current_session:
            return
        
        model_files = self.current_session.get_model_files()
        self.models_table.setRowCount(len(model_files))
        
        for row, (name, path, size_mb) in enumerate(model_files):
            name_item = QTableWidgetItem(name)
            size_item = QTableWidgetItem(f"{size_mb:.1f}")
            path_item = QTableWidgetItem(path)
            
            self.models_table.setItem(row, 0, name_item)
            self.models_table.setItem(row, 1, size_item)
            self.models_table.setItem(row, 2, path_item)
    
    def copy_model_path(self):
        """复制模型路径到剪贴板"""
        current_row = self.models_table.currentRow()
        if current_row >= 0:
            path_item = self.models_table.item(current_row, 2)
            if path_item:
                QApplication.clipboard().setText(path_item.text())
                QMessageBox.information(self, "提示", "模型路径已复制到剪贴板")


class ModelManagerMainWindow(QMainWindow):
    """模型管理器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.manager = TrainingSessionManager()
        self.setup_ui()
        self.load_sessions()
    
    def setup_ui(self):
        self.setWindowTitle("YOLO模型管理器")
        self.setGeometry(100, 100, 1400, 800)
        
        # 中心组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_sessions)
        
        self.compare_btn = QPushButton("模型比较")
        self.compare_btn.clicked.connect(self.show_comparison_dialog)
        
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.compare_btn)
        toolbar_layout.addStretch()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        toolbar_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(toolbar_layout)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：会话列表
        self.session_list = SessionListWidget()
        self.session_list.session_selected.connect(self.on_session_selected)
        splitter.addWidget(self.session_list)
        
        # 右侧：详细信息
        self.session_detail = SessionDetailWidget()
        splitter.addWidget(self.session_detail)
        
        # 设置分割比例
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar().showMessage("准备就绪")
    
    def load_sessions(self):
        """异步加载训练会话"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.refresh_btn.setEnabled(False)
        
        self.load_thread = LoadSessionsThread(self.manager)
        self.load_thread.sessions_loaded.connect(self.on_sessions_loaded)
        self.load_thread.progress_update.connect(self.on_progress_update)
        self.load_thread.start()
    
    def on_sessions_loaded(self, sessions: List[TrainingSession]):
        """会话加载完成"""
        self.session_list.update_sessions(sessions)
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        
        # 启用比较按钮（需要至少2个会话）
        self.compare_btn.setEnabled(len(sessions) >= 2)
        
        status_msg = f"加载完成，找到 {len(sessions)} 个训练会话"
        self.statusBar().showMessage(status_msg)
    
    def on_progress_update(self, value: int, message: str):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.statusBar().showMessage(message)
    
    def on_session_selected(self, session: TrainingSession):
        """会话选中事件"""
        self.session_detail.update_session(session)
        self.statusBar().showMessage(f"已选择: {session.session_name}")
    
    def show_comparison_dialog(self):
        """显示模型比较对话框"""
        if not hasattr(self.manager, 'sessions') or len(self.manager.sessions) < 2:
            QMessageBox.warning(self, "警告", "需要至少2个训练会话才能进行比较")
            return
        
        # 显示比较对话框
        dialog = ModelComparisonDialog(self.manager.sessions, self)
        dialog.exec_()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = ModelManagerMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()