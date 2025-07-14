#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的Material Design界面
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
except ImportError:
    print("错误: 需要安装PyQt5")
    print("请运行: pip install PyQt5")
    sys.exit(1)

def test_ui():
    """测试新界面"""
    print("🚀 启动labelImg新界面测试...")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # 导入主窗口
        from labelImg import get_main_app
        
        print("✅ 成功导入labelImg模块")
        
        # 创建主窗口
        app, win = get_main_app(sys.argv)
        
        print("✅ 成功创建主窗口")
        print("🎨 新的Material Design界面已加载")
        print("\n🌟 新功能特性:")
        print("  📱 现代化Material Design风格")
        print("  🎯 欢迎界面和快捷操作")
        print("  🔍 文件和标签搜索功能")
        print("  📊 实时统计信息显示")
        print("  🎨 分组工具栏设计")
        print("  💡 增强的状态栏信息")
        print("  🚀 快捷操作面板")
        
        # 设置窗口标题
        win.setWindowTitle("labelImg - Material Design 界面")
        
        # 显示窗口
        win.show()
        
        print("\n🎉 界面测试启动成功!")
        print("💡 提示: 可以尝试打开图片或文件夹来测试新功能")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    required_modules = [
        'PyQt5',
        'lxml',
        'Pillow'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (缺失)")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  缺少依赖项: {', '.join(missing_modules)}")
        print("请运行以下命令安装:")
        for module in missing_modules:
            if module == 'Pillow':
                print(f"  pip install {module}")
            else:
                print(f"  pip install {module}")
        return False
    
    print("✅ 所有依赖项已满足")
    return True

def main():
    """主函数"""
    print("🏷️  labelImg Material Design 界面测试")
    print("=" * 50)
    
    # 检查依赖项
    if not check_dependencies():
        return 1
    
    # 测试界面
    return test_ui()

if __name__ == '__main__':
    sys.exit(main())
