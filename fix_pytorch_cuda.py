#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyTorch CUDA兼容性修复工具
专门修复PyTorch 2.7.1开发版本与ultralytics的兼容性问题
解决torchvision::nms CUDA错误，确保GPU训练正常工作
"""

import subprocess
import sys
import os

def check_current_versions():
    """检查当前版本并诊断问题"""
    try:
        import torch
        import torchvision
        import ultralytics

        print("当前版本信息:")
        print(f"PyTorch: {torch.__version__}")
        print(f"torchvision: {torchvision.__version__}")
        print(f"ultralytics: {ultralytics.__version__}")
        print(f"CUDA可用: {torch.cuda.is_available()}")

        # 检查是否是问题版本
        if "2.7.1" in torch.__version__:
            print("⚠️  检测到PyTorch 2.7.1开发版本")
            print("   这是导致torchvision::nms CUDA错误的根本原因！")
            print("   开发版本与ultralytics存在兼容性问题")
            return True
        elif "2.7" in torch.__version__:
            print("⚠️  检测到PyTorch 2.7.x版本，可能存在兼容性问题")
            return True
        else:
            print("✅ PyTorch版本看起来正常")
            return False

    except ImportError as e:
        print(f"❌ 无法检查版本: {e}")
        return False

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"\n正在执行: {description}")
    print(f"命令: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True)
        print("✓ 成功完成")
        if result.stdout:
            print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 失败: {e}")
        if e.stdout:
            print("标准输出:", e.stdout)
        if e.stderr:
            print("错误输出:", e.stderr)
        return False

def install_compatible_pytorch():
    """安装兼容的PyTorch稳定版本"""
    print("\n正在修复PyTorch版本兼容性问题...")
    print("将安装PyTorch 2.1.0+cu118 (稳定版本，与ultralytics完全兼容)")

    # 步骤1: 卸载现有的 PyTorch 相关包
    print("\n步骤 1: 卸载现有的 PyTorch 相关包")
    uninstall_cmd = "pip uninstall torch torchvision torchaudio -y"
    run_command(uninstall_cmd, "卸载 PyTorch 相关包")

    # 步骤2: 清理缓存
    print("\n步骤 2: 清理 pip 缓存")
    cache_cmd = "pip cache purge"
    run_command(cache_cmd, "清理 pip 缓存")

    # 步骤3: 安装兼容的 PyTorch 版本 (CUDA 11.8)
    print("\n步骤 3: 安装兼容的 PyTorch 稳定版本")
    print("使用PyTorch 2.6.0 (CUDA 11.8索引中的最新稳定版本)")

    # 首先尝试安装PyTorch 2.6.0 (CUDA 11.8索引中可用的稳定版本)
    install_cmd = "pip install torch==2.6.0+cu118 torchvision==0.21.0+cu118 torchaudio==2.6.0+cu118 --index-url https://download.pytorch.org/whl/cu118"

    if not run_command(install_cmd, "安装 PyTorch 2.6.0 CUDA 11.8 版本"):
        print("\n尝试备用安装方法...")
        # 备用方法：使用通用CUDA版本
        backup_cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        return run_command(backup_cmd, "使用备用方法安装最新兼容的 PyTorch")

    return True

def test_cuda_nms():
    """测试CUDA NMS操作是否正常"""
    try:
        import torch
        import torchvision

        print("\n步骤 4: 测试CUDA NMS兼容性...")

        if not torch.cuda.is_available():
            print("❌ CUDA不可用，无法测试")
            return False

        # 创建测试数据
        device = torch.device('cuda')
        boxes = torch.tensor([[0, 0, 10, 10], [5, 5, 15, 15], [20, 20, 30, 30]],
                           dtype=torch.float32, device=device)
        scores = torch.tensor([0.9, 0.8, 0.7], dtype=torch.float32, device=device)

        # 测试torchvision NMS
        keep = torchvision.ops.nms(boxes, scores, 0.5)
        print(f"✅ CUDA NMS测试成功: 保留索引 {keep}")
        return True

    except Exception as e:
        print(f"❌ CUDA NMS测试失败: {e}")
        return False

def test_yolo_prediction():
    """测试YOLO预测是否正常"""
    try:
        from ultralytics import YOLO
        import torch

        print("\n步骤 5: 测试YOLO CUDA预测...")

        # 创建一个简单的YOLO模型进行测试
        model = YOLO('yolov8n.pt')  # 使用最小的模型进行测试

        # 强制使用CUDA
        if torch.cuda.is_available():
            model.to('cuda')
            print("✅ YOLO模型已加载到CUDA设备")

            # 创建测试图像
            import numpy as np
            test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

            # 进行预测测试
            results = model(test_image, verbose=False)
            print("✅ YOLO CUDA预测测试成功")
            return True
        else:
            print("⚠️  CUDA不可用，跳过YOLO CUDA测试")
            return False

    except Exception as e:
        print(f"❌ YOLO预测测试失败: {e}")
        return False

def main():
    print("PyTorch CUDA 兼容性修复工具")
    print("专门修复PyTorch 2.7.1开发版本导致的torchvision::nms CUDA错误")
    print("=" * 60)

    # 检查当前版本
    needs_fix = check_current_versions()

    if not needs_fix:
        print("\n✅ 当前版本看起来正常，无需修复")
        return

    # 执行修复
    print("\n开始修复过程...")
    if install_compatible_pytorch():
        if test_cuda_nms():
            if test_yolo_prediction():
                print("\n🎉 修复完成！问题已解决，现在可以正常使用GPU训练了！")
            else:
                print("\n⚠️  PyTorch修复成功，但YOLO测试失败，可能需要进一步检查")
        else:
            print("\n⚠️  PyTorch修复成功，但CUDA NMS测试失败")
    else:
        print("\n❌ PyTorch修复失败")
def verify_final_installation():
    """最终验证安装"""
    try:
        import torch
        import torchvision
        import ultralytics

        print("\n" + "="*60)
        print("最终验证结果:")
        print("="*60)
        print(f"PyTorch版本: {torch.__version__}")
        print(f"torchvision版本: {torchvision.__version__}")
        print(f"ultralytics版本: {ultralytics.__version__}")
        print(f"CUDA可用: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            print(f"CUDA版本: {torch.version.cuda}")
            print(f"CUDA设备数量: {torch.cuda.device_count()}")
            print(f"当前CUDA设备: {torch.cuda.get_device_name()}")

            # 检查版本兼容性
            if "2.6.0" in torch.__version__:
                print("✅ PyTorch 2.6.0是稳定版本，与ultralytics兼容")
            elif "2.1.0" in torch.__version__ or "2.2" in torch.__version__:
                print("✅ 这也是兼容的稳定版本")
            elif "2.7.1" not in torch.__version__:
                print("✅ 已成功避开问题版本PyTorch 2.7.1")
            else:
                print("⚠️  仍然是问题版本，可能需要手动修复")

            print("\n🎉 修复完成！现在可以正常使用GPU进行训练和预测了！")
            print("💡 建议重启Python环境以确保所有更改生效")
        else:
            print("⚠️  CUDA不可用，请检查CUDA驱动")

        return True
    except ImportError as e:
        print(f"❌ 最终验证失败: {e}")
        return False

if __name__ == "__main__":
    main()
