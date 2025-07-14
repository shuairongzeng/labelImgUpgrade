#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试YOLO导出功能
"""
import os
import sys
import tempfile
import shutil
from xml.etree import ElementTree

# 添加libs目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from libs.pascal_to_yolo_converter import PascalToYOLOConverter

def create_test_xml(filename, width=640, height=480, objects=None):
    """创建测试用的Pascal VOC XML文件"""
    if objects is None:
        objects = [
            {'name': 'person', 'xmin': 100, 'ymin': 100, 'xmax': 200, 'ymax': 300},
            {'name': 'car', 'xmin': 300, 'ymin': 200, 'xmax': 500, 'ymax': 400}
        ]
    
    # 创建XML结构
    annotation = ElementTree.Element('annotation')
    
    # 文件名
    filename_elem = ElementTree.SubElement(annotation, 'filename')
    filename_elem.text = filename.replace('.xml', '.jpg')
    
    # 尺寸信息
    size = ElementTree.SubElement(annotation, 'size')
    width_elem = ElementTree.SubElement(size, 'width')
    width_elem.text = str(width)
    height_elem = ElementTree.SubElement(size, 'height')
    height_elem.text = str(height)
    depth_elem = ElementTree.SubElement(size, 'depth')
    depth_elem.text = '3'
    
    # 对象信息
    for obj in objects:
        object_elem = ElementTree.SubElement(annotation, 'object')
        
        name_elem = ElementTree.SubElement(object_elem, 'name')
        name_elem.text = obj['name']
        
        bndbox = ElementTree.SubElement(object_elem, 'bndbox')
        xmin_elem = ElementTree.SubElement(bndbox, 'xmin')
        xmin_elem.text = str(obj['xmin'])
        ymin_elem = ElementTree.SubElement(bndbox, 'ymin')
        ymin_elem.text = str(obj['ymin'])
        xmax_elem = ElementTree.SubElement(bndbox, 'xmax')
        xmax_elem.text = str(obj['xmax'])
        ymax_elem = ElementTree.SubElement(bndbox, 'ymax')
        ymax_elem.text = str(obj['ymax'])
    
    return annotation

def create_test_image(filename, width=640, height=480):
    """创建测试用的图片文件（空文件）"""
    with open(filename, 'wb') as f:
        # 创建一个简单的BMP文件头（最小的图片文件）
        # 这只是为了测试，实际上不是有效的图片
        f.write(b'BM')  # BMP signature
        f.write((54 + width * height * 3).to_bytes(4, 'little'))  # File size
        f.write(b'\x00\x00\x00\x00')  # Reserved
        f.write(b'\x36\x00\x00\x00')  # Offset to pixel data
        f.write(b'\x28\x00\x00\x00')  # Header size
        f.write(width.to_bytes(4, 'little'))  # Width
        f.write(height.to_bytes(4, 'little'))  # Height
        f.write(b'\x01\x00\x18\x00')  # Planes and bits per pixel
        f.write(b'\x00' * 24)  # Rest of header
        f.write(b'\x00' * (width * height * 3))  # Pixel data

def test_pascal_to_yolo_converter():
    """测试Pascal到YOLO转换器"""
    print("开始测试Pascal到YOLO转换器...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)
        
        # 创建测试数据
        test_files = [
            ("image1.xml", "image1.jpg"),
            ("image2.xml", "image2.jpg"),
            ("image3.xml", "image3.jpg"),
        ]
        
        for xml_file, img_file in test_files:
            # 创建XML文件
            xml_path = os.path.join(source_dir, xml_file)
            xml_tree = create_test_xml(xml_file)
            ElementTree.ElementTree(xml_tree).write(xml_path, encoding='utf-8', xml_declaration=True)
            
            # 创建对应的图片文件
            img_path = os.path.join(source_dir, img_file)
            create_test_image(img_path)
        
        print(f"创建了 {len(test_files)} 个测试文件")
        
        # 测试转换器
        converter = PascalToYOLOConverter(
            source_dir=source_dir,
            target_dir=target_dir,
            dataset_name="test_dataset",
            train_ratio=0.8
        )
        
        # 执行转换
        success, message = converter.convert()
        
        if success:
            print("✅ 转换成功!")
            print(f"转换信息: {message}")
            
            # 验证输出结构
            dataset_path = os.path.join(target_dir, "test_dataset")
            expected_dirs = [
                "images/train",
                "images/val", 
                "labels/train",
                "labels/val"
            ]
            
            for dir_path in expected_dirs:
                full_path = os.path.join(dataset_path, dir_path)
                if os.path.exists(full_path):
                    files = os.listdir(full_path)
                    print(f"✅ {dir_path}: {len(files)} 个文件")
                else:
                    print(f"❌ 缺少目录: {dir_path}")
            
            # 检查配置文件
            yaml_file = os.path.join(dataset_path, "data.yaml")
            classes_file = os.path.join(dataset_path, "classes.txt")
            
            if os.path.exists(yaml_file):
                print("✅ data.yaml 文件已生成")
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    print("YAML内容预览:")
                    print(f.read()[:200] + "...")
            else:
                print("❌ 缺少 data.yaml 文件")
            
            if os.path.exists(classes_file):
                print("✅ classes.txt 文件已生成")
                with open(classes_file, 'r', encoding='utf-8') as f:
                    classes = f.read().strip().split('\n')
                    print(f"类别列表: {classes}")
            else:
                print("❌ 缺少 classes.txt 文件")
            
            # 检查YOLO标注格式
            train_labels_dir = os.path.join(dataset_path, "labels/train")
            if os.path.exists(train_labels_dir):
                label_files = [f for f in os.listdir(train_labels_dir) if f.endswith('.txt')]
                if label_files:
                    sample_file = os.path.join(train_labels_dir, label_files[0])
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        print(f"✅ YOLO标注示例 ({label_files[0]}):")
                        print(content)
                        
                        # 验证格式
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) == 5:
                                    try:
                                        class_id = int(parts[0])
                                        coords = [float(x) for x in parts[1:]]
                                        if all(0 <= coord <= 1 for coord in coords):
                                            print(f"✅ 标注格式正确: class={class_id}, coords={coords}")
                                        else:
                                            print(f"❌ 坐标超出范围: {coords}")
                                    except ValueError:
                                        print(f"❌ 标注格式错误: {line}")
                                else:
                                    print(f"❌ 标注字段数量错误: {line}")
        else:
            print(f"❌ 转换失败: {message}")
            return False
    
    return True

def test_ui_integration():
    """测试UI集成"""
    print("\n开始测试UI集成...")
    
    try:
        # 测试导入
        from libs.yolo_export_dialog import YOLOExportDialog
        print("✅ YOLOExportDialog 导入成功")
        
        # 测试字符串资源
        from libs.stringBundle import StringBundle
        string_bundle = StringBundle.get_bundle()
        
        test_strings = [
            'exportYOLO',
            'exportYOLODetail', 
            'exportYOLODialog',
            'selectExportDir',
            'datasetName',
            'trainRatio',
            'exportProgress',
            'exportComplete',
            'exportSuccess',
            'noAnnotations'
        ]
        
        for string_id in test_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ 字符串资源 '{string_id}': {value}")
            except:
                print(f"❌ 缺少字符串资源: {string_id}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("YOLO导出功能测试")
    print("=" * 50)
    
    # 测试转换器
    converter_test = test_pascal_to_yolo_converter()
    
    # 测试UI集成
    ui_test = test_ui_integration()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"转换器测试: {'✅ 通过' if converter_test else '❌ 失败'}")
    print(f"UI集成测试: {'✅ 通过' if ui_test else '❌ 失败'}")
    
    if converter_test and ui_test:
        print("🎉 所有测试通过!")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
