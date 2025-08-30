#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目配置适配器
提供与现有系统的兼容性接口，确保平滑迁移
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from libs.project_manager import get_project_manager, get_current_project_config, save_current_project_config
from libs.logger_config import get_logger

logger = get_logger(__name__)

class ProjectConfigAdapter:
    """项目配置适配器，处理新旧配置系统的兼容性"""
    
    def __init__(self):
        self.project_manager = get_project_manager()
        self.legacy_configs_path = Path("configs")
    
    def get_class_config_path(self) -> str:
        """获取类别配置文件路径（兼容旧接口）"""
        current_project = self.project_manager.get_current_project()
        config_path = self.project_manager.get_project_config_path(current_project)
        return str(config_path / "class_config.yaml")
    
    def get_training_preferences_path(self) -> str:
        """获取训练偏好配置文件路径（兼容旧接口）"""
        current_project = self.project_manager.get_current_project()
        config_path = self.project_manager.get_project_config_path(current_project)
        return str(config_path / "training_preferences.json")
    
    def get_training_history_path(self) -> str:
        """获取训练历史文件路径（兼容旧接口）"""
        current_project = self.project_manager.get_current_project()
        config_path = self.project_manager.get_project_config_path(current_project)
        return str(config_path / "training_history.json")
    
    def load_classes(self) -> List[str]:
        """加载当前项目的类别列表"""
        try:
            config = get_current_project_config()
            if config:
                return config.classes
            return []
        except Exception as e:
            logger.error(f"加载类别列表失败: {e}")
            return []
    
    def save_classes(self, classes: List[str], class_metadata: Dict[str, Any] = None) -> bool:
        """保存当前项目的类别列表"""
        try:
            config = get_current_project_config()
            if config is None:
                logger.error("无法获取当前项目配置")
                return False
            
            config.classes = classes
            if class_metadata:
                config.class_metadata.update(class_metadata)
            
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"保存类别列表失败: {e}")
            return False
    
    def load_training_preferences(self) -> Dict[str, Any]:
        """加载训练偏好设置"""
        try:
            config = get_current_project_config()
            if config:
                return config.training_preferences
            return {}
        except Exception as e:
            logger.error(f"加载训练偏好失败: {e}")
            return {}
    
    def save_training_preferences(self, preferences: Dict[str, Any]) -> bool:
        """保存训练偏好设置"""
        try:
            config = get_current_project_config()
            if config is None:
                return False
            
            config.training_preferences.update(preferences)
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"保存训练偏好失败: {e}")
            return False
    
    def load_training_history(self) -> List[Dict[str, Any]]:
        """加载训练历史"""
        try:
            config = get_current_project_config()
            if config:
                return config.training_history
            return []
        except Exception as e:
            logger.error(f"加载训练历史失败: {e}")
            return []
    
    def save_training_history(self, history: List[Dict[str, Any]]) -> bool:
        """保存训练历史"""
        try:
            config = get_current_project_config()
            if config is None:
                return False
            
            config.training_history = history
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"保存训练历史失败: {e}")
            return False
    
    def add_training_record(self, record: Dict[str, Any]) -> bool:
        """添加训练记录"""
        try:
            config = get_current_project_config()
            if config is None:
                return False
            
            config.training_history.append(record)
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"添加训练记录失败: {e}")
            return False
    
    def load_ui_preferences(self) -> Dict[str, Any]:
        """加载UI偏好设置"""
        try:
            config = get_current_project_config()
            if config:
                return config.ui_preferences
            return {}
        except Exception as e:
            logger.error(f"加载UI偏好失败: {e}")
            return {}
    
    def save_ui_preferences(self, preferences: Dict[str, Any]) -> bool:
        """保存UI偏好设置"""
        try:
            config = get_current_project_config()
            if config is None:
                return False
            
            config.ui_preferences.update(preferences)
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"保存UI偏好失败: {e}")
            return False
    
    def load_shortcuts(self) -> Dict[str, str]:
        """加载快捷键设置"""
        try:
            config = get_current_project_config()
            if config:
                return config.shortcuts
            return {}
        except Exception as e:
            logger.error(f"加载快捷键设置失败: {e}")
            return {}
    
    def save_shortcuts(self, shortcuts: Dict[str, str]) -> bool:
        """保存快捷键设置"""
        try:
            config = get_current_project_config()
            if config is None:
                return False
            
            config.shortcuts.update(shortcuts)
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"保存快捷键设置失败: {e}")
            return False
    
    def load_ai_settings(self) -> Dict[str, Any]:
        """加载AI设置"""
        try:
            config = get_current_project_config()
            if config:
                return config.ai_settings
            return {}
        except Exception as e:
            logger.error(f"加载AI设置失败: {e}")
            return {}
    
    def save_ai_settings(self, settings: Dict[str, Any]) -> bool:
        """保存AI设置"""
        try:
            config = get_current_project_config()
            if config is None:
                return False
            
            config.ai_settings.update(settings)
            return save_current_project_config(config)
        except Exception as e:
            logger.error(f"保存AI设置失败: {e}")
            return False
    
    def migrate_legacy_configs(self) -> bool:
        """迁移旧配置到当前项目"""
        try:
            if not self.legacy_configs_path.exists():
                logger.info("未发现旧配置目录，跳过迁移")
                return True
            
            current_project = self.project_manager.get_current_project()
            logger.info(f"开始迁移旧配置到项目: {current_project}")
            
            # 检查是否已经迁移过
            project_config_path = self.project_manager.get_project_config_path(current_project)
            if (project_config_path / "class_config.yaml").exists():
                logger.info("项目配置已存在，跳过迁移")
                return True
            
            # 迁移类别配置
            old_class_config = self.legacy_configs_path / "class_config.yaml"
            if old_class_config.exists():
                import shutil
                shutil.copy2(old_class_config, project_config_path / "class_config.yaml")
                logger.info("已迁移类别配置")
            
            # 迁移训练配置
            old_training_prefs = self.legacy_configs_path / "training_preferences.json"
            if old_training_prefs.exists():
                import shutil
                shutil.copy2(old_training_prefs, project_config_path / "training_preferences.json")
                logger.info("已迁移训练偏好配置")
            
            # 迁移训练历史
            old_training_hist = self.legacy_configs_path / "training_history.json"
            if old_training_hist.exists():
                import shutil
                shutil.copy2(old_training_hist, project_config_path / "training_history.json")
                logger.info("已迁移训练历史")
            
            logger.info("旧配置迁移完成")
            return True
            
        except Exception as e:
            logger.error(f"迁移旧配置失败: {e}")
            return False
    
    def get_project_data_path(self) -> str:
        """获取当前项目数据路径"""
        current_project = self.project_manager.get_current_project()
        project_path = self.project_manager.get_project_path(current_project)
        data_path = project_path / "data"
        data_path.mkdir(exist_ok=True)
        return str(data_path)
    
    def get_project_models_path(self) -> str:
        """获取当前项目模型路径"""
        current_project = self.project_manager.get_current_project()
        project_path = self.project_manager.get_project_path(current_project)
        models_path = project_path / "models"
        models_path.mkdir(exist_ok=True)
        return str(models_path)
    
    def get_project_exports_path(self) -> str:
        """获取当前项目导出路径"""
        current_project = self.project_manager.get_current_project()
        project_path = self.project_manager.get_project_path(current_project)
        exports_path = project_path / "exports"
        exports_path.mkdir(exist_ok=True)
        return str(exports_path)
    
    def get_project_runs_path(self) -> str:
        """获取当前项目运行记录路径"""
        current_project = self.project_manager.get_current_project()
        project_path = self.project_manager.get_project_path(current_project)
        runs_path = project_path / "runs"
        runs_path.mkdir(exist_ok=True)
        return str(runs_path)


# 单例适配器
_config_adapter = None

def get_config_adapter() -> ProjectConfigAdapter:
    """获取配置适配器单例"""
    global _config_adapter
    if _config_adapter is None:
        _config_adapter = ProjectConfigAdapter()
        # 自动执行迁移
        _config_adapter.migrate_legacy_configs()
    return _config_adapter