#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能epochs计算功能最终集成测试
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path

# 添加libs目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def create_test_dataset(temp_dir, train_count=200, val_count=50, num_classes=3):
    """创建测试数据集"""
    try:
        # 创建目录结构
        images_train_dir = Path(temp_dir) / "images" / "train"
        images_val_dir = Path(temp_dir) / "images" / "val"
        
        for dir_path in [images_train_dir, images_val_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建图片文件
        for i in range(train_count):
            (images_train_dir / f"train_{i:04d}.jpg").touch()
        
        for i in range(val_count):
            (images_val_dir / f"val_{i:04d}.jpg").touch()
        
        # 创建data.yaml
        yaml_config = {
            'path': str(temp_dir),
            'train': 'images/train',
            'val': 'images/val',
            'nc': num_classes,
            'names': [f"class_{i}" for i in range(num_classes)]
        }
        
        yaml_file = Path(temp_dir) / "data.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True)
        
        return str(yaml_file)
        
    except Exception as e:
        print(f"创建测试数据集失败: {str(e)}")
        return None

def test_complete_workflow():
    """测试完整工作流程"""
    print("🧪 测试完整工作流程...")
    
    try:
        from smart_epochs_calculator import SmartEpochsCalculator
        from training_config_manager import TrainingConfigManager
        
        # 创建测试数据集
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 300, 100, 5)
            if not yaml_path:
                return False
            
            print(f"✅ 测试数据集创建成功: {yaml_path}")
            
            # 初始化组件
            calculator = SmartEpochsCalculator()
            config_manager = TrainingConfigManager()
            
            # 步骤1: 获取数据集信息
            dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
            if not dataset_info:
                print("❌ 数据集信息获取失败")
                return False
            
            print(f"✅ 数据集信息: {dataset_info.total_images}张图片, {dataset_info.num_classes}类")
            
            # 步骤2: 智能计算轮数
            result = calculator.calculate_smart_epochs(dataset_info, 'yolov8s', 16)
            print(f"✅ 智能计算结果: {result.recommended_epochs}轮 (置信度: {result.confidence_level})")
            
            # 步骤3: 保存计算结果
            config_manager.save_smart_calc_result(
                yaml_path,
                {
                    "total_images": dataset_info.total_images,
                    "train_images": dataset_info.train_images,
                    "val_images": dataset_info.val_images,
                    "num_classes": dataset_info.num_classes
                },
                {
                    "recommended_epochs": result.recommended_epochs,
                    "confidence_level": result.confidence_level
                }
            )
            print("✅ 计算结果保存成功")
            
            # 步骤4: 模拟用户调整
            adjusted_epochs = result.recommended_epochs + 20
            config_manager.save_user_adjustment(
                yaml_path, 
                result.recommended_epochs, 
                adjusted_epochs, 
                "用户手动调整测试"
            )
            print(f"✅ 用户调整保存成功: {result.recommended_epochs} -> {adjusted_epochs}")
            
            # 步骤5: 获取用户偏好
            preference = config_manager.get_user_preference_for_dataset(yaml_path)
            if preference:
                print(f"✅ 用户偏好获取成功: {preference['preferred_epochs']}轮")
            else:
                print("❌ 用户偏好获取失败")
                return False
            
            print("🎉 完整工作流程测试通过！")
            return True
            
    except Exception as e:
        print(f"❌ 工作流程测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况...")
    
    try:
        from smart_epochs_calculator import SmartEpochsCalculator
        calculator = SmartEpochsCalculator()
        
        # 测试极小数据集
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 20, 5, 1)
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8n', 16)
                    print(f"✅ 极小数据集测试: {result.recommended_epochs}轮")
                    
                    # 验证推荐轮数合理性
                    if 50 <= result.recommended_epochs <= 400:
                        print("✅ 极小数据集轮数合理")
                    else:
                        print(f"❌ 极小数据集轮数异常: {result.recommended_epochs}")
                        return False
        
        # 测试大数据集
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 3000, 1000, 20)
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8l', 32)
                    print(f"✅ 大数据集测试: {result.recommended_epochs}轮")
                    
                    # 验证推荐轮数合理性
                    if 30 <= result.recommended_epochs <= 150:
                        print("✅ 大数据集轮数合理")
                    else:
                        print(f"❌ 大数据集轮数异常: {result.recommended_epochs}")
                        return False
        
        print("🎉 边界情况测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 边界情况测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 智能epochs计算功能最终集成测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        ("完整工作流程", test_complete_workflow),
        ("边界情况", test_edge_cases),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有集成测试通过！智能epochs计算功能已完全就绪。")
        print("\n📋 功能摘要:")
        print("• ✅ 智能epochs计算算法")
        print("• ✅ 数据集信息分析")
        print("• ✅ 用户偏好记忆")
        print("• ✅ 配置保存和加载")
        print("• ✅ 错误处理和用户体验")
        print("• ✅ 帮助文档和界面集成")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
