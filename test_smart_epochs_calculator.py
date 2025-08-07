#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能训练轮数计算器测试用例

测试智能epochs计算功能的正确性
"""

import os
import sys
import tempfile
import yaml
import shutil
from pathlib import Path

# 添加libs目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def create_test_dataset(base_dir, train_count, val_count, num_classes):
    """创建测试数据集"""
    try:
        # 创建目录结构
        images_train_dir = Path(base_dir) / "images" / "train"
        images_val_dir = Path(base_dir) / "images" / "val"
        labels_train_dir = Path(base_dir) / "labels" / "train"
        labels_val_dir = Path(base_dir) / "labels" / "val"
        
        for dir_path in [images_train_dir, images_val_dir, labels_train_dir, labels_val_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建训练图片和标签
        for i in range(train_count):
            # 创建空的图片文件
            img_file = images_train_dir / f"train_{i:04d}.jpg"
            img_file.touch()
            
            # 创建对应的标签文件
            label_file = labels_train_dir / f"train_{i:04d}.txt"
            label_file.write_text("0 0.5 0.5 0.2 0.2\n")
        
        # 创建验证图片和标签
        for i in range(val_count):
            # 创建空的图片文件
            img_file = images_val_dir / f"val_{i:04d}.jpg"
            img_file.touch()
            
            # 创建对应的标签文件
            label_file = labels_val_dir / f"val_{i:04d}.txt"
            label_file.write_text("0 0.5 0.5 0.2 0.2\n")
        
        # 创建classes.txt
        classes_file = Path(base_dir) / "classes.txt"
        classes = [f"class_{i}" for i in range(num_classes)]
        classes_file.write_text("\n".join(classes))
        
        # 创建data.yaml
        yaml_config = {
            'path': str(base_dir),
            'train': 'images/train',
            'val': 'images/val',
            'nc': num_classes,
            'names': classes
        }
        
        yaml_file = Path(base_dir) / "data.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True)
        
        return str(yaml_file)
        
    except Exception as e:
        print(f"创建测试数据集失败: {str(e)}")
        return None

def test_smart_epochs_calculator():
    """测试智能epochs计算器"""
    print("🧪 开始测试智能epochs计算器...")
    
    try:
        from smart_epochs_calculator import SmartEpochsCalculator
        
        calculator = SmartEpochsCalculator()
        print("✅ 智能计算器初始化成功")
        
        # 测试用例1：极小数据集
        print("\n📊 测试用例1：极小数据集 (50张图片)")
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 35, 15, 2)
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8n', 16)
                    print(f"   推荐轮数: {result.recommended_epochs}")
                    print(f"   置信度: {result.confidence_level}")
                    print(f"   计算依据: {result.calculation_basis[0] if result.calculation_basis else '无'}")
                    
                    # 验证结果合理性
                    assert 150 <= result.recommended_epochs <= 300, f"极小数据集轮数应在150-300之间，实际: {result.recommended_epochs}"
                    print("   ✅ 极小数据集测试通过")
                else:
                    print("   ❌ 无法获取数据集信息")
            else:
                print("   ❌ 无法创建测试数据集")
        
        # 测试用例2：小数据集
        print("\n📊 测试用例2：小数据集 (300张图片)")
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 210, 90, 5)
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8s', 16)
                    print(f"   推荐轮数: {result.recommended_epochs}")
                    print(f"   置信度: {result.confidence_level}")
                    print(f"   计算依据: {result.calculation_basis[0] if result.calculation_basis else '无'}")
                    
                    # 验证结果合理性
                    assert 100 <= result.recommended_epochs <= 250, f"小数据集轮数应在100-250之间，实际: {result.recommended_epochs}"
                    print("   ✅ 小数据集测试通过")
        
        # 测试用例3：中等数据集
        print("\n📊 测试用例3：中等数据集 (1500张图片)")
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 1050, 450, 10)
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8m', 16)
                    print(f"   推荐轮数: {result.recommended_epochs}")
                    print(f"   置信度: {result.confidence_level}")
                    print(f"   计算依据: {result.calculation_basis[0] if result.calculation_basis else '无'}")
                    
                    # 验证结果合理性
                    assert 80 <= result.recommended_epochs <= 180, f"中等数据集轮数应在80-180之间，实际: {result.recommended_epochs}"
                    print("   ✅ 中等数据集测试通过")
        
        # 测试用例4：大数据集
        print("\n📊 测试用例4：大数据集 (5000张图片)")
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 3500, 1500, 20)
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8l', 32)
                    print(f"   推荐轮数: {result.recommended_epochs}")
                    print(f"   置信度: {result.confidence_level}")
                    print(f"   计算依据: {result.calculation_basis[0] if result.calculation_basis else '无'}")
                    
                    # 验证结果合理性
                    assert 50 <= result.recommended_epochs <= 120, f"大数据集轮数应在50-120之间，实际: {result.recommended_epochs}"
                    print("   ✅ 大数据集测试通过")
        
        # 测试用例5：不平衡数据集
        print("\n📊 测试用例5：不平衡数据集 (训练/验证比例不当)")
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = create_test_dataset(temp_dir, 450, 50, 3)  # 90%训练，10%验证
            if yaml_path:
                dataset_info = calculator.get_dataset_info_from_yaml(yaml_path)
                if dataset_info:
                    result = calculator.calculate_smart_epochs(dataset_info, 'yolov8n', 16)
                    print(f"   推荐轮数: {result.recommended_epochs}")
                    print(f"   置信度: {result.confidence_level}")
                    print(f"   额外建议: {result.additional_notes}")
                    
                    # 验证是否有关于数据不平衡的建议
                    has_balance_warning = any("验证" in note for note in result.additional_notes)
                    assert has_balance_warning, "应该有关于验证数据过少的警告"
                    print("   ✅ 不平衡数据集测试通过")
        
        print("\n🎉 所有测试用例通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        print("请确保smart_epochs_calculator.py文件存在于libs目录中")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_training_config_manager():
    """测试训练配置管理器"""
    print("\n🧪 开始测试训练配置管理器...")
    
    try:
        from training_config_manager import TrainingConfigManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = TrainingConfigManager(temp_dir)
            print("✅ 配置管理器初始化成功")
            
            # 测试保存和加载配置
            test_config = {
                "epochs": 150,
                "batch_size": 32,
                "learning_rate": 0.005,
                "model_type": "yolov8s"
            }
            
            # 保存配置
            success = config_manager.save_config(test_config)
            assert success, "配置保存应该成功"
            print("✅ 配置保存测试通过")
            
            # 加载配置
            loaded_config = config_manager.load_config()
            assert loaded_config["epochs"] == 150, f"加载的epochs应为150，实际: {loaded_config['epochs']}"
            assert loaded_config["batch_size"] == 32, f"加载的batch_size应为32，实际: {loaded_config['batch_size']}"
            print("✅ 配置加载测试通过")
            
            # 测试用户调整记录
            config_manager.save_user_adjustment("/test/dataset", 100, 120, "用户手动调整")
            preference = config_manager.get_user_preference_for_dataset("/test/dataset")
            assert preference is not None, "应该能获取到用户偏好"
            assert preference["preferred_epochs"] == 120, f"偏好轮数应为120，实际: {preference['preferred_epochs']}"
            print("✅ 用户调整记录测试通过")
            
            print("🎉 配置管理器测试通过！")
            return True
            
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        print("请确保training_config_manager.py文件存在于libs目录中")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始智能epochs计算功能测试")
    print("=" * 50)
    
    # 测试智能计算器
    calc_success = test_smart_epochs_calculator()
    
    # 测试配置管理器
    config_success = test_training_config_manager()
    
    print("\n" + "=" * 50)
    if calc_success and config_success:
        print("🎉 所有测试通过！智能epochs计算功能正常工作。")
        return True
    else:
        print("❌ 部分测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
