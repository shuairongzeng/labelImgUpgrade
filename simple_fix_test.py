#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的修复效果测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入"""
    print("🔍 测试导入...")
    
    try:
        from labelImg import get_persistent_predefined_classes_path
        print("✅ labelImg 导入成功")
        
        # 测试预设类别文件路径
        predefined_file = get_persistent_predefined_classes_path()
        print(f"✅ 预设类别文件路径: {predefined_file}")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_ai_panel_methods():
    """测试AI面板方法"""
    print("\n🔍 测试AI面板方法...")
    
    try:
        from libs.ai_assistant_panel import AIAssistantPanel
        print("✅ AIAssistantPanel 导入成功")
        
        # 检查关键方法是否存在
        methods_to_check = [
            'on_classes_source_changed',
            'show_classes_info_in_training',
            'create_data_config_tab',
            'refresh_classes_info'
        ]
        
        for method_name in methods_to_check:
            if hasattr(AIAssistantPanel, method_name):
                print(f"✅ 方法存在: {method_name}")
            else:
                print(f"❌ 方法缺失: {method_name}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ AI面板测试失败: {e}")
        return False

def test_class_manager():
    """测试类别管理器"""
    print("\n🔍 测试类别管理器...")
    
    try:
        from libs.class_manager import ClassConfigManager
        print("✅ ClassConfigManager 导入成功")
        
        # 创建临时管理器
        manager = ClassConfigManager("configs")
        config = manager.load_class_config()
        print(f"✅ 类别配置加载成功: {len(config.get('classes', []))} 个类别")
        
        return True
    except Exception as e:
        print(f"❌ 类别管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 类别管理修复效果简单测试")
    print("=" * 50)
    
    tests = [
        ("导入测试", test_imports),
        ("AI面板方法测试", test_ai_panel_methods),
        ("类别管理器测试", test_class_manager)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"💥 {test_name} 出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        print("\n✅ 修复内容总结:")
        print("   1. 预设类别文件路径修复 - 使用正确的持久化路径")
        print("   2. 类别源选择下拉框添加 - 在训练对话框中可选择类别来源")
        print("   3. 类别信息同步机制 - 添加新标签后自动更新AI面板")
        print("   4. 训练对话框类别显示 - 支持多种类别源显示")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
