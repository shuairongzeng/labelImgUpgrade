#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据集路径调试测试脚本

测试数据集配置文件的路径解析逻辑
"""

import os
import sys
import yaml
from pathlib import Path

def test_dataset_path_resolution():
    """测试数据集路径解析"""
    print("🔍 测试数据集路径解析")
    print("=" * 50)
    
    # 测试配置文件路径
    config_file = "datasets/training_dataset/data.yaml"
    
    print(f"📁 配置文件路径: {config_file}")
    print(f"📂 当前工作目录: {os.getcwd()}")
    print(f"✅ 配置文件存在: {os.path.exists(config_file)}")
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在，无法继续测试")
        return False
    
    # 读取配置文件
    print("\n📋 读取配置文件内容:")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # 解析路径
    print("\n🔗 路径解析过程:")
    
    config_path = Path(config_file)
    config_dir = config_path.parent
    print(f"📂 配置文件目录: {config_dir.absolute()}")
    
    # 处理path字段
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ 数据集path字段: {dataset_base_path}")
        
        if not os.path.isabs(dataset_base_path):
            dataset_base_path = config_dir / dataset_base_path
            print(f"🔗 解析后的绝对路径: {dataset_base_path.absolute()}")
        
        dataset_base_path = Path(dataset_base_path)
    else:
        dataset_base_path = config_dir
        print("📁 使用配置文件目录作为基础路径")
    
    print(f"📍 最终基础路径: {dataset_base_path.absolute()}")
    
    # 构建训练和验证路径
    train_relative = config.get('train', '')
    val_relative = config.get('val', '')
    
    print(f"\n🚂 训练数据相对路径: {train_relative}")
    print(f"✅ 验证数据相对路径: {val_relative}")
    
    train_path = dataset_base_path / train_relative
    val_path = dataset_base_path / val_relative
    
    print(f"🚂 训练数据绝对路径: {train_path.absolute()}")
    print(f"✅ 验证数据绝对路径: {val_path.absolute()}")
    
    # 检查路径是否存在
    print(f"\n📊 路径存在性检查:")
    print(f"🚂 训练路径存在: {train_path.exists()}")
    print(f"✅ 验证路径存在: {val_path.exists()}")
    
    if train_path.exists():
        train_images = list(train_path.glob("*.jpg")) + list(train_path.glob("*.png")) + list(train_path.glob("*.jpeg"))
        print(f"📊 训练图片数量: {len(train_images)}")
        if len(train_images) > 0:
            print(f"📷 示例图片: {train_images[0].name}")
    
    if val_path.exists():
        val_images = list(val_path.glob("*.jpg")) + list(val_path.glob("*.png")) + list(val_path.glob("*.jpeg"))
        print(f"📊 验证图片数量: {len(val_images)}")
        if len(val_images) > 0:
            print(f"📷 示例图片: {val_images[0].name}")
    
    return True

def test_different_working_directories():
    """测试不同工作目录下的路径解析"""
    print("\n🔄 测试不同工作目录")
    print("=" * 50)
    
    original_cwd = os.getcwd()
    print(f"📂 原始工作目录: {original_cwd}")
    
    # 测试场景1：在项目根目录
    config_file = "datasets/training_dataset/data.yaml"
    if os.path.exists(config_file):
        print(f"\n✅ 场景1 - 项目根目录: {original_cwd}")
        print(f"📁 配置文件: {config_file}")
        print(f"🔗 绝对路径: {os.path.abspath(config_file)}")
    
    # 测试场景2：在datasets目录
    datasets_dir = os.path.join(original_cwd, "datasets")
    if os.path.exists(datasets_dir):
        try:
            os.chdir(datasets_dir)
            print(f"\n✅ 场景2 - datasets目录: {os.getcwd()}")
            
            config_file2 = "training_dataset/data.yaml"
            if os.path.exists(config_file2):
                print(f"📁 配置文件: {config_file2}")
                print(f"🔗 绝对路径: {os.path.abspath(config_file2)}")
        finally:
            os.chdir(original_cwd)
    
    # 测试场景3：在training_dataset目录
    training_dir = os.path.join(original_cwd, "datasets", "training_dataset")
    if os.path.exists(training_dir):
        try:
            os.chdir(training_dir)
            print(f"\n✅ 场景3 - training_dataset目录: {os.getcwd()}")
            
            config_file3 = "data.yaml"
            if os.path.exists(config_file3):
                print(f"📁 配置文件: {config_file3}")
                print(f"🔗 绝对路径: {os.path.abspath(config_file3)}")
        finally:
            os.chdir(original_cwd)

def main():
    """主函数"""
    print("🧪 数据集路径调试测试")
    print("=" * 60)
    
    try:
        # 测试基本路径解析
        success1 = test_dataset_path_resolution()
        
        # 测试不同工作目录
        test_different_working_directories()
        
        print("\n" + "=" * 60)
        if success1:
            print("✅ 路径解析测试完成")
            print("\n💡 调试建议:")
            print("1. 检查训练日志中的路径解析过程")
            print("2. 确认数据集配置文件中的path字段是否正确")
            print("3. 验证训练和验证数据目录是否存在")
            print("4. 检查图片文件是否在正确的目录中")
        else:
            print("❌ 路径解析测试失败")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
