#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试中文转拼音功能
"""

import sys
import os

# 添加libs目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from pinyin_utils import process_label_text, has_chinese, chinese_to_pinyin

def test_pinyin_conversion():
    """测试中文转拼音功能"""
    test_cases = [
        ("称号", "chengHao"),
        ("人物", "renWu"),
        ("汽车", "qiChe"),
        ("动物", "dongWu"),
        ("建筑", "jianZhu"),
        ("食品", "shiPin"),
        ("工具", "gongJu"),
        ("电器", "dianQi"),
        ("衣服", "yiFu"),
        ("手机", "shouJi"),
        ("电脑", "dianNao"),
        ("桌子", "zhuoZi"),
        ("椅子", "yiZi"),
        ("hello", "hello"),
        ("test123", "test123"),
        ("", ""),
    ]
    
    print("=== 中文转拼音测试 ===")
    all_passed = True
    
    for input_text, expected in test_cases:
        result = process_label_text(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' -> '{result}' (期望: '{expected}')")
        
        if result != expected:
            all_passed = False
    
    print(f"\n测试结果: {'全部通过' if all_passed else '部分失败'}")
    return all_passed

def test_chinese_detection():
    """测试中文检测功能"""
    test_cases = [
        ("称号", True),
        ("hello", False),
        ("中英mixed", True),
        ("123", False),
        ("", False),
    ]
    
    print("\n=== 中文检测测试 ===")
    all_passed = True
    
    for input_text, expected in test_cases:
        result = has_chinese(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' -> {result} (期望: {expected})")
        
        if result != expected:
            all_passed = False
    
    print(f"\n测试结果: {'全部通过' if all_passed else '部分失败'}")
    return all_passed

if __name__ == "__main__":
    print("开始测试中文转拼音功能...")
    
    test1_passed = test_chinese_detection()
    test2_passed = test_pinyin_conversion()
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
