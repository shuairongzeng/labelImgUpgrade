#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
测试统一的类别处理逻辑
"""

import os
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import json
import tempfile
import shutil
from xml.etree import ElementTree as ET

# 添加libs目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.pascal_to_yolo_converter import PascalToYOLOConverter


def create_test_xml(filepath, class_name):
    """创建测试用的XML文件"""
    root = ET.Element("annotation")
    
    # 添加文件名
    filename = ET.SubElement(root, "filename")
    filename.text = "test.jpg"
    
    # 添加尺寸
    size = ET.SubElement(root, "size")
    width = ET.SubElement(size, "width")
    width.text = "640"
    height = ET.SubElement(size, "height")
    height.text = "480"
    
    # 添加对象
    obj = ET.SubElement(root, "object")
    name = ET.SubElement(obj, "name")
    name.text = class_name
    
    bndbox = ET.SubElement(obj, "bndbox")
    xmin = ET.SubElement(bndbox, "xmin")
    xmin.text = "100"
    ymin = ET.SubElement(bndbox, "ymin")
    ymin.text = "100"
    xmax = ET.SubElement(bndbox, "xmax")
    xmax.text = "200"
    ymax = ET.SubElement(bndbox, "ymax")
    ymax.text = "200"
    
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)


def create_test_json(filepath, class_name):
    """创建测试用的JSON文件"""
    data = [{
        "image": "test.jpg",
        "annotations": [{
            "label": class_name,
            "coordinates": {
                "x": 150,
                "y": 150,
                "width": 100,
                "height": 100
            }
        }]
    }]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def test_unified_processing():
    """测试统一的类别处理"""
    print("=" * 60)
    print("测试统一的类别处理逻辑")
    print("=" * 60)
    
    # 创建临时目录
    test_dir = tempfile.mkdtemp(prefix="test_converter_")
    output_dir = tempfile.mkdtemp(prefix="test_output_")
    
    try:
        # 测试1: XML格式的新类别处理
        print("\n📝 测试1: XML格式的新类别处理")
        xml_path = os.path.join(test_dir, "test.xml")
        create_test_xml(xml_path, "new_class_xml")
        
        converter_xml = PascalToYOLOConverter(
            source_dir=test_dir,
            target_dir=output_dir,
            dataset_name="test_xml",
            use_class_config=True
        )
        
        width, height, objects = converter_xml.parse_xml_annotation(xml_path)
        if objects:
            print(f"✅ XML解析成功: 找到 {len(objects)} 个对象")
            print(f"   类别ID: {objects[0][0]}")
        else:
            print("❌ XML解析失败: 未找到对象")
        
        # 测试2: JSON格式的新类别处理
        print("\n📝 测试2: JSON格式的新类别处理")
        json_path = os.path.join(test_dir, "test.json")
        create_test_json(json_path, "new_class_json")
        
        # 创建测试图片 - 使用PIL创建一个真实的图片
        test_image = os.path.join(test_dir, "test.jpg")
        try:
            from PIL import Image
            img = Image.new('RGB', (640, 480), color='white')
            img.save(test_image)
        except ImportError:
            # 如果没有PIL，创建一个简单的占位文件
            with open(test_image, 'wb') as f:
                f.write(b'dummy')
        
        converter_json = PascalToYOLOConverter(
            source_dir=test_dir,
            target_dir=output_dir,
            dataset_name="test_json",
            use_class_config=True
        )
        
        width, height, objects = converter_json.parse_json_annotation(json_path, "test.jpg")
        if objects:
            print(f"✅ JSON解析成功: 找到 {len(objects)} 个对象")
            print(f"   类别ID: {objects[0][0]}")
        else:
            print("❌ JSON解析失败: 未找到对象")
        
        # 测试3: 验证两种格式使用相同的处理逻辑
        print("\n📝 测试3: 验证处理逻辑一致性")
        
        # 创建相同类别的XML和JSON
        same_class = "test_class"
        xml_path2 = os.path.join(test_dir, "test2.xml")
        json_path2 = os.path.join(test_dir, "test2.json")
        
        create_test_xml(xml_path2, same_class)
        create_test_json(json_path2, same_class)
        
        converter = PascalToYOLOConverter(
            source_dir=test_dir,
            target_dir=output_dir,
            dataset_name="test_unified",
            use_class_config=True
        )
        
        _, _, xml_objects = converter.parse_xml_annotation(xml_path2)
        _, _, json_objects = converter.parse_json_annotation(json_path2, "test.jpg")
        
        if xml_objects and json_objects:
            xml_class_id = xml_objects[0][0]
            json_class_id = json_objects[0][0]
            
            if xml_class_id == json_class_id:
                print(f"✅ 类别处理一致: XML和JSON都分配了相同的类别ID ({xml_class_id})")
            else:
                print(f"❌ 类别处理不一致: XML类别ID={xml_class_id}, JSON类别ID={json_class_id}")
        
        print("\n📊 统计信息:")
        print(f"   总类别数: {len(converter.classes)}")
        print(f"   类别列表: {converter.classes}")
        if converter.unknown_classes:
            print(f"   未知类别: {converter.unknown_classes}")
        
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_unified_processing()