#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路径清理修复 - 确保没有不必要的 \. 拼接
"""

import os
import yaml
from pathlib import Path

def test_path_clean_fix():
    """测试路径清理修复"""
    print("🔍 测试路径清理修复")
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
    
    # 模拟修复后的路径解析逻辑
    print(f"\n🔗 修复后的路径解析逻辑:")
    config_dir = os.path.dirname(config_file)
    print(f"📂 配置文件目录: {config_dir}")
    
    # 处理path字段 - 修复后的逻辑
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ 原始path字段: '{dataset_base_path}'")
        
        if not os.path.isabs(dataset_base_path):
            if dataset_base_path == '.':
                # 如果是当前目录，直接使用配置文件目录
                dataset_base_path = config_dir
                print(f"🔗 使用配置文件目录作为基础路径: {dataset_base_path}")
            else:
                # 其他相对路径正常拼接
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
    
    print(f"\n📊 最终路径结果:")
    print(f"🗂️ 基础路径: {dataset_base_path}")
    print(f"🚂 训练路径: {train_path}")
    print(f"✅ 验证路径: {val_path}")
    
    # 检查路径中是否有不必要的 \. 
    print(f"\n🔍 检查路径清洁度:")
    has_dot_issue = False
    
    if '\\.' in dataset_base_path or '/.' in dataset_base_path:
        print(f"❌ 基础路径包含不必要的 \\. : {dataset_base_path}")
        has_dot_issue = True
    else:
        print(f"✅ 基础路径清洁: {dataset_base_path}")
    
    if '\\.' in train_path or '/.' in train_path:
        print(f"❌ 训练路径包含不必要的 \\. : {train_path}")
        has_dot_issue = True
    else:
        print(f"✅ 训练路径清洁: {train_path}")
    
    if '\\.' in val_path or '/.' in val_path:
        print(f"❌ 验证路径包含不必要的 \\. : {val_path}")
        has_dot_issue = True
    else:
        print(f"✅ 验证路径清洁: {val_path}")
    
    # 检查路径是否存在
    print(f"\n📊 路径存在性检查:")
    print(f"🚂 训练路径存在: {os.path.exists(train_path)}")
    print(f"✅ 验证路径存在: {os.path.exists(val_path)}")
    
    # 检查路径是否正确
    expected_train = "datasets/training_dataset/images/train"
    expected_val = "datasets/training_dataset/images/val"
    
    train_normalized = os.path.normpath(train_path)
    val_normalized = os.path.normpath(val_path)
    expected_train_normalized = os.path.normpath(expected_train)
    expected_val_normalized = os.path.normpath(expected_val)
    
    print(f"\n🎯 路径正确性检查:")
    train_correct = train_normalized == expected_train_normalized
    val_correct = val_normalized == expected_val_normalized
    
    print(f"🚂 训练路径正确: {train_correct}")
    print(f"   期望: {expected_train_normalized}")
    print(f"   实际: {train_normalized}")
    
    print(f"✅ 验证路径正确: {val_correct}")
    print(f"   期望: {expected_val_normalized}")
    print(f"   实际: {val_normalized}")
    
    # 总结
    if not has_dot_issue and train_correct and val_correct:
        print(f"\n🎉 路径清理修复成功！")
        print(f"✅ 没有不必要的 \\. 拼接")
        print(f"✅ 所有路径都正确")
        return True
    else:
        print(f"\n❌ 仍有问题:")
        if has_dot_issue:
            print(f"   - 路径中包含不必要的 \\.")
        if not train_correct:
            print(f"   - 训练路径不正确")
        if not val_correct:
            print(f"   - 验证路径不正确")
        return False

if __name__ == "__main__":
    test_path_clean_fix()
