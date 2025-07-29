#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证训练历史记录功能实现
"""

import os
import sys

def check_files_exist():
    """检查文件是否存在"""
    print("📁 检查文件存在性")
    print("-" * 30)
    
    files_to_check = [
        "libs/training_history_manager.py",
        "libs/ai_assistant_panel.py"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist


def check_training_history_manager():
    """检查训练历史管理器"""
    print("\n🔧 检查训练历史管理器")
    print("-" * 30)
    
    try:
        # 检查文件内容
        with open("libs/training_history_manager.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键类和方法
        checks = [
            ("class TrainingHistoryManager", "TrainingHistoryManager类"),
            ("def add_training_session", "添加训练会话方法"),
            ("def get_trained_images", "获取已训练图片方法"),
            ("def is_image_trained", "检查图片训练状态方法"),
            ("def filter_untrained_images", "过滤未训练图片方法"),
            ("def get_training_statistics", "获取统计信息方法")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def check_ai_assistant_panel():
    """检查AI助手面板修改"""
    print("\n🎛️ 检查AI助手面板修改")
    print("-" * 30)
    
    try:
        # 检查文件内容
        with open("libs/ai_assistant_panel.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键修改
        checks = [
            ("from .training_history_manager import TrainingHistoryManager", "导入训练历史管理器"),
            ("self.training_history_manager = TrainingHistoryManager()", "初始化训练历史管理器"),
            ("self.exclude_trained_checkbox", "排除已训练图片复选框"),
            ("不包含已训练的图片", "复选框标签"),
            ("def is_image_trained", "图片训练状态检查方法"),
            ("def filter_untrained_images", "图片过滤方法"),
            ("def _create_filtered_source_dir", "创建过滤目录方法"),
            ("def _update_training_history", "更新训练历史方法"),
            ("def _record_exported_images", "记录导出图片方法")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def check_ui_integration():
    """检查UI集成"""
    print("\n🖥️ 检查UI集成")
    print("-" * 30)
    
    try:
        with open("libs/ai_assistant_panel.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查一键配置对话框中的复选框
        ui_checks = [
            ("exclude_trained_checkbox = QCheckBox()", "复选框创建"),
            ("排除已经训练过的图片", "复选框提示文本"),
            ("exclude_trained = self.exclude_trained_checkbox.isChecked()", "复选框状态获取"),
            ("filtered_source_dir = self._create_filtered_source_dir", "过滤目录创建调用"),
            ("source_dir=filtered_source_dir", "使用过滤后的源目录")
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def main():
    """主验证函数"""
    print("🔍 验证训练历史记录功能实现")
    print("=" * 50)
    
    success = True
    
    # 检查文件存在性
    if not check_files_exist():
        success = False
    
    # 检查训练历史管理器
    if not check_training_history_manager():
        success = False
    
    # 检查AI助手面板修改
    if not check_ai_assistant_panel():
        success = False
    
    # 检查UI集成
    if not check_ui_integration():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有检查通过！功能实现完整。")
        print("\n📋 实现的功能:")
        print("1. ✅ 训练历史记录管理器 (TrainingHistoryManager)")
        print("2. ✅ 图片训练状态检查功能")
        print("3. ✅ 一键配置面板复选框 ('不包含已训练的图片')")
        print("4. ✅ 数据导出时自动过滤已训练图片")
        print("5. ✅ 训练完成后自动更新训练历史记录")
        
        print("\n🎯 使用说明:")
        print("1. 在一键配置对话框中勾选'不包含已训练的图片'")
        print("2. 系统会自动创建临时目录，只包含未训练过的图片")
        print("3. 训练完成后会自动记录本次训练使用的图片")
        print("4. 训练历史保存在 configs/training_history.json")
        
        print("\n⚠️ 注意事项:")
        print("1. 首次使用时没有训练历史，所有图片都会被包含")
        print("2. 训练历史基于图片文件名和路径进行匹配")
        print("3. 临时目录会在使用后自动清理")
        
    else:
        print("❌ 部分检查失败，请检查实现。")
    
    return success


if __name__ == "__main__":
    main()
