#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动测试模型导出对话框

运行这个脚本会打开模型导出对话框，让您可以手动验证：
1. 首次打开时是否自动选择了最佳模型
2. 模型详细信息是否立即显示
3. 性能指标是否正确显示
4. 文件名是否自动生成

使用方法：
python manual_test_dialog.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        from PyQt5.QtWidgets import QApplication
        from libs.model_export_dialog import ModelExportDialog
        
        print("🚀 启动模型导出对话框手动测试...")
        print("\n请观察以下几点：")
        print("1. 对话框打开后，模型下拉框是否自动选择了推荐模型")
        print("2. 模型名称标签是否显示了详细信息")
        print("3. 性能指标进度条是否显示了正确的数值")
        print("4. 输出文件名是否自动生成")
        print("5. 模型详情面板是否可见")
        print("\n如果以上都正常显示，说明修复成功！")
        print("=" * 50)
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建并显示对话框
        dialog = ModelExportDialog()
        dialog.show()
        
        print("✅ 对话框已打开，请检查界面显示...")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
