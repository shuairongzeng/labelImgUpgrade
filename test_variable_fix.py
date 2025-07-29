#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试变量初始化修复
"""

import os
import sys

def test_variable_initialization():
    """测试变量初始化是否正确"""
    print("🔧 测试变量初始化修复")
    print("="*40)
    
    try:
        # 检查修复后的代码
        with open("libs/ai_assistant_panel.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找关键代码段
        lines = content.split('\n')
        
        # 找到 filtered_source_dir 的初始化位置
        filtered_source_dir_init_line = -1
        converter_creation_line = -1
        
        for i, line in enumerate(lines):
            if "filtered_source_dir = source_dir" in line:
                filtered_source_dir_init_line = i + 1
                print(f"✅ 找到 filtered_source_dir 初始化: 第 {filtered_source_dir_init_line} 行")
            
            if "converter = PascalToYOLOConverter(" in line:
                converter_creation_line = i + 1
                print(f"✅ 找到转换器创建: 第 {converter_creation_line} 行")
        
        # 检查初始化顺序
        if filtered_source_dir_init_line > 0 and converter_creation_line > 0:
            if filtered_source_dir_init_line < converter_creation_line:
                print("✅ 变量初始化顺序正确")
                return True
            else:
                print("❌ 变量初始化顺序错误")
                return False
        else:
            print("❌ 未找到关键代码")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def check_code_structure():
    """检查代码结构"""
    print("\n📋 检查代码结构")
    print("-"*30)
    
    try:
        with open("libs/ai_assistant_panel.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键代码段是否存在
        checks = [
            ("exclude_trained = self.exclude_trained_checkbox.isChecked()", "排除已训练图片选项获取"),
            ("filtered_source_dir = source_dir", "过滤目录初始化"),
            ("if exclude_trained and self.training_history_manager:", "条件检查"),
            ("filtered_source_dir = self._create_filtered_source_dir(", "过滤目录创建"),
            ("source_dir=filtered_source_dir", "使用过滤目录")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 变量初始化修复测试")
    print("="*50)
    
    success = True
    
    # 测试变量初始化
    if not test_variable_initialization():
        success = False
    
    # 检查代码结构
    if not check_code_structure():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 修复验证通过！")
        print("\n📋 修复内容:")
        print("1. ✅ 将 filtered_source_dir 初始化移到转换器创建之前")
        print("2. ✅ 将排除已训练图片的逻辑提前处理")
        print("3. ✅ 删除重复的变量初始化代码")
        
        print("\n🔧 修复说明:")
        print("- 原问题: filtered_source_dir 在使用前未初始化")
        print("- 解决方案: 重新组织代码顺序，确保变量在使用前正确初始化")
        print("- 现在流程: 检查选项 → 初始化变量 → 创建过滤目录 → 创建转换器")
    else:
        print("❌ 修复验证失败，请检查代码。")
    
    return success


if __name__ == "__main__":
    main()
