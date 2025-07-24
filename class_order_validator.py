#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
类别顺序验证工具
Class Order Validation Tool

验证和修复YOLO数据集中的类别顺序一致性问题
"""

import os
import sys
import yaml
import json
from datetime import datetime

def load_class_config(config_file="configs/class_config.yaml"):
    """加载类别配置文件"""
    try:
        if not os.path.exists(config_file):
            print(f"❌ 类别配置文件不存在: {config_file}")
            return None
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"✅ 成功加载类别配置: {config_file}")
        return config
        
    except Exception as e:
        print(f"❌ 加载类别配置失败: {e}")
        return None


def validate_dataset(dataset_path, class_config):
    """验证数据集的类别顺序一致性"""
    print(f"\n🔍 验证数据集: {dataset_path}")
    
    if not os.path.exists(dataset_path):
        print(f"❌ 数据集路径不存在: {dataset_path}")
        return False
    
    # 检查data.yaml文件
    data_yaml_path = os.path.join(dataset_path, "data.yaml")
    classes_txt_path = os.path.join(dataset_path, "classes.txt")
    
    validation_results = {
        'dataset_path': dataset_path,
        'data_yaml_exists': os.path.exists(data_yaml_path),
        'classes_txt_exists': os.path.exists(classes_txt_path),
        'data_yaml_classes': [],
        'classes_txt_classes': [],
        'config_classes': class_config.get('classes', []),
        'issues': [],
        'recommendations': []
    }
    
    # 验证data.yaml
    if validation_results['data_yaml_exists']:
        try:
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            names = yaml_config.get('names', {})
            if isinstance(names, dict):
                validation_results['data_yaml_classes'] = [names[i] for i in sorted(names.keys())]
            elif isinstance(names, list):
                validation_results['data_yaml_classes'] = names
            
            print(f"📄 data.yaml中的类别: {validation_results['data_yaml_classes']}")
            
        except Exception as e:
            validation_results['issues'].append(f"读取data.yaml失败: {e}")
    
    # 验证classes.txt
    if validation_results['classes_txt_exists']:
        try:
            with open(classes_txt_path, 'r', encoding='utf-8') as f:
                validation_results['classes_txt_classes'] = [line.strip() for line in f if line.strip()]
            
            print(f"📄 classes.txt中的类别: {validation_results['classes_txt_classes']}")
            
        except Exception as e:
            validation_results['issues'].append(f"读取classes.txt失败: {e}")
    
    # 比较一致性
    config_classes = validation_results['config_classes']
    yaml_classes = validation_results['data_yaml_classes']
    txt_classes = validation_results['classes_txt_classes']
    
    print(f"📋 配置文件中的类别: {config_classes}")
    
    # 检查与配置文件的一致性
    if yaml_classes and yaml_classes != config_classes:
        validation_results['issues'].append("data.yaml中的类别顺序与配置文件不一致")
        print(f"⚠️ data.yaml类别顺序不一致")
        print(f"   配置: {config_classes}")
        print(f"   实际: {yaml_classes}")
    
    if txt_classes and txt_classes != config_classes:
        validation_results['issues'].append("classes.txt中的类别顺序与配置文件不一致")
        print(f"⚠️ classes.txt类别顺序不一致")
        print(f"   配置: {config_classes}")
        print(f"   实际: {txt_classes}")
    
    # 检查data.yaml和classes.txt之间的一致性
    if yaml_classes and txt_classes and yaml_classes != txt_classes:
        validation_results['issues'].append("data.yaml和classes.txt中的类别顺序不一致")
        print(f"⚠️ data.yaml和classes.txt之间不一致")
    
    # 生成建议
    if validation_results['issues']:
        validation_results['recommendations'].append("建议使用修复功能统一类别顺序")
    else:
        validation_results['recommendations'].append("类别顺序一致，无需修复")
        print("✅ 类别顺序验证通过")
    
    return validation_results


def fix_dataset_classes(dataset_path, class_config):
    """修复数据集的类别顺序"""
    print(f"\n🔧 修复数据集类别顺序: {dataset_path}")
    
    config_classes = class_config.get('classes', [])
    if not config_classes:
        print("❌ 配置文件中没有类别信息")
        return False
    
    # 修复data.yaml
    data_yaml_path = os.path.join(dataset_path, "data.yaml")
    if os.path.exists(data_yaml_path):
        try:
            # 读取现有配置
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            # 备份原文件
            backup_path = data_yaml_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True)
            print(f"📋 已备份原data.yaml: {backup_path}")
            
            # 更新类别映射
            yaml_config['names'] = {i: name for i, name in enumerate(config_classes)}
            
            # 保存修复后的文件
            with open(data_yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 已修复data.yaml文件")
            
        except Exception as e:
            print(f"❌ 修复data.yaml失败: {e}")
            return False
    
    # 修复classes.txt
    classes_txt_path = os.path.join(dataset_path, "classes.txt")
    if os.path.exists(classes_txt_path):
        try:
            # 备份原文件
            backup_path = classes_txt_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(classes_txt_path, backup_path)
            print(f"📋 已备份原classes.txt: {backup_path}")
            
            # 写入固定顺序的类别
            with open(classes_txt_path, 'w', encoding='utf-8') as f:
                for class_name in config_classes:
                    f.write(f"{class_name}\n")
            
            print(f"✅ 已修复classes.txt文件")
            
        except Exception as e:
            print(f"❌ 修复classes.txt失败: {e}")
            return False
    
    print("🎉 数据集类别顺序修复完成")
    return True


def generate_report(validation_results):
    """生成验证报告"""
    print(f"\n📊 生成验证报告...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'validation_results': validation_results,
        'summary': {
            'total_issues': len(validation_results['issues']),
            'has_data_yaml': validation_results['data_yaml_exists'],
            'has_classes_txt': validation_results['classes_txt_exists'],
            'is_consistent': len(validation_results['issues']) == 0
        }
    }
    
    # 保存报告
    report_file = f"class_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 验证报告已保存: {report_file}")
        return report_file
        
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return None


def main():
    """主函数"""
    print("🚀 类别顺序验证工具")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载类别配置
    class_config = load_class_config()
    if not class_config:
        print("❌ 无法加载类别配置，退出")
        return False
    
    print(f"📋 配置的类别数量: {len(class_config.get('classes', []))}")
    print(f"📋 配置的类别列表: {class_config.get('classes', [])}")
    
    # 验证现有数据集
    dataset_path = "datasets/training_dataset"
    validation_results = validate_dataset(dataset_path, class_config)
    
    if not validation_results:
        print("❌ 验证失败")
        return False
    
    # 显示验证结果
    print(f"\n{'='*50}")
    print("📊 验证结果汇总")
    print(f"{'='*50}")
    print(f"数据集路径: {validation_results['dataset_path']}")
    print(f"发现问题数量: {len(validation_results['issues'])}")
    
    if validation_results['issues']:
        print("⚠️ 发现的问题:")
        for i, issue in enumerate(validation_results['issues'], 1):
            print(f"  {i}. {issue}")
        
        print("\n💡 建议:")
        for i, rec in enumerate(validation_results['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # 询问是否修复
        print(f"\n🔧 是否要修复这些问题？")
        print("注意：修复前会自动备份原文件")
        
        # 自动修复（在实际使用中可以改为用户输入）
        fix_dataset_classes(dataset_path, class_config)
        
        # 重新验证
        print(f"\n🔍 重新验证修复结果...")
        new_validation = validate_dataset(dataset_path, class_config)
        if new_validation and not new_validation['issues']:
            print("✅ 修复成功，类别顺序现在一致了")
        else:
            print("⚠️ 修复后仍有问题，请手动检查")
    
    # 生成报告
    generate_report(validation_results)
    
    print(f"\n🎉 验证完成")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
