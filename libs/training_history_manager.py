#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
训练历史记录管理器
用于跟踪哪些图片已经被用于训练，避免重复训练
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TrainingHistoryManager:
    """训练历史记录管理器"""

    def __init__(self, history_file: str = "configs/training_history.json"):
        """
        初始化训练历史记录管理器

        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = Path(history_file)
        self.history_data = self._load_history()

        # 确保配置目录存在
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_history(self) -> Dict:
        """加载训练历史记录"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(
                        f"加载训练历史记录: {len(data.get('training_sessions', []))} 个训练会话")
                    return data
            else:
                logger.debug("训练历史记录文件不存在，创建新的记录")
                return {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "training_sessions": []
                }
        except Exception as e:
            logger.error(f"加载训练历史记录失败: {str(e)}")
            return {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "training_sessions": []
            }

    def _save_history(self) -> bool:
        """保存训练历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"训练历史记录已保存到: {self.history_file}")
            return True
        except Exception as e:
            logger.error(f"保存训练历史记录失败: {str(e)}")
            return False

    def add_training_session(self,
                             session_name: str,
                             dataset_path: str,
                             image_files: List[str],
                             model_path: str = None,
                             training_config: Dict = None) -> str:
        """
        添加训练会话记录

        Args:
            session_name: 训练会话名称
            dataset_path: 数据集路径
            image_files: 参与训练的图片文件列表
            model_path: 训练生成的模型路径
            training_config: 训练配置信息

        Returns:
            str: 训练会话ID
        """
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 标准化图片路径（使用相对路径）
            normalized_images = []
            for img_path in image_files:
                try:
                    # 转换为相对路径，便于跨目录比较
                    rel_path = os.path.relpath(img_path)
                    normalized_images.append(rel_path)
                except ValueError:
                    # 如果无法转换为相对路径，使用原路径
                    normalized_images.append(img_path)

            session_data = {
                "session_id": session_id,
                "session_name": session_name,
                "timestamp": datetime.now().isoformat(),
                "dataset_path": dataset_path,
                "image_count": len(normalized_images),
                "image_files": normalized_images,
                "model_path": model_path,
                "training_config": training_config or {},
                "status": "completed"
            }

            self.history_data["training_sessions"].append(session_data)

            if self._save_history():
                logger.info(
                    f"训练会话记录已添加: {session_id} ({len(normalized_images)} 张图片)")
                return session_id
            else:
                logger.error("保存训练会话记录失败")
                return None

        except Exception as e:
            logger.error(f"添加训练会话记录失败: {str(e)}")
            return None

    def get_trained_images(self) -> Set[str]:
        """
        获取所有已训练过的图片路径集合

        Returns:
            Set[str]: 已训练图片路径集合
        """
        trained_images = set()

        try:
            for session in self.history_data.get("training_sessions", []):
                if session.get("status") == "completed":
                    for img_path in session.get("image_files", []):
                        trained_images.add(img_path)

            logger.debug(f"获取到 {len(trained_images)} 张已训练图片")
            return trained_images

        except Exception as e:
            logger.error(f"获取已训练图片列表失败: {str(e)}")
            return set()

    def is_image_trained(self, image_path: str, strict_mode: bool = False) -> bool:
        """
        检查指定图片是否已经被训练过

        Args:
            image_path: 图片路径
            strict_mode: 严格模式，只进行完全路径匹配，不进行文件名匹配

        Returns:
            bool: True表示已训练，False表示未训练
        """
        try:
            # 标准化路径
            normalized_path = os.path.relpath(image_path)
            trained_images = self.get_trained_images()

            # 检查完全匹配
            if normalized_path in trained_images:
                logger.debug(f"完全路径匹配: {normalized_path}")
                return True

            # 如果是严格模式，只进行完全匹配
            if strict_mode:
                return False

            # 检查文件名匹配（处理路径差异）
            image_name = os.path.basename(image_path)

            # 避免过于宽松的匹配：只有当文件名比较独特时才进行文件名匹配
            # 如果文件名太短或太常见，跳过文件名匹配
            if len(image_name) < 8 or image_name.lower() in ['image.jpg', 'photo.png', 'picture.jpg']:
                logger.debug(f"文件名太短或太常见，跳过文件名匹配: {image_name}")
                return False

            for trained_path in trained_images:
                if os.path.basename(trained_path) == image_name:
                    logger.debug(f"文件名匹配: {image_name} (训练路径: {trained_path})")
                    return True

            return False

        except Exception as e:
            logger.error(f"检查图片训练状态失败: {str(e)}")
            return False

    def filter_untrained_images(self, image_paths: List[str]) -> List[str]:
        """
        过滤出未训练过的图片

        Args:
            image_paths: 图片路径列表

        Returns:
            List[str]: 未训练过的图片路径列表
        """
        try:
            untrained_images = []
            trained_images = self.get_trained_images()

            for img_path in image_paths:
                if not self.is_image_trained(img_path):
                    untrained_images.append(img_path)

            logger.info(
                f"过滤结果: {len(image_paths)} -> {len(untrained_images)} 张未训练图片")
            return untrained_images

        except Exception as e:
            logger.error(f"过滤未训练图片失败: {str(e)}")
            return image_paths  # 出错时返回原列表

    def get_training_statistics(self) -> Dict:
        """
        获取训练统计信息

        Returns:
            Dict: 训练统计信息
        """
        try:
            sessions = self.history_data.get("training_sessions", [])
            total_sessions = len(sessions)
            total_images = len(self.get_trained_images())

            # 最近训练时间
            last_training = None
            if sessions:
                last_session = max(
                    sessions, key=lambda x: x.get("timestamp", ""))
                last_training = last_session.get("timestamp")

            return {
                "total_sessions": total_sessions,
                "total_trained_images": total_images,
                "last_training": last_training,
                "history_file": str(self.history_file)
            }

        except Exception as e:
            logger.error(f"获取训练统计信息失败: {str(e)}")
            return {
                "total_sessions": 0,
                "total_trained_images": 0,
                "last_training": None,
                "history_file": str(self.history_file)
            }

    def clear_history(self) -> bool:
        """
        清空训练历史记录

        Returns:
            bool: 清空是否成功
        """
        try:
            self.history_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "training_sessions": []
            }

            if self._save_history():
                logger.info("训练历史记录已清空")
                return True
            else:
                logger.error("清空训练历史记录失败")
                return False

        except Exception as e:
            logger.error(f"清空训练历史记录失败: {str(e)}")
            return False
