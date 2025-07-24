#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YOLO集成技术调研测试脚本
测试ultralytics库的功能和性能
"""

import sys
import os
import time
import traceback
from pathlib import Path

def test_ultralytics_installation():
    """测试ultralytics库安装"""
    print("=" * 50)
    print("测试 ultralytics 库安装")
    print("=" * 50)
    
    try:
        import ultralytics
        print(f"✓ ultralytics 版本: {ultralytics.__version__}")
        return True
    except ImportError as e:
        print(f"✗ ultralytics 未安装: {e}")
        print("请运行: pip install ultralytics")
        return False

def test_torch_installation():
    """测试PyTorch安装"""
    print("\n" + "=" * 50)
    print("测试 PyTorch 安装")
    print("=" * 50)
    
    try:
        import torch
        print(f"✓ PyTorch 版本: {torch.__version__}")
        print(f"✓ CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ CUDA 版本: {torch.version.cuda}")
            print(f"✓ GPU 数量: {torch.cuda.device_count()}")
        return True
    except ImportError as e:
        print(f"✗ PyTorch 未安装: {e}")
        return False

def test_opencv_installation():
    """测试OpenCV安装"""
    print("\n" + "=" * 50)
    print("测试 OpenCV 安装")
    print("=" * 50)
    
    try:
        import cv2
        print(f"✓ OpenCV 版本: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"✗ OpenCV 未安装: {e}")
        print("请运行: pip install opencv-python")
        return False

def test_yolo_model_loading():
    """测试YOLO模型加载"""
    print("\n" + "=" * 50)
    print("测试 YOLO 模型加载")
    print("=" * 50)
    
    try:
        from ultralytics import YOLO
        
        # 测试加载预训练模型
        print("正在加载 YOLOv8n 模型...")
        start_time = time.time()
        model = YOLO('yolov8n.pt')  # 会自动下载
        load_time = time.time() - start_time
        
        print(f"✓ 模型加载成功，耗时: {load_time:.2f}秒")
        print(f"✓ 模型类型: {type(model)}")
        print(f"✓ 模型设备: {model.device}")
        
        # 获取模型信息
        if hasattr(model, 'model') and hasattr(model.model, 'names'):
            class_names = model.model.names
            print(f"✓ 类别数量: {len(class_names)}")
            print(f"✓ 前5个类别: {list(class_names.values())[:5]}")
        
        return model
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        traceback.print_exc()
        return None

def test_image_prediction(model):
    """测试图像预测"""
    print("\n" + "=" * 50)
    print("测试图像预测")
    print("=" * 50)
    
    if model is None:
        print("✗ 模型未加载，跳过预测测试")
        return False
    
    try:
        # 查找测试图像
        test_image_paths = [
            "demo/demo.jpg",
            "demo/demo3.jpg", 
            "demo/demo4.png",
            "demo/demo5.png"
        ]
        
        test_image = None
        for path in test_image_paths:
            if os.path.exists(path):
                test_image = path
                break
        
        if test_image is None:
            print("✗ 未找到测试图像")
            return False
        
        print(f"使用测试图像: {test_image}")
        
        # 执行预测
        start_time = time.time()
        results = model(test_image)
        predict_time = time.time() - start_time
        
        print(f"✓ 预测完成，耗时: {predict_time:.2f}秒")
        
        # 分析结果
        if results and len(results) > 0:
            result = results[0]
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes
                print(f"✓ 检测到 {len(boxes)} 个目标")
                
                # 显示前几个检测结果
                for i, box in enumerate(boxes[:3]):  # 只显示前3个
                    if hasattr(box, 'conf') and hasattr(box, 'cls'):
                        conf = float(box.conf[0]) if len(box.conf) > 0 else 0
                        cls_id = int(box.cls[0]) if len(box.cls) > 0 else 0
                        cls_name = model.model.names.get(cls_id, f"class_{cls_id}")
                        print(f"  - 目标 {i+1}: {cls_name} (置信度: {conf:.3f})")
            else:
                print("✓ 预测完成，但未检测到目标")
        
        return True
    except Exception as e:
        print(f"✗ 预测失败: {e}")
        traceback.print_exc()
        return False

def test_batch_prediction(model):
    """测试批量预测"""
    print("\n" + "=" * 50)
    print("测试批量预测")
    print("=" * 50)
    
    if model is None:
        print("✗ 模型未加载，跳过批量预测测试")
        return False
    
    try:
        # 收集所有demo图像
        demo_dir = Path("demo")
        if not demo_dir.exists():
            print("✗ demo目录不存在")
            return False
        
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(demo_dir.glob(ext))
        
        if not image_files:
            print("✗ demo目录中没有图像文件")
            return False
        
        print(f"找到 {len(image_files)} 个图像文件")
        
        # 批量预测
        start_time = time.time()
        results = model(image_files)
        batch_time = time.time() - start_time
        
        print(f"✓ 批量预测完成，耗时: {batch_time:.2f}秒")
        print(f"✓ 平均每张图像: {batch_time/len(image_files):.3f}秒")
        
        # 统计结果
        total_detections = 0
        for result in results:
            if hasattr(result, 'boxes') and result.boxes is not None:
                total_detections += len(result.boxes)
        
        print(f"✓ 总共检测到 {total_detections} 个目标")
        
        return True
    except Exception as e:
        print(f"✗ 批量预测失败: {e}")
        traceback.print_exc()
        return False

def test_memory_usage():
    """测试内存使用情况"""
    print("\n" + "=" * 50)
    print("测试内存使用情况")
    print("=" * 50)
    
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        print(f"✓ 当前内存使用: {memory_info.rss / 1024 / 1024:.1f} MB")
        print(f"✓ 虚拟内存使用: {memory_info.vms / 1024 / 1024:.1f} MB")
        return True
    except ImportError:
        print("✗ psutil 未安装，无法获取内存信息")
        print("可选安装: pip install psutil")
        return False

def generate_requirements():
    """生成AI功能所需的依赖包列表"""
    print("\n" + "=" * 50)
    print("生成AI功能依赖包列表")
    print("=" * 50)
    
    ai_requirements = [
        "# AI功能依赖包",
        "ultralytics>=8.0.0  # YOLOv8支持",
        "torch>=1.9.0        # PyTorch深度学习框架", 
        "torchvision>=0.10.0 # PyTorch视觉库",
        "opencv-python>=4.5.0 # OpenCV图像处理",
        "numpy>=1.21.0       # 数值计算",
        "pillow>=8.0.0       # 图像处理",
        "matplotlib>=3.3.0   # 数据可视化",
        "pyyaml>=5.4.0       # YAML配置文件",
        "psutil>=5.8.0       # 系统监控(可选)",
        "",
        "# 现有依赖包",
        "pyqt5>=5.14.1       # GUI框架",
        "lxml>=4.9.1         # XML处理"
    ]
    
    requirements_file = "requirements_ai.txt"
    with open(requirements_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ai_requirements))
    
    print(f"✓ 依赖包列表已保存到: {requirements_file}")
    return requirements_file

def main():
    """主测试函数"""
    print("labelImg YOLO集成技术调研")
    print("=" * 60)
    
    # 基础环境测试
    torch_ok = test_torch_installation()
    cv_ok = test_opencv_installation()
    ultra_ok = test_ultralytics_installation()
    
    if not (torch_ok and cv_ok and ultra_ok):
        print("\n" + "=" * 60)
        print("⚠️  部分依赖包未安装，请先安装所需依赖")
        print("建议运行: pip install ultralytics opencv-python")
        return False
    
    # YOLO功能测试
    model = test_yolo_model_loading()
    test_image_prediction(model)
    test_batch_prediction(model)
    test_memory_usage()
    
    # 生成依赖包列表
    generate_requirements()
    
    print("\n" + "=" * 60)
    print("🎉 YOLO集成技术调研完成！")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()
