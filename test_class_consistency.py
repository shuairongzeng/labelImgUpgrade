#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
类别顺序一致性测试
Class Order Consistency Test

测试修复后的YOLO转换器是否能确保类别顺序的一致性
"""

from libs.pascal_to_yolo_converter import PascalToYOLOConverter
from libs.class_manager import ClassConfigManager
import os
import sys
import tempfile
import shutil
import yaml
from datetime import datetime

# 禁用日志以避免多进程问题
import logging
logging.disable(logging.CRITICAL)

# 添加libs路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))


def create_test_xml_files(test_dir, classes_data):
    """创建测试用的XML文件"""
    xml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<annotation>
    <folder>test</folder>
    <filename>{filename}</filename>
    <size>
        <width>640</width>
        <height>480</height>
        <depth>3</depth>
    </size>
    <object>
        <name>{class_name}</name>
        <bndbox>
            <xmin>100</xmin>
            <ymin>100</ymin>
            <xmax>200</xmax>
            <ymax>200</ymax>
        </bndbox>
    </object>
</annotation>'''

    # 创建XML和图片文件
    for i, (filename, class_name) in enumerate(classes_data):
        # 创建XML文件
        xml_content = xml_template.format(
            filename=filename, class_name=class_name)
        xml_path = os.path.join(test_dir, f"{filename}.xml")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        # 创建对应的图片文件（空文件）
        img_path = os.path.join(test_dir, f"{filename}.jpg")
        with open(img_path, 'w') as f:
            f.write("")  # 空文件，仅用于测试


def test_class_config_manager():
    """测试类别配置管理器"""
    print("🧪 测试类别配置管理器...")

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = os.path.join(temp_dir, "configs")

        # 创建类别管理器
        manager = ClassConfigManager(config_dir)

        # 测试添加类别
        test_classes = ["person", "car", "bicycle", "dog", "cat"]
        for i, class_name in enumerate(test_classes):
            success = manager.add_class(class_name, f"测试类别 {i+1}")
            assert success, f"添加类别失败: {class_name}"

        # 保存配置
        success = manager.save_class_config()
        assert success, "保存配置失败"

        # 验证类别顺序
        classes = manager.get_class_list()
        assert classes == test_classes, f"类别顺序不正确: {classes} != {test_classes}"

        # 验证映射
        class_to_id = manager.get_class_to_id_mapping()
        expected_mapping = {name: idx for idx, name in enumerate(test_classes)}
        assert class_to_id == expected_mapping, f"类别映射不正确: {class_to_id}"

        print("✅ 类别配置管理器测试通过")
        return True


def test_converter_consistency():
    """测试转换器的一致性"""
    print("🧪 测试转换器类别顺序一致性...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 设置测试目录
        source_dir = os.path.join(temp_dir, "source")
        output_dir = os.path.join(temp_dir, "output")
        config_dir = os.path.join(temp_dir, "configs")

        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # 创建测试数据 - 故意使用不同的顺序
        test_data_1 = [
            ("img1", "dog"),
            ("img2", "car"),
            ("img3", "person"),
            ("img4", "bicycle")
        ]

        test_data_2 = [
            ("img5", "bicycle"),
            ("img6", "person"),
            ("img7", "dog"),
            ("img8", "car")
        ]

        # 第一次转换
        print("📋 第一次转换...")
        create_test_xml_files(source_dir, test_data_1)

        converter1 = PascalToYOLOConverter(
            source_dir=source_dir,
            target_dir=output_dir,
            dataset_name="test_dataset_1",
            use_class_config=True,
            class_config_dir=config_dir
        )

        success1, report1 = converter1.convert()
        assert success1, f"第一次转换失败: {report1}"

        # 获取第一次转换的类别信息
        stats1 = converter1.get_class_statistics()
        classes1 = stats1['classes']
        class_to_id1 = stats1['class_to_id']

        print(f"第一次转换类别: {classes1}")
        print(f"第一次转换映射: {class_to_id1}")

        # 清理源目录，准备第二次转换
        for file in os.listdir(source_dir):
            os.remove(os.path.join(source_dir, file))

        # 第二次转换 - 使用不同的数据顺序
        print("📋 第二次转换...")
        create_test_xml_files(source_dir, test_data_2)

        converter2 = PascalToYOLOConverter(
            source_dir=source_dir,
            target_dir=output_dir,
            dataset_name="test_dataset_2",
            use_class_config=True,
            class_config_dir=config_dir
        )

        success2, report2 = converter2.convert()
        assert success2, f"第二次转换失败: {report2}"

        # 获取第二次转换的类别信息
        stats2 = converter2.get_class_statistics()
        classes2 = stats2['classes']
        class_to_id2 = stats2['class_to_id']

        print(f"第二次转换类别: {classes2}")
        print(f"第二次转换映射: {class_to_id2}")

        # 验证一致性
        assert classes1 == classes2, f"类别顺序不一致: {classes1} != {classes2}"
        assert class_to_id1 == class_to_id2, f"类别映射不一致: {class_to_id1} != {class_to_id2}"

        print("✅ 转换器一致性测试通过")
        return True


def test_data_yaml_consistency():
    """测试data.yaml文件的一致性"""
    print("🧪 测试data.yaml文件一致性...")

    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "source")
        output_dir = os.path.join(temp_dir, "output")
        config_dir = os.path.join(temp_dir, "configs")

        os.makedirs(source_dir, exist_ok=True)

        # 创建测试数据
        test_data = [
            ("img1", "zebra"),
            ("img2", "apple"),
            ("img3", "mouse"),
            ("img4", "book")
        ]

        create_test_xml_files(source_dir, test_data)

        # 执行多次转换
        yaml_configs = []
        for i in range(3):
            print(f"📋 第 {i+1} 次转换...")

            converter = PascalToYOLOConverter(
                source_dir=source_dir,
                target_dir=output_dir,
                dataset_name=f"test_dataset_{i+1}",
                use_class_config=True,
                class_config_dir=config_dir
            )

            success, report = converter.convert()
            assert success, f"第 {i+1} 次转换失败: {report}"

            # 读取生成的data.yaml文件
            yaml_path = os.path.join(
                output_dir, f"test_dataset_{i+1}", "data.yaml")
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            yaml_configs.append(config)
            print(f"第 {i+1} 次转换的类别映射: {config['names']}")

        # 验证所有data.yaml文件的类别映射都相同
        base_names = yaml_configs[0]['names']
        for i, config in enumerate(yaml_configs[1:], 1):
            assert config['names'] == base_names, \
                f"第 {i+1} 次转换的类别映射与第1次不一致: {config['names']} != {base_names}"

        print("✅ data.yaml文件一致性测试通过")
        return True


def test_unknown_class_handling():
    """测试未知类别处理"""
    print("🧪 测试未知类别处理...")

    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "source")
        output_dir = os.path.join(temp_dir, "output")
        config_dir = os.path.join(temp_dir, "configs")

        os.makedirs(source_dir, exist_ok=True)

        # 先创建类别配置
        manager = ClassConfigManager(config_dir)
        manager.add_class("person", "人")
        manager.add_class("car", "汽车")
        manager.save_class_config()

        # 创建包含未知类别的测试数据
        test_data = [
            ("img1", "person"),    # 已知类别
            ("img2", "car"),       # 已知类别
            ("img3", "unknown1"),  # 未知类别
            ("img4", "unknown2")   # 未知类别
        ]

        create_test_xml_files(source_dir, test_data)

        # 执行转换
        converter = PascalToYOLOConverter(
            source_dir=source_dir,
            target_dir=output_dir,
            dataset_name="test_unknown",
            use_class_config=True,
            class_config_dir=config_dir
        )

        success, report = converter.convert()
        assert success, f"转换失败: {report}"

        # 检查未知类别是否被正确记录
        stats = converter.get_class_statistics()
        unknown_classes = stats['unknown_classes']

        expected_unknown = ["unknown1", "unknown2"]
        assert set(unknown_classes) == set(expected_unknown), \
            f"未知类别记录不正确: {unknown_classes} != {expected_unknown}"

        print(f"✅ 未知类别处理测试通过，发现未知类别: {unknown_classes}")
        return True


def main():
    """主测试函数"""
    print("🚀 开始类别顺序一致性测试...")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("类别配置管理器", test_class_config_manager),
        ("转换器一致性", test_converter_consistency),
        ("data.yaml一致性", test_data_yaml_consistency),
        ("未知类别处理", test_unknown_class_handling)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"🧪 测试: {test_name}")
            print(f"{'='*50}")

            result = test_func()
            if result:
                print(f"✅ {test_name} - 通过")
                passed += 1
            else:
                print(f"❌ {test_name} - 失败")
                failed += 1

        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"📊 测试结果汇总")
    print(f"{'='*50}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")

    if failed == 0:
        print("🎉 所有测试都通过了！类别顺序一致性修复成功！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
