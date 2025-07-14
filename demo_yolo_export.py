#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YOLO导出功能演示脚本
创建示例数据并演示导出功能
"""
import os
import sys
import tempfile
import shutil
from xml.etree import ElementTree

def create_demo_data():
    """创建演示数据"""
    print("创建演示数据...")
    
    # 创建临时目录
    demo_dir = os.path.join(os.getcwd(), "demo_data")
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    os.makedirs(demo_dir)
    
    # 示例数据
    demo_files = [
        {
            "image": "person_001.jpg",
            "xml": "person_001.xml",
            "width": 640,
            "height": 480,
            "objects": [
                {"name": "person", "xmin": 100, "ymin": 50, "xmax": 300, "ymax": 400},
                {"name": "bicycle", "xmin": 350, "ymin": 200, "xmax": 600, "ymax": 450}
            ]
        },
        {
            "image": "car_001.jpg", 
            "xml": "car_001.xml",
            "width": 800,
            "height": 600,
            "objects": [
                {"name": "car", "xmin": 150, "ymin": 100, "xmax": 650, "ymax": 500},
                {"name": "person", "xmin": 50, "ymin": 200, "xmax": 120, "ymax": 400}
            ]
        },
        {
            "image": "street_001.jpg",
            "xml": "street_001.xml", 
            "width": 1024,
            "height": 768,
            "objects": [
                {"name": "car", "xmin": 200, "ymin": 300, "xmax": 500, "ymax": 600},
                {"name": "car", "xmin": 600, "ymin": 250, "xmax": 900, "ymax": 550},
                {"name": "person", "xmin": 100, "ymin": 400, "xmax": 180, "ymax": 700},
                {"name": "traffic_light", "xmin": 50, "ymin": 50, "xmax": 100, "ymax": 200}
            ]
        }
    ]
    
    for file_info in demo_files:
        # 创建XML标注文件
        xml_path = os.path.join(demo_dir, file_info["xml"])
        create_pascal_xml(xml_path, file_info)
        
        # 创建虚拟图片文件
        img_path = os.path.join(demo_dir, file_info["image"])
        create_dummy_image(img_path, file_info["width"], file_info["height"])
        
        print(f"  创建: {file_info['image']} 和 {file_info['xml']}")
    
    print(f"演示数据已创建在: {demo_dir}")
    return demo_dir

def create_pascal_xml(xml_path, file_info):
    """创建Pascal VOC格式的XML文件"""
    annotation = ElementTree.Element('annotation')
    
    # 文件名
    filename = ElementTree.SubElement(annotation, 'filename')
    filename.text = file_info["image"]
    
    # 路径
    path = ElementTree.SubElement(annotation, 'path')
    path.text = os.path.join(os.path.dirname(xml_path), file_info["image"])
    
    # 源信息
    source = ElementTree.SubElement(annotation, 'source')
    database = ElementTree.SubElement(source, 'database')
    database.text = 'Unknown'
    
    # 尺寸信息
    size = ElementTree.SubElement(annotation, 'size')
    width = ElementTree.SubElement(size, 'width')
    width.text = str(file_info["width"])
    height = ElementTree.SubElement(size, 'height')
    height.text = str(file_info["height"])
    depth = ElementTree.SubElement(size, 'depth')
    depth.text = '3'
    
    # 分割信息
    segmented = ElementTree.SubElement(annotation, 'segmented')
    segmented.text = '0'
    
    # 对象信息
    for obj in file_info["objects"]:
        object_elem = ElementTree.SubElement(annotation, 'object')
        
        name = ElementTree.SubElement(object_elem, 'name')
        name.text = obj['name']
        
        pose = ElementTree.SubElement(object_elem, 'pose')
        pose.text = 'Unspecified'
        
        truncated = ElementTree.SubElement(object_elem, 'truncated')
        truncated.text = '0'
        
        difficult = ElementTree.SubElement(object_elem, 'difficult')
        difficult.text = '0'
        
        bndbox = ElementTree.SubElement(object_elem, 'bndbox')
        xmin = ElementTree.SubElement(bndbox, 'xmin')
        xmin.text = str(obj['xmin'])
        ymin = ElementTree.SubElement(bndbox, 'ymin')
        ymin.text = str(obj['ymin'])
        xmax = ElementTree.SubElement(bndbox, 'xmax')
        xmax.text = str(obj['xmax'])
        ymax = ElementTree.SubElement(bndbox, 'ymax')
        ymax.text = str(obj['ymax'])
    
    # 写入文件
    tree = ElementTree.ElementTree(annotation)
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)

def create_dummy_image(img_path, width, height):
    """创建虚拟图片文件（简单的BMP格式）"""
    # BMP文件头
    file_size = 54 + width * height * 3
    
    with open(img_path, 'wb') as f:
        # BMP文件头 (14字节)
        f.write(b'BM')  # 签名
        f.write(file_size.to_bytes(4, 'little'))  # 文件大小
        f.write(b'\x00\x00')  # 保留字段1
        f.write(b'\x00\x00')  # 保留字段2
        f.write(b'\x36\x00\x00\x00')  # 像素数据偏移
        
        # DIB头 (40字节)
        f.write(b'\x28\x00\x00\x00')  # DIB头大小
        f.write(width.to_bytes(4, 'little'))  # 图片宽度
        f.write(height.to_bytes(4, 'little'))  # 图片高度
        f.write(b'\x01\x00')  # 颜色平面数
        f.write(b'\x18\x00')  # 每像素位数 (24位)
        f.write(b'\x00\x00\x00\x00')  # 压缩方法
        f.write(b'\x00\x00\x00\x00')  # 图像大小
        f.write(b'\x13\x0B\x00\x00')  # 水平分辨率
        f.write(b'\x13\x0B\x00\x00')  # 垂直分辨率
        f.write(b'\x00\x00\x00\x00')  # 调色板颜色数
        f.write(b'\x00\x00\x00\x00')  # 重要颜色数
        
        # 像素数据 (简单的渐变)
        for y in range(height):
            for x in range(width):
                # 创建简单的渐变效果
                r = (x * 255) // width
                g = (y * 255) // height
                b = 128
                f.write(bytes([b, g, r]))  # BMP是BGR格式

def demo_conversion():
    """演示转换功能"""
    print("\n开始演示转换功能...")
    
    # 创建演示数据
    demo_dir = create_demo_data()
    
    try:
        # 导入转换器
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        
        # 创建输出目录
        output_dir = os.path.join(os.getcwd(), "yolo_output")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        
        # 创建转换器
        converter = PascalToYOLOConverter(
            source_dir=demo_dir,
            target_dir=output_dir,
            dataset_name="demo_dataset",
            train_ratio=0.7  # 70%训练，30%验证
        )
        
        print(f"\n转换配置:")
        print(f"  源目录: {demo_dir}")
        print(f"  输出目录: {output_dir}")
        print(f"  数据集名称: demo_dataset")
        print(f"  训练集比例: 70%")
        
        # 执行转换
        def progress_callback(current, total, message):
            print(f"  [{current:3d}%] {message}")
        
        print("\n开始转换...")
        success, message = converter.convert(progress_callback)
        
        if success:
            print(f"\n✅ 转换成功!")
            print(f"转换详情: {message}")
            
            # 显示输出结构
            dataset_path = os.path.join(output_dir, "demo_dataset")
            print(f"\n生成的数据集结构:")
            show_directory_tree(dataset_path)
            
            # 显示配置文件内容
            show_config_files(dataset_path)
            
        else:
            print(f"❌ 转换失败: {message}")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保所有依赖都已安装")
    except Exception as e:
        print(f"❌ 转换过程出错: {e}")

def show_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """显示目录树结构"""
    if current_depth > max_depth:
        return
        
    if not os.path.exists(path):
        return
        
    items = sorted(os.listdir(path))
    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item}")
        
        if os.path.isdir(item_path):
            next_prefix = prefix + ("    " if is_last else "│   ")
            show_directory_tree(item_path, next_prefix, max_depth, current_depth + 1)
        elif item.endswith(('.txt', '.yaml')):
            # 显示文件大小
            size = os.path.getsize(item_path)
            print(f"{prefix}{'    ' if is_last else '│   '}    ({size} bytes)")

def show_config_files(dataset_path):
    """显示配置文件内容"""
    print(f"\n配置文件内容:")
    
    # 显示classes.txt
    classes_file = os.path.join(dataset_path, "classes.txt")
    if os.path.exists(classes_file):
        print(f"\n📄 classes.txt:")
        with open(classes_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            for i, line in enumerate(content.split('\n')):
                print(f"  {i}: {line}")
    
    # 显示data.yaml
    yaml_file = os.path.join(dataset_path, "data.yaml")
    if os.path.exists(yaml_file):
        print(f"\n📄 data.yaml:")
        with open(yaml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip():
                    print(f"  {line}")
    
    # 显示示例YOLO标注
    train_labels = os.path.join(dataset_path, "labels", "train")
    if os.path.exists(train_labels):
        label_files = [f for f in os.listdir(train_labels) if f.endswith('.txt')]
        if label_files:
            sample_file = os.path.join(train_labels, label_files[0])
            print(f"\n📄 示例YOLO标注 ({label_files[0]}):")
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                for line in content.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) == 5:
                            class_id, x, y, w, h = parts
                            print(f"  类别{class_id}: 中心({x}, {y}) 尺寸({w}, {h})")

def main():
    """主函数"""
    print("=" * 60)
    print("YOLO导出功能演示")
    print("=" * 60)
    
    print("这个演示将:")
    print("1. 创建示例的Pascal VOC格式标注数据")
    print("2. 使用转换器将其转换为YOLO格式")
    print("3. 展示生成的数据集结构和配置文件")
    
    try:
        demo_conversion()
        
        print("\n" + "=" * 60)
        print("演示完成!")
        print("=" * 60)
        print("\n生成的文件:")
        print("- demo_data/: 演示用的Pascal VOC数据")
        print("- yolo_output/demo_dataset/: 转换后的YOLO数据集")
        print("\n您可以:")
        print("1. 查看生成的目录结构")
        print("2. 检查YOLO标注格式")
        print("3. 使用data.yaml进行YOLO模型训练")
        
    except Exception as e:
        print(f"\n❌ 演示过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
