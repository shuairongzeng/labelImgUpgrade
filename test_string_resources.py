#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试字符串资源是否正确加载
"""
import sys
import os

# 添加libs目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def test_string_bundle():
    """测试字符串资源"""
    print("测试字符串资源加载...")
    
    try:
        from libs.stringBundle import StringBundle
        
        # 获取字符串包
        string_bundle = StringBundle.get_bundle()
        
        # 测试新添加的字符串
        test_strings = [
            'exportYOLO',
            'exportYOLODetail',
            'exportYOLODialog',
            'selectExportDir',
            'datasetName',
            'trainRatio',
            'exportProgress',
            'exportComplete',
            'exportSuccess',
            'exportError',
            'noAnnotations',
            'invalidDirectory',
            'processingFiles',
            'copyingImages',
            'generatingConfig',
            'exportCancelled'
        ]
        
        print("测试新增的字符串资源:")
        for string_id in test_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ {string_id}: {value}")
            except Exception as e:
                print(f"❌ {string_id}: {e}")
        
        # 测试一些现有的字符串
        print("\n测试现有的字符串资源:")
        existing_strings = ['openFile', 'save', 'quit', 'menu_file']
        for string_id in existing_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ {string_id}: {value}")
            except Exception as e:
                print(f"❌ {string_id}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 字符串资源测试失败: {e}")
        return False

def test_yolo_converter_import():
    """测试YOLO转换器导入"""
    print("\n测试YOLO转换器导入...")
    
    try:
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        print("✅ PascalToYOLOConverter 导入成功")
        
        # 测试创建实例
        converter = PascalToYOLOConverter("./test", "./output", "test")
        print("✅ 转换器实例创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 转换器导入失败: {e}")
        return False

def test_dialog_import():
    """测试对话框导入"""
    print("\n测试对话框导入...")
    
    try:
        from libs.yolo_export_dialog import YOLOExportDialog
        print("✅ YOLOExportDialog 导入成功")
        return True
    except Exception as e:
        print(f"❌ 对话框导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("字符串资源和模块导入测试")
    print("=" * 50)
    
    tests = [
        ("字符串资源", test_string_bundle),
        ("YOLO转换器", test_yolo_converter_import),
        ("导出对话框", test_dialog_import)
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
        print("🎉 所有测试通过! labelImg的YOLO导出功能已准备就绪。")
    else:
        print("⚠️ 部分测试失败，请检查相关模块。")
    
    return passed == len(results)

if __name__ == "__main__":
    main()
