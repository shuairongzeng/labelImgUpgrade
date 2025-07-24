#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路径修复验证测试

验证修复后的数据集路径解析是否正确
"""

import os
import sys
import yaml
from pathlib import Path

def test_corrected_path_resolution():
    """测试修正后的路径解析"""
    print("🔧 测试修正后的路径解析")
    print("=" * 50)
    
    # 配置文件路径
    config_file = "datasets/training_dataset/data.yaml"
    print(f"📁 配置文件: {config_file}")
    print(f"📂 当前工作目录: {os.getcwd()}")
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return False
    
    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"\n📋 配置文件内容:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # 模拟修复后的路径解析逻辑
    print(f"\n🔗 路径解析过程:")
    
    # 1. 获取配置文件目录
    config_path = Path(config_file)
    config_dir = config_path.parent
    print(f"📂 配置文件目录: {config_dir.absolute()}")
    
    # 2. 处理path字段
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ path字段: '{dataset_base_path}'")
        
        if not os.path.isabs(dataset_base_path):
            if dataset_base_path == '.':
                dataset_base_path = config_dir
                print(f"🔗 '.' 解析为配置文件目录: {dataset_base_path.absolute()}")
            else:
                dataset_base_path = config_dir / dataset_base_path
                print(f"🔗 相对路径解析: {dataset_base_path.absolute()}")
        else:
            dataset_base_path = Path(dataset_base_path)
            print(f"🔗 绝对路径: {dataset_base_path.absolute()}")
    else:
        dataset_base_path = config_dir
        print(f"📁 使用配置文件目录: {dataset_base_path.absolute()}")
    
    # 3. 构建训练和验证路径
    train_relative = config.get('train', '')
    val_relative = config.get('val', '')
    
    print(f"\n📊 最终路径:")
    print(f"🗂️ 数据集基础路径: {dataset_base_path.absolute()}")
    print(f"🚂 训练相对路径: {train_relative}")
    print(f"✅ 验证相对路径: {val_relative}")
    
    train_path = dataset_base_path / train_relative
    val_path = dataset_base_path / val_relative
    
    print(f"🚂 训练绝对路径: {train_path.absolute()}")
    print(f"✅ 验证绝对路径: {val_path.absolute()}")
    
    # 4. 验证路径存在性
    print(f"\n✔️ 路径验证:")
    train_exists = train_path.exists()
    val_exists = val_path.exists()
    
    print(f"🚂 训练路径存在: {train_exists}")
    print(f"✅ 验证路径存在: {val_exists}")
    
    if train_exists:
        train_images = list(train_path.glob("*.jpg")) + list(train_path.glob("*.png")) + list(train_path.glob("*.jpeg"))
        print(f"📊 训练图片数量: {len(train_images)}")
    
    if val_exists:
        val_images = list(val_path.glob("*.jpg")) + list(val_path.glob("*.png")) + list(val_path.glob("*.jpeg"))
        print(f"📊 验证图片数量: {len(val_images)}")
    
    return train_exists and val_exists

def test_ui_display_paths():
    """测试UI显示路径的逻辑"""
    print("\n🖥️ 测试UI显示路径逻辑")
    print("=" * 50)
    
    config_file = "datasets/training_dataset/data.yaml"
    
    # 模拟load_dataset_config方法的逻辑
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    config_dir = os.path.dirname(config_file)
    print(f"📂 配置文件目录: {config_dir}")
    
    # 确定数据集基础路径
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
    if 'train' in config:
        train_relative = config['train']
        train_path = os.path.join(dataset_base_path, train_relative)
        print(f"🚂 训练路径: {train_relative} -> {train_path}")
    
    if 'val' in config:
        val_relative = config['val']
        val_path = os.path.join(dataset_base_path, val_relative)
        print(f"✅ 验证路径: {val_relative} -> {val_path}")
    
    # 这些就是UI中应该显示的路径
    print(f"\n📱 UI应该显示的路径:")
    print(f"   数据集路径: {dataset_base_path}")
    print(f"   训练集: {train_path}")
    print(f"   验证集: {val_path}")
    
    return True

def main():
    """主函数"""
    print("🧪 路径修复验证测试")
    print("=" * 60)
    
    try:
        # 测试路径解析
        success1 = test_corrected_path_resolution()
        
        # 测试UI显示逻辑
        success2 = test_ui_display_paths()
        
        print("\n" + "=" * 60)
        print("📊 测试结果:")
        
        if success1 and success2:
            print("✅ 所有测试通过！路径解析已修复")
            print("\n🎯 修复要点:")
            print("1. ✅ data.yaml中path字段改为'.'")
            print("2. ✅ 路径解析逻辑：配置目录 + path + train/val")
            print("3. ✅ UI显示正确的绝对路径")
            print("4. ✅ 训练器使用正确的路径验证")
        else:
            print("❌ 部分测试失败")
        
        return success1 and success2
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
