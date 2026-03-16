#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bridge 模块

进化引擎与其他系统的桥接层
"""

from .memory_bridge import MemoryBridge
from .work_memory_bridge import WorkMemoryBridge

__all__ = ['MemoryBridge', 'WorkMemoryBridge']
