#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试PyInstaller的datas配置
"""

import os
import sys

def test_pyinstaller_datas():
    """测试PyInstaller的datas配置"""
    print("🔧 测试PyInstaller datas配置")
    print("=" * 50)
    
    # 1. 检查spec文件
    print("\n1. 检查spec文件配置...")
    with open('labelImg.spec', 'r', encoding='utf-8') as f:
        spec_content = f.read()
    
    if "datas=[('data', 'data')" in spec_content:
        print("✅ spec文件包含data文件夹配置")
    else:
        print("❌ spec文件缺少data文件夹配置")
        print("当前spec文件内容:")
        print(spec_content)
        return False
    
    if "('resources', 'resources')" in spec_content:
        print("✅ spec文件包含resources文件夹配置")
    else:
        print("❌ spec文件缺少resources文件夹配置")
    
    # 2. 检查源文件夹
    print("\n2. 检查源文件夹...")
    if os.path.exists('data'):
        print("✅ data文件夹存在")
        data_files = os.listdir('data')
        print(f"   data文件夹内容: {data_files}")
    else:
        print("❌ data文件夹不存在")
        return False
    
    if os.path.exists('resources'):
        print("✅ resources文件夹存在")
        resources_files = os.listdir('resources')
        print(f"   resources文件夹内容: {resources_files}")
    else:
        print("❌ resources文件夹不存在")
    
    # 3. 检查当前工作目录
    print(f"\n3. 当前工作目录: {os.getcwd()}")
    current_files = os.listdir('.')
    print(f"   当前目录内容: {current_files}")
    
    return True

def create_alternative_spec():
    """创建一个替代的spec文件，使用绝对路径"""
    print("\n4. 创建替代spec文件...")
    
    current_dir = os.getcwd()
    data_path = os.path.join(current_dir, 'data')
    resources_path = os.path.join(current_dir, 'resources')
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['labelImg.py'],
    pathex=['{current_dir}\\libs', '{current_dir}'],
    binaries=[],
    datas=[(r'{data_path}', 'data'), (r'{resources_path}', 'resources')],
    hiddenimports=['pyqt5', 'lxml'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='labelImg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open('labelImg_fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建了labelImg_fixed.spec文件，使用绝对路径")
    print(f"   data路径: {data_path}")
    print(f"   resources路径: {resources_path}")

def show_packaging_instructions():
    """显示打包说明"""
    print("\n" + "=" * 50)
    print("📦 重新打包说明:")
    
    print("\n方法1: 使用修复后的spec文件")
    print("pyinstaller labelImg.spec")
    
    print("\n方法2: 使用新创建的绝对路径spec文件")
    print("pyinstaller labelImg_fixed.spec")
    
    print("\n方法3: 直接使用命令行参数")
    current_dir = os.getcwd()
    data_path = os.path.join(current_dir, 'data')
    resources_path = os.path.join(current_dir, 'resources')
    print(f'pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --add-data "{data_path};data" --add-data "{resources_path};resources" -F -n "labelImg" -c labelImg.py -p ./libs -p ./')
    
    print("\n🔍 验证打包结果:")
    print("打包完成后，运行程序应该显示:")
    print("[DEBUG] 资源文件是否存在: True")
    print("[DEBUG] 成功读取 X 行标签")
    
    print("\n如果仍然失败，请检查:")
    print("1. 确保在正确的目录下运行打包命令")
    print("2. 确保data和resources文件夹在当前目录下")
    print("3. 尝试使用绝对路径的spec文件")

def main():
    try:
        if test_pyinstaller_datas():
            create_alternative_spec()
            show_packaging_instructions()
            print("\n🎉 配置检查完成！请尝试重新打包。")
        else:
            print("\n❌ 配置检查失败，请先修复配置问题。")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
