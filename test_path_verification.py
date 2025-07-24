#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证数据集路径解析是否正确
"""

import os
import yaml
from pathlib import Path

def test_path_resolution():
    """测试路径解析"""
    print("🔍 测试数据集路径解析")
    print("=" * 50)
    
    # 配置文件路径
    config_file = "datasets/training_dataset/data.yaml"
    print(f"📁 配置文件: {config_file}")
    print(f"📂 当前目录: {os.getcwd()}")
    print(f"✅ 文件存在: {os.path.exists(config_file)}")
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return False
    
    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"\n📄 配置内容:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # 路径解析
    print(f"\n🔗 路径解析:")
    config_path = Path(config_file)
    config_dir = config_path.parent
    print(f"📂 配置文件目录: {config_dir.absolute()}")
    
    # 处理path字段
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ path字段: '{dataset_base_path}'")
        
        if not os.path.isabs(dataset_base_path):
            if dataset_base_path == '.':
                # 使用配置文件目录
                dataset_base_path = config_dir
                print(f"🔗 '.' 解析为配置文件目录: {dataset_base_path.absolute()}")
            else:
                # 相对路径解析
                dataset_base_path = config_dir / dataset_base_path
                print(f"🔗 相对路径解析: {dataset_base_path.absolute()}")
        else:
            dataset_base_path = Path(dataset_base_path)
            print(f"🔗 绝对路径: {dataset_base_path.absolute()}")
    else:
        dataset_base_path = config_dir
        print(f"📁 使用配置文件目录: {dataset_base_path.absolute()}")
    
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
        train_images = list(train_path.glob('*.jpg')) + list(train_path.glob('*.png'))
        print(f"🚂 训练图片数量: {len(train_images)}")
    
    if val_path.exists():
        val_images = list(val_path.glob('*.jpg')) + list(val_path.glob('*.png'))
        print(f"✅ 验证图片数量: {len(val_images)}")
    
    return True

if __name__ == "__main__":
    test_path_resolution()
