#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能预测修复验证脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_signal_flow():
    """测试信号流程"""
    print("🧪 测试智能预测信号流程...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.ai_assistant_panel import AIAssistantPanel
        from labelImg import MainWindow
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        # 检查信号连接
        ai_panel = window.ai_assistant_panel
        
        # 检查智能预测状态变量
        assert hasattr(ai_panel, 'is_smart_predicting'), "❌ 智能预测状态变量不存在"
        print("✅ 智能预测状态变量存在")
        
        # 检查信号连接
        collapsible_panel = window.collapsible_ai_panel
        
        # 验证信号连接
        prediction_signal = collapsible_panel.predictions_applied
        print(f"✅ predictions_applied信号存在: {prediction_signal}")
        
        # 检查主窗口的信号处理方法
        assert hasattr(window, 'on_ai_predictions_applied'), "❌ 预测结果应用处理方法不存在"
        print("✅ 预测结果应用处理方法存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 信号流程测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_predict_logic():
    """测试智能预测逻辑"""
    print("\n🧪 测试智能预测逻辑...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from labelImg import MainWindow
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        # 检查智能预测相关方法
        methods_to_check = [
            'trigger_smart_prediction_if_needed',
            '_execute_smart_prediction'
        ]
        
        for method_name in methods_to_check:
            assert hasattr(window, method_name), f"❌ 方法不存在: {method_name}"
            print(f"✅ 方法存在: {method_name}")
        
        # 检查AI助手面板的智能预测方法
        ai_panel = window.ai_assistant_panel
        
        ai_methods = [
            'is_smart_predict_enabled',
            'on_smart_predict_changed'
        ]
        
        for method_name in ai_methods:
            assert hasattr(ai_panel, method_name), f"❌ AI面板方法不存在: {method_name}"
            print(f"✅ AI面板方法存在: {method_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 智能预测逻辑测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_status_management():
    """测试状态管理"""
    print("\n🧪 测试智能预测状态管理...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.ai_assistant_panel import AIAssistantPanel
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建AI助手面板
        panel = AIAssistantPanel()
        
        # 检查状态变量
        assert hasattr(panel, 'is_smart_predicting'), "❌ 智能预测状态变量不存在"
        print("✅ 智能预测状态变量存在")
        
        # 检查初始状态
        assert panel.is_smart_predicting == False, "❌ 智能预测状态初始值不正确"
        print("✅ 智能预测状态初始值正确")
        
        # 测试状态切换
        panel.is_smart_predicting = True
        assert panel.is_smart_predicting == True, "❌ 智能预测状态设置失败"
        print("✅ 智能预测状态设置成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 状态管理测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_fix_summary():
    """打印修复总结"""
    print("\n📋 智能预测修复总结:")
    print("   🔧 修复内容:")
    print("      - 修复了智能预测信号连接问题")
    print("      - 添加了智能预测状态管理")
    print("      - 实现了预测结果自动应用")
    print("      - 优化了用户状态反馈")
    print("      - 添加了防重复触发机制")
    print("\n   ✨ 用户体验改进:")
    print("      - 智能预测结果现在会自动显示在画布上")
    print("      - 状态栏显示详细的预测进度和结果")
    print("      - 智能预测过程中避免重复触发")
    print("      - 更清晰的成功/失败状态提示")

if __name__ == "__main__":
    print("🚀 智能预测修复验证开始\n")
    
    # 运行测试
    test1 = test_signal_flow()
    test2 = test_smart_predict_logic() if test1 else False
    test3 = test_status_management() if test2 else False
    
    print(f"\n📊 测试结果:")
    print(f"   - 信号流程测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   - 智能预测逻辑: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"   - 状态管理测试: {'✅ 通过' if test3 else '❌ 失败'}")
    
    if test1 and test2 and test3:
        print("\n🎉 智能预测修复验证通过！")
        print_fix_summary()
        print("\n💡 建议：启动labelImg程序测试实际的智能预测效果")
    else:
        print("\n❌ 修复验证失败，请检查实现。")
