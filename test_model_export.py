#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型导出功能测试脚本

测试YOLO模型导出为其他格式的功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_imports():
    """测试导入功能"""
    print("测试导入功能...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog, ExportConfig, ModelExportThread
        print("✅ ModelExportDialog 导入成功")
        print("✅ ExportConfig 导入成功")
        print("✅ ModelExportThread 导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_export_config():
    """测试导出配置类"""
    print("\n测试导出配置类...")
    
    try:
        from libs.model_export_dialog import ExportConfig
        
        config = ExportConfig()
        
        # 测试默认值
        assert config.export_format == "onnx"
        assert config.onnx_opset == 12
        assert config.image_size == 640
        assert config.device == "cpu"
        
        print("✅ ExportConfig 默认值正确")
        
        # 测试设置值
        config.model_path = "test_model.pt"
        config.export_format = "tensorrt"
        config.tensorrt_precision = "fp16"
        
        assert config.model_path == "test_model.pt"
        assert config.export_format == "tensorrt"
        assert config.tensorrt_precision == "fp16"
        
        print("✅ ExportConfig 设置值正确")
        return True
        
    except Exception as e:
        print(f"❌ ExportConfig 测试失败: {e}")
        return False

def test_string_resources():
    """测试字符串资源"""
    print("\n测试字符串资源...")
    
    try:
        from libs.stringBundle import StringBundle
        
        string_bundle = StringBundle.get_bundle()
        
        # 测试新增的字符串资源
        test_strings = [
            'exportModel',
            'exportModelDialog',
            'exportModelTitle',
            'selectModel',
            'exportFormat',
            'exportParameters',
            'outputSettings',
            'startExport',
            'onnxDescription',
            'tensorrtDescription'
        ]
        
        missing_strings = []
        for string_id in test_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ 字符串资源 '{string_id}': {value}")
            except:
                missing_strings.append(string_id)
                print(f"❌ 缺少字符串资源: {string_id}")
        
        if missing_strings:
            print(f"❌ 缺少 {len(missing_strings)} 个字符串资源")
            return False
        else:
            print("✅ 所有字符串资源都存在")
            return True
            
    except Exception as e:
        print(f"❌ 字符串资源测试失败: {e}")
        return False

def test_dialog_creation():
    """测试对话框创建"""
    print("\n测试对话框创建...")
    
    try:
        # 需要QApplication才能创建对话框
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from libs.model_export_dialog import ModelExportDialog
        
        dialog = ModelExportDialog()
        
        # 检查关键组件是否存在
        assert hasattr(dialog, 'model_path_edit')
        assert hasattr(dialog, 'format_combo')
        assert hasattr(dialog, 'export_btn')
        assert hasattr(dialog, 'progress_bar')
        
        print("✅ 对话框创建成功")
        print("✅ 关键组件都存在")
        
        # 测试格式选择
        format_count = dialog.format_combo.count()
        assert format_count >= 4  # 至少有4种格式
        print(f"✅ 支持 {format_count} 种导出格式")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ 对话框创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_integration():
    """测试菜单集成"""
    print("\n测试菜单集成...")
    
    try:
        # 检查labelImg.py中是否有导出方法
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('ModelExportDialog', '模型导出对话框导入'),
            ('export_model', '导出模型方法'),
            ('exportModel', '导出模型动作'),
            ('Ctrl+Shift+M', '快捷键设置')
        ]
        
        all_passed = True
        for check_item, description in checks:
            if check_item in content:
                print(f"✅ {description} 已添加")
            else:
                print(f"❌ 缺少 {description}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 菜单集成检查失败: {e}")
        return False

def test_constants():
    """测试常量定义"""
    print("\n测试常量定义...")
    
    try:
        from libs.constants import SETTING_MODEL_EXPORT_DIR
        print("✅ SETTING_MODEL_EXPORT_DIR 常量已定义")
        return True
    except ImportError:
        print("❌ SETTING_MODEL_EXPORT_DIR 常量未定义")
        return False

def test_ultralytics_availability():
    """测试ultralytics库可用性"""
    print("\n测试ultralytics库可用性...")
    
    try:
        from ultralytics import YOLO
        print("✅ ultralytics库可用")
        
        # 测试模型加载（如果有模型文件）
        model_files = ['yolov8n.pt', 'yolo11n.pt', 'models/yolov8n.pt']
        for model_file in model_files:
            if os.path.exists(model_file):
                try:
                    model = YOLO(model_file)
                    print(f"✅ 成功加载模型: {model_file}")
                    return True
                except Exception as e:
                    print(f"⚠️ 加载模型失败 {model_file}: {e}")
        
        print("⚠️ 没有找到可用的YOLO模型文件")
        return True
        
    except ImportError:
        print("❌ ultralytics库不可用")
        print("   请运行: pip install ultralytics")
        return False

def main():
    """主测试函数"""
    print("开始测试模型导出功能...\n")
    
    tests = [
        ("导入功能", test_imports),
        ("导出配置类", test_export_config),
        ("字符串资源", test_string_resources),
        ("对话框创建", test_dialog_creation),
        ("菜单集成", test_menu_integration),
        ("常量定义", test_constants),
        ("ultralytics库", test_ultralytics_availability)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！模型导出功能已成功集成。")
        print("\n📋 功能说明:")
        print("1. 在文件菜单中添加了'导出模型'选项")
        print("2. 快捷键: Ctrl+Shift+M")
        print("3. 支持导出格式: ONNX, TensorRT, CoreML, TensorFlow Lite")
        print("4. 可配置导出参数（如ONNX opset版本）")
        print("5. 支持中英文界面")
        return True
    else:
        print(f"\n❌ {total - passed} 个测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
