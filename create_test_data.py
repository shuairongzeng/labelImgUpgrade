#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建持久的测试数据用于测试切换到未标注图片功能
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_test_data():
    """创建测试数据"""
    test_dir = "test_images"
    
    # 创建测试目录
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"创建测试目录: {test_dir}")
    
    # 创建10张测试图片
    colors = [
        (255, 100, 100),  # 红色
        (100, 255, 100),  # 绿色
        (100, 100, 255),  # 蓝色
        (255, 255, 100),  # 黄色
        (255, 100, 255),  # 紫色
        (100, 255, 255),  # 青色
        (255, 150, 100),  # 橙色
        (150, 255, 150),  # 浅绿
        (150, 150, 255),  # 浅蓝
        (255, 200, 200),  # 粉色
    ]
    
    for i in range(10):
        img = Image.new('RGB', (400, 300), color=colors[i])
        draw = ImageDraw.Draw(img)
        
        # 绘制一些简单的形状作为标注目标
        # 矩形
        draw.rectangle([50, 50, 150, 120], outline='black', width=3)
        # 圆形
        draw.ellipse([200, 80, 300, 180], outline='black', width=3)
        # 文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            # 如果没有找到字体，使用默认字体
            font = ImageFont.load_default()
        
        draw.text((50, 200), f"Image {i+1:02d}", fill='black', font=font)
        draw.text((50, 230), "Test Object", fill='black', font=font)
        
        img_path = os.path.join(test_dir, f'test_image_{i+1:02d}.jpg')
        img.save(img_path)
        print(f"创建图片: {img_path}")
    
    # 为部分图片创建标注文件（1, 3, 5, 7, 9）
    annotated_indices = [1, 3, 5, 7, 9]
    
    for i in annotated_indices:
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<annotation>
    <folder>test_images</folder>
    <filename>test_image_{i:02d}.jpg</filename>
    <path>{os.path.abspath(os.path.join(test_dir, f'test_image_{i:02d}.jpg'))}</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>400</width>
        <height>300</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    <object>
        <name>rectangle</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>50</xmin>
            <ymin>50</ymin>
            <xmax>150</xmax>
            <ymax>120</ymax>
        </bndbox>
    </object>
    <object>
        <name>circle</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>200</xmin>
            <ymin>80</ymin>
            <xmax>300</xmax>
            <ymax>180</ymax>
        </bndbox>
    </object>
</annotation>"""
        
        xml_path = os.path.join(test_dir, f'test_image_{i:02d}.xml')
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"创建标注: {xml_path}")
    
    print("\n" + "="*50)
    print("测试数据创建完成！")
    print("="*50)
    print(f"测试目录: {os.path.abspath(test_dir)}")
    print("\n图片状态:")
    
    for i in range(1, 11):
        img_file = f'test_image_{i:02d}.jpg'
        xml_file = f'test_image_{i:02d}.xml'
        xml_path = os.path.join(test_dir, xml_file)
        status = "✅已标注" if os.path.exists(xml_path) else "❌未标注"
        print(f"  {img_file} - {status}")
    
    print("\n测试步骤:")
    print("1. 启动 labelImg")
    print("2. 打开目录:", os.path.abspath(test_dir))
    print("3. 在标签面板中找到'🎯 切换到未标注图片'按钮")
    print("4. 点击按钮测试功能")
    print("\n预期行为:")
    print("- 应该在未标注的图片(2,4,6,8,10)之间切换")
    print("- 状态栏显示跳过的已标注图片数量")
    print("- 按钮工具提示显示剩余未标注图片数量")

if __name__ == '__main__':
    create_test_data()
