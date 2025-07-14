#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证修复功能的实际测试
"""
import os
import sys
import tempfile

def test_yolo_export_dialog_memory():
    """测试YOLO导出对话框的目录记忆功能"""
    print("测试YOLO导出对话框的目录记忆功能...")
    
    try:
        # 添加libs目录到路径
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
        
        from libs.yolo_export_dialog import YOLOExportDialog
        from libs.settings import Settings
        from libs.constants import SETTING_YOLO_EXPORT_DIR
        
        # 创建临时目录用于测试
        test_dir = tempfile.mkdtemp()
        print(f"创建测试目录: {test_dir}")
        
        # 创建一个模拟的父窗口类
        class MockParent:
            def __init__(self):
                pass
        
        # 测试1: 创建对话框实例
        parent = MockParent()
        dialog = YOLOExportDialog(parent, test_dir)
        print("✅ YOLOExportDialog实例创建成功")
        
        # 测试2: 检查设置对象是否正确初始化
        if hasattr(dialog, 'settings') and dialog.settings is not None:
            print("✅ Settings对象正确初始化")
        else:
            print("❌ Settings对象初始化失败")
            return False
            
        # 测试3: 检查方法是否存在
        if hasattr(dialog, 'load_last_export_dir'):
            print("✅ load_last_export_dir方法存在")
        else:
            print("❌ load_last_export_dir方法不存在")
            return False
            
        if hasattr(dialog, 'save_export_dir'):
            print("✅ save_export_dir方法存在")
        else:
            print("❌ save_export_dir方法不存在")
            return False
            
        # 测试4: 测试保存和加载功能
        test_export_dir = os.path.join(test_dir, "export_test")
        os.makedirs(test_export_dir, exist_ok=True)
        
        # 保存目录
        dialog.save_export_dir(test_export_dir)
        print(f"✅ 保存测试目录: {test_export_dir}")
        
        # 验证设置是否保存
        saved_dir = dialog.settings.get(SETTING_YOLO_EXPORT_DIR)
        if saved_dir == test_export_dir:
            print("✅ 目录保存到设置成功")
        else:
            print(f"❌ 目录保存失败，期望: {test_export_dir}, 实际: {saved_dir}")
            return False
            
        # 测试5: 创建新的对话框实例，验证是否能加载上次的目录
        dialog2 = YOLOExportDialog(parent, test_dir)
        loaded_dir = dialog2.target_edit.text()
        if loaded_dir == test_export_dir:
            print("✅ 上次目录加载成功")
        else:
            print(f"❌ 上次目录加载失败，期望: {test_export_dir}, 实际: {loaded_dir}")
            return False
            
        # 清理测试目录
        import shutil
        shutil.rmtree(test_dir)
        print("✅ 测试目录清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dock_features_fix():
    """测试专家模式dock_features修复（不启动GUI）"""
    print("\n测试专家模式dock_features修复...")
    
    try:
        # 检查代码修复
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查self.dock_features定义
        if 'self.dock_features = QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable' in content:
            print("✅ self.dock_features正确定义")
        else:
            print("❌ self.dock_features定义有问题")
            return False
            
        # 检查toggle_advanced_mode方法中的使用
        if 'self.dock.setFeatures(self.dock.features() | self.dock_features)' in content:
            print("✅ toggle_advanced_mode方法正确使用self.dock_features")
        else:
            print("❌ toggle_advanced_mode方法使用有问题")
            return False
            
        print("✅ 专家模式dock_features修复验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始验证修复功能...\n")
    
    # 测试专家模式修复
    test1_result = test_dock_features_fix()
    
    # 测试YOLO导出记忆功能
    test2_result = test_yolo_export_dialog_memory()
    
    print("\n" + "="*60)
    print("验证结果总结:")
    print(f"专家模式dock_features修复: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"YOLO导出目录记忆功能: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if all([test1_result, test2_result]):
        print("\n🎉 所有功能验证通过！")
        print("\n📋 修复总结:")
        print("1. 修复了专家模式菜单点击时的AttributeError错误")
        print("   - 将dock_features改为实例变量self.dock_features")
        print("2. 添加了YOLO导出目标目录记忆功能")
        print("   - 新增SETTING_YOLO_EXPORT_DIR常量")
        print("   - 在YOLOExportDialog中集成Settings")
        print("   - 自动保存和加载上次选择的目标目录")
        print("\n✨ 现在可以正常使用这些功能了！")
        return True
    else:
        print("\n❌ 部分功能验证失败，请检查修复。")
        return False

if __name__ == "__main__":
    main()
