#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化引擎 v2.0 - 安装脚本

热插拔设计：
- 可独立安装
- 不依赖 OpenClaw 核心
- 可选功能扩展
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')

setup(
    name="evolution-engine",
    version="2.0.0",
    author="Lyra-eva",
    author_email="admin@evolution-engine.local",
    description="进化引擎 v2.0 - 热插拔 AI 进化系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/evolution-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
    install_requires=[],  # 最小依赖，只用标准库
    extras_require={
        "full": [
            "numpy>=1.20.0",      # 数值计算
            "networkx>=2.5.0",    # 图谱分析
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
        ]
    },
    entry_points={
        'console_scripts': [
            'evolution=evolution_engine.core:main',
        ],
    },
)
