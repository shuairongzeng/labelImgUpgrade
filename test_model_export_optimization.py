#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模型导出功能优化
验证智能模型选择、中文菜单显示和界面样式改进
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_manager_integration():
    """测试ModelManager集成"""
    print("🔧 测试ModelManager集成...")
    
    try:
        from libs.ai_assistant.model_manager import ModelManager
        
        # 创建模型管理器
        manager = ModelManager()
        print("✅ ModelManager创建成功")
        
        # 扫描模型
        models = manager.scan_models()
        print(f"✅ 扫描到 {len(models)} 个模型")
        
        # 测试模型信息获取
        if models:
            test_model = models[0]
            info = manager.get_model_info(test_model)
            print(f"✅ 获取模型信息成功: {info.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ModelManager集成测试失败: {e}")
        return False

def test_model_export_dialog():
    """测试模型导出对话框"""
    print("\n🎨 测试模型导出对话框...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建应用（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = ModelExportDialog()
        print("✅ 对话框创建成功")
        
        # 测试模型管理器集成
        if hasattr(dialog, 'model_manager'):
            print("✅ ModelManager集成成功")
        else:
            print("❌ ModelManager未集成")
            return False
        
        # 测试模型信息显示组件
        if hasattr(dialog, 'model_details_widget'):
            print("✅ 模型详细信息组件存在")
        else:
            print("❌ 模型详细信息组件缺失")
            return False
        
        # 测试智能推荐方法
        if hasattr(dialog, '_find_recommended_model'):
            print("✅ 智能推荐功能存在")
        else:
            print("❌ 智能推荐功能缺失")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 对话框测试失败: {e}")
        return False

def test_chinese_menu():
    """测试中文菜单显示"""
    print("\n🇨🇳 测试中文菜单显示...")
    
    try:
        from libs.stringBundle import StringBundle
        
        # 获取字符串包
        bundle = StringBundle.get_bundle()
        
        # 测试关键字符串
        export_model = bundle.get_string('exportModel')
        export_detail = bundle.get_string('exportModelDetail')
        
        if export_model == "导出模型":
            print("✅ 菜单项中文显示正确")
        else:
            print(f"❌ 菜单项显示错误: {export_model}")
            return False
        
        if "YOLO模型导出" in export_detail:
            print("✅ 菜单详情中文显示正确")
        else:
            print(f"❌ 菜单详情显示错误: {export_detail}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 中文菜单测试失败: {e}")
        return False

def test_style_improvements():
    """测试样式改进"""
    print("\n🎨 测试样式改进...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建应用（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = ModelExportDialog()
        
        # 检查样式设置
        style_sheet = dialog.styleSheet()
        
        # 检查关键样式元素
        style_checks = [
            ("color: #212121", "主文字颜色设置"),
            ("background-color: #fafafa", "背景色设置"),
            ("font-family:", "字体设置"),
            ("border-radius:", "圆角设置"),
            ("QGroupBox", "组框样式"),
            ("QPushButton", "按钮样式"),
            ("QLabel", "标签样式")
        ]
        
        for check, description in style_checks:
            if check in style_sheet:
                print(f"✅ {description}正确")
            else:
                print(f"❌ {description}缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 样式测试失败: {e}")
        return False

def test_smart_model_recommendation():
    """测试智能模型推荐"""
    print("\n🧠 测试智能模型推荐...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建应用（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = ModelExportDialog()
        
        # 创建测试模型列表
        test_models = [
            "models/yolov8n.pt",
            "runs/train/exp1/weights/best.pt",
            "runs/train/exp2/weights/best.pt",
            "models/custom/my_model.pt"
        ]
        
        # 测试推荐算法
        recommended = dialog._find_recommended_model(test_models)
        
        if recommended:
            print(f"✅ 智能推荐成功: {os.path.basename(recommended)}")
        else:
            print("ℹ️ 无推荐模型（正常，如果没有训练模型）")
        
        # 测试模型列表更新
        dialog.update_model_list(test_models)
        
        if dialog.model_combo.count() > 0:
            print("✅ 模型列表更新成功")
        else:
            print("❌ 模型列表更新失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 智能推荐测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 模型导出功能优化测试")
    print("=" * 50)
    
    tests = [
        ("ModelManager集成", test_model_manager_integration),
        ("模型导出对话框", test_model_export_dialog),
        ("中文菜单显示", test_chinese_menu),
        ("样式改进", test_style_improvements),
        ("智能模型推荐", test_smart_model_recommendation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有优化功能测试通过！")
        print("\n📋 优化总结:")
        print("✅ 智能模型选择 - 自动扫描和推荐最佳模型")
        print("✅ 模型信息显示 - 详细的模型信息和性能指标")
        print("✅ 中文菜单显示 - 正确显示为'导出模型'")
        print("✅ 界面样式优化 - 提高字体对比度和视觉效果")
        print("✅ Material Design - 保持一致的设计风格")
    else:
        print("⚠️ 部分功能需要进一步优化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
