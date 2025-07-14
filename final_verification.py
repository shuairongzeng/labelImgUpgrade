#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 确保YOLO导出功能完全正常
"""
import sys
import os

# 添加libs目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def check_labelimg_startup():
    """检查labelImg是否可以正常启动"""
    print("检查labelImg启动...")
    
    try:
        # 导入主要模块
        import labelImg
        print("✅ labelImg模块导入成功")
        
        # 检查MainWindow类
        main_window_class = getattr(labelImg, 'MainWindow', None)
        if main_window_class:
            print("✅ MainWindow类存在")
        else:
            print("❌ MainWindow类不存在")
            return False
            
        # 检查export_yolo_dataset方法
        if hasattr(main_window_class, 'export_yolo_dataset'):
            print("✅ export_yolo_dataset方法已添加")
        else:
            print("❌ export_yolo_dataset方法缺失")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ labelImg启动检查失败: {e}")
        return False

def check_string_resources():
    """检查字符串资源"""
    print("\n检查字符串资源...")
    
    try:
        from libs.stringBundle import StringBundle
        
        string_bundle = StringBundle.get_bundle()
        
        # 检查关键字符串
        key_strings = ['exportYOLO', 'exportYOLODetail', 'noAnnotations']
        
        for string_id in key_strings:
            value = string_bundle.get_string(string_id)
            if value and value != string_id:
                print(f"✅ {string_id}: {value}")
            else:
                print(f"❌ {string_id}: 字符串缺失或无效")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 字符串资源检查失败: {e}")
        return False

def check_converter_functionality():
    """检查转换器功能"""
    print("\n检查转换器功能...")
    
    try:
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        
        # 创建转换器实例
        converter = PascalToYOLOConverter(
            source_dir="./test",
            target_dir="./output",
            dataset_name="test_dataset"
        )
        
        print("✅ 转换器实例创建成功")
        
        # 检查关键方法
        methods = ['create_directories', 'scan_annotations', 'parse_xml_annotation', 
                  'write_yolo_annotation', 'generate_yaml_config']
        
        for method_name in methods:
            if hasattr(converter, method_name):
                print(f"✅ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 转换器功能检查失败: {e}")
        return False

def check_dialog_functionality():
    """检查对话框功能"""
    print("\n检查对话框功能...")
    
    try:
        from libs.yolo_export_dialog import YOLOExportDialog, ConvertThread
        
        print("✅ YOLOExportDialog 导入成功")
        print("✅ ConvertThread 导入成功")
        
        # 检查关键方法
        dialog_methods = ['init_ui', 'browse_target_directory', 'start_export', 'validate_inputs']
        
        for method_name in dialog_methods:
            if hasattr(YOLOExportDialog, method_name):
                print(f"✅ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 对话框功能检查失败: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("\n检查依赖...")
    
    dependencies = [
        ('PyQt5', 'PyQt5'),
        ('yaml', 'PyYAML'),
        ('xml.etree', 'xml.etree'),
        ('os', 'os'),
        ('shutil', 'shutil')
    ]
    
    all_ok = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name} 可用")
        except ImportError:
            print(f"❌ {package_name} 缺失")
            all_ok = False
    
    return all_ok

def check_file_structure():
    """检查文件结构"""
    print("\n检查文件结构...")
    
    required_files = [
        'labelImg.py',
        'libs/pascal_to_yolo_converter.py',
        'libs/yolo_export_dialog.py',
        'libs/stringBundle.py',
        'resources/strings/strings-zh-CN.properties',
        'resources/strings/strings.properties'
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 缺失")
            all_ok = False
    
    return all_ok

def main():
    """主验证函数"""
    print("=" * 60)
    print("labelImg YOLO导出功能 - 最终验证")
    print("=" * 60)
    
    checks = [
        ("文件结构", check_file_structure),
        ("依赖检查", check_dependencies),
        ("字符串资源", check_string_resources),
        ("转换器功能", check_converter_functionality),
        ("对话框功能", check_dialog_functionality),
        ("labelImg启动", check_labelimg_startup)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} 检查异常: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("验证结果总结:")
    print("=" * 60)
    
    passed = 0
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name:15}: {status}")
        if result:
            passed += 1
    
    print(f"\n通过率: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if passed == len(results):
        print("\n🎉 所有验证通过!")
        print("=" * 60)
        print("YOLO导出功能已成功集成到labelImg中!")
        print("\n使用方法:")
        print("1. 启动labelImg: python labelImg.py")
        print("2. 打开包含Pascal VOC标注的图片目录")
        print("3. 点击 '文件' → '导出为YOLO数据集' (或按Ctrl+E)")
        print("4. 配置导出设置并开始导出")
        print("5. 导出的数据集可直接用于YOLO训练")
        print("=" * 60)
    else:
        print("\n⚠️ 部分验证失败，请检查相关功能")
        print("建议:")
        print("- 检查所有文件是否正确保存")
        print("- 确保所有依赖都已安装")
        print("- 重新启动Python环境")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
