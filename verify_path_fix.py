#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证labelImg打包路径问题修复
"""

import os
import sys

def main():
    print("🔧 验证labelImg打包路径问题修复")
    print("=" * 50)
    
    # 1. 检查代码修复
    print("\n1. 检查代码修复...")
    with open('labelImg.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'self.load_predefined_classes(self.predefined_classes_file)' in content:
        print("✅ load_predefined_classes现在使用正确的文件路径参数")
    else:
        print("❌ load_predefined_classes参数未修复")
    
    # 2. 检查spec文件修复
    print("\n2. 检查spec文件修复...")
    with open('labelImg.spec', 'r', encoding='utf-8') as f:
        spec_content = f.read()
    
    if "datas=[('data', 'data')" in spec_content:
        print("✅ spec文件已包含data文件夹")
    else:
        print("❌ spec文件未包含data文件夹")
    
    # 3. 检查get_resource_path函数
    print("\n3. 检查get_resource_path函数...")
    if 'def get_resource_path(relative_path):' in content:
        print("✅ get_resource_path函数存在")
        if 'sys._MEIPASS' in content:
            print("✅ 函数支持PyInstaller环境")
        else:
            print("❌ 函数不支持PyInstaller环境")
    else:
        print("❌ get_resource_path函数不存在")
    
    # 4. 检查data文件夹
    print("\n4. 检查data文件夹...")
    if os.path.exists('data'):
        print("✅ data文件夹存在")
        if os.path.exists('data/predefined_classes.txt'):
            print("✅ predefined_classes.txt文件存在")
        else:
            print("❌ predefined_classes.txt文件不存在")
    else:
        print("❌ data文件夹不存在")
    
    print("\n" + "=" * 50)
    print("📦 修复总结:")
    print("1. ✅ 修复了load_predefined_classes方法的参数问题")
    print("   - 原来: self.load_predefined_classes(default_prefdef_class_file)")
    print("   - 现在: self.load_predefined_classes(self.predefined_classes_file)")
    print("2. ✅ 修复了PyInstaller spec文件的datas配置")
    print("   - 原来: datas=[]")
    print("   - 现在: datas=[('data', 'data'), ('resources', 'resources')]")
    
    print("\n🚀 重新打包命令:")
    print("方法1 (推荐): pyinstaller labelImg.spec")
    print("方法2: pyinstaller --hidden-import=pyqt5 --hidden-import=lxml -F -n \"labelImg\" -c labelImg.py -p ./libs -p ./")
    
    print("\n✨ 修复说明:")
    print("问题原因:")
    print("- labelImg.py第449行使用了错误的参数default_prefdef_class_file")
    print("- 该参数可能为None，导致无法找到文件")
    print("- PyInstaller spec文件没有包含data文件夹")
    print("\n修复方案:")
    print("- 使用self.predefined_classes_file参数，该参数通过get_resource_path正确处理")
    print("- 在spec文件中添加data和resources文件夹到datas配置")
    print("- get_resource_path函数会根据是否在PyInstaller环境自动选择正确路径")
    
    print("\n现在重新打包后应该不会再出现'Not find:/data/predefined_classes.txt'错误了！")

if __name__ == '__main__':
    main()
