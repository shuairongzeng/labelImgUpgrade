#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的data.yaml配置文件
Test Fixed data.yaml Configuration File
"""

import os
import yaml

def test_data_yaml_config():
    """测试data.yaml配置文件"""
    print("🔍 测试修复后的data.yaml配置文件...")
    
    config_path = "datasets/training_dataset/data.yaml"
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    print(f"✅ 配置文件存在: {config_path}")
    
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"📄 配置文件内容: {config}")
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    # 获取配置文件所在目录
    config_dir = os.path.dirname(config_path)
    config_dir_abs = os.path.abspath(config_dir)
    print(f"📂 配置文件目录: {config_dir}")
    print(f"📂 配置文件绝对目录: {config_dir_abs}")
    
    # 解析路径
    if 'path' in config and config['path']:
        dataset_base_path = config['path']
        print(f"🗂️ 原始path字段: {dataset_base_path}")
        
        if not os.path.isabs(dataset_base_path):
            if dataset_base_path == '.':
                # 如果是当前目录，直接使用配置文件目录
                dataset_base_path = config_dir_abs
                print(f"🔗 使用配置文件目录作为基础路径: {dataset_base_path}")
            elif dataset_base_path.startswith('datasets/'):
                # 如果是相对于项目根目录的datasets路径，使用项目根目录作为基础
                project_root = os.getcwd()
                dataset_base_path = os.path.join(project_root, dataset_base_path)
                dataset_base_path = os.path.abspath(dataset_base_path)
                print(f"🔗 项目根目录: {project_root}")
                print(f"🔗 相对于项目根目录解析: {dataset_base_path}")
            else:
                # 其他相对路径相对于配置文件目录拼接
                dataset_base_path = os.path.join(config_dir_abs, dataset_base_path)
                dataset_base_path = os.path.abspath(dataset_base_path)
                print(f"🔗 相对于配置文件目录解析: {dataset_base_path}")
        else:
            print(f"🔗 使用绝对路径: {dataset_base_path}")
    else:
        # 如果没有path字段，使用配置文件所在目录
        dataset_base_path = config_dir_abs
        print(f"📁 使用配置文件目录作为基础路径: {dataset_base_path}")
    
    # 检查数据集基础路径是否存在
    if not os.path.exists(dataset_base_path):
        print(f"❌ 数据集基础路径不存在: {dataset_base_path}")
        return False
    else:
        print(f"✅ 数据集基础路径存在: {dataset_base_path}")
    
    # 检查训练路径
    if 'train' in config:
        train_relative = config['train']
        train_path = os.path.join(dataset_base_path, train_relative)
        train_path = os.path.abspath(train_path)
        print(f"🚂 训练相对路径: {train_relative}")
        print(f"🚂 训练绝对路径: {train_path}")
        
        if os.path.exists(train_path):
            print(f"✅ 训练路径存在")
            # 统计训练图片数量
            try:
                train_images = [f for f in os.listdir(train_path) 
                              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                print(f"📊 训练图片数量: {len(train_images)}")
            except Exception as e:
                print(f"⚠️ 无法统计训练图片: {str(e)}")
        else:
            print(f"❌ 训练路径不存在: {train_path}")
            return False
    
    # 检查验证路径
    if 'val' in config:
        val_relative = config['val']
        val_path = os.path.join(dataset_base_path, val_relative)
        val_path = os.path.abspath(val_path)
        print(f"✅ 验证相对路径: {val_relative}")
        print(f"✅ 验证绝对路径: {val_path}")
        
        if os.path.exists(val_path):
            print(f"✅ 验证路径存在")
            # 统计验证图片数量
            try:
                val_images = [f for f in os.listdir(val_path) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                print(f"📊 验证图片数量: {len(val_images)}")
            except Exception as e:
                print(f"⚠️ 无法统计验证图片: {str(e)}")
        else:
            print(f"❌ 验证路径不存在: {val_path}")
            return False
    
    # 检查类别信息
    if 'names' in config:
        names = config['names']
        if isinstance(names, dict):
            classes_list = [names[i] for i in sorted(names.keys())]
        elif isinstance(names, list):
            classes_list = names
        else:
            classes_list = []
        
        print(f"🏷️ 类别数量: {len(classes_list)}")
        print(f"🏷️ 类别列表: {classes_list}")
    
    print("\n🎉 data.yaml配置文件验证通过！")
    return True

def main():
    """主函数"""
    print("🧪 开始测试修复后的data.yaml配置...")
    
    success = test_data_yaml_config()
    
    if success:
        print("\n✅ 测试通过！配置文件已正确修复。")
        print("\n📋 修复说明:")
        print("   • 将path字段从'datasets/training_dataset'改为'.'")
        print("   • 将train路径从'datasets/training_dataset/images/train'改为'images/train'")
        print("   • 将val路径从'datasets/training_dataset/images/val'改为'images/val'")
        print("   • 避免了路径重复拼接的问题")
        
        print("\n🚀 现在可以正常进行训练了！")
    else:
        print("\n❌ 测试失败！请检查配置文件。")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
