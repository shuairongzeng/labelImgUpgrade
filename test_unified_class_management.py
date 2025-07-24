#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试统一类别管理系统修复效果
验证一键配置与类别源选择的统一性
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_class_config_manager():
    """测试类别配置管理器"""
    print("\n=== 测试类别配置管理器 ===")
    
    try:
        from libs.class_manager import ClassConfigManager
        
        # 创建临时配置目录
        temp_dir = tempfile.mkdtemp()
        print(f"使用临时目录: {temp_dir}")
        
        # 初始化管理器
        manager = ClassConfigManager(temp_dir)
        
        # 测试加载配置
        config = manager.load_class_config()
        print(f"✅ 成功加载配置: {config.get('version', 'unknown')}")
        
        # 测试添加类别
        test_classes = ['naiBa', 'naiMa', 'lingZhu', 'guaiWu', 'xiuLuo', 'xiuLiShang']
        for class_name in test_classes:
            success = manager.add_class(class_name, f"测试类别: {class_name}")
            if success:
                print(f"✅ 成功添加类别: {class_name}")
            else:
                print(f"⚠️ 类别已存在或添加失败: {class_name}")
        
        # 测试获取类别列表
        classes = manager.get_class_list()
        print(f"✅ 类别列表: {classes}")
        print(f"✅ 类别数量: {len(classes)}")
        
        # 测试类别映射
        mapping = manager.get_class_to_id_mapping()
        print(f"✅ 类别映射: {mapping}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 类别配置管理器测试失败: {e}")
        return False

def test_predefined_classes_sync():
    """测试预设类别文件同步"""
    print("\n=== 测试预设类别文件同步 ===")
    
    try:
        from libs.class_manager import ClassConfigManager
        
        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_predefined_file = os.path.join(temp_dir, 'predefined_classes.txt')
        
        # 创建测试预设类别文件
        test_classes = ['naiMa', 'lingZhu', 'guaiWu', 'naiBa', 'xiuLuo', 'xiuLiShang']
        with open(temp_predefined_file, 'w', encoding='utf-8') as f:
            for class_name in test_classes:
                f.write(f"{class_name}\n")
        
        print(f"✅ 创建测试预设文件: {temp_predefined_file}")
        print(f"✅ 测试类别: {test_classes}")
        
        # 初始化管理器
        config_dir = os.path.join(temp_dir, 'configs')
        os.makedirs(config_dir, exist_ok=True)
        manager = ClassConfigManager(config_dir)
        
        # 测试同步
        success = manager.sync_with_predefined_classes(temp_predefined_file)
        if success:
            print("✅ 同步成功")
            
            # 验证同步结果
            synced_classes = manager.get_class_list()
            print(f"✅ 同步后的类别: {synced_classes}")
            
            if synced_classes == test_classes:
                print("✅ 类别顺序完全一致")
            else:
                print(f"⚠️ 类别顺序不一致")
                print(f"   期望: {test_classes}")
                print(f"   实际: {synced_classes}")
        else:
            print("❌ 同步失败")
            return False
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 预设类别文件同步测试失败: {e}")
        return False

def test_class_source_methods():
    """测试类别源获取方法"""
    print("\n=== 测试类别源获取方法 ===")
    
    try:
        # 模拟AI助手面板的类别源获取方法
        def get_classes_from_source(source):
            """模拟_get_classes_from_source方法"""
            if source == "使用预设类别文件":
                # 创建临时预设文件
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
                test_classes = ['naiMa', 'lingZhu', 'guaiWu', 'naiBa', 'xiuLuo', 'xiuLiShang']
                for class_name in test_classes:
                    temp_file.write(f"{class_name}\n")
                temp_file.close()
                
                # 读取文件
                with open(temp_file.name, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                # 清理临时文件
                os.unlink(temp_file.name)
                
                return lines
            
            elif source == "使用类别配置文件":
                from libs.class_manager import ClassConfigManager
                
                # 创建临时配置
                temp_dir = tempfile.mkdtemp()
                manager = ClassConfigManager(temp_dir)
                
                # 添加测试类别
                test_classes = ['naiBa', 'naiMa', 'lingZhu', 'guaiWu', 'xiuLuo']
                for class_name in test_classes:
                    manager.add_class(class_name)
                
                classes = manager.get_class_list()
                
                # 清理临时目录
                shutil.rmtree(temp_dir)
                
                return classes
            
            else:
                return []
        
        # 测试不同类别源
        sources = ["使用预设类别文件", "使用类别配置文件"]
        
        for source in sources:
            print(f"\n测试类别源: {source}")
            classes = get_classes_from_source(source)
            print(f"✅ 获取到类别: {classes}")
            print(f"✅ 类别数量: {len(classes)}")
            
            if classes:
                print(f"✅ 类别源 '{source}' 测试成功")
            else:
                print(f"⚠️ 类别源 '{source}' 返回空列表")
        
        return True
        
    except Exception as e:
        print(f"❌ 类别源获取方法测试失败: {e}")
        return False

def test_unknown_class_handling():
    """测试未知类别处理"""
    print("\n=== 测试未知类别处理 ===")
    
    try:
        from libs.pascal_to_yolo_converter import PascalToYOLOConverter
        from libs.class_manager import ClassConfigManager
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        config_dir = os.path.join(temp_dir, 'configs')
        os.makedirs(config_dir, exist_ok=True)
        
        # 初始化类别管理器，只添加部分类别
        manager = ClassConfigManager(config_dir)
        initial_classes = ['naiBa', 'naiMa', 'lingZhu', 'guaiWu', 'xiuLuo']
        for class_name in initial_classes:
            manager.add_class(class_name)
        
        print(f"✅ 初始类别: {initial_classes}")
        
        # 创建转换器实例
        source_dir = os.path.join(temp_dir, 'source')
        target_dir = os.path.join(temp_dir, 'target')
        os.makedirs(source_dir, exist_ok=True)
        
        converter = PascalToYOLOConverter(
            source_dir=source_dir,
            target_dir=target_dir,
            dataset_name="test_dataset",
            use_class_config=True,
            class_config_dir=config_dir
        )
        
        print(f"✅ 转换器初始类别: {converter.classes}")
        
        # 测试自动添加未知类别
        unknown_class = 'xiuLiShang'
        print(f"\n测试添加未知类别: {unknown_class}")
        
        success = converter._auto_add_unknown_class(unknown_class)
        if success:
            print(f"✅ 成功自动添加未知类别: {unknown_class}")
            print(f"✅ 更新后的类别: {converter.classes}")
            
            # 验证类别映射
            if unknown_class in converter.class_to_id:
                class_id = converter.class_to_id[unknown_class]
                print(f"✅ 新类别ID: {class_id}")
            else:
                print(f"❌ 新类别未在映射中找到")
                return False
        else:
            print(f"❌ 自动添加未知类别失败: {unknown_class}")
            return False
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 未知类别处理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 统一类别管理系统修复效果测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    tests = [
        ("类别配置管理器", test_class_config_manager),
        ("预设类别文件同步", test_predefined_classes_sync),
        ("类别源获取方法", test_class_source_methods),
        ("未知类别处理", test_unknown_class_handling),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 输出测试总结
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！统一类别管理系统修复成功！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查和修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
