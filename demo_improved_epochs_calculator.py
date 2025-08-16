#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进后的智能epochs计算器演示
展示防过拟合优化效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from libs.smart_epochs_calculator import SmartEpochsCalculator, DatasetInfo

def demo_improved_calculator():
    """演示改进后的智能epochs计算器"""
    print("🧠 改进后的智能Epochs计算器演示")
    print("=" * 60)
    print("🎯 重点：防止小数据集过拟合")
    print()
    
    calculator = SmartEpochsCalculator()
    
    # 测试不同规模的数据集
    test_cases = [
        {
            "name": "极小数据集",
            "total_images": 50,
            "train_images": 35,
            "val_images": 15,
            "num_classes": 2,
            "model": "yolov8n"
        },
        {
            "name": "小数据集", 
            "total_images": 300,
            "train_images": 210,
            "val_images": 90,
            "num_classes": 5,
            "model": "yolov8s"
        },
        {
            "name": "中等数据集",
            "total_images": 1500,
            "train_images": 1050,
            "val_images": 450,
            "num_classes": 10,
            "model": "yolov8m"
        },
        {
            "name": "大数据集",
            "total_images": 5000,
            "train_images": 3500,
            "val_images": 1500,
            "num_classes": 20,
            "model": "yolov8l"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"📊 测试案例 {i}: {case['name']}")
        print(f"   数据量: {case['total_images']}张 (训练:{case['train_images']}, 验证:{case['val_images']})")
        print(f"   类别数: {case['num_classes']}类")
        print(f"   模型: {case['model']}")
        
        # 创建数据集信息
        dataset_info = DatasetInfo(
            dataset_path="demo_dataset",
            config_path="demo_config.yaml",
            total_images=case['total_images'],
            train_images=case['train_images'],
            val_images=case['val_images'],
            num_classes=case['num_classes']
        )
        
        # 计算推荐epochs
        result = calculator.calculate_smart_epochs(
            dataset_info, 
            case['model'], 
            batch_size=16
        )
        
        print(f"   🎯 推荐轮数: {result.recommended_epochs}")
        print(f"   📊 建议范围: {result.min_epochs}-{result.max_epochs}")
        print(f"   🔍 置信度: {result.confidence_level}")
        
        # 显示关键建议
        if result.additional_notes:
            print("   💡 重要建议:")
            for note in result.additional_notes[:3]:  # 只显示前3条
                print(f"      • {note}")
        
        print()
    
    print("🔍 改进要点总结:")
    print("=" * 60)
    print("✅ 极小数据集(<100张): 从200轮降到80轮，防止严重过拟合")
    print("✅ 小数据集(100-800张): 从150轮降到100轮，采用谨慎策略")
    print("✅ 增强过拟合预防建议: Early Stopping、数据增强等")
    print("✅ 更严格的置信度评估: 小数据集给出更低置信度")
    print("✅ 详细的训练指导: 提供具体的防过拟合检查清单")
    print()
    print("🚨 特别提醒: 小数据集训练时务必监控验证集性能！")

if __name__ == "__main__":
    demo_improved_calculator()
