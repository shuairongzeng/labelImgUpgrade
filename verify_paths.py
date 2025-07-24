#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的路径验证脚本
"""

import os
import yaml

def main():
    print("🔍 验证数据集路径")
    
    # 配置文件路径
    config_file = "datasets/training_dataset/data.yaml"
    print(f"配置文件: {config_file}")
    print(f"工作目录: {os.getcwd()}")
    print(f"配置文件存在: {os.path.exists(config_file)}")
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"配置内容: {config}")
        
        # 路径解析
        config_dir = os.path.dirname(config_file)
        print(f"配置目录: {config_dir}")
        
        if config.get('path') == '.':
            base_path = config_dir
        else:
            base_path = os.path.join(config_dir, config.get('path', ''))
        
        print(f"基础路径: {base_path}")
        
        train_path = os.path.join(base_path, config.get('train', ''))
        val_path = os.path.join(base_path, config.get('val', ''))
        
        print(f"训练路径: {train_path}")
        print(f"验证路径: {val_path}")
        print(f"训练路径存在: {os.path.exists(train_path)}")
        print(f"验证路径存在: {os.path.exists(val_path)}")

if __name__ == "__main__":
    main()
