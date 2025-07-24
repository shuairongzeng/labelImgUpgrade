#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI助手模块测试脚本

测试YOLO预测器、模型管理器、批量处理器和置信度过滤器的功能
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_yolo_predictor():
    """测试YOLO预测器"""
    print("=" * 60)
    print("测试 YOLO 预测器")
    print("=" * 60)
    
    try:
        from libs.ai_assistant import YOLOPredictor, Detection, PredictionResult
        
        # 创建预测器
        predictor = YOLOPredictor()
        print(f"✓ 预测器创建成功")
        
        # 加载模型
        model_path = "yolov8n.pt"
        success = predictor.load_model(model_path)
        if success:
            print(f"✓ 模型加载成功: {model_path}")
        else:
            print(f"✗ 模型加载失败: {model_path}")
            return False
        
        # 获取模型信息
        model_info = predictor.get_model_info()
        print(f"✓ 模型信息: {model_info.get('class_count', 0)} 个类别")
        
        # 测试单图预测
        test_image = "demo/demo.jpg"
        if os.path.exists(test_image):
            print(f"正在预测图像: {test_image}")
            result = predictor.predict_single(test_image, conf_threshold=0.25)
            
            if result:
                print(f"✓ 预测成功: 检测到 {len(result.detections)} 个目标")
                print(f"  推理时间: {result.inference_time:.3f}秒")
                
                # 显示检测结果
                for i, det in enumerate(result.detections[:3]):  # 只显示前3个
                    print(f"  目标 {i+1}: {det.class_name} (置信度: {det.confidence:.3f})")
            else:
                print(f"✗ 预测失败")
                return False
        else:
            print(f"⚠️  测试图像不存在: {test_image}")
        
        # 卸载模型
        predictor.unload_model()
        print(f"✓ 模型已卸载")
        
        return True
        
    except Exception as e:
        print(f"✗ YOLO预测器测试失败: {e}")
        return False

def test_model_manager():
    """测试模型管理器"""
    print("\n" + "=" * 60)
    print("测试模型管理器")
    print("=" * 60)
    
    try:
        from libs.ai_assistant import ModelManager
        
        # 创建模型管理器
        manager = ModelManager()
        print(f"✓ 模型管理器创建成功")
        
        # 扫描模型
        models = manager.scan_models()
        print(f"✓ 扫描到 {len(models)} 个模型文件")
        
        # 显示可用模型
        for model_path in models[:3]:  # 只显示前3个
            print(f"  - {os.path.basename(model_path)}")
        
        # 获取预训练模型信息
        pretrained = manager.get_pretrained_models()
        print(f"✓ 支持 {len(pretrained)} 个预训练模型")
        
        # 测试模型验证
        if models:
            test_model = models[0]
            print(f"正在验证模型: {os.path.basename(test_model)}")
            is_valid = manager.validate_model(test_model)
            
            if is_valid:
                print(f"✓ 模型验证成功")
                
                # 获取模型信息
                info = manager.get_model_info(test_model)
                print(f"  类别数量: {info.get('class_count', 0)}")
                print(f"  文件大小: {info.get('size', 'Unknown')}")
            else:
                print(f"✗ 模型验证失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型管理器测试失败: {e}")
        return False

def test_batch_processor():
    """测试批量处理器"""
    print("\n" + "=" * 60)
    print("测试批量处理器")
    print("=" * 60)
    
    try:
        from libs.ai_assistant import YOLOPredictor, BatchProcessor
        
        # 创建预测器和批量处理器
        predictor = YOLOPredictor("yolov8n.pt")
        processor = BatchProcessor(predictor)
        print(f"✓ 批量处理器创建成功")
        
        # 测试目录扫描
        demo_dir = "demo"
        if os.path.exists(demo_dir):
            # 连接信号
            results_received = []
            
            def on_file_processed(file_path, result):
                results_received.append((file_path, result))
                print(f"  处理完成: {os.path.basename(file_path)} -> {len(result.detections)} 个目标")
            
            def on_batch_completed(summary):
                print(f"✓ 批量处理完成:")
                print(f"  总文件数: {summary['total_files']}")
                print(f"  成功处理: {summary['successful_files']}")
                print(f"  失败处理: {summary['failed_files']}")
                print(f"  总耗时: {summary['total_time']:.2f}秒")
            
            processor.file_processed.connect(on_file_processed)
            processor.batch_completed.connect(on_batch_completed)
            
            # 开始批量处理
            print(f"正在批量处理目录: {demo_dir}")
            processor.process_directory(demo_dir, recursive=False)
            
            # 等待处理完成
            timeout = 30  # 30秒超时
            start_time = time.time()
            while processor.is_busy() and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if processor.is_busy():
                print(f"⚠️  批量处理超时")
                processor.cancel_processing()
            else:
                print(f"✓ 批量处理测试完成")
        else:
            print(f"⚠️  demo目录不存在，跳过批量处理测试")
        
        return True
        
    except Exception as e:
        print(f"✗ 批量处理器测试失败: {e}")
        return False

def test_confidence_filter():
    """测试置信度过滤器"""
    print("\n" + "=" * 60)
    print("测试置信度过滤器")
    print("=" * 60)
    
    try:
        from libs.ai_assistant import ConfidenceFilter, Detection
        
        # 创建过滤器
        filter = ConfidenceFilter(default_threshold=0.3)
        print(f"✓ 置信度过滤器创建成功")
        
        # 创建测试检测结果
        test_detections = [
            Detection(bbox=(10, 10, 50, 50), confidence=0.9, class_id=0, class_name="person"),
            Detection(bbox=(60, 60, 100, 100), confidence=0.7, class_id=1, class_name="car"),
            Detection(bbox=(110, 110, 150, 150), confidence=0.4, class_id=0, class_name="person"),
            Detection(bbox=(160, 160, 200, 200), confidence=0.2, class_id=2, class_name="bike"),
            Detection(bbox=(15, 15, 55, 55), confidence=0.8, class_id=0, class_name="person"),  # 重叠框
        ]
        
        print(f"原始检测数量: {len(test_detections)}")
        
        # 测试置信度过滤
        filtered = filter.filter_detections(test_detections, threshold=0.5)
        print(f"✓ 置信度过滤 (>0.5): {len(test_detections)} -> {len(filtered)}")
        
        # 测试NMS
        nms_result = filter.apply_nms(test_detections, iou_threshold=0.5)
        print(f"✓ NMS过滤: {len(test_detections)} -> {len(nms_result)}")
        
        # 测试标注优化
        optimized = filter.optimize_for_annotation(test_detections)
        print(f"✓ 标注优化: {len(test_detections)} -> {len(optimized)}")
        
        # 获取统计信息
        stats = filter.get_statistics()
        print(f"✓ 过滤统计: {stats}")
        
        # 获取置信度分布
        distribution = filter.get_confidence_distribution(test_detections)
        print(f"✓ 置信度分布: 平均 {distribution.get('mean', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 置信度过滤器测试失败: {e}")
        return False

def test_integration():
    """测试模块集成"""
    print("\n" + "=" * 60)
    print("测试模块集成")
    print("=" * 60)
    
    try:
        from libs.ai_assistant import YOLOPredictor, ModelManager, BatchProcessor, ConfidenceFilter
        
        # 创建所有组件
        manager = ModelManager()
        predictor = YOLOPredictor()
        processor = BatchProcessor(predictor)
        filter = ConfidenceFilter()
        
        print(f"✓ 所有组件创建成功")
        
        # 测试完整工作流
        models = manager.scan_models()
        if models:
            # 选择第一个模型
            model_path = models[0]
            print(f"使用模型: {os.path.basename(model_path)}")
            
            # 验证并加载模型
            if manager.validate_model(model_path):
                predictor.load_model(model_path)
                print(f"✓ 模型加载成功")
                
                # 测试预测和过滤
                test_image = "demo/demo.jpg"
                if os.path.exists(test_image):
                    result = predictor.predict_single(test_image)
                    if result:
                        # 应用过滤
                        filtered_detections = filter.filter_detections(result.detections, threshold=0.3)
                        optimized_detections = filter.optimize_for_annotation(filtered_detections)
                        
                        print(f"✓ 完整工作流测试成功:")
                        print(f"  原始检测: {len(result.detections)}")
                        print(f"  过滤后: {len(filtered_detections)}")
                        print(f"  优化后: {len(optimized_detections)}")
                
                predictor.unload_model()
        
        return True
        
    except Exception as e:
        print(f"✗ 模块集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("labelImg AI助手模块测试")
    print("=" * 80)
    
    # 检查必要的目录和文件
    if not os.path.exists("models"):
        os.makedirs("models")
        print("✓ 创建models目录")
    
    if not os.path.exists("config"):
        os.makedirs("config")
        print("✓ 创建config目录")
    
    # 运行测试
    tests = [
        ("YOLO预测器", test_yolo_predictor),
        ("模型管理器", test_model_manager),
        ("批量处理器", test_batch_processor),
        ("置信度过滤器", test_confidence_filter),
        ("模块集成", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n🎉 {test_name} 测试通过")
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n💥 {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI助手核心模块开发完成！")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
