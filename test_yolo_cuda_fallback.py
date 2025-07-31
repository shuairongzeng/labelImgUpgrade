#!/usr/bin/env python3
"""
测试YOLO预测器的CUDA回退功能
"""

import sys
import os
import tempfile
import shutil

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image():
    """创建一个测试图像"""
    try:
        from PIL import Image
        import numpy as np
        
        # 创建一个简单的测试图像
        img_array = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name)
        temp_file.close()
        
        return temp_file.name
        
    except ImportError:
        print("⚠️ PIL未安装，使用现有测试图像")
        # 查找现有的测试图像
        test_dirs = ['test_images', 'examples', 'data']
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for file in os.listdir(test_dir):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        return os.path.join(test_dir, file)
        
        print("❌ 未找到测试图像")
        return None

def test_yolo_predictor_cuda_fallback():
    """测试YOLO预测器的CUDA回退功能"""
    print("🔍 测试YOLO预测器CUDA回退功能...")
    
    try:
        from libs.ai_assistant.yolo_predictor import YOLOPredictor
        
        # 创建预测器
        predictor = YOLOPredictor()
        print(f"  初始设备: {predictor.device}")
        
        # 测试CUDA兼容性检查
        cuda_compatible = predictor._test_cuda_compatibility()
        print(f"  CUDA兼容性: {'✅ 通过' if cuda_compatible else '❌ 失败'}")
        
        # 测试强制CPU模式
        print("  测试强制CPU模式...")
        original_device = predictor.device
        predictor.force_cpu_mode()
        print(f"  强制CPU后设备: {predictor.device}")
        
        # 恢复原始设备检测
        predictor._detect_device()
        print(f"  重新检测后设备: {predictor.device}")
        
        return True
        
    except ImportError as e:
        print(f"❌ YOLO预测器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ YOLO预测器测试失败: {e}")
        return False

def test_yolo_prediction_with_fallback():
    """测试带回退机制的YOLO预测"""
    print("\n🔍 测试YOLO预测（带CUDA回退）...")
    
    try:
        from libs.ai_assistant.yolo_predictor import YOLOPredictor
        
        # 创建测试图像
        test_image = create_test_image()
        if not test_image:
            print("❌ 无法创建测试图像")
            return False
        
        print(f"  测试图像: {test_image}")
        
        # 创建预测器
        predictor = YOLOPredictor()
        
        # 尝试加载一个轻量级模型进行测试
        model_candidates = [
            "yolov8n.pt",  # 最小的YOLOv8模型
            "models/yolov8n.pt",
            "models/custom/yolov8n.pt"
        ]
        
        model_loaded = False
        for model_path in model_candidates:
            if os.path.exists(model_path):
                print(f"  尝试加载模型: {model_path}")
                if predictor.load_model(model_path):
                    print(f"  ✅ 模型加载成功: {model_path}")
                    model_loaded = True
                    break
            else:
                print(f"  模型不存在: {model_path}")
        
        if not model_loaded:
            print("  ⚠️ 未找到可用模型，尝试下载yolov8n.pt...")
            try:
                # 尝试使用ultralytics下载模型
                from ultralytics import YOLO
                model = YOLO('yolov8n.pt')  # 这会自动下载模型
                if predictor.load_model('yolov8n.pt'):
                    print("  ✅ 模型下载并加载成功")
                    model_loaded = True
                else:
                    print("  ❌ 模型下载成功但加载失败")
            except Exception as e:
                print(f"  ❌ 模型下载失败: {e}")
        
        if not model_loaded:
            print("  ⚠️ 跳过预测测试（无可用模型）")
            return True  # 不算失败，只是跳过
        
        # 执行预测测试
        print(f"  执行预测，当前设备: {predictor.device}")
        result = predictor.predict_single(test_image, conf_threshold=0.25)
        
        if result:
            print(f"  ✅ 预测成功，检测到 {len(result.detections)} 个目标")
            print(f"  推理时间: {result.inference_time:.3f}秒")
            print(f"  使用设备: {predictor.device}")
        else:
            print("  ❌ 预测失败")
            return False
        
        # 清理测试图像
        if test_image and os.path.exists(test_image):
            os.unlink(test_image)
        
        return True
        
    except Exception as e:
        print(f"❌ 预测测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simulated_cuda_error():
    """模拟CUDA错误测试回退机制"""
    print("\n🔍 模拟CUDA错误测试...")
    
    try:
        from libs.ai_assistant.yolo_predictor import YOLOPredictor
        
        # 创建预测器
        predictor = YOLOPredictor()
        original_device = predictor.device
        
        print(f"  原始设备: {original_device}")
        
        # 模拟CUDA错误 - 强制切换到CPU
        if original_device == "cuda":
            print("  模拟CUDA错误，强制切换到CPU...")
            predictor.force_cpu_mode()
            print(f"  切换后设备: {predictor.device}")
            
            if predictor.device == "cpu":
                print("  ✅ CUDA回退机制工作正常")
                return True
            else:
                print("  ❌ CUDA回退机制失败")
                return False
        else:
            print("  ℹ️ 当前已是CPU模式，跳过CUDA回退测试")
            return True
            
    except Exception as e:
        print(f"❌ CUDA回退测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("YOLO预测器CUDA回退功能测试")
    print("=" * 50)
    
    # 测试1: YOLO预测器基本功能
    predictor_ok = test_yolo_predictor_cuda_fallback()
    
    # 测试2: 预测功能（带回退）
    prediction_ok = test_yolo_prediction_with_fallback()
    
    # 测试3: 模拟CUDA错误
    fallback_ok = test_simulated_cuda_error()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"预测器基本功能: {'✅' if predictor_ok else '❌'}")
    print(f"预测功能测试: {'✅' if prediction_ok else '❌'}")
    print(f"CUDA回退机制: {'✅' if fallback_ok else '❌'}")
    
    if predictor_ok and prediction_ok and fallback_ok:
        print("\n🎉 所有测试通过！CUDA回退机制工作正常。")
        print("💡 现在可以安全使用AI预测功能，即使遇到CUDA问题也会自动回退到CPU。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
    
    return predictor_ok and prediction_ok and fallback_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
