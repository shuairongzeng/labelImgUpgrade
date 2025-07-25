#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能预测功能测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_smart_predict_feature():
    """测试智能预测功能"""
    print("🧪 开始测试智能预测功能...")

    try:
        # 导入必要的模块
        from libs.ai_assistant_panel import AIAssistantPanel
        from PyQt5.QtWidgets import QApplication

        # 创建应用程序
        app = QApplication(sys.argv)

        # 创建AI助手面板
        panel = AIAssistantPanel()

        # 测试智能预测复选框是否存在
        assert hasattr(panel, 'smart_predict_checkbox'), "❌ 智能预测复选框不存在"
        print("✅ 智能预测复选框创建成功")

        # 测试智能预测状态检查方法
        assert hasattr(panel, 'is_smart_predict_enabled'), "❌ 智能预测状态检查方法不存在"
        print("✅ 智能预测状态检查方法存在")

        # 测试默认状态（应该是开启的）
        assert panel.is_smart_predict_enabled() == True, "❌ 智能预测默认状态不正确"
        print("✅ 智能预测默认状态正确（开启）")

        # 测试状态切换
        panel.smart_predict_checkbox.setChecked(False)
        assert panel.is_smart_predict_enabled() == False, "❌ 智能预测状态切换失败"
        print("✅ 智能预测状态切换成功")

        # 测试设置保存和加载方法
        assert hasattr(panel, 'save_smart_predict_setting'), "❌ 设置保存方法不存在"
        assert hasattr(panel, 'load_smart_predict_setting'), "❌ 设置加载方法不存在"
        print("✅ 设置保存和加载方法存在")

        # 测试复选框样式
        object_name = panel.smart_predict_checkbox.objectName()
        assert object_name == "smartPredictCheckbox", f"❌ 复选框对象名称不正确: {object_name}"
        print("✅ 复选框对象名称正确")

        # 测试工具提示
        tooltip = panel.smart_predict_checkbox.toolTip()
        print(f"📝 实际工具提示内容: '{tooltip}'")
        assert "智能预测" in tooltip, f"❌ 工具提示内容不正确，实际内容: '{tooltip}'"
        print("✅ 工具提示内容正确")

        print("\n🎉 智能预测功能测试全部通过！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window_integration():
    """测试主窗口集成"""
    print("\n🧪 开始测试主窗口集成...")

    try:
        # 导入主窗口
        from labelImg import MainWindow
        from PyQt5.QtWidgets import QApplication

        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # 创建主窗口
        window = MainWindow()

        # 测试智能预测相关变量
        assert hasattr(window, 'smart_predict_timer'), "❌ 智能预测定时器变量不存在"
        assert hasattr(window, 'last_smart_predict_path'), "❌ 最后预测路径变量不存在"
        print("✅ 智能预测相关变量存在")

        # 测试智能预测方法
        assert hasattr(
            window, 'trigger_smart_prediction_if_needed'), "❌ 智能预测触发方法不存在"
        assert hasattr(window, '_execute_smart_prediction'), "❌ 智能预测执行方法不存在"
        print("✅ 智能预测方法存在")

        print("✅ 主窗口集成测试通过！")
        return True

    except Exception as e:
        print(f"❌ 主窗口集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 智能预测功能测试开始\n")

    # 运行测试
    test1_passed = test_smart_predict_feature()
    test2_passed = test_main_window_integration()

    print(f"\n📊 测试结果:")
    print(f"   - AI助手面板测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"   - 主窗口集成测试: {'✅ 通过' if test2_passed else '❌ 失败'}")

    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！智能预测功能实现成功！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查实现。")
        sys.exit(1)
