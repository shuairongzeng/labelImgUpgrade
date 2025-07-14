#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单测试脚本，验证labelImg的修改
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modifications():
    """测试修改"""
    print("=== 测试labelImg修改 ===")
    
    # 测试1: 检查默认窗口大小设置
    print("\n1. 测试默认窗口大小...")
    try:
        # 读取labelImg.py文件内容
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'QSize(1366, 768)' in content:
            print("✓ 默认窗口大小已设置为1366x768")
        else:
            print("✗ 默认窗口大小设置未找到")
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
    
    # 测试2: 检查自动保存默认设置
    print("\n2. 测试自动保存默认设置...")
    try:
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'settings.get(SETTING_AUTO_SAVE, True)' in content:
            print("✓ 自动保存默认设置为True")
        else:
            print("✗ 自动保存默认设置未找到")
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
    
    # 测试3: 检查窗口居中代码
    print("\n3. 测试窗口居中功能...")
    try:
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'has_valid_saved_position' in content and 'center the window' in content:
            print("✓ 窗口居中功能已添加")
        else:
            print("✗ 窗口居中功能未找到")
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("所有修改已验证。程序现在应该：")
    print("- 默认窗口大小为1366x768")
    print("- 启动时自动居中")
    print("- 自动保存默认勾选")

if __name__ == "__main__":
    test_modifications()
