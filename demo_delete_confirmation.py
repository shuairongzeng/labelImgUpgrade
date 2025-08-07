#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
删除确认功能演示脚本
展示新的智能删除确认功能的使用方法
"""

import os
import sys
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.delete_confirmation_dialog import DeleteConfirmationDialog, SimpleDeleteConfirmationDialog


def demo_settings_functionality():
    """演示设置功能"""
    print("=" * 60)
    print("🔧 删除确认设置功能演示")
    print("=" * 60)
    
    # 1. 检查默认状态
    print("1. 检查默认状态:")
    show_current = DeleteConfirmationDialog.should_show_confirmation("delete_current")
    show_menu = DeleteConfirmationDialog.should_show_confirmation("delete_menu")
    print(f"   delete_current: {'显示确认对话框' if show_current else '不显示确认对话框'}")
    print(f"   delete_menu: {'显示确认对话框' if show_menu else '不显示确认对话框'}")
    
    # 2. 模拟用户禁用确认对话框
    print("\n2. 模拟用户选择'不再提示':")
    from libs.settings import Settings
    settings = Settings()
    settings.load()
    settings['delete_confirmation_disabled_delete_current'] = True
    settings.save()
    print("   已保存设置: delete_current 不再显示确认对话框")
    
    # 3. 验证设置生效
    print("\n3. 验证设置生效:")
    show_current = DeleteConfirmationDialog.should_show_confirmation("delete_current")
    show_menu = DeleteConfirmationDialog.should_show_confirmation("delete_menu")
    print(f"   delete_current: {'显示确认对话框' if show_current else '不显示确认对话框'}")
    print(f"   delete_menu: {'显示确认对话框' if show_menu else '不显示确认对话框'}")
    
    # 4. 重置设置
    print("\n4. 重置确认设置:")
    success = DeleteConfirmationDialog.reset_confirmation_settings()
    print(f"   重置结果: {'成功' if success else '失败'}")
    
    # 5. 验证重置结果
    print("\n5. 验证重置结果:")
    show_current = DeleteConfirmationDialog.should_show_confirmation("delete_current")
    show_menu = DeleteConfirmationDialog.should_show_confirmation("delete_menu")
    print(f"   delete_current: {'显示确认对话框' if show_current else '不显示确认对话框'}")
    print(f"   delete_menu: {'显示确认对话框' if show_menu else '不显示确认对话框'}")


def demo_workflow():
    """演示完整的工作流程"""
    print("\n" + "=" * 60)
    print("🔄 完整工作流程演示")
    print("=" * 60)
    
    # 创建临时测试文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(b'test image data')
    temp_file.close()
    
    try:
        print(f"创建测试文件: {temp_file.name}")
        
        # 1. 第一次删除 - 应该显示完整对话框
        print("\n1. 第一次删除操作:")
        should_show = DeleteConfirmationDialog.should_show_confirmation("delete_current")
        print(f"   应该显示完整确认对话框: {should_show}")
        
        if should_show:
            print("   -> 会显示包含'不再提示'复选框的完整对话框")
        else:
            print("   -> 会显示简化的确认对话框")
        
        # 2. 模拟用户勾选"不再提示"
        print("\n2. 模拟用户勾选'不再提示'并确认删除:")
        from libs.settings import Settings
        settings = Settings()
        settings.load()
        settings['delete_confirmation_disabled_delete_current'] = True
        settings.save()
        print("   用户选择: 不再显示确认对话框")
        
        # 3. 第二次删除 - 应该显示简化对话框
        print("\n3. 第二次删除操作:")
        should_show = DeleteConfirmationDialog.should_show_confirmation("delete_current")
        print(f"   应该显示完整确认对话框: {should_show}")
        
        if should_show:
            print("   -> 会显示包含'不再提示'复选框的完整对话框")
        else:
            print("   -> 会显示简化的确认对话框")
        
        # 4. 用户通过菜单重置设置
        print("\n4. 用户通过菜单重置确认设置:")
        success = DeleteConfirmationDialog.reset_confirmation_settings()
        print(f"   重置结果: {'成功' if success else '失败'}")
        
        # 5. 第三次删除 - 应该重新显示完整对话框
        print("\n5. 第三次删除操作:")
        should_show = DeleteConfirmationDialog.should_show_confirmation("delete_current")
        print(f"   应该显示完整确认对话框: {should_show}")
        
        if should_show:
            print("   -> 会显示包含'不再提示'复选框的完整对话框")
        else:
            print("   -> 会显示简化的确认对话框")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        print(f"\n清理测试文件: {temp_file.name}")


def demo_different_operation_types():
    """演示不同操作类型的独立性"""
    print("\n" + "=" * 60)
    print("🎯 不同操作类型独立性演示")
    print("=" * 60)
    
    # 重置所有设置
    DeleteConfirmationDialog.reset_confirmation_settings()
    
    print("1. 初始状态 - 所有操作都显示确认对话框:")
    for op_type in ["delete_current", "delete_menu"]:
        should_show = DeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    # 只禁用delete_current
    print("\n2. 只禁用delete_current的确认对话框:")
    from libs.settings import Settings
    settings = Settings()
    settings.load()
    settings['delete_confirmation_disabled_delete_current'] = True
    settings.save()
    
    for op_type in ["delete_current", "delete_menu"]:
        should_show = DeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    # 禁用所有
    print("\n3. 禁用所有确认对话框:")
    settings['delete_confirmation_disabled_delete_menu'] = True
    settings.save()
    
    for op_type in ["delete_current", "delete_menu"]:
        should_show = DeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    # 重置
    print("\n4. 重置所有设置:")
    DeleteConfirmationDialog.reset_confirmation_settings()
    
    for op_type in ["delete_current", "delete_menu"]:
        should_show = DeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")


def demo_user_experience():
    """演示用户体验改进"""
    print("\n" + "=" * 60)
    print("✨ 用户体验改进演示")
    print("=" * 60)
    
    print("新功能带来的用户体验改进:")
    print()
    print("🎯 智能确认系统:")
    print("   • 第一次删除：显示详细的确认对话框")
    print("   • 包含'不再提示'复选框，用户可选择简化后续操作")
    print("   • 勾选后：后续删除只显示简单确认，提高效率")
    print()
    print("🔧 灵活的设置管理:")
    print("   • 不同删除方式（按钮删除 vs 菜单删除）独立设置")
    print("   • 可通过菜单随时重置确认设置")
    print("   • 设置持久化保存，重启应用后仍然有效")
    print()
    print("🎨 优化的视觉反馈:")
    print("   • 删除按钮增强hover效果和危险提示")
    print("   • 状态栏显示详细的删除结果和恢复提示")
    print("   • 现代化的对话框设计，信息层次清晰")
    print()
    print("🛡️ 安全性保障:")
    print("   • 即使选择'不再提示'，仍有简化确认对话框")
    print("   • 删除按钮工具提示明确标注危险性")
    print("   • 可随时恢复完整确认模式")


def main():
    """主函数"""
    print("🗑️ labelImg 智能删除确认功能演示")
    print("=" * 60)
    print("这个演示展示了新的智能删除确认功能的各项特性")
    print("包括设置保存/加载、工作流程、操作类型独立性等")
    print()
    
    try:
        # 演示设置功能
        demo_settings_functionality()
        
        # 演示完整工作流程
        demo_workflow()
        
        # 演示不同操作类型的独立性
        demo_different_operation_types()
        
        # 演示用户体验改进
        demo_user_experience()
        
        print("\n" + "=" * 60)
        print("✅ 演示完成！")
        print("=" * 60)
        print("新功能已经准备就绪，可以在labelImg中使用。")
        print()
        print("使用方法:")
        print("1. 启动labelImg应用")
        print("2. 加载图片后，点击'删除当前图片'按钮")
        print("3. 在确认对话框中可选择'不再提示'")
        print("4. 如需恢复确认对话框，可通过'工具' -> '重置删除确认'")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
