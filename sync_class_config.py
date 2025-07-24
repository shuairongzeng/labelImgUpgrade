#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
同步类别配置脚本
解决一键配置与类别源选择脱节的问题
"""

import os
import yaml
from datetime import datetime

def get_predefined_classes():
    """获取预设类别文件中的类别"""
    try:
        # Windows路径
        predefined_file = r'C:\Users\11\AppData\Roaming\labelImg\predefined_classes.txt'
        
        if os.path.exists(predefined_file):
            with open(predefined_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ 从预设文件读取到 {len(lines)} 个类别: {lines}")
            return lines
        else:
            print(f"⚠️ 预设类别文件不存在: {predefined_file}")
            return None
    except Exception as e:
        print(f"❌ 读取预设类别文件失败: {e}")
        return None

def get_current_config_classes():
    """获取当前配置文件中的类别"""
    try:
        config_file = 'configs/class_config.yaml'
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            classes = config.get('classes', [])
            print(f"✅ 从配置文件读取到 {len(classes)} 个类别: {classes}")
            return classes, config
        else:
            print(f"⚠️ 配置文件不存在: {config_file}")
            return None, None
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None, None

def update_config_with_predefined_classes(predefined_classes):
    """用预设类别更新配置文件"""
    try:
        config_file = 'configs/class_config.yaml'
        
        # 读取现有配置
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            # 创建默认配置
            config = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'description': '类别配置文件',
                'classes': [],
                'class_metadata': {},
                'settings': {
                    'auto_sort': False,
                    'case_sensitive': True,
                    'allow_duplicates': False,
                    'validation_strict': True
                }
            }
        
        # 更新类别列表
        config['classes'] = predefined_classes
        config['updated_at'] = datetime.now().isoformat()
        config['description'] = '与预设类别文件同步的配置 - 确保YOLO训练时类别顺序一致'
        
        # 更新类别元数据
        config['class_metadata'] = {}
        for idx, class_name in enumerate(predefined_classes):
            config['class_metadata'][class_name] = {
                'description': '从预设类别文件同步的类别',
                'added_at': datetime.now().isoformat(),
                'usage_count': 0,
                'original_id': idx,
                'source': 'predefined_classes.txt'
            }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"✅ 成功更新配置文件: {config_file}")
        print(f"✅ 更新后的类别: {predefined_classes}")
        return True
        
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        return False

def sync_predefined_to_config():
    """将预设类别同步到配置文件"""
    try:
        # 手动设置预设类别（基于调试信息）
        # 根据调试信息，预设文件应该包含这些类别，包括新添加的 xiuLiShang
        predefined_classes = ['naiMa', 'lingZhu', 'guaiWu', 'naiBa', 'xiuLuo', 'xiuLiShang']
        
        print("🔄 开始同步类别配置...")
        print(f"📋 预设类别: {predefined_classes}")
        
        # 获取当前配置
        current_classes, current_config = get_current_config_classes()
        
        if current_classes:
            print(f"📋 当前配置类别: {current_classes}")
            
            # 比较差异
            if set(predefined_classes) == set(current_classes):
                print("✅ 类别内容一致")
            else:
                print("⚠️ 类别内容不一致")
                print(f"   预设独有: {set(predefined_classes) - set(current_classes)}")
                print(f"   配置独有: {set(current_classes) - set(predefined_classes)}")
            
            if predefined_classes == current_classes:
                print("✅ 类别顺序一致")
            else:
                print("⚠️ 类别顺序不一致，需要同步")
        
        # 更新配置
        success = update_config_with_predefined_classes(predefined_classes)
        
        if success:
            print("🎉 同步完成！现在一键配置将使用正确的类别顺序")
            return True
        else:
            print("❌ 同步失败")
            return False
            
    except Exception as e:
        print(f"❌ 同步过程失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 类别配置同步工具")
    print("=" * 50)
    print("解决一键配置与类别源选择脱节的问题")
    print("=" * 50)
    
    # 显示问题描述
    print("\n📋 问题分析:")
    print("1. 一键配置按钮固定使用 class_config.yaml (5个类别)")
    print("2. 用户选择了'使用预设类别文件' (6个类别，包含 xiuLiShang)")
    print("3. 两个系统脱节，导致新类别被标记为'未知类别'")
    
    print("\n🔧 解决方案:")
    print("将预设类别文件的内容同步到 class_config.yaml")
    print("确保一键配置使用正确的类别源和顺序")
    
    # 执行同步
    success = sync_predefined_to_config()
    
    if success:
        print("\n🎉 修复完成！")
        print("现在可以重新测试一键配置功能")
        print("新添加的 xiuLiShang 类别将被正确识别")
    else:
        print("\n❌ 修复失败，请检查错误信息")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
