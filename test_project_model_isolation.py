#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 设置控制台编码为utf-8
if sys.platform.startswith('win'):
    os.system("chcp 65001 > nul")

"""
测试项目模型隔离修复
验证AI模型管理器能否正确扫描项目特定的训练模型
"""

import os
import sys
import json
from pathlib import Path

# 添加libs路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def test_project_model_scanning():
    """测试项目模型扫描功能"""
    print("=" * 60)
    print("🔍 测试项目模型隔离修复")
    print("=" * 60)
    
    try:
        # 1. 验证项目目录结构
        print("\n1. 验证项目目录结构...")
        dnf_project_dir = Path("projects/DnfSmallMap")
        if not dnf_project_dir.exists():
            print("❌ DnfSmallMap项目目录不存在")
            return False
            
        models_dir = dnf_project_dir / "models"
        if not models_dir.exists():
            print("❌ DnfSmallMap项目模型目录不存在")
            return False
            
        # 检查模型文件
        model_files = list(models_dir.glob("*.pt"))
        print(f"📁 项目模型目录: {models_dir}")
        print(f"📦 找到模型文件数量: {len(model_files)}")
        for model_file in model_files:
            print(f"   - {model_file.name} ({model_file.stat().st_size} bytes)")
        
        # 2. 测试项目管理器
        print("\n2. 测试项目管理器...")
        try:
            from libs.project_manager import get_project_manager
            manager = get_project_manager()
            current_project = manager.get_current_project()
            print(f"📋 当前项目: {current_project}")
            
            if current_project != "DnfSmallMap":
                print(f"⚠️  当前项目不是DnfSmallMap，而是: {current_project}")
                print("正在切换到DnfSmallMap项目...")
                manager.switch_project("DnfSmallMap")
                current_project = manager.get_current_project()
                print(f"📋 切换后当前项目: {current_project}")
            
        except Exception as e:
            print(f"❌ 项目管理器测试失败: {e}")
            return False
            
        # 3. 测试AI模型管理器
        print("\n3. 测试AI模型管理器...")
        try:
            from libs.ai_assistant.model_manager import ModelManager
            model_manager = ModelManager()
            
            print("🔍 开始扫描模型...")
            models = model_manager.scan_models()
            
            print(f"📊 扫描结果总数: {len(models)}")
            
            # 分类显示模型
            shared_models = []
            project_models = []
            global_models = []
            
            for model in models:
                model_path = str(model)
                if "projects/shared/models" in model_path:
                    shared_models.append(model)
                elif f"projects/{current_project}/models" in model_path:
                    project_models.append(model)
                else:
                    global_models.append(model)
            
            print(f"\n📈 模型分类统计:")
            print(f"   🌐 共享模型: {len(shared_models)}")
            print(f"   📦 项目模型: {len(project_models)}")
            print(f"   🌍 全局模型: {len(global_models)}")
            
            print(f"\n📦 项目 '{current_project}' 的模型:")
            if project_models:
                for model in project_models:
                    print(f"   ✅ {model}")
            else:
                print("   ⚠️  未找到项目特定的模型")
                
            # 验证是否找到了我们添加的测试模型
            test_model_found = False
            for model in project_models:
                if "trained_model_20250828_133309.pt" in str(model):
                    test_model_found = True
                    break
            
            if test_model_found:
                print("✅ 成功找到测试添加的训练模型")
                return True
            else:
                print("❌ 未找到测试添加的训练模型")
                return False
                
        except Exception as e:
            print(f"❌ AI模型管理器测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 测试过程失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_project_model_scanning()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 项目模型隔离修复验证成功！")
        print("✅ AI模型管理器能够正确扫描项目特定的训练模型")
    else:
        print("❌ 项目模型隔离修复验证失败")
        print("需要进一步调试和修复")
    print("=" * 60)

if __name__ == "__main__":
    main()