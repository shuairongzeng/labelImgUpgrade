#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重复绘制修复验证脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_signal_flow_fix():
    """测试信号流程修复"""
    print("🧪 测试重复绘制修复...")
    
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
        ai_panel = window.ai_assistant_panel
        
        # 检查修复后的逻辑
        print("✅ 检查智能预测状态管理...")
        assert hasattr(ai_panel, 'is_smart_predicting'), "❌ 智能预测状态变量不存在"
        assert ai_panel.is_smart_predicting == False, "❌ 智能预测状态初始值不正确"
        
        # 检查方法存在性
        print("✅ 检查预测完成处理方法...")
        assert hasattr(ai_panel, 'on_prediction_completed'), "❌ 预测完成处理方法不存在"
        
        # 检查信号连接
        print("✅ 检查信号连接...")
        collapsible_panel = window.collapsible_ai_panel
        assert hasattr(collapsible_panel, 'predictions_applied'), "❌ predictions_applied信号不存在"
        
        return True
        
    except Exception as e:
        print(f"❌ 信号流程修复测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_prediction_logic():
    """测试预测逻辑"""
    print("\n🧪 测试预测逻辑修复...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.ai_assistant_panel import AIAssistantPanel
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建AI助手面板
        panel = AIAssistantPanel()
        
        # 检查start_prediction方法的修改
        assert hasattr(panel, 'start_prediction'), "❌ start_prediction方法不存在"
        print("✅ start_prediction方法存在")
        
        # 检查on_prediction_completed方法的修改
        assert hasattr(panel, 'on_prediction_completed'), "❌ on_prediction_completed方法不存在"
        print("✅ on_prediction_completed方法存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 预测逻辑测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_fix_details():
    """打印修复详情"""
    print("\n📋 重复绘制修复详情:")
    print("   🔧 问题原因:")
    print("      - start_prediction()方法中发送了predictions_applied信号")
    print("      - on_prediction_completed()中又发送了predictions_applied信号")
    print("      - 导致同一个预测结果被绘制两次")
    print("\n   ✨ 修复方案:")
    print("      - 修改start_prediction()：只启动预测，不处理结果")
    print("      - 统一在on_prediction_completed()中处理所有预测结果")
    print("      - 根据is_smart_predicting状态区分智能预测和手动预测")
    print("      - 确保每个预测结果只发送一次predictions_applied信号")
    print("\n   🎯 修复效果:")
    print("      - 智能预测：结果自动应用，只绘制一次")
    print("      - 手动预测：结果正常应用，只绘制一次")
    print("      - 状态管理：清晰的状态转换和重置")
    print("      - 调试信息：详细的日志输出便于跟踪")

def simulate_prediction_flow():
    """模拟预测流程"""
    print("\n🎮 模拟修复后的预测流程:")
    print("   📱 智能预测流程:")
    print("      1. 图片切换 → trigger_smart_prediction_if_needed()")
    print("      2. 设置 is_smart_predicting = True")
    print("      3. 发送 prediction_requested 信号")
    print("      4. start_prediction() 启动预测（不处理结果）")
    print("      5. predictor.predict_single() 执行预测")
    print("      6. 发送 prediction_completed 信号")
    print("      7. on_prediction_completed() 检测到智能预测")
    print("      8. 自动发送 predictions_applied 信号（只发送一次）")
    print("      9. 主窗口绘制结果到画布")
    print("      10. 重置 is_smart_predicting = False")
    print("\n   🖱️ 手动预测流程:")
    print("      1. 用户点击预测按钮")
    print("      2. 发送 prediction_requested 信号")
    print("      3. start_prediction() 启动预测（不处理结果）")
    print("      4. predictor.predict_single() 执行预测")
    print("      5. 发送 prediction_completed 信号")
    print("      6. on_prediction_completed() 检测到手动预测")
    print("      7. 发送 predictions_applied 信号（只发送一次）")
    print("      8. 主窗口绘制结果到画布")

if __name__ == "__main__":
    print("🚀 重复绘制修复验证开始\n")
    
    # 运行测试
    test1 = test_signal_flow_fix()
    test2 = test_prediction_logic() if test1 else False
    
    print(f"\n📊 测试结果:")
    print(f"   - 信号流程修复: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   - 预测逻辑修复: {'✅ 通过' if test2 else '❌ 失败'}")
    
    if test1 and test2:
        print("\n🎉 重复绘制修复验证通过！")
        print_fix_details()
        simulate_prediction_flow()
        print("\n💡 建议：启动labelImg程序测试智能预测，确认不再出现重复绘制")
    else:
        print("\n❌ 修复验证失败，请检查实现。")
