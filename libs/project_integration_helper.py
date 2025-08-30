#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目集成辅助工具
提供与现有labelImg系统的集成方法和工具函数
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List

from libs.project_manager import get_project_manager
from libs.project_config_adapter import get_config_adapter
from libs.logger_config import get_logger

logger = get_logger(__name__)

class ProjectIntegrationHelper:
    """项目集成辅助类"""
    
    def __init__(self):
        self.project_manager = get_project_manager()
        self.config_adapter = get_config_adapter()
    
    def initialize_project_system(self) -> bool:
        """初始化项目系统"""
        try:
            logger.info("正在初始化项目管理系统...")
            
            # 检查是否首次运行项目系统
            if self.is_first_run():
                logger.info("检测到首次运行，开始配置迁移...")
                success = self.migrate_legacy_system()
                if success:
                    logger.info("系统迁移完成")
                else:
                    logger.warning("系统迁移部分失败，但不影响正常使用")
            
            # 确保默认项目存在并配置正确
            self.ensure_default_project()
            
            # 确保共享模型存在
            self.ensure_shared_models()
            
            # 验证当前项目配置
            current_project = self.project_manager.get_current_project()
            if not self.validate_project_config(current_project):
                logger.warning(f"项目 '{current_project}' 配置异常，尝试修复...")
                self.repair_project_config(current_project)
            
            logger.info("项目管理系统初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化项目系统失败: {e}")
            return False
    
    def is_first_run(self) -> bool:
        """检查是否首次运行项目系统"""
        # 检查是否存在旧的configs目录但没有projects目录
        legacy_configs = Path("configs")
        projects_dir = Path("projects")
        
        return (legacy_configs.exists() and 
                not projects_dir.exists() and
                not (projects_dir / "projects_index.json").exists())
    
    def migrate_legacy_system(self) -> bool:
        """迁移旧版系统"""
        try:
            # 自动执行配置迁移
            success = self.config_adapter.migrate_legacy_configs()
            if not success:
                return False
            
            # 迁移其他相关文件和目录
            self.migrate_data_files()
            self.migrate_model_files()
            
            # 创建迁移完成标记
            migration_marker = Path("projects") / ".migration_completed"
            migration_marker.touch()
            
            return True
            
        except Exception as e:
            logger.error(f"系统迁移失败: {e}")
            return False
    
    def migrate_data_files(self) -> None:
        """迁移数据文件"""
        try:
            # 常见的数据目录
            data_dirs = ["data", "images", "annotations", "datasets"]
            default_project_data = Path("projects/default/data")
            
            for dir_name in data_dirs:
                old_dir = Path(dir_name)
                if old_dir.exists() and old_dir.is_dir():
                    target_dir = default_project_data / dir_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 移动文件而不是整个目录
                    for item in old_dir.iterdir():
                        if item.is_file():
                            target_file = target_dir / item.name
                            if not target_file.exists():
                                shutil.move(str(item), str(target_file))
                    
                    logger.info(f"已迁移数据目录: {dir_name}")
            
        except Exception as e:
            logger.warning(f"数据文件迁移失败: {e}")
    
    def migrate_model_files(self) -> None:
        """迁移模型文件"""
        try:
            # 查找根目录下的模型文件
            model_extensions = [".pt", ".onnx", ".engine"]
            shared_models_path = Path("projects/shared/models")
            shared_models_path.mkdir(parents=True, exist_ok=True)
            
            for ext in model_extensions:
                for model_file in Path(".").glob(f"*{ext}"):
                    if model_file.is_file():
                        target_file = shared_models_path / model_file.name
                        if not target_file.exists():
                            shutil.copy2(model_file, target_file)
                            logger.info(f"已复制模型文件到共享目录: {model_file.name}")
            
        except Exception as e:
            logger.warning(f"模型文件迁移失败: {e}")
    
    def ensure_default_project(self) -> None:
        """确保默认项目存在且配置正确"""
        try:
            projects = self.project_manager.list_projects()
            if "default" not in projects:
                logger.info("创建默认项目...")
                self.project_manager.create_project(
                    "default",
                    display_name="默认项目",
                    description="系统默认项目，包含基础配置"
                )
            
            # 确保默认项目是当前项目
            current = self.project_manager.get_current_project()
            if current not in projects and current != "default":
                logger.info("切换到默认项目...")
                self.project_manager.switch_project("default")
            
        except Exception as e:
            logger.error(f"确保默认项目失败: {e}")
    
    def ensure_shared_models(self) -> None:
        """确保共享模型存在"""
        try:
            from pathlib import Path
            import shutil
            
            # 创建共享模型目录
            shared_models_dir = Path("projects/shared/models")
            shared_models_dir.mkdir(parents=True, exist_ok=True)
            
            # 检查是否需要复制基础模型
            base_models = ["yolov8n.pt"]  # 基础共享模型列表
            
            for model_name in base_models:
                shared_model_path = shared_models_dir / model_name
                
                # 如果共享目录中没有这个模型，尝试从各个位置复制
                if not shared_model_path.exists():
                    source_paths = [
                        Path(model_name),  # 根目录
                        Path(f"models/{model_name}"),  # models目录
                        Path(f"models/custom/{model_name}"),  # custom目录
                    ]
                    
                    for source_path in source_paths:
                        if source_path.exists():
                            shutil.copy2(source_path, shared_model_path)
                            logger.info(f"已复制共享模型: {model_name}")
                            break
                    else:
                        logger.warning(f"未找到基础模型 {model_name}，可能需要手动下载")
            
            logger.info("共享模型检查完成")
            
        except Exception as e:
            logger.error(f"确保共享模型失败: {e}")
    
    def validate_project_config(self, project_name: str) -> bool:
        """验证项目配置完整性"""
        try:
            config = self.project_manager.get_project_config(project_name)
            if config is None:
                return False
            
            # 检查必要的配置项
            required_configs = [
                'classes', 'training_preferences', 'ui_preferences'
            ]
            
            for req_config in required_configs:
                if not hasattr(config, req_config):
                    return False
            
            # 检查项目目录结构
            project_path = self.project_manager.get_project_path(project_name)
            required_dirs = ['configs', 'data', 'models', 'exports', 'runs']
            
            for req_dir in required_dirs:
                dir_path = project_path / req_dir
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except Exception as e:
            logger.error(f"验证项目配置失败: {e}")
            return False
    
    def repair_project_config(self, project_name: str) -> bool:
        """修复项目配置"""
        try:
            logger.info(f"开始修复项目 '{project_name}' 的配置...")
            
            # 重新创建项目配置
            from libs.project_manager import ProjectConfig
            
            default_config = ProjectConfig(
                classes=[],
                class_metadata={},
                training_preferences={
                    "epochs": 100,
                    "batch_size": 16,
                    "img_size": 640,
                    "model": "yolov8n.pt"
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
            
            # 尝试保存现有的类别配置
            try:
                old_classes = self.config_adapter.load_classes()
                if old_classes:
                    default_config.classes = old_classes
            except:
                pass
            
            # 保存修复后的配置
            success = self.project_manager.save_project_config(project_name, default_config)
            
            if success:
                logger.info(f"项目 '{project_name}' 配置修复完成")
            else:
                logger.error(f"项目 '{project_name}' 配置修复失败")
            
            return success
            
        except Exception as e:
            logger.error(f"修复项目配置失败: {e}")
            return False
    
    def get_current_project_info(self) -> Dict[str, Any]:
        """获取当前项目信息"""
        try:
            current_project = self.project_manager.get_current_project()
            projects = self.project_manager.list_projects()
            
            if current_project in projects:
                project_info = projects[current_project].copy()
                project_info['name'] = current_project
                
                # 添加统计信息
                config = self.project_manager.get_project_config(current_project)
                if config:
                    project_info['classes_count'] = len(config.classes)
                    project_info['training_count'] = len(config.training_history)
                
                return project_info
            
            return {}
            
        except Exception as e:
            logger.error(f"获取当前项目信息失败: {e}")
            return {}
    
    def create_project_from_template(self, 
                                   name: str, 
                                   template_type: str = "basic",
                                   **kwargs) -> bool:
        """从模板创建项目"""
        try:
            templates = {
                "basic": {
                    "display_name": f"{name}",
                    "description": "基础项目模板",
                    "classes": [],
                    "training_prefs": {
                        "epochs": 100,
                        "batch_size": 16,
                        "model": "yolov8n.pt"
                    }
                },
                "detection": {
                    "display_name": f"{name} - 目标检测",
                    "description": "目标检测项目模板",
                    "classes": ["object"],
                    "training_prefs": {
                        "epochs": 150,
                        "batch_size": 16,
                        "model": "yolov8s.pt",
                        "img_size": 640
                    }
                },
                "classification": {
                    "display_name": f"{name} - 图像分类",
                    "description": "图像分类项目模板",
                    "classes": ["class1", "class2"],
                    "training_prefs": {
                        "epochs": 200,
                        "batch_size": 32,
                        "model": "yolov8n-cls.pt"
                    }
                }
            }
            
            template = templates.get(template_type, templates["basic"])
            template.update(kwargs)
            
            # 创建项目
            success = self.project_manager.create_project(
                name,
                display_name=template["display_name"],
                description=template["description"]
            )
            
            if success and template_type != "basic":
                # 应用模板配置
                config = self.project_manager.get_project_config(name)
                if config:
                    config.classes = template["classes"]
                    config.training_preferences.update(template["training_prefs"])
                    self.project_manager.save_project_config(name, config)
            
            return success
            
        except Exception as e:
            logger.error(f"从模板创建项目失败: {e}")
            return False
    
    def export_project(self, project_name: str, export_path: str) -> bool:
        """导出项目配置和数据"""
        try:
            export_path = Path(export_path)
            export_path.mkdir(parents=True, exist_ok=True)
            
            # 获取项目路径
            project_path = self.project_manager.get_project_path(project_name)
            
            # 创建压缩包
            import zipfile
            zip_path = export_path / f"{project_name}_export.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加项目文件
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"项目 '{project_name}' 导出完成: {zip_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出项目失败: {e}")
            return False
    
    def import_project(self, import_path: str, project_name: str = None) -> bool:
        """导入项目配置和数据"""
        try:
            import_path = Path(import_path)
            
            if import_path.suffix == '.zip':
                # 从压缩包导入
                import zipfile
                
                with zipfile.ZipFile(import_path, 'r') as zipf:
                    # 如果没有指定项目名，使用文件名
                    if project_name is None:
                        project_name = import_path.stem.replace('_export', '')
                    
                    # 解压到项目目录
                    project_path = self.project_manager.get_project_path(project_name)
                    zipf.extractall(project_path)
            else:
                # 从目录导入
                if project_name is None:
                    project_name = import_path.name
                
                project_path = self.project_manager.get_project_path(project_name)
                shutil.copytree(import_path, project_path, dirs_exist_ok=True)
            
            # 更新项目索引
            metadata_file = project_path / "project.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.project_manager.index["projects"][project_name] = {
                    "display_name": metadata.get('display_name', project_name),
                    "description": metadata.get('description', ''),
                    "created_at": metadata.get('created_at', ''),
                    "updated_at": metadata.get('updated_at', ''),
                    "path": str(project_path)
                }
                
                self.project_manager._save_index()
            
            logger.info(f"项目 '{project_name}' 导入完成")
            return True
            
        except Exception as e:
            logger.error(f"导入项目失败: {e}")
            return False
    
    def cleanup_orphaned_files(self) -> List[str]:
        """清理孤立文件"""
        cleaned_files = []
        try:
            # 清理根目录下的旧配置文件备份
            old_patterns = [
                "*.backup", "*.bak", "*.old", 
                "configs_*", "*_backup", "*_old"
            ]
            
            for pattern in old_patterns:
                for file_path in Path(".").glob(pattern):
                    if file_path.is_file() or (file_path.is_dir() and not list(file_path.iterdir())):
                        try:
                            if file_path.is_dir():
                                shutil.rmtree(file_path)
                            else:
                                file_path.unlink()
                            cleaned_files.append(str(file_path))
                        except Exception as e:
                            logger.warning(f"清理文件失败 {file_path}: {e}")
            
            if cleaned_files:
                logger.info(f"已清理 {len(cleaned_files)} 个孤立文件")
            
            return cleaned_files
            
        except Exception as e:
            logger.error(f"清理孤立文件失败: {e}")
            return cleaned_files


# 全局集成辅助实例
_integration_helper = None

def get_integration_helper() -> ProjectIntegrationHelper:
    """获取集成辅助实例"""
    global _integration_helper
    if _integration_helper is None:
        _integration_helper = ProjectIntegrationHelper()
    return _integration_helper

def initialize_project_system() -> bool:
    """初始化项目系统（便捷函数）"""
    helper = get_integration_helper()
    return helper.initialize_project_system()

def get_current_project_paths() -> Dict[str, str]:
    """获取当前项目的所有路径（便捷函数）"""
    adapter = get_config_adapter()
    return {
        'data': adapter.get_project_data_path(),
        'models': adapter.get_project_models_path(),
        'exports': adapter.get_project_exports_path(),
        'runs': adapter.get_project_runs_path(),
        'configs': str(Path(adapter.get_class_config_path()).parent)
    }