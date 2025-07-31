#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复前的重复加载问题
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from labelImg import MainWindow


def test_duplicate_before_fix():
    """测试修复前的重复加载问题"""
    print("🔍 测试修复前的重复加载问题...")
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    
    # 等待窗口初始化
    app.processEvents()
    time.sleep(0.5)
    
    # 测试目录路径
    test_dir = os.path.join(os.getcwd(), "test_images")
    print(f"📁 测试目录: {test_dir}")
    
    # 设置default_save_dir为测试目录
    main_window.default_save_dir = test_dir
    
    # 加载第一张图片，这会触发重复加载问题
    first_image_path = os.path.join(test_dir, "test_image_01.jpg")
    xml_path = os.path.join(test_dir, "test_image_01.xml")

    print(f"🖼️ 加载图片: {first_image_path}")

    # 加载图片目录，这会触发第一张图片的重复加载问题
    main_window.import_dir_images(test_dir)
    
    app.processEvents()
    time.sleep(1.0)
    
    # 检查标注框数量
    label_count = main_window.label_list.count()
    canvas_shapes_count = len(main_window.canvas.shapes)
    
    print(f"📊 加载图片目录后:")
    print(f"  - 标签列表数量: {label_count}")
    print(f"  - 画布标注框数量: {canvas_shapes_count}")

    # 从XML文件读取期望的标注框数量
    expected_count = count_objects_in_xml(xml_path)
    print(f"  - XML文件中的标注框数量: {expected_count}")

    if label_count == expected_count * 2:
        print("❌ 检测到重复加载！标注框数量是期望的2倍")
        result = True
    elif label_count == expected_count:
        print("✅ 没有重复加载")
        result = False
    else:
        print(f"⚠️ 意外的标注框数量: {label_count}")
        result = False
    
    main_window.close()
    app.quit()
    return result


def count_objects_in_xml(xml_path):
    """从XML文件中计算标注框数量"""
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_path)
        root = tree.getroot()
        objects = root.findall('object')
        return len(objects)
    except Exception as e:
        print(f"❌ 解析XML文件失败: {e}")
        return 0


if __name__ == "__main__":
    has_duplicate = test_duplicate_before_fix()
    if has_duplicate:
        print("\n✅ 确认存在重复加载问题")
    else:
        print("\n❌ 没有检测到重复加载问题")
