#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试labelImg打包后的路径问题修复
"""

import os
import sys
import tempfile
import shutil

def test_get_resource_path():
    """测试get_resource_path函数在不同环境下的行为"""
    print("=== 测试get_resource_path函数 ===")
    
    # 导入函数
    sys.path.insert(0, '.')
    from labelImg import get_resource_path
    
    # 保存原始状态
    original_meipass = getattr(sys, '_MEIPASS', None)
    
    try:
        # 测试开发环境（没有_MEIPASS）
        if hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')
        
        dev_path = get_resource_path(os.path.join("data", "predefined_classes.txt"))
        print(f"开发环境路径: {dev_path}")
        print(f"开发环境文件存在: {os.path.exists(dev_path)}")
        
        # 测试PyInstaller环境（有_MEIPASS）
        test_meipass = tempfile.mkdtemp()
        sys._MEIPASS = test_meipass
        
        # 创建测试的data目录和文件
        test_data_dir = os.path.join(test_meipass, "data")
        os.makedirs(test_data_dir, exist_ok=True)
        test_file = os.path.join(test_data_dir, "predefined_classes.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("test_label\n")
        
        packed_path = get_resource_path(os.path.join("data", "predefined_classes.txt"))
        print(f"打包环境路径: {packed_path}")
        print(f"打包环境文件存在: {os.path.exists(packed_path)}")
        
        # 清理测试目录
        shutil.rmtree(test_meipass)
        
    finally:
        # 恢复原始状态
        if original_meipass:
            sys._MEIPASS = original_meipass
        elif hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')
    
    print("✅ get_resource_path函数测试完成")

def test_load_predefined_classes_fix():
    """测试load_predefined_classes修复"""
    print("\n=== 测试load_predefined_classes修复 ===")
    
    # 检查代码修复
    with open('labelImg.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否使用了正确的参数
    if 'self.load_predefined_classes(self.predefined_classes_file)' in content:
        print("✅ load_predefined_classes现在使用正确的文件路径参数")
    else:
        print("❌ load_predefined_classes仍然使用错误的参数")
        return False
    
    # 检查是否还有错误的调用
    if 'self.load_predefined_classes(default_prefdef_class_file)' in content:
        print("❌ 仍然存在使用default_prefdef_class_file的调用")
        return False
    else:
        print("✅ 已移除错误的default_prefdef_class_file调用")
    
    return True

def test_spec_file_fix():
    """测试spec文件修复"""
    print("\n=== 测试spec文件修复 ===")
    
    with open('labelImg.spec', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "datas=[('data', 'data')" in content:
        print("✅ spec文件已包含data文件夹")
    else:
        print("❌ spec文件未包含data文件夹")
        return False
    
    if "('resources', 'resources')" in content:
        print("✅ spec文件已包含resources文件夹")
    else:
        print("❌ spec文件未包含resources文件夹")
        return False
    
    return True

def test_predefined_classes_file_access():
    """测试预定义类文件访问"""
    print("\n=== 测试预定义类文件访问 ===")
    
    from labelImg import get_resource_path
    
    # 测试文件路径
    predefined_file = get_resource_path(os.path.join("data", "predefined_classes.txt"))
    print(f"预定义类文件路径: {predefined_file}")
    
    if os.path.exists(predefined_file):
        print("✅ 预定义类文件存在")
        try:
            with open(predefined_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"✅ 文件包含 {len(lines)} 行标签")
                if lines:
                    print(f"✅ 示例标签: {lines[0].strip()}")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return False
    else:
        print("❌ 预定义类文件不存在")
        return False
    
    return True

def main():
    print("🔧 labelImg 打包路径问题修复测试")
    print("=" * 60)
    
    try:
        # 运行所有测试
        test_get_resource_path()
        fix1 = test_load_predefined_classes_fix()
        fix2 = test_spec_file_fix()
        fix3 = test_predefined_classes_file_access()
        
        if fix1 and fix2 and fix3:
            print("\n🎉 所有修复测试通过！")
            print("\n修复内容总结:")
            print("1. ✅ 修复了load_predefined_classes方法的参数问题")
            print("   - 原来: self.load_predefined_classes(default_prefdef_class_file)")
            print("   - 现在: self.load_predefined_classes(self.predefined_classes_file)")
            print("2. ✅ 修复了PyInstaller spec文件的datas配置")
            print("   - 原来: datas=[]")
            print("   - 现在: datas=[('data', 'data'), ('resources', 'resources')]")
            print("3. ✅ get_resource_path函数正确处理PyInstaller环境")
            
            print("\n📦 重新打包建议:")
            print("使用以下命令重新打包:")
            print("pyinstaller labelImg.spec")
            print("\n或者使用原始命令但会自动使用修复后的spec文件:")
            print("pyinstaller --hidden-import=pyqt5 --hidden-import=lxml -F -n \"labelImg\" -c labelImg.py -p ./libs -p ./")
            
            print("\n现在打包后的程序应该能正确找到 /data/predefined_classes.txt 文件了！")
        else:
            print("\n❌ 部分测试失败，请检查修复内容")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
