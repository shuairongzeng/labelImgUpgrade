#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证数据集路径修复是否成功
"""

import os
import yaml

def verify_path_fix():
    """验证路径修复"""
    print("🔍 验证数据集路径修复")
    print("=" * 50)
    
    # 配置文件路径
    config_file = "datasets/training_dataset/data.yaml"
    print(f"📁 配置文件: {config_file}")
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return False
    
    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"📄 配置内容:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # 模拟UI中的路径解析逻辑
    print(f"\n🔗 UI路径解析逻辑:")
    config_dir = os.path.dirname(config_file)
    print(f"📂 配置文件目录: {config_dir}")
    
    # 处理path字段
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ 原始path字段: {dataset_base_path}")
        
        if not os.path.isabs(dataset_base_path):
            dataset_base_path = os.path.join(config_dir, dataset_base_path)
            print(f"🔗 解析后的数据集基础路径: {dataset_base_path}")
    else:
        dataset_base_path = config_dir
        print("📁 使用配置文件目录作为基础路径")
    
    # 构建训练和验证路径
    train_relative = config.get('train', '')
    val_relative = config.get('val', '')
    
    train_path = os.path.join(dataset_base_path, train_relative)
    val_path = os.path.join(dataset_base_path, val_relative)
    
    print(f"🚂 训练路径: {train_relative} -> {train_path}")
    print(f"✅ 验证路径: {val_relative} -> {val_path}")
    
    # 检查路径是否存在
    print(f"\n📊 路径存在性检查:")
    print(f"🚂 训练路径存在: {os.path.exists(train_path)}")
    print(f"✅ 验证路径存在: {os.path.exists(val_path)}")
    
    # 检查是否有重复路径问题
    print(f"\n🔍 检查路径是否正确:")
    expected_train = "datasets/training_dataset/images/train"
    expected_val = "datasets/training_dataset/images/val"
    
    # 标准化路径进行比较
    train_normalized = os.path.normpath(train_path)
    val_normalized = os.path.normpath(val_path)
    expected_train_normalized = os.path.normpath(expected_train)
    expected_val_normalized = os.path.normpath(expected_val)
    
    print(f"🚂 训练路径正确: {train_normalized == expected_train_normalized}")
    print(f"✅ 验证路径正确: {val_normalized == expected_val_normalized}")
    
    if train_normalized == expected_train_normalized and val_normalized == expected_val_normalized:
        print(f"\n🎉 路径修复成功！")
        print(f"✅ 训练路径: {train_normalized}")
        print(f"✅ 验证路径: {val_normalized}")
        return True
    else:
        print(f"\n❌ 路径仍有问题:")
        print(f"   期望训练路径: {expected_train_normalized}")
        print(f"   实际训练路径: {train_normalized}")
        print(f"   期望验证路径: {expected_val_normalized}")
        print(f"   实际验证路径: {val_normalized}")
        return False

if __name__ == "__main__":
    verify_path_fix()
