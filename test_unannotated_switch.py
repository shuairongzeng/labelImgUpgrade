#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试切换到未标注图片功能的脚本
"""

import os
import sys
import tempfile
import shutil
from PIL import Image

def create_test_images(test_dir, num_images=5):
    """创建测试图片"""
    print(f"创建 {num_images} 张测试图片到 {test_dir}")
    
    for i in range(num_images):
        # 创建一个简单的测试图片
        img = Image.new('RGB', (100, 100), color=(i*50, 100, 150))
        img_path = os.path.join(test_dir, f'test_image_{i+1:02d}.jpg')
        img.save(img_path)
        print(f"  创建: {os.path.basename(img_path)}")

def create_test_annotations(test_dir, annotated_indices):
    """为指定的图片创建标注文件"""
    print(f"为图片 {annotated_indices} 创建标注文件")
    
    for i in annotated_indices:
        # 创建XML标注文件
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<annotation>
    <filename>test_image_{i:02d}.jpg</filename>
    <size>
        <width>100</width>
        <height>100</height>
        <depth>3</depth>
    </size>
    <object>
        <name>test_object</name>
        <bndbox>
            <xmin>10</xmin>
            <ymin>10</ymin>
            <xmax>90</xmax>
            <ymax>90</ymax>
        </bndbox>
    </object>
</annotation>"""
        
        xml_path = os.path.join(test_dir, f'test_image_{i:02d}.xml')
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"  创建标注: {os.path.basename(xml_path)}")

def main():
    """主测试函数"""
    print("=" * 50)
    print("测试切换到未标注图片功能")
    print("=" * 50)
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix='labelimg_test_')
    print(f"测试目录: {test_dir}")
    
    try:
        # 场景1: 创建5张图片，其中1,3,5已标注
        print("\n场景1: 部分图片已标注")
        create_test_images(test_dir, 5)
        create_test_annotations(test_dir, [1, 3, 5])
        
        print("\n图片列表:")
        for f in sorted(os.listdir(test_dir)):
            if f.endswith('.jpg'):
                xml_file = f.replace('.jpg', '.xml')
                status = "✅已标注" if xml_file in os.listdir(test_dir) else "❌未标注"
                print(f"  {f} - {status}")
        
        print(f"\n请在labelImg中打开目录: {test_dir}")
        print("然后测试'切换到未标注图片'按钮功能")
        print("预期行为:")
        print("- 按钮应该可以在未标注的图片(2,4)之间切换")
        print("- 状态栏应该显示跳过的已标注图片数量")
        print("- 当所有图片都标注完成后，应该显示完成消息")
        
        input("\n按回车键继续到下一个测试场景...")
        
        # 场景2: 所有图片都已标注
        print("\n场景2: 所有图片都已标注")
        create_test_annotations(test_dir, [2, 4])  # 标注剩余的图片
        
        print("\n图片列表:")
        for f in sorted(os.listdir(test_dir)):
            if f.endswith('.jpg'):
                xml_file = f.replace('.jpg', '.xml')
                status = "✅已标注" if xml_file in os.listdir(test_dir) else "❌未标注"
                print(f"  {f} - {status}")
        
        print("预期行为:")
        print("- 按钮点击后应该显示'所有图片都已标注完成'")
        
        input("\n按回车键清理测试文件...")
        
    finally:
        # 清理测试文件
        try:
            shutil.rmtree(test_dir)
            print(f"已清理测试目录: {test_dir}")
        except Exception as e:
            print(f"清理测试目录失败: {e}")

if __name__ == '__main__':
    main()
