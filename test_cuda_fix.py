#!/usr/bin/env python3
"""
测试 CUDA 兼容性修复
"""

import sys
import os
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pytorch_installation():
    """测试 PyTorch 安装状态"""
    print("🔍 检查 PyTorch 安装状态...")
    
    try:
        import torch
        print(f"✅ PyTorch 版本: {torch.__version__}")
        print(f"✅ CUDA 可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA 版本: {torch.version.cuda}")
            print(f"✅ GPU 设备数量: {torch.cuda.device_count()}")
            print(f"✅ 当前 GPU: {torch.cuda.get_device_name(0)}")
        
        return True
    except ImportError as e:
        print(f"❌ PyTorch 未安装: {e}")
        return False
    except Exception as e:
        print(f"❌ PyTorch 检查失败: {e}")
        return False

def test_torchvision_nms():
    """测试 torchvision NMS 操作"""
    print("\n🔍 测试 torchvision NMS 操作...")
    
    try:
        import torch
        import torchvision
        from torchvision.ops import nms
        
        print(f"✅ torchvision 版本: {torchvision.__version__}")
        
        # 创建测试数据
        boxes = torch.tensor([[0, 0, 10, 10], [5, 5, 15, 15]], dtype=torch.float32)
        scores = torch.tensor([0.9, 0.8], dtype=torch.float32)
        
        # 测试 CPU NMS
        print("  测试 CPU NMS...")
        result_cpu = nms(boxes, scores, 0.5)
        print(f"  ✅ CPU NMS 成功: {result_cpu}")
        
        # 测试 CUDA NMS（如果可用）
        if torch.cuda.is_available():
            print("  测试 CUDA NMS...")
            try:
                boxes_cuda = boxes.cuda()
                scores_cuda = scores.cuda()
                result_cuda = nms(boxes_cuda, scores_cuda, 0.5)
                print(f"  ✅ CUDA NMS 成功: {result_cuda}")
                return True
            except Exception as e:
                print(f"  ❌ CUDA NMS 失败: {e}")
                print("  ℹ️ 将自动切换到 CPU 训练")
                return False
        else:
            print("  ℹ️ CUDA 不可用，使用 CPU 训练")
            return True
            
    except ImportError as e:
        print(f"❌ torchvision 未安装: {e}")
        return False
    except Exception as e:
        print(f"❌ torchvision 测试失败: {e}")
        return False

def test_trainer_cuda_fallback():
    """测试训练器的 CUDA 回退功能"""
    print("\n🔍 测试训练器 CUDA 回退功能...")
    
    try:
        from libs.ai_assistant.yolo_trainer import YOLOTrainer, TrainingConfig
        
        trainer = YOLOTrainer()
        
        # 创建 CUDA 配置
        config = TrainingConfig(
            dataset_config="datasets/training_dataset/data.yaml",
            epochs=1,
            batch_size=1,
            learning_rate=0.01,
            model_type="pretrained",
            model_path="yolov8n.pt",
            model_name="yolov8n",
            device="cuda",  # 故意设置为 CUDA
            output_dir=tempfile.mkdtemp()
        )
        
        print(f"  原始设备配置: {config.device}")
        
        # 验证配置（会自动检查 CUDA 兼容性）
        is_valid = trainer.validate_config(config)
        
        print(f"  最终设备配置: {config.device}")
        print(f"  配置验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        return is_valid
        
    except ImportError as e:
        print(f"❌ 训练器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 训练器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("CUDA 兼容性修复测试")
    print("=" * 50)
    
    # 测试 1: PyTorch 安装
    pytorch_ok = test_pytorch_installation()
    
    # 测试 2: torchvision NMS
    nms_ok = test_torchvision_nms() if pytorch_ok else False
    
    # 测试 3: 训练器回退功能
    trainer_ok = test_trainer_cuda_fallback() if pytorch_ok else False
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"PyTorch 安装: {'✅' if pytorch_ok else '❌'}")
    print(f"torchvision NMS: {'✅' if nms_ok else '❌'}")
    print(f"训练器回退: {'✅' if trainer_ok else '❌'}")
    
    if pytorch_ok and trainer_ok:
        print("\n🎉 修复成功！现在可以尝试重新训练。")
        print("💡 如果 CUDA 有问题，训练器会自动切换到 CPU 模式。")
    else:
        print("\n⚠️ 仍有问题需要解决。")
        
        if not pytorch_ok:
            print("建议: 重新安装 PyTorch")
            print("命令: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")

if __name__ == "__main__":
    main()
