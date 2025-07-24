#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建使用绝对路径的data.yaml文件
Create data.yaml with Absolute Paths
"""

import os
import yaml

def create_absolute_data_yaml():
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
    
    # 创建新的配置
    new_config = {
        'path': dataset_path,
        'train': train_path,
        'val': val_path,
        'test': None,
        'names': names
    }
    
    # 保存新的配置文件
    new_config_path = os.path.join(dataset_path, "data_absolute.yaml")
    try:
        with open(new_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ 创建绝对路径配置文件: {new_config_path}")
        
        # 显示新配置内容
        print("\n📋 新配置文件内容:")
        with open(new_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        return new_config_path
        
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

def test_absolute_config(config_path):
    """测试绝对路径配置"""
    print(f"\n🧪 测试绝对路径配置: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"📋 配置内容: {config}")
        
        # 检查所有路径
        for key in ['path', 'train', 'val']:
            if key in config and config[key]:
                path = config[key]
                if os.path.exists(path):
                    print(f"✅ {key}: {path} (存在)")
                    
                    if key in ['train', 'val']:
                        # 统计图片数量
                        try:
                            images = [f for f in os.listdir(path) 
                                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
                            print(f"   📊 图片数量: {len(images)}")
                        except Exception as e:
                            print(f"   ⚠️ 无法统计图片: {str(e)}")
                else:
                    print(f"❌ {key}: {path} (不存在)")
                    return False
        
        print("🎉 绝对路径配置验证通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试配置失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始创建绝对路径data.yaml配置...")
    
    config_path = create_absolute_data_yaml()
    
    if config_path:
        success = test_absolute_config(config_path)
        
        if success:
            print(f"\n✅ 成功创建绝对路径配置文件!")
            print(f"📄 配置文件路径: {config_path}")
            print("\n📋 使用说明:")
            print("   1. 在训练配置中选择这个新的配置文件")
            print("   2. 或者将其重命名为data.yaml替换原文件")
            print("   3. 这样可以避免YOLO训练器的路径解析问题")
        else:
            print("\n❌ 配置文件创建失败!")
    else:
        print("\n❌ 无法创建配置文件!")
    
    return config_path is not False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
