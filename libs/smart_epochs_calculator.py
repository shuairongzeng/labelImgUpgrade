#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能训练轮数计算器

基于YOLO训练最佳实践，智能计算推荐的训练轮数
"""

import os
import math
import yaml
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DatasetInfo:
    """数据集信息"""
    train_images: int
    val_images: int
    total_images: int
    num_classes: int
    dataset_path: str
    config_path: str


@dataclass
class EpochsCalculationResult:
    """训练轮数计算结果"""
    recommended_epochs: int
    min_epochs: int
    max_epochs: int
    calculation_basis: List[str]
    confidence_level: str  # "高", "中", "低"
    additional_notes: List[str]


class SmartEpochsCalculator:
    """智能训练轮数计算器"""
    
    def __init__(self):
        # 基础参数配置
        self.base_epochs_per_1000_images = 100  # 每1000张图片的基础轮数
        self.min_epochs = 50   # 最小训练轮数
        self.max_epochs = 500  # 最大训练轮数
        
        # 模型复杂度系数
        self.model_complexity_factors = {
            'yolov8n': 0.8,   # nano模型，训练更快，需要更多轮数
            'yolov8s': 1.0,   # small模型，基准
            'yolov8m': 1.2,   # medium模型，更复杂，需要更少轮数
            'yolov8l': 1.4,   # large模型，最复杂
            'yolov8x': 1.6,   # extra large模型
        }
        
        # 数据集大小分类阈值
        self.dataset_size_thresholds = {
            'very_small': 100,    # 极小数据集
            'small': 800,         # 小数据集
            'medium': 3000,       # 中等数据集
            'large': 10000,       # 大数据集
        }
    
    def get_dataset_info_from_yaml(self, yaml_path: str) -> Optional[DatasetInfo]:
        """从YAML配置文件获取数据集信息"""
        try:
            if not os.path.exists(yaml_path):
                logger.error(f"配置文件不存在: {yaml_path}")
                return None
            
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 获取数据集基础路径
            dataset_base = Path(yaml_path).parent
            
            # 获取训练和验证路径
            train_path = dataset_base / config.get('train', 'images/train')
            val_path = dataset_base / config.get('val', 'images/val')
            
            # 统计图片数量
            train_images = self._count_images_in_directory(train_path)
            val_images = self._count_images_in_directory(val_path)
            total_images = train_images + val_images
            
            # 获取类别数量
            num_classes = config.get('nc', 0)
            
            return DatasetInfo(
                train_images=train_images,
                val_images=val_images,
                total_images=total_images,
                num_classes=num_classes,
                dataset_path=str(dataset_base),
                config_path=yaml_path
            )
            
        except Exception as e:
            logger.error(f"解析数据集配置失败: {str(e)}")
            return None
    
    def _count_images_in_directory(self, directory: Path) -> int:
        """统计目录中的图片数量"""
        try:
            if not directory.exists():
                return 0
            
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
            count = 0
            
            for ext in image_extensions:
                count += len(list(directory.glob(f"*{ext}")))
                count += len(list(directory.glob(f"*{ext.upper()}")))
            
            return count
            
        except Exception as e:
            logger.error(f"统计图片数量失败: {str(e)}")
            return 0
    
    def calculate_smart_epochs(self, 
                             dataset_info: DatasetInfo, 
                             model_type: str = 'yolov8n',
                             batch_size: int = 16) -> EpochsCalculationResult:
        """智能计算训练轮数"""
        try:
            calculation_basis = []
            additional_notes = []
            
            # 1. 基于数据集大小的基础计算
            base_epochs = self._calculate_base_epochs_by_dataset_size(
                dataset_info.total_images, calculation_basis)
            
            # 2. 模型复杂度调整
            model_factor = self.model_complexity_factors.get(model_type.lower(), 1.0)
            adjusted_epochs = int(base_epochs * model_factor)
            calculation_basis.append(f"模型复杂度调整 ({model_type}): {base_epochs} × {model_factor} = {adjusted_epochs}")
            
            # 3. 类别数量调整
            class_adjusted_epochs = self._adjust_for_class_count(
                adjusted_epochs, dataset_info.num_classes, calculation_basis)
            
            # 4. 数据集质量评估调整
            quality_adjusted_epochs = self._adjust_for_dataset_quality(
                class_adjusted_epochs, dataset_info, calculation_basis)
            
            # 5. 批次大小调整
            final_epochs = self._adjust_for_batch_size(
                quality_adjusted_epochs, batch_size, dataset_info.total_images, calculation_basis)
            
            # 6. 应用边界限制
            final_epochs = max(self.min_epochs, min(self.max_epochs, final_epochs))
            
            # 7. 计算推荐范围
            min_epochs = max(self.min_epochs, int(final_epochs * 0.7))
            max_epochs = min(self.max_epochs, int(final_epochs * 1.3))
            
            # 8. 评估置信度
            confidence_level = self._evaluate_confidence(dataset_info, additional_notes)
            
            # 9. 添加额外建议
            self._add_training_recommendations(dataset_info, model_type, additional_notes)
            
            return EpochsCalculationResult(
                recommended_epochs=final_epochs,
                min_epochs=min_epochs,
                max_epochs=max_epochs,
                calculation_basis=calculation_basis,
                confidence_level=confidence_level,
                additional_notes=additional_notes
            )
            
        except Exception as e:
            logger.error(f"计算智能轮数失败: {str(e)}")
            # 返回默认值
            return EpochsCalculationResult(
                recommended_epochs=100,
                min_epochs=50,
                max_epochs=200,
                calculation_basis=[f"计算失败，使用默认值: {str(e)}"],
                confidence_level="低",
                additional_notes=["建议手动调整参数"]
            )
    
    def _calculate_base_epochs_by_dataset_size(self, total_images: int, basis: List[str]) -> int:
        """基于数据集大小计算基础轮数 - 防止小数据集过拟合"""
        if total_images <= self.dataset_size_thresholds['very_small']:
            # 极小数据集：保守策略，防止过拟合
            base_epochs = 80  # 从200降到80，避免过拟合
            basis.append(f"极小数据集 ({total_images}张): 基础轮数 {base_epochs} (保守策略防过拟合)")
        elif total_images <= self.dataset_size_thresholds['small']:
            # 小数据集：适中轮数，仍需谨慎
            base_epochs = 100  # 从150降到100
            basis.append(f"小数据集 ({total_images}张): 基础轮数 {base_epochs} (谨慎策略)")
        elif total_images <= self.dataset_size_thresholds['medium']:
            # 中等数据集：标准轮数
            base_epochs = 120  # 从100提升到120，中等数据集可以稍多
            basis.append(f"中等数据集 ({total_images}张): 基础轮数 {base_epochs}")
        elif total_images <= self.dataset_size_thresholds['large']:
            # 大数据集：较少轮数
            base_epochs = 100  # 从80提升到100
            basis.append(f"大数据集 ({total_images}张): 基础轮数 {base_epochs}")
        else:
            # 超大数据集：最少轮数
            base_epochs = 80  # 从60提升到80
            basis.append(f"超大数据集 ({total_images}张): 基础轮数 {base_epochs}")

        return base_epochs
    
    def _adjust_for_class_count(self, base_epochs: int, num_classes: int, basis: List[str]) -> int:
        """基于类别数量调整轮数"""
        if num_classes <= 1:
            # 单类别或未知类别数
            adjusted = base_epochs
            basis.append(f"类别数调整: {num_classes}类，无调整")
        elif num_classes <= 5:
            # 少类别：稍微减少轮数
            adjusted = int(base_epochs * 0.9)
            basis.append(f"类别数调整: {num_classes}类，轮数 × 0.9 = {adjusted}")
        elif num_classes <= 20:
            # 中等类别数：标准
            adjusted = base_epochs
            basis.append(f"类别数调整: {num_classes}类，无调整")
        else:
            # 多类别：增加轮数
            adjusted = int(base_epochs * 1.2)
            basis.append(f"类别数调整: {num_classes}类，轮数 × 1.2 = {adjusted}")
        
        return adjusted
    
    def _adjust_for_dataset_quality(self, base_epochs: int, dataset_info: DatasetInfo, basis: List[str]) -> int:
        """基于数据集质量调整轮数"""
        # 计算训练/验证比例
        if dataset_info.total_images == 0:
            return base_epochs
        
        train_ratio = dataset_info.train_images / dataset_info.total_images
        
        if train_ratio < 0.6:
            # 训练数据太少，需要更多轮数
            adjusted = int(base_epochs * 1.3)
            basis.append(f"数据质量调整: 训练比例过低({train_ratio:.1%})，轮数 × 1.3 = {adjusted}")
        elif train_ratio > 0.9:
            # 验证数据太少，可能过拟合，减少轮数
            adjusted = int(base_epochs * 0.8)
            basis.append(f"数据质量调整: 验证比例过低({1-train_ratio:.1%})，轮数 × 0.8 = {adjusted}")
        else:
            # 比例合理
            adjusted = base_epochs
            basis.append(f"数据质量调整: 训练/验证比例合理({train_ratio:.1%})，无调整")
        
        return adjusted
    
    def _adjust_for_batch_size(self, base_epochs: int, batch_size: int, total_images: int, basis: List[str]) -> int:
        """基于批次大小调整轮数"""
        if total_images == 0:
            return base_epochs
        
        # 计算每个epoch的迭代次数
        iterations_per_epoch = max(1, total_images // batch_size)
        
        if iterations_per_epoch < 10:
            # 每个epoch迭代次数太少，需要更多轮数
            adjusted = int(base_epochs * 1.5)
            basis.append(f"批次大小调整: 每轮迭代过少({iterations_per_epoch}次)，轮数 × 1.5 = {adjusted}")
        elif iterations_per_epoch > 100:
            # 每个epoch迭代次数很多，可以减少轮数
            adjusted = int(base_epochs * 0.8)
            basis.append(f"批次大小调整: 每轮迭代较多({iterations_per_epoch}次)，轮数 × 0.8 = {adjusted}")
        else:
            # 迭代次数合理
            adjusted = base_epochs
            basis.append(f"批次大小调整: 每轮迭代合理({iterations_per_epoch}次)，无调整")
        
        return adjusted
    
    def _evaluate_confidence(self, dataset_info: DatasetInfo, notes: List[str]) -> str:
        """评估计算结果的置信度 - 对小数据集更保守"""
        confidence_score = 0

        # 数据集大小评分 - 对小数据集更严格
        if dataset_info.total_images >= 2000:
            confidence_score += 3
        elif dataset_info.total_images >= 800:
            confidence_score += 2
        elif dataset_info.total_images >= 200:
            confidence_score += 1
        else:
            confidence_score += 0  # 极小数据集不加分
            if dataset_info.total_images < 100:
                notes.append("🚨 数据集过小，推荐结果仅供参考，强烈建议人工调整")
            else:
                notes.append("⚠️ 数据集较小，建议增加更多训练数据并谨慎调整epochs")

        # 类别数量评分
        if 2 <= dataset_info.num_classes <= 50:
            confidence_score += 2
        else:
            confidence_score += 1
            if dataset_info.num_classes > 50:
                notes.append("类别数量较多，可能需要更长的训练时间")

        # 数据分布评分
        if dataset_info.train_images > 0 and dataset_info.val_images > 0:
            train_ratio = dataset_info.train_images / dataset_info.total_images
            if 0.7 <= train_ratio <= 0.8:
                confidence_score += 2
            else:
                confidence_score += 1
                notes.append("建议调整训练/验证数据比例至7:3或8:2")

        # 小数据集额外降低置信度
        if dataset_info.total_images < 500:
            confidence_score = max(0, confidence_score - 1)  # 小数据集降低1分

        # 返回置信度等级 - 提高标准
        if confidence_score >= 6:
            return "高"
        elif confidence_score >= 3:
            return "中"
        else:
            return "低"
    
    def _add_training_recommendations(self, dataset_info: DatasetInfo, model_type: str, notes: List[str]):
        """添加训练建议 - 重点关注过拟合预防"""
        # 数据集大小相关建议 - 强化过拟合预防
        if dataset_info.total_images < 100:
            notes.append("🚨 数据集过小，极易过拟合！强烈建议：")
            notes.append("   • 使用Early Stopping监控验证集loss")
            notes.append("   • 启用数据增强(旋转、缩放、翻转等)")
            notes.append("   • 考虑使用预训练模型微调")
            notes.append("   • 每10-20轮检查一次验证集性能")
        elif dataset_info.total_images < 500:
            notes.append("⚠️ 小数据集，注意过拟合风险：")
            notes.append("   • 建议使用Early Stopping")
            notes.append("   • 监控训练/验证loss差异")
            notes.append("   • 适当使用数据增强")

        # 模型选择建议 - 更严格的过拟合预防
        if dataset_info.total_images < 200 and model_type in ['yolov8m', 'yolov8l', 'yolov8x']:
            notes.append("🚨 数据集太小，模型过大！强烈建议使用yolov8n避免严重过拟合")
        elif dataset_info.total_images < 800 and model_type in ['yolov8l', 'yolov8x']:
            notes.append("⚠️ 数据集较小，建议使用更小的模型(yolov8n/s/m)避免过拟合")

        # Early Stopping建议
        if dataset_info.total_images < 1000:
            notes.append("💡 强烈建议设置Early Stopping：patience=10-20")

        # 验证数据建议
        if dataset_info.val_images < 50:
            notes.append("⚠️ 验证数据过少，可能无法准确评估模型性能和过拟合")

        # 类别平衡建议
        if dataset_info.num_classes > 20:
            notes.append("💡 多类别检测，建议监控各类别的训练效果")

        # 通用过拟合预防建议
        if dataset_info.total_images < 1000:
            notes.append("📊 过拟合预防检查清单：")
            notes.append("   ✓ 训练loss下降但验证loss上升时立即停止")
            notes.append("   ✓ 定期保存最佳验证性能的模型权重")
            notes.append("   ✓ 使用学习率调度器逐步降低学习率")
