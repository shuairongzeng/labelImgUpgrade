#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建使用绝对路径的data.yaml文件
"""

import os
import yaml

def create_absolute_path_yaml():
    """创建使用绝对路径的data.yaml文件"""
    print("🔧 创建使用绝对路径的data.yaml文件...")
    
    # 获取项目根目录
    project_root = os.path.abspath(os.getcwd())
    print(f"📂 项目根目录: {project_root}")
    
    # 构建绝对路径
    dataset_path = os.path.join(project_root, "datasets", "training_dataset")
    train_path = os.path.join(dataset_path, "images", "train")
    val_path = os.path.join(dataset_path, "images", "val")
    
    print(f"📁 数据集路径: {dataset_path}")
    print(f"🚂 训练路径: {train_path}")
    print(f"✅ 验证路径: {val_path}")
    
    # 检查路径是否存在
    if not os.path.exists(train_path):
        print(f"❌ 训练路径不存在: {train_path}")
        return False
    
    if not os.path.exists(val_path):
        print(f"❌ 验证路径不存在: {val_path}")
        return False
    
    print("✅ 所有路径都存在")
    
    # 读取原始配置文件获取类别信息
    original_config_path = os.path.join(dataset_path, "data.yaml")
    try:
        with open(original_config_path, 'r', encoding='utf-8') as f:
            original_config = yaml.safe_load(f)
        
        names = original_config.get('names', {})
        print(f"🏷️ 类别信息: {names}")
        
    except Exception as e:
        print(f"❌ 读取原始配置失败: {e}")
        return False
    
    # 创建新的配置（使用绝对路径）
    new_config = {
        'path': dataset_path,  # 绝对路径
        'train': train_path,   # 绝对路径
        'val': val_path,       # 绝对路径
        'test': None,
        'names': names
    }
    
    print(f"\n📋 新配置内容:")
    print(f"  path: {new_config['path']}")
    print(f"  train: {new_config['train']}")
    print(f"  val: {new_config['val']}")
    print(f"  names: {new_config['names']}")
    
    # 保存新配置文件
    try:
        with open(original_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n✅ 已更新配置文件: {original_config_path}")
        return True
        
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

if __name__ == "__main__":
    success = create_absolute_path_yaml()
    if success:
        print("\n🎉 绝对路径配置文件创建成功！")
    else:
        print("\n❌ 绝对路径配置文件创建失败")
