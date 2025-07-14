# -*- coding: utf-8 -*-
"""
中文转拼音工具模块
用于将中文标签转换为驼峰式拼音格式
"""

import re

def has_chinese(text):
    """
    检查文本是否包含中文字符
    
    Args:
        text (str): 要检查的文本
        
    Returns:
        bool: 如果包含中文字符返回True，否则返回False
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))

def chinese_to_pinyin(text):
    """
    将中文文本转换为驼峰式拼音格式
    
    Args:
        text (str): 包含中文的文本
        
    Returns:
        str: 转换后的驼峰式拼音文本
        
    Examples:
        >>> chinese_to_pinyin("称号")
        'chengHao'
        >>> chinese_to_pinyin("人物")
        'renWu'
        >>> chinese_to_pinyin("汽车")
        'qiChe'
    """
    if not text or not has_chinese(text):
        return text
    
    try:
        # 尝试导入pypinyin库
        from pypinyin import lazy_pinyin, Style
        
        # 获取拼音列表，不带声调
        pinyin_list = lazy_pinyin(text, style=Style.NORMAL)
        
        # 转换为驼峰格式：第一个词小写，后续词首字母大写
        if pinyin_list:
            result = pinyin_list[0].lower()
            for pinyin in pinyin_list[1:]:
                result += pinyin.capitalize()
            return result
        else:
            return text
            
    except ImportError:
        # 如果pypinyin库未安装，使用简单的映射表作为备用方案
        print("Warning: pypinyin library not found, using fallback mapping")
        return chinese_to_pinyin_fallback(text)
    except Exception as e:
        print(f"Error converting Chinese to pinyin: {e}")
        return text

def chinese_to_pinyin_fallback(text):
    """
    备用的中文转拼音方案，使用简单的映射表
    
    Args:
        text (str): 包含中文的文本
        
    Returns:
        str: 转换后的拼音文本
    """
    # 常用中文字符到拼音的映射表（部分示例）
    chinese_pinyin_map = {
        '人': 'ren', '物': 'wu', '车': 'che', '汽': 'qi',
        '称': 'cheng', '号': 'hao', '标': 'biao', '签': 'qian',
        '动': 'dong', '物': 'wu', '植': 'zhi', '建': 'jian',
        '筑': 'zhu', '食': 'shi', '品': 'pin', '工': 'gong',
        '具': 'ju', '电': 'dian', '器': 'qi', '家': 'jia',
        '具': 'ju', '衣': 'yi', '服': 'fu', '鞋': 'xie',
        '子': 'zi', '包': 'bao', '手': 'shou', '机': 'ji',
        '电': 'dian', '脑': 'nao', '书': 'shu', '本': 'ben',
        '桌': 'zhuo', '椅': 'yi', '床': 'chuang', '门': 'men',
        '窗': 'chuang', '墙': 'qiang', '地': 'di', '板': 'ban',
        '天': 'tian', '花': 'hua', '板': 'ban', '灯': 'deng',
        '水': 'shui', '杯': 'bei', '碗': 'wan', '盘': 'pan',
        '筷': 'kuai', '勺': 'shao', '刀': 'dao', '叉': 'cha',
        '猫': 'mao', '狗': 'gou', '鸟': 'niao', '鱼': 'yu',
        '树': 'shu', '花': 'hua', '草': 'cao', '山': 'shan',
        '水': 'shui', '河': 'he', '湖': 'hu', '海': 'hai',
        '天': 'tian', '空': 'kong', '云': 'yun', '雨': 'yu',
        '雪': 'xue', '风': 'feng', '太': 'tai', '阳': 'yang',
        '月': 'yue', '亮': 'liang', '星': 'xing', '星': 'xing'
    }
    
    result = ""
    pinyin_words = []
    
    for char in text:
        if char in chinese_pinyin_map:
            pinyin_words.append(chinese_pinyin_map[char])
        elif has_chinese(char):
            # 对于未映射的中文字符，使用字符的unicode编码作为标识
            pinyin_words.append(f"char{ord(char)}")
        else:
            # 非中文字符直接添加
            if pinyin_words:
                # 如果前面有拼音词，将当前字符添加到最后一个拼音词
                pinyin_words[-1] += char
            else:
                pinyin_words.append(char)
    
    # 转换为驼峰格式
    if pinyin_words:
        result = pinyin_words[0].lower()
        for word in pinyin_words[1:]:
            result += word.capitalize()
    
    return result if result else text

def process_label_text(text):
    """
    处理标签文本，如果包含中文则转换为拼音
    
    Args:
        text (str): 原始标签文本
        
    Returns:
        str: 处理后的标签文本
    """
    if not text:
        return text
    
    # 去除首尾空格
    text = text.strip()
    
    # 如果包含中文，转换为拼音
    if has_chinese(text):
        return chinese_to_pinyin(text)
    
    return text

# 测试函数
if __name__ == "__main__":
    test_cases = [
        "称号",
        "人物", 
        "汽车",
        "动物",
        "建筑",
        "食品",
        "工具",
        "电器",
        "衣服",
        "手机",
        "电脑",
        "桌子",
        "椅子",
        "hello",
        "test123",
        "中英mixed",
        ""
    ]
    
    print("中文转拼音测试:")
    for case in test_cases:
        result = process_label_text(case)
        print(f"'{case}' -> '{result}'")
