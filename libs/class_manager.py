#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
类别配置管理模块
Class Configuration Manager Module

用于管理YOLO训练中的类别顺序一致性，确保每次训练的类别ID映射都相同。
Manages class order consistency in YOLO training to ensure class ID mapping is the same across training sessions.
"""

import os
import yaml
import json
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_ENCODING = 'utf-8'


class ClassConfigManager:
    """类别配置管理器"""

    def __init__(self, config_dir: str = "configs"):
        """
        初始化类别配置管理器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.class_config_file = os.path.join(config_dir, "class_config.yaml")
        self.backup_dir = os.path.join(config_dir, "backups")

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

        # 当前类别配置
        self.class_config = None

    def load_class_config(self) -> Dict:
        """
        加载类别配置文件

        Returns:
            Dict: 类别配置字典
        """
        try:
            if os.path.exists(self.class_config_file):
                with open(self.class_config_file, 'r', encoding=DEFAULT_ENCODING) as f:
                    self.class_config = yaml.safe_load(f)
                logger.info(f"✅ 成功加载类别配置: {self.class_config_file}")
            else:
                # 创建默认配置
                self.class_config = self._create_default_config()
                self.save_class_config()
                logger.info(f"📝 创建默认类别配置: {self.class_config_file}")

            return self.class_config

        except Exception as e:
            logger.error(f"❌ 加载类别配置失败: {e}")
            # 返回默认配置
            return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """创建默认类别配置"""
        return {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'description': 'YOLO类别配置文件 - 确保训练时类别顺序一致',
            'classes': [],
            'class_metadata': {},
            'settings': {
                'auto_sort': False,  # 是否自动排序类别
                'case_sensitive': True,  # 类别名称是否区分大小写
                'allow_duplicates': False,  # 是否允许重复类别
                'validation_strict': True  # 是否启用严格验证
            }
        }

    def save_class_config(self) -> bool:
        """
        保存类别配置文件

        Returns:
            bool: 保存是否成功
        """
        try:
            # 更新时间戳
            if self.class_config:
                self.class_config['updated_at'] = datetime.now().isoformat()

            # 备份现有配置
            if os.path.exists(self.class_config_file):
                self._backup_config()

            # 保存新配置
            with open(self.class_config_file, 'w', encoding=DEFAULT_ENCODING) as f:
                yaml.dump(self.class_config, f, default_flow_style=False,
                          allow_unicode=True, sort_keys=False)

            logger.info(f"✅ 类别配置保存成功: {self.class_config_file}")
            return True

        except Exception as e:
            logger.error(f"❌ 保存类别配置失败: {e}")
            return False

    def _backup_config(self):
        """备份当前配置文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(
                self.backup_dir, f"class_config_{timestamp}.yaml")

            import shutil
            shutil.copy2(self.class_config_file, backup_file)
            logger.info(f"📋 配置文件已备份: {backup_file}")

        except Exception as e:
            logger.warning(f"⚠️ 配置文件备份失败: {e}")

    def get_class_list(self) -> List[str]:
        """
        获取固定顺序的类别列表

        Returns:
            List[str]: 类别名称列表（按固定顺序）
        """
        if not self.class_config:
            self.load_class_config()

        return self.class_config.get('classes', [])

    def get_class_to_id_mapping(self) -> Dict[str, int]:
        """
        获取类别名称到ID的映射

        Returns:
            Dict[str, int]: 类别名称到ID的映射
        """
        classes = self.get_class_list()
        return {class_name: idx for idx, class_name in enumerate(classes)}

    def get_id_to_class_mapping(self) -> Dict[int, str]:
        """
        获取ID到类别名称的映射

        Returns:
            Dict[int, str]: ID到类别名称的映射
        """
        classes = self.get_class_list()
        return {idx: class_name for idx, class_name in enumerate(classes)}

    def add_class(self, class_name: str, description: str = "", position: Optional[int] = None) -> bool:
        """
        添加新类别

        Args:
            class_name: 类别名称
            description: 类别描述
            position: 插入位置（None表示添加到末尾）

        Returns:
            bool: 添加是否成功
        """
        try:
            if not self.class_config:
                self.load_class_config()

            # 验证类别名称
            if not class_name or not class_name.strip():
                logger.error("❌ 类别名称不能为空")
                return False

            class_name = class_name.strip()

            # 检查重复
            if class_name in self.class_config['classes']:
                logger.warning(f"⚠️ 类别已存在: {class_name}")
                return False

            # 添加类别
            if position is None:
                self.class_config['classes'].append(class_name)
            else:
                self.class_config['classes'].insert(position, class_name)

            # 添加元数据
            self.class_config['class_metadata'][class_name] = {
                'description': description,
                'added_at': datetime.now().isoformat(),
                'usage_count': 0
            }

            logger.info(f"✅ 成功添加类别: {class_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 添加类别失败: {e}")
            return False

    def remove_class(self, class_name: str) -> bool:
        """
        移除类别

        Args:
            class_name: 要移除的类别名称

        Returns:
            bool: 移除是否成功
        """
        try:
            if not self.class_config:
                self.load_class_config()

            if class_name not in self.class_config['classes']:
                logger.warning(f"⚠️ 类别不存在: {class_name}")
                return False

            # 移除类别
            self.class_config['classes'].remove(class_name)

            # 移除元数据
            if class_name in self.class_config['class_metadata']:
                del self.class_config['class_metadata'][class_name]

            logger.info(f"✅ 成功移除类别: {class_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 移除类别失败: {e}")
            return False

    def reorder_classes(self, new_order: List[str]) -> bool:
        """
        重新排序类别

        Args:
            new_order: 新的类别顺序列表

        Returns:
            bool: 重排序是否成功
        """
        try:
            if not self.class_config:
                self.load_class_config()

            current_classes = set(self.class_config['classes'])
            new_classes = set(new_order)

            # 验证类别完整性
            if current_classes != new_classes:
                missing = current_classes - new_classes
                extra = new_classes - current_classes
                logger.error(f"❌ 类别不匹配 - 缺失: {missing}, 多余: {extra}")
                return False

            # 更新顺序
            self.class_config['classes'] = new_order
            logger.info(f"✅ 成功重排序类别: {new_order}")
            return True

        except Exception as e:
            logger.error(f"❌ 重排序类别失败: {e}")
            return False

    def validate_classes(self, classes_to_check: List[str]) -> Tuple[bool, List[str], List[str]]:
        """
        验证类别列表

        Args:
            classes_to_check: 要验证的类别列表

        Returns:
            Tuple[bool, List[str], List[str]]: (是否有效, 缺失的类别, 多余的类别)
        """
        try:
            if not self.class_config:
                self.load_class_config()

            configured_classes = set(self.class_config['classes'])
            check_classes = set(classes_to_check)

            missing_classes = list(configured_classes - check_classes)
            extra_classes = list(check_classes - configured_classes)

            is_valid = len(missing_classes) == 0 and len(extra_classes) == 0

            return is_valid, missing_classes, extra_classes

        except Exception as e:
            logger.error(f"❌ 验证类别失败: {e}")
            return False, [], []

    def analyze_dataset_classes(self, dataset_path: str) -> Dict:
        """
        分析数据集中的类别使用情况

        Args:
            dataset_path: 数据集路径

        Returns:
            Dict: 分析结果
        """
        try:
            analysis = {
                'dataset_path': dataset_path,
                'data_yaml_path': None,
                'classes_txt_path': None,
                'yaml_classes': [],
                'txt_classes': [],
                'label_files_classes': set(),
                'class_usage_count': {},
                'inconsistencies': [],
                'recommendations': []
            }

            # 检查data.yaml文件
            data_yaml_path = os.path.join(dataset_path, "data.yaml")
            if os.path.exists(data_yaml_path):
                analysis['data_yaml_path'] = data_yaml_path
                try:
                    with open(data_yaml_path, 'r', encoding=DEFAULT_ENCODING) as f:
                        yaml_config = yaml.safe_load(f)

                    if 'names' in yaml_config:
                        names = yaml_config['names']
                        if isinstance(names, dict):
                            # 按ID排序获取类别列表
                            analysis['yaml_classes'] = [names[i]
                                                        for i in sorted(names.keys())]
                        elif isinstance(names, list):
                            analysis['yaml_classes'] = names

                except Exception as e:
                    logger.warning(f"⚠️ 读取data.yaml失败: {e}")

            # 检查classes.txt文件
            classes_txt_path = os.path.join(dataset_path, "classes.txt")
            if os.path.exists(classes_txt_path):
                analysis['classes_txt_path'] = classes_txt_path
                try:
                    with open(classes_txt_path, 'r', encoding=DEFAULT_ENCODING) as f:
                        analysis['txt_classes'] = [line.strip()
                                                   for line in f if line.strip()]
                except Exception as e:
                    logger.warning(f"⚠️ 读取classes.txt失败: {e}")

            # 分析标签文件中的类别使用情况
            labels_dirs = [
                os.path.join(dataset_path, "labels", "train"),
                os.path.join(dataset_path, "labels", "val"),
                os.path.join(dataset_path, "labels")
            ]

            for labels_dir in labels_dirs:
                if os.path.exists(labels_dir):
                    for label_file in os.listdir(labels_dir):
                        if label_file.endswith('.txt'):
                            label_path = os.path.join(labels_dir, label_file)
                            try:
                                with open(label_path, 'r', encoding=DEFAULT_ENCODING) as f:
                                    for line in f:
                                        parts = line.strip().split()
                                        if parts:
                                            class_id = int(parts[0])
                                            analysis['label_files_classes'].add(
                                                class_id)
                                            analysis['class_usage_count'][class_id] = \
                                                analysis['class_usage_count'].get(
                                                    class_id, 0) + 1
                            except Exception as e:
                                logger.warning(
                                    f"⚠️ 读取标签文件失败 {label_path}: {e}")

            # 转换为列表便于JSON序列化
            analysis['label_files_classes'] = sorted(
                list(analysis['label_files_classes']))

            # 检查一致性
            self._check_dataset_consistency(analysis)

            return analysis

        except Exception as e:
            logger.error(f"❌ 分析数据集失败: {e}")
            return {}

    def _check_dataset_consistency(self, analysis: Dict):
        """检查数据集一致性并生成建议"""
        try:
            yaml_classes = analysis['yaml_classes']
            txt_classes = analysis['txt_classes']
            label_class_ids = analysis['label_files_classes']

            # 检查yaml和txt文件的一致性
            if yaml_classes and txt_classes:
                if yaml_classes != txt_classes:
                    analysis['inconsistencies'].append(
                        "data.yaml和classes.txt中的类别顺序不一致"
                    )

            # 检查标签文件中的类别ID是否超出范围
            if yaml_classes and label_class_ids:
                max_valid_id = len(yaml_classes) - 1
                invalid_ids = [
                    cid for cid in label_class_ids if cid > max_valid_id]
                if invalid_ids:
                    analysis['inconsistencies'].append(
                        f"标签文件中存在无效的类别ID: {invalid_ids}"
                    )

            # 生成建议
            if not yaml_classes and not txt_classes:
                analysis['recommendations'].append(
                    "建议创建类别配置文件来固定类别顺序"
                )
            elif analysis['inconsistencies']:
                analysis['recommendations'].append(
                    "建议使用类别配置管理器来修复不一致问题"
                )
            else:
                analysis['recommendations'].append(
                    "数据集类别配置看起来是一致的"
                )

        except Exception as e:
            logger.warning(f"⚠️ 检查一致性失败: {e}")

    def create_config_from_dataset(self, dataset_path: str, description: str = "") -> bool:
        """
        从现有数据集创建类别配置

        Args:
            dataset_path: 数据集路径
            description: 配置描述

        Returns:
            bool: 创建是否成功
        """
        try:
            analysis = self.analyze_dataset_classes(dataset_path)

            if not analysis:
                logger.error("❌ 无法分析数据集")
                return False

            # 优先使用data.yaml中的类别顺序
            classes = analysis.get('yaml_classes', [])
            if not classes:
                classes = analysis.get('txt_classes', [])

            if not classes:
                logger.error("❌ 数据集中未找到类别信息")
                return False

            # 创建新配置
            self.class_config = self._create_default_config()
            self.class_config['description'] = description or f"从数据集 {dataset_path} 创建的类别配置"
            self.class_config['classes'] = classes

            # 添加类别元数据
            for idx, class_name in enumerate(classes):
                usage_count = sum(1 for cid, count in analysis['class_usage_count'].items()
                                  if cid == idx for _ in range(count))
                self.class_config['class_metadata'][class_name] = {
                    'description': f"从数据集导入的类别",
                    'added_at': datetime.now().isoformat(),
                    'usage_count': usage_count,
                    'original_id': idx
                }

            # 保存配置
            success = self.save_class_config()
            if success:
                logger.info(f"✅ 成功从数据集创建类别配置: {len(classes)} 个类别")

            return success

        except Exception as e:
            logger.error(f"❌ 从数据集创建配置失败: {e}")
            return False

    def sync_with_predefined_classes(self, predefined_classes_file: str = None) -> bool:
        """
        与预设类别文件同步

        Args:
            predefined_classes_file: 预设类别文件路径，如果为None则自动获取

        Returns:
            bool: 同步是否成功
        """
        try:
            # 获取预设类别文件路径
            if predefined_classes_file is None:
                try:
                    # 尝试导入labelImg模块获取路径
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(
                        os.path.dirname(__file__), '..'))
                    from labelImg import get_persistent_predefined_classes_path
                    predefined_classes_file = get_persistent_predefined_classes_path()
                except ImportError:
                    logger.warning("⚠️ 无法导入labelImg模块，使用默认路径")
                    predefined_classes_file = os.path.join(
                        os.path.expanduser('~'), '.labelImg', 'predefined_classes.txt')

            logger.info(f"🔄 开始与预设类别文件同步: {predefined_classes_file}")

            # 检查预设类别文件是否存在
            if not os.path.exists(predefined_classes_file):
                logger.warning(f"⚠️ 预设类别文件不存在: {predefined_classes_file}")
                return False

            # 读取预设类别文件
            with open(predefined_classes_file, 'r', encoding='utf-8') as f:
                predefined_classes = [line.strip()
                                      for line in f.readlines() if line.strip()]

            if not predefined_classes:
                logger.warning("⚠️ 预设类别文件为空")
                return False

            logger.info(f"📋 从预设类别文件读取到 {len(predefined_classes)} 个类别")
            logger.info(f"🏷️ 预设类别: {predefined_classes}")

            # 加载当前配置
            if not self.class_config:
                self.load_class_config()

            current_classes = self.class_config.get('classes', [])
            logger.info(f"📋 当前配置中有 {len(current_classes)} 个类别")
            logger.info(f"🏷️ 当前类别: {current_classes}")

            # 检查是否需要同步
            if current_classes == predefined_classes:
                logger.info("✅ 类别已同步，无需更新")
                return True

            # 更新配置
            self.class_config['classes'] = predefined_classes
            self.class_config['updated_at'] = datetime.now().isoformat()
            self.class_config['description'] = f"与预设类别文件同步的配置 - 确保YOLO训练时类别顺序一致"

            # 更新类别元数据
            self.class_config['class_metadata'] = {}
            for idx, class_name in enumerate(predefined_classes):
                self.class_config['class_metadata'][class_name] = {
                    'description': f"从预设类别文件同步的类别",
                    'added_at': datetime.now().isoformat(),
                    'usage_count': 0,
                    'original_id': idx,
                    'source': 'predefined_classes.txt'
                }

            # 保存配置
            success = self.save_class_config()
            if success:
                logger.info(f"✅ 成功同步类别配置: {len(predefined_classes)} 个类别")
                logger.info(f"🏷️ 同步后的类别顺序: {predefined_classes}")
                return True
            else:
                logger.error("❌ 保存同步后的配置失败")
                return False

        except Exception as e:
            logger.error(f"❌ 与预设类别文件同步失败: {e}")
            return False

    def sync_to_predefined_classes(self, predefined_classes_file: str = None) -> bool:
        """
        将当前配置同步到预设类别文件

        Args:
            predefined_classes_file: 预设类别文件路径，如果为None则自动获取

        Returns:
            bool: 同步是否成功
        """
        try:
            # 获取预设类别文件路径
            if predefined_classes_file is None:
                try:
                    # 尝试导入labelImg模块获取路径
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(
                        os.path.dirname(__file__), '..'))
                    from labelImg import get_persistent_predefined_classes_path
                    predefined_classes_file = get_persistent_predefined_classes_path()
                except ImportError:
                    logger.warning("⚠️ 无法导入labelImg模块，使用默认路径")
                    predefined_classes_file = os.path.join(
                        os.path.expanduser('~'), '.labelImg', 'predefined_classes.txt')

            logger.info(f"🔄 开始将配置同步到预设类别文件: {predefined_classes_file}")

            # 加载当前配置
            if not self.class_config:
                self.load_class_config()

            current_classes = self.class_config.get('classes', [])
            if not current_classes:
                logger.warning("⚠️ 当前配置中没有类别")
                return False

            logger.info(f"📋 将同步 {len(current_classes)} 个类别到预设文件")
            logger.info(f"🏷️ 类别列表: {current_classes}")

            # 确保目录存在
            os.makedirs(os.path.dirname(
                predefined_classes_file), exist_ok=True)

            # 写入预设类别文件
            with open(predefined_classes_file, 'w', encoding='utf-8') as f:
                for class_name in current_classes:
                    f.write(f"{class_name}\n")

            logger.info(f"✅ 成功将类别配置同步到预设文件: {predefined_classes_file}")
            return True

        except Exception as e:
            logger.error(f"❌ 同步到预设类别文件失败: {e}")
            return False
