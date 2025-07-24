#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import shutil
import random
import yaml
from xml.etree import ElementTree
from libs.constants import DEFAULT_ENCODING
from libs.class_manager import ClassConfigManager


class PascalToYOLOConverter:
    """Pascal VOC到YOLO格式的转换器 - 支持固定类别顺序"""

    def __init__(self, source_dir, target_dir, dataset_name="dataset", train_ratio=0.8,
                 use_class_config=True, class_config_dir="configs"):
        """
        初始化转换器

        Args:
            source_dir: 源目录，包含图片和XML标注文件
            target_dir: 目标目录，将创建YOLO格式的数据集
            dataset_name: 数据集名称
            train_ratio: 训练集比例，默认0.8
            use_class_config: 是否使用类别配置管理器，默认True
            class_config_dir: 类别配置文件目录，默认"configs"
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.dataset_name = dataset_name
        self.train_ratio = train_ratio
        self.use_class_config = use_class_config

        # 数据集路径
        self.dataset_path = os.path.join(target_dir, dataset_name)
        self.images_dir = os.path.join(self.dataset_path, "images")
        self.labels_dir = os.path.join(self.dataset_path, "labels")
        self.train_images_dir = os.path.join(self.images_dir, "train")
        self.val_images_dir = os.path.join(self.images_dir, "val")
        self.train_labels_dir = os.path.join(self.labels_dir, "train")
        self.val_labels_dir = os.path.join(self.labels_dir, "val")

        # 类别管理
        if self.use_class_config:
            self.class_manager = ClassConfigManager(class_config_dir)
            self.class_manager.load_class_config()
            # 使用配置文件中的固定类别顺序
            self.classes = self.class_manager.get_class_list()
            self.class_to_id = self.class_manager.get_class_to_id_mapping()
            print(f"📋 使用固定类别配置: {len(self.classes)} 个类别")
            if self.classes:
                print(f"🏷️ 类别顺序: {self.classes}")
        else:
            # 传统的动态类别添加方式（不推荐）
            self.classes = []
            self.class_to_id = {}
            self.class_manager = None
            print("⚠️ 使用动态类别添加模式（可能导致顺序不一致）")

        # 统计信息
        self.total_files = 0
        self.processed_files = 0
        self.train_count = 0
        self.val_count = 0
        self.unknown_classes = set()  # 记录未知类别

    def create_directories(self, clean_existing=False, backup_existing=False):
        """
        创建YOLO数据集目录结构

        Args:
            clean_existing: 是否清空现有目录
            backup_existing: 是否备份现有目录
        """
        directories = [
            self.dataset_path,
            self.images_dir,
            self.labels_dir,
            self.train_images_dir,
            self.val_images_dir,
            self.train_labels_dir,
            self.val_labels_dir
        ]

        # 如果需要备份现有数据
        if backup_existing and os.path.exists(self.dataset_path):
            self._backup_existing_dataset()

        # 如果需要清空现有目录
        if clean_existing:
            self._clean_existing_directories(directories)

        # 创建目录结构
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _backup_existing_dataset(self):
        """备份现有数据集"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.dataset_path}_backup_{timestamp}"

            print(f"📋 备份现有数据集到: {backup_path}")
            shutil.copytree(self.dataset_path, backup_path)

            # 记录备份路径，用于可能的恢复
            self.backup_path = backup_path
            print(f"✅ 数据集备份完成: {backup_path}")

        except Exception as e:
            print(f"⚠️ 备份数据集失败: {e}")
            self.backup_path = None

    def _clean_existing_directories(self, directories):
        """清空现有目录"""
        try:
            cleaned_count = 0
            for directory in directories:
                if os.path.exists(directory):
                    # 统计要删除的文件数量
                    file_count = sum([len(files)
                                     for r, d, files in os.walk(directory)])
                    if file_count > 0:
                        print(f"🗑️ 清空目录: {directory} ({file_count} 个文件)")
                        shutil.rmtree(directory)
                        cleaned_count += file_count

            if cleaned_count > 0:
                print(f"✅ 已清空 {cleaned_count} 个现有文件")
            else:
                print("ℹ️ 目标目录为空，无需清空")

        except Exception as e:
            print(f"❌ 清空目录失败: {e}")
            raise

    def get_existing_files_info(self):
        """获取现有文件信息，用于用户确认"""
        try:
            info = {
                'dataset_exists': os.path.exists(self.dataset_path),
                'total_files': 0,
                'train_images': 0,
                'val_images': 0,
                'train_labels': 0,
                'val_labels': 0
            }

            if info['dataset_exists']:
                # 统计各类文件数量
                if os.path.exists(self.train_images_dir):
                    info['train_images'] = len([f for f in os.listdir(self.train_images_dir)
                                               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])

                if os.path.exists(self.val_images_dir):
                    info['val_images'] = len([f for f in os.listdir(self.val_images_dir)
                                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])

                if os.path.exists(self.train_labels_dir):
                    info['train_labels'] = len([f for f in os.listdir(self.train_labels_dir)
                                               if f.endswith('.txt')])

                if os.path.exists(self.val_labels_dir):
                    info['val_labels'] = len([f for f in os.listdir(self.val_labels_dir)
                                             if f.endswith('.txt')])

                info['total_files'] = info['train_images'] + \
                    info['val_images'] + \
                    info['train_labels'] + info['val_labels']

            return info

        except Exception as e:
            print(f"⚠️ 获取现有文件信息失败: {e}")
            return {'dataset_exists': False, 'total_files': 0}

    def verify_conversion_integrity(self, source_files):
        """验证转换后的数据完整性"""
        try:
            print("🔍 验证转换数据完整性...")

            # 统计转换后的文件
            train_images = len([f for f in os.listdir(self.train_images_dir)
                               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]) if os.path.exists(self.train_images_dir) else 0
            val_images = len([f for f in os.listdir(self.val_images_dir)
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]) if os.path.exists(self.val_images_dir) else 0
            train_labels = len([f for f in os.listdir(self.train_labels_dir)
                               if f.endswith('.txt')]) if os.path.exists(self.train_labels_dir) else 0
            val_labels = len([f for f in os.listdir(self.val_labels_dir)
                             if f.endswith('.txt')]) if os.path.exists(self.val_labels_dir) else 0

            total_converted = train_images + val_images
            total_source = len(source_files)

            # 验证文件数量
            integrity_report = {
                'source_files': total_source,
                'converted_images': total_converted,
                'train_images': train_images,
                'val_images': val_images,
                'train_labels': train_labels,
                'val_labels': val_labels,
                'images_match_labels': train_images == train_labels and val_images == val_labels,
                'all_files_converted': total_converted == total_source,
                'integrity_passed': False
            }

            # 检查完整性
            if integrity_report['images_match_labels'] and integrity_report['all_files_converted']:
                integrity_report['integrity_passed'] = True
                print("✅ 数据完整性验证通过")
                print(f"   源文件: {total_source} 个")
                print(f"   转换图片: {total_converted} 个")
                print(f"   训练集: {train_images} 图片, {train_labels} 标签")
                print(f"   验证集: {val_images} 图片, {val_labels} 标签")
            else:
                print("⚠️ 数据完整性验证失败")
                if not integrity_report['all_files_converted']:
                    print(
                        f"   文件数量不匹配: 源文件 {total_source} 个, 转换 {total_converted} 个")
                if not integrity_report['images_match_labels']:
                    print(
                        f"   图片标签不匹配: 训练集 {train_images}:{train_labels}, 验证集 {val_images}:{val_labels}")

            return integrity_report

        except Exception as e:
            print(f"❌ 数据完整性验证失败: {e}")
            return {'integrity_passed': False, 'error': str(e)}

    def scan_annotations(self):
        """扫描源目录中的XML标注文件"""
        xml_files = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

        for file in os.listdir(self.source_dir):
            if file.lower().endswith('.xml'):
                # 检查是否有对应的图片文件
                base_name = os.path.splitext(file)[0]
                image_file = None

                for ext in image_extensions:
                    potential_image = os.path.join(
                        self.source_dir, base_name + ext)
                    if os.path.exists(potential_image):
                        image_file = base_name + ext
                        break

                if image_file:
                    xml_files.append((file, image_file))

        return xml_files

    def parse_xml_annotation(self, xml_path):
        """解析Pascal VOC XML标注文件"""
        try:
            tree = ElementTree.parse(xml_path)
            root = tree.getroot()

            # 获取图片尺寸
            size = root.find('size')
            if size is None:
                return None, None, None

            width = int(size.find('width').text)
            height = int(size.find('height').text)

            # 解析所有对象
            objects = []
            for obj in root.findall('object'):
                name = obj.find('name').text

                # 处理类别映射
                if self.use_class_config:
                    # 使用固定类别配置
                    if name not in self.class_to_id:
                        # 尝试自动添加新类别到配置
                        if self._auto_add_unknown_class(name):
                            class_id = self.class_to_id[name]
                            print(f"✅ 自动添加新类别: {name} (ID: {class_id})")
                        else:
                            # 记录未知类别并跳过
                            self.unknown_classes.add(name)
                            print(f"⚠️ 发现未知类别: {name} (将跳过此对象)")
                            continue
                    else:
                        class_id = self.class_to_id[name]
                else:
                    # 传统的动态添加方式
                    if name not in self.classes:
                        self.classes.append(name)
                        self.class_to_id[name] = len(self.classes) - 1
                    class_id = self.class_to_id[name]

                # 获取边界框
                bbox = obj.find('bndbox')
                if bbox is None:
                    continue

                xmin = float(bbox.find('xmin').text)
                ymin = float(bbox.find('ymin').text)
                xmax = float(bbox.find('xmax').text)
                ymax = float(bbox.find('ymax').text)

                # 转换为YOLO格式 (中心点坐标和相对尺寸)
                x_center = (xmin + xmax) / 2.0 / width
                y_center = (ymin + ymax) / 2.0 / height
                bbox_width = (xmax - xmin) / width
                bbox_height = (ymax - ymin) / height

                objects.append(
                    (class_id, x_center, y_center, bbox_width, bbox_height))

            return width, height, objects

        except Exception as e:
            print(f"Error parsing XML file {xml_path}: {e}")
            return None, None, None

    def write_yolo_annotation(self, objects, output_path):
        """写入YOLO格式的标注文件"""
        try:
            with open(output_path, 'w', encoding=DEFAULT_ENCODING) as f:
                for obj in objects:
                    class_id, x_center, y_center, width, height = obj
                    f.write(
                        f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            return True
        except Exception as e:
            print(f"Error writing YOLO annotation to {output_path}: {e}")
            return False

    def copy_image(self, source_image_path, target_image_path):
        """复制图片文件"""
        try:
            shutil.copy2(source_image_path, target_image_path)
            return True
        except Exception as e:
            print(
                f"Error copying image from {source_image_path} to {target_image_path}: {e}")
            return False

    def generate_classes_file(self):
        """生成classes.txt文件"""
        classes_file = os.path.join(self.dataset_path, "classes.txt")
        try:
            with open(classes_file, 'w', encoding=DEFAULT_ENCODING) as f:
                for class_name in self.classes:
                    f.write(f"{class_name}\n")
            return True
        except Exception as e:
            print(f"Error generating classes file: {e}")
            return False

    def generate_yaml_config(self):
        """生成YOLO训练配置文件"""
        yaml_file = os.path.join(self.dataset_path, "data.yaml")

        # 使用绝对路径确保YOLO训练器能正确找到数据
        dataset_abs_path = os.path.abspath(self.dataset_path)

        config = {
            'path': dataset_abs_path,  # 使用绝对路径，确保YOLO训练器能正确找到数据
            'train': "images/train",   # 相对于path字段的路径
            'val': "images/val",       # 相对于path字段的路径
            'test': None,
            'names': {i: name for i, name in enumerate(self.classes)}
        }

        try:
            with open(yaml_file, 'w', encoding=DEFAULT_ENCODING) as f:
                yaml.dump(config, f, default_flow_style=False,
                          allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error generating YAML config: {e}")
            return False

    def convert(self, progress_callback=None, clean_existing=False, backup_existing=False):
        """
        执行转换过程

        Args:
            progress_callback: 进度回调函数，接收 (current, total, message) 参数
            clean_existing: 是否清空现有目录
            backup_existing: 是否备份现有目录
        """
        try:
            # 创建目录结构
            self.create_directories(
                clean_existing=clean_existing, backup_existing=backup_existing)

            # 如果使用类别配置但配置为空，先扫描所有类别
            if self.use_class_config and not self.classes:
                if progress_callback:
                    progress_callback(0, 100, "扫描数据集类别...")
                self._scan_and_setup_classes()

            # 扫描标注文件
            if progress_callback:
                progress_callback(5, 100, "扫描标注文件...")

            xml_files = self.scan_annotations()
            if not xml_files:
                raise Exception("未找到有效的标注文件")

            self.total_files = len(xml_files)

            # 随机分割训练集和验证集
            random.shuffle(xml_files)
            split_index = int(len(xml_files) * self.train_ratio)
            train_files = xml_files[:split_index]
            val_files = xml_files[split_index:]

            # 处理训练集
            if progress_callback:
                progress_callback(
                    10, 100, f"处理训练集文件 ({len(train_files)} 个)...")

            for i, (xml_file, image_file) in enumerate(train_files):
                self._process_file(xml_file, image_file, is_train=True)
                self.train_count += 1
                if progress_callback:
                    progress = 10 + (i + 1) / len(train_files) * 40
                    progress_callback(int(progress), 100,
                                      f"处理训练集: {i+1}/{len(train_files)}")

            # 处理验证集
            if progress_callback:
                progress_callback(50, 100, f"处理验证集文件 ({len(val_files)} 个)...")

            for i, (xml_file, image_file) in enumerate(val_files):
                self._process_file(xml_file, image_file, is_train=False)
                self.val_count += 1
                if progress_callback:
                    progress = 50 + (i + 1) / len(val_files) * 40
                    progress_callback(int(progress), 100,
                                      f"处理验证集: {i+1}/{len(val_files)}")

            # 生成配置文件
            if progress_callback:
                progress_callback(90, 100, "生成配置文件...")

            self.generate_classes_file()
            self.generate_yaml_config()

            # 验证数据完整性
            if progress_callback:
                progress_callback(95, 100, "验证数据完整性...")

            integrity_report = self.verify_conversion_integrity(xml_files)
            if not integrity_report.get('integrity_passed', False):
                warning_msg = "⚠️ 数据完整性验证未通过，但转换已完成"
                print(warning_msg)

            if progress_callback:
                progress_callback(100, 100, "转换完成!")

            # 生成转换报告
            report = self._generate_conversion_report()

            # 添加完整性信息到报告
            if integrity_report.get('integrity_passed', False):
                report += "\n\n✅ 数据完整性验证: 通过"
            else:
                report += "\n\n⚠️ 数据完整性验证: 未通过"
                if 'error' in integrity_report:
                    report += f"\n   错误: {integrity_report['error']}"

            return True, report

        except Exception as e:
            return False, str(e)

    def _process_file(self, xml_file, image_file, is_train=True):
        """处理单个文件"""
        xml_path = os.path.join(self.source_dir, xml_file)
        image_path = os.path.join(self.source_dir, image_file)

        # 解析XML标注
        width, height, objects = self.parse_xml_annotation(xml_path)
        if objects is None:
            return False

        # 确定目标目录
        if is_train:
            target_images_dir = self.train_images_dir
            target_labels_dir = self.train_labels_dir
        else:
            target_images_dir = self.val_images_dir
            target_labels_dir = self.val_labels_dir

        # 复制图片
        base_name = os.path.splitext(image_file)[0]
        target_image_path = os.path.join(target_images_dir, image_file)
        if not self.copy_image(image_path, target_image_path):
            return False

        # 写入YOLO标注
        target_label_path = os.path.join(target_labels_dir, base_name + ".txt")
        if not self.write_yolo_annotation(objects, target_label_path):
            return False

        self.processed_files += 1
        return True

    def _scan_and_setup_classes(self):
        """扫描数据集中的所有类别并设置类别配置"""
        try:
            print("🔍 扫描数据集中的类别...")
            found_classes = set()

            # 扫描所有XML文件获取类别
            xml_files = self.scan_annotations()
            for xml_file in xml_files:
                xml_path = os.path.join(self.source_dir, xml_file)
                try:
                    tree = ElementTree.parse(xml_path)
                    root = tree.getroot()

                    for obj in root.findall('object'):
                        name = obj.find('name').text
                        if name:
                            found_classes.add(name)

                except Exception as e:
                    print(f"⚠️ 解析XML文件失败 {xml_file}: {e}")

            found_classes = sorted(list(found_classes))  # 按字母顺序排序
            print(f"📋 发现类别: {found_classes}")

            if found_classes:
                # 更新类别配置
                self.class_manager.class_config['classes'] = found_classes
                for idx, class_name in enumerate(found_classes):
                    from datetime import datetime
                    self.class_manager.class_config['class_metadata'][class_name] = {
                        'description': f"从数据集自动发现的类别",
                        'added_at': datetime.now().isoformat(),
                        'usage_count': 0,
                        'auto_discovered': True
                    }

                # 保存配置
                self.class_manager.save_class_config()

                # 更新当前实例的类别信息
                self.classes = found_classes
                self.class_to_id = {name: idx for idx,
                                    name in enumerate(found_classes)}

                print(f"✅ 自动配置了 {len(found_classes)} 个类别")
            else:
                print("⚠️ 未发现任何类别")

        except Exception as e:
            print(f"❌ 扫描类别失败: {e}")

    def _auto_add_unknown_class(self, class_name: str) -> bool:
        """
        自动添加未知类别到配置中

        Args:
            class_name: 类别名称

        Returns:
            bool: 是否成功添加
        """
        try:
            if not self.class_manager:
                return False

            print(f"🔄 尝试自动添加未知类别: {class_name}")

            # 添加类别到配置管理器
            success = self.class_manager.add_class(
                class_name,
                description=f"转换过程中自动发现的类别"
            )

            if success:
                # 重新加载类别配置
                self.classes = self.class_manager.get_class_list()
                self.class_to_id = self.class_manager.get_class_to_id_mapping()

                # 保存配置
                self.class_manager.save_class_config()

                print(f"✅ 成功添加类别: {class_name}")
                print(f"📋 更新后的类别列表: {self.classes}")

                return True
            else:
                print(f"❌ 添加类别失败: {class_name}")
                return False

        except Exception as e:
            print(f"❌ 自动添加类别时出错: {e}")
            return False

    def _generate_conversion_report(self) -> str:
        """生成转换报告"""
        try:
            report_lines = [
                f"✅ 转换完成！",
                f"📊 文件统计:",
                f"  - 总文件数: {self.total_files}",
                f"  - 训练集: {self.train_count} 个",
                f"  - 验证集: {self.val_count} 个",
                f"🏷️ 类别信息:",
                f"  - 类别数量: {len(self.classes)}",
                f"  - 类别列表: {self.classes}"
            ]

            if self.use_class_config:
                report_lines.append(f"📋 使用固定类别配置: ✅")
                if self.unknown_classes:
                    report_lines.extend([
                        f"⚠️ 发现未知类别 (已跳过):",
                        f"  - {sorted(list(self.unknown_classes))}"
                    ])
            else:
                report_lines.append(f"⚠️ 使用动态类别添加 (可能导致顺序不一致)")

            return "\n".join(report_lines)

        except Exception as e:
            return f"转换完成，但生成报告失败: {e}"

    def get_class_statistics(self) -> dict:
        """获取类别统计信息"""
        return {
            'total_classes': len(self.classes),
            'classes': self.classes.copy(),
            'class_to_id': self.class_to_id.copy(),
            'unknown_classes': sorted(list(self.unknown_classes)),
            'use_class_config': self.use_class_config,
            'config_file': self.class_manager.class_config_file if self.class_manager else None
        }
