#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建类别配置文件
Create Class Configuration File

基于现有数据集创建固定的类别配置文件
"""

import os
import sys
import yaml
from datetime import datetime

def create_class_config_from_existing_dataset():
    """从现有数据集创建类别配置"""
    print("🔧 从现有数据集创建类别配置...")
    
    # 检查现有数据集
    dataset_path = "datasets/training_dataset"
    data_yaml_path = os.path.join(dataset_path, "data.yaml")
    
    if not os.path.exists(data_yaml_path):
        print(f"❌ 数据集配置文件不存在: {data_yaml_path}")
        return False
    
    # 读取现有配置
    try:
        with open(data_yaml_path, 'r', encoding='utf-8') as f:
            existing_config = yaml.safe_load(f)
        
        print(f"📄 读取现有配置: {data_yaml_path}")
        print(f"📋 现有类别映射: {existing_config.get('names', {})}")
        
    except Exception as e:
        print(f"❌ 读取现有配置失败: {e}")
        return False
    
    # 提取类别信息
    names = existing_config.get('names', {})
    if isinstance(names, dict):
        # 按ID排序获取类别列表
        classes = [names[i] for i in sorted(names.keys())]
    elif isinstance(names, list):
        classes = names
    else:
        print("❌ 无效的类别格式")
        return False
    
    if not classes:
        print("❌ 未找到类别信息")
        return False
    
    print(f"🏷️ 提取的类别列表: {classes}")
    
    # 创建类别配置
    class_config = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'description': f'从数据集 {dataset_path} 创建的固定类别配置',
        'classes': classes,
        'class_metadata': {},
        'settings': {
            'auto_sort': False,
            'case_sensitive': True,
            'allow_duplicates': False,
            'validation_strict': True
        }
    }
    
    # 添加类别元数据
    for idx, class_name in enumerate(classes):
        class_config['class_metadata'][class_name] = {
            'description': f'从现有数据集导入的类别',
            'added_at': datetime.now().isoformat(),
            'usage_count': 0,
            'original_id': idx,
            'imported_from': dataset_path
        }
    
    # 创建配置目录
    config_dir = "configs"
    os.makedirs(config_dir, exist_ok=True)
    
    # 保存类别配置
    config_file = os.path.join(config_dir, "class_config.yaml")
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(class_config, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False)
        
        print(f"✅ 类别配置已保存: {config_file}")
        
        # 显示配置内容
        print(f"\n📋 类别配置内容:")
        print(f"  版本: {class_config['version']}")
        print(f"  描述: {class_config['description']}")
        print(f"  类别数量: {len(classes)}")
        print(f"  类别列表: {classes}")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False


def verify_class_config():
    """验证类别配置文件"""
    print("\n🔍 验证类别配置文件...")
    
    config_file = "configs/class_config.yaml"
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ 配置文件读取成功")
        print(f"📋 配置信息:")
        print(f"  版本: {config.get('version', 'N/A')}")
        print(f"  创建时间: {config.get('created_at', 'N/A')}")
        print(f"  类别数量: {len(config.get('classes', []))}")
        print(f"  类别列表: {config.get('classes', [])}")
        
        # 验证类别映射
        classes = config.get('classes', [])
        expected_mapping = {name: idx for idx, name in enumerate(classes)}
        print(f"🔗 预期的类别映射: {expected_mapping}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证配置失败: {e}")
        return False


def create_test_converter():
    """创建测试转换器配置"""
    print("\n🧪 创建测试转换器配置...")
    
    # 创建一个简单的测试脚本
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试固定类别顺序的转换器
"""

import os
import sys

# 添加libs路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def test_fixed_class_order():
    """测试固定类别顺序"""
    try:
        from libs.class_manager import ClassConfigManager
        
        # 创建类别管理器
        manager = ClassConfigManager("configs")
        config = manager.load_class_config()
        
        print("📋 加载的类别配置:")
        print(f"  类别列表: {manager.get_class_list()}")
        print(f"  类别映射: {manager.get_class_to_id_mapping()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 测试固定类别顺序...")
    success = test_fixed_class_order()
    print("✅ 测试完成" if success else "❌ 测试失败")
'''
    
    test_file = "test_fixed_classes.py"
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print(f"✅ 测试脚本已创建: {test_file}")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试脚本失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 创建类别配置文件...")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    steps = [
        ("从现有数据集创建类别配置", create_class_config_from_existing_dataset),
        ("验证类别配置文件", verify_class_config),
        ("创建测试转换器配置", create_test_converter)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*50}")
        print(f"🔧 {step_name}")
        print(f"{'='*50}")
        
        try:
            if step_func():
                print(f"✅ {step_name} - 完成")
            else:
                print(f"❌ {step_name} - 失败")
                return False
        except Exception as e:
            print(f"❌ {step_name} - 异常: {e}")
            return False
    
    print(f"\n{'='*50}")
    print("🎉 类别配置创建完成！")
    print(f"{'='*50}")
    print("📋 下一步:")
    print("  1. 检查 configs/class_config.yaml 文件")
    print("  2. 运行 python test_fixed_classes.py 进行测试")
    print("  3. 使用新的转换器进行YOLO数据集转换")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
