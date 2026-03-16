#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Bridge 模块

实现进化引擎与 OpenClaw 原始记忆的桥接
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime


class MemoryBridge:
    """
    记忆桥接器
    
    用于进化引擎与 OpenClaw 原始记忆之间的数据同步和协作
    """
    
    def __init__(self, evolution_engine, openclaw_memory_dir: str = None):
        """
        初始化记忆桥接器
        
        Args:
            evolution_engine: 进化引擎实例
            openclaw_memory_dir: OpenClaw 记忆目录（默认 ~/.openclaw/workspace/memory）
        """
        self.evolution = evolution_engine
        
        if openclaw_memory_dir is None:
            openclaw_memory_dir = os.path.expanduser("~/.openclaw/workspace/memory")
        
        self.openclaw_dir = openclaw_memory_dir
        self.graph_db = os.path.join(openclaw_memory_dir, 'cognition', 'graph.db')
        
        self.logger = evolution_engine.logger if hasattr(evolution_engine, 'logger') else None
    
    def sync_events_to_evolution(self, limit: int = 100) -> int:
        """
        同步 OpenClaw 事件到进化引擎
        
        Args:
            limit: 最大同步数量
        
        Returns:
            同步的事件数量
        """
        if not os.path.exists(self.graph_db):
            if self.logger:
                self.logger.warning(f"OpenClaw graph.db 不存在：{self.graph_db}")
            return 0
        
        try:
            conn = sqlite3.connect(self.graph_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询最近的事件
            cursor.execute("""
                SELECT properties, created_at 
                FROM nodes 
                WHERE node_type = 'Event'
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            events = cursor.fetchall()
            conn.close()
            
            # 同步到进化引擎
            synced = 0
            for event in events:
                try:
                    properties = json.loads(event['properties'])
                    self.evolution.pattern_miner.add_event(properties)
                    synced += 1
                except:
                    continue
            
            if self.logger:
                self.logger.info(f"同步了 {synced} 个事件到进化引擎")
            
            return synced
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"同步事件失败：{e}")
            return 0
    
    def sync_patterns_to_memory(self) -> int:
        """
        同步进化引擎模式到 OpenClaw 记忆图谱
        
        Returns:
            同步的模式数量
        """
        if not os.path.exists(self.graph_db):
            return 0
        
        try:
            conn = sqlite3.connect(self.graph_db)
            cursor = conn.cursor()
            
            # 获取进化引擎的模式
            patterns = self.evolution.pattern_miner.export_patterns()
            
            synced = 0
            for pattern in patterns:
                try:
                    # 创建图谱节点
                    node_id = f"pattern_{pattern['type']}_{synced}"
                    properties = json.dumps({
                        'type': 'Pattern',
                        'pattern': pattern['pattern'],
                        'confidence': pattern['confidence'],
                        'occurrences': pattern['occurrences']
                    })
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO nodes (id, node_type, properties)
                        VALUES (?, ?, ?)
                    """, (node_id, 'Pattern', properties))
                    
                    synced += 1
                except:
                    continue
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.info(f"同步了 {synced} 个模式到 OpenClaw 记忆")
            
            return synced
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"同步模式失败：{e}")
            return 0
    
    def sync_capabilities_to_memory(self) -> int:
        """
        同步能力图谱到 OpenClaw 记忆图谱
        
        Returns:
            同步的能力数量
        """
        if not os.path.exists(self.graph_db):
            return 0
        
        try:
            conn = sqlite3.connect(self.graph_db)
            cursor = conn.cursor()
            
            # 获取能力图谱
            capabilities = self.evolution.capability_graph.get_capabilities()
            
            synced = 0
            for cap in capabilities:
                try:
                    node_id = f"capability_{cap['name']}"
                    properties = json.dumps({
                        'type': 'Capability',
                        'name': cap['name'],
                        'level': cap['level'],
                        'description': cap.get('description', '')
                    })
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO nodes (id, node_type, properties)
                        VALUES (?, ?, ?)
                    """, (node_id, 'Capability', properties))
                    
                    synced += 1
                except:
                    continue
            
            conn.commit()
            conn.close()
            
            if self.logger:
                self.logger.info(f"同步了 {synced} 个能力到 OpenClaw 记忆")
            
            return synced
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"同步能力失败：{e}")
            return 0
    
    def query_combined(self, query: str) -> Dict:
        """
        联合查询
        
        Args:
            query: 查询字符串
        
        Returns:
            查询结果
        """
        result = {
            'evolution_data': {},
            'openclaw_data': {},
            'combined_insights': []
        }
        
        # 查询进化引擎数据
        result['evolution_data'] = {
            'patterns': self.evolution.pattern_miner.export_patterns()[:10],
            'capabilities': self.evolution.capability_graph.get_capabilities()[:10],
            'skills': self.evolution.skill_evolution.get_active_skills()[:10]
        }
        
        # 查询 OpenClaw 记忆数据
        if os.path.exists(self.graph_db):
            try:
                conn = sqlite3.connect(self.graph_db)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 查询相关节点
                cursor.execute("""
                    SELECT node_type, properties 
                    FROM nodes 
                    WHERE properties LIKE ?
                    LIMIT 20
                """, (f'%{query}%',))
                
                nodes = cursor.fetchall()
                conn.close()
                
                result['openclaw_data'] = {
                    'nodes': [dict(node) for node in nodes]
                }
            except:
                result['openclaw_data'] = {'nodes': []}
        
        # 生成联合洞察
        result['combined_insights'] = self._generate_insights(result)
        
        return result
    
    def _generate_insights(self, query_result: Dict) -> List[Dict]:
        """
        生成联合洞察
        
        Args:
            query_result: 查询结果
        
        Returns:
            洞察列表
        """
        insights = []
        
        # 分析进化引擎数据
        patterns = query_result['evolution_data'].get('patterns', [])
        if patterns:
            insights.append({
                'type': 'pattern_insight',
                'description': f'识别到 {len(patterns)} 个模式',
                'data': patterns[:3]
            })
        
        # 分析能力数据
        capabilities = query_result['evolution_data'].get('capabilities', [])
        if capabilities:
            insights.append({
                'type': 'capability_insight',
                'description': f'当前有 {len(capabilities)} 个能力',
                'avg_level': sum(c['level'] for c in capabilities) / len(capabilities)
            })
        
        return insights
    
    def full_sync(self) -> Dict:
        """
        完整同步
        
        Returns:
            同步结果
        """
        result = {
            'events_synced': self.sync_events_to_evolution(),
            'patterns_synced': self.sync_patterns_to_memory(),
            'capabilities_synced': self.sync_capabilities_to_memory(),
            'timestamp': datetime.now().isoformat()
        }
        
        if self.logger:
            self.logger.info(f"完整同步完成：{result}")
        
        return result
