#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI预测调试测试脚本

测试AI助手预测功能的调试信息输出
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_ai_prediction_debug():
    """测试AI预测调试信息"""
    print("🔍 测试AI预测调试信息...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        import labelImg
        
        # 创建应用和主窗口
        app, win = labelImg.get_main_app([])
        
        print("\n📋 检查AI助手组件:")
        
        # 检查AI助手面板
        if hasattr(win, 'ai_assistant_panel'):
            panel = win.ai_assistant_panel
            print("✅ AI助手面板存在")
            
            # 检查预测器
            if hasattr(panel, 'predictor'):
                predictor = panel.predictor
                print("✅ YOLO预测器存在")
                
                # 检查模型加载状态
                print(f"  模型加载状态: {predictor.is_model_loaded()}")
                print(f"  当前模型: {getattr(predictor, 'model_name', 'None')}")
                
                # 检查方法存在性
                methods_to_check = ['load_model', 'predict_single', 'is_model_loaded']
                for method in methods_to_check:
                    if hasattr(predictor, method):
                        print(f"✅ 方法 {method} 存在")
                    else:
                        print(f"❌ 方法 {method} 不存在")
            else:
                print("❌ YOLO预测器不存在")
            
            # 检查AI助手面板方法
            panel_methods = ['start_prediction', 'on_predict_current', 'get_current_confidence']
            for method in panel_methods:
                if hasattr(panel, method):
                    print(f"✅ AI助手面板方法 {method} 存在")
                else:
                    print(f"❌ AI助手面板方法 {method} 不存在")
        else:
            print("❌ AI助手面板不存在")
        
        print("\n📋 检查信号连接:")
        
        # 检查信号连接
        if hasattr(win, 'ai_assistant_panel'):
            panel = win.ai_assistant_panel
            signals = ['prediction_requested', 'predictions_applied', 'model_changed']
            for signal_name in signals:
                if hasattr(panel, signal_name):
                    print(f"✅ 信号 {signal_name} 存在")
                else:
                    print(f"❌ 信号 {signal_name} 不存在")
        
        # 检查主窗口信号处理方法
        handler_methods = ['on_ai_prediction_requested', 'on_ai_predictions_applied']
        for method in handler_methods:
            if hasattr(win, method):
                print(f"✅ 主窗口方法 {method} 存在")
            else:
                print(f"❌ 主窗口方法 {method} 不存在")
        
        print("\n🎯 调试信息测试建议:")
        print("1. 启动labelImg: python labelImg.py")
        print("2. 打开一张图片")
        print("3. 在AI助手面板中选择YOLO模型")
        print("4. 点击'预测当前图像'按钮")
        print("5. 观察控制台输出的调试信息")
        
        print("\n📝 预期的调试信息流程:")
        print("[DEBUG] AI助手: 开始预测当前图像")
        print("[DEBUG] AI助手: 置信度设置为 X.X")
        print("[DEBUG] AI助手: 发送预测请求信号")
        print("[DEBUG] 主窗口: 收到AI预测请求...")
        print("[DEBUG] 主窗口: 使用当前图像路径: ...")
        print("[DEBUG] 主窗口: 调用AI助手面板的start_prediction方法")
        print("[DEBUG] AI助手: start_prediction被调用...")
        print("[DEBUG] YOLO预测器: predict_single被调用")
        print("[DEBUG] YOLO预测器: 开始预测图像...")
        print("[DEBUG] YOLO预测器: 模型预测完成...")
        print("[DEBUG] YOLO预测器: 预测完成，检测到 X 个目标")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_loading_debug():
    """测试模型加载调试信息"""
    print("\n🔍 测试模型加载调试信息...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.ai_assistant.yolo_predictor import YOLOPredictor
        
        app = QApplication([])
        predictor = YOLOPredictor()
        
        print("✅ YOLO预测器创建成功")
        
        # 测试无效模型路径
        print("\n📋 测试无效模型路径:")
        result = predictor.load_model("invalid_model.pt")
        print(f"加载结果: {result}")
        
        # 检查模型加载状态
        print(f"模型加载状态: {predictor.is_model_loaded()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型加载测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 AI预测调试信息测试")
    print("=" * 60)
    
    success = True
    
    # 测试AI预测调试
    if not test_ai_prediction_debug():
        success = False
    
    # 测试模型加载调试
    if not test_model_loading_debug():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("\n💡 现在可以运行labelImg并观察调试信息:")
        print("   python labelImg.py")
        print("\n🔍 如果预测没有输出，请检查:")
        print("1. 模型文件是否正确加载")
        print("2. 图像文件是否存在")
        print("3. 控制台是否有错误信息")
        print("4. 置信度阈值是否过高")
    else:
        print("❌ 部分测试失败")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
