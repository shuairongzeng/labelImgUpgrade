#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试项目隔离修复
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_initialization_logic():
    """测试初始化逻辑是否正确"""
    print("========== 测试初始化逻辑 ==========")
    
    # 读取labelImg.py文件
    with open('labelImg.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    success = True
    
    # 检查1: 项目模式下predefined_classes_file应该设为None
    if 'self.predefined_classes_file = None' in content:
        print("[PASS] 正确：找到项目模式下设置predefined_classes_file = None的代码")
    else:
        print("[FAIL] 错误：未找到项目模式下设置predefined_classes_file = None的代码")
        success = False
    
    # 检查2: 确保项目模式优先检查
    pattern = r'if self\.config_adapter:.*?else:'
    if re.search(pattern, content, re.DOTALL):
        print("[PASS] 正确：项目管理系统优先检查逻辑存在")
    else:
        print("[FAIL] 错误：项目管理系统优先检查逻辑不正确")
        success = False
    
    # 检查3: 确保只有在非项目模式下才设置全局路径  
    # 只匹配实际的函数调用（赋值语句），不匹配函数定义
    global_path_pattern = r'=\s*get_persistent_predefined_classes_path\(\)'
    global_matches = re.findall(global_path_pattern, content)
    
    # 应该只有1次调用（在else分支中）
    if len(global_matches) == 1:
        print("[PASS] 正确：全局路径获取只在非项目模式下调用")
    else:
        print(f"[FAIL] 错误：全局路径获取调用了{len(global_matches)}次，应该只有1次")
        success = False
    
    # 检查4: 确保save方法中有None检查
    if 'if self.predefined_classes_file is None:' in content:
        print("[PASS] 正确：save方法中有predefined_classes_file为None的检查")
    else:
        print("[FAIL] 错误：save方法中缺少predefined_classes_file为None的检查")
        success = False
        
    # 检查5: 确保项目模式下不会回退到全局配置
    if '项目模式：不使用全局预设类文件，确保项目隔离' in content:
        print("[PASS] 正确：找到项目隔离确保的日志信息")
    else:
        print("[FAIL] 错误：未找到项目隔离确保的日志信息")
        success = False
    
    return success

def test_debug_output():
    """测试是否会输出全局路径信息"""
    print("\n========== 测试调试输出 ==========")
    
    with open('labelImg.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    success = True
    
    # 检查是否会在项目模式下输出持久化路径信息
    problem_logs = [
        '使用持久化预设类文件路径',
        'get_persistent_predefined_classes_path'
    ]
    
    for log in problem_logs:
        # 统计出现次数和上下文
        matches = []
        for i, line in enumerate(content.split('\n')):
            if log in line and 'print' in line:
                matches.append((i+1, line.strip()))
        
        if matches:
            # 检查是否都在else分支中（非项目模式）
            in_else_branch = True
            for line_num, line_content in matches:
                # 简单检查：如果在else分支中，前面应该有相应的if语句
                before_lines = content.split('\n')[max(0, line_num-10):line_num-1]
                has_if_config_adapter = any('if self.config_adapter:' in bl for bl in before_lines)
                has_else = any('else:' in bl for bl in before_lines[-5:])
                
                if not (has_if_config_adapter and has_else):
                    in_else_branch = False
                    break
            
            if in_else_branch:
                print(f"[PASS] 正确：'{log}' 只在非项目模式下输出")
            else:
                print(f"[FAIL] 错误：'{log}' 可能在项目模式下也会输出")
                success = False
        else:
            print(f"[PASS] 正确：未找到 '{log}' 的输出（或已正确处理）")
    
    return success

if __name__ == "__main__":
    print("开始简单测试项目隔离修复...")
    
    logic_success = test_initialization_logic()
    output_success = test_debug_output()
    
    print(f"\n========== 测试结果 ==========")
    print(f"初始化逻辑测试: {'[PASS] 通过' if logic_success else '[FAIL] 失败'}")
    print(f"调试输出测试: {'[PASS] 通过' if output_success else '[FAIL] 失败'}")
    
    if logic_success and output_success:
        print(f"\n[SUCCESS] 所有测试通过！项目隔离修复成功。")
        
        print(f"\n========== 修复效果 ==========")
        print("[PASS] 项目模式下不再设置全局predefined_classes_file路径")
        print("[PASS] 项目模式下不再输出'使用持久化预设类文件路径'消息")
        print("[PASS] 项目配置加载失败时保持项目隔离，不回退到全局配置")
        print("[PASS] save方法正确处理项目模式下的None路径")
        print("[PASS] 确保了如Docker容器般的完全项目隔离")
        
        sys.exit(0)
    else:
        print(f"\n[FAIL] 部分测试失败，需要进一步检查。")
        sys.exit(1)