#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的YAML配置生成功能
"""

import os
import sys
import yaml
import tempfile
import shutil

def test_yaml_generation():
    """测试修改后的YAML配置生成功能"""
    print("🧪 测试修改后的YAML配置生成功能...")
    
    # 添加libs目录到Python路径
    libs_path = os.path.join(os.path.dirname(__file__), 'libs')
    if libs_path not in sys.path:
        sys.path.insert(0, libs_path)
    
    try:
        from pascal_to_yolo_converter import PascalToYOLOConverter
        print("✅ 成功导入PascalToYOLOConverter")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="yolo_test_")
    print(f"📁 创建测试目录: {test_dir}")
    
    try:
        # 创建测试数据集目录结构
        dataset_name = "test_dataset"
        target_dir = test_dir
        
        # 创建转换器实例
        converter = PascalToYOLOConverter(
            source_dir=test_dir,  # 源目录（这里只是为了测试）
            target_dir=target_dir,
            dataset_name=dataset_name,
            train_ratio=0.8
        )
        
        # 添加一些测试类别
        converter.classes = ['class1', 'class2', 'class3']
        converter.class_to_id = {'class1': 0, 'class2': 1, 'class3': 2}
        
        print(f"🏷️ 测试类别: {converter.classes}")
        
        # 创建数据集目录
        dataset_path = os.path.join(target_dir, dataset_name)
        os.makedirs(dataset_path, exist_ok=True)
        
        # 设置转换器的数据集路径
        converter.dataset_path = dataset_path
        
        print(f"📂 数据集路径: {dataset_path}")
        
        # 生成YAML配置
        print("🔧 生成YAML配置文件...")
        success = converter.generate_yaml_config()
        
        if not success:
            print("❌ YAML配置生成失败")
            return False
        
        # 读取生成的配置文件
        yaml_file = os.path.join(dataset_path, "data.yaml")
        if not os.path.exists(yaml_file):
            print(f"❌ 配置文件不存在: {yaml_file}")
            return False
        
        print(f"📄 配置文件路径: {yaml_file}")
        
        # 解析配置文件
        with open(yaml_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("\n📋 生成的配置内容:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # 验证配置
        path_value = config.get('path')
        if not path_value:
            print("❌ 缺少path字段")
            return False
        
        # 检查是否使用了绝对路径
        if not os.path.isabs(path_value):
            print(f"❌ path字段不是绝对路径: {path_value}")
            return False
        
        print(f"✅ path字段使用绝对路径: {path_value}")
        
        # 验证路径是否正确
        expected_path = os.path.abspath(dataset_path)
        if path_value != expected_path:
            print(f"❌ path路径不匹配:")
            print(f"  期望: {expected_path}")
            print(f"  实际: {path_value}")
            return False
        
        print("✅ path路径匹配正确")
        
        # 验证其他字段
        if config.get('train') != 'images/train':
            print(f"❌ train字段错误: {config.get('train')}")
            return False
        
        if config.get('val') != 'images/val':
            print(f"❌ val字段错误: {config.get('val')}")
            return False
        
        names = config.get('names')
        if not names or len(names) != 3:
            print(f"❌ names字段错误: {names}")
            return False
        
        expected_names = {0: 'class1', 1: 'class2', 2: 'class3'}
        if names != expected_names:
            print(f"❌ names内容不匹配:")
            print(f"  期望: {expected_names}")
            print(f"  实际: {names}")
            return False
        
        print("✅ 所有字段验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试目录
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 清理测试目录: {test_dir}")
        except Exception as e:
            print(f"⚠️ 清理测试目录失败: {e}")

def main():
    """主函数"""
    print("🚀 开始测试YAML配置生成修复...")
    
    success = test_yaml_generation()
    
    if success:
        print("\n🎉 测试通过！修改后的YAML配置生成功能正常工作")
        print("💡 现在一键配置功能将生成使用绝对路径的data.yaml文件")
    else:
        print("\n❌ 测试失败！需要进一步检查修改")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
