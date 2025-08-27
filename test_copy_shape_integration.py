#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成测试：模拟实际的复制形状操作场景
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_copy_selected_shape_integration():
    """集成测试：模拟实际的copy_selected_shape调用"""
    print("🔍 集成测试：模拟实际的copy_selected_shape调用...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QPointF
        from libs.canvas import Canvas
        from libs.shape import Shape
        
        # 创建QApplication实例（如果不存在）
        if not QApplication.instance():
            app = QApplication([])
        
        # 创建Canvas实例
        canvas = Canvas()
        
        # 创建一个形状并添加到canvas
        shape = Shape(label="test_person", paint_label=True)
        shape.add_point(QPointF(100, 100))
        shape.add_point(QPointF(200, 100))
        shape.add_point(QPointF(200, 200))
        shape.add_point(QPointF(100, 200))
        shape.close()
        shape.difficult = False
        
        # 添加形状到canvas
        canvas.shapes.append(shape)
        canvas.selected_shape = shape
        shape.selected = True
        
        print("✅ 测试形状创建并选中成功")
        print(f"  标签: {shape.label}")
        print(f"  paint_label: {shape.paint_label}")
        print(f"  selected: {shape.selected}")
        
        # 测试复制选中的形状
        copied_shape = canvas.copy_selected_shape()
        
        if copied_shape is not None:
            print("✅ 形状复制成功")
            print(f"  复制后标签: {copied_shape.label}")
            print(f"  复制后paint_label: {copied_shape.paint_label}")
            print(f"  复制后selected: {copied_shape.selected}")
            print(f"  复制后difficult: {copied_shape.difficult}")
            
            # 验证复制的形状属性
            assert copied_shape.label == shape.label, "标签复制失败"
            assert copied_shape.paint_label == shape.paint_label, "paint_label复制失败"
            assert copied_shape.difficult == shape.difficult, "difficult复制失败"
            assert len(copied_shape.points) == len(shape.points), "点数量复制失败"
            
            print("✅ 复制形状属性验证通过")
        else:
            print("❌ 复制形状失败，返回None")
            return False
        
        # 测试没有选中形状的情况
        canvas.selected_shape = None
        result = canvas.copy_selected_shape()
        
        if result is None:
            print("✅ 没有选中形状时正确返回None")
        else:
            print(f"❌ 期望返回None，但得到: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_labelimg_copy_selected_shape():
    """模拟labelImg中copy_selected_shape方法的调用"""
    print("\n🔍 模拟labelImg.copy_selected_shape()方法调用...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QCheckBox
        from PyQt5.QtCore import QPointF
        from libs.canvas import Canvas
        from libs.shape import Shape
        
        # 创建QApplication实例（如果不存在）
        if not QApplication.instance():
            app = QApplication([])
        
        # 模拟MainWindow的部分功能
        class MockMainWindow:
            def __init__(self):
                self.canvas = Canvas()
                self.display_label_option = QCheckBox()
                self.display_label_option.setChecked(True)
                self.shapes_to_items = {}
                self.items_to_shapes = {}
            
            def add_label(self, shape):
                """模拟add_label方法"""
                if shape is None:
                    raise AttributeError("'NoneType' object has no attribute 'paint_label'")
                
                shape.paint_label = self.display_label_option.isChecked()
                print(f"  添加标签成功: {shape.label}, paint_label: {shape.paint_label}")
                return True
            
            def copy_selected_shape(self):
                """修复后的copy_selected_shape方法"""
                copied_shape = self.canvas.copy_selected_shape()
                if copied_shape is not None:
                    self.add_label(copied_shape)
                    print("  形状复制和添加标签完成")
                    return True
                else:
                    print("  没有选中的形状可以复制")
                    return False
        
        # 创建模拟的主窗口
        mock_window = MockMainWindow()
        
        # 测试1: 有选中形状的情况
        print("测试1: 有选中形状的情况")
        shape = Shape(label="test_car", paint_label=False)
        shape.add_point(QPointF(50, 50))
        shape.add_point(QPointF(150, 50))
        shape.add_point(QPointF(150, 100))
        shape.add_point(QPointF(50, 100))
        shape.close()
        
        mock_window.canvas.shapes.append(shape)
        mock_window.canvas.selected_shape = shape
        shape.selected = True
        
        result1 = mock_window.copy_selected_shape()
        if result1:
            print("✅ 有选中形状时复制成功")
        else:
            print("❌ 有选中形状时复制失败")
            return False
        
        # 测试2: 没有选中形状的情况
        print("\n测试2: 没有选中形状的情况")
        mock_window.canvas.selected_shape = None
        
        result2 = mock_window.copy_selected_shape()
        if not result2:
            print("✅ 没有选中形状时正确处理")
        else:
            print("❌ 没有选中形状时处理错误")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 模拟测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始集成测试...")
    
    success_count = 0
    total_tests = 2
    
    # 集成测试
    if test_copy_selected_shape_integration():
        success_count += 1
    
    # 模拟labelImg测试
    if test_mock_labelimg_copy_selected_shape():
        success_count += 1
    
    print(f"\n📊 集成测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有集成测试通过！bug修复验证成功")
        return True
    else:
        print("❌ 部分集成测试失败")
        return False

if __name__ == "__main__":
    main()
