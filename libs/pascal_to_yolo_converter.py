#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import shutil
import random
import yaml
from xml.etree import ElementTree
from libs.constants import DEFAULT_ENCODING

class PascalToYOLOConverter:
    """Pascal VOC到YOLO格式的转换器"""
    
    def __init__(self, source_dir, target_dir, dataset_name="dataset", train_ratio=0.8):
        """
        初始化转换器
        
        Args:
            source_dir: 源目录，包含图片和XML标注文件
            target_dir: 目标目录，将创建YOLO格式的数据集
            dataset_name: 数据集名称
            train_ratio: 训练集比例，默认0.8
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.dataset_name = dataset_name
        self.train_ratio = train_ratio
        
        # 数据集路径
        self.dataset_path = os.path.join(target_dir, dataset_name)
        self.images_dir = os.path.join(self.dataset_path, "images")
        self.labels_dir = os.path.join(self.dataset_path, "labels")
        self.train_images_dir = os.path.join(self.images_dir, "train")
        self.val_images_dir = os.path.join(self.images_dir, "val")
        self.train_labels_dir = os.path.join(self.labels_dir, "train")
        self.val_labels_dir = os.path.join(self.labels_dir, "val")
        
        # 类别列表
        self.classes = []
        self.class_to_id = {}
        
        # 统计信息
        self.total_files = 0
        self.processed_files = 0
        self.train_count = 0
        self.val_count = 0
        
    def create_directories(self):
        """创建YOLO数据集目录结构"""
        directories = [
            self.dataset_path,
            self.images_dir,
            self.labels_dir,
            self.train_images_dir,
            self.val_images_dir,
            self.train_labels_dir,
            self.val_labels_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
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
                    potential_image = os.path.join(self.source_dir, base_name + ext)
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
                
                # 添加类别到列表中
                if name not in self.classes:
                    self.classes.append(name)
                    self.class_to_id[name] = len(self.classes) - 1
                
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
                
                class_id = self.class_to_id[name]
                objects.append((class_id, x_center, y_center, bbox_width, bbox_height))
            
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
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
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
            print(f"Error copying image from {source_image_path} to {target_image_path}: {e}")
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
        
        config = {
            'path': f"../datasets/{self.dataset_name}",
            'train': "images/train",
            'val': "images/val",
            'test': None,
            'names': {i: name for i, name in enumerate(self.classes)}
        }
        
        try:
            with open(yaml_file, 'w', encoding=DEFAULT_ENCODING) as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error generating YAML config: {e}")
            return False
    
    def convert(self, progress_callback=None):
        """
        执行转换过程
        
        Args:
            progress_callback: 进度回调函数，接收 (current, total, message) 参数
        """
        try:
            # 创建目录结构
            self.create_directories()
            
            # 扫描标注文件
            if progress_callback:
                progress_callback(0, 100, "扫描标注文件...")
            
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
                progress_callback(10, 100, f"处理训练集文件 ({len(train_files)} 个)...")
            
            for i, (xml_file, image_file) in enumerate(train_files):
                self._process_file(xml_file, image_file, is_train=True)
                self.train_count += 1
                if progress_callback:
                    progress = 10 + (i + 1) / len(train_files) * 40
                    progress_callback(int(progress), 100, f"处理训练集: {i+1}/{len(train_files)}")
            
            # 处理验证集
            if progress_callback:
                progress_callback(50, 100, f"处理验证集文件 ({len(val_files)} 个)...")
            
            for i, (xml_file, image_file) in enumerate(val_files):
                self._process_file(xml_file, image_file, is_train=False)
                self.val_count += 1
                if progress_callback:
                    progress = 50 + (i + 1) / len(val_files) * 40
                    progress_callback(int(progress), 100, f"处理验证集: {i+1}/{len(val_files)}")
            
            # 生成配置文件
            if progress_callback:
                progress_callback(90, 100, "生成配置文件...")
            
            self.generate_classes_file()
            self.generate_yaml_config()
            
            if progress_callback:
                progress_callback(100, 100, "转换完成!")
            
            return True, f"成功转换 {self.total_files} 个文件\n训练集: {self.train_count} 个\n验证集: {self.val_count} 个\n类别数: {len(self.classes)}"
            
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
