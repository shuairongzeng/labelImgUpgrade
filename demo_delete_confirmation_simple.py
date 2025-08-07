#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
删除确认功能演示脚本（简化版）
展示新的智能删除确认功能的核心逻辑，不依赖GUI组件
"""

import os
import sys
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.settings import Settings


class MockDeleteConfirmationDialog:
    """模拟删除确认对话框类，用于演示核心逻辑"""
    
    @staticmethod
    def should_show_confirmation(operation_type="delete_current"):
        """检查是否应该显示确认对话框"""
        try:
            settings = Settings()
            settings.load()
            setting_key = f'delete_confirmation_disabled_{operation_type}'
            return not settings.get(setting_key, False)
        except Exception as e:
            print(f"检查删除确认设置失败: {e}")
            return True  # 默认显示确认对话框
    
    @staticmethod
    def reset_confirmation_settings():
        """重置确认设置（恢复显示确认对话框）"""
        try:
            settings = Settings()
            settings.load()
            
            # 重置所有删除确认设置
            for operation_type in ["delete_current", "delete_menu"]:
                setting_key = f'delete_confirmation_disabled_{operation_type}'
                if setting_key in settings.data:
                    del settings.data[setting_key]
            
            settings.save()
            return True
        except Exception as e:
            print(f"重置删除确认设置失败: {e}")
            return False
    
    @staticmethod
    def save_dont_ask_setting(operation_type, dont_ask):
        """保存"不再提示"设置"""
        try:
            settings = Settings()
            settings.load()
            setting_key = f'delete_confirmation_disabled_{operation_type}'
            settings[setting_key] = dont_ask
            settings.save()
            return True
        except Exception as e:
            print(f"保存删除确认设置失败: {e}")
            return False


def demo_settings_functionality():
    """演示设置功能"""
    print("=" * 60)
    print("🔧 删除确认设置功能演示")
    print("=" * 60)
    
    # 1. 检查默认状态
    print("1. 检查默认状态:")
    show_current = MockDeleteConfirmationDialog.should_show_confirmation("delete_current")
    show_menu = MockDeleteConfirmationDialog.should_show_confirmation("delete_menu")
    print(f"   delete_current: {'显示确认对话框' if show_current else '不显示确认对话框'}")
    print(f"   delete_menu: {'显示确认对话框' if show_menu else '不显示确认对话框'}")
    
    # 2. 模拟用户禁用确认对话框
    print("\n2. 模拟用户选择'不再提示':")
    success = MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
    print(f"   保存结果: {'成功' if success else '失败'}")
    print("   已保存设置: delete_current 不再显示确认对话框")
    
    # 3. 验证设置生效
    print("\n3. 验证设置生效:")
    show_current = MockDeleteConfirmationDialog.should_show_confirmation("delete_current")
    show_menu = MockDeleteConfirmationDialog.should_show_confirmation("delete_menu")
    print(f"   delete_current: {'显示确认对话框' if show_current else '不显示确认对话框'}")
    print(f"   delete_menu: {'显示确认对话框' if show_menu else '不显示确认对话框'}")
    
    # 4. 重置设置
    print("\n4. 重置确认设置:")
    success = MockDeleteConfirmationDialog.reset_confirmation_settings()
    print(f"   重置结果: {'成功' if success else '失败'}")
    
    # 5. 验证重置结果
    print("\n5. 验证重置结果:")
    show_current = MockDeleteConfirmationDialog.should_show_confirmation("delete_current")
    show_menu = MockDeleteConfirmationDialog.should_show_confirmation("delete_menu")
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
        print(f"创建测试文件: {os.path.basename(temp_file.name)}")
        
        # 1. 第一次删除 - 应该显示完整对话框
        print("\n1. 第一次删除操作:")
        should_show = MockDeleteConfirmationDialog.should_show_confirmation("delete_current")
        print(f"   应该显示完整确认对话框: {should_show}")
        
        if should_show:
            print("   -> 会显示包含'不再提示'复选框的完整对话框")
            print("   -> 用户可以选择勾选'不再提示'来简化后续操作")
        else:
            print("   -> 会显示简化的确认对话框")
        
        # 2. 模拟用户勾选"不再提示"
        print("\n2. 模拟用户勾选'不再提示'并确认删除:")
        success = MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
        print(f"   保存设置结果: {'成功' if success else '失败'}")
        print("   用户选择: 不再显示完整确认对话框")
        
        # 3. 第二次删除 - 应该显示简化对话框
        print("\n3. 第二次删除操作:")
        should_show = MockDeleteConfirmationDialog.should_show_confirmation("delete_current")
        print(f"   应该显示完整确认对话框: {should_show}")
        
        if should_show:
            print("   -> 会显示包含'不再提示'复选框的完整对话框")
        else:
            print("   -> 会显示简化的确认对话框")
            print("   -> 提高了删除效率，减少了重复确认")
        
        # 4. 用户通过菜单重置设置
        print("\n4. 用户通过菜单重置确认设置:")
        success = MockDeleteConfirmationDialog.reset_confirmation_settings()
        print(f"   重置结果: {'成功' if success else '失败'}")
        print("   用户可以通过'工具' -> '重置删除确认'来恢复完整确认模式")
        
        # 5. 第三次删除 - 应该重新显示完整对话框
        print("\n5. 第三次删除操作:")
        should_show = MockDeleteConfirmationDialog.should_show_confirmation("delete_current")
        print(f"   应该显示完整确认对话框: {should_show}")
        
        if should_show:
            print("   -> 会显示包含'不再提示'复选框的完整对话框")
            print("   -> 安全性得到恢复，防止误删除")
        else:
            print("   -> 会显示简化的确认对话框")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        print(f"\n清理测试文件: {os.path.basename(temp_file.name)}")


def demo_different_operation_types():
    """演示不同操作类型的独立性"""
    print("\n" + "=" * 60)
    print("🎯 不同操作类型独立性演示")
    print("=" * 60)
    
    # 重置所有设置
    MockDeleteConfirmationDialog.reset_confirmation_settings()
    
    print("1. 初始状态 - 所有操作都显示确认对话框:")
    for op_type in ["delete_current", "delete_menu"]:
        should_show = MockDeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    # 只禁用delete_current
    print("\n2. 只禁用delete_current的确认对话框:")
    MockDeleteConfirmationDialog.save_dont_ask_setting("delete_current", True)
    
    for op_type in ["delete_current", "delete_menu"]:
        should_show = MockDeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    print("   -> 按钮删除简化，菜单删除仍显示完整确认")
    
    # 禁用所有
    print("\n3. 禁用所有确认对话框:")
    MockDeleteConfirmationDialog.save_dont_ask_setting("delete_menu", True)
    
    for op_type in ["delete_current", "delete_menu"]:
        should_show = MockDeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    print("   -> 所有删除操作都使用简化确认")
    
    # 重置
    print("\n4. 重置所有设置:")
    MockDeleteConfirmationDialog.reset_confirmation_settings()
    
    for op_type in ["delete_current", "delete_menu"]:
        should_show = MockDeleteConfirmationDialog.should_show_confirmation(op_type)
        print(f"   {op_type}: {'显示' if should_show else '不显示'}")
    
    print("   -> 所有删除操作恢复完整确认模式")


def demo_user_experience():
    """演示用户体验改进"""
    print("\n" + "=" * 60)
    print("✨ 用户体验改进演示")
    print("=" * 60)
    
    print("新功能带来的用户体验改进:")
    print()
    print("🎯 智能确认系统:")
    print("   • 第一次删除：显示详细的确认对话框，包含文件信息")
    print("   • 包含'不再提示'复选框，用户可选择简化后续操作")
    print("   • 勾选后：后续删除只显示简单确认，大幅提高效率")
    print("   • 即使简化，仍保留基本的安全确认")
    print()
    print("🔧 灵活的设置管理:")
    print("   • 不同删除方式（按钮删除 vs 菜单删除）独立设置")
    print("   • 可通过菜单随时重置确认设置")
    print("   • 设置持久化保存，重启应用后仍然有效")
    print("   • 支持部分简化：可以只简化某种删除方式")
    print()
    print("🎨 优化的视觉反馈:")
    print("   • 删除按钮增强hover效果和危险提示")
    print("   • 状态栏显示详细的删除结果和恢复提示")
    print("   • 现代化的对话框设计，信息层次清晰")
    print("   • 工具提示明确标注操作危险性")
    print()
    print("🛡️ 安全性保障:")
    print("   • 即使选择'不再提示'，仍有简化确认对话框")
    print("   • 删除按钮默认不获得焦点，防止误操作")
    print("   • 可随时恢复完整确认模式")
    print("   • 不同操作类型独立设置，精细控制")


def demo_implementation_details():
    """演示实现细节"""
    print("\n" + "=" * 60)
    print("🔧 实现细节演示")
    print("=" * 60)
    
    print("技术实现要点:")
    print()
    print("📁 文件结构:")
    print("   • libs/delete_confirmation_dialog.py - 对话框类")
    print("   • DeleteConfirmationDialog - 完整确认对话框")
    print("   • SimpleDeleteConfirmationDialog - 简化确认对话框")
    print("   • 集成到labelImg.py主程序中")
    print()
    print("💾 设置存储:")
    print("   • 使用现有的Settings类进行设置管理")
    print("   • 设置键格式: delete_confirmation_disabled_{operation_type}")
    print("   • 支持delete_current和delete_menu两种操作类型")
    print("   • 设置文件: ~/.labelImgSettings.pkl")
    print()
    print("🔄 工作流程:")
    print("   • 1. 检查should_show_confirmation()判断显示哪种对话框")
    print("   • 2. 显示对应的确认对话框")
    print("   • 3. 用户确认后保存设置（如果勾选了'不再提示'）")
    print("   • 4. 执行删除操作")
    print("   • 5. 显示增强的状态栏反馈")
    print()
    print("🧪 测试覆盖:")
    print("   • 单元测试覆盖设置保存/加载逻辑")
    print("   • 集成测试验证完整工作流程")
    print("   • 错误处理测试确保健壮性")


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
        
        # 演示实现细节
        demo_implementation_details()
        
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
        print("5. 不同的删除方式（按钮 vs 菜单）可以独立设置")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
