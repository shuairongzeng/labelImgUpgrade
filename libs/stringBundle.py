#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
if items were added in files in the resources/strings folder,
then execute "pyrcc5 resources.qrc -o resources.py" in the root directory
and execute "pyrcc5 ../resources.qrc -o resources.py" in the libs directory
"""
import re
import os
import sys
import locale
from libs.ustr import ustr

try:
    from PyQt5.QtCore import *
except ImportError:
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtCore import *


class StringBundle:

    __create_key = object()

    def __init__(self, create_key, locale_str):
        assert(create_key == StringBundle.__create_key), "StringBundle must be created using StringBundle.getBundle"
        self.id_to_message = {}
        paths = self.__create_lookup_fallback_list(locale_str)
        for path in paths:
            self.__load_bundle(path)

    @classmethod
    def get_bundle(cls, locale_str=None):
        # Force Chinese interface - always use zh-CN locale
        locale_str = 'zh-CN'
        return StringBundle(cls.__create_key, locale_str)

    def get_string(self, string_id):
        # 新增字符串的fallback定义
        fallback_strings = {
            'exportYOLO': '导出为YOLO数据集',
            'exportYOLODetail': '将Pascal VOC标注导出为YOLO格式数据集',
            'exportYOLODialog': '导出YOLO数据集',
            'selectExportDir': '选择导出目录',
            'datasetName': '数据集名称',
            'trainRatio': '训练集比例',
            'exportProgress': '导出进度',
            'exportComplete': '导出完成',
            'exportSuccess': 'YOLO数据集导出成功！',
            'exportError': '导出失败',
            'noAnnotations': '未找到标注文件',
            'invalidDirectory': '无效的目录路径',
            'processingFiles': '正在处理文件...',
            'copyingImages': '正在复制图片...',
            'generatingConfig': '正在生成配置文件...',
            'exportCancelled': '导出已取消'
        }

        if string_id in self.id_to_message:
            return self.id_to_message[string_id]
        elif string_id in fallback_strings:
            return fallback_strings[string_id]
        else:
            # 如果都找不到，返回字符串ID本身作为fallback
            print(f"Warning: Missing string id: {string_id}")
            return string_id

    def __create_lookup_fallback_list(self, locale_str):
        result_paths = []
        base_path = ":/strings"
        result_paths.append(base_path)
        if locale_str is not None:
            # Don't follow standard BCP47. Simple fallback
            tags = re.split('[^a-zA-Z]', locale_str)
            for tag in tags:
                last_path = result_paths[-1]
                result_paths.append(last_path + '-' + tag)

        return result_paths

    def __load_bundle(self, path):
        PROP_SEPERATOR = '='
        f = QFile(path)
        if f.exists():
            if f.open(QIODevice.ReadOnly | QFile.Text):
                text = QTextStream(f)
                text.setCodec("UTF-8")

            while not text.atEnd():
                line = ustr(text.readLine())
                key_value = line.split(PROP_SEPERATOR)
                key = key_value[0].strip()
                value = PROP_SEPERATOR.join(key_value[1:]).strip().strip('"')
                self.id_to_message[key] = value

            f.close()
