#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
固定类别顺序功能演示
Fixed Class Order Feature Demo

演示修复后的YOLO转换器如何确保类别顺序一致性
"""

import os
import sys
import tempfile
import yaml
from datetime import datetime

def create_demo_data():
    """创建演示数据"""
    print("📋 创建演示数据...")
    
    # XML模板
    xml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<annotation>
    <folder>demo</folder>
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
    
    # 创建不同顺序的测试数据
    demo_data_sets = [
        # 数据集1：按字母顺序
        [("img1", "apple"), ("img2", "banana"), ("img3", "cherry"), ("img4", "dog")],
        # 数据集2：随机顺序
        [("img5", "dog"), ("img6", "apple"), ("img7", "cherry"), ("img8", "banana")],
        # 数据集3：反向顺序
        [("img9", "dog"), ("img10", "cherry"), ("img11", "banana"), ("img12", "apple")]
    ]
    
    return demo_data_sets, xml_template


def create_test_files(source_dir, data_set, xml_template):
    """创建测试文件"""
    os.makedirs(source_dir, exist_ok=True)
    
    for filename, class_name in data_set:
        # 创建XML文件
        xml_content = xml_template.format(filename=filename, class_name=class_name)
        xml_path = os.path.join(source_dir, f"{filename}.xml")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # 创建对应的图片文件（空文件）
        img_path = os.path.join(source_dir, f"{filename}.jpg")
        with open(img_path, 'w') as f:
            f.write("")


def demo_old_vs_new():
    """演示旧版本vs新版本的差异"""
    print("🚀 演示：旧版本 vs 新版本的类别顺序处理")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建演示数据
    demo_data_sets, xml_template = create_demo_data()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📂 临时目录: {temp_dir}")
        
        # 演示旧版本的问题
        print(f"\n{'='*60}")
        print("❌ 旧版本问题演示（动态类别添加）")
        print(f"{'='*60}")
        
        old_results = []
        for i, data_set in enumerate(demo_data_sets, 1):
            print(f"\n📋 数据集 {i} 的类别遇到顺序:")
            classes_encountered = []
            for filename, class_name in data_set:
                if class_name not in classes_encountered:
                    classes_encountered.append(class_name)
            
            print(f"   遇到顺序: {classes_encountered}")
            class_mapping = {name: idx for idx, name in enumerate(classes_encountered)}
            print(f"   类别映射: {class_mapping}")
            old_results.append((classes_encountered, class_mapping))
        
        # 显示问题
        print(f"\n⚠️ 问题分析:")
        base_classes, base_mapping = old_results[0]
        for i, (classes, mapping) in enumerate(old_results[1:], 2):
            if classes != base_classes or mapping != base_mapping:
                print(f"   数据集{i}的类别顺序与数据集1不同！")
                print(f"   数据集1: {base_mapping}")
                print(f"   数据集{i}: {mapping}")
        
        # 演示新版本的解决方案
        print(f"\n{'='*60}")
        print("✅ 新版本解决方案（固定类别配置）")
        print(f"{'='*60}")
        
        # 显示固定配置
        config_classes = ["apple", "banana", "cherry", "dog"]  # 固定顺序
        fixed_mapping = {name: idx for idx, name in enumerate(config_classes)}
        
        print(f"📋 固定类别配置:")
        print(f"   类别顺序: {config_classes}")
        print(f"   类别映射: {fixed_mapping}")
        
        print(f"\n🔄 所有数据集转换结果:")
        for i in range(len(demo_data_sets)):
            print(f"   数据集{i+1}: {fixed_mapping} ✅ (完全一致)")


def demo_with_real_converter():
    """使用真实转换器进行演示"""
    print(f"\n{'='*60}")
    print("🧪 真实转换器演示")
    print(f"{'='*60}")
    
    try:
        # 添加libs路径
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        
        demo_data_sets, xml_template = create_demo_data()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = os.path.join(temp_dir, "configs")
            os.makedirs(config_dir, exist_ok=True)
            
            # 创建演示用的类别配置
            demo_config = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'description': '演示用固定类别配置',
                'classes': ['apple', 'banana', 'cherry', 'dog'],
                'class_metadata': {},
                'settings': {
                    'auto_sort': False,
                    'case_sensitive': True,
                    'allow_duplicates': False,
                    'validation_strict': True
                }
            }
            
            config_file = os.path.join(config_dir, "class_config.yaml")
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(demo_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"📋 创建演示配置: {config_file}")
            print(f"🏷️ 固定类别顺序: {demo_config['classes']}")
            
            # 使用不同数据集进行多次转换
            conversion_results = []
            
            for i, data_set in enumerate(demo_data_sets, 1):
                print(f"\n🔄 第 {i} 次转换...")
                
                source_dir = os.path.join(temp_dir, f"source_{i}")
                output_dir = os.path.join(temp_dir, f"output_{i}")
                
                # 创建测试文件
                create_test_files(source_dir, data_set, xml_template)
                
                # 创建转换器
                converter = PascalToYOLOConverter(
                    source_dir=source_dir,
                    target_dir=output_dir,
                    dataset_name=f"demo_dataset_{i}",
                    use_class_config=True,
                    class_config_dir=config_dir
                )
                
                # 执行转换
                success, report = converter.convert()
                
                if success:
                    # 读取生成的data.yaml
                    yaml_path = os.path.join(output_dir, f"demo_dataset_{i}", "data.yaml")
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f)
                    
                    names = yaml_config.get('names', {})
                    conversion_results.append(names)
                    
                    print(f"   ✅ 转换成功")
                    print(f"   📄 生成的类别映射: {names}")
                else:
                    print(f"   ❌ 转换失败: {report}")
            
            # 验证一致性
            print(f"\n🔍 一致性验证:")
            if len(conversion_results) > 1:
                base_result = conversion_results[0]
                all_consistent = True
                
                for i, result in enumerate(conversion_results[1:], 2):
                    if result == base_result:
                        print(f"   转换 {i} vs 转换 1: ✅ 一致")
                    else:
                        print(f"   转换 {i} vs 转换 1: ❌ 不一致")
                        all_consistent = False
                
                if all_consistent:
                    print(f"\n🎉 所有转换结果完全一致！类别顺序问题已解决！")
                else:
                    print(f"\n⚠️ 发现不一致，需要进一步检查")
            
    except ImportError as e:
        print(f"❌ 无法导入转换器模块: {e}")
        print("请确保libs目录存在且包含必要的模块")
    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")


def show_benefits():
    """展示修复的好处"""
    print(f"\n{'='*60}")
    print("🎯 修复带来的好处")
    print(f"{'='*60}")
    
    benefits = [
        ("训练一致性", "每次训练使用相同的类别ID映射，确保模型训练结果可重现"),
        ("预测准确性", "模型预测的类别ID始终对应正确的类别名称"),
        ("增量训练", "可以在现有模型基础上继续训练，不会出现类别映射错乱"),
        ("模型部署", "生产环境中的类别解释始终正确，避免预测结果错误"),
        ("团队协作", "团队成员使用相同的类别配置，避免因顺序不同导致的问题"),
        ("版本控制", "类别配置可以版本化管理，便于追踪和回滚")
    ]
    
    for i, (title, desc) in enumerate(benefits, 1):
        print(f"{i}. **{title}**")
        print(f"   {desc}")
        print()


def main():
    """主演示函数"""
    print("🎬 YOLO类别顺序一致性修复功能演示")
    print("=" * 80)
    
    # 演示问题和解决方案对比
    demo_old_vs_new()
    
    # 使用真实转换器演示
    demo_with_real_converter()
    
    # 展示修复的好处
    show_benefits()
    
    print(f"\n{'='*80}")
    print("📋 总结")
    print(f"{'='*80}")
    print("✅ 问题：原有转换器的动态类别添加导致顺序不一致")
    print("✅ 解决：实现固定类别配置管理系统")
    print("✅ 效果：确保每次转换的类别ID映射完全一致")
    print("✅ 工具：提供验证、修复、配置管理等完整工具链")
    
    print(f"\n🚀 现在可以放心使用YOLO转换器进行训练了！")


if __name__ == "__main__":
    main()
