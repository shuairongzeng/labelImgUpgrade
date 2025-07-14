#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试labelImg的调试输出功能
"""

import os
import sys
import subprocess

def test_debug_output():
    """测试调试输出"""
    print("🔧 测试labelImg调试输出功能")
    print("=" * 50)
    
    # 检查调试代码是否已添加
    print("\n1. 检查调试代码是否已添加...")
    
    with open('labelImg.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    debug_checks = [
        ('[DEBUG] PyInstaller环境检测到', 'PyInstaller环境检测'),
        ('[DEBUG] 开发环境检测到', '开发环境检测'),
        ('[DEBUG] 资源文件完整路径', '资源文件路径调试'),
        ('[DEBUG] 初始化预设类文件路径', '预设类文件初始化调试'),
        ('[DEBUG] load_predefined_classes被调用', '加载预设类调试'),
        ('[DEBUG] 文件存在检查结果', '文件存在性检查调试'),
    ]
    
    all_debug_found = True
    for debug_str, description in debug_checks:
        if debug_str in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_debug_found = False
    
    if all_debug_found:
        print("\n✅ 所有调试代码已正确添加")
    else:
        print("\n❌ 部分调试代码缺失")
    
    print("\n2. 调试信息说明:")
    print("添加的调试信息包括:")
    print("- 环境检测（PyInstaller vs 开发环境）")
    print("- 资源文件路径解析过程")
    print("- 预设类文件加载过程")
    print("- 文件存在性检查")
    print("- 目录内容列表（当文件不存在时）")
    print("- 错误详细信息")
    
    print("\n3. 打包建议:")
    print("现在可以重新打包程序，调试信息会显示:")
    print("- 程序运行在哪种环境（开发/打包）")
    print("- 使用的基础路径是什么")
    print("- 最终的文件路径是什么")
    print("- 文件是否真的存在")
    print("- 如果不存在，当前目录有什么文件")
    
    return all_debug_found

def show_packaging_commands():
    """显示打包命令"""
    print("\n" + "=" * 50)
    print("📦 重新打包命令:")
    print("\n方法1 (推荐，使用修复后的spec文件):")
    print("pyinstaller labelImg.spec")
    
    print("\n方法2 (使用原始命令):")
    print("pyinstaller --hidden-import=pyqt5 --hidden-import=lxml -F -n \"labelImg\" -c labelImg.py -p ./libs -p ./")
    
    print("\n🔍 运行打包后的程序:")
    print("运行 dist/labelImg.exe 后，您会看到详细的调试信息，包括:")
    print("- [DEBUG] ========== labelImg 启动调试信息 ==========")
    print("- [DEBUG] Python版本: ...")
    print("- [DEBUG] 当前工作目录: ...")
    print("- [DEBUG] PyInstaller环境检测到 (或 开发环境检测到)")
    print("- [DEBUG] _MEIPASS路径: ... (如果是打包环境)")
    print("- [DEBUG] 初始化预设类文件路径...")
    print("- [DEBUG] 资源文件完整路径: ...")
    print("- [DEBUG] 资源文件是否存在: True/False")
    print("- [DEBUG] load_predefined_classes被调用")
    print("- [DEBUG] 文件存在检查结果: True/False")
    
    print("\n如果仍然出现问题，调试信息会告诉您:")
    print("- 程序在哪个步骤失败")
    print("- 使用的路径是什么")
    print("- 当前目录有哪些文件")
    print("- 具体的错误信息")

def main():
    try:
        debug_ok = test_debug_output()
        show_packaging_commands()
        
        if debug_ok:
            print("\n🎉 调试功能已成功添加！")
            print("现在重新打包程序，运行时会显示详细的调试信息，")
            print("帮助您准确定位问题所在。")
        else:
            print("\n⚠️  部分调试功能可能有问题，请检查代码。")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
