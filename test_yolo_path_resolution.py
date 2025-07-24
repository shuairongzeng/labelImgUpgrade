#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试YOLO路径解析逻辑
Test YOLO Path Resolution Logic
"""

import os
import yaml
from pathlib import Path

def test_yolo_path_resolution():
    """测试YOLO路径解析逻辑"""
    print("🔍 测试YOLO路径解析逻辑...")
    
    # 模拟YOLO训练器的路径解析逻辑
    config_path = "datasets/training_dataset/data.yaml"
    project_root = os.getcwd()
    
    print(f"📂 项目根目录: {project_root}")
    print(f"📄 配置文件路径: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"📋 配置文件内容: {config}")
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    # 模拟YOLO的路径解析逻辑
    print("\n🔗 YOLO路径解析逻辑:")
    
    # YOLO通常相对于当前工作目录解析路径
    if 'path' in config and config['path']:
        dataset_path = config['path']
        print(f"🗂️ path字段: {dataset_path}")
        
        if not os.path.isabs(dataset_path):
            # 相对于当前工作目录解析
            dataset_abs_path = os.path.join(project_root, dataset_path)
            dataset_abs_path = os.path.abspath(dataset_abs_path)
            print(f"🔗 解析后的数据集路径: {dataset_abs_path}")
        else:
            dataset_abs_path = dataset_path
            print(f"🔗 使用绝对路径: {dataset_abs_path}")
        
        # 检查数据集路径是否存在
        if os.path.exists(dataset_abs_path):
            print(f"✅ 数据集路径存在")
        else:
            print(f"❌ 数据集路径不存在: {dataset_abs_path}")
            return False
    
    # 检查训练路径
    if 'train' in config:
        train_path = config['train']
        print(f"🚂 train字段: {train_path}")
        
        if not os.path.isabs(train_path):
            # 相对于当前工作目录解析
            train_abs_path = os.path.join(project_root, train_path)
            train_abs_path = os.path.abspath(train_abs_path)
            print(f"🔗 解析后的训练路径: {train_abs_path}")
        else:
            train_abs_path = train_path
            print(f"🔗 使用绝对路径: {train_abs_path}")
        
        # 检查训练路径是否存在
        if os.path.exists(train_abs_path):
            print(f"✅ 训练路径存在")
            # 统计图片数量
            try:
                train_images = [f for f in os.listdir(train_abs_path) 
                              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                print(f"📊 训练图片数量: {len(train_images)}")
            except Exception as e:
                print(f"⚠️ 无法统计训练图片: {str(e)}")
        else:
            print(f"❌ 训练路径不存在: {train_abs_path}")
            return False
    
    # 检查验证路径
    if 'val' in config:
        val_path = config['val']
        print(f"✅ val字段: {val_path}")
        
        if not os.path.isabs(val_path):
            # 相对于当前工作目录解析
            val_abs_path = os.path.join(project_root, val_path)
            val_abs_path = os.path.abspath(val_abs_path)
            print(f"🔗 解析后的验证路径: {val_abs_path}")
        else:
            val_abs_path = val_path
            print(f"🔗 使用绝对路径: {val_abs_path}")
        
        # 检查验证路径是否存在
        if os.path.exists(val_abs_path):
            print(f"✅ 验证路径存在")
            # 统计图片数量
            try:
                val_images = [f for f in os.listdir(val_abs_path) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                print(f"📊 验证图片数量: {len(val_images)}")
            except Exception as e:
                print(f"⚠️ 无法统计验证图片: {str(e)}")
        else:
            print(f"❌ 验证路径不存在: {val_abs_path}")
            return False
    
    print("\n🎉 YOLO路径解析验证通过！")
    return True

def test_alternative_config():
    """测试备选配置方案"""
    print("\n🔄 测试备选配置方案...")
    
    # 方案1：使用绝对路径
    project_root = os.path.abspath(os.getcwd())
    train_abs = os.path.join(project_root, "datasets", "training_dataset", "images", "train")
    val_abs = os.path.join(project_root, "datasets", "training_dataset", "images", "val")
    
    print("📋 方案1 - 绝对路径配置:")
    print(f"path: {os.path.join(project_root, 'datasets', 'training_dataset')}")
    print(f"train: {train_abs}")
    print(f"val: {val_abs}")
    
    if os.path.exists(train_abs) and os.path.exists(val_abs):
        print("✅ 方案1可行")
    else:
        print("❌ 方案1不可行")
    
    # 方案2：相对于项目根目录的路径
    print("\n📋 方案2 - 相对路径配置:")
    print("path: datasets/training_dataset")
    print("train: datasets/training_dataset/images/train")
    print("val: datasets/training_dataset/images/val")
    
    train_rel = os.path.join(project_root, "datasets", "training_dataset", "images", "train")
    val_rel = os.path.join(project_root, "datasets", "training_dataset", "images", "val")
    
    if os.path.exists(train_rel) and os.path.exists(val_rel):
        print("✅ 方案2可行")
    else:
        print("❌ 方案2不可行")

def main():
    """主函数"""
    print("🧪 开始测试YOLO路径解析...")
    
    success = test_yolo_path_resolution()
    test_alternative_config()
    
    if success:
        print("\n✅ 测试通过！当前配置应该可以正常工作。")
        print("\n📋 当前配置说明:")
        print("   • path: datasets/training_dataset (相对于项目根目录)")
        print("   • train: datasets/training_dataset/images/train (相对于项目根目录)")
        print("   • val: datasets/training_dataset/images/val (相对于项目根目录)")
        print("   • 这样YOLO训练器可以正确解析所有路径")
    else:
        print("\n❌ 测试失败！需要进一步调整配置。")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
