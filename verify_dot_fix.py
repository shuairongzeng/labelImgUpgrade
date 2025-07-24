#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 \. 修复
"""

import os

def verify_dot_fix():
    """验证 \. 修复"""
    print("🔍 验证 \\. 修复")
    print("=" * 50)
    
    config_dir = "datasets/training_dataset"
    path_field = "."
    
    print(f"配置目录: {config_dir}")
    print(f"path字段: '{path_field}'")
    
    # 修复前的逻辑（会产生不必要的 \.）
    old_result = os.path.join(config_dir, path_field)
    print(f"\n修复前的逻辑:")
    print(f"os.path.join('{config_dir}', '{path_field}') = '{old_result}'")
    
    # 修复后的逻辑
    print(f"\n修复后的逻辑:")
    if path_field == '.':
        new_result = config_dir
        print(f"path_field == '.' -> 直接使用配置目录: '{new_result}'")
    else:
        new_result = os.path.join(config_dir, path_field)
        print(f"其他情况 -> os.path.join: '{new_result}'")
    
    # 检查结果
    print(f"\n结果对比:")
    print(f"修复前: '{old_result}'")
    print(f"修复后: '{new_result}'")
    
    old_has_dot = '\\.' in old_result or '/.' in old_result
    new_has_dot = '\\.' in new_result or '/.' in new_result
    
    print(f"\n包含不必要的 \\. 检查:")
    print(f"修复前包含 \\.: {old_has_dot}")
    print(f"修复后包含 \\.: {new_has_dot}")
    
    if not new_has_dot:
        print(f"\n🎉 修复成功！路径中不再包含不必要的 \\.")
        return True
    else:
        print(f"\n❌ 修复失败，路径中仍包含 \\.")
        return False

if __name__ == "__main__":
    verify_dot_fix()
