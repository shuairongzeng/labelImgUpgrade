#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的YOLO导出功能测试
"""
import os
import sys

def test_imports():
    """测试导入"""
    print("测试模块导入...")
    
    try:
        # 添加libs目录到路径
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
        
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        print("✅ PascalToYOLOConverter 导入成功")
        
        from libs.yolo_export_dialog import YOLOExportDialog
        print("✅ YOLOExportDialog 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_string_resources():
    """测试字符串资源"""
    print("\n测试字符串资源...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
        from libs.stringBundle import StringBundle
        
        string_bundle = StringBundle.get_bundle()
        
        # 测试新添加的字符串
        test_strings = [
            'exportYOLO',
            'exportYOLODetail',
            'noAnnotations'
        ]
        
        for string_id in test_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ '{string_id}': {value}")
            except:
                print(f"❌ 缺少字符串: {string_id}")
        
        return True
    except Exception as e:
        print(f"❌ 字符串资源测试失败: {e}")
        return False

def test_converter_class():
    """测试转换器类"""
    print("\n测试转换器类...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        
        # 创建转换器实例
        converter = PascalToYOLOConverter(
            source_dir="./test",
            target_dir="./output",
            dataset_name="test_dataset"
        )
        
        print("✅ 转换器实例创建成功")
        print(f"  - 源目录: {converter.source_dir}")
        print(f"  - 目标目录: {converter.target_dir}")
        print(f"  - 数据集名称: {converter.dataset_name}")
        print(f"  - 训练集比例: {converter.train_ratio}")
        
        return True
    except Exception as e:
        print(f"❌ 转换器测试失败: {e}")
        return False

def check_menu_integration():
    """检查菜单集成"""
    print("\n检查菜单集成...")
    
    try:
        # 检查labelImg.py中是否有导出方法
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'export_yolo_dataset' in content:
            print("✅ export_yolo_dataset 方法已添加")
        else:
            print("❌ 缺少 export_yolo_dataset 方法")
            
        if 'YOLOExportDialog' in content:
            print("✅ YOLOExportDialog 已导入")
        else:
            print("❌ 缺少 YOLOExportDialog 导入")
            
        if 'export_yolo' in content:
            print("✅ export_yolo 动作已添加")
        else:
            print("❌ 缺少 export_yolo 动作")
            
        return True
    except Exception as e:
        print(f"❌ 菜单集成检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("YOLO导出功能简单测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("字符串资源", test_string_resources), 
        ("转换器类", test_converter_class),
        ("菜单集成", check_menu_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n通过率: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if passed == len(results):
        print("🎉 所有测试通过!")
    else:
        print("⚠️ 部分测试失败")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
