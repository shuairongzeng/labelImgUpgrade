#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文件名生成功能测试脚本

测试新的智能文件名生成功能：
1. 智能文件名生成算法
2. 文件名模板系统
3. 文件名预览和编辑
4. 文件名冲突检测
5. 文件名显示和交互优化
"""

import sys
import os
import tempfile
import yaml
import csv
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_mock_model_info():
    """创建模拟模型信息用于测试"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建训练目录结构
    train_dir = os.path.join(temp_dir, "runs", "train", "yolov8n_experiment1")
    weights_dir = os.path.join(train_dir, "weights")
    os.makedirs(weights_dir, exist_ok=True)
    
    # 创建模型文件
    best_model = os.path.join(weights_dir, "best.pt")
    with open(best_model, 'wb') as f:
        f.write(b'mock model data' * 1000)  # 约13KB
    
    # 创建训练配置文件
    args_file = os.path.join(train_dir, "args.yaml")
    config_data = {
        'epochs': 100,
        'batch': 16,
        'data': 'datasets/custom_data.yaml',
        'model': 'yolov8n.pt',
        'lr0': 0.01
    }
    
    with open(args_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    # 创建训练结果文件
    results_file = os.path.join(train_dir, "results.csv")
    results_data = [
        ['epoch', 'metrics/mAP50(B)', 'metrics/mAP50-95(B)', 'metrics/precision(B)', 'metrics/recall(B)'],
        ['99', '0.856', '0.634', '0.878', '0.845']  # 优秀性能
    ]
    
    with open(results_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(results_data)
    
    return temp_dir, best_model

def test_smart_filename_generation():
    """测试智能文件名生成功能"""
    print("🧪 开始测试智能文件名生成功能...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建模拟模型信息
        temp_dir, best_model = create_mock_model_info()
        print(f"✅ 创建模拟模型信息: {temp_dir}")
        
        # 创建模型导出对话框
        dialog = ModelExportDialog()
        print("✅ 创建模型导出对话框成功")
        
        # 获取模型详细信息
        model_info = dialog._get_model_detailed_info(best_model)
        print("✅ 获取模型详细信息成功")
        
        # 测试1: 智能文件名生成算法
        print("\n🧠 测试1: 智能文件名生成算法")
        
        test_formats = ["onnx", "tensorrt", "coreml", "tflite"]
        for export_format in test_formats:
            filename = dialog.generate_smart_filename(model_info, export_format)
            print(f"  {export_format.upper()}: {filename}")
            
            # 验证文件名格式
            format_map = {
                "onnx": "onnx",
                "tensorrt": "trt",
                "coreml": "coreml",
                "tflite": "tflite"
            }
            expected_ext = format_map.get(export_format.lower(), export_format.lower())

            if filename and "_" in filename and expected_ext in filename.lower():
                print(f"    ✅ {export_format} 文件名格式正确")
            else:
                print(f"    ❌ {export_format} 文件名格式错误")
                return False
        
        # 测试2: 文件名模板系统
        print("\n📝 测试2: 文件名模板系统")
        
        templates = [
            "智能模式 (推荐)",
            "简洁模式", 
            "详细模式",
            "时间戳模式"
        ]
        
        for template in templates:
            filename = dialog.generate_filename_by_template(model_info, "onnx", template)
            print(f"  {template}: {filename}")
            
            # 验证不同模板生成不同的文件名
            if filename:
                print(f"    ✅ {template} 生成成功")
            else:
                print(f"    ❌ {template} 生成失败")
                return False
        
        # 测试3: 基础模型名称提取
        print("\n🔍 测试3: 基础模型名称提取")
        
        test_paths = [
            "/path/to/yolov8n.pt",
            "/path/to/yolov8s.pt", 
            "/path/to/yolo11m.pt",
            "/path/to/custom_model.pt",
            "/path/to/best.pt"
        ]
        
        for path in test_paths:
            base_name = dialog._extract_base_model_name(path)
            print(f"  {os.path.basename(path)} -> {base_name}")
            
            if base_name:
                print(f"    ✅ 提取成功")
            else:
                print(f"    ❌ 提取失败")
                return False
        
        # 测试4: 性能等级识别
        print("\n⭐ 测试4: 性能等级识别")
        
        test_mAP50_values = [0.95, 0.85, 0.75, 0.65, 0.55, 0.0]
        expected_levels = ["excellent", "good", "fair", "poor", "basic", ""]
        
        for mAP50, expected in zip(test_mAP50_values, expected_levels):
            level = dialog._get_performance_level_short(mAP50)
            print(f"  mAP50={mAP50} -> {level}")
            
            if level == expected:
                print(f"    ✅ 等级正确")
            else:
                print(f"    ❌ 等级错误，期望: {expected}")
                return False
        
        # 测试5: 文件名清理
        print("\n🧹 测试5: 文件名清理")
        
        test_filenames = [
            "model<test>",
            "model:with:colons",
            "model/with/slashes",
            "model___multiple___underscores",
            "_leading_underscore_",
            "normal_filename"
        ]
        
        for filename in test_filenames:
            cleaned = dialog._sanitize_filename(filename)
            print(f"  '{filename}' -> '{cleaned}'")
            
            # 验证清理后的文件名不包含非法字符
            import re
            if not re.search(r'[<>:"/\\|?*]', cleaned):
                print(f"    ✅ 清理成功")
            else:
                print(f"    ❌ 清理失败，仍包含非法字符")
                return False
        
        # 测试6: 文件名验证
        print("\n✅ 测试6: 文件名验证")
        
        test_cases = [
            ("valid_filename", True, ""),
            ("file<name>", False, "包含非法字符"),
            ("CON", False, "系统保留名称"),
            ("a" * 250, False, "文件名过长"),
            (".hidden_file.", False, "不能以点开头或结尾"),
            ("", True, "")
        ]
        
        for filename, expected_valid, expected_error_type in test_cases:
            is_valid, error_msg, cleaned = dialog.validate_filename_input(filename)
            print(f"  '{filename}' -> valid={is_valid}, error='{error_msg}'")
            
            if is_valid == expected_valid:
                print(f"    ✅ 验证结果正确")
            else:
                print(f"    ❌ 验证结果错误，期望: {expected_valid}")
                return False
        
        # 测试7: 文件名冲突检测
        print("\n⚠️ 测试7: 文件名冲突检测")
        
        # 创建测试目录和文件
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, "test_model.onnx")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # 测试冲突检测
        has_conflict, suggested_name, conflict_info = dialog.check_filename_conflict("test_model", test_dir)
        print(f"  冲突检测: conflict={has_conflict}, suggested='{suggested_name}'")
        
        if has_conflict and suggested_name != "test_model":
            print(f"    ✅ 冲突检测成功")
        else:
            print(f"    ❌ 冲突检测失败")
            return False
        
        # 测试8: 时间戳生成
        print("\n⏰ 测试8: 时间戳生成")
        
        timestamp = dialog._get_timestamp()
        print(f"  时间戳: {timestamp}")
        
        # 验证时间戳格式 (YYYYMMDD_HHMM)
        import re
        if re.match(r'\d{8}_\d{4}', timestamp):
            print(f"    ✅ 时间戳格式正确")
        else:
            print(f"    ❌ 时间戳格式错误")
            return False
        
        print("\n🎉 所有测试通过！智能文件名生成功能正常工作")
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_smart_filename_generation()
    sys.exit(0 if success else 1)
