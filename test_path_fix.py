#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路径修复是否有效
"""

import os
import yaml
from pathlib import Path

def test_path_resolution():
    """测试路径解析是否正确"""
    print("🔍 测试路径解析修复...")
    
    # 配置文件路径
    config_file = "datasets/training_dataset/data.yaml"
    
    print(f"📄 配置文件: {config_file}")
    print(f"📂 当前工作目录: {os.getcwd()}")
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    # 读取配置文件
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"📋 配置文件内容: {config}")
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    # 解析路径（模拟训练器的逻辑）
    print("\n🔗 路径解析过程:")
    
    config_path = Path(config_file)
    config_dir = config_path.parent
    print(f"📂 配置文件目录: {config_dir.absolute()}")
    
    # 处理path字段
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ 数据集path字段: '{dataset_base_path}'")
        
        if not os.path.isabs(dataset_base_path):
            if dataset_base_path == '.':
                # 如果是当前目录，直接使用配置文件目录
                dataset_base_path = config_dir
                print("🔗 使用配置文件目录作为基础路径")
            else:
                # 其他相对路径正常拼接
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
    train_exists = train_path.exists()
    val_exists = val_path.exists()
    
    print(f"🚂 训练路径存在: {train_exists}")
    print(f"✅ 验证路径存在: {val_exists}")
    
    if train_exists and val_exists:
        print("\n🎉 路径修复成功！所有路径都正确解析并存在")
        
        # 统计文件数量
        try:
            train_images = [f for f in os.listdir(train_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            val_images = [f for f in os.listdir(val_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            
            print(f"📊 训练图片数量: {len(train_images)}")
            print(f"📊 验证图片数量: {len(val_images)}")
            
        except Exception as e:
            print(f"⚠️ 无法统计图片数量: {e}")
        
        return True
    else:
        print("\n❌ 路径修复失败，仍有路径不存在")
        if not train_exists:
            print(f"❌ 训练路径不存在: {train_path.absolute()}")
        if not val_exists:
            print(f"❌ 验证路径不存在: {val_path.absolute()}")
        return False

if __name__ == "__main__":
    success = test_path_resolution()
    if success:
        print("\n✅ 测试通过，路径问题已解决")
    else:
        print("\n❌ 测试失败，路径问题仍然存在")
