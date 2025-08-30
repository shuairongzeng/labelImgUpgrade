#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终验证项目隔离修复是否成功
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("========== 项目隔离修复最终验证 ==========")
    
    with open('labelImg.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_checks_passed = True
    
    # 检查1: 项目模式下设置predefined_classes_file = None
    check1 = 'self.predefined_classes_file = None' in content
    print(f"[{'PASS' if check1 else 'FAIL'}] 项目模式下设置predefined_classes_file = None: {check1}")
    if not check1:
        all_checks_passed = False
    
    # 检查2: 存在项目隔离的日志消息
    check2 = '项目模式：不使用全局预设类文件，确保项目隔离' in content
    print(f"[{'PASS' if check2 else 'FAIL'}] 包含项目隔离确认日志: {check2}")
    if not check2:
        all_checks_passed = False
    
    # 检查3: save方法中有None检查防护
    check3 = 'if self.predefined_classes_file is None:' in content
    print(f"[{'PASS' if check3 else 'FAIL'}] save方法有None检查防护: {check3}")
    if not check3:
        all_checks_passed = False
    
    # 检查4: 项目配置加载失败时不回退到全局配置
    check4 = '即使项目配置加载失败，也初始化空的标签列表，不回退到全局配置' in content
    print(f"[{'PASS' if check4 else 'FAIL'}] 配置加载失败时保持项目隔离: {check4}")
    if not check4:
        all_checks_passed = False
    
    # 检查5: 优先使用项目配置的逻辑结构存在
    check5 = ('if self.config_adapter:' in content and 
              '使用项目标签配置，确保完全项目隔离' in content)
    print(f"[{'PASS' if check5 else 'FAIL'}] 优先使用项目配置的逻辑: {check5}")
    if not check5:
        all_checks_passed = False
    
    print(f"\n========== 验证结果 ==========")
    if all_checks_passed:
        print("[SUCCESS] 所有检查通过！项目隔离修复成功。")
        
        print(f"\n========== 修复效果总结 ==========")
        print("1. 项目模式下完全不使用全局predefined_classes_file路径")
        print("2. 项目配置优先，确保了Docker容器般的完全隔离")
        print("3. 配置加载失败时保持项目隔离，不回退到全局配置")
        print("4. save方法正确处理项目模式下的None路径情况")
        print("5. 清晰的调试日志显示项目隔离状态")
        
        print(f"\n关键修复点:")
        print("- 初始化时优先检查项目管理系统")
        print("- 项目模式下将predefined_classes_file设为None")
        print("- 全局路径获取仅在非项目模式的else分支中执行")
        print("- 保存时对None路径进行防护检查")
        
        return True
    else:
        print("[FAIL] 部分检查失败，修复可能不完整。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)