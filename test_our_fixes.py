#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试我们的三个修复功能
"""

import os
import sys
import inspect

def test_reset_all_method():
    """测试reset_all方法是否包含自动重启逻辑"""
    print("=" * 60)
    print("测试1: reset_all方法自动重启功能")
    print("=" * 60)
    
    try:
        # 读取labelImg.py文件内容
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查reset_all方法是否包含必要的逻辑
        checks = [
            ('确认对话框', 'QMessageBox.question' in content),
            ('重置设置', 'self.settings.reset()' in content),
            ('获取启动参数', 'sys.argv[:]' in content),
            ('启动新进程', 'process.startDetached' in content),
            ('Python脚本检测', "current_args[0].endswith('.py')" in content)
        ]
        
        print("检查reset_all方法修复:")
        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}: {'通过' if result else '失败'}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def test_window_centering_logic():
    """测试窗口居中逻辑"""
    print("\n" + "=" * 60)
    print("测试2: 窗口居中逻辑")
    print("=" * 60)
    
    try:
        # 读取labelImg.py文件内容
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查窗口居中逻辑是否包含必要的修改
        checks = [
            ('首次启动检测', 'is_fresh_start = not os.path.exists' in content),
            ('设置文件检测', 'len(settings.data) == 0' in content),
            ('条件判断修改', 'if not is_fresh_start:' in content),
            ('居中条件', 'if not has_valid_saved_position or is_fresh_start:' in content),
            ('屏幕几何计算', 'screen.width() - size.width()' in content)
        ]
        
        print("检查窗口居中逻辑修复:")
        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}: {'通过' if result else '失败'}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def test_open_dir_dialog_fix():
    """测试打开文件夹对话框修复"""
    print("\n" + "=" * 60)
    print("测试3: 打开文件夹流程优化")
    print("=" * 60)
    
    try:
        # 读取labelImg.py文件内容
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查open_dir_dialog方法是否包含必要的修改
        checks = [
            ('直接设置保存目录', 'self.default_save_dir = target_dir_path' in content),
            ('状态栏更新', "self.statusBar().showMessage('%s . Annotation will be saved to %s'" in content),
            ('Open Directory消息', "'Open Directory'" in content),
            ('状态栏显示', 'self.statusBar().show()' in content)
        ]
        
        print("检查打开文件夹流程修复:")
        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}: {'通过' if result else '失败'}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        return False

def test_code_syntax():
    """测试代码语法是否正确"""
    print("\n" + "=" * 60)
    print("测试4: 代码语法检查")
    print("=" * 60)
    
    try:
        # 尝试编译labelImg.py
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'labelImg.py', 'exec')
        print("✓ 代码语法检查通过")
        return True
        
    except SyntaxError as e:
        print(f"✗ 语法错误: {e}")
        print(f"  行号: {e.lineno}")
        print(f"  错误位置: {e.text}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

def main():
    """主测试函数"""
    print("labelImg功能修复验证")
    print("验证时间:", __import__('time').strftime("%Y-%m-%d %H:%M:%S"))
    print("当前目录:", os.getcwd())
    
    # 检查labelImg.py文件是否存在
    if not os.path.exists('labelImg.py'):
        print("✗ 错误: 找不到labelImg.py文件")
        return
    
    # 执行测试
    tests = [
        ("reset_all方法自动重启", test_reset_all_method),
        ("窗口居中逻辑", test_window_centering_logic),
        ("打开文件夹流程", test_open_dir_dialog_fix),
        ("代码语法检查", test_code_syntax)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ 测试 {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有修复验证通过！")
        print("\n修复功能说明:")
        print("1. 全部重置功能现在会显示确认对话框，并在用户确认后自动重启程序")
        print("2. 程序重启后会自动居中显示，不再使用之前保存的位置")
        print("3. 打开文件夹时不再弹出第二次保存目录选择框，直接使用图片目录作为标注保存目录")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查相关功能")

if __name__ == "__main__":
    main()
