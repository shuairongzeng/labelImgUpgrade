#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
训练配置管理器

用于保存和加载用户的训练参数偏好设置
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class TrainingConfigManager:
    """训练配置管理器"""
    
    def __init__(self, config_dir: str = "configs"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件存储目录
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "training_preferences.json"
        self.ensure_config_dir()
        
        # 默认配置
        self.default_config = {
            "epochs": 100,
            "batch_size": 16,
            "learning_rate": 0.01,
            "model_type": "yolov8n",
            "device": "auto",
            "user_adjustments": {},  # 用户手动调整的记录
            "smart_calc_history": []  # 智能计算历史
        }
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"创建配置目录失败: {str(e)}")
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 合并默认配置和用户配置
            merged_config = self.default_config.copy()
            merged_config.update(config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(merged_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"训练配置已保存到: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存训练配置失败: {str(e)}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        try:
            if not self.config_file.exists():
                logger.info("配置文件不存在，使用默认配置")
                return self.default_config.copy()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 合并默认配置，确保所有必要的键都存在
            merged_config = self.default_config.copy()
            merged_config.update(config)
            
            logger.info(f"训练配置已从文件加载: {self.config_file}")
            return merged_config
            
        except Exception as e:
            logger.error(f"加载训练配置失败: {str(e)}")
            return self.default_config.copy()
    
    def save_user_adjustment(self, dataset_path: str, original_epochs: int, 
                           adjusted_epochs: int, reason: str = ""):
        """
        保存用户手动调整记录
        
        Args:
            dataset_path: 数据集路径
            original_epochs: 原始推荐轮数
            adjusted_epochs: 用户调整后的轮数
            reason: 调整原因
        """
        try:
            config = self.load_config()
            
            # 创建调整记录
            adjustment_record = {
                "dataset_path": dataset_path,
                "original_epochs": original_epochs,
                "adjusted_epochs": adjusted_epochs,
                "reason": reason,
                "timestamp": self._get_timestamp()
            }
            
            # 添加到用户调整历史
            if "user_adjustments" not in config:
                config["user_adjustments"] = {}
            
            dataset_key = os.path.basename(dataset_path)
            if dataset_key not in config["user_adjustments"]:
                config["user_adjustments"][dataset_key] = []
            
            config["user_adjustments"][dataset_key].append(adjustment_record)
            
            # 保持最近10条记录
            config["user_adjustments"][dataset_key] = \
                config["user_adjustments"][dataset_key][-10:]
            
            self.save_config(config)
            
        except Exception as e:
            logger.error(f"保存用户调整记录失败: {str(e)}")
    
    def save_smart_calc_result(self, dataset_path: str, dataset_info: Dict[str, Any], 
                             calculation_result: Dict[str, Any]):
        """
        保存智能计算结果
        
        Args:
            dataset_path: 数据集路径
            dataset_info: 数据集信息
            calculation_result: 计算结果
        """
        try:
            config = self.load_config()
            
            # 创建计算记录
            calc_record = {
                "dataset_path": dataset_path,
                "dataset_info": {
                    "total_images": dataset_info.get("total_images", 0),
                    "train_images": dataset_info.get("train_images", 0),
                    "val_images": dataset_info.get("val_images", 0),
                    "num_classes": dataset_info.get("num_classes", 0)
                },
                "recommended_epochs": calculation_result.get("recommended_epochs", 100),
                "confidence_level": calculation_result.get("confidence_level", "中"),
                "timestamp": self._get_timestamp()
            }
            
            # 添加到智能计算历史
            if "smart_calc_history" not in config:
                config["smart_calc_history"] = []
            
            config["smart_calc_history"].append(calc_record)
            
            # 保持最近20条记录
            config["smart_calc_history"] = config["smart_calc_history"][-20:]
            
            self.save_config(config)
            
        except Exception as e:
            logger.error(f"保存智能计算结果失败: {str(e)}")
    
    def get_user_preference_for_dataset(self, dataset_path: str) -> Optional[Dict[str, Any]]:
        """
        获取用户对特定数据集的偏好设置
        
        Args:
            dataset_path: 数据集路径
            
        Returns:
            Optional[Dict[str, Any]]: 用户偏好设置，如果没有则返回None
        """
        try:
            config = self.load_config()
            dataset_key = os.path.basename(dataset_path)
            
            # 查找用户调整记录
            user_adjustments = config.get("user_adjustments", {})
            if dataset_key in user_adjustments and user_adjustments[dataset_key]:
                # 返回最近的调整记录
                latest_adjustment = user_adjustments[dataset_key][-1]
                return {
                    "preferred_epochs": latest_adjustment["adjusted_epochs"],
                    "last_adjustment_reason": latest_adjustment.get("reason", ""),
                    "last_adjustment_time": latest_adjustment.get("timestamp", "")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取用户偏好设置失败: {str(e)}")
            return None
    
    def get_similar_dataset_recommendations(self, current_dataset_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于历史记录获取相似数据集的推荐
        
        Args:
            current_dataset_info: 当前数据集信息
            
        Returns:
            List[Dict[str, Any]]: 相似数据集的推荐列表
        """
        try:
            config = self.load_config()
            smart_calc_history = config.get("smart_calc_history", [])
            
            current_size = current_dataset_info.get("total_images", 0)
            current_classes = current_dataset_info.get("num_classes", 0)
            
            similar_datasets = []
            
            for record in smart_calc_history:
                dataset_info = record.get("dataset_info", {})
                record_size = dataset_info.get("total_images", 0)
                record_classes = dataset_info.get("num_classes", 0)
                
                # 计算相似度（基于图片数量和类别数量）
                size_similarity = self._calculate_similarity(current_size, record_size)
                class_similarity = self._calculate_similarity(current_classes, record_classes)
                
                # 综合相似度
                overall_similarity = (size_similarity + class_similarity) / 2
                
                if overall_similarity > 0.7:  # 相似度阈值
                    similar_datasets.append({
                        "dataset_path": record.get("dataset_path", ""),
                        "recommended_epochs": record.get("recommended_epochs", 100),
                        "confidence_level": record.get("confidence_level", "中"),
                        "similarity": overall_similarity,
                        "dataset_info": dataset_info
                    })
            
            # 按相似度排序
            similar_datasets.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similar_datasets[:5]  # 返回最相似的5个
            
        except Exception as e:
            logger.error(f"获取相似数据集推荐失败: {str(e)}")
            return []
    
    def _calculate_similarity(self, value1: float, value2: float) -> float:
        """
        计算两个数值的相似度
        
        Args:
            value1: 数值1
            value2: 数值2
            
        Returns:
            float: 相似度 (0-1)
        """
        if value1 == 0 and value2 == 0:
            return 1.0
        
        if value1 == 0 or value2 == 0:
            return 0.0
        
        # 使用相对差异计算相似度
        diff_ratio = abs(value1 - value2) / max(value1, value2)
        similarity = max(0, 1 - diff_ratio)
        
        return similarity
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到指定路径
        
        Args:
            export_path: 导出路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            config = self.load_config()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已导出到: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {str(e)}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从指定路径导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            bool: 导入是否成功
        """
        try:
            if not os.path.exists(import_path):
                logger.error(f"导入文件不存在: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证配置格式
            if not isinstance(imported_config, dict):
                logger.error("导入的配置格式无效")
                return False
            
            # 保存导入的配置
            return self.save_config(imported_config)
            
        except Exception as e:
            logger.error(f"导入配置失败: {str(e)}")
            return False
