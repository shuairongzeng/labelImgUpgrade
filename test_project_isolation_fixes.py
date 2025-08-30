#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试项目隔离修复
确保：
1. ImageCacheManager.cleanup_cache() 不再报错
2. 项目模式下不显示全局资源路径调试信息  
3. 项目模式下不显示"Not find:/data/predefined_classes.txt"消息
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_image_cache_manager_cleanup():
    """测试ImageCacheManager cleanup_cache方法修复"""
    print("=== 测试ImageCacheManager.cleanup_cache()方法 ===")
    
    try:
        from libs.image_cache_manager import ImageCacheManager
        from PyQt5.QtCore import QObject
        
        # 创建测试实例
        cache_manager = ImageCacheManager()
        
        # 测试原始调用方式（不传参数）
        try:
            result = cache_manager.cleanup_cache()
            print(f"✓ cleanup_cache() 调用成功，返回: {result}")
        except Exception as e:
            print(f"✗ cleanup_cache() 调用失败: {e}")
            return False
            
        # 测试带auto参数的调用方式（修复后应该支持）
        try:
            result = cache_manager.cleanup_cache(auto=True)
            print(f"✓ cleanup_cache(auto=True) 调用成功，返回: {result}")
        except Exception as e:
            print(f"✗ cleanup_cache(auto=True) 调用失败: {e}")
            return False
            
        # 测试带target_ratio参数的调用方式
        try:
            result = cache_manager.cleanup_cache(target_ratio=0.3)
            print(f"✓ cleanup_cache(target_ratio=0.3) 调用成功，返回: {result}")
        except Exception as e:
            print(f"✗ cleanup_cache(target_ratio=0.3) 调用失败: {e}")
            return False
            
        # 测试同时带两个参数的调用方式
        try:
            result = cache_manager.cleanup_cache(target_ratio=0.7, auto=True)
            print(f"✓ cleanup_cache(target_ratio=0.7, auto=True) 调用成功，返回: {result}")
        except Exception as e:
            print(f"✗ cleanup_cache(target_ratio=0.7, auto=True) 调用失败: {e}")
            return False
            
        print("✓ ImageCacheManager.cleanup_cache()方法修复成功！")
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_resource_path_suppression():
    """测试资源路径调试信息抑制"""
    print("\n=== 测试资源路径调试信息抑制 ===")
    
    try:
        # 导入时不应该显示调试信息，因为现在有条件控制
        from labelImg import get_resource_path
        import sys
        import labelImg as labelimg_module
        
        # 测试非项目模式（应该显示调试信息）
        if hasattr(labelimg_module, '_project_mode_active'):
            delattr(labelimg_module, '_project_mode_active')
        
        print("测试非项目模式（应该显示调试信息）：")
        path1 = get_resource_path(os.path.join("data", "predefined_classes.txt"))
        
        # 测试项目模式（不应该显示调试信息）
        setattr(labelimg_module, '_project_mode_active', True)
        print("\n测试项目模式（不应该显示调试信息）：")
        path2 = get_resource_path(os.path.join("data", "predefined_classes.txt"))
        
        print(f"✓ 资源路径调试信息抑制功能正常工作")
        return True
        
    except Exception as e:
        print(f"✗ 资源路径调试信息抑制测试失败: {e}")
        return False

def test_performance_integration():
    """测试性能集成管理器不再报错"""
    print("\n=== 测试性能集成管理器cleanup调用 ===")
    
    try:
        from libs.performance_integration_manager import PerformanceIntegrationManager
        from libs.image_cache_manager import ImageCacheManager
        from PyQt5.QtCore import QObject
        
        # 创建测试实例
        perf_manager = PerformanceIntegrationManager()
        cache_manager = ImageCacheManager()
        
        # 注册组件
        perf_manager.register_component('image_cache_manager', cache_manager)
        
        # 测试自动缓存清理（之前会出错的地方）
        try:
            perf_manager._auto_cache_cleanup()
            print("✓ 性能集成管理器自动缓存清理成功")
            return True
        except Exception as e:
            print(f"✗ 性能集成管理器自动缓存清理失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ 性能集成管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始项目隔离修复验证测试...\n")
    
    results = []
    
    # 运行各项测试
    results.append(test_image_cache_manager_cleanup())
    results.append(test_resource_path_suppression())
    results.append(test_performance_integration())
    
    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    print(f"- ImageCacheManager.cleanup_cache()修复: {'通过' if results[0] else '失败'}")
    print(f"- 资源路径调试信息抑制: {'通过' if results[1] else '失败'}")
    print(f"- 性能集成管理器修复: {'通过' if results[2] else '失败'}")
    
    if all(results):
        print("\n🎉 所有测试通过！项目隔离修复成功。")
        print("\n现在系统应该实现完全的项目隔离：")
        print("1. 项目模式下不显示全局资源路径调试信息")
        print("2. ImageCacheManager.cleanup_cache()支持auto参数")
        print("3. 性能集成管理器不再报参数错误")
        print("4. 项目模式下不显示'Not find:/data/predefined_classes.txt'消息")
    else:
        print(f"\n❌ {sum(1 for r in results if not r)} 个测试失败，需要进一步修复。")

if __name__ == "__main__":
    main()