#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证修复结果
"""

import os
import yaml

def main():
    """验证修复结果"""
    print("🔍 验证修复结果...")
    
    config_file = "datasets/training_dataset/data.yaml"
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return
    
    # 读取配置文件
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"✅ 配置文件存在，开始验证内容...")
    print(f"📋 配置文件内容: {config}")
    
    # 验证类别信息
    if 'names' in config and config['names']:
        print(f"✅ 类别信息正常，共 {len(config['names'])} 个类别")
    else:
        print("❌ 类别信息缺失")
        return
    
    # 验证路径配置
    print(f"✅ 训练集路径: {config.get('train', 'N/A')}")
    print(f"✅ 验证集路径: {config.get('val', 'N/A')}")
    
    # 模拟UI中的路径解析逻辑
    config_dir = os.path.dirname(config_file)
    print(f"📂 数据集基础路径: {config_dir}")
    
    # 处理path字段
    if 'path' in config and config['path']:
        base_path = config['path']
        print(f"🗂️ 原始path字段: {base_path}")
        
        if not os.path.isabs(base_path):
            if base_path == '.':
                base_path = config_dir
                print("🔗 使用配置文件目录作为基础路径")
            elif base_path.startswith('datasets/'):
                # 智能检测路径重复
                config_dir_normalized = os.path.normpath(config_dir)
                base_path_normalized = os.path.normpath(base_path)
                
                if config_dir_normalized.endswith(base_path_normalized.replace('/', os.sep)):
                    base_path = config_dir
                    print(f"🔧 检测到路径重复，使用配置文件目录: {config_dir}")
                else:
                    project_root = os.getcwd()
                    base_path = os.path.join(project_root, base_path)
                    print(f"🔗 相对于项目根目录解析: {base_path}")
            else:
                base_path = os.path.join(config_dir, base_path)
                print(f"🔗 相对于配置文件目录解析: {base_path}")
        
        base_path = os.path.abspath(base_path)
    else:
        base_path = config_dir
        print("📁 使用配置文件目录作为基础路径")
    
    print(f"📂 数据集基础路径: {base_path}")
    
    # 构建训练和验证路径
    if 'train' in config:
        train_path = os.path.join(base_path, config['train'])
        if os.path.exists(train_path):
            print(f"✅ 训练集路径存在: {train_path}")
        else:
            print(f"❌ 训练集路径不存在: {train_path}")
            return
    
    if 'val' in config:
        val_path = os.path.join(base_path, config['val'])
        if os.path.exists(val_path):
            print(f"✅ 验证集路径存在: {val_path}")
        else:
            print(f"❌ 验证集路径不存在: {val_path}")
            return
    
    print("✅ 验证通过！所有路径都正确！")
    print("\n🎉 修复成功！现在可以正常使用训练功能了。")

if __name__ == "__main__":
    main()
