#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模式挖掘模块

实现事件模式识别和挖掘
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class PatternMiner:
    """
    模式挖掘器
    
    用于识别和挖掘事件模式
    """
    
    def __init__(self, data_dir: str = None):
        """
        初始化模式挖掘器
        
        Args:
            data_dir: 数据目录（默认 ~/.openclaw/workspace/evolution-data/patterns）
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/evolution-data/patterns")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 模式数据
        self.patterns: List[Dict] = []
        self.event_history: List[Dict] = []
        
        # 加载已有数据
        self._load_patterns()
    
    def _load_patterns(self):
        """加载模式数据"""
        patterns_file = os.path.join(self.data_dir, 'patterns.json')
        
        if os.path.exists(patterns_file):
            with open(patterns_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.patterns = data.get('patterns', [])
                self.event_history = data.get('event_history', [])
    
    def _save_patterns(self):
        """保存模式数据"""
        patterns_file = os.path.join(self.data_dir, 'patterns.json')
        
        data = {
            'patterns': self.patterns,
            'event_history': self.event_history[-1000:],  # 保留最近 1000 条
            'updated_at': datetime.now().isoformat()
        }
        
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_event(self, event: Dict):
        """
        添加事件
        
        Args:
            event: 事件数据
        """
        event_record = {
            'timestamp': datetime.now().isoformat(),
            'data': event
        }
        
        self.event_history.append(event_record)
        
        # 定期挖掘模式（每 10 个事件）
        if len(self.event_history) % 10 == 0:
            self.mine_patterns()
        
        self._save_patterns()
    
    def mine_patterns(self, min_support: float = 0.1) -> List[Dict]:
        """
        挖掘模式
        
        Args:
            min_support: 最小支持度（0-1）
        
        Returns:
            识别的模式列表
        """
        if len(self.event_history) < 5:
            return []
        
        new_patterns = []
        
        # 1. 时间模式挖掘
        time_patterns = self._mine_time_patterns(min_support)
        new_patterns.extend(time_patterns)
        
        # 2. 行为模式挖掘
        behavior_patterns = self._mine_behavior_patterns(min_support)
        new_patterns.extend(behavior_patterns)
        
        # 3. 关联模式挖掘
        association_patterns = self._mine_association_patterns(min_support)
        new_patterns.extend(association_patterns)
        
        # 合并已有模式
        self._merge_patterns(new_patterns)
        
        return new_patterns
    
    def _mine_time_patterns(self, min_support: float) -> List[Dict]:
        """
        挖掘时间模式
        
        Args:
            min_support: 最小支持度
        
        Returns:
            时间模式列表
        """
        patterns = []
        
        # 按小时统计
        hour_counts = defaultdict(int)
        for event in self.event_history:
            try:
                timestamp = datetime.fromisoformat(event['timestamp'])
                hour = timestamp.hour
                hour_counts[hour] += 1
            except:
                continue
        
        # 识别高峰时段
        total_events = len(self.event_history)
        for hour, count in hour_counts.items():
            support = count / total_events
            if support >= min_support:
                patterns.append({
                    'type': 'time_pattern',
                    'pattern': f'活跃时段：{hour}:00-{hour+1}:00',
                    'confidence': support,
                    'occurrences': count,
                    'data': {'hour': hour},
                    'suggestion': f'{hour}:00 左右用户活跃度高'
                })
        
        # 按星期统计
        weekday_counts = defaultdict(int)
        for event in self.event_history:
            try:
                timestamp = datetime.fromisoformat(event['timestamp'])
                weekday = timestamp.weekday()
                weekday_counts[weekday] += 1
            except:
                continue
        
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        for weekday, count in weekday_counts.items():
            support = count / total_events
            if support >= min_support:
                patterns.append({
                    'type': 'time_pattern',
                    'pattern': f'活跃日期：{weekday_names[weekday]}',
                    'confidence': support,
                    'occurrences': count,
                    'data': {'weekday': weekday},
                    'suggestion': f'{weekday_names[weekday]}用户活跃度高'
                })
        
        return patterns
    
    def _mine_behavior_patterns(self, min_support: float) -> List[Dict]:
        """
        挖掘行为模式
        
        Args:
            min_support: 最小支持度
        
        Returns:
            行为模式列表
        """
        patterns = []
        
        # 统计事件类型频率
        type_counts = defaultdict(int)
        for event in self.event_history:
            event_type = event['data'].get('type', 'unknown')
            type_counts[event_type] += 1
        
        # 识别高频行为
        total_events = len(self.event_history)
        for event_type, count in type_counts.items():
            support = count / total_events
            if support >= min_support:
                patterns.append({
                    'type': 'behavior_pattern',
                    'pattern': f'高频行为：{event_type}',
                    'confidence': support,
                    'occurrences': count,
                    'data': {'event_type': event_type},
                    'suggestion': f'用户经常{event_type}'
                })
        
        # 识别行为序列
        if len(self.event_history) >= 3:
            sequence_counts = defaultdict(int)
            for i in range(len(self.event_history) - 2):
                seq = (
                    self.event_history[i]['data'].get('type', 'unknown'),
                    self.event_history[i+1]['data'].get('type', 'unknown'),
                    self.event_history[i+2]['data'].get('type', 'unknown')
                )
                sequence_counts[seq] += 1
            
            for seq, count in sequence_counts.items():
                support = count / total_events
                if support >= min_support:
                    patterns.append({
                        'type': 'behavior_pattern',
                        'pattern': f'行为序列：{" → ".join(seq)}',
                        'confidence': support,
                        'occurrences': count,
                        'data': {'sequence': seq},
                        'suggestion': f'用户经常按顺序执行：{seq}'
                    })
        
        return patterns
    
    def _mine_association_patterns(self, min_support: float) -> List[Dict]:
        """
        挖掘关联模式
        
        Args:
            min_support: 最小支持度
        
        Returns:
            关联模式列表
        """
        patterns = []
        
        # 统计事件共现
        co_occurrence = defaultdict(int)
        event_types = set()
        
        for event in self.event_history:
            event_type = event['data'].get('type', 'unknown')
            event_types.add(event_type)
        
        # 计算共现频率
        for i, event1 in enumerate(self.event_history):
            type1 = event1['data'].get('type', 'unknown')
            for j in range(i+1, min(i+5, len(self.event_history))):
                event2 = self.event_history[j]
                type2 = event2['data'].get('type', 'unknown')
                
                if type1 != type2:
                    pair = tuple(sorted([type1, type2]))
                    co_occurrence[pair] += 1
        
        # 识别强关联
        total_pairs = sum(co_occurrence.values())
        for pair, count in co_occurrence.items():
            support = count / total_pairs if total_pairs > 0 else 0
            if support >= min_support:
                patterns.append({
                    'type': 'association_pattern',
                    'pattern': f'关联事件：{pair[0]} ↔ {pair[1]}',
                    'confidence': support,
                    'occurrences': count,
                    'data': {'pair': pair},
                    'suggestion': f'{pair[0]}和{pair[1]}经常一起出现'
                })
        
        return patterns
    
    def _merge_patterns(self, new_patterns: List[Dict]):
        """
        合并新模式到已有模式
        
        Args:
            new_patterns: 新模式列表
        """
        for new_pattern in new_patterns:
            # 查找是否已存在相似模式
            found = False
            for existing in self.patterns:
                if (existing['type'] == new_pattern['type'] and
                    existing['pattern'] == new_pattern['pattern']):
                    # 更新已有模式
                    existing['confidence'] = (existing['confidence'] + new_pattern['confidence']) / 2
                    existing['occurrences'] += new_pattern['occurrences']
                    existing['last_seen'] = datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                # 添加新模式
                new_pattern['created_at'] = datetime.now().isoformat()
                new_pattern['last_seen'] = datetime.now().isoformat()
                self.patterns.append(new_pattern)
        
        # 保留高置信度模式
        self.patterns = [p for p in self.patterns if p['confidence'] >= 0.05]
        
        # 按置信度排序
        self.patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 限制模式数量
        self.patterns = self.patterns[:100]
    
    def match_pattern(self, event: Dict) -> List[Dict]:
        """
        匹配模式
        
        Args:
            event: 事件数据
        
        Returns:
            匹配的模式列表
        """
        matched = []
        event_type = event.get('type', 'unknown')
        
        for pattern in self.patterns:
            if pattern['type'] == 'behavior_pattern':
                if event_type in pattern['pattern']:
                    matched.append(pattern)
            elif pattern['type'] == 'association_pattern':
                if event_type in pattern['data'].get('pair', []):
                    matched.append(pattern)
            elif pattern['type'] == 'time_pattern':
                # 时间模式需要检查当前时间
                current_hour = datetime.now().hour
                if pattern['data'].get('hour') == current_hour:
                    matched.append(pattern)
        
        return matched
    
    def get_pattern_stats(self) -> Dict:
        """
        获取模式统计
        
        Returns:
            统计信息
        """
        if not self.patterns:
            return {
                'total_patterns': 0,
                'by_type': {},
                'avg_confidence': 0
            }
        
        by_type = defaultdict(int)
        for pattern in self.patterns:
            by_type[pattern['type']] += 1
        
        return {
            'total_patterns': len(self.patterns),
            'by_type': dict(by_type),
            'avg_confidence': sum(p['confidence'] for p in self.patterns) / len(self.patterns)
        }
    
    def export_patterns(self) -> List[Dict]:
        """
        导出模式
        
        Returns:
            模式列表
        """
        return self.patterns.copy()
    
    def clear_history(self):
        """清空事件历史"""
        self.event_history = []
        self._save_patterns()
