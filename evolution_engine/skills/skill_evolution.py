#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能进化模块

实现技能的自动进化和版本管理
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class SkillEvolution:
    """
    技能进化类
    
    用于管理和进化 AI 技能
    """
    
    def __init__(self, data_dir: str = None):
        """
        初始化技能进化
        
        Args:
            data_dir: 数据目录（默认 ~/.openclaw/workspace/evolution-data/skills）
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/evolution-data/skills")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'skill_versions'), exist_ok=True)
        
        # 技能数据
        self.skills: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        
        # 加载已有数据
        self._load_skills()
    
    def _load_skills(self):
        """加载技能数据"""
        skills_file = os.path.join(self.data_dir, 'skill_history.json')
        
        if os.path.exists(skills_file):
            with open(skills_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.skills = data.get('skills', {})
                self.history = data.get('history', [])
    
    def _save_skills(self):
        """保存技能数据"""
        skills_file = os.path.join(self.data_dir, 'skill_history.json')
        
        data = {
            'skills': self.skills,
            'history': self.history[-500:],  # 保留最近 500 条记录
            'updated_at': datetime.now().isoformat()
        }
        
        with open(skills_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_skill_use(self, skill_name: str, success: bool, 
                        feedback: Dict = None, context: Dict = None):
        """
        记录技能使用
        
        Args:
            skill_name: 技能名称
            success: 是否成功
            feedback: 反馈数据
            context: 上下文数据
        """
        # 初始化技能
        if skill_name not in self.skills:
            self.skills[skill_name] = {
                'name': skill_name,
                'level': 1,
                'experience': 0,
                'next_level_exp': 100,
                'accuracy': 0.5,
                'uses': 0,
                'successes': 0,
                'created_at': datetime.now().isoformat(),
                'last_evolved': None,
                'versions': []
            }
        
        skill = self.skills[skill_name]
        
        # 更新使用统计
        skill['uses'] += 1
        if success:
            skill['successes'] += 1
        
        # 计算准确率
        skill['accuracy'] = skill['successes'] / skill['uses']
        
        # 计算经验值
        exp_gain = self._calculate_experience_gain(success, feedback)
        skill['experience'] += exp_gain
        
        # 记录历史
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'skill_name': skill_name,
            'success': success,
            'feedback': feedback,
            'context': context,
            'exp_gain': exp_gain
        })
        
        # 检查是否升级
        if skill['experience'] >= skill['next_level_exp']:
            self.evolve_skill(skill_name)
        
        self._save_skills()
    
    def _calculate_experience_gain(self, success: bool, feedback: Dict = None) -> int:
        """
        计算经验值增益
        
        Args:
            success: 是否成功
            feedback: 反馈数据
        
        Returns:
            经验值
        """
        base_exp = 10 if success else 2
        
        # 反馈加成
        if feedback:
            if feedback.get('rating', 0) >= 4:
                base_exp += 5
            elif feedback.get('rating', 0) >= 3:
                base_exp += 2
        
        return base_exp
    
    def evolve_skill(self, skill_name: str) -> Dict:
        """
        进化技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            进化后的技能数据
        """
        if skill_name not in self.skills:
            return {}
        
        skill = self.skills[skill_name]
        
        # 升级
        skill['level'] += 1
        skill['experience'] = 0
        skill['next_level_exp'] = int(skill['next_level_exp'] * 1.5)
        skill['last_evolved'] = datetime.now().isoformat()
        
        # 计算新准确率（基于最近表现）
        recent_history = [
            h for h in self.history 
            if h.get('skill_name') == skill_name and 'success' in h
        ][-20:]
        
        if recent_history:
            recent_successes = sum(1 for h in recent_history if h.get('success', False))
            skill['accuracy'] = recent_successes / len(recent_history)
        
        # 保存版本（版本 1 是初始版本）
        version_data = {
            'version': skill['level'],
            'accuracy': skill['accuracy'],
            'evolved_at': skill['last_evolved'],
            'stats': {
                'uses': skill['uses'],
                'successes': skill['successes'],
                'experience': skill['experience']
            }
        }
        
        # 如果是第一次升级，添加版本 1
        if skill['level'] == 2 and len(skill['versions']) == 0:
            version_1 = {
                'version': 1,
                'accuracy': 0.5,
                'evolved_at': skill.get('created_at', datetime.now().isoformat()),
                'stats': {
                    'uses': 0,
                    'successes': 0,
                    'experience': 0
                }
            }
            skill['versions'].append(version_1)
        
        skill['versions'].append(version_data)
        
        # 保存版本文件
        self._save_version(skill_name, version_data)
        
        # 触发进化事件
        self._on_skill_evolved(skill)
        
        self._save_skills()
        
        return skill
    
    def _save_version(self, skill_name: str, version_data: Dict):
        """
        保存技能版本
        
        Args:
            skill_name: 技能名称
            version_data: 版本数据
        """
        version_file = os.path.join(
            self.data_dir, 
            'skill_versions',
            f"{skill_name}_v{version_data['version']}.json"
        )
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
    
    def _on_skill_evolved(self, skill: Dict):
        """
        技能进化回调
        
        Args:
            skill: 进化后的技能数据
        """
        # 记录进化事件
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'skill_evolved',
            'skill_name': skill['name'],
            'new_level': skill['level'],
            'accuracy': skill['accuracy']
        })
    
    def get_skill_version(self, skill_name: str, version: int = None) -> Optional[Dict]:
        """
        获取技能版本
        
        Args:
            skill_name: 技能名称
            version: 版本号（默认最新版本）
        
        Returns:
            版本数据
        """
        if skill_name not in self.skills:
            return None
        
        skill = self.skills[skill_name]
        
        if version is None:
            # 返回最新版本
            return skill['versions'][-1] if skill['versions'] else None
        
        # 返回指定版本
        for v in skill['versions']:
            if v['version'] == version:
                return v
        
        return None
    
    def compare_versions(self, skill_name: str, v1: int, v2: int) -> Dict:
        """
        比较版本
        
        Args:
            skill_name: 技能名称
            v1: 版本 1
            v2: 版本 2
        
        Returns:
            比较结果
        """
        version1 = self.get_skill_version(skill_name, v1)
        version2 = self.get_skill_version(skill_name, v2)
        
        if not version1 or not version2:
            return {'error': '版本不存在'}
        
        return {
            'skill_name': skill_name,
            'version_1': {
                'version': v1,
                'accuracy': version1['accuracy'],
                'evolved_at': version1['evolved_at']
            },
            'version_2': {
                'version': v2,
                'accuracy': version2['accuracy'],
                'evolved_at': version2['evolved_at']
            },
            'improvement': {
                'accuracy_diff': version2['accuracy'] - version1['accuracy'],
                'time_diff_days': 0  # Python 3.6 不支持 fromisoformat，暂时设为 0
            }
        }
    
    def get_skill_level(self, skill_name: str) -> int:
        """
        获取技能等级
        
        Args:
            skill_name: 技能名称
        
        Returns:
            技能等级
        """
        if skill_name not in self.skills:
            return 0
        
        return self.skills[skill_name]['level']
    
    def get_active_skills(self) -> List[Dict]:
        """
        获取活跃技能列表
        
        Returns:
            技能列表
        """
        return [
            {
                'name': skill['name'],
                'level': skill['level'],
                'accuracy': skill['accuracy'],
                'uses': skill['uses']
            }
            for skill in self.skills.values()
        ]
    
    def get_skill_statistics(self, skill_name: str) -> Dict:
        """
        获取技能统计
        
        Args:
            skill_name: 技能名称
        
        Returns:
            统计信息
        """
        if skill_name not in self.skills:
            return {}
        
        skill = self.skills[skill_name]
        
        return {
            'name': skill['name'],
            'level': skill['level'],
            'experience': skill['experience'],
            'next_level_exp': skill['next_level_exp'],
            'accuracy': skill['accuracy'],
            'uses': skill['uses'],
            'successes': skill['successes'],
            'versions': len(skill['versions']),
            'last_evolved': skill['last_evolved']
        }
    
    def export_skill_data(self) -> Dict:
        """
        导出技能数据
        
        Returns:
            技能数据
        """
        return {
            'skills': self.skills.copy(),
            'history': self.history[-100:],
            'statistics': {
                'total_skills': len(self.skills),
                'total_uses': sum(s['uses'] for s in self.skills.values()),
                'avg_level': sum(s['level'] for s in self.skills.values()) / len(self.skills) if self.skills else 0
            }
        }
    
    def reset_skill(self, skill_name: str) -> bool:
        """
        重置技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            是否成功
        """
        if skill_name not in self.skills:
            return False
        
        del self.skills[skill_name]
        self._save_skills()
        return True
