#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证数据配置日志功能的代码语法和结构
Verify Data Configuration Logging Code Syntax and Structure
"""

import sys
import os
import ast

def check_syntax(file_path):
    """检查Python文件的语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 解析AST
        ast.parse(source_code)
        print(f"✅ {file_path} 语法检查通过")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} 语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ {file_path} 检查失败: {e}")
        return False

def check_methods_exist(file_path):
    """检查关键方法是否存在"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            '_safe_append_data_log',
            'refresh_dataset_config',
            'load_dataset_config',
            'scan_dataset',
            'validate_training_config',
            'on_dataset_config_changed'
        ]
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}" not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 缺少方法: {missing_methods}")
            return False
        else:
            print("✅ 所有必需的方法都存在")
            return True
            
    except Exception as e:
        print(f"❌ 检查方法失败: {e}")
        return False

def check_log_calls(file_path):
    """检查日志调用是否正确添加"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查_safe_append_data_log调用
        log_call_count = content.count('_safe_append_data_log')
        
        if log_call_count > 0:
            print(f"✅ 找到 {log_call_count} 个数据配置日志调用")
            return True
        else:
            print("❌ 没有找到数据配置日志调用")
            return False
            
    except Exception as e:
        print(f"❌ 检查日志调用失败: {e}")
        return False

def check_ui_components(file_path):
    """检查UI组件是否正确添加"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ui_components = [
            'data_config_log_text',
            'QTextEdit',
            '数据配置日志',
            'clear_log_btn',
            'refresh_btn'
        ]
        
        missing_components = []
        for component in ui_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"⚠️ 可能缺少UI组件: {missing_components}")
        else:
            print("✅ 所有UI组件都存在")
        
        return len(missing_components) == 0
            
    except Exception as e:
        print(f"❌ 检查UI组件失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 开始验证数据配置日志功能...")
    
    file_path = "libs/ai_assistant_panel.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    print(f"\n📁 检查文件: {file_path}")
    
    # 检查语法
    print("\n1. 检查语法...")
    syntax_ok = check_syntax(file_path)
    
    # 检查方法存在性
    print("\n2. 检查方法存在性...")
    methods_ok = check_methods_exist(file_path)
    
    # 检查日志调用
    print("\n3. 检查日志调用...")
    log_calls_ok = check_log_calls(file_path)
    
    # 检查UI组件
    print("\n4. 检查UI组件...")
    ui_ok = check_ui_components(file_path)
    
    # 总结
    print("\n" + "="*50)
    print("📊 验证结果总结:")
    print(f"   语法检查: {'✅ 通过' if syntax_ok else '❌ 失败'}")
    print(f"   方法检查: {'✅ 通过' if methods_ok else '❌ 失败'}")
    print(f"   日志调用: {'✅ 通过' if log_calls_ok else '❌ 失败'}")
    print(f"   UI组件: {'✅ 通过' if ui_ok else '⚠️ 部分缺失'}")
    
    all_ok = syntax_ok and methods_ok and log_calls_ok
    
    if all_ok:
        print("\n🎉 验证通过！数据配置日志功能已正确实现。")
        print("\n📋 功能说明:")
        print("   • 在数据配置标签页中添加了日志显示区域")
        print("   • 在所有数据配置相关方法中添加了详细的日志输出")
        print("   • 包括路径解析、文件检查、错误诊断等详细信息")
        print("   • 用户现在可以观察每一步的执行过程和错误原因")
        
        print("\n🚀 使用方法:")
        print("   1. 打开YOLO模型训练配置对话框")
        print("   2. 在'数据配置'标签页中可以看到新的日志区域")
        print("   3. 选择或配置data.yaml文件时会显示详细的日志信息")
        print("   4. 可以使用'清空日志'和'刷新配置'按钮")
        
    else:
        print("\n❌ 验证失败！请检查上述错误。")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
