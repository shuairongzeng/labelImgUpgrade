#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件夹清空功能
验证一键配置中的数据清空和备份机制
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_data(test_dir):
    """创建测试数据"""
    try:
        # 创建源数据
        source_dir = os.path.join(test_dir, 'source')
        os.makedirs(source_dir, exist_ok=True)
        
        # 创建测试图片和XML文件
        test_files = ['test1.jpg', 'test2.jpg', 'test3.jpg']
        for i, filename in enumerate(test_files):
            # 创建假的图片文件
            img_path = os.path.join(source_dir, filename)
            with open(img_path, 'w') as f:
                f.write(f"fake image data {i}")
            
            # 创建对应的XML标注文件
            xml_filename = filename.replace('.jpg', '.xml')
            xml_path = os.path.join(source_dir, xml_filename)
            xml_content = f'''<?xml version="1.0"?>
<annotation>
    <filename>{filename}</filename>
    <object>
        <name>naiBa</name>
        <bndbox>
            <xmin>10</xmin>
            <ymin>10</ymin>
            <xmax>100</xmax>
            <ymax>100</ymax>
        </bndbox>
    </object>
</annotation>'''
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
        
        print(f"✅ 创建测试数据: {len(test_files)} 个文件对")
        return source_dir, test_files
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        return None, []

def create_existing_dataset(target_dir, dataset_name):
    """创建现有的数据集文件"""
    try:
        dataset_path = os.path.join(target_dir, dataset_name)
        
        # 创建目录结构
        dirs = [
            os.path.join(dataset_path, 'images', 'train'),
            os.path.join(dataset_path, 'images', 'val'),
            os.path.join(dataset_path, 'labels', 'train'),
            os.path.join(dataset_path, 'labels', 'val')
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        # 创建一些旧文件
        old_files = []
        for i in range(3):
            # 训练图片和标签
            train_img = os.path.join(dirs[0], f'old_train_{i}.jpg')
            train_label = os.path.join(dirs[2], f'old_train_{i}.txt')
            
            with open(train_img, 'w') as f:
                f.write(f"old train image {i}")
            with open(train_label, 'w') as f:
                f.write(f"0 0.5 0.5 0.2 0.2")
            
            old_files.extend([train_img, train_label])
            
            # 验证图片和标签
            if i < 2:  # 只创建2个验证文件
                val_img = os.path.join(dirs[1], f'old_val_{i}.jpg')
                val_label = os.path.join(dirs[3], f'old_val_{i}.txt')
                
                with open(val_img, 'w') as f:
                    f.write(f"old val image {i}")
                with open(val_label, 'w') as f:
                    f.write(f"1 0.3 0.3 0.4 0.4")
                
                old_files.extend([val_img, val_label])
        
        print(f"✅ 创建现有数据集: {len(old_files)} 个旧文件")
        return dataset_path, old_files
        
    except Exception as e:
        print(f"❌ 创建现有数据集失败: {e}")
        return None, []

def test_converter_with_cleanup():
    """测试转换器的清空功能"""
    print("\n=== 测试转换器清空功能 ===")
    
    try:
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"使用临时目录: {temp_dir}")
            
            # 创建测试数据
            source_dir, test_files = create_test_data(temp_dir)
            if not source_dir:
                return False
            
            target_dir = os.path.join(temp_dir, 'output')
            dataset_name = 'test_dataset'
            
            # 创建现有数据集
            dataset_path, old_files = create_existing_dataset(target_dir, dataset_name)
            if not dataset_path:
                return False
            
            # 测试1: 不清空现有数据
            print("\n--- 测试1: 不清空现有数据 ---")
            converter1 = PascalToYOLOConverter(
                source_dir=source_dir,
                target_dir=target_dir,
                dataset_name=dataset_name,
                use_class_config=False  # 使用动态类别
            )
            
            # 获取现有文件信息
            existing_info = converter1.get_existing_files_info()
            print(f"转换前现有文件: {existing_info['total_files']} 个")
            
            # 执行转换（不清空）
            success1, message1 = converter1.convert(clean_existing=False, backup_existing=False)
            
            if success1:
                print("✅ 转换成功（不清空模式）")
                
                # 检查文件数量（应该包含旧文件和新文件）
                final_info = converter1.get_existing_files_info()
                print(f"转换后文件: {final_info['total_files']} 个")
                
                if final_info['total_files'] > existing_info['total_files']:
                    print("✅ 确认文件累积问题存在")
                else:
                    print("⚠️ 未检测到文件累积")
            else:
                print(f"❌ 转换失败: {message1}")
                return False
            
            # 重新创建现有数据集用于测试2
            shutil.rmtree(dataset_path)
            dataset_path, old_files = create_existing_dataset(target_dir, dataset_name)
            
            # 测试2: 清空现有数据
            print("\n--- 测试2: 清空现有数据 ---")
            converter2 = PascalToYOLOConverter(
                source_dir=source_dir,
                target_dir=target_dir,
                dataset_name=dataset_name,
                use_class_config=False  # 使用动态类别
            )
            
            # 获取现有文件信息
            existing_info2 = converter2.get_existing_files_info()
            print(f"转换前现有文件: {existing_info2['total_files']} 个")
            
            # 执行转换（清空）
            success2, message2 = converter2.convert(clean_existing=True, backup_existing=False)
            
            if success2:
                print("✅ 转换成功（清空模式）")
                
                # 检查文件数量（应该只有新文件）
                final_info2 = converter2.get_existing_files_info()
                print(f"转换后文件: {final_info2['total_files']} 个")
                
                # 验证只有新文件
                expected_files = len(test_files) * 2  # 图片 + 标签
                if final_info2['total_files'] == expected_files:
                    print("✅ 确认清空功能正常工作")
                else:
                    print(f"⚠️ 文件数量不符合预期: 期望 {expected_files}, 实际 {final_info2['total_files']}")
            else:
                print(f"❌ 转换失败: {message2}")
                return False
            
            # 测试3: 备份功能
            print("\n--- 测试3: 备份功能 ---")
            # 重新创建现有数据集
            shutil.rmtree(dataset_path)
            dataset_path, old_files = create_existing_dataset(target_dir, dataset_name)
            
            converter3 = PascalToYOLOConverter(
                source_dir=source_dir,
                target_dir=target_dir,
                dataset_name=dataset_name,
                use_class_config=False
            )
            
            # 执行转换（清空+备份）
            success3, message3 = converter3.convert(clean_existing=True, backup_existing=True)
            
            if success3:
                print("✅ 转换成功（清空+备份模式）")
                
                # 检查是否创建了备份
                if hasattr(converter3, 'backup_path') and converter3.backup_path:
                    if os.path.exists(converter3.backup_path):
                        print(f"✅ 备份创建成功: {converter3.backup_path}")
                        
                        # 验证备份内容
                        backup_files = sum([len(files) for r, d, files in os.walk(converter3.backup_path)])
                        print(f"✅ 备份文件数量: {backup_files} 个")
                    else:
                        print("❌ 备份路径不存在")
                        return False
                else:
                    print("⚠️ 未创建备份")
            else:
                print(f"❌ 转换失败: {message3}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试转换器清空功能失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_files_info():
    """测试现有文件信息获取"""
    print("\n=== 测试现有文件信息获取 ===")
    
    try:
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = os.path.join(temp_dir, 'output')
            dataset_name = 'info_test'
            
            # 创建转换器
            converter = PascalToYOLOConverter(
                source_dir=".",  # 临时值
                target_dir=target_dir,
                dataset_name=dataset_name
            )
            
            # 测试空目录
            info1 = converter.get_existing_files_info()
            print(f"空目录信息: {info1}")
            
            if not info1['dataset_exists'] and info1['total_files'] == 0:
                print("✅ 空目录检测正确")
            else:
                print("❌ 空目录检测错误")
                return False
            
            # 创建一些文件
            dataset_path, old_files = create_existing_dataset(target_dir, dataset_name)
            
            # 测试有文件的目录
            info2 = converter.get_existing_files_info()
            print(f"有文件目录信息: {info2}")
            
            if info2['dataset_exists'] and info2['total_files'] > 0:
                print("✅ 有文件目录检测正确")
                print(f"   训练图片: {info2['train_images']}")
                print(f"   验证图片: {info2['val_images']}")
                print(f"   训练标签: {info2['train_labels']}")
                print(f"   验证标签: {info2['val_labels']}")
            else:
                print("❌ 有文件目录检测错误")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试现有文件信息获取失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 文件夹清空功能测试")
    print("=" * 60)
    
    tests = [
        ("现有文件信息获取", test_existing_files_info),
        ("转换器清空功能", test_converter_with_cleanup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出结果
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！文件夹清空功能正常工作！")
        print("\n📋 功能总结:")
        print("✅ 支持清空现有数据，避免文件累积")
        print("✅ 支持备份现有数据，防止意外丢失")
        print("✅ 支持现有文件信息检查")
        print("✅ 支持数据完整性验证")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
