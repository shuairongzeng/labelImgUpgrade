#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证labelImg修改是否正确
"""

import os
import sys

def check_file_exists(filepath):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} 文件存在: {filepath}")
    return exists

def check_import():
    """检查导入是否正常"""
    try:
        sys.path.insert(0, 'libs')
        from pinyin_utils import process_label_text, has_chinese
        print("✓ 成功导入pinyin_utils模块")
        
        # 测试基本功能
        test_result = process_label_text("测试")
        print(f"✓ 中文转拼音测试: '测试' -> '{test_result}'")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def check_labelimg_modifications():
    """检查labelImg.py的修改"""
    try:
        with open('labelImg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('from libs.pinyin_utils import', '导入pinyin_utils模块'),
            ('self.predefined_classes_file =', '预设类文件路径存储'),
            ('process_label_text(text)', '中文转拼音处理'),
            ('save_predefined_classes()', '自动保存预设标签'),
            ('clear_labels_button', '清空标签按钮'),
            ('clear_predefined_classes_with_confirmation', '确认清空功能'),
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✓ 找到修改: {description}")
            else:
                print(f"✗ 未找到修改: {description}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"✗ 检查labelImg.py失败: {e}")
        return False

def main():
    """主验证函数"""
    print("=== labelImg改造验证 ===\n")
    
    print("1. 检查文件存在性:")
    file_checks = [
        check_file_exists('labelImg.py'),
        check_file_exists('libs/pinyin_utils.py'),
        check_file_exists('data/predefined_classes.txt'),
    ]
    
    print("\n2. 检查模块导入:")
    import_check = check_import()
    
    print("\n3. 检查代码修改:")
    modification_check = check_labelimg_modifications()
    
    print("\n=== 验证结果 ===")
    if all(file_checks) and import_check and modification_check:
        print("🎉 所有检查通过！改造成功完成。")
        print("\n使用说明:")
        print("1. 运行 python labelImg.py 启动程序")
        print("2. 输入中文标签时会自动转换为拼音")
        print("3. 新标签会自动保存到预设列表")
        print("4. 可以使用'清空预设标签'按钮清空所有预设标签")
        return True
    else:
        print("❌ 部分检查失败，请检查修改是否正确。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
