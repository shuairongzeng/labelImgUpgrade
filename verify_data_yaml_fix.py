#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的data.yaml配置文件
"""

import os
import yaml

def verify_data_yaml():
    """验证data.yaml配置文件"""
    print("🔍 验证修复后的data.yaml配置文件...")
    
    config_file = "datasets/training_dataset/data.yaml"
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        # 读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"📄 配置文件内容:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # 验证path字段
        path = config.get('path')
        if not path:
            print("❌ 缺少path字段")
            return False
        
        print(f"\n🗂️ 基础路径: {path}")
        
        if not os.path.exists(path):
            print(f"❌ 基础路径不存在: {path}")
            return False
        
        print("✅ 基础路径存在")
        
        # 验证train路径
        train_path = config.get('train')
        if train_path:
            if os.path.isabs(train_path):
                full_train_path = train_path
            else:
                full_train_path = os.path.join(path, train_path)
            
            print(f"🚂 训练路径: {full_train_path}")
            
            if os.path.exists(full_train_path):
                train_files = os.listdir(full_train_path)
                train_count = len([f for f in train_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
                print(f"✅ 训练路径存在，包含 {train_count} 个图片文件")
            else:
                print(f"❌ 训练路径不存在: {full_train_path}")
                return False
        
        # 验证val路径
        val_path = config.get('val')
        if val_path:
            if os.path.isabs(val_path):
                full_val_path = val_path
            else:
                full_val_path = os.path.join(path, val_path)
            
            print(f"✅ 验证路径: {full_val_path}")
            
            if os.path.exists(full_val_path):
                val_files = os.listdir(full_val_path)
                val_count = len([f for f in val_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
                print(f"✅ 验证路径存在，包含 {val_count} 个图片文件")
            else:
                print(f"❌ 验证路径不存在: {full_val_path}")
                return False
        
        # 验证类别信息
        names = config.get('names')
        if names:
            print(f"🏷️ 类别信息: {names}")
            print(f"📊 类别数量: {len(names)}")
        else:
            print("❌ 缺少类别信息")
            return False
        
        print("\n✅ 所有配置验证通过！")
        return True
        
    except Exception as e:
        print(f"❌ 验证配置文件失败: {e}")
        return False

if __name__ == "__main__":
    success = verify_data_yaml()
    if success:
        print("\n🎉 data.yaml配置文件修复成功！")
        print("💡 现在可以重新尝试YOLO训练了")
    else:
        print("\n❌ data.yaml配置文件仍有问题")
    
    exit(0 if success else 1)
