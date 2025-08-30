#!/usr/bin/env python3
"""测试模型项目隔离"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, '.')

def test_model_isolation():
    """测试模型项目隔离功能"""
    try:
        print("开始测试模型项目隔离功能...")
        
        # 导入所需模块
        from libs.project_manager import get_project_manager
        from libs.ai_assistant.model_manager import ModelManager
        
        # 检查项目管理器
        manager = get_project_manager()
        if manager:
            current_project = manager.get_current_project()
            print(f"✓ 当前项目: {current_project}")
            
            if current_project:
                # 检查项目模型目录
                project_models_dir = Path(f"projects/{current_project}/models")
                print(f"✓ 项目模型目录: {project_models_dir}")
                print(f"✓ 项目模型目录存在: {project_models_dir.exists()}")
                
                if project_models_dir.exists():
                    model_files = list(project_models_dir.glob("*.pt"))
                    print(f"✓ 项目模型文件数量: {len(model_files)}")
                    for model_file in model_files:
                        print(f"  - {model_file}")
                else:
                    print("⚠️ 项目模型目录不存在，创建中...")
                    project_models_dir.mkdir(parents=True, exist_ok=True)
                    print(f"✓ 项目模型目录已创建: {project_models_dir}")
                
                # 测试模型扫描
                print("\n测试模型扫描...")
                model_manager = ModelManager()
                models = model_manager.scan_models()
                print(f"✓ 扫描到模型总数: {len(models)}")
                
                # 分类显示模型
                shared_models = [m for m in models if str(m).replace("\\", "/").startswith("projects/shared/models")]
                project_models = [m for m in models if str(m).replace("\\", "/").startswith(f"projects/{current_project}/models")]
                
                print(f"  - 共享模型: {len(shared_models)}")
                for model in shared_models:
                    print(f"    {model}")
                
                print(f"  - 项目模型: {len(project_models)}")
                for model in project_models:
                    print(f"    {model}")
                
            else:
                print("❌ 当前项目为空")
                return False
        else:
            print("❌ 项目管理器未初始化")
            return False
        
        print("\n✓ 模型项目隔离测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_copy_logic():
    """测试模型复制逻辑"""
    try:
        print("\n开始测试模型复制逻辑...")
        
        # 模拟训练完成后的模型复制
        from libs.project_manager import get_project_manager
        
        manager = get_project_manager()
        current_project = manager.get_current_project() if manager else None
        
        if current_project:
            models_dir = os.path.join(os.getcwd(), "projects", current_project, "models")
            print(f"✓ 项目模型目录路径: {models_dir}")
            print(f"✓ 项目模型目录存在: {os.path.exists(models_dir)}")
            
            # 确保目录存在
            os.makedirs(models_dir, exist_ok=True)
            print(f"✓ 确保项目模型目录存在")
            
        else:
            models_dir = os.path.join(os.getcwd(), "models", "custom")
            print(f"⚠️ 回退到全局模型目录: {models_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型复制逻辑测试失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_model_isolation()
    success2 = test_model_copy_logic()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1)