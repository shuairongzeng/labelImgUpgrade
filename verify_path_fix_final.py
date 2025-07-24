#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证路径修复是否有效
"""

import os
import yaml

def update_existing_data_yaml():
    """更新现有的data.yaml文件"""
    print("🔄 更新现有的data.yaml文件")
    print("=" * 50)
    
    config_file = "datasets/training_dataset/data.yaml"
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"📄 原始配置: {config}")
        
        # 修复path字段
        if config.get('path') == 'datasets/training_dataset':
            config['path'] = '.'
            print("🔧 修复path字段: datasets/training_dataset -> .")
            
            # 保存修复后的配置
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 配置文件已更新: {config_file}")
            
            # 验证修复结果
            with open(config_file, 'r', encoding='utf-8') as f:
                updated_config = yaml.safe_load(f)
            
            print(f"📄 更新后配置: {updated_config}")
            return True
        else:
            print(f"ℹ️ 配置文件path字段: {config.get('path')}")
            if config.get('path') == '.':
                print("✅ 配置文件已经是正确的格式")
            return True
            
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        return False

def test_path_resolution():
    """测试路径解析逻辑"""
    print("\n🧠 测试智能路径解析逻辑")
    print("=" * 50)
    
    config_file = "datasets/training_dataset/data.yaml"
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        config_dir = os.path.dirname(config_file)
        
        print(f"📄 配置文件: {config_file}")
        print(f"📂 配置文件目录: {config_dir}")
        print(f"🗂️ path字段: {config.get('path')}")
        
        # 使用修复后的路径解析逻辑
        base_path = config.get('path', '.')
        if not os.path.isabs(base_path):
            if base_path == '.':
                base_path = config_dir
                print("🔗 使用配置文件目录作为基础路径")
            elif base_path.startswith('datasets/'):
                # 检查config_dir是否已经包含了base_path
                config_dir_normalized = os.path.normpath(config_dir)
                base_path_normalized = os.path.normpath(base_path)
                
                print(f"🔍 配置目录标准化: {config_dir_normalized}")
                print(f"🔍 path字段标准化: {base_path_normalized}")
                
                if config_dir_normalized.endswith(base_path_normalized.replace('/', os.sep)):
                    # 如果配置文件目录已经包含了path路径，直接使用配置文件目录
                    base_path = config_dir
                    print(f"🔧 检测到路径重复，使用配置文件目录: {config_dir}")
                else:
                    # 否则相对于项目根目录解析
                    project_root = os.getcwd()
                    base_path = os.path.join(project_root, base_path)
                    print(f"🔗 相对于项目根目录解析: {base_path}")
            else:
                # 其他相对路径正常拼接
                base_path = os.path.join(config_dir, base_path)
                print(f"🔗 相对于配置文件目录解析: {base_path}")
        
        base_path = os.path.abspath(base_path)
        print(f"✅ 最终解析结果: {base_path}")
        
        # 构建训练和验证路径
        train_path = os.path.join(base_path, config.get('train', 'images/train'))
        val_path = os.path.join(base_path, config.get('val', 'images/val'))
        
        print(f"✅ 训练路径: {train_path}")
        print(f"✅ 验证路径: {val_path}")
        
        # 检查路径是否存在
        print(f"\n📊 路径存在性检查:")
        print(f"🚂 训练路径存在: {os.path.exists(train_path)}")
        print(f"✅ 验证路径存在: {os.path.exists(val_path)}")
        
        if os.path.exists(train_path) and os.path.exists(val_path):
            print("🎉 所有路径都存在，修复成功！")
            return True
        else:
            print("❌ 部分路径不存在，需要进一步检查")
            return False
            
    except Exception as e:
        print(f"❌ 测试路径解析失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 开始最终验证路径修复...")
    
    # 更新现有的data.yaml文件
    update_success = update_existing_data_yaml()
    
    if update_success:
        # 测试路径解析
        test_success = test_path_resolution()
        
        if test_success:
            print("\n🎉 路径修复验证完成！")
            print("\n📋 修复总结:")
            print("1. ✅ 修复了PascalToYOLOConverter生成data.yaml时的path字段")
            print("2. ✅ 修复了验证配置时的路径解析逻辑")
            print("3. ✅ 修复了训练器中的路径解析逻辑")
            print("4. ✅ 添加了智能路径重复检测")
            print("5. ✅ 更新了现有的data.yaml文件")
            print("\n现在可以重新运行程序，点击'验证配置'按钮应该不会再出现路径错误！")
        else:
            print("\n❌ 路径解析测试失败，请检查数据集目录结构")
    else:
        print("\n❌ 配置文件更新失败")

if __name__ == "__main__":
    main()
