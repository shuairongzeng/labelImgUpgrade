#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试标注文件加载问题
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from labelImg import MainWindow


def debug_annotation_loading():
    """调试标注文件加载"""
    print("🔍 调试标注文件加载...")
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    
    # 等待窗口初始化
    app.processEvents()
    time.sleep(0.5)
    
    # 测试目录路径
    test_dir = os.path.join(os.getcwd(), "test_images")
    print(f"📁 测试目录: {test_dir}")
    
    # 检查测试文件
    first_image_path = os.path.join(test_dir, "test_image_01.jpg")
    xml_path = os.path.join(test_dir, "test_image_01.xml")
    
    print(f"🖼️ 图片文件: {first_image_path}")
    print(f"📄 XML文件: {xml_path}")
    print(f"📄 图片文件存在: {os.path.exists(first_image_path)}")
    print(f"📄 XML文件存在: {os.path.exists(xml_path)}")
    
    # 加载测试图片目录
    print("\n🔄 加载测试图片目录...")
    main_window.import_dir_images(test_dir)
    
    # 等待加载完成
    app.processEvents()
    time.sleep(1.0)
    
    # 检查状态
    print(f"\n📊 当前状态:")
    print(f"  - file_path: {main_window.file_path}")
    print(f"  - default_save_dir: {main_window.default_save_dir}")
    print(f"  - label_file: {main_window.label_file}")
    print(f"  - 标签列表数量: {main_window.label_list.count()}")
    print(f"  - 画布标注框数量: {len(main_window.canvas.shapes)}")
    
    # 手动调用show_bounding_box_from_annotation_file
    print(f"\n🔄 手动调用show_bounding_box_from_annotation_file...")
    main_window.show_bounding_box_from_annotation_file(first_image_path)
    
    app.processEvents()
    time.sleep(0.5)
    
    print(f"\n📊 手动调用后状态:")
    print(f"  - 标签列表数量: {main_window.label_list.count()}")
    print(f"  - 画布标注框数量: {len(main_window.canvas.shapes)}")
    
    # 检查标注文件路径
    if main_window.default_save_dir:
        basename = os.path.basename(os.path.splitext(first_image_path)[0])
        expected_xml_path = os.path.join(main_window.default_save_dir, basename + ".xml")
        print(f"\n📄 期望的XML路径: {expected_xml_path}")
        print(f"📄 期望的XML文件存在: {os.path.exists(expected_xml_path)}")
    
    main_window.close()
    app.quit()


if __name__ == "__main__":
    debug_annotation_loading()
