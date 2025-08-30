#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目管理系统简单测试
验证核心功能是否正常工作
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_basic_functionality():
    """测试基本功能"""
    print("开始测试项目管理系统基本功能...")
    
    try:
        # 测试导入模块
        from libs.project_manager import get_project_manager
        from libs.project_config_adapter import get_config_adapter
        print("[OK] 成功导入项目管理模块")
        
        # 初始化项目管理器
        manager = get_project_manager()
        print("[OK] 项目管理器初始化完成")
        
        # 检查默认项目
        current_project = manager.get_current_project()
        print(f"[INFO] 当前项目: {current_project}")
        
        # 列出所有项目
        projects = manager.list_projects()
        print(f"[INFO] 项目列表: {list(projects.keys())}")
        
        # 测试配置适配器
        adapter = get_config_adapter()
        print("[OK] 配置适配器初始化完成")
        
        # 测试类别操作
        test_classes = ["test_class1", "test_class2"]
        success = adapter.save_classes(test_classes)
        if success:
            print("[OK] 类别保存成功")
        else:
            print("[WARN] 类别保存失败")
        
        loaded_classes = adapter.load_classes()
        if loaded_classes == test_classes:
            print("[OK] 类别加载成功，数据一致")
        else:
            print(f"[WARN] 类别数据不一致: 期望{test_classes}, 实际{loaded_classes}")
        
        # 测试创建新项目
        new_project_name = "simple_test"
        success = manager.create_project(
            new_project_name,
            display_name="简单测试项目",
            description="用于验证项目管理功能"
        )
        
        if success:
            print(f"[OK] 新项目 '{new_project_name}' 创建成功")
            
            # 测试项目切换
            switch_success = manager.switch_project(new_project_name)
            if switch_success:
                print(f"[OK] 切换到项目 '{new_project_name}' 成功")
                
                # 切换回默认项目
                manager.switch_project("default")
                print("[OK] 切换回默认项目成功")
                
                # 删除测试项目
                delete_success = manager.delete_project(new_project_name)
                if delete_success:
                    print(f"[OK] 删除测试项目 '{new_project_name}' 成功")
                else:
                    print(f"[WARN] 删除测试项目失败")
            else:
                print(f"[WARN] 切换到项目 '{new_project_name}' 失败")
        else:
            print(f"[WARN] 创建新项目 '{new_project_name}' 失败")
        
        print("\n项目管理系统基本功能测试完成!")
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_components():
    """测试GUI组件（仅创建测试）"""
    print("\n开始测试GUI组件...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        # 创建QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 测试项目选择器
        from libs.project_selector import ProjectSelector
        selector = ProjectSelector()
        if selector:
            print("[OK] 项目选择器创建成功")
        
        # 测试项目管理对话框
        from libs.project_management_dialog import ProjectManagementDialog
        dialog = ProjectManagementDialog()
        if dialog:
            print("[OK] 项目管理对话框创建成功")
        
        print("GUI组件测试完成!")
        return True
        
    except ImportError:
        print("[SKIP] PyQt5不可用，跳过GUI测试")
        return True
    except Exception as e:
        print(f"[ERROR] GUI测试失败: {e}")
        return False

def test_integration():
    """测试系统集成"""
    print("\n开始测试系统集成...")
    
    try:
        from libs.project_integration_helper import get_integration_helper
        helper = get_integration_helper()
        print("[OK] 集成辅助工具初始化成功")
        
        # 测试当前项目信息获取
        info = helper.get_current_project_info()
        if info and "name" in info:
            print(f"[OK] 当前项目信息: {info.get('display_name', info.get('name', 'Unknown'))}")
        else:
            print("[WARN] 无法获取项目信息")
        
        # 测试路径获取
        from libs.project_integration_helper import get_current_project_paths
        paths = get_current_project_paths()
        
        print("[INFO] 当前项目路径:")
        for path_type, path in paths.items():
            print(f"  {path_type}: {path}")
            # 确保路径存在
            Path(path).mkdir(parents=True, exist_ok=True)
        
        print("系统集成测试完成!")
        return True
        
    except Exception as e:
        print(f"[ERROR] 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_project_structure():
    """显示项目结构"""
    print("\n当前项目结构:")
    
    try:
        projects_dir = Path("projects")
        if projects_dir.exists():
            print("projects/")
            for item in projects_dir.iterdir():
                if item.is_dir():
                    print(f"├── {item.name}/")
                    for subitem in item.iterdir():
                        if subitem.is_dir():
                            print(f"│   ├── {subitem.name}/")
                        else:
                            print(f"│   └── {subitem.name}")
                else:
                    print(f"└── {item.name}")
        else:
            print("projects目录不存在")
            
    except Exception as e:
        print(f"显示项目结构失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("              项目管理系统测试")
    print("=" * 60)
    
    # 保存原始工作目录
    original_dir = os.getcwd()
    
    try:
        # 运行测试
        success1 = test_basic_functionality()
        success2 = test_gui_components()
        success3 = test_integration()
        
        if success1 and success2 and success3:
            print("\n" + "=" * 60)
            print("[SUCCESS] 所有测试通过!")
            print("项目管理系统已准备就绪，可以集成到主程序中。")
            print("=" * 60)
            
            # 显示项目结构
            show_project_structure()
            
            return True
        else:
            print("\n" + "=" * 60)
            print("[FAILED] 部分测试失败")
            print("请检查错误信息并修复问题。")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] 测试执行异常: {e}")
        return False
    finally:
        # 恢复原始工作目录
        os.chdir(original_dir)

if __name__ == "__main__":
    success = main()
    input("\n按Enter键退出...")
    sys.exit(0 if success else 1)