#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目管理系统集成测试
验证项目管理功能的完整性和与现有系统的兼容性
"""

import os
import sys
import tempfile
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_project_manager():
    """测试项目管理器核心功能"""
    print("=== 测试项目管理器核心功能 ===")
    
    # 使用临时目录进行测试
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        from libs.project_manager import ProjectManager
        
        # 初始化项目管理器
        manager = ProjectManager()
        
        # 测试默认项目创建
        projects = manager.list_projects()
        assert "default" in projects, "默认项目应该自动创建"
        print("✓ 默认项目自动创建成功")
        
        # 测试项目创建
        success = manager.create_project(
            "test_project",
            display_name="测试项目",
            description="这是一个测试项目"
        )
        assert success, "项目创建应该成功"
        print("✓ 项目创建成功")
        
        # 测试项目列表
        projects = manager.list_projects()
        assert "test_project" in projects, "新项目应该出现在列表中"
        print("✓ 项目列表正确")
        
        # 测试项目切换
        success = manager.switch_project("test_project")
        assert success, "项目切换应该成功"
        current = manager.get_current_project()
        assert current == "test_project", "当前项目应该是test_project"
        print("✓ 项目切换成功")
        
        # 测试项目配置
        from libs.project_manager import ProjectConfig
        config = ProjectConfig(
            classes=["cat", "dog"],
            class_metadata={},
            training_preferences={"epochs": 50},
            training_history=[],
            ui_preferences={},
            shortcuts={},
            ai_settings={}
        )
        
        success = manager.save_project_config("test_project", config)
        assert success, "项目配置保存应该成功"
        print("✓ 项目配置保存成功")
        
        loaded_config = manager.get_project_config("test_project")
        assert loaded_config is not None, "应该能加载项目配置"
        assert loaded_config.classes == ["cat", "dog"], "类别配置应该正确"
        print("✓ 项目配置加载成功")
        
        # 测试项目删除
        manager.switch_project("default")  # 先切换到其他项目
        success = manager.delete_project("test_project")
        assert success, "项目删除应该成功"
        
        projects = manager.list_projects()
        assert "test_project" not in projects, "删除的项目不应该在列表中"
        print("✓ 项目删除成功")
        
    print("项目管理器核心功能测试通过！\n")

def test_config_adapter():
    """测试配置适配器"""
    print("=== 测试配置适配器 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        from libs.project_manager import get_project_manager
        from libs.project_config_adapter import get_config_adapter
        
        # 初始化
        manager = get_project_manager()
        adapter = get_config_adapter()
        
        # 测试类别操作
        classes = ["person", "car", "bike"]
        success = adapter.save_classes(classes)
        assert success, "保存类别应该成功"
        print("✓ 类别保存成功")
        
        loaded_classes = adapter.load_classes()
        assert loaded_classes == classes, "加载的类别应该与保存的一致"
        print("✓ 类别加载成功")
        
        # 测试训练配置
        prefs = {"epochs": 100, "batch_size": 16, "model": "yolov8n.pt"}
        success = adapter.save_training_preferences(prefs)
        assert success, "保存训练配置应该成功"
        
        loaded_prefs = adapter.load_training_preferences()
        assert loaded_prefs["epochs"] == 100, "训练配置应该正确"
        print("✓ 训练配置保存和加载成功")
        
        # 测试训练历史
        record = {
            "timestamp": datetime.now().isoformat(),
            "epochs": 50,
            "best_map": 0.85
        }
        success = adapter.add_training_record(record)
        assert success, "添加训练记录应该成功"
        
        history = adapter.load_training_history()
        assert len(history) == 1, "应该有一条训练记录"
        assert history[0]["epochs"] == 50, "训练记录内容应该正确"
        print("✓ 训练历史记录成功")
        
        # 测试路径获取
        data_path = adapter.get_project_data_path()
        assert os.path.exists(data_path), "项目数据路径应该存在"
        print("✓ 项目路径获取成功")
        
    print("配置适配器测试通过！\n")

def test_legacy_migration():
    """测试旧版配置迁移"""
    print("=== 测试旧版配置迁移 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # 创建旧版配置文件
        old_configs_dir = Path("configs")
        old_configs_dir.mkdir()
        
        # 创建旧版类别配置
        old_class_config = {
            'version': '1.0',
            'classes': ['old_class1', 'old_class2'],
            'class_metadata': {},
            'settings': {}
        }
        
        with open(old_configs_dir / "class_config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(old_class_config, f, allow_unicode=True)
        
        # 创建旧版训练配置
        old_training_prefs = {
            'epochs': 75,
            'batch_size': 8,
            'model': 'yolov8s.pt'
        }
        
        with open(old_configs_dir / "training_preferences.json", 'w', encoding='utf-8') as f:
            json.dump(old_training_prefs, f)
        
        print("✓ 创建旧版配置文件")
        
        # 执行迁移
        from libs.project_integration_helper import get_integration_helper
        helper = get_integration_helper()
        
        assert helper.is_first_run(), "应该检测到首次运行"
        print("✓ 检测到首次运行")
        
        success = helper.migrate_legacy_system()
        assert success, "迁移应该成功"
        print("✓ 旧版配置迁移成功")
        
        # 验证迁移结果
        from libs.project_config_adapter import get_config_adapter
        adapter = get_config_adapter()
        
        classes = adapter.load_classes()
        assert classes == ['old_class1', 'old_class2'], "迁移后的类别应该正确"
        print("✓ 类别配置迁移正确")
        
        prefs = adapter.load_training_preferences()
        assert prefs['epochs'] == 75, "迁移后的训练配置应该正确"
        print("✓ 训练配置迁移正确")
        
        # 验证项目结构
        projects_dir = Path("projects")
        assert projects_dir.exists(), "应该创建projects目录"
        assert (projects_dir / "default").exists(), "应该有default项目"
        print("✓ 项目结构创建正确")
        
    print("旧版配置迁移测试通过！\n")

def test_gui_components():
    """测试GUI组件（无显示测试）"""
    print("=== 测试GUI组件 ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        # 创建QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # 初始化项目系统
            from libs.project_integration_helper import initialize_project_system
            initialize_project_system()
            
            # 测试项目选择器组件
            from libs.project_selector import ProjectSelector, CompactProjectSelector
            
            selector = ProjectSelector()
            assert selector is not None, "项目选择器应该能创建"
            print("✓ 项目选择器创建成功")
            
            compact_selector = CompactProjectSelector()
            assert compact_selector is not None, "紧凑型选择器应该能创建"
            print("✓ 紧凑型选择器创建成功")
            
            # 测试项目管理对话框
            from libs.project_management_dialog import ProjectManagementDialog, ProjectCreationDialog
            
            # 不显示对话框，只测试创建
            dialog = ProjectManagementDialog()
            assert dialog is not None, "项目管理对话框应该能创建"
            print("✓ 项目管理对话框创建成功")
            
            creation_dialog = ProjectCreationDialog()
            assert creation_dialog is not None, "项目创建对话框应该能创建"
            print("✓ 项目创建对话框创建成功")
        
    except ImportError as e:
        print(f"⚠ GUI组件测试跳过（PyQt5不可用）: {e}")
    except Exception as e:
        print(f"✗ GUI组件测试出现异常: {e}")
        raise
    
    print("GUI组件测试完成！\n")

def test_integration_helper():
    """测试集成辅助工具"""
    print("=== 测试集成辅助工具 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        from libs.project_integration_helper import get_integration_helper
        helper = get_integration_helper()
        
        # 测试系统初始化
        success = helper.initialize_project_system()
        assert success, "系统初始化应该成功"
        print("✓ 系统初始化成功")
        
        # 测试项目信息获取
        info = helper.get_current_project_info()
        assert info is not None, "应该能获取项目信息"
        assert "name" in info, "项目信息应该包含名称"
        print("✓ 项目信息获取成功")
        
        # 测试从模板创建项目
        success = helper.create_project_from_template("template_test", "detection")
        assert success, "从模板创建项目应该成功"
        print("✓ 从模板创建项目成功")
        
        # 验证模板配置
        from libs.project_manager import get_project_manager
        manager = get_project_manager()
        config = manager.get_project_config("template_test")
        assert config is not None, "应该能获取模板项目配置"
        assert "object" in config.classes, "检测模板应该有object类别"
        print("✓ 模板配置验证成功")
        
        # 测试项目导出
        export_dir = Path(temp_dir) / "exports"
        success = helper.export_project("template_test", str(export_dir))
        assert success, "项目导出应该成功"
        
        export_file = export_dir / "template_test_export.zip"
        assert export_file.exists(), "导出文件应该存在"
        print("✓ 项目导出成功")
        
        # 测试项目导入
        success = helper.import_project(str(export_file), "imported_test")
        assert success, "项目导入应该成功"
        
        projects = manager.list_projects()
        assert "imported_test" in projects, "导入的项目应该在列表中"
        print("✓ 项目导入成功")
        
    print("集成辅助工具测试通过！\n")

def test_error_handling():
    """测试错误处理"""
    print("=== 测试错误处理 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        from libs.project_manager import get_project_manager
        manager = get_project_manager()
        
        # 测试重复项目创建
        success1 = manager.create_project("duplicate_test", "重复项目1")
        assert success1, "第一次创建应该成功"
        
        success2 = manager.create_project("duplicate_test", "重复项目2")
        assert not success2, "重复创建应该失败"
        print("✓ 重复项目创建正确处理")
        
        # 测试删除不存在的项目
        success = manager.delete_project("nonexistent")
        assert not success, "删除不存在的项目应该失败"
        print("✓ 删除不存在项目正确处理")
        
        # 测试切换到不存在的项目
        success = manager.switch_project("nonexistent")
        assert not success, "切换到不存在项目应该失败"
        print("✓ 切换不存在项目正确处理")
        
        # 测试无效项目名称
        success = manager.create_project("invalid/name", "无效名称")
        assert not success, "无效项目名称应该被拒绝"
        print("✓ 无效项目名称正确处理")
        
    print("错误处理测试通过！\n")

def test_performance():
    """测试性能（大量项目）"""
    print("=== 测试性能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        from libs.project_manager import get_project_manager
        manager = get_project_manager()
        
        import time
        start_time = time.time()
        
        # 创建多个项目
        project_count = 20
        for i in range(project_count):
            success = manager.create_project(f"perf_test_{i}", f"性能测试项目{i}")
            assert success, f"项目{i}创建应该成功"
        
        creation_time = time.time() - start_time
        print(f"✓ 创建{project_count}个项目用时: {creation_time:.2f}秒")
        
        # 测试项目列表性能
        start_time = time.time()
        for _ in range(10):
            projects = manager.list_projects()
            assert len(projects) >= project_count, "项目数量应该正确"
        
        list_time = time.time() - start_time
        print(f"✓ 10次项目列表查询用时: {list_time:.2f}秒")
        
        # 测试项目切换性能
        start_time = time.time()
        for i in range(5):
            success = manager.switch_project(f"perf_test_{i}")
            assert success, f"切换到项目{i}应该成功"
        
        switch_time = time.time() - start_time
        print(f"✓ 5次项目切换用时: {switch_time:.2f}秒")
        
        # 性能基准检查
        assert creation_time < 5.0, "项目创建性能应该可接受"
        assert list_time < 1.0, "项目列表查询性能应该可接受"
        assert switch_time < 2.0, "项目切换性能应该可接受"
        
    print("性能测试通过！\n")

def main():
    """运行所有测试"""
    print("开始项目管理系统集成测试...\n")
    
    try:
        test_project_manager()
        test_config_adapter()
        test_legacy_migration()
        test_gui_components()
        test_integration_helper()
        test_error_handling()
        test_performance()
        
        print("🎉 所有测试通过！项目管理系统已准备就绪。")
        print("\n集成建议：")
        print("1. 将项目管理系统集成到主程序labelImg.py中")
        print("2. 在主界面添加项目选择器组件")
        print("3. 在菜单栏添加项目管理菜单")
        print("4. 测试现有功能的兼容性")
        print("5. 为用户提供项目管理说明文档")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)