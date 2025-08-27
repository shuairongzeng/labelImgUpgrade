#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试复制形状bug修复的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_shape_copy_method():
    """测试Shape类的copy方法是否正确复制paint_label属性"""
    print("🔍 测试Shape.copy()方法...")
    
    try:
        from libs.shape import Shape
        from PyQt5.QtCore import QPointF
        
        # 创建原始形状
        original_shape = Shape(label="test_object", paint_label=True)
        original_shape.add_point(QPointF(10, 10))
        original_shape.add_point(QPointF(50, 10))
        original_shape.add_point(QPointF(50, 30))
        original_shape.add_point(QPointF(10, 30))
        original_shape.close()
        original_shape.difficult = True
        
        print(f"✅ 原始形状创建成功")
        print(f"  标签: {original_shape.label}")
        print(f"  paint_label: {original_shape.paint_label}")
        print(f"  difficult: {original_shape.difficult}")
        print(f"  点数量: {len(original_shape.points)}")
        
        # 复制形状
        copied_shape = original_shape.copy()
        
        print(f"✅ 形状复制成功")
        print(f"  复制后标签: {copied_shape.label}")
        print(f"  复制后paint_label: {copied_shape.paint_label}")
        print(f"  复制后difficult: {copied_shape.difficult}")
        print(f"  复制后点数量: {len(copied_shape.points)}")
        
        # 验证属性是否正确复制
        assert copied_shape.label == original_shape.label, "标签复制失败"
        assert copied_shape.paint_label == original_shape.paint_label, "paint_label复制失败"
        assert copied_shape.difficult == original_shape.difficult, "difficult复制失败"
        assert len(copied_shape.points) == len(original_shape.points), "点数量复制失败"
        
        print("✅ 所有属性复制验证通过")
        return True
        
    except Exception as e:
        print(f"❌ Shape.copy()测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_canvas_copy_selected_shape():
    """测试Canvas.copy_selected_shape()方法的空值处理"""
    print("\n🔍 测试Canvas.copy_selected_shape()方法...")
    
    try:
        from libs.canvas import Canvas
        from PyQt5.QtWidgets import QApplication
        
        # 创建QApplication实例（如果不存在）
        if not QApplication.instance():
            app = QApplication([])
        
        # 创建Canvas实例
        canvas = Canvas()
        
        # 测试没有选中形状时的情况
        result = canvas.copy_selected_shape()
        
        if result is None:
            print("✅ 没有选中形状时正确返回None")
        else:
            print(f"❌ 期望返回None，但得到: {result}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Canvas.copy_selected_shape()测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试复制形状bug修复...")
    
    success_count = 0
    total_tests = 2
    
    # 测试Shape.copy()方法
    if test_shape_copy_method():
        success_count += 1
    
    # 测试Canvas.copy_selected_shape()方法
    if test_canvas_copy_selected_shape():
        success_count += 1
    
    print(f"\n📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！复制形状bug修复成功")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    main()
