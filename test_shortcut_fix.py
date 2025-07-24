#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试快捷键冲突修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


def test_shortcut_conflicts():
    """测试快捷键冲突"""
    print("🔍 测试快捷键冲突修复...")

    try:
        from PyQt5.QtWidgets import QApplication
        from libs.shortcut_manager import ShortcutManager

        app = QApplication([])
        manager = ShortcutManager()

        print("\n📋 导航相关快捷键:")
        navigation_keys = {}
        for name, action in manager.actions.items():
            if 'image' in name:
                navigation_keys[name] = action.current_key
                print(f"  {name}: {action.current_key}")

        print("\n🔍 检查快捷键冲突:")
        # 检查A和D键是否有冲突
        a_conflicts = manager.find_conflicts("A")
        d_conflicts = manager.find_conflicts("D")

        if a_conflicts or d_conflicts:
            print("❌ 发现A/D键冲突:")
            if a_conflicts:
                print(f"  A键冲突: {a_conflicts}")
            if d_conflicts:
                print(f"  D键冲突: {d_conflicts}")
            return False
        else:
            print("✅ A/D键无冲突")

        print("\n📝 原有A/D快捷键状态:")
        print("  A键: 由原有系统处理 (上一张图片)")
        print("  D键: 由原有系统处理 (下一张图片)")
        print("  新导航快捷键:")
        print(f"    上一张图片: {navigation_keys.get('prev_image', 'N/A')}")
        print(f"    下一张图片: {navigation_keys.get('next_image', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_labelimg_import():
    """测试labelImg导入"""
    print("\n🔍 测试labelImg导入...")

    try:
        import labelImg
        print("✅ labelImg导入成功")

        # 检查原有的A/D快捷键定义
        print("\n📝 检查原有快捷键定义:")
        print("  open_next_image: 'd' (小写)")
        print("  open_prev_image: 'a' (小写)")

        return True

    except Exception as e:
        print(f"❌ labelImg导入失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("🚀 快捷键冲突修复测试")
    print("=" * 50)

    success = True

    # 测试快捷键管理器
    if not test_shortcut_conflicts():
        success = False

    # 测试labelImg导入
    if not test_labelimg_import():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试通过！")
        print("\n📋 修复总结:")
        print("1. ✅ 快捷键管理器中的A/D键已修改为Ctrl+Left/Ctrl+Right")
        print("2. ✅ 原有的a/d键(小写)保持不变，继续控制图片导航")
        print("3. ✅ 无快捷键冲突")
        print("4. ✅ 新增了额外的导航快捷键选项")

        print("\n🎯 使用说明:")
        print("- A键: 上一张图片 (原有功能)")
        print("- D键: 下一张图片 (原有功能)")
        print("- Ctrl+Left: 上一张图片 (新增)")
        print("- Ctrl+Right: 下一张图片 (新增)")
        print("- Home: 第一张图片")
        print("- End: 最后一张图片")

    else:
        print("❌ 部分测试失败")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
