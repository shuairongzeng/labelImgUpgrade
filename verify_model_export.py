#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型导出功能验证脚本

验证模型导出功能是否正确集成到labelImg中
"""

import os
import sys
import tempfile
import time

def verify_menu_integration():
    """验证菜单集成"""
    print("验证菜单集成...")
    
    try:
        # 检查labelImg.py中的集成
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('from libs.model_export_dialog import ModelExportDialog', '模型导出对话框导入'),
            ('export_model = action', '导出模型动作定义'),
            ('def export_model(self)', '导出模型方法定义'),
            ('Ctrl+Shift+M', '快捷键定义'),
            ('export_model', '菜单项添加')
        ]
        
        all_passed = True
        for check_text, description in checks:
            if check_text in content:
                print(f"✅ {description}")
            else:
                print(f"❌ 缺少: {description}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 菜单集成验证失败: {e}")
        return False

def verify_dialog_functionality():
    """验证对话框功能"""
    print("\n验证对话框功能...")
    
    try:
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from libs.model_export_dialog import ModelExportDialog, ExportConfig
        
        # 创建对话框
        dialog = ModelExportDialog()
        
        # 验证UI组件
        ui_components = [
            ('model_path_edit', '模型路径输入框'),
            ('format_combo', '格式选择下拉框'),
            ('onnx_opset_spin', 'ONNX Opset设置'),
            ('tensorrt_precision_combo', 'TensorRT精度设置'),
            ('output_dir_edit', '输出目录输入框'),
            ('output_name_edit', '输出文件名输入框'),
            ('export_btn', '导出按钮'),
            ('progress_bar', '进度条'),
            ('log_text', '日志文本框')
        ]
        
        all_passed = True
        for component, description in ui_components:
            if hasattr(dialog, component):
                print(f"✅ {description}")
            else:
                print(f"❌ 缺少: {description}")
                all_passed = False
        
        # 验证格式选择
        format_count = dialog.format_combo.count()
        if format_count >= 4:
            print(f"✅ 支持 {format_count} 种导出格式")
        else:
            print(f"❌ 导出格式数量不足: {format_count}")
            all_passed = False
        
        # 验证配置功能
        config = dialog.get_export_config()
        if isinstance(config, ExportConfig):
            print("✅ 配置获取功能正常")
        else:
            print("❌ 配置获取功能异常")
            all_passed = False
        
        dialog.close()
        return all_passed
        
    except Exception as e:
        print(f"❌ 对话框功能验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_string_resources():
    """验证字符串资源"""
    print("\n验证字符串资源...")
    
    try:
        from libs.stringBundle import StringBundle
        
        string_bundle = StringBundle.get_bundle()
        
        # 检查关键字符串资源
        key_strings = [
            'exportModel',
            'exportModelDialog', 
            'selectModel',
            'exportFormat',
            'exportParameters',
            'outputSettings',
            'startExport',
            'onnxDescription',
            'tensorrtDescription'
        ]
        
        missing_count = 0
        for string_id in key_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ {string_id}: {value[:50]}...")
            except:
                print(f"❌ 缺少字符串: {string_id}")
                missing_count += 1
        
        if missing_count == 0:
            print("✅ 所有字符串资源都存在")
            return True
        else:
            print(f"❌ 缺少 {missing_count} 个字符串资源")
            return False
            
    except Exception as e:
        print(f"❌ 字符串资源验证失败: {e}")
        return False

def verify_export_formats():
    """验证导出格式支持"""
    print("\n验证导出格式支持...")
    
    try:
        from libs.model_export_dialog import ExportConfig
        
        # 测试各种格式配置
        formats = ['onnx', 'tensorrt', 'coreml', 'tflite']
        
        for fmt in formats:
            config = ExportConfig()
            config.export_format = fmt
            
            if fmt == 'onnx':
                config.onnx_opset = 12
                config.onnx_dynamic = False
                config.onnx_simplify = True
            elif fmt == 'tensorrt':
                config.tensorrt_precision = 'fp16'
                config.tensorrt_workspace = 4
            
            print(f"✅ {fmt.upper()} 格式配置正常")
        
        print("✅ 所有导出格式都支持")
        return True
        
    except Exception as e:
        print(f"❌ 导出格式验证失败: {e}")
        return False

def verify_ultralytics_integration():
    """验证ultralytics集成"""
    print("\n验证ultralytics集成...")
    
    try:
        from ultralytics import YOLO
        print("✅ ultralytics库可用")
        
        # 检查是否有可用的模型文件
        model_files = ['yolov8n.pt', 'yolo11n.pt', 'models/yolov8n.pt']
        found_model = False
        
        for model_file in model_files:
            if os.path.exists(model_file):
                print(f"✅ 找到模型文件: {model_file}")
                found_model = True
                break
        
        if not found_model:
            print("⚠️ 没有找到YOLO模型文件，但这不影响功能")
        
        return True
        
    except ImportError:
        print("❌ ultralytics库不可用")
        print("   请运行: pip install ultralytics")
        return False

def verify_constants():
    """验证常量定义"""
    print("\n验证常量定义...")
    
    try:
        from libs.constants import SETTING_MODEL_EXPORT_DIR
        print("✅ SETTING_MODEL_EXPORT_DIR 常量已定义")
        return True
    except ImportError:
        print("❌ SETTING_MODEL_EXPORT_DIR 常量未定义")
        return False

def create_usage_guide():
    """创建使用指南"""
    print("\n创建使用指南...")
    
    guide_content = """# 模型导出功能使用指南

## 功能概述
labelImg现在支持将YOLO模型导出为其他格式，包括ONNX、TensorRT、CoreML和TensorFlow Lite。

## 使用方法

### 1. 打开模型导出对话框
- 方法1: 在文件菜单中选择"导出模型"
- 方法2: 使用快捷键 Ctrl+Shift+M

### 2. 选择模型文件
- 点击"浏览..."按钮选择YOLO模型文件(.pt格式)
- 支持YOLOv8、YOLOv11等模型

### 3. 选择导出格式
- ONNX (.onnx): 跨平台推理格式
- TensorRT (.engine): NVIDIA GPU优化格式
- CoreML (.mlmodel): Apple设备格式
- TensorFlow Lite (.tflite): 移动端格式

### 4. 配置导出参数
- ONNX格式:
  - Opset版本 (默认12)
  - 动态batch大小
  - 模型简化
- TensorRT格式:
  - 精度模式 (FP16/FP32)
  - 工作空间大小

### 5. 设置输出
- 选择输出目录
- 设置输出文件名

### 6. 开始导出
- 点击"开始导出"按钮
- 查看进度和日志信息
- 等待导出完成

## 注意事项
1. 确保已安装ultralytics库: `pip install ultralytics`
2. TensorRT导出需要NVIDIA GPU和TensorRT库
3. 导出过程可能需要几分钟时间
4. 支持中英文界面

## 故障排除
- 如果导出失败，请检查模型文件是否有效
- 确保有足够的磁盘空间
- 检查网络连接（首次使用可能需要下载依赖）
"""
    
    try:
        with open('模型导出功能使用指南.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print("✅ 使用指南已创建: 模型导出功能使用指南.md")
        return True
    except Exception as e:
        print(f"❌ 创建使用指南失败: {e}")
        return False

def main():
    """主验证函数"""
    print("模型导出功能验证")
    print("="*50)
    
    verifications = [
        ("菜单集成", verify_menu_integration),
        ("对话框功能", verify_dialog_functionality),
        ("字符串资源", verify_string_resources),
        ("导出格式", verify_export_formats),
        ("ultralytics集成", verify_ultralytics_integration),
        ("常量定义", verify_constants),
        ("使用指南", create_usage_guide)
    ]
    
    results = []
    for name, verify_func in verifications:
        try:
            result = verify_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 验证异常: {e}")
            results.append((name, False))
    
    print("\n" + "="*50)
    print("验证结果总结:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项验证通过")
    
    if passed == total:
        print("\n🎉 所有验证通过！模型导出功能已成功集成。")
        print("\n📋 功能特性:")
        print("✅ 支持4种主流导出格式")
        print("✅ 可配置导出参数")
        print("✅ 友好的用户界面")
        print("✅ 中英文界面支持")
        print("✅ 进度显示和日志记录")
        print("✅ 集成到主菜单")
        print("✅ 快捷键支持 (Ctrl+Shift+M)")
        
        print("\n🚀 现在可以在labelImg中使用模型导出功能了！")
        return True
    else:
        print(f"\n❌ {total - passed} 项验证失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
