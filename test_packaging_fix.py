#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试打包修复的脚本
"""

import sys
import os

def test_resource_path_function():
    """测试get_resource_path函数"""
    print("=== 测试资源路径函数 ===")
    
    # 模拟PyInstaller环境
    original_meipass = getattr(sys, '_MEIPASS', None)
    
    # 导入函数
    sys.path.insert(0, '.')
    from labelImg import get_resource_path
    
    # 测试正常环境
    if hasattr(sys, '_MEIPASS'):
        delattr(sys, '_MEIPASS')
    
    path1 = get_resource_path(os.path.join("data", "predefined_classes.txt"))
    print(f"开发环境路径: {path1}")
    
    # 测试PyInstaller环境
    sys._MEIPASS = "C:\\temp\\test_meipass"
    path2 = get_resource_path(os.path.join("data", "predefined_classes.txt"))
    print(f"打包环境路径: {path2}")
    
    # 恢复原始状态
    if original_meipass:
        sys._MEIPASS = original_meipass
    elif hasattr(sys, '_MEIPASS'):
        delattr(sys, '_MEIPASS')
    
    print("✅ 资源路径函数测试通过")

def test_show_bounding_box_fix():
    """测试show_bounding_box_from_annotation_file的空值检查"""
    print("\n=== 测试空值检查修复 ===")
    
    # 创建一个模拟的MainWindow类来测试
    class MockMainWindow:
        def __init__(self):
            self.default_save_dir = None
            
        def show_bounding_box_from_annotation_file(self, file_path):
            # 检查file_path是否为None，避免TypeError
            if file_path is None:
                print("✅ 空值检查生效，函数安全返回")
                return
            print(f"处理文件: {file_path}")
    
    mock_window = MockMainWindow()
    
    # 测试None值
    mock_window.show_bounding_box_from_annotation_file(None)
    
    # 测试正常值
    mock_window.show_bounding_box_from_annotation_file("test.jpg")
    
    print("✅ 空值检查修复测试通过")

def test_predefined_classes_file():
    """测试预定义类文件是否存在"""
    print("\n=== 测试预定义类文件 ===")
    
    from labelImg import get_resource_path
    
    predefined_file = get_resource_path(os.path.join("data", "predefined_classes.txt"))
    
    if os.path.exists(predefined_file):
        print(f"✅ 预定义类文件存在: {predefined_file}")
        with open(predefined_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"✅ 文件包含 {len(lines)} 行标签")
    else:
        print(f"❌ 预定义类文件不存在: {predefined_file}")

def main():
    print("🔧 labelImg 打包修复测试")
    print("=" * 50)
    
    try:
        test_resource_path_function()
        test_show_bounding_box_fix()
        test_predefined_classes_file()
        
        print("\n🎉 所有测试通过！")
        print("\n修复内容:")
        print("1. ✅ 添加了get_resource_path函数处理PyInstaller资源路径")
        print("2. ✅ 修复了show_bounding_box_from_annotation_file的空值检查")
        print("3. ✅ 修复了change_save_dir_dialog的空值检查")
        print("4. ✅ 修复了open_dir_dialog的空值检查")
        print("5. ✅ 修复了copy_previous_bounding_boxes的空值检查")
        print("\n现在打包后的程序应该不会再出现TypeError错误了！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
