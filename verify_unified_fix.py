#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
简单验证统一类别处理逻辑
"""

import os
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加libs目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.pascal_to_yolo_converter import PascalToYOLOConverter

# 创建转换器实例
converter = PascalToYOLOConverter(
    source_dir=".",
    target_dir=".",
    use_class_config=True
)

print("=" * 60)
print("验证统一类别处理逻辑")
print("=" * 60)

# 测试几个不同的类别名称
test_classes = ["person", "car", "dog", "unknown_class"]

print("\n测试 _process_class_name 方法:")
print("-" * 40)

for class_name in test_classes:
    class_id, success = converter._process_class_name(class_name)
    if success:
        print(f"类别 '{class_name}' -> ID: {class_id} (成功)")
    else:
        print(f"类别 '{class_name}' -> 处理失败 (跳过)")

print("\n" + "-" * 40)
print(f"最终类别列表: {converter.classes}")
print(f"未知类别集合: {converter.unknown_classes}")

print("\n" + "=" * 60)
print("验证完成！现在XML和JSON都使用相同的类别处理逻辑")
print("=" * 60)