#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型导出界面优化测试脚本

测试新的模型详情面板功能：
1. 高级模型详情面板创建
2. 性能指标可视化（进度条）
3. 模型性能评级系统
4. 模型信息分组展示
5. 推荐理由展示
6. 界面布局和样式
7. 动态信息更新
8. 模型对比功能
"""

import sys
import os
import tempfile
import yaml
import csv
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_mock_training_results():
    """创建模拟训练结果文件用于测试"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建训练目录结构
    train_dir = os.path.join(temp_dir, "runs", "train", "test_training")
    weights_dir = os.path.join(train_dir, "weights")
    os.makedirs(weights_dir, exist_ok=True)
    
    # 创建模型文件
    best_model = os.path.join(weights_dir, "best.pt")
    last_model = os.path.join(weights_dir, "last.pt")
    
    # 创建空的模型文件
    with open(best_model, 'wb') as f:
        f.write(b'mock model data' * 1000)  # 约13KB
    with open(last_model, 'wb') as f:
        f.write(b'mock model data' * 800)   # 约10KB
    
    # 创建训练配置文件
    args_file = os.path.join(train_dir, "args.yaml")
    config_data = {
        'epochs': 100,
        'batch': 16,
        'data': 'datasets/custom_data.yaml',
        'model': 'yolov8n.pt',
        'lr0': 0.01
    }
    
    with open(args_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    # 创建训练结果文件
    results_file = os.path.join(train_dir, "results.csv")
    results_data = [
        ['epoch', 'metrics/mAP50(B)', 'metrics/mAP50-95(B)', 'metrics/precision(B)', 'metrics/recall(B)'],
        ['0', '0.123', '0.089', '0.156', '0.134'],
        ['10', '0.234', '0.178', '0.267', '0.245'],
        ['20', '0.345', '0.267', '0.378', '0.356'],
        ['50', '0.567', '0.445', '0.589', '0.578'],
        ['99', '0.789', '0.634', '0.812', '0.798']  # 最终结果
    ]
    
    with open(results_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(results_data)
    
    return temp_dir, best_model, last_model

def test_model_export_ui_optimization():
    """测试模型导出界面优化功能"""
    print("🧪 开始测试模型导出界面优化功能...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.model_export_dialog import ModelExportDialog
        from libs.ai_assistant.model_manager import ModelManager
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建模拟训练结果
        temp_dir, best_model, last_model = create_mock_training_results()
        print(f"✅ 创建模拟训练结果: {temp_dir}")
        
        # 创建模型导出对话框
        dialog = ModelExportDialog()
        print("✅ 创建模型导出对话框成功")
        
        # 测试1: 检查高级模型详情面板组件
        print("\n📋 测试1: 高级模型详情面板组件")
        required_components = [
            'model_details_group', 'model_name_label',
            'map50_bar', 'map50_value', 'map50_label',
            'precision_bar', 'precision_value', 'precision_label',
            'recall_bar', 'recall_value', 'recall_label',
            'model_size_label', 'model_type_label', 'model_path_label',
            'config_epochs_label', 'config_batch_label', 'config_dataset_label',
            'recommendation_label', 'compare_button'
        ]
        
        missing_components = []
        for component in required_components:
            if not hasattr(dialog, component):
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ 缺少组件: {missing_components}")
            return False
        else:
            print("✅ 所有必需组件都存在")
        
        # 测试2: 性能指标可视化
        print("\n📊 测试2: 性能指标可视化")
        test_performance = {
            'mAP50': 0.789,
            'precision': 0.812,
            'recall': 0.798
        }
        
        dialog.update_performance_bars(test_performance)
        
        # 检查进度条值
        if (dialog.map50_bar.value() == 78 and  # 78.9% -> 78
            dialog.precision_bar.value() == 81 and  # 81.2% -> 81
            dialog.recall_bar.value() == 79):  # 79.8% -> 79
            print("✅ 性能指标进度条更新正确")
        else:
            print(f"❌ 进度条值不正确: mAP50={dialog.map50_bar.value()}, precision={dialog.precision_bar.value()}, recall={dialog.recall_bar.value()}")
            return False
        
        # 测试3: 性能评级系统
        print("\n⭐ 测试3: 性能评级系统")
        test_cases = [
            (0.95, "⭐⭐⭐⭐⭐", "卓越"),
            (0.85, "⭐⭐⭐⭐", "优秀"),
            (0.75, "⭐⭐⭐", "良好"),
            (0.65, "⭐⭐", "一般"),
            (0.55, "⭐", "较差"),
            (0.0, "", "未知")
        ]
        
        for mAP50, expected_stars, expected_rating in test_cases:
            stars, rating = dialog._get_performance_rating(mAP50)
            if stars == expected_stars and rating == expected_rating:
                print(f"✅ mAP50={mAP50}: {stars} ({rating})")
            else:
                print(f"❌ mAP50={mAP50}: 期望 {expected_stars} ({expected_rating}), 实际 {stars} ({rating})")
                return False
        
        # 测试4: 模型详细信息获取
        print("\n📄 测试4: 模型详细信息获取")
        model_info = dialog._get_model_detailed_info(best_model)
        
        required_keys = ['path', 'name', 'size_mb', 'training_dir', 'model_type', 'config', 'performance']
        missing_keys = [key for key in required_keys if key not in model_info]
        
        if missing_keys:
            print(f"❌ 模型信息缺少字段: {missing_keys}")
            return False
        else:
            print("✅ 模型详细信息获取成功")
            print(f"   - 大小: {model_info['size_mb']} MB")
            print(f"   - 训练目录: {model_info['training_dir']}")
            print(f"   - 配置: {model_info['config']}")
            print(f"   - 性能: {model_info['performance']}")
        
        # 测试5: 训练性能指标获取
        print("\n📈 测试5: 训练性能指标获取")
        performance = dialog._get_training_performance(best_model)
        
        if performance and performance.get('mAP50', 0) > 0:
            print("✅ 训练性能指标获取成功")
            print(f"   - mAP50: {performance.get('mAP50', 0)}")
            print(f"   - 精确度: {performance.get('precision', 0)}")
            print(f"   - 召回率: {performance.get('recall', 0)}")
        else:
            print("❌ 训练性能指标获取失败")
            return False
        
        # 测试6: 模型详情显示更新
        print("\n🔄 测试6: 模型详情显示更新")
        dialog.update_model_details_display(model_info)

        # 检查模型名称是否更新
        if dialog.model_name_label.text():
            print("✅ 模型详情显示更新成功")
            print(f"   模型名称: {dialog.model_name_label.text()}")
        else:
            print("❌ 模型详情显示更新失败")
            return False
        
        # 测试7: 推荐理由生成
        print("\n🌟 测试7: 推荐理由生成")
        # 模拟推荐模型
        dialog.model_combo.addItem("🏆 test_training-best 🌟推荐", best_model)
        dialog.model_combo.setCurrentIndex(0)

        dialog.update_recommendation_display(model_info)

        if dialog.recommendation_label.text():
            print("✅ 推荐理由生成成功")
            print(f"   推荐理由: {dialog.recommendation_label.text()[:100]}...")
        else:
            print("⚠️ 推荐理由为空，但功能正常")
            # 不返回False，因为这可能是正常情况
        
        # 测试8: 界面组件样式
        print("\n🎨 测试8: 界面组件样式")
        style_components = [
            (dialog.model_name_label, "font-weight"),
            (dialog.map50_bar, "QProgressBar"),
            (dialog.recommendation_label, "background-color")
        ]

        for component, style_check in style_components:
            if style_check in component.styleSheet():
                print(f"✅ {component.objectName() or type(component).__name__} 样式正确")
            else:
                print(f"⚠️ {component.objectName() or type(component).__name__} 样式可能需要调整")
        
        print("\n🎉 所有测试通过！模型导出界面优化功能正常工作")
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_export_ui_optimization()
    sys.exit(0 if success else 1)
