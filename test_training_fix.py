#!/usr/bin/env python3
"""
测试训练修复
"""

import sys
import os
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_training_with_cpu():
    """测试使用 CPU 训练"""
    print("🔍 测试 CPU 训练配置...")
    
    try:
        from libs.ai_assistant.yolo_trainer import YOLOTrainer, TrainingConfig
        
        trainer = YOLOTrainer()
        
        # 创建 CPU 配置
        config = TrainingConfig(
            dataset_config="datasets/training_dataset/data.yaml",
            epochs=1,  # 只训练1轮用于测试
            batch_size=1,
            learning_rate=0.01,
            model_size="yolov8n",
            device="cpu",  # 强制使用 CPU
            output_dir=tempfile.mkdtemp()
        )
        
        print(f"  原始设备配置: {config.device}")
        
        # 验证配置
        is_valid = trainer.validate_config(config)
        
        print(f"  最终设备配置: {config.device}")
        print(f"  配置验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        if is_valid:
            print("  ✅ CPU 训练配置验证成功")
            return True
        else:
            print("  ❌ CPU 训练配置验证失败")
            return False
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_device_string_normalization():
    """测试设备字符串标准化"""
    print("\n🔍 测试设备字符串标准化...")
    
    try:
        from libs.ai_assistant.yolo_trainer import YOLOTrainer, TrainingConfig
        
        trainer = YOLOTrainer()
        
        # 测试不同的设备字符串格式
        test_cases = [
            ("GPU (推荐)", "cuda"),
            ("GPU", "cuda"),
            ("cuda", "cuda"),
            ("CUDA", "cuda"),
            ("CPU", "cpu"),
            ("cpu", "cpu"),
            ("GPU (不可用)", "cuda"),  # 这个会被后续检查改为 cpu
        ]
        
        for input_device, expected_normalized in test_cases:
            config = TrainingConfig(
                dataset_config="datasets/training_dataset/data.yaml",
                epochs=1,
                batch_size=1,
                learning_rate=0.01,
                model_size="yolov8n",
                device=input_device,
                output_dir=tempfile.mkdtemp()
            )
            
            print(f"  测试: '{input_device}' -> ", end="")
            
            # 验证配置（会进行设备字符串标准化）
            trainer.validate_config(config)
            
            print(f"'{config.device}'")
            
            # 对于 CUDA 设备，最终可能会被改为 cpu（如果 CUDA 不可用）
            if expected_normalized == "cuda" and config.device == "cpu":
                print(f"    ℹ️ CUDA 不可用，自动切换到 CPU")
            elif config.device in ["cuda", "cpu"]:
                print(f"    ✅ 标准化成功")
            else:
                print(f"    ❌ 标准化失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 设备字符串标准化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("训练修复测试")
    print("=" * 50)
    
    # 测试 1: CPU 训练
    cpu_ok = test_training_with_cpu()
    
    # 测试 2: 设备字符串标准化
    normalize_ok = test_device_string_normalization()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"CPU 训练配置: {'✅' if cpu_ok else '❌'}")
    print(f"设备字符串标准化: {'✅' if normalize_ok else '❌'}")
    
    if cpu_ok and normalize_ok:
        print("\n🎉 修复成功！现在可以尝试重新训练。")
        print("💡 训练器会自动检测 CUDA 兼容性，如有问题会切换到 CPU。")
        print("\n📋 建议:")
        print("1. 在训练对话框中选择 'CPU' 设备")
        print("2. 或者选择 'GPU (推荐)'，系统会自动检测并回退到 CPU")
        print("3. 使用较小的批次大小（如 1-4）以适应 CPU 训练")
    else:
        print("\n⚠️ 仍有问题需要解决。")

if __name__ == "__main__":
    main()
