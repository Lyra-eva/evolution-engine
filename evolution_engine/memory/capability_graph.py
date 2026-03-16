#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能力图谱模块

实现 AI 能力图谱的构建、查询和导出
"""

import os
import json
from typing import Dict, List, Optional, Set
from datetime import datetime


class CapabilityGraph:
    """
    能力图谱类
    
    用于管理和查询 AI 能力图谱
    """
    
    def __init__(self, data_dir: str = None):
        """
        初始化能力图谱
        
        Args:
            data_dir: 数据目录（默认 ~/.openclaw/workspace/evolution-data/capabilities）
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/evolution-data/capabilities")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 图谱数据
        self.nodes: Dict[str, Dict] = {}  # 能力节点
        self.edges: Dict[str, Dict] = {}  # 能力关系
        
        # 加载已有数据
        self._load_graph()
    
    def _load_graph(self):
        """加载图谱数据"""
        graph_file = os.path.join(self.data_dir, 'graph.json')
        
        if os.path.exists(graph_file):
            with open(graph_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.nodes = data.get('nodes', {})
                self.edges = data.get('edges', {})
    
    def _save_graph(self):
        """保存图谱数据"""
        graph_file = os.path.join(self.data_dir, 'graph.json')
        
        data = {
            'nodes': self.nodes,
            'edges': self.edges,
            'updated_at': datetime.now().isoformat()
        }
        
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_capability(self, name: str, level: int = 1, 
                      description: str = '', metadata: Dict = None) -> bool:
        """
        添加能力节点
        
        Args:
            name: 能力名称
            level: 能力等级（1-10）
            description: 能力描述
            metadata: 元数据
        
        Returns:
            bool: 是否成功添加
        """
        if name in self.nodes:
            # 更新现有能力
            self.nodes[name]['level'] = max(self.nodes[name]['level'], level)
            self.nodes[name]['updated_at'] = datetime.now().isoformat()
            if description:
                self.nodes[name]['description'] = description
            if metadata:
                self.nodes[name]['metadata'].update(metadata)
        else:
            # 添加新能力
            self.nodes[name] = {
                'name': name,
                'level': level,
                'description': description,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        self._save_graph()
        return True
    
    def remove_capability(self, name: str) -> bool:
        """
        删除能力节点
        
        Args:
            name: 能力名称
        
        Returns:
            bool: 是否成功删除
        """
        if name not in self.nodes:
            return False
        
        # 删除节点
        del self.nodes[name]
        
        # 删除相关边
        edges_to_remove = [
            edge_id for edge_id, edge in self.edges.items()
            if edge['from'] == name or edge['to'] == name
        ]
        
        for edge_id in edges_to_remove:
            del self.edges[edge_id]
        
        self._save_graph()
        return True
    
    def add_relation(self, from_cap: str, to_cap: str, 
                    relation: str, weight: float = 1.0) -> bool:
        """
        添加能力关系
        
        Args:
            from_cap: 源能力
            to_cap: 目标能力
            relation: 关系类型 (requires/optimizes/enhances/blocks)
            weight: 关系权重（0-1）
        
        Returns:
            bool: 是否成功添加
        """
        # 验证能力存在
        if from_cap not in self.nodes or to_cap not in self.nodes:
            return False
        
        # 创建边 ID
        edge_id = f"{from_cap}__{to_cap}__{relation}"
        
        self.edges[edge_id] = {
            'from': from_cap,
            'to': to_cap,
            'relation': relation,
            'weight': weight,
            'created_at': datetime.now().isoformat()
        }
        
        self._save_graph()
        return True
    
    def get_capability(self, name: str) -> Optional[Dict]:
        """
        获取能力信息
        
        Args:
            name: 能力名称
        
        Returns:
            能力信息，不存在返回 None
        """
        return self.nodes.get(name)
    
    def get_capabilities(self, min_level: int = 0, 
                        max_level: int = 10) -> List[Dict]:
        """
        获取能力列表
        
        Args:
            min_level: 最小等级
            max_level: 最大等级
        
        Returns:
            能力列表
        """
        capabilities = []
        
        for name, cap in self.nodes.items():
            if min_level <= cap['level'] <= max_level:
                capabilities.append(cap.copy())
        
        # 按等级排序
        capabilities.sort(key=lambda x: x['level'], reverse=True)
        
        return capabilities
    
    def get_relations(self, capability_name: str) -> List[Dict]:
        """
        获取能力关系
        
        Args:
            capability_name: 能力名称
        
        Returns:
            关系列表
        """
        relations = []
        
        for edge_id, edge in self.edges.items():
            if edge['from'] == capability_name or edge['to'] == capability_name:
                relations.append(edge.copy())
        
        return relations
    
    def find_path(self, from_cap: str, to_cap: str) -> List[str]:
        """
        查找能力路径（BFS 算法）
        
        Args:
            from_cap: 起始能力
            to_cap: 目标能力
        
        Returns:
            能力路径列表
        """
        if from_cap not in self.nodes or to_cap not in self.nodes:
            return []
        
        # 构建邻接表
        adj: Dict[str, Set[str]] = {}
        for edge in self.edges.values():
            if edge['from'] not in adj:
                adj[edge['from']] = set()
            if edge['to'] not in adj:
                adj[edge['to']] = set()
            
            adj[edge['from']].add(edge['to'])
            adj[edge['to']].add(edge['from'])  # 无向图
        
        # BFS
        queue = [(from_cap, [from_cap])]
        visited = {from_cap}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == to_cap:
                return path
            
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # 无路径
    
    def get_dependencies(self, capability_name: str) -> List[str]:
        """
        获取能力依赖
        
        Args:
            capability_name: 能力名称
        
        Returns:
            依赖能力列表
        """
        dependencies = []
        
        for edge in self.edges.values():
            if edge['to'] == capability_name and edge['relation'] == 'requires':
                dependencies.append(edge['from'])
        
        return dependencies
    
    def get_enhancements(self, capability_name: str) -> List[str]:
        """
        获取能力提升关系
        
        Args:
            capability_name: 能力名称
        
        Returns:
            提升能力列表
        """
        enhancements = []
        
        for edge in self.edges.values():
            if edge['from'] == capability_name and edge['relation'] == 'enhances':
                enhancements.append(edge['to'])
        
        return enhancements
    
    def export_graph(self) -> Dict:
        """
        导出图谱
        
        Returns:
            图谱数据
        """
        return {
            'nodes': self.nodes.copy(),
            'edges': self.edges.copy(),
            'statistics': {
                'total_capabilities': len(self.nodes),
                'total_relations': len(self.edges),
                'avg_level': sum(n['level'] for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0
            }
        }
    
    def import_graph(self, data: Dict):
        """
        导入图谱
        
        Args:
            data: 图谱数据
        """
        self.nodes = data.get('nodes', {})
        self.edges = data.get('edges', {})
        self._save_graph()
    
    def get_statistics(self) -> Dict:
        """
        获取图谱统计信息
        
        Returns:
            统计信息
        """
        if not self.nodes:
            return {
                'total_capabilities': 0,
                'total_relations': 0,
                'avg_level': 0,
                'max_level': 0,
                'min_level': 0
            }
        
        levels = [n['level'] for n in self.nodes.values()]
        
        return {
            'total_capabilities': len(self.nodes),
            'total_relations': len(self.edges),
            'avg_level': sum(levels) / len(levels),
            'max_level': max(levels),
            'min_level': min(levels)
        }
    
    def visualize_text(self) -> str:
        """
        文本可视化
        
        Returns:
            文本图谱
        """
        lines = ["能力图谱:", "=" * 50]
        
        # 按等级分组
        by_level: Dict[int, List[str]] = {}
        for name, cap in self.nodes.items():
            level = cap['level']
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(name)
        
        # 输出
        for level in sorted(by_level.keys(), reverse=True):
            lines.append(f"\n等级 {level}:")
            for name in sorted(by_level[level]):
                deps = self.get_dependencies(name)
                deps_str = f" ← {', '.join(deps)}" if deps else ""
                lines.append(f"  • {name}{deps_str}")
        
        return '\n'.join(lines)
