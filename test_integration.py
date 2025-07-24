#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
labelImg 集成功能测试脚本

测试AI助手、批量操作、快捷键管理等新功能的集成情况
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    
    try:
        # 测试AI助手模块导入
        from libs.ai_assistant_panel import AIAssistantPanel
        from libs.ai_assistant import YOLOPredictor, ModelManager, BatchProcessor, ConfidenceFilter
        print("✅ AI助手模块导入成功")
    except Exception as e:
        print(f"❌ AI助手模块导入失败: {str(e)}")
        traceback.print_exc()
    
    try:
        # 测试批量操作模块导入
        from libs.batch_operations import BatchOperations, BatchOperationsDialog
        print("✅ 批量操作模块导入成功")
    except Exception as e:
        print(f"❌ 批量操作模块导入失败: {str(e)}")
        traceback.print_exc()
    
    try:
        # 测试快捷键管理模块导入
        from libs.shortcut_manager import ShortcutManager, ShortcutConfigDialog
        print("✅ 快捷键管理模块导入成功")
    except Exception as e:
        print(f"❌ 快捷键管理模块导入失败: {str(e)}")
        traceback.print_exc()
    
    try:
        # 测试主界面导入
        import labelImg
        print("✅ 主界面模块导入成功")
    except Exception as e:
        print(f"❌ 主界面模块导入失败: {str(e)}")
        traceback.print_exc()

def test_main_window_creation():
    """测试主窗口创建"""
    print("=" * 50)
    print("测试主窗口创建...")
    
    try:
        import labelImg
        app, win = labelImg.get_main_app([])
        
        # 检查AI助手面板
        if hasattr(win, 'ai_assistant_panel'):
            print("✅ AI助手面板创建成功")
        else:
            print("❌ AI助手面板未创建")
        
        # 检查AI助手停靠窗口
        if hasattr(win, 'ai_dock'):
            print("✅ AI助手停靠窗口创建成功")
        else:
            print("❌ AI助手停靠窗口未创建")
        
        # 检查批量操作管理器
        if hasattr(win, 'batch_operations'):
            print("✅ 批量操作管理器创建成功")
        else:
            print("❌ 批量操作管理器未创建")
        
        # 检查快捷键管理器
        if hasattr(win, 'shortcut_manager'):
            print("✅ 快捷键管理器创建成功")
        else:
            print("❌ 快捷键管理器未创建")
        
        # 检查新菜单
        if hasattr(win.menus, 'tools'):
            print("✅ 工具菜单创建成功")
        else:
            print("❌ 工具菜单未创建")
        
        # 检查新动作
        if hasattr(win.actions, 'aiPredictCurrent'):
            print("✅ AI预测动作创建成功")
        else:
            print("❌ AI预测动作未创建")
        
        if hasattr(win.actions, 'batchOperations'):
            print("✅ 批量操作动作创建成功")
        else:
            print("❌ 批量操作动作未创建")
        
        if hasattr(win.actions, 'shortcutConfig'):
            print("✅ 快捷键配置动作创建成功")
        else:
            print("❌ 快捷键配置动作未创建")
        
        return app, win
        
    except Exception as e:
        print(f"❌ 主窗口创建失败: {str(e)}")
        traceback.print_exc()
        return None, None

def test_signal_connections(win):
    """测试信号连接"""
    print("=" * 50)
    print("测试信号连接...")
    
    try:
        # 测试AI助手信号
        if hasattr(win, 'ai_assistant_panel'):
            panel = win.ai_assistant_panel
            
            # 检查信号是否存在
            signals = ['prediction_requested', 'batch_prediction_requested', 
                      'predictions_applied', 'model_changed']
            for signal_name in signals:
                if hasattr(panel, signal_name):
                    print(f"✅ AI助手信号 {signal_name} 存在")
                else:
                    print(f"❌ AI助手信号 {signal_name} 不存在")
        
        # 测试批量操作信号
        if hasattr(win, 'batch_operations'):
            batch_ops = win.batch_operations
            
            signals = ['operation_started', 'operation_progress', 
                      'operation_completed', 'operation_error']
            for signal_name in signals:
                if hasattr(batch_ops, signal_name):
                    print(f"✅ 批量操作信号 {signal_name} 存在")
                else:
                    print(f"❌ 批量操作信号 {signal_name} 不存在")
        
        # 测试快捷键管理信号
        if hasattr(win, 'shortcut_manager'):
            shortcut_mgr = win.shortcut_manager
            
            signals = ['shortcut_triggered', 'shortcuts_changed']
            for signal_name in signals:
                if hasattr(shortcut_mgr, signal_name):
                    print(f"✅ 快捷键管理信号 {signal_name} 存在")
                else:
                    print(f"❌ 快捷键管理信号 {signal_name} 不存在")
        
    except Exception as e:
        print(f"❌ 信号连接测试失败: {str(e)}")
        traceback.print_exc()

def test_menu_actions(win):
    """测试菜单动作"""
    print("=" * 50)
    print("测试菜单动作...")
    
    try:
        # 测试工具菜单是否有动作
        if hasattr(win.menus, 'tools'):
            tools_menu = win.menus.tools
            actions = tools_menu.actions()
            print(f"✅ 工具菜单包含 {len(actions)} 个动作")
            
            for action in actions:
                if action.isSeparator():
                    continue
                print(f"  - {action.text()}: {action.shortcut().toString()}")
        
        # 测试动作方法是否存在
        methods = ['on_ai_predict_current', 'on_ai_batch_predict', 'on_ai_toggle_panel',
                  'on_batch_copy', 'on_batch_delete', 'show_batch_operations_dialog',
                  'show_shortcut_config_dialog']
        
        for method_name in methods:
            if hasattr(win, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
        
    except Exception as e:
        print(f"❌ 菜单动作测试失败: {str(e)}")
        traceback.print_exc()

def test_dialog_creation(win):
    """测试对话框创建"""
    print("=" * 50)
    print("测试对话框创建...")
    
    try:
        # 测试批量操作对话框
        from libs.batch_operations import BatchOperationsDialog
        dialog = BatchOperationsDialog(win)
        print("✅ 批量操作对话框创建成功")
        dialog.close()
        
        # 测试快捷键配置对话框
        if hasattr(win, 'shortcut_manager'):
            from libs.shortcut_manager import ShortcutConfigDialog
            dialog = ShortcutConfigDialog(win.shortcut_manager, win)
            print("✅ 快捷键配置对话框创建成功")
            dialog.close()
        
    except Exception as e:
        print(f"❌ 对话框创建测试失败: {str(e)}")
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🚀 开始labelImg集成功能测试")
    print("测试时间:", os.popen('date').read().strip() if os.name != 'nt' else 'Windows')
    
    # 创建QApplication
    app = QApplication(sys.argv)
    
    # 运行测试
    test_imports()
    
    app_obj, win = test_main_window_creation()
    
    if win:
        test_signal_connections(win)
        test_menu_actions(win)
        test_dialog_creation(win)
        
        print("=" * 50)
        print("✅ 集成功能测试完成！")
        print("💡 建议：运行labelImg.py查看实际界面效果")
        
        # 显示主窗口进行手动测试
        win.show()
        
        # 设置定时器自动关闭（可选）
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(10000)  # 10秒后自动关闭
        
        return app.exec_()
    else:
        print("=" * 50)
        print("❌ 集成功能测试失败！")
        return 1

if __name__ == '__main__':
    sys.exit(main())
