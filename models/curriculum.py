from datetime import datetime
from typing import List, Dict, Optional

class MicroTask:
    def __init__(self, task_id: str, title: str, description: str, 
                 duration_minutes: int, difficulty: str, subject: str):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.duration_minutes = duration_minutes
        self.difficulty = difficulty  # easy, medium, hard
        self.subject = subject
        self.skills_targeted = []
        self.learning_objectives = []
        self.instructions = []
        self.resources = []
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'difficulty': self.difficulty,
            'subject': self.subject,
            'skills_targeted': self.skills_targeted,
            'learning_objectives': self.learning_objectives,
            'instructions': self.instructions,
            'resources': self.resources,
            'created_at': self.created_at.isoformat()
        }

class BreakPeriod:
    def __init__(self, start_time: str, end_time: str, duration_minutes: int, 
                 break_type: str = "short"):
        self.start_time = start_time
        self.end_time = end_time
        self.duration_minutes = duration_minutes
        self.break_type = break_type  # short, long, lunch
        self.previous_class = None
        self.next_class = None
        self.assigned_tasks = []
    
    def to_dict(self):
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_minutes': self.duration_minutes,
            'break_type': self.break_type,
            'previous_class': self.previous_class,
            'next_class': self.next_class,
            'assigned_tasks': [task.to_dict() if hasattr(task, 'to_dict') else task 
                             for task in self.assigned_tasks]
        }

class DailyCurriculum:
    def __init__(self, student_id: str, date: str):
        self.student_id = student_id
        self.date = date
        self.break_periods = []
        self.total_tasks = 0
        self.estimated_learning_time = 0
        self.subjects_covered = set()
        self.generated_at = datetime.now()
    
    def add_break_curriculum(self, break_period: BreakPeriod):
        """Add curriculum for a break period"""
        self.break_periods.append(break_period)
        self.total_tasks += len(break_period.assigned_tasks)
        self.estimated_learning_time += sum(
            task.duration_minutes if hasattr(task, 'duration_minutes') 
            else task.get('duration_minutes', 0) 
            for task in break_period.assigned_tasks
        )
        
        # Track subjects covered
        for task in break_period.assigned_tasks:
            subject = task.subject if hasattr(task, 'subject') else task.get('subject', '')
            if subject:
                self.subjects_covered.add(subject)
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'date': self.date,
            'break_periods': [bp.to_dict() for bp in self.break_periods],
            'total_tasks': self.total_tasks,
            'estimated_learning_time': self.estimated_learning_time,
            'subjects_covered': list(self.subjects_covered),
            'generated_at': self.generated_at.isoformat()
        }
