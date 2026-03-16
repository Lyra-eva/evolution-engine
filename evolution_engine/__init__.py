#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化引擎 v2.0 - 热插拔 AI 进化系统

核心功能：
- OODA 循环决策
- 事件记录与分析
- 技能进化
- 模式挖掘
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

from .logger import setup_logger
from .memory.capability_graph import CapabilityGraph
from .memory.pattern_miner import PatternMiner
from .skills.skill_evolution import SkillEvolution

__version__ = "2.1.0"
__all__ = ['EvolutionEngine', 'CapabilityGraph', 'PatternMiner', 'SkillEvolution']


class EvolutionEngine:
    """
    进化引擎核心类 v2.1
    
    热插拔设计：
    - 独立运行，不依赖 OpenClaw 核心
    - 可选启用/禁用
    - 数据隔离存储
    
    新增功能（v2.1）：
    - 能力图谱管理
    - 模式挖掘
    - 技能进化
    """
    
    def __init__(self, data_dir: str = None):
        """
        初始化进化引擎
        
        Args:
            data_dir: 数据目录（默认 ~/.openclaw/workspace/evolution-data）
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/evolution-data")
        
        self.data_dir = data_dir
        self.logger = setup_logger('evolution_engine', os.path.join(data_dir, 'evolution.log'))
        
        # 初始化目录
        self._init_directories()
        
        # 初始化子模块
        self.capability_graph = CapabilityGraph(os.path.join(data_dir, 'capabilities'))
        self.pattern_miner = PatternMiner(os.path.join(data_dir, 'patterns'))
        self.skill_evolution = SkillEvolution(os.path.join(data_dir, 'skills'))
        
        # 初始化统计
        self.stats = {
            'events_recorded': 0,
            'skills_evolved': 0,
            'patterns_mined': 0,
            'decisions_made': 0
        }
        
        # 加载配置
        self.config = self._load_config()
        
        self.logger.info(f"进化引擎 v{__version__} 已初始化：{data_dir}")
    
    def _init_directories(self):
        """初始化目录结构"""
        directories = [
            'events',
            'capabilities',
            'patterns',
            'skills',
            'backups',
            'logs'
        ]
        
        for dir_name in directories:
            dir_path = os.path.join(self.data_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_file = os.path.join(self.data_dir, 'config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                'enabled': True,
                'ooda_interval_seconds': 30,
                'auto_evolve': True,
                'max_events': 10000,
                'backup_enabled': True
            }
            
            # 保存默认配置
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            return default_config
    
    def record_event(self, event: Dict):
        """
        记录事件
        
        Args:
            event: 事件数据 {type, timestamp, data, ...}
        """
        timestamp = datetime.now().strftime('%Y-%m-%d')
        event_file = os.path.join(self.data_dir, 'events', f'{timestamp}.jsonl')
        
        event_record = {
            'timestamp': datetime.now().isoformat(),
            'type': event.get('type', 'unknown'),
            'data': event
        }
        
        with open(event_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event_record, ensure_ascii=False) + '\n')
        
        self.stats['events_recorded'] += 1
        self.logger.debug(f"事件已记录：{event.get('type', 'unknown')}")
    
    def ooda_loop(self, event: Dict) -> Dict:
        """
        OODA 循环决策
        
        Args:
            event: 输入事件
        
        Returns:
            决策结果
        """
        # Observe（观察）
        observation = self._observe(event)
        
        # Orient（调整）
        orientation = self._orient(observation)
        
        # Decide（决策）
        decision = self._decide(orientation)
        
        # Act（行动）
        action = self._act(decision)
        
        self.stats['decisions_made'] += 1
        
        return action
    
    def _observe(self, event: Dict) -> Dict:
        """观察阶段"""
        return {
            'event': event,
            'timestamp': datetime.now().isoformat(),
            'context': self._get_context()
        }
    
    def _orient(self, observation: Dict) -> Dict:
        """调整阶段"""
        return {
            'observation': observation,
            'patterns': self._match_patterns(observation),
            'capabilities': self._get_capabilities()
        }
    
    def _decide(self, orientation: Dict) -> Dict:
        """决策阶段"""
        # 简单决策逻辑（可扩展）
        return {
            'action': 'evolve',
            'priority': 'normal',
            'data': orientation
        }
    
    def _act(self, decision: Dict) -> Dict:
        """行动阶段"""
        # 记录技能使用
        if decision.get('action') == 'evolve':
            skill_name = decision.get('skill', 'general')
            self.skill_evolution.record_skill_use(
                skill_name,
                success=True,
                feedback={'decision': decision}
            )
        
        return {
            'status': 'executed',
            'decision': decision,
            'result': None
        }
    
    def _get_context(self) -> Dict:
        """获取上下文"""
        return {
            'recent_events': self._get_recent_events(10),
            'active_skills': self._get_active_skills()
        }
    
    def _match_patterns(self, observation: Dict) -> List:
        """模式匹配"""
        # TODO: 实现模式匹配逻辑
        return []
    
    def _get_capabilities(self) -> List:
        """获取能力列表"""
        # TODO: 实现能力获取
        return []
    
    def _get_recent_events(self, limit: int = 10) -> List:
        """获取最近事件"""
        events = []
        events_dir = os.path.join(self.data_dir, 'events')
        
        if os.path.exists(events_dir):
            # 读取最新的事件文件
            files = sorted(os.listdir(events_dir), reverse=True)
            for file in files[:1]:
                file_path = os.path.join(events_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        events.append(json.loads(line))
                        if len(events) >= limit:
                            return events
        
        return events
    
    def _get_active_skills(self) -> List:
        """获取活跃技能"""
        # TODO: 实现技能获取
        return []
    
    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            'version': __version__,
            'enabled': self.config.get('enabled', True),
            'data_dir': self.data_dir,
            'stats': self.stats,
            'config': self.config,
            'modules': {
                'capability_graph': self.capability_graph.get_statistics(),
                'pattern_miner': self.pattern_miner.get_pattern_stats(),
                'skill_evolution': {
                    'total_skills': len(self.skill_evolution.skills),
                    'active_skills': len(self.skill_evolution.get_active_skills())
                }
            }
        }
    
    def enable(self):
        """启用引擎"""
        self.config['enabled'] = True
        self._save_config()
        self.logger.info("进化引擎已启用")
    
    def disable(self):
        """禁用引擎"""
        self.config['enabled'] = False
        self._save_config()
        self.logger.info("进化引擎已禁用")
    
    def _save_config(self):
        """保存配置"""
        config_file = os.path.join(self.data_dir, 'config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def backup(self, backup_dir: str = None):
        """备份数据"""
        import shutil
        from datetime import datetime
        
        if backup_dir is None:
            backup_dir = os.path.join(self.data_dir, 'backups', datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份关键数据
        for dir_name in ['events', 'capabilities', 'patterns', 'skills']:
            src = os.path.join(self.data_dir, dir_name)
            if os.path.exists(src):
                shutil.copytree(src, os.path.join(backup_dir, dir_name))
        
        self.logger.info(f"数据已备份到：{backup_dir}")
        return backup_dir


# 便捷函数
def create_engine(data_dir: str = None) -> EvolutionEngine:
    """创建进化引擎实例"""
    return EvolutionEngine(data_dir)


def get_engine_status(data_dir: str = None) -> Dict:
    """获取引擎状态"""
    engine = EvolutionEngine(data_dir)
    return engine.get_status()
