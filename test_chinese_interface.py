#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Chinese interface specifically
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chinese_strings():
    """Test if Chinese strings are properly loaded"""
    print("Testing Chinese interface...")
    
    try:
        # Import required modules
        from libs.stringBundle import StringBundle
        import libs.resources  # This loads the resources
        
        # Create string bundle - should force Chinese
        bundle = StringBundle.get_bundle()
        
        # Test some key strings
        test_strings = [
            ('openFile', '打开文件'),
            ('quit', '退出'),
            ('save', '保存'),
            ('openDir', '打开目录'),
            ('menu_file', '文件(&F)'),
            ('menu_edit', '编辑(&E)'),
            ('menu_view', '查看(&V)'),
            ('menu_help', '帮助(&H)')
        ]
        
        success_count = 0
        total_count = len(test_strings)
        
        for string_id, expected_chinese in test_strings:
            try:
                actual_value = bundle.get_string(string_id)
                if expected_chinese in actual_value or actual_value == expected_chinese:
                    print(f"✓ {string_id}: {actual_value}")
                    success_count += 1
                else:
                    print(f"✗ {string_id}: expected '{expected_chinese}', got '{actual_value}'")
            except Exception as e:
                print(f"✗ {string_id}: failed to get string - {e}")
        
        print(f"\nChinese interface test: {success_count}/{total_count} strings correct")
        
        if success_count == total_count:
            print("✓ Chinese interface is working perfectly!")
        elif success_count > total_count // 2:
            print("✓ Chinese interface is mostly working")
        else:
            print("✗ Chinese interface needs attention")
            
    except Exception as e:
        print(f"✗ Chinese interface test failed: {e}")

if __name__ == "__main__":
    test_chinese_strings()
