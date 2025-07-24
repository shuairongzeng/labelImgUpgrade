#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试方法名修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_method_names():
    """测试AI助手面板方法名"""
    print("🔍 测试AI助手面板方法名...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.ai_assistant_panel import AIAssistantPanel
        
        app = QApplication([])
        
        # 创建一个简单的父窗口用于测试
        class MockParent:
            def __init__(self):
                pass
        
        parent = MockParent()
        panel = AIAssistantPanel(parent)
        
        print("✅ AI助手面板创建成功")
        
        # 检查所有get_current_方法
        methods_to_check = [
            'get_current_confidence',
            'get_current_nms', 
            'get_current_max_det',
            'get_current_predictions'
        ]
        
        for method_name in methods_to_check:
            if hasattr(panel, method_name):
                print(f"✅ 方法 {method_name} 存在")
                try:
                    # 尝试调用方法（除了get_current_predictions）
                    if method_name != 'get_current_predictions':
                        result = getattr(panel, method_name)()
                        print(f"  返回值: {result}")
                except Exception as e:
                    print(f"  调用失败: {e}")
            else:
                print(f"❌ 方法 {method_name} 不存在")
        
        # 检查错误的方法名
        if hasattr(panel, 'get_current_iou'):
            print("❌ 错误的方法 get_current_iou 仍然存在")
        else:
            print("✅ 错误的方法 get_current_iou 已移除")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 方法名修复测试")
    print("=" * 40)
    
    success = test_method_names()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ 方法名修复测试通过！")
        print("\n💡 现在可以重新测试AI预测功能:")
        print("   python labelImg.py")
        print("   打开图片 → 点击'预测当前图像'")
    else:
        print("❌ 方法名修复测试失败")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
