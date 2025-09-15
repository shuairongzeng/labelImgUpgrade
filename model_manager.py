#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
YOLO模型管理器
基于现有训练输出设计的模型管理和分析工具

主要功能:
1. 扫描和管理训练会话
2. 解析训练指标和配置
3. 可视化展示训练结果
4. 模型性能比较
5. 智能评估和建议
"""

import os
import sys
import yaml
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
                            QTabWidget, QLabel, QTextEdit, QPushButton, QCheckBox,
                            QGroupBox, QScrollArea, QMessageBox, QHeaderView,
                            QProgressBar, QComboBox, QLineEdit)
from PyQt5.QtGui import QPixmap, QFont


@dataclass
class TrainingMetrics:
    """训练指标数据结构"""
    best_map50: float = 0.0
    best_map50_95: float = 0.0
    final_train_loss: float = 0.0
    final_val_loss: float = 0.0
    total_epochs: int = 0
    convergence_epoch: int = 0  # 收敛轮次
    training_time: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    
    def get_quality_score(self) -> float:
        """计算模型质量评分 (0-100)"""
        map_score = (self.best_map50_95 * 100) * 0.6  # 60% 权重
        precision_score = (self.precision * 100) * 0.2  # 20% 权重
        recall_score = (self.recall * 100) * 0.2  # 20% 权重
        return min(100.0, map_score + precision_score + recall_score)
    
    def get_training_status(self) -> str:
        """获取训练状态描述"""
        if self.best_map50_95 >= 0.8:
            return "优秀"
        elif self.best_map50_95 >= 0.6:
            return "良好"
        elif self.best_map50_95 >= 0.4:
            return "一般"
        else:
            return "需要改进"


@dataclass
class DatasetInfo:
    """数据集信息"""
    classes: Dict[int, str] = None
    dataset_path: str = ""
    train_path: str = ""
    val_path: str = ""
    num_classes: int = 0
    
    def __post_init__(self):
        if self.classes is None:
            self.classes = {}
        self.num_classes = len(self.classes)


@dataclass
class TrainingConfig:
    """训练配置信息"""
    model_path: str = ""
    epochs: int = 0
    batch_size: int = 0
    image_size: int = 640
    device: str = ""
    optimizer: str = ""
    learning_rate: float = 0.01
    data_yaml: str = ""


class TrainingSession:
    """训练会话数据模型"""
    
    def __init__(self, session_path: str):
        self.session_path = session_path
        self.session_name = os.path.basename(session_path)
        self.creation_date = self._get_creation_date()
        
        # 数据容器
        self.metrics: Optional[TrainingMetrics] = None
        self.config: Optional[TrainingConfig] = None
        self.dataset_info: Optional[DatasetInfo] = None
        self.results_df: Optional[pd.DataFrame] = None
        
        # 文件路径
        self.args_yaml_path = os.path.join(session_path, "args.yaml")
        self.results_csv_path = os.path.join(session_path, "results.csv")
        self.results_png_path = os.path.join(session_path, "results.png")
        self.confusion_matrix_path = os.path.join(session_path, "confusion_matrix.png")
        self.labels_jpg_path = os.path.join(session_path, "labels.jpg")
        self.weights_dir = os.path.join(session_path, "weights")
        
        # 状态标志
        self._loaded = False
    
    def _get_creation_date(self) -> datetime:
        """获取会话创建日期"""
        try:
            timestamp = os.path.getctime(self.session_path)
            return datetime.fromtimestamp(timestamp)
        except:
            return datetime.now()
    
    def is_valid(self) -> bool:
        """检查会话是否有效"""
        required_files = [
            self.args_yaml_path,
            self.results_csv_path
        ]
        return all(os.path.exists(f) for f in required_files)
    
    def load_data(self):
        """加载所有训练数据"""
        if self._loaded:
            return
        
        try:
            self._load_config()
            self._load_metrics()
            self._load_dataset_info()
            self._loaded = True
        except Exception as e:
            print(f"加载会话数据失败 {self.session_name}: {e}")
    
    def _load_config(self):
        """加载训练配置"""
        if not os.path.exists(self.args_yaml_path):
            return
        
        with open(self.args_yaml_path, 'r', encoding='utf-8') as f:
            args_data = yaml.safe_load(f)
        
        self.config = TrainingConfig(
            model_path=args_data.get('model', ''),
            epochs=args_data.get('epochs', 0),
            batch_size=args_data.get('batch', 0),
            image_size=args_data.get('imgsz', 640),
            device=args_data.get('device', ''),
            optimizer=args_data.get('optimizer', ''),
            learning_rate=args_data.get('lr0', 0.01),
            data_yaml=args_data.get('data', '')
        )
    
    def _load_metrics(self):
        """加载训练指标"""
        if not os.path.exists(self.results_csv_path):
            return
        
        # 读取results.csv
        self.results_df = pd.read_csv(self.results_csv_path)
        
        if len(self.results_df) == 0:
            return
        
        # 提取关键指标
        best_map50_idx = self.results_df['metrics/mAP50(B)'].idxmax()
        best_map50_95_idx = self.results_df['metrics/mAP50-95(B)'].idxmax()
        
        self.metrics = TrainingMetrics(
            best_map50=self.results_df.loc[best_map50_idx, 'metrics/mAP50(B)'],
            best_map50_95=self.results_df.loc[best_map50_95_idx, 'metrics/mAP50-95(B)'],
            final_train_loss=self.results_df['train/box_loss'].iloc[-1] + 
                           self.results_df['train/cls_loss'].iloc[-1],
            final_val_loss=self.results_df['val/box_loss'].iloc[-1] + 
                          self.results_df['val/cls_loss'].iloc[-1],
            total_epochs=len(self.results_df),
            training_time=self.results_df['time'].iloc[-1] if 'time' in self.results_df.columns else 0,
            precision=self.results_df['metrics/precision(B)'].iloc[-1],
            recall=self.results_df['metrics/recall(B)'].iloc[-1]
        )
        
        # 计算收敛轮次 (mAP50-95达到最大值80%的轮次)
        max_map = self.metrics.best_map50_95
        convergence_threshold = max_map * 0.8
        convergence_mask = self.results_df['metrics/mAP50-95(B)'] >= convergence_threshold
        if convergence_mask.any():
            self.metrics.convergence_epoch = convergence_mask.idxmax() + 1
    
    def _load_dataset_info(self):
        """加载数据集信息"""
        if not self.config or not self.config.data_yaml:
            return
        
        data_yaml_path = self.config.data_yaml
        if not os.path.isabs(data_yaml_path):
            # 尝试相对于当前目录的路径
            data_yaml_path = os.path.join(os.getcwd(), data_yaml_path)
        
        if not os.path.exists(data_yaml_path):
            return
        
        try:
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                data_config = yaml.safe_load(f)
            
            self.dataset_info = DatasetInfo(
                classes=data_config.get('names', {}),
                dataset_path=data_config.get('path', ''),
                train_path=data_config.get('train', ''),
                val_path=data_config.get('val', '')
            )
        except Exception as e:
            print(f"加载数据集信息失败: {e}")
    
    def get_available_charts(self) -> List[Tuple[str, str]]:
        """获取可用的图表文件"""
        charts = []
        chart_files = {
            "训练曲线": "results.png",
            "混淆矩阵": "confusion_matrix.png",  
            "F1曲线": "BoxF1_curve.png",
            "精确度曲线": "BoxP_curve.png",
            "召回率曲线": "BoxR_curve.png",
            "PR曲线": "BoxPR_curve.png",
            "标签分布": "labels.jpg"
        }
        
        for name, filename in chart_files.items():
            file_path = os.path.join(self.session_path, filename)
            if os.path.exists(file_path):
                charts.append((name, file_path))
        
        return charts
    
    def get_model_files(self) -> List[Tuple[str, str, float]]:
        """获取模型文件信息 (名称, 路径, 大小MB)"""
        model_files = []
        if not os.path.exists(self.weights_dir):
            return model_files
        
        for filename in os.listdir(self.weights_dir):
            if filename.endswith('.pt'):
                file_path = os.path.join(self.weights_dir, filename)
                try:
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    model_files.append((filename, file_path, size_mb))
                except:
                    continue
        
        return sorted(model_files, key=lambda x: x[0])


class TrainingSessionManager:
    """训练会话管理器"""
    
    def __init__(self, runs_dir: str = "runs/train"):
        self.runs_dir = runs_dir
        self.sessions: List[TrainingSession] = []
    
    def scan_sessions(self) -> List[TrainingSession]:
        """扫描所有训练会话"""
        self.sessions.clear()
        
        if not os.path.exists(self.runs_dir):
            print(f"训练目录不存在: {self.runs_dir}")
            return self.sessions
        
        # 扫描所有训练会话目录
        for item in os.listdir(self.runs_dir):
            session_path = os.path.join(self.runs_dir, item)
            
            if os.path.isdir(session_path) and item.startswith('yolo_training'):
                session = TrainingSession(session_path)
                if session.is_valid():
                    self.sessions.append(session)
        
        # 按创建时间排序（最新的在前）
        self.sessions.sort(key=lambda x: x.creation_date, reverse=True)
        
        print(f"发现 {len(self.sessions)} 个有效训练会话")
        return self.sessions
    
    def get_session_by_name(self, name: str) -> Optional[TrainingSession]:
        """根据名称获取会话"""
        for session in self.sessions:
            if session.session_name == name:
                return session
        return None
    
    def get_sessions_summary(self) -> List[Dict]:
        """获取所有会话的摘要信息"""
        summaries = []
        for session in self.sessions:
            # 确保数据已加载
            session.load_data()
            
            summary = {
                'name': session.session_name,
                'date': session.creation_date.strftime('%Y-%m-%d %H:%M'),
                'status': session.metrics.get_training_status() if session.metrics else "未知",
                'map50_95': f"{session.metrics.best_map50_95:.3f}" if session.metrics else "N/A",
                'epochs': session.metrics.total_epochs if session.metrics else 0,
                'quality_score': f"{session.metrics.get_quality_score():.1f}" if session.metrics else "0.0"
            }
            summaries.append(summary)
        
        return summaries


# 导出给外部使用
__all__ = ['TrainingSession', 'TrainingSessionManager', 'TrainingMetrics', 'DatasetInfo', 'TrainingConfig']


if __name__ == "__main__":
    # 简单测试
    manager = TrainingSessionManager()
    sessions = manager.scan_sessions()
    
    if sessions:
        print(f"\n找到 {len(sessions)} 个训练会话:")
        for session in sessions[:3]:  # 显示前3个
            session.load_data()
            print(f"- {session.session_name}")
            print(f"  日期: {session.creation_date.strftime('%Y-%m-%d %H:%M')}")
            if session.metrics:
                print(f"  mAP50-95: {session.metrics.best_map50_95:.3f}")
                print(f"  状态: {session.metrics.get_training_status()}")
    else:
        print("未找到训练会话")