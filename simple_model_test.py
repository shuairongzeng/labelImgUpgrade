#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版项目模型隔离测试
"""

import os
import sys
from pathlib import Path

# 添加libs路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def test_model_scanning():
    """测试模型扫描"""
    print("=" * 50)
    print("项目模型隔离测试")
    print("=" * 50)
    
    try:
        # 1. 检查项目目录
        print("\n1. 检查项目目录...")
        models_dir = Path("projects/DnfSmallMap/models")
        if models_dir.exists():
            model_files = list(models_dir.glob("*.pt"))
            print(f"项目模型目录存在: {models_dir}")
            print(f"找到模型文件: {len(model_files)}")
            for model_file in model_files:
                print(f"  - {model_file.name}")
        else:
            print("项目模型目录不存在")
            return False
        
        # 2. 测试项目管理器
        print("\n2. 测试项目管理器...")
        from libs.project_manager import get_project_manager
        manager = get_project_manager()
        current_project = manager.get_current_project()
        print(f"当前项目: {current_project}")
        
        if current_project != "DnfSmallMap":
            print("切换到DnfSmallMap项目...")
            manager.switch_project("DnfSmallMap")
            current_project = manager.get_current_project()
            print(f"切换后项目: {current_project}")
        
        # 3. 测试模型管理器
        print("\n3. 测试模型管理器...")
        from libs.ai_assistant.model_manager import ModelManager
        model_manager = ModelManager()
        
        models = model_manager.scan_models()
        print(f"扫描到模型总数: {len(models)}")
        
        # 分类统计
        project_models = []
        for model in models:
            model_path = str(model)
            if f"projects/{current_project}/models" in model_path:
                project_models.append(model)
        
        print(f"项目特定模型数量: {len(project_models)}")
        for model in project_models:
            print(f"  - {model}")
        
        # 检查测试模型
        test_model_found = any("trained_model_20250828_133309.pt" in str(model) 
                              for model in project_models)
        
        if test_model_found:
            print("\n成功找到测试模型!")
            return True
        else:
            print("\n未找到测试模型")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_scanning()
    print("\n" + "=" * 50)
    if success:
        print("测试通过 - 项目模型隔离工作正常")
    else:
        print("测试失败 - 需要进一步调试")
    print("=" * 50)