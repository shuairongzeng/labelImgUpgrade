#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试YAML配置生成
"""

import os
import yaml

def test_simple_yaml_generation():
    """简单测试YAML配置生成"""
    print("🧪 简单测试YAML配置生成...")
    
    # 模拟数据集路径
    dataset_path = "datasets/training_dataset"
    dataset_abs_path = os.path.abspath(dataset_path)
    
    print(f"📂 数据集相对路径: {dataset_path}")
    print(f"📂 数据集绝对路径: {dataset_abs_path}")
    
    # 创建配置（模拟修改后的逻辑）
    config = {
        'path': dataset_abs_path,  # 使用绝对路径
        'train': "images/train",   # 相对于path字段的路径
        'val': "images/val",       # 相对于path字段的路径
        'test': None,
        'names': {0: 'class1', 1: 'class2', 2: 'class3'}
    }
    
    print("\n📋 生成的配置:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # 验证路径
    if os.path.isabs(config['path']):
        print("✅ path字段使用绝对路径")
    else:
        print("❌ path字段不是绝对路径")
        return False
    
    # 检查路径是否存在
    if os.path.exists(config['path']):
        print("✅ path路径存在")
    else:
        print("❌ path路径不存在")
        return False
    
    # 检查train和val路径
    train_full_path = os.path.join(config['path'], config['train'])
    val_full_path = os.path.join(config['path'], config['val'])
    
    print(f"🚂 完整训练路径: {train_full_path}")
    print(f"✅ 完整验证路径: {val_full_path}")
    
    if os.path.exists(train_full_path):
        print("✅ 训练路径存在")
    else:
        print("❌ 训练路径不存在")
        return False
    
    if os.path.exists(val_full_path):
        print("✅ 验证路径存在")
    else:
        print("❌ 验证路径不存在")
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_yaml_generation()
    if success:
        print("\n🎉 简单测试通过！")
    else:
        print("\n❌ 简单测试失败！")
