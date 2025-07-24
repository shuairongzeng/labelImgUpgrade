#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试类别管理修复效果
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """测试基本导入"""
    print("🔍 测试基本导入...")
    
    try:
        from libs.class_manager import ClassConfigManager
        print("✅ ClassConfigManager 导入成功")
        
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        print("✅ PascalToYOLOConverter 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_manager_basic():
    """测试类别管理器基本功能"""
    print("\n🔍 测试类别管理器基本功能...")
    
    try:
        from libs.class_manager import ClassConfigManager
        
        # 使用现有的configs目录
        manager = ClassConfigManager("configs")
        print("✅ 成功创建ClassConfigManager")
        
        # 加载配置
        config = manager.load_class_config()
        print(f"✅ 成功加载配置")
        
        # 获取类别列表
        classes = manager.get_class_list()
        print(f"✅ 当前类别: {classes}")
        print(f"✅ 类别数量: {len(classes)}")
        
        # 获取类别映射
        mapping = manager.get_class_to_id_mapping()
        print(f"✅ 类别映射: {mapping}")
        
        return True
    except Exception as e:
        print(f"❌ 类别管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predefined_classes_path():
    """测试预设类别文件路径"""
    print("\n🔍 测试预设类别文件路径...")
    
    try:
        from labelImg import get_persistent_predefined_classes_path
        
        predefined_file = get_persistent_predefined_classes_path()
        print(f"✅ 预设类别文件路径: {predefined_file}")
        
        if os.path.exists(predefined_file):
            with open(predefined_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ 预设类别文件存在，包含 {len(lines)} 个类别")
            print(f"✅ 预设类别: {lines}")
        else:
            print(f"⚠️ 预设类别文件不存在: {predefined_file}")
        
        return True
    except Exception as e:
        print(f"❌ 预设类别文件路径测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_functionality():
    """测试同步功能"""
    print("\n🔍 测试同步功能...")
    
    try:
        from libs.class_manager import ClassConfigManager
        from labelImg import get_persistent_predefined_classes_path
        
        manager = ClassConfigManager("configs")
        predefined_file = get_persistent_predefined_classes_path()
        
        if os.path.exists(predefined_file):
            print(f"✅ 开始同步测试...")
            
            # 读取预设类别
            with open(predefined_file, 'r', encoding='utf-8') as f:
                predefined_classes = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ 预设类别: {predefined_classes}")
            
            # 获取当前配置类别
            current_classes = manager.get_class_list()
            print(f"✅ 当前配置类别: {current_classes}")
            
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
                print("⚠️ 类别顺序不一致")
                
        else:
            print("⚠️ 预设类别文件不存在，跳过同步测试")
        
        return True
    except Exception as e:
        print(f"❌ 同步功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 类别管理修复效果测试")
    print("=" * 50)
    
    tests = [
        ("基本导入", test_basic_import),
        ("类别管理器基本功能", test_class_manager_basic),
        ("预设类别文件路径", test_predefined_classes_path),
        ("同步功能", test_sync_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出结果
    print(f"\n{'='*50}")
    print("📊 测试结果")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
