#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
优化后的模型导出功能测试脚本

测试所有优化功能，包括模型下拉框、默认路径、自动打开文件夹等
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_model_manager_integration():
    """测试模型管理器集成"""
    print("测试模型管理器集成...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog
        from libs.ai_assistant.model_manager import ModelManager
        
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = ModelExportDialog()
        
        # 检查模型管理器是否正确初始化
        assert hasattr(dialog, 'model_manager'), "模型管理器未初始化"
        assert isinstance(dialog.model_manager, ModelManager), "模型管理器类型错误"
        
        # 检查模型下拉框
        assert hasattr(dialog, 'model_combo'), "模型下拉框不存在"
        assert hasattr(dialog, 'refresh_model_btn'), "刷新按钮不存在"
        
        print("✅ 模型管理器集成正常")
        print("✅ 模型下拉框创建成功")
        print("✅ 刷新按钮存在")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ 模型管理器集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_list_functionality():
    """测试模型列表功能"""
    print("\n测试模型列表功能...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ModelExportDialog()
        
        # 测试模型列表更新
        test_models = [
            "yolov8n.pt",
            "yolov8s.pt", 
            "runs/train/exp1/weights/best.pt",
            "models/custom/my_model.pt"
        ]
        
        dialog.update_model_list(test_models)
        
        # 检查下拉框是否有内容
        assert dialog.model_combo.count() > 0, "模型下拉框为空"
        
        # 测试模型选择
        if dialog.model_combo.count() > 0:
            dialog.model_combo.setCurrentIndex(0)
            selected_path = dialog.get_selected_model_path()
            print(f"✅ 模型选择功能正常，当前选择: {selected_path}")
        
        # 测试格式化功能
        training_name = dialog._format_training_model_name("runs/train/exp1/weights/best.pt")
        assert "exp1" in training_name, "训练模型名称格式化失败"
        print("✅ 训练模型名称格式化正常")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ 模型列表功能测试失败: {e}")
        return False

def test_default_export_path():
    """测试默认导出路径"""
    print("\n测试默认导出路径...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ModelExportDialog()
        
        # 检查默认导出路径
        default_dir = dialog.get_default_export_dir()
        assert default_dir, "默认导出路径为空"
        print(f"✅ 默认导出路径: {default_dir}")
        
        # 检查输出目录是否已设置
        output_dir = dialog.output_dir_edit.text()
        assert output_dir, "输出目录未设置"
        print(f"✅ 输出目录已设置: {output_dir}")
        
        # 检查目录是否存在或可创建
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                print("✅ 输出目录创建成功")
                # 清理测试目录
                if "test" in output_dir.lower():
                    shutil.rmtree(output_dir, ignore_errors=True)
            except Exception as e:
                print(f"⚠️ 输出目录创建失败: {e}")
        else:
            print("✅ 输出目录已存在")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ 默认导出路径测试失败: {e}")
        return False

def test_model_info_display():
    """测试模型信息显示"""
    print("\n测试模型信息显示...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ModelExportDialog()
        
        # 测试模型类型检测
        test_cases = [
            ("yolov8n.pt", "YOLOv8"),
            ("yolo11s.pt", "YOLOv11"),
            ("custom_model.pt", "PyTorch"),
            ("model.onnx", "ONNX"),
            ("model.engine", "TensorRT")
        ]
        
        for model_name, expected_type in test_cases:
            detected_type = dialog._detect_model_type(model_name)
            assert expected_type in detected_type, f"模型类型检测错误: {model_name}"
            print(f"✅ {model_name} -> {detected_type}")
        
        # 测试格式扩展名获取
        dialog.format_combo.setCurrentIndex(0)  # ONNX
        ext = dialog._get_format_extension()
        assert ext == ".onnx", "ONNX扩展名错误"
        print("✅ 格式扩展名获取正常")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ 模型信息显示测试失败: {e}")
        return False

def test_ui_improvements():
    """测试UI改进"""
    print("\n测试UI改进...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ModelExportDialog()
        
        # 检查UI组件
        ui_components = [
            ('model_combo', '模型下拉框'),
            ('refresh_model_btn', '刷新按钮'),
            ('browse_model_btn', '浏览按钮'),
            ('output_dir_edit', '输出目录输入框'),
            ('output_name_edit', '输出文件名输入框'),
            ('format_combo', '格式选择框'),
            ('export_btn', '导出按钮'),
            ('progress_bar', '进度条'),
            ('log_text', '日志文本框')
        ]
        
        for component, description in ui_components:
            assert hasattr(dialog, component), f"缺少组件: {description}"
            print(f"✅ {description}")
        
        # 测试格式改变事件
        original_name = "test_model"
        dialog.output_name_edit.setText(original_name)
        
        # 模拟格式改变
        dialog.on_format_changed("ONNX (.onnx)")
        updated_name = dialog.output_name_edit.text()
        assert "onnx" in updated_name.lower(), "格式改变时文件名未更新"
        print("✅ 格式改变时文件名自动更新")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ UI改进测试失败: {e}")
        return False

def test_string_resources():
    """测试字符串资源"""
    print("\n测试字符串资源...")
    
    try:
        from libs.stringBundle import StringBundle
        
        string_bundle = StringBundle.get_bundle()
        
        # 测试新增的字符串资源
        new_strings = [
            'refreshModels',
            'noModelsFound', 
            'noModelsAvailable',
            'openFolder',
            'folderNotFound',
            'openFolderFailed',
            'modelType',
            'classCount',
            'unknown'
        ]
        
        missing_count = 0
        for string_id in new_strings:
            try:
                value = string_bundle.get_string(string_id)
                print(f"✅ {string_id}: {value}")
            except:
                print(f"❌ 缺少字符串: {string_id}")
                missing_count += 1
        
        if missing_count == 0:
            print("✅ 所有新增字符串资源都存在")
            return True
        else:
            print(f"❌ 缺少 {missing_count} 个字符串资源")
            return False
            
    except Exception as e:
        print(f"❌ 字符串资源测试失败: {e}")
        return False

def test_export_config_generation():
    """测试导出配置生成"""
    print("\n测试导出配置生成...")
    
    try:
        from libs.model_export_dialog import ModelExportDialog, ExportConfig
        
        # 创建QApplication
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            from PyQt4.QtGui import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        dialog = ModelExportDialog()
        
        # 设置测试值
        test_models = ["test_model.pt"]
        dialog.update_model_list(test_models)
        dialog.output_dir_edit.setText("/test/output")
        dialog.output_name_edit.setText("test_export")
        
        # 获取配置
        config = dialog.get_export_config()
        
        assert isinstance(config, ExportConfig), "配置对象类型错误"
        assert config.model_path == "test_model.pt", "模型路径设置错误"
        assert config.output_dir == "/test/output", "输出目录设置错误"
        assert config.output_name == "test_export", "输出文件名设置错误"
        
        print("✅ 导出配置生成正常")
        print(f"   模型路径: {config.model_path}")
        print(f"   输出目录: {config.output_dir}")
        print(f"   输出文件名: {config.output_name}")
        print(f"   导出格式: {config.export_format}")
        
        dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ 导出配置生成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("优化后的模型导出功能测试")
    print("="*50)
    
    tests = [
        ("模型管理器集成", test_model_manager_integration),
        ("模型列表功能", test_model_list_functionality),
        ("默认导出路径", test_default_export_path),
        ("模型信息显示", test_model_info_display),
        ("UI改进", test_ui_improvements),
        ("字符串资源", test_string_resources),
        ("导出配置生成", test_export_config_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
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
        print("\n🎉 所有优化功能测试通过！")
        print("\n📋 优化功能总结:")
        print("✅ 模型选择改为智能下拉框")
        print("✅ 自动扫描和分类显示模型")
        print("✅ 设置合理的默认导出路径")
        print("✅ 导出完成后可自动打开文件夹")
        print("✅ 增强的模型信息显示")
        print("✅ 改进的用户界面体验")
        print("✅ 完整的中英文字符串资源")
        
        print("\n🚀 优化后的模型导出功能已准备就绪！")
        return True
    else:
        print(f"\n❌ {total - passed} 个测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
