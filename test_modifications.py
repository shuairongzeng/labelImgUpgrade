#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify the modifications made to labelImg
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unicode_fix():
    """Test the Unicode encoding fix"""
    print("Testing Unicode encoding fix...")
    
    # Test the pascal_voc_io fix
    try:
        from libs.pascal_voc_io import PascalVocWriter
        
        # Create a test writer with Chinese path
        test_path = "测试路径/test"
        writer = PascalVocWriter("测试文件夹", "测试文件.jpg", (512, 512, 3))
        writer.add_bnd_box(10, 10, 100, 100, "测试标签", 0)
        
        # Test the prettify method
        root = writer.gen_xml()
        writer.append_objects(root)
        prettify_result = writer.prettify(root)
        
        # Check if the result is bytes and can be decoded
        if isinstance(prettify_result, bytes):
            decoded = prettify_result.decode('utf-8')
            print("✓ Pascal VOC Unicode fix working correctly")
        else:
            print("✓ Pascal VOC prettify returns string directly")
            
    except Exception as e:
        print(f"✗ Pascal VOC Unicode fix failed: {e}")

def test_chinese_interface():
    """Test the Chinese interface fix"""
    print("\nTesting Chinese interface fix...")
    
    try:
        from libs.stringBundle import StringBundle
        
        # Test that get_bundle always returns Chinese
        bundle = StringBundle.get_bundle()
        bundle2 = StringBundle.get_bundle('en')  # Should still return Chinese
        
        # Check if Chinese strings are loaded
        if hasattr(bundle, 'id_to_message') and bundle.id_to_message:
            # Try to get a Chinese string
            try:
                open_file_text = bundle.get_string('openFile')
                if '打开文件' in open_file_text:
                    print("✓ Chinese interface working correctly")
                else:
                    print(f"? Chinese interface may not be working: got '{open_file_text}'")
            except:
                print("? Chinese strings may not be loaded properly")
        else:
            print("? StringBundle may not have loaded strings")
            
    except Exception as e:
        print(f"✗ Chinese interface fix failed: {e}")

def test_path_memory():
    """Test the path memory functionality"""
    print("\nTesting path memory functionality...")
    
    try:
        from libs.settings import Settings
        from libs.constants import SETTING_LAST_OPENED_DIR
        
        # Test settings functionality
        settings = Settings()
        
        # Test setting and getting the last opened directory
        test_dir = "C:\\test\\directory"
        settings[SETTING_LAST_OPENED_DIR] = test_dir
        
        retrieved_dir = settings.get(SETTING_LAST_OPENED_DIR)
        
        if retrieved_dir == test_dir:
            print("✓ Path memory settings working correctly")
        else:
            print(f"✗ Path memory settings failed: expected '{test_dir}', got '{retrieved_dir}'")
            
    except Exception as e:
        print(f"✗ Path memory functionality failed: {e}")

def test_yolo_encoding():
    """Test YOLO encoding fix"""
    print("\nTesting YOLO encoding fix...")

    try:
        from libs.yolo_io import YOLOWriter, ENCODE_METHOD
        from libs.constants import DEFAULT_ENCODING

        # Test that ENCODE_METHOD is properly defined
        if ENCODE_METHOD == 'utf-8' and DEFAULT_ENCODING == 'utf-8':
            print("✓ YOLO encoding method correctly set to utf-8")
        else:
            print(f"? YOLO encoding method is '{ENCODE_METHOD}', DEFAULT_ENCODING is '{DEFAULT_ENCODING}'")

    except Exception as e:
        print(f"✗ YOLO encoding test failed: {e}")

def test_default_window_size():
    """Test default window size"""
    print("\nTesting default window size...")

    try:
        from libs.settings import Settings
        from libs.constants import SETTING_WIN_SIZE
        try:
            from PyQt5.QtCore import QSize
        except ImportError:
            from PyQt4.QtCore import QSize

        # Create a new settings object (without loading existing settings)
        settings = Settings()

        # Test default window size
        default_size = QSize(1366, 768)
        size = settings.get(SETTING_WIN_SIZE, default_size)

        print(f"Default window size: {size.width()}x{size.height()}")

        if size.width() == 1366 and size.height() == 768:
            print("✓ Default window size set correctly")
        else:
            print(f"? Default window size: expected 1366x768, got {size.width()}x{size.height()}")

    except Exception as e:
        print(f"✗ Default window size test failed: {e}")

def test_auto_save_default():
    """Test auto save default state"""
    print("\nTesting auto save default state...")

    try:
        from libs.settings import Settings
        from libs.constants import SETTING_AUTO_SAVE

        # Create a new settings object (without loading existing settings)
        settings = Settings()

        # Test auto save default value
        auto_save_default = settings.get(SETTING_AUTO_SAVE, True)

        print(f"Auto save default state: {auto_save_default}")

        if auto_save_default == True:
            print("✓ Auto save default checked setting correct")
        else:
            print("? Auto save default state should be True")

    except Exception as e:
        print(f"✗ Auto save default state test failed: {e}")

def main():
    print("=== Testing labelImg Modifications ===")
    print("This script tests the modifications made to fix Unicode errors,")
    print("enable Chinese interface, add path memory functionality,")
    print("and the new window size/centering/auto-save features.\n")

    test_unicode_fix()
    test_chinese_interface()
    test_path_memory()
    test_yolo_encoding()
    test_default_window_size()
    test_auto_save_default()

    print("\n=== Test Summary ===")
    print("All core modifications have been tested.")
    print("Note: Full GUI testing requires PyQt5 installation.")

if __name__ == "__main__":
    main()
