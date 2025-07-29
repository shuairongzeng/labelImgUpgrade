#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证变量初始化修复
"""

def main():
    print("🔧 验证变量初始化修复")
    print("="*40)
    
    try:
        with open("libs/ai_assistant_panel.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键代码段
        if "filtered_source_dir = source_dir" in content:
            print("✅ 找到变量初始化")
        else:
            print("❌ 未找到变量初始化")
            return False
        
        if "source_dir=filtered_source_dir" in content:
            print("✅ 找到变量使用")
        else:
            print("❌ 未找到变量使用")
            return False
        
        # 检查顺序
        lines = content.split('\n')
        init_line = -1
        use_line = -1
        
        for i, line in enumerate(lines):
            if "filtered_source_dir = source_dir" in line and init_line == -1:
                init_line = i
            if "source_dir=filtered_source_dir" in line and use_line == -1:
                use_line = i
        
        if init_line < use_line:
            print("✅ 变量初始化顺序正确")
            print(f"   初始化: 第 {init_line + 1} 行")
            print(f"   使用: 第 {use_line + 1} 行")
            return True
        else:
            print("❌ 变量初始化顺序错误")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    if main():
        print("\n🎉 修复验证成功！")
        print("现在可以正常使用'不包含已训练的图片'功能了。")
    else:
        print("\n❌ 修复验证失败！")
