#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态栏诊断脚本
用于检查labelImg应用的状态栏实际状态
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import QTimer

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_status_bar():
    """诊断状态栏问题"""
    app = QApplication(sys.argv)
    
    try:
        # 导入主窗口类
        from labelImg import MainWindow
        
        # 创建主窗口实例
        main_window = MainWindow()
        
        print("=== 状态栏诊断报告 ===")
        print(f"主窗口类型: {type(main_window)}")
        
        # 获取状态栏
        status_bar = main_window.statusBar()
        print(f"状态栏对象: {status_bar}")
        print(f"状态栏是否可见: {status_bar.isVisible()}")
        
        # 检查状态栏中的所有子控件
        print("\n=== 状态栏子控件列表 ===")
        children = status_bar.children()
        print(f"子控件总数: {len(children)}")
        
        for i, child in enumerate(children):
            if isinstance(child, QLabel):
                print(f"  {i}: QLabel - 文本: '{child.text()}' - 可见: {child.isVisible()}")
            else:
                print(f"  {i}: {type(child).__name__} - 可见: {getattr(child, 'isVisible', lambda: 'N/A')()}")
        
        # 检查特定的状态栏元素是否存在
        print("\n=== 检查特定状态栏元素 ===")
        
        # 检查我们期望的新元素
        expected_elements = [
            'image_info_label',
            'annotation_stats_label', 
            'zoom_info_label',
            'annotation_progress_label',
            'annotation_progress_bar',
            'current_image_status',
            'label_coordinates',
            'position_label'
        ]
        
        for element_name in expected_elements:
            if hasattr(main_window, element_name):
                element = getattr(main_window, element_name)
                print(f"  ✅ {element_name}: 存在")
                print(f"     类型: {type(element).__name__}")
                if hasattr(element, 'text'):
                    print(f"     文本: '{element.text()}'")
                if hasattr(element, 'isVisible'):
                    print(f"     可见: {element.isVisible()}")
                if hasattr(element, 'parent'):
                    parent = element.parent()
                    print(f"     父控件: {type(parent).__name__ if parent else 'None'}")
            else:
                print(f"  ❌ {element_name}: 不存在")
        
        # 检查setup_enhanced_status_bar方法是否存在
        print(f"\n=== 方法检查 ===")
        print(f"setup_enhanced_status_bar方法存在: {hasattr(main_window, 'setup_enhanced_status_bar')}")
        print(f"update_status_bar_info方法存在: {hasattr(main_window, 'update_status_bar_info')}")
        print(f"calculate_annotation_statistics方法存在: {hasattr(main_window, 'calculate_annotation_statistics')}")
        
        # 尝试调用update_status_bar_info方法
        print(f"\n=== 尝试更新状态栏 ===")
        try:
            main_window.update_status_bar_info()
            print("✅ update_status_bar_info调用成功")
        except Exception as e:
            print(f"❌ update_status_bar_info调用失败: {e}")
        
        # 检查状态栏布局
        print(f"\n=== 状态栏布局信息 ===")
        layout = status_bar.layout()
        print(f"布局对象: {layout}")
        
        # 显示主窗口（用于测试）
        main_window.show()

        # 设置定时器在200ms后重新检查状态栏（等待ensure_status_bar_visible执行）
        def recheck_status_bar():
            print("\n=== 重新检查状态栏状态 ===")
            status_bar = main_window.statusBar()
            print(f"状态栏是否可见（重新检查）: {status_bar.isVisible()}")

            # 检查所有子控件的可见性
            children = status_bar.children()
            visible_count = 0
            for i, child in enumerate(children):
                if hasattr(child, 'isVisible') and child.isVisible():
                    visible_count += 1
                    if isinstance(child, QLabel):
                        print(f"  可见的QLabel: '{child.text()}'")

            print(f"可见的子控件数量: {visible_count}/{len(children)}")

        QTimer.singleShot(200, recheck_status_bar)

        # 设置定时器在3秒后关闭应用
        def close_app():
            print("\n=== 诊断完成 ===")
            app.quit()

        QTimer.singleShot(3000, close_app)
        
        # 运行应用
        app.exec_()
        
    except Exception as e:
        print(f"❌ 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        app.quit()

if __name__ == "__main__":
    diagnose_status_bar()
