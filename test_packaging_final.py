#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终打包测试和说明
"""

import os
import subprocess
import sys

def check_environment():
    """检查打包环境"""
    print("🔧 检查打包环境")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查必要文件和文件夹
    required_items = [
        ('labelImg.py', '主程序文件'),
        ('data', 'data文件夹'),
        ('data/predefined_classes.txt', '预设类文件'),
        ('resources', 'resources文件夹'),
        ('libs', 'libs文件夹'),
    ]
    
    all_exists = True
    for item, description in required_items:
        if os.path.exists(item):
            print(f"✅ {description}: {item}")
        else:
            print(f"❌ {description}: {item} (不存在)")
            all_exists = False
    
    return all_exists

def show_packaging_options():
    """显示打包选项"""
    print("\n📦 打包选项")
    print("=" * 50)
    
    print("\n方法1: 使用修复后的spec文件")
    print("pyinstaller labelImg.spec")
    
    print("\n方法2: 使用简化的spec文件")
    print("pyinstaller labelImg_simple.spec")
    
    print("\n方法3: 使用命令行参数 (Windows)")
    print('pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --add-data "data;data" --add-data "resources;resources" -F -n "labelImg" -c labelImg.py -p ./libs -p ./')
    
    print("\n方法4: 使用命令行参数 (跨平台)")
    print('pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --add-data "data:data" --add-data "resources:resources" -F -n "labelImg" -c labelImg.py -p ./libs -p ./')

def create_batch_file():
    """创建批处理文件"""
    print("\n📝 创建打包批处理文件")
    print("=" * 50)
    
    batch_content = '''@echo off
echo 开始打包labelImg...
echo.

echo 方法1: 使用spec文件
pyinstaller labelImg.spec
if %errorlevel% neq 0 (
    echo 方法1失败，尝试方法2...
    echo.
    
    echo 方法2: 使用命令行参数
    pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --add-data "data;data" --add-data "resources;resources" -F -n "labelImg" -c labelImg.py -p ./libs -p ./
    if %errorlevel% neq 0 (
        echo 打包失败！
        pause
        exit /b 1
    )
)

echo.
echo 打包完成！
echo 可执行文件位置: dist\\labelImg.exe
echo.
echo 测试运行...
cd dist
labelImg.exe
cd ..

pause
'''
    
    with open('打包labelImg.bat', 'w', encoding='gbk') as f:
        f.write(batch_content)
    
    print("✅ 创建了 '打包labelImg.bat' 批处理文件")
    print("   双击运行即可自动打包")

def show_troubleshooting():
    """显示故障排除信息"""
    print("\n🔍 故障排除")
    print("=" * 50)
    
    print("\n如果打包仍然失败:")
    print("1. 清理旧的构建文件:")
    print("   rmdir /s build")
    print("   rmdir /s dist")
    print("   del *.spec")
    
    print("\n2. 检查PyInstaller版本:")
    print("   pip show pyinstaller")
    print("   如果版本过旧，升级: pip install --upgrade pyinstaller")
    
    print("\n3. 使用详细日志:")
    print("   pyinstaller --log-level DEBUG labelImg.spec")
    
    print("\n4. 手动指定路径:")
    current_dir = os.getcwd().replace('\\', '\\\\')
    print(f'   pyinstaller --add-data "{current_dir}\\\\data;data" --add-data "{current_dir}\\\\resources;resources" -F labelImg.py')

def show_expected_output():
    """显示预期输出"""
    print("\n🎯 预期的调试输出")
    print("=" * 50)
    
    print("\n成功打包后，运行程序应该显示:")
    print("""
[DEBUG] ========== labelImg 启动调试信息 ==========
[DEBUG] PyInstaller环境检测到
[DEBUG] _MEIPASS路径: C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...
[DEBUG] 资源文件完整路径: C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...\\data\\predefined_classes.txt
[DEBUG] 资源文件是否存在: True  ← 这里应该是True
[DEBUG] 初始化预设类文件路径...
[DEBUG] default_prefdef_class_file参数: C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...\\data\\predefined_classes.txt
[DEBUG] 最终预设类文件路径: C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...\\data\\predefined_classes.txt
[DEBUG] 开始加载预设类文件...
[DEBUG] load_predefined_classes被调用
[DEBUG] 传入的文件路径: C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...\\data\\predefined_classes.txt
[DEBUG] 文件路径类型: <class 'str'>
[DEBUG] 检查文件是否存在: C:\\Users\\...\\AppData\\Local\\Temp\\_MEI...\\data\\predefined_classes.txt
[DEBUG] 文件存在检查结果: True  ← 这里应该是True
[DEBUG] 开始读取文件内容...
[DEBUG] 成功读取 X 行标签  ← 应该显示成功读取
[DEBUG] 检查标签历史记录...
[DEBUG] 标签历史记录包含 X 个标签
[DEBUG] 第一个标签: dog
""")
    
    print("如果仍然显示 'Not find:/data/predefined_classes.txt (optional)'")
    print("说明data文件夹仍然没有被正确打包。")

def main():
    print("🚀 labelImg 最终打包解决方案")
    print("=" * 60)
    
    try:
        env_ok = check_environment()
        
        if not env_ok:
            print("\n❌ 环境检查失败，请确保所有必要文件存在")
            return
        
        show_packaging_options()
        create_batch_file()
        show_troubleshooting()
        show_expected_output()
        
        print("\n" + "=" * 60)
        print("🎉 准备完成！")
        print("\n推荐步骤:")
        print("1. 运行: pyinstaller labelImg.spec")
        print("2. 如果失败，运行: pyinstaller labelImg_simple.spec")
        print("3. 如果还失败，双击运行 '打包labelImg.bat'")
        print("4. 测试: dist\\labelImg.exe")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
