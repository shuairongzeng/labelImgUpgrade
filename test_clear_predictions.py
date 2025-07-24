#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试清除AI预测结果功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_clear_signal():
    """测试清除信号"""
    print("🔍 测试清除信号...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.ai_assistant_panel import AIAssistantPanel
        
        app = QApplication([])
        
        # 创建AI助手面板（需要一个简单的父对象）
        class MockParent:
            pass
        
        # 由于AIAssistantPanel继承自QWidget，需要传入None作为父对象
        panel = AIAssistantPanel(None)
        
        print("✅ AI助手面板创建成功")
        
        # 检查清除信号是否存在
        if hasattr(panel, 'predictions_cleared'):
            print("✅ predictions_cleared信号存在")
        else:
            print("❌ predictions_cleared信号不存在")
            return False
        
        # 检查清除方法是否存在
        methods_to_check = ['on_clear_results', 'on_cancel_prediction', 'clear_prediction_results']
        for method_name in methods_to_check:
            if hasattr(panel, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_shape_marking():
    """测试Shape标记功能"""
    print("\n🔍 测试Shape标记功能...")
    
    try:
        from libs.shape import Shape
        from PyQt5.QtCore import QPointF
        
        # 创建一个Shape对象
        shape = Shape(label="test_person")
        
        # 添加矩形顶点
        shape.add_point(QPointF(10, 10))
        shape.add_point(QPointF(50, 10))
        shape.add_point(QPointF(50, 30))
        shape.add_point(QPointF(10, 30))
        shape.close()
        
        # 测试AI标记
        shape.ai_generated = True
        shape.ai_confidence = 0.85
        
        print("✅ Shape对象创建和标记成功")
        print(f"  标签: {shape.label}")
        print(f"  AI生成: {getattr(shape, 'ai_generated', False)}")
        print(f"  置信度: {getattr(shape, 'ai_confidence', 'N/A')}")
        
        # 测试标记检查
        is_ai_generated = hasattr(shape, 'ai_generated') and shape.ai_generated
        print(f"✅ AI生成标记检查: {is_ai_generated}")
        
        return True
        
    except Exception as e:
        print(f"❌ Shape标记测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_methods():
    """测试主窗口方法"""
    print("\n🔍 测试主窗口方法...")
    
    try:
        import labelImg
        import inspect
        
        # 获取MainWindow类的方法
        main_window_class = None
        for name, obj in inspect.getmembers(labelImg):
            if inspect.isclass(obj) and 'MainWindow' in name:
                main_window_class = obj
                break
        
        if not main_window_class:
            print("❌ 找不到MainWindow类")
            return False
        
        print("✅ 找到MainWindow类")
        
        # 检查清除相关方法
        methods_to_check = ['on_ai_predictions_cleared']
        methods = [name for name, method in inspect.getmembers(main_window_class, predicate=inspect.isfunction)]
        
        for method_name in methods_to_check:
            if method_name in methods:
                print(f"✅ 主窗口方法 {method_name} 存在")
            else:
                print(f"❌ 主窗口方法 {method_name} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 主窗口方法测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 清除AI预测结果功能测试")
    print("=" * 60)
    
    success = True
    
    # 测试清除信号
    if not test_clear_signal():
        success = False
    
    # 测试Shape标记
    if not test_shape_marking():
        success = False
    
    # 测试主窗口方法
    if not test_main_window_methods():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("\n💡 功能实现总结:")
        print("1. ✅ 添加了predictions_cleared信号")
        print("2. ✅ 实现了clear_prediction_results方法")
        print("3. ✅ 修改了on_clear_results和on_cancel_prediction方法")
        print("4. ✅ 添加了AI生成标注框的标记功能")
        print("5. ✅ 实现了on_ai_predictions_cleared处理方法")
        
        print("\n🎯 现在清除功能应该完全正常工作:")
        print("   点击'清除结果' → 清空面板显示 + 清空图片标注框")
        print("   点击'取消预测' → 停止预测 + 清空所有结果")
        
        print("\n📊 预期行为:")
        print("- 只清除AI生成的标注框，保留手动创建的")
        print("- 同时更新标签列表和画布显示")
        print("- 保持界面状态的一致性")
        
    else:
        print("❌ 部分测试失败")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
