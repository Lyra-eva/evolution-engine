#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具
"""

import logging
import os
from pathlib import Path


def setup_logger(name: str, log_file: str = None, level: int = logging.INFO):
    """
    配置日志器
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径（可选）
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 创建 formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件 handler（可选）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
