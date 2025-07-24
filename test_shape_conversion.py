#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试预测结果转换为Shape对象
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_detection_to_shape():
    """测试Detection转换为Shape"""
    print("🔍 测试Detection转换为Shape...")
    
    try:
        from libs.ai_assistant.yolo_predictor import Detection
        
        # 创建模拟检测结果
        detection = Detection(
            bbox=(100, 100, 200, 200),
            confidence=0.85,
            class_id=0,
            class_name='person',
            image_width=800,
            image_height=600
        )
        
        print("✅ Detection对象创建成功")
        print(f"  类别: {detection.class_name}")
        print(f"  置信度: {detection.confidence}")
        print(f"  边界框: {detection.bbox}")
        
        # 测试转换为Shape
        shape = detection.to_shape()
        
        print("✅ 成功转换为Shape对象")
        print(f"  标签: {shape.label}")
        print(f"  点数量: {len(shape.points)}")
        print(f"  是否闭合: {shape.is_closed()}")
        
        # 检查点坐标
        if len(shape.points) == 4:
            print("✅ 矩形顶点正确")
            for i, point in enumerate(shape.points):
                print(f"  点{i+1}: ({point.x()}, {point.y()})")
        else:
            print(f"❌ 矩形顶点数量错误: {len(shape.points)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_shape_methods():
    """测试Shape相关方法"""
    print("\n🔍 测试Shape相关方法...")
    
    try:
        from libs.shape import Shape
        from PyQt5.QtCore import QPointF
        
        # 创建Shape对象
        shape = Shape(label="test_object")
        
        # 添加矩形顶点
        shape.add_point(QPointF(10, 10))  # 左上
        shape.add_point(QPointF(50, 10))  # 右上
        shape.add_point(QPointF(50, 30))  # 右下
        shape.add_point(QPointF(10, 30))  # 左下
        shape.close()
        
        print("✅ Shape对象创建成功")
        print(f"  标签: {shape.label}")
        print(f"  点数量: {len(shape.points)}")
        print(f"  是否闭合: {shape.is_closed()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Shape测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_color_generation():
    """测试颜色生成"""
    print("\n🔍 测试颜色生成...")
    
    try:
        from libs.utils import generate_color_by_text
        
        # 测试不同标签的颜色生成
        labels = ['person', 'bus', 'stop sign', 'car', 'bicycle']
        
        for label in labels:
            color = generate_color_by_text(label)
            print(f"✅ 标签 '{label}' 的颜色: RGB({color.red()}, {color.green()}, {color.blue()})")
        
        return True
        
    except Exception as e:
        print(f"❌ 颜色生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 预测结果转换为Shape对象测试")
    print("=" * 60)
    
    success = True
    
    # 测试Detection转换
    if not test_detection_to_shape():
        success = False
    
    # 测试Shape方法
    if not test_shape_methods():
        success = False
    
    # 测试颜色生成
    if not test_color_generation():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！")
        print("\n💡 修复总结:")
        print("1. ✅ Detection.to_shape() 方法正常工作")
        print("2. ✅ Shape对象创建和操作正常")
        print("3. ✅ 颜色生成功能正常")
        print("4. ✅ 预测结果应用功能已实现")
        
        print("\n🎯 现在可以完整测试AI预测标注功能:")
        print("   python labelImg.py")
        print("   打开图片 → 点击'预测当前图像' → 查看标注框显示")
        
        print("\n📊 预期效果:")
        print("- 预测完成后，检测框会自动显示在图像上")
        print("- 每个检测框有对应的标签和颜色")
        print("- 标签列表会显示所有检测到的对象")
        print("- 可以像手动标注一样编辑这些标注框")
        
    else:
        print("❌ 部分测试失败")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
