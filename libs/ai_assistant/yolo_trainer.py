#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YOLO训练器模块

提供YOLO模型训练功能，包括数据加载、模型训练、进度监控等
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass

try:
    from PyQt5.QtCore import QObject, pyqtSignal, QThread
except ImportError:
    from PyQt4.QtCore import QObject, pyqtSignal, QThread

# 导入YOLO相关库
try:
    from ultralytics import YOLO
    import torch
    import yaml
    YOLO_AVAILABLE = True
except ImportError as e:
    YOLO_AVAILABLE = False
    IMPORT_ERROR = str(e)

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """训练配置数据类"""
    dataset_config: str          # 数据集配置文件路径
    epochs: int                  # 训练轮数
    batch_size: int             # 批次大小
    learning_rate: float        # 学习率
    model_type: str             # 模型类型 (pretrained, custom, manual)
    model_path: str             # 模型路径
    model_name: str             # 模型名称
    device: str                 # 训练设备 (cpu, cuda)
    output_dir: str             # 输出目录
    resume: bool = False        # 是否恢复训练
    save_period: int = 10       # 保存周期


@dataclass
class TrainingMetrics:
    """训练指标数据类"""
    epoch: int
    total_epochs: int
    train_loss: float
    val_loss: float
    precision: float
    recall: float
    map50: float
    map50_95: float
    lr: float
    time_elapsed: float


class YOLOTrainer(QObject):
    """YOLO模型训练器"""

    # 信号定义
    training_started = pyqtSignal()                    # 训练开始
    training_progress = pyqtSignal(object)             # 训练进度 (TrainingMetrics)
    training_completed = pyqtSignal(str)               # 训练完成 (模型路径)
    training_error = pyqtSignal(str)                   # 训练错误
    training_stopped = pyqtSignal()                    # 训练停止
    log_message = pyqtSignal(str)                      # 日志消息

    def __init__(self):
        """初始化YOLO训练器"""
        super().__init__()

        # 检查YOLO库是否可用
        if not YOLO_AVAILABLE:
            logger.error(f"YOLO库不可用: {IMPORT_ERROR}")
            self.training_error.emit(f"YOLO库不可用: {IMPORT_ERROR}")
            return

        # 初始化属性
        self.model = None
        self.config = None
        self.is_training = False
        self.should_stop = False
        self.training_thread = None
        self.start_time = None

        # 训练回调函数
        self.progress_callback = None

    def validate_config(self, config: TrainingConfig) -> bool:
        """
        验证训练配置

        Args:
            config: 训练配置

        Returns:
            bool: 配置是否有效
        """
        try:
            self.log_message.emit("🔍 开始验证训练配置...")

            # 检查数据集配置文件
            self.log_message.emit(f"📁 检查数据集配置文件: {config.dataset_config}")
            if not os.path.exists(config.dataset_config):
                error_msg = f"数据集配置文件不存在: {config.dataset_config}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return False

            self.log_message.emit("✅ 数据集配置文件存在")

            # 验证YAML格式
            self.log_message.emit("📋 解析YAML配置文件...")
            with open(config.dataset_config, 'r', encoding='utf-8') as f:
                dataset_info = yaml.safe_load(f)

            self.log_message.emit(f"📄 YAML内容: {dataset_info}")

            # 检查必要字段
            required_fields = ['train', 'val', 'names']
            self.log_message.emit(f"🔍 检查必要字段: {required_fields}")
            for field in required_fields:
                if field not in dataset_info:
                    error_msg = f"数据集配置缺少必要字段: {field}"
                    self.log_message.emit(f"❌ {error_msg}")
                    self.training_error.emit(error_msg)
                    return False

            self.log_message.emit("✅ 所有必要字段都存在")

            # 检查数据路径
            dataset_config_path = Path(config.dataset_config)
            dataset_dir = dataset_config_path.parent
            self.log_message.emit(f"📂 数据集配置文件目录: {dataset_dir.absolute()}")

            # 处理path字段（如果存在）
            if 'path' in dataset_info and dataset_info['path']:
                dataset_base_path = dataset_info['path']
                self.log_message.emit(f"🗂️ 数据集path字段: {dataset_base_path}")

                # 如果path是相对路径，相对于配置文件目录解析
                if not os.path.isabs(dataset_base_path):
                    if dataset_base_path == '.':
                        # 如果是当前目录，直接使用配置文件目录
                        dataset_base_path = dataset_dir
                        self.log_message.emit("🔗 使用配置文件目录作为基础路径")
                    elif dataset_base_path.startswith('datasets/'):
                        # 如果是相对于项目根目录的datasets路径，检查是否存在重复拼接
                        # 检查dataset_dir是否已经包含了dataset_base_path
                        dataset_dir_normalized = os.path.normpath(
                            str(dataset_dir))
                        base_path_normalized = os.path.normpath(
                            dataset_base_path)

                        if dataset_dir_normalized.endswith(base_path_normalized.replace('/', os.sep)):
                            # 如果配置文件目录已经包含了path路径，直接使用配置文件目录
                            dataset_base_path = dataset_dir
                            self.log_message.emit(
                                f"🔧 检测到路径重复，使用配置文件目录: {dataset_dir}")
                        else:
                            # 否则相对于项目根目录解析
                            project_root = Path.cwd()
                            dataset_base_path = project_root / dataset_base_path
                            self.log_message.emit(
                                f"🔗 相对于项目根目录解析: {dataset_base_path.absolute()}")
                    else:
                        # 其他相对路径正常拼接
                        dataset_base_path = dataset_dir / dataset_base_path
                        self.log_message.emit(
                            f"🔗 相对于配置文件目录解析: {dataset_base_path.absolute()}")

                dataset_base_path = Path(dataset_base_path)
            else:
                # 如果没有path字段，使用配置文件所在目录
                dataset_base_path = dataset_dir
                self.log_message.emit("📁 使用配置文件目录作为基础路径")

            # 构建训练和验证数据路径
            train_relative = dataset_info['train']
            val_relative = dataset_info['val']

            self.log_message.emit(f"🚂 训练数据相对路径: {train_relative}")
            self.log_message.emit(f"✅ 验证数据相对路径: {val_relative}")

            train_path = dataset_base_path / train_relative
            val_path = dataset_base_path / val_relative

            self.log_message.emit(f"🚂 训练数据绝对路径: {train_path.absolute()}")
            self.log_message.emit(f"✅ 验证数据绝对路径: {val_path.absolute()}")

            # 检查路径是否存在
            if not train_path.exists():
                error_msg = f"训练数据路径不存在: {train_path.absolute()}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return False

            if not val_path.exists():
                error_msg = f"验证数据路径不存在: {val_path.absolute()}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return False

            self.log_message.emit("✅ 训练和验证数据路径都存在")

            # 检查数据文件数量
            train_images = list(train_path.glob(
                "*.jpg")) + list(train_path.glob("*.png")) + list(train_path.glob("*.jpeg"))
            val_images = list(val_path.glob(
                "*.jpg")) + list(val_path.glob("*.png")) + list(val_path.glob("*.jpeg"))

            self.log_message.emit(f"📊 训练图片数量: {len(train_images)}")
            self.log_message.emit(f"📊 验证图片数量: {len(val_images)}")

            if len(train_images) == 0:
                error_msg = f"训练目录中没有找到图片文件: {train_path.absolute()}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return False

            if len(val_images) == 0:
                error_msg = f"验证目录中没有找到图片文件: {val_path.absolute()}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return False

            # 标准化设备字符串
            device_str = str(config.device).lower()
            if "gpu" in device_str or "cuda" in device_str:
                config.device = 'cuda'
            else:
                config.device = 'cpu'

            # 检查设备可用性和兼容性
            if config.device == 'cuda':
                if not torch.cuda.is_available():
                    self.log_message.emit("⚠️ CUDA不可用，自动切换到CPU训练")
                    config.device = 'cpu'
                else:
                    # 检查torchvision CUDA兼容性
                    try:
                        import torchvision
                        # 测试CUDA NMS操作
                        test_boxes = torch.tensor(
                            [[0, 0, 1, 1]], dtype=torch.float32).cuda()
                        test_scores = torch.tensor(
                            [0.9], dtype=torch.float32).cuda()
                        _ = torchvision.ops.nms(test_boxes, test_scores, 0.5)
                        self.log_message.emit("✅ CUDA兼容性检查通过")
                    except Exception as e:
                        self.log_message.emit(
                            f"⚠️ CUDA torchvision兼容性问题，切换到CPU训练: {str(e)}")
                        config.device = 'cpu'

            # 创建输出目录
            os.makedirs(config.output_dir, exist_ok=True)

            logger.info("训练配置验证通过")
            return True

        except Exception as e:
            error_msg = f"配置验证失败: {str(e)}"
            logger.error(error_msg)
            self.training_error.emit(error_msg)
            return False

    def start_training(self, config: TrainingConfig):
        """
        开始训练

        Args:
            config: 训练配置
        """
        if self.is_training:
            self.training_error.emit("训练已在进行中")
            return

        # 验证配置
        if not self.validate_config(config):
            return

        self.config = config
        self.is_training = True
        self.should_stop = False

        # 在新线程中执行训练
        self.training_thread = threading.Thread(target=self._train_worker)
        self.training_thread.daemon = True
        self.training_thread.start()

    def stop_training(self):
        """停止训练"""
        if self.is_training:
            self.should_stop = True
            self.log_message.emit("🛑 正在停止训练...")

    def _train_worker(self):
        """训练工作线程"""
        try:
            self.training_started.emit()
            self.start_time = time.time()

            self.log_message.emit("🚀 开始YOLO模型训练...")
            self.log_message.emit(f"📁 数据集配置: {self.config.dataset_config}")
            self.log_message.emit(
                f"⚙️ 训练参数: {self.config.epochs}轮, 批次{self.config.batch_size}, 学习率{self.config.learning_rate}")
            self.log_message.emit(f"🖥️ 训练设备: {self.config.device.upper()}")
            self.log_message.emit(f"📂 输出目录: {self.config.output_dir}")

            # 再次验证数据集配置（训练前最后检查）
            self.log_message.emit("🔍 训练前最后验证数据集配置...")

            # 读取并显示数据集配置
            with open(self.config.dataset_config, 'r', encoding='utf-8') as f:
                dataset_info = yaml.safe_load(f)

            self.log_message.emit(f"📋 最终使用的数据集配置:")
            for key, value in dataset_info.items():
                self.log_message.emit(f"   {key}: {value}")

            # 初始化模型
            self.log_message.emit(f"🤖 模型配置信息:")
            self.log_message.emit(f"   模型类型: {self.config.model_type}")
            self.log_message.emit(f"   模型名称: {self.config.model_name}")
            self.log_message.emit(f"   模型路径: {self.config.model_path}")

            # 根据模型类型加载模型
            if self.config.model_type == 'pretrained':
                # 预训练模型，直接使用模型名称
                model_path = self.config.model_path
                self.log_message.emit(f"📦 加载预训练模型: {model_path}")
            elif self.config.model_type in ['custom', 'manual']:
                # 自定义或手动指定模型，使用完整路径
                model_path = self.config.model_path
                if not os.path.exists(model_path):
                    error_msg = f"模型文件不存在: {model_path}"
                    self.log_message.emit(f"❌ {error_msg}")
                    self.training_error.emit(error_msg)
                    return
                self.log_message.emit(f"📄 加载自定义模型: {model_path}")
            else:
                error_msg = f"未知的模型类型: {self.config.model_type}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return

            # 验证模型文件
            try:
                if self.config.model_type != 'pretrained' and not os.path.exists(model_path):
                    raise FileNotFoundError(f"模型文件不存在: {model_path}")

                # 获取模型文件大小
                if os.path.exists(model_path):
                    file_size = os.path.getsize(
                        model_path) / (1024 * 1024)  # MB
                    self.log_message.emit(f"📊 模型文件大小: {file_size:.2f} MB")

                self.model = YOLO(model_path)
                self.log_message.emit(f"✅ 模型加载成功")

            except Exception as e:
                error_msg = f"模型加载失败: {str(e)}"
                self.log_message.emit(f"❌ {error_msg}")
                self.training_error.emit(error_msg)
                return

            # 设置训练回调
            self.model.add_callback('on_train_epoch_end', self._on_epoch_end)

            # 开始训练
            results = self.model.train(
                data=self.config.dataset_config,
                epochs=self.config.epochs,
                batch=self.config.batch_size,
                lr0=self.config.learning_rate,
                device=self.config.device,
                project=self.config.output_dir,
                name='yolo_training',
                save_period=self.config.save_period,
                resume=self.config.resume,
                verbose=True
            )

            if not self.should_stop:
                # 训练完成
                model_path = str(results.save_dir / 'weights' / 'best.pt')
                self.log_message.emit(f"✅ 训练完成！模型已保存到: {model_path}")
                self.training_completed.emit(model_path)
            else:
                self.log_message.emit("🛑 训练已停止")
                self.training_stopped.emit()

        except Exception as e:
            error_msg = f"训练失败: {str(e)}"
            logger.error(error_msg)
            self.training_error.emit(error_msg)
        finally:
            self.is_training = False

    def _on_epoch_end(self, trainer):
        """训练轮次结束回调"""
        try:
            if self.should_stop:
                trainer.stop = True
                return

            # 获取训练指标
            epoch = trainer.epoch + 1
            total_epochs = trainer.epochs

            # 从训练器获取指标
            metrics = trainer.metrics
            if metrics:
                train_loss = getattr(metrics, 'box_loss', 0.0)
                val_loss = getattr(metrics, 'val_box_loss', 0.0)
                precision = getattr(metrics, 'precision', 0.0)
                recall = getattr(metrics, 'recall', 0.0)
                map50 = getattr(metrics, 'map50', 0.0)
                map50_95 = getattr(metrics, 'map50_95', 0.0)
                lr = getattr(trainer.optimizer, 'param_groups', [{}])[
                    0].get('lr', 0.0)
            else:
                train_loss = val_loss = precision = recall = map50 = map50_95 = lr = 0.0

            time_elapsed = time.time() - self.start_time

            # 创建训练指标对象
            training_metrics = TrainingMetrics(
                epoch=epoch,
                total_epochs=total_epochs,
                train_loss=train_loss,
                val_loss=val_loss,
                precision=precision,
                recall=recall,
                map50=map50,
                map50_95=map50_95,
                lr=lr,
                time_elapsed=time_elapsed
            )

            # 发送进度信号
            self.training_progress.emit(training_metrics)

            # 发送日志消息
            progress_percent = (epoch / total_epochs) * 100
            self.log_message.emit(
                f"📊 Epoch {epoch}/{total_epochs} ({progress_percent:.1f}%) - "
                f"Loss: {train_loss:.4f}, mAP50: {map50:.4f}"
            )

        except Exception as e:
            logger.error(f"回调函数错误: {str(e)}")
