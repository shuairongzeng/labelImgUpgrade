#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型导出功能演示脚本

演示如何使用新增的模型导出功能
"""

import os
import sys
import tempfile
from pathlib import Path

def demo_model_export_dialog():
    """演示模型导出对话框"""
    print("演示模型导出对话框...")
    
    try:
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QTimer
        except ImportError:
            from PyQt4.QtGui import QApplication
            from PyQt4.QtCore import QTimer
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建对话框
        dialog = ModelExportDialog()
        
        # 设置一些示例值
        if os.path.exists("yolov8n.pt"):
            dialog.model_path_edit.setText("yolov8n.pt")
            dialog.update_model_info("yolov8n.pt")
        elif os.path.exists("yolo11n.pt"):
            dialog.model_path_edit.setText("yolo11n.pt")
            dialog.update_model_info("yolo11n.pt")
        
        dialog.output_name_edit.setText("exported_model")
        
        print("✅ 对话框已创建并设置示例值")
        print("📋 对话框功能:")
        print("   - 模型文件选择")
        print("   - 导出格式选择 (ONNX, TensorRT, CoreML, TensorFlow Lite)")
        print("   - 参数配置 (如ONNX opset版本)")
        print("   - 输出设置")
        print("   - 进度显示")
        
        # 显示对话框（非阻塞）
        dialog.show()
        
        # 设置定时器自动关闭（演示用）
        timer = QTimer()
        timer.timeout.connect(dialog.close)
        timer.setSingleShot(True)
        timer.start(3000)  # 3秒后关闭
        
        app.processEvents()
        
        print("✅ 对话框演示完成")
        return True
        
    except Exception as e:
        print(f"❌ 对话框演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_export_config():
    """演示导出配置"""
    print("\n演示导出配置...")
    
    try:
        from libs.model_export_dialog import ExportConfig
        
        # 创建ONNX导出配置
        onnx_config = ExportConfig()
        onnx_config.model_path = "yolov8s.pt"
        onnx_config.export_format = "onnx"
        onnx_config.onnx_opset = 12
        onnx_config.onnx_dynamic = False
        onnx_config.onnx_simplify = True
        onnx_config.image_size = 640
        onnx_config.output_dir = "exports"
        onnx_config.output_name = "yolov8s_onnx"
        
        print("✅ ONNX导出配置:")
        print(f"   模型: {onnx_config.model_path}")
        print(f"   格式: {onnx_config.export_format}")
        print(f"   Opset: {onnx_config.onnx_opset}")
        print(f"   动态batch: {onnx_config.onnx_dynamic}")
        print(f"   简化模型: {onnx_config.onnx_simplify}")
        print(f"   图像尺寸: {onnx_config.image_size}")
        
        # 创建TensorRT导出配置
        tensorrt_config = ExportConfig()
        tensorrt_config.model_path = "yolov8s.pt"
        tensorrt_config.export_format = "tensorrt"
        tensorrt_config.tensorrt_precision = "fp16"
        tensorrt_config.tensorrt_workspace = 4
        tensorrt_config.image_size = 640
        tensorrt_config.device = "cuda:0"
        tensorrt_config.output_dir = "exports"
        tensorrt_config.output_name = "yolov8s_tensorrt"
        
        print("\n✅ TensorRT导出配置:")
        print(f"   模型: {tensorrt_config.model_path}")
        print(f"   格式: {tensorrt_config.export_format}")
        print(f"   精度: {tensorrt_config.tensorrt_precision}")
        print(f"   工作空间: {tensorrt_config.tensorrt_workspace} GB")
        print(f"   设备: {tensorrt_config.device}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导出配置演示失败: {e}")
        return False

def demo_menu_integration():
    """演示菜单集成"""
    print("\n演示菜单集成...")
    
    try:
        print("📋 菜单集成说明:")
        print("1. 在labelImg主界面的'文件'菜单中添加了'导出模型'选项")
        print("2. 快捷键: Ctrl+Shift+M")
        print("3. 点击后会打开模型导出对话框")
        print("4. 支持中英文界面切换")
        
        # 检查菜单集成
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'export_model' in content and 'ModelExportDialog' in content:
            print("✅ 菜单集成已完成")
            return True
        else:
            print("❌ 菜单集成不完整")
            return False
            
    except Exception as e:
        print(f"❌ 菜单集成演示失败: {e}")
        return False

def demo_supported_formats():
    """演示支持的导出格式"""
    print("\n演示支持的导出格式...")
    
    formats = [
        {
            "name": "ONNX",
            "extension": ".onnx",
            "description": "跨平台推理格式，支持多种推理引擎",
            "parameters": ["opset版本", "动态batch", "模型简化"]
        },
        {
            "name": "TensorRT",
            "extension": ".engine",
            "description": "NVIDIA GPU优化格式，高性能推理",
            "parameters": ["精度模式(FP16/FP32)", "工作空间大小"]
        },
        {
            "name": "CoreML",
            "extension": ".mlmodel",
            "description": "Apple设备专用格式，iOS/macOS应用",
            "parameters": ["默认设置"]
        },
        {
            "name": "TensorFlow Lite",
            "extension": ".tflite",
            "description": "移动端和嵌入式设备格式",
            "parameters": ["默认设置"]
        }
    ]
    
    print("✅ 支持的导出格式:")
    for i, fmt in enumerate(formats, 1):
        print(f"\n{i}. {fmt['name']} ({fmt['extension']})")
        print(f"   描述: {fmt['description']}")
        print(f"   可配置参数: {', '.join(fmt['parameters'])}")
    
    return True

def demo_usage_workflow():
    """演示使用流程"""
    print("\n演示使用流程...")
    
    workflow = [
        "1. 启动labelImg应用程序",
        "2. 在文件菜单中选择'导出模型'或按Ctrl+Shift+M",
        "3. 在对话框中选择要导出的YOLO模型文件(.pt)",
        "4. 选择目标导出格式(ONNX/TensorRT/CoreML/TensorFlow Lite)",
        "5. 配置格式特定参数(如ONNX的opset版本)",
        "6. 设置输出目录和文件名",
        "7. 点击'开始导出'按钮",
        "8. 等待导出完成，查看进度和日志",
        "9. 导出完成后，在指定目录找到转换后的模型文件"
    ]
    
    print("✅ 使用流程:")
    for step in workflow:
        print(f"   {step}")
    
    print("\n💡 使用提示:")
    print("   - 确保已安装ultralytics库: pip install ultralytics")
    print("   - ONNX导出推荐opset版本12（默认值）")
    print("   - TensorRT导出需要NVIDIA GPU和TensorRT库")
    print("   - 导出过程可能需要几分钟，请耐心等待")
    
    return True

def main():
    """主演示函数"""
    print("模型导出功能演示")
    print("="*50)
    
    demos = [
        ("导出配置", demo_export_config),
        ("支持格式", demo_supported_formats),
        ("菜单集成", demo_menu_integration),
        ("使用流程", demo_usage_workflow),
        ("对话框演示", demo_model_export_dialog)
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            result = demo_func()
            if not result:
                print(f"❌ {demo_name} 演示失败")
        except Exception as e:
            print(f"❌ {demo_name} 演示异常: {e}")
    
    print("\n" + "="*50)
    print("🎉 模型导出功能演示完成！")
    print("\n📋 功能总结:")
    print("✅ 支持4种主流导出格式")
    print("✅ 可配置导出参数")
    print("✅ 友好的用户界面")
    print("✅ 中英文界面支持")
    print("✅ 进度显示和日志记录")
    print("✅ 集成到主菜单")
    
    print("\n🚀 现在可以在labelImg中使用模型导出功能了！")

if __name__ == "__main__":
    main()
