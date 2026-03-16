#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Work Memory Bridge 模块

实现进化引擎与 Work Memory 的桥接
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class WorkMemoryBridge:
    """
    Work Memory 桥接器
    
    用于进化引擎与 Work Memory 之间的协作
    """
    
    def __init__(self, evolution_engine, work_memory=None):
        """
        初始化 Work Memory 桥接器
        
        Args:
            evolution_engine: 进化引擎实例
            work_memory: Work Memory 实例（可选）
        """
        self.evolution = evolution_engine
        self.work_memory = work_memory
        
        self.logger = evolution_engine.logger if hasattr(evolution_engine, 'logger') else None
    
    def set_work_memory(self, work_memory):
        """
        设置 Work Memory 实例
        
        Args:
            work_memory: Work Memory 实例
        """
        self.work_memory = work_memory
    
    def sync_project_events(self) -> int:
        """
        同步项目事件到进化引擎
        
        Returns:
            同步的事件数量
        """
        if not self.work_memory:
            if self.logger:
                self.logger.warning("Work Memory 未设置")
            return 0
        
        try:
            # 获取所有项目
            projects = self.work_memory.list_projects()
            
            synced = 0
            for project in projects:
                try:
                    # 记录项目创建事件
                    self.evolution.pattern_miner.add_event({
                        'type': 'project_created',
                        'data': {
                            'project_id': project.get('id'),
                            'project_name': project.get('name'),
                            'status': project.get('status')
                        }
                    })
                    synced += 1
                except:
                    continue
            
            if self.logger:
                self.logger.info(f"同步了 {synced} 个项目事件到进化引擎")
            
            return synced
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"同步项目事件失败：{e}")
            return 0
    
    def sync_task_events(self) -> int:
        """
        同步任务事件到进化引擎
        
        Returns:
            同步的事件数量
        """
        if not self.work_memory:
            return 0
        
        try:
            # 获取所有任务
            tasks = self.work_memory.list_tasks()
            
            synced = 0
            for task in tasks:
                try:
                    # 记录任务事件
                    self.evolution.pattern_miner.add_event({
                        'type': f'task_{task.get("status", "unknown")}',
                        'data': {
                            'task_id': task.get('id'),
                            'task_title': task.get('title'),
                            'status': task.get('status'),
                            'priority': task.get('priority')
                        }
                    })
                    synced += 1
                except:
                    continue
            
            if self.logger:
                self.logger.info(f"同步了 {synced} 个任务事件到进化引擎")
            
            return synced
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"同步任务事件失败：{e}")
            return 0
    
    def analyze_work_patterns(self) -> Dict:
        """
        分析工作模式
        
        Returns:
            模式分析结果
        """
        # 同步事件
        self.sync_project_events()
        self.sync_task_events()
        
        # 挖掘模式
        patterns = self.evolution.pattern_miner.mine_patterns()
        
        # 分析工作相关模式
        work_patterns = []
        for pattern in patterns:
            if any(kw in pattern['pattern'] for kw in ['project', 'task', 'work']):
                work_patterns.append(pattern)
        
        return {
            'total_patterns': len(patterns),
            'work_patterns': work_patterns,
            'insights': self._generate_work_insights(work_patterns)
        }
    
    def _generate_work_insights(self, patterns: List[Dict]) -> List[Dict]:
        """
        生成工作洞察
        
        Args:
            patterns: 模式列表
        
        Returns:
            洞察列表
        """
        insights = []
        
        for pattern in patterns:
            if pattern['type'] == 'time_pattern':
                insights.append({
                    'type': 'time_insight',
                    'description': pattern['pattern'],
                    'suggestion': f'建议在{pattern["suggestion"]}安排重要工作'
                })
            elif pattern['type'] == 'behavior_pattern':
                if 'project' in pattern['pattern']:
                    insights.append({
                        'type': 'project_insight',
                        'description': pattern['pattern'],
                        'suggestion': '用户经常创建项目，可提供项目模板'
                    })
                elif 'task' in pattern['pattern']:
                    insights.append({
                        'type': 'task_insight',
                        'description': pattern['pattern'],
                        'suggestion': '优化任务管理流程'
                    })
        
        return insights
    
    def optimize_task_assignment(self) -> Dict:
        """
        优化任务分配
        
        Returns:
            优化建议
        """
        # 分析工作模式
        analysis = self.analyze_work_patterns()
        
        # 获取技能信息
        skills = self.evolution.skill_evolution.get_active_skills()
        
        # 生成优化建议
        suggestions = []
        
        # 基于时间模式的建议
        time_patterns = [p for p in analysis['work_patterns'] if p['type'] == 'time_pattern']
        if time_patterns:
            suggestions.append({
                'type': 'time_optimization',
                'description': '根据活跃时间优化任务安排',
                'patterns': time_patterns[:3]
            })
        
        # 基于技能的建议
        if skills:
            high_level_skills = [s for s in skills if s['level'] >= 3]
            if high_level_skills:
                suggestions.append({
                    'type': 'skill_optimization',
                    'description': '优先分配高技能等级任务',
                    'skills': high_level_skills[:5]
                })
        
        return {
            'analysis': analysis,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
    
    def on_project_completed(self, project_data: Dict):
        """
        项目完成回调
        
        Args:
            project_data: 项目数据
        """
        # 记录到进化引擎
        self.evolution.pattern_miner.add_event({
            'type': 'project_completed',
            'data': project_data
        })
        
        # 记录技能使用
        self.evolution.skill_evolution.record_skill_use(
            'project_management',
            success=True,
            feedback={'project': project_data}
        )
        
        if self.logger:
            self.logger.info(f"项目完成事件已记录：{project_data.get('name', 'unknown')}")
    
    def on_task_completed(self, task_data: Dict):
        """
        任务完成回调
        
        Args:
            task_data: 任务数据
        """
        # 记录到进化引擎
        self.evolution.pattern_miner.add_event({
            'type': 'task_completed',
            'data': task_data
        })
        
        # 记录技能使用
        self.evolution.skill_evolution.record_skill_use(
            'task_management',
            success=True,
            feedback={'task': task_data}
        )
        
        if self.logger:
            self.logger.info(f"任务完成事件已记录：{task_data.get('title', 'unknown')}")
    
    def get_work_statistics(self) -> Dict:
        """
        获取工作统计
        
        Returns:
            统计信息
        """
        if not self.work_memory:
            return {}
        
        try:
            # 获取 Work Memory 统计
            wm_stats = self.work_memory.get_stats()
            
            # 获取进化引擎统计
            evo_stats = self.evolution.get_status()
            
            return {
                'work_memory': wm_stats,
                'evolution_engine': evo_stats['modules'],
                'combined': {
                    'total_projects': wm_stats.get('projects', {}).get('active', 0),
                    'total_tasks': wm_stats.get('tasks', {}).get('pending', 0),
                    'active_skills': evo_stats['modules']['skill_evolution']['active_skills'],
                    'recognized_patterns': evo_stats['modules']['pattern_miner']['total_patterns']
                }
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"获取工作统计失败：{e}")
            return {}
