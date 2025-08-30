#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目管理核心类
管理项目的创建、删除、切换以及配置隔离
"""

import os
import json
import yaml
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from libs.logger_config import get_logger

logger = get_logger(__name__)

@dataclass
class ProjectMetadata:
    """项目元数据"""
    name: str
    display_name: str
    description: str
    created_at: str
    updated_at: str
    version: str = "1.0"
    author: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ProjectConfig:
    """项目配置"""
    # 类别配置
    classes: List[str]
    class_metadata: Dict[str, Any]
    
    # 训练配置
    training_preferences: Dict[str, Any]
    training_history: List[Dict[str, Any]]
    
    # UI设置
    ui_preferences: Dict[str, Any]
    
    # 快捷键设置
    shortcuts: Dict[str, str]
    
    # AI助手设置
    ai_settings: Dict[str, Any]
    
    def __post_init__(self):
        # 设置默认值
        if not self.classes:
            self.classes = []
        if not self.class_metadata:
            self.class_metadata = {}
        if not self.training_preferences:
            self.training_preferences = {
                "epochs": 100,
                "batch_size": 16,
                "img_size": 640,
                "model": "yolov8n.pt"
            }
        if not self.training_history:
            self.training_history = []
        if not self.ui_preferences:
            self.ui_preferences = {
                "theme": "material_light",
                "language": "zh_CN",
                "auto_save": True
            }
        if not self.shortcuts:
            self.shortcuts = {}
        if not self.ai_settings:
            self.ai_settings = {
                "enabled": True,
                "auto_predict": False,
                "confidence_threshold": 0.5
            }

class ProjectManager:
    """项目管理器"""
    
    def __init__(self, base_path: str = None):
        """初始化项目管理器
        
        Args:
            base_path: 项目基础路径，默认为当前目录下的projects文件夹
        """
        if base_path is None:
            base_path = os.path.join(os.getcwd(), "projects")
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # 项目索引文件
        self.index_file = self.base_path / "projects_index.json"
        
        # 共享资源目录
        self.shared_path = self.base_path / "shared"
        self.shared_path.mkdir(exist_ok=True)
        
        # 共享模型目录
        self.shared_models_path = self.shared_path / "models"
        self.shared_models_path.mkdir(exist_ok=True)
        
        # 当前项目
        self.current_project: Optional[str] = None
        
        # 加载项目索引
        self._load_index()
        
        # 确保default项目存在
        self._ensure_default_project()
    
    def _load_index(self) -> None:
        """加载项目索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except Exception as e:
                logger.error(f"加载项目索引失败: {e}")
                self.index = {"projects": {}, "current_project": "default"}
        else:
            self.index = {"projects": {}, "current_project": "default"}
    
    def _save_index(self) -> None:
        """保存项目索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存项目索引失败: {e}")
    
    def _ensure_default_project(self) -> None:
        """确保default项目存在"""
        if "default" not in self.index["projects"]:
            self.create_project(
                "default",
                display_name="默认项目",
                description="系统默认项目，包含基础配置"
            )
    
    def get_project_path(self, project_name: str) -> Path:
        """获取项目路径"""
        return self.base_path / project_name
    
    def get_project_config_path(self, project_name: str) -> Path:
        """获取项目配置路径"""
        return self.get_project_path(project_name) / "configs"
    
    def create_project(self, 
                      name: str, 
                      display_name: str = None,
                      description: str = "",
                      author: str = "",
                      tags: List[str] = None,
                      copy_from: str = None) -> bool:
        """创建新项目
        
        Args:
            name: 项目内部名称（英文，用作目录名）
            display_name: 项目显示名称
            description: 项目描述
            author: 作者
            tags: 标签列表
            copy_from: 从指定项目复制配置
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if name in self.index["projects"]:
                logger.warning(f"项目 '{name}' 已存在")
                return False
            
            if display_name is None:
                display_name = name
            
            # 创建项目目录结构
            project_path = self.get_project_path(name)
            project_path.mkdir(exist_ok=True)
            
            # 创建配置目录
            config_path = self.get_project_config_path(name)
            config_path.mkdir(exist_ok=True)
            
            # 创建其他必要目录
            (project_path / "data").mkdir(exist_ok=True)
            (project_path / "models").mkdir(exist_ok=True)
            (project_path / "exports").mkdir(exist_ok=True)
            (project_path / "runs").mkdir(exist_ok=True)
            
            # 创建项目元数据
            now = datetime.now().isoformat()
            metadata = ProjectMetadata(
                name=name,
                display_name=display_name,
                description=description,
                created_at=now,
                updated_at=now,
                author=author,
                tags=tags or []
            )
            
            # 保存项目元数据
            with open(project_path / "project.json", 'w', encoding='utf-8') as f:
                json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
            
            # 创建或复制配置
            if copy_from and copy_from in self.index["projects"]:
                self._copy_project_config(copy_from, name)
            else:
                self._create_default_config(name)
            
            # 更新索引
            self.index["projects"][name] = {
                "display_name": display_name,
                "description": description,
                "created_at": now,
                "updated_at": now,
                "path": str(project_path)
            }
            
            self._save_index()
            
            logger.info(f"项目 '{name}' 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建项目 '{name}' 失败: {e}")
            return False
    
    def delete_project(self, name: str, force: bool = False) -> bool:
        """删除项目
        
        Args:
            name: 项目名称
            force: 是否强制删除（包括default项目）
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if name == "default" and not force:
                logger.warning("不能删除default项目")
                return False
            
            if name not in self.index["projects"]:
                logger.warning(f"项目 '{name}' 不存在")
                return False
            
            # 如果是当前项目，切换到default
            if self.current_project == name:
                self.switch_project("default")
            
            # 删除项目目录
            project_path = self.get_project_path(name)
            if project_path.exists():
                shutil.rmtree(project_path)
            
            # 从索引中删除
            del self.index["projects"][name]
            self._save_index()
            
            logger.info(f"项目 '{name}' 删除成功")
            return True
            
        except Exception as e:
            logger.error(f"删除项目 '{name}' 失败: {e}")
            return False
    
    def switch_project(self, name: str) -> bool:
        """切换当前项目
        
        Args:
            name: 项目名称
            
        Returns:
            bool: 切换是否成功
        """
        try:
            if name not in self.index["projects"]:
                logger.warning(f"项目 '{name}' 不存在")
                return False
            
            self.current_project = name
            self.index["current_project"] = name
            self._save_index()
            
            logger.info(f"已切换到项目 '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"切换到项目 '{name}' 失败: {e}")
            return False
    
    def get_current_project(self) -> str:
        """获取当前项目名称"""
        if self.current_project is None:
            self.current_project = self.index.get("current_project", "default")
        return self.current_project
    
    def list_projects(self) -> Dict[str, Dict]:
        """列出所有项目"""
        return self.index["projects"].copy()
    
    def get_project_metadata(self, name: str) -> Optional[ProjectMetadata]:
        """获取项目元数据"""
        try:
            project_path = self.get_project_path(name)
            metadata_file = project_path / "project.json"
            
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ProjectMetadata(**data)
        except Exception as e:
            logger.error(f"获取项目 '{name}' 元数据失败: {e}")
            return None
    
    def update_project_metadata(self, name: str, **kwargs) -> bool:
        """更新项目元数据"""
        try:
            metadata = self.get_project_metadata(name)
            if metadata is None:
                return False
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            metadata.updated_at = datetime.now().isoformat()
            
            # 保存更新
            project_path = self.get_project_path(name)
            with open(project_path / "project.json", 'w', encoding='utf-8') as f:
                json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
            
            # 更新索引
            if name in self.index["projects"]:
                self.index["projects"][name]["display_name"] = metadata.display_name
                self.index["projects"][name]["description"] = metadata.description
                self.index["projects"][name]["updated_at"] = metadata.updated_at
            self._save_index()
            
            return True
        except Exception as e:
            logger.error(f"更新项目 '{name}' 元数据失败: {e}")
            return False
    
    def get_project_config(self, name: str) -> Optional[ProjectConfig]:
        """获取项目配置"""
        try:
            config_path = self.get_project_config_path(name)
            
            # 加载各种配置文件
            classes = []
            class_metadata = {}
            
            class_config_file = config_path / "class_config.yaml"
            if class_config_file.exists():
                with open(class_config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    classes = data.get('classes', [])
                    class_metadata = data.get('class_metadata', {})
            
            # 训练配置
            training_preferences = {}
            training_prefs_file = config_path / "training_preferences.json"
            if training_prefs_file.exists():
                with open(training_prefs_file, 'r', encoding='utf-8') as f:
                    training_preferences = json.load(f)
            
            # 训练历史
            training_history = []
            training_hist_file = config_path / "training_history.json"
            if training_hist_file.exists():
                with open(training_hist_file, 'r', encoding='utf-8') as f:
                    training_history = json.load(f).get('history', [])
            
            # UI设置
            ui_preferences = {}
            ui_prefs_file = config_path / "ui_preferences.json"
            if ui_prefs_file.exists():
                with open(ui_prefs_file, 'r', encoding='utf-8') as f:
                    ui_preferences = json.load(f)
            
            # 快捷键设置
            shortcuts = {}
            shortcuts_file = config_path / "shortcuts.json"
            if shortcuts_file.exists():
                with open(shortcuts_file, 'r', encoding='utf-8') as f:
                    shortcuts = json.load(f)
            
            # AI设置
            ai_settings = {}
            ai_settings_file = config_path / "ai_settings.json"
            if ai_settings_file.exists():
                with open(ai_settings_file, 'r', encoding='utf-8') as f:
                    ai_settings = json.load(f)
            
            return ProjectConfig(
                classes=classes,
                class_metadata=class_metadata,
                training_preferences=training_preferences,
                training_history=training_history,
                ui_preferences=ui_preferences,
                shortcuts=shortcuts,
                ai_settings=ai_settings
            )
            
        except Exception as e:
            logger.error(f"获取项目 '{name}' 配置失败: {e}")
            return None
    
    def save_project_config(self, name: str, config: ProjectConfig) -> bool:
        """保存项目配置"""
        try:
            config_path = self.get_project_config_path(name)
            config_path.mkdir(exist_ok=True)
            
            # 保存类别配置
            class_config = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'description': f'项目 {name} 的类别配置',
                'classes': config.classes,
                'class_metadata': config.class_metadata,
                'settings': {
                    'auto_sort': False,
                    'case_sensitive': True,
                    'allow_duplicates': False,
                    'validation_strict': True
                }
            }
            
            with open(config_path / "class_config.yaml", 'w', encoding='utf-8') as f:
                yaml.dump(class_config, f, allow_unicode=True, default_flow_style=False)
            
            # 保存训练配置
            with open(config_path / "training_preferences.json", 'w', encoding='utf-8') as f:
                json.dump(config.training_preferences, f, ensure_ascii=False, indent=2)
            
            # 保存训练历史
            with open(config_path / "training_history.json", 'w', encoding='utf-8') as f:
                json.dump({"history": config.training_history}, f, ensure_ascii=False, indent=2)
            
            # 保存UI设置
            with open(config_path / "ui_preferences.json", 'w', encoding='utf-8') as f:
                json.dump(config.ui_preferences, f, ensure_ascii=False, indent=2)
            
            # 保存快捷键设置
            with open(config_path / "shortcuts.json", 'w', encoding='utf-8') as f:
                json.dump(config.shortcuts, f, ensure_ascii=False, indent=2)
            
            # 保存AI设置
            with open(config_path / "ai_settings.json", 'w', encoding='utf-8') as f:
                json.dump(config.ai_settings, f, ensure_ascii=False, indent=2)
            
            # 更新项目元数据的更新时间
            self.update_project_metadata(name, updated_at=datetime.now().isoformat())
            
            logger.info(f"项目 '{name}' 配置保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存项目 '{name}' 配置失败: {e}")
            return False
    
    def _copy_project_config(self, source_name: str, target_name: str) -> None:
        """复制项目配置"""
        try:
            source_config = self.get_project_config(source_name)
            if source_config:
                self.save_project_config(target_name, source_config)
        except Exception as e:
            logger.error(f"复制项目配置失败: {e}")
            # 如果复制失败，创建默认配置
            self._create_default_config(target_name)
    
    def _create_default_config(self, name: str) -> None:
        """创建默认配置（新项目始终创建空白配置）"""
        try:
            logger.info(f"为项目 '{name}' 创建全新的空白默认配置...")
            
            # 始终创建全新的空白默认配置，确保项目隔离
            default_config = ProjectConfig(
                classes=[],  # 新项目没有任何预设类别
                class_metadata={},
                training_preferences={
                    "epochs": 100,
                    "batch_size": 16,
                    "img_size": 640,
                    "model": "yolov8n.pt"  # 使用共享的基础模型
                },
                training_history=[],
                ui_preferences={
                    "theme": "material_light",
                    "language": "zh_CN",
                    "auto_save": True
                },
                shortcuts={},
                ai_settings={
                    "enabled": True,
                    "auto_predict": False,
                    "confidence_threshold": 0.5
                }
            )
            
            self.save_project_config(name, default_config)
            logger.info(f"项目 '{name}' 的空白默认配置创建完成")
        except Exception as e:
            logger.error(f"创建默认配置失败: {e}")
    
    def _migrate_from_old_configs(self, name: str) -> None:
        """从旧的配置目录迁移配置"""
        try:
            old_configs_path = Path("configs")
            project_config_path = self.get_project_config_path(name)
            
            # 复制现有配置文件
            for config_file in old_configs_path.glob("*.yaml"):
                shutil.copy2(config_file, project_config_path)
            
            for config_file in old_configs_path.glob("*.json"):
                shutil.copy2(config_file, project_config_path)
            
            logger.info(f"已将现有配置迁移到项目 '{name}'")
            
        except Exception as e:
            logger.error(f"迁移配置失败: {e}")
    
    def get_shared_model_path(self, model_name: str) -> Path:
        """获取共享模型路径"""
        return self.shared_models_path / model_name
    
    def copy_model_to_shared(self, model_path: str, model_name: str = None) -> bool:
        """复制模型到共享目录"""
        try:
            source_path = Path(model_path)
            if not source_path.exists():
                logger.error(f"源模型文件不存在: {model_path}")
                return False
            
            if model_name is None:
                model_name = source_path.name
            
            target_path = self.get_shared_model_path(model_name)
            
            if target_path.exists():
                logger.info(f"共享模型 '{model_name}' 已存在，跳过复制")
                return True
            
            shutil.copy2(source_path, target_path)
            logger.info(f"模型 '{model_name}' 已复制到共享目录")
            return True
            
        except Exception as e:
            logger.error(f"复制模型到共享目录失败: {e}")
            return False
    
    def list_shared_models(self) -> List[str]:
        """列出共享模型"""
        try:
            return [f.name for f in self.shared_models_path.glob("*.pt")]
        except Exception as e:
            logger.error(f"列出共享模型失败: {e}")
            return []


# 单例模式的项目管理器实例
_project_manager = None

def get_project_manager() -> ProjectManager:
    """获取项目管理器单例"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager

def get_current_project_config() -> Optional[ProjectConfig]:
    """获取当前项目配置"""
    manager = get_project_manager()
    current_project = manager.get_current_project()
    return manager.get_project_config(current_project)

def save_current_project_config(config: ProjectConfig) -> bool:
    """保存当前项目配置"""
    manager = get_project_manager()
    current_project = manager.get_current_project()
    return manager.save_project_config(current_project, config)