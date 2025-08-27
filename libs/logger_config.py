# -*- coding: utf-8 -*-
"""
日志配置模块
为项目提供统一的日志记录配置
"""

import logging
import os
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    
    return logger


def setup_file_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    设置文件日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
        
    Returns:
        配置好的文件日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    
    return logger


def configure_root_logger(level: int = logging.WARNING):
    """
    配置根日志记录器
    
    Args:
        level: 根日志级别，默认为WARNING
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# 默认配置根日志记录器
configure_root_logger()