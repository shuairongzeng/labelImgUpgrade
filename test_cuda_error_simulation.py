#!/usr/bin/env python3
"""
模拟原始CUDA错误并测试修复效果
"""

import sys
import os
import tempfile
import unittest.mock as mock

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_torchvision_nms_cuda_error():
    """模拟torchvision::nms CUDA错误"""
    error_message = """
Could not run 'torchvision::nms' with arguments from the 'CUDA' backend. This could be because the operator doesn't exist for this backend, or was omitted during the selective/custom build process (if using custom build). If you are a Facebook employee using PyTorch on mobile, please visit https://fburl.com/ptmfixes for possible resolutions. 'torchvision::nms' is only available for these backends: [CPU, Meta, QuantizedCPU, BackendSelect, Python, FuncTorchDynamicLayerBackMode, Functionalize, Named, Conjugate, Negative, ZeroTensor, ADInplaceOrView, AutogradOther, AutogradCPU, AutogradCUDA, AutogradXLA, AutogradMPS, AutogradXPU, AutogradHPU, AutogradLazy, AutogradMTIA, AutogradMeta, Tracer, AutocastCPU, AutocastMTIA, AutocastXPU, AutocastMPS, AutocastCUDA, FuncTorchBatched, BatchedNestedTensor, FuncTorchVmapMode, Batched, VmapMode, FuncTorchGradWrapper, PythonTLSSnapshot, FuncTorchDynamicLayerFrontMode, PreDispatch, PythonDispatcher].
"""
    return RuntimeError(error_message.strip())

def test_cuda_error_handling():
    """测试CUDA错误处理"""
    print("🔍 测试CUDA错误处理机制...")
    
    try:
        from libs.ai_assistant.yolo_predictor import YOLOPredictor
        from ultralytics import YOLO
        
        # 创建测试图像
        test_image = create_test_image()
        if not test_image:
            print("❌ 无法创建测试图像")
            return False
        
        print(f"  测试图像: {test_image}")
        
        # 创建预测器
        predictor = YOLOPredictor()
        
        # 加载模型
        if not predictor.load_model('yolov8n.pt'):
            print("❌ 模型加载失败")
            return False
        
        print(f"  模型加载成功，当前设备: {predictor.device}")
        
        # 模拟CUDA错误 - 修改模型的__call__方法
        original_call = predictor.model.__call__
        
        def mock_model_call(*args, **kwargs):
            # 第一次调用抛出CUDA错误
            if not hasattr(mock_model_call, 'called'):
                mock_model_call.called = True
                raise simulate_torchvision_nms_cuda_error()
            else:
                # 第二次调用使用原始方法（模拟CPU模式成功）
                return original_call(*args, **kwargs)
        
        # 替换模型调用方法
        predictor.model.__call__ = mock_model_call
        
        print("  模拟CUDA错误并执行预测...")
        
        # 执行预测 - 应该自动回退到CPU
        result = predictor.predict_single(test_image, conf_threshold=0.25)
        
        if result:
            print(f"  ✅ 预测成功（经过CUDA回退），设备: {predictor.device}")
            print(f"  检测到 {len(result.detections)} 个目标")
            print(f"  推理时间: {result.inference_time:.3f}秒")
            
            # 验证设备已切换到CPU
            if predictor.device == "cpu":
                print("  ✅ 成功回退到CPU模式")
                success = True
            else:
                print(f"  ❌ 设备未正确切换，当前: {predictor.device}")
                success = False
        else:
            print("  ❌ 预测失败")
            success = False
        
        # 恢复原始方法
        predictor.model.__call__ = original_call
        
        # 清理测试图像
        if test_image and os.path.exists(test_image):
            os.unlink(test_image)
        
        return success
        
    except Exception as e:
        print(f"❌ CUDA错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

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

def test_ai_assistant_panel_integration():
    """测试AI助手面板集成"""
    print("\n🔍 测试AI助手面板集成...")
    
    try:
        # 这里只测试导入和基本功能，不启动GUI
        from libs.ai_assistant_panel import AIAssistantPanel
        
        print("  ✅ AI助手面板导入成功")
        
        # 测试是否有强制CPU选项相关的方法
        panel_methods = dir(AIAssistantPanel)
        
        if 'on_force_cpu_changed' in panel_methods:
            print("  ✅ 强制CPU模式回调方法存在")
        else:
            print("  ❌ 强制CPU模式回调方法缺失")
            return False
        
        print("  ✅ AI助手面板集成测试通过")
        return True
        
    except ImportError as e:
        print(f"❌ AI助手面板导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ AI助手面板测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("CUDA错误模拟和修复验证测试")
    print("=" * 50)
    
    # 测试1: CUDA错误处理
    cuda_error_ok = test_cuda_error_handling()
    
    # 测试2: AI助手面板集成
    panel_ok = test_ai_assistant_panel_integration()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"CUDA错误处理: {'✅' if cuda_error_ok else '❌'}")
    print(f"面板集成测试: {'✅' if panel_ok else '❌'}")
    
    if cuda_error_ok and panel_ok:
        print("\n🎉 修复验证成功！")
        print("✅ CUDA错误会被自动捕获并回退到CPU模式")
        print("✅ AI助手面板支持强制CPU模式选项")
        print("✅ 用户可以继续正常使用预测功能")
        print("\n💡 使用建议:")
        print("   - 如果遇到CUDA相关错误，系统会自动回退到CPU")
        print("   - 可以在AI助手面板中勾选'强制使用CPU模式'避免CUDA问题")
        print("   - CPU模式虽然较慢，但确保功能稳定可用")
    else:
        print("\n⚠️ 修复验证失败，请检查相关功能。")
    
    return cuda_error_ok and panel_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
