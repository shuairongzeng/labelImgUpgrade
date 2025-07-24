#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的DEL键功能测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.canvas import Canvas
from libs.shape import Shape
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QPointF


def test_canvas_delete():
    """测试画布删除功能"""
    print("[TEST] 开始测试画布删除功能...")
    
    app = QApplication(sys.argv)
    
    # 创建一个简单的widget作为父对象
    parent = QWidget()
    
    # 创建画布
    canvas = Canvas(parent)
    
    # 创建测试标注框
    print("[TEST] 创建测试标注框...")
    test_shape = Shape()
    test_shape.add_point(QPointF(100, 100))
    test_shape.add_point(QPointF(200, 100))
    test_shape.add_point(QPointF(200, 200))
    test_shape.add_point(QPointF(100, 200))
    test_shape.close()
    test_shape.label = "test_box"
    
    # 添加到画布
    canvas.shapes.append(test_shape)
    print(f"[TEST] 添加后，画布中有 {len(canvas.shapes)} 个标注框")
    
    # 选中标注框
    canvas.select_shape(test_shape)
    print(f"[TEST] 选中的标注框: {canvas.selected_shape}")
    
    # 删除选中的标注框
    print("[TEST] 删除选中的标注框...")
    deleted_shape = canvas.delete_selected()
    
    print(f"[TEST] 删除后，画布中有 {len(canvas.shapes)} 个标注框")
    print(f"[TEST] 当前选中的标注框: {canvas.selected_shape}")
    print(f"[TEST] 删除的标注框: {deleted_shape}")
    
    # 验证结果
    if len(canvas.shapes) == 0 and canvas.selected_shape is None and deleted_shape is not None:
        print("[TEST] ✅ 画布删除功能正常")
        result = True
    else:
        print("[TEST] ❌ 画布删除功能异常")
        result = False
    
    app.quit()
    return result


if __name__ == "__main__":
    success = test_canvas_delete()
    if success:
        print("\n[RESULT] 测试通过 ✅")
        sys.exit(0)
    else:
        print("\n[RESULT] 测试失败 ❌")
        sys.exit(1)
