#!/usr/bin/env python3
"""
修复 PyTorch CUDA 兼容性问题的脚本
"""

import subprocess
import sys
import os

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

def main():
    print("PyTorch CUDA 兼容性修复工具")
    print("=" * 50)
    
    # 步骤1: 卸载现有的 PyTorch 相关包
    print("\n步骤 1: 卸载现有的 PyTorch 相关包")
    uninstall_cmd = "pip uninstall torch torchvision torchaudio -y"
    run_command(uninstall_cmd, "卸载 PyTorch 相关包")
    
    # 步骤2: 清理缓存
    print("\n步骤 2: 清理 pip 缓存")
    cache_cmd = "pip cache purge"
    run_command(cache_cmd, "清理 pip 缓存")
    
    # 步骤3: 安装兼容的 PyTorch 版本 (CUDA 11.8)
    print("\n步骤 3: 安装兼容的 PyTorch 版本")
    # 使用 PyTorch 官方推荐的 CUDA 11.8 版本
    install_cmd = "pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118"
    
    if not run_command(install_cmd, "安装 PyTorch CUDA 11.8 版本"):
        print("\n尝试备用安装方法...")
        # 备用方法：使用 conda-forge
        backup_cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        run_command(backup_cmd, "使用备用方法安装 PyTorch")
    
    # 步骤4: 验证安装
    print("\n步骤 4: 验证安装")
    verify_script = '''
import torch
import torchvision
print(f"PyTorch 版本: {torch.__version__}")
print(f"torchvision 版本: {torchvision.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 设备数量: {torch.cuda.device_count()}")
    print(f"当前 GPU: {torch.cuda.get_device_name(0)}")

# 测试 torchvision NMS 操作
try:
    from torchvision.ops import nms
    import torch
    boxes = torch.tensor([[0, 0, 10, 10], [5, 5, 15, 15]], dtype=torch.float32)
    scores = torch.tensor([0.9, 0.8], dtype=torch.float32)
    if torch.cuda.is_available():
        boxes = boxes.cuda()
        scores = scores.cuda()
        result = nms(boxes, scores, 0.5)
        print("✓ CUDA NMS 测试成功")
    else:
        result = nms(boxes, scores, 0.5)
        print("✓ CPU NMS 测试成功")
except Exception as e:
    print(f"✗ NMS 测试失败: {e}")
'''
    
    with open("verify_pytorch.py", "w", encoding="utf-8") as f:
        f.write(verify_script)
    
    run_command("python verify_pytorch.py", "验证 PyTorch 安装")
    
    # 清理临时文件
    if os.path.exists("verify_pytorch.py"):
        os.remove("verify_pytorch.py")
    
    print("\n" + "=" * 50)
    print("修复完成！")
    print("如果验证成功，现在可以重新尝试 YOLO 训练。")
    print("如果仍有问题，可能需要:")
    print("1. 重启 Python 环境")
    print("2. 检查 CUDA 驱动版本")
    print("3. 使用 CPU 模式训练 (device='cpu')")

if __name__ == "__main__":
    main()
