#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型性能比较工具
支持多个YOLO训练会话的性能对比和分析
"""

import sys
from typing import List, Dict
import pandas as pd

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QTextEdit,
                            QSplitter, QGroupBox, QHeaderView, QCheckBox,
                            QMessageBox, QWidget)
from PyQt5.QtGui import QFont

from model_manager import TrainingSession, TrainingMetrics


class ModelComparisonDialog(QDialog):
    """模型比较对话框"""
    
    def __init__(self, sessions: List[TrainingSession], parent=None):
        super().__init__(parent)
        self.sessions = sessions
        self.selected_sessions = []
        self.setup_ui()
        self.populate_sessions()
    
    def setup_ui(self):
        self.setWindowTitle("模型性能比较")
        self.setGeometry(150, 150, 1200, 800)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("选择要比较的训练会话")
        title_label.setFont(QFont("", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # 分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 上部：会话选择
        session_widget = self.create_session_selection_widget()
        splitter.addWidget(session_widget)
        
        # 下部：比较结果
        comparison_widget = self.create_comparison_widget()
        splitter.addWidget(comparison_widget)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.compare_btn = QPushButton("开始比较")
        self.compare_btn.clicked.connect(self.perform_comparison)
        self.compare_btn.setEnabled(False)
        
        self.export_btn = QPushButton("导出报告")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.compare_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_session_selection_widget(self) -> QWidget:
        """创建会话选择区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明文本
        instruction_label = QLabel("勾选要比较的会话（建议选择2-5个）:")
        layout.addWidget(instruction_label)
        
        # 会话列表
        self.session_table = QTableWidget()
        self.session_table.setColumnCount(6)
        self.session_table.setHorizontalHeaderLabels([
            "选择", "会话名称", "日期", "mAP50-95", "质量评分", "状态"
        ])
        
        # 设置列宽
        header = self.session_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.session_table.setAlternatingRowColors(True)
        self.session_table.setMaximumHeight(250)
        
        layout.addWidget(self.session_table)
        
        return widget
    
    def create_comparison_widget(self) -> QWidget:
        """创建比较结果区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 结果标题
        result_label = QLabel("比较结果")
        result_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(result_label)
        
        # 分割器 - 表格和分析
        result_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：比较表格
        table_group = QGroupBox("详细对比")
        table_layout = QVBoxLayout(table_group)
        
        self.comparison_table = QTableWidget()
        table_layout.addWidget(self.comparison_table)
        result_splitter.addWidget(table_group)
        
        # 右侧：分析报告
        analysis_group = QGroupBox("分析报告")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_text)
        result_splitter.addWidget(analysis_group)
        
        result_splitter.setSizes([600, 400])
        layout.addWidget(result_splitter)
        
        return widget
    
    def populate_sessions(self):
        """填充会话列表"""
        self.session_table.setRowCount(len(self.sessions))
        
        for row, session in enumerate(self.sessions):
            # 确保数据已加载
            session.load_data()
            
            # 复选框
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.session_table.setCellWidget(row, 0, checkbox)
            
            # 会话信息
            name_item = QTableWidgetItem(session.session_name)
            date_item = QTableWidgetItem(session.creation_date.strftime('%m-%d %H:%M'))
            
            if session.metrics:
                map_item = QTableWidgetItem(f"{session.metrics.best_map50_95:.3f}")
                score_item = QTableWidgetItem(f"{session.metrics.get_quality_score():.1f}")
                status_item = QTableWidgetItem(session.metrics.get_training_status())
            else:
                map_item = QTableWidgetItem("N/A")
                score_item = QTableWidgetItem("0.0")
                status_item = QTableWidgetItem("未知")
            
            self.session_table.setItem(row, 1, name_item)
            self.session_table.setItem(row, 2, date_item)
            self.session_table.setItem(row, 3, map_item)
            self.session_table.setItem(row, 4, score_item)
            self.session_table.setItem(row, 5, status_item)
    
    def on_selection_changed(self):
        """选择变更事件"""
        self.selected_sessions.clear()
        
        for row in range(self.session_table.rowCount()):
            checkbox = self.session_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                self.selected_sessions.append(self.sessions[row])
        
        # 更新按钮状态
        self.compare_btn.setEnabled(len(self.selected_sessions) >= 2)
        
        if len(self.selected_sessions) > 5:
            QMessageBox.warning(self, "警告", "建议最多选择5个会话进行比较，以获得最佳显示效果")
    
    def perform_comparison(self):
        """执行模型比较"""
        if len(self.selected_sessions) < 2:
            QMessageBox.warning(self, "错误", "请至少选择2个会话进行比较")
            return
        
        # 创建比较表格
        self.create_comparison_table()
        
        # 生成分析报告
        self.generate_analysis_report()
        
        # 启用导出按钮
        self.export_btn.setEnabled(True)
    
    def create_comparison_table(self):
        """创建比较表格"""
        # 定义比较指标
        metrics_info = [
            ("会话名称", lambda s: s.session_name),
            ("创建日期", lambda s: s.creation_date.strftime('%Y-%m-%d')),
            ("mAP50", lambda s: f"{s.metrics.best_map50:.4f}" if s.metrics else "N/A"),
            ("mAP50-95", lambda s: f"{s.metrics.best_map50_95:.4f}" if s.metrics else "N/A"),
            ("精确度", lambda s: f"{s.metrics.precision:.4f}" if s.metrics else "N/A"),
            ("召回率", lambda s: f"{s.metrics.recall:.4f}" if s.metrics else "N/A"),
            ("训练轮数", lambda s: str(s.metrics.total_epochs) if s.metrics else "N/A"),
            ("收敛轮次", lambda s: str(s.metrics.convergence_epoch) if s.metrics else "N/A"),
            ("训练损失", lambda s: f"{s.metrics.final_train_loss:.4f}" if s.metrics else "N/A"),
            ("验证损失", lambda s: f"{s.metrics.final_val_loss:.4f}" if s.metrics else "N/A"),
            ("质量评分", lambda s: f"{s.metrics.get_quality_score():.1f}" if s.metrics else "0.0"),
            ("训练状态", lambda s: s.metrics.get_training_status() if s.metrics else "未知"),
        ]
        
        # 设置表格
        self.comparison_table.setRowCount(len(metrics_info))
        self.comparison_table.setColumnCount(len(self.selected_sessions))
        
        # 设置表头
        column_headers = [session.session_name for session in self.selected_sessions]
        self.comparison_table.setHorizontalHeaderLabels(column_headers)
        
        row_headers = [info[0] for info in metrics_info]
        self.comparison_table.setVerticalHeaderLabels(row_headers)
        
        # 填充数据
        for row, (metric_name, metric_func) in enumerate(metrics_info):
            for col, session in enumerate(self.selected_sessions):
                try:
                    value = metric_func(session)
                    item = QTableWidgetItem(str(value))
                    
                    # 为关键指标添加颜色标识
                    if metric_name in ["mAP50-95", "质量评分"]:
                        try:
                            numeric_value = float(value)
                            if metric_name == "mAP50-95":
                                if numeric_value >= 0.8:
                                    item.setBackground(Qt.green)
                                elif numeric_value >= 0.6:
                                    item.setBackground(Qt.yellow)
                                elif numeric_value < 0.4:
                                    item.setBackground(Qt.red)
                            elif metric_name == "质量评分":
                                if numeric_value >= 80:
                                    item.setBackground(Qt.green)
                                elif numeric_value >= 60:
                                    item.setBackground(Qt.yellow)
                                elif numeric_value < 40:
                                    item.setBackground(Qt.red)
                        except:
                            pass
                    
                    self.comparison_table.setItem(row, col, item)
                except:
                    self.comparison_table.setItem(row, col, QTableWidgetItem("N/A"))
        
        # 调整列宽
        self.comparison_table.resizeColumnsToContents()
    
    def generate_analysis_report(self):
        """生成分析报告"""
        if not self.selected_sessions:
            return
        
        # 过滤有指标的会话
        sessions_with_metrics = [s for s in self.selected_sessions if s.metrics]
        
        if not sessions_with_metrics:
            self.analysis_text.setText("所选会话中没有可用的性能指标数据")
            return
        
        report = "=== 模型性能比较分析报告 ===\n\n"
        
        # 1. 基本统计
        report += f"比较会话数量: {len(self.selected_sessions)}\n"
        report += f"有效数据会话: {len(sessions_with_metrics)}\n\n"
        
        # 2. 最佳表现者
        if sessions_with_metrics:
            best_map = max(sessions_with_metrics, key=lambda s: s.metrics.best_map50_95)
            best_quality = max(sessions_with_metrics, key=lambda s: s.metrics.get_quality_score())
            fastest_converge = min(sessions_with_metrics, key=lambda s: s.metrics.convergence_epoch)
            
            report += "=== 最佳表现者 ===\n"
            report += f"最高mAP50-95: {best_map.session_name} ({best_map.metrics.best_map50_95:.4f})\n"
            report += f"最高质量评分: {best_quality.session_name} ({best_quality.metrics.get_quality_score():.1f})\n"
            report += f"最快收敛: {fastest_converge.session_name} ({fastest_converge.metrics.convergence_epoch}轮)\n\n"
        
        # 3. 性能统计
        map_values = [s.metrics.best_map50_95 for s in sessions_with_metrics]
        quality_scores = [s.metrics.get_quality_score() for s in sessions_with_metrics]
        convergence_epochs = [s.metrics.convergence_epoch for s in sessions_with_metrics]
        
        report += "=== 性能统计 ===\n"
        report += f"mAP50-95 - 最高: {max(map_values):.4f}, 最低: {min(map_values):.4f}, 平均: {sum(map_values)/len(map_values):.4f}\n"
        report += f"质量评分 - 最高: {max(quality_scores):.1f}, 最低: {min(quality_scores):.1f}, 平均: {sum(quality_scores)/len(quality_scores):.1f}\n"
        report += f"收敛轮次 - 最快: {min(convergence_epochs)}, 最慢: {max(convergence_epochs)}, 平均: {sum(convergence_epochs)/len(convergence_epochs):.1f}\n\n"
        
        # 4. 训练效率分析
        report += "=== 训练效率分析 ===\n"
        for session in sessions_with_metrics:
            efficiency = session.metrics.convergence_epoch / session.metrics.total_epochs
            efficiency_desc = "高效" if efficiency < 0.5 else "正常" if efficiency < 0.8 else "缓慢"
            report += f"{session.session_name}: {efficiency_desc} (收敛比例: {efficiency:.1%})\n"
        
        report += "\n"
        
        # 5. 过拟合风险分析
        report += "=== 过拟合风险分析 ===\n"
        for session in sessions_with_metrics:
            loss_diff = abs(session.metrics.final_val_loss - session.metrics.final_train_loss)
            risk_level = "低" if loss_diff < 0.1 else "中等" if loss_diff < 0.3 else "高"
            report += f"{session.session_name}: {risk_level}风险 (损失差异: {loss_diff:.4f})\n"
        
        report += "\n"
        
        # 6. 改进建议
        report += "=== 改进建议 ===\n"
        
        # 找出需要改进的会话
        poor_performers = [s for s in sessions_with_metrics if s.metrics.best_map50_95 < 0.6]
        if poor_performers:
            report += "性能待提升的会话:\n"
            for session in poor_performers:
                report += f"• {session.session_name}: 考虑增加训练轮数或调整超参数\n"
        
        # 检查过拟合问题
        overfitting_sessions = [s for s in sessions_with_metrics 
                               if abs(s.metrics.final_val_loss - s.metrics.final_train_loss) > 0.3]
        if overfitting_sessions:
            report += "\n存在过拟合风险的会话:\n"
            for session in overfitting_sessions:
                report += f"• {session.session_name}: 考虑添加正则化或数据增强\n"
        
        # 收敛缓慢的会话
        slow_converge_sessions = [s for s in sessions_with_metrics 
                                 if s.metrics.convergence_epoch > s.metrics.total_epochs * 0.8]
        if slow_converge_sessions:
            report += "\n收敛缓慢的会话:\n"
            for session in slow_converge_sessions:
                report += f"• {session.session_name}: 考虑调整学习率或优化器参数\n"
        
        self.analysis_text.setText(report)
    
    def export_report(self):
        """导出比较报告"""
        if not self.selected_sessions:
            return
        
        try:
            # 生成文件名
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"model_comparison_report_{timestamp}.txt"
            
            # 准备报告内容
            content = f"YOLO模型性能比较报告\n"
            content += f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
            content += f"比较会话: {', '.join([s.session_name for s in self.selected_sessions])}\n\n"
            
            # 添加分析报告
            content += self.analysis_text.toPlainText()
            
            # 保存文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            QMessageBox.information(self, "导出成功", f"报告已保存为: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"保存报告时出错: {str(e)}")


def main():
    """测试用主函数"""
    from PyQt5.QtWidgets import QApplication
    from model_manager import TrainingSessionManager
    
    app = QApplication(sys.argv)
    
    # 加载会话数据
    manager = TrainingSessionManager()
    sessions = manager.scan_sessions()
    
    if len(sessions) < 2:
        print("至少需要2个训练会话才能进行比较")
        return
    
    # 加载数据
    for session in sessions:
        session.load_data()
    
    # 显示比较对话框
    dialog = ModelComparisonDialog(sessions)
    dialog.exec_()


if __name__ == "__main__":
    main()