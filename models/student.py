from datetime import datetime
from typing import Dict, List, Optional

class StudentProfile:
    def __init__(self, student_id: str, name: str, grade: str, section: str):
        self.student_id = student_id
        self.name = name
        self.grade = grade
        self.section = section
        self.interests = []
        self.career_goals = []
        self.learning_style = "visual"  # visual, auditory, kinesthetic
        self.academic_performance = {}
        self.skills = {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'grade': self.grade,
            'section': self.section,
            'interests': self.interests,
            'career_goals': self.career_goals,
            'learning_style': self.learning_style,
            'academic_performance': self.academic_performance,
            'skills': self.skills,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    def update_performance(self, subject: str, score: float, test_type: str = "exam"):
        """Update academic performance for a subject"""
        if subject not in self.academic_performance:
            self.academic_performance[subject] = []
        
        self.academic_performance[subject].append({
            'score': score,
            'test_type': test_type,
            'date': datetime.now().isoformat()
        })
        self.last_updated = datetime.now()
    
    def get_average_score(self, subject: str) -> float:
        """Get average score for a subject"""
        if subject not in self.academic_performance:
            return 0.0
        
        scores = [entry['score'] for entry in self.academic_performance[subject]]
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_weak_subjects(self, threshold: float = 60.0) -> List[str]:
        """Get subjects where student performance is below threshold"""
        weak_subjects = []
        for subject in self.academic_performance:
            avg_score = self.get_average_score(subject)
            if avg_score < threshold:
                weak_subjects.append(subject)
        return weak_subjects
    
    def get_strong_subjects(self, threshold: float = 80.0) -> List[str]:
        """Get subjects where student excels"""
        strong_subjects = []
        for subject in self.academic_performance:
            avg_score = self.get_average_score(subject)
            if avg_score >= threshold:
                strong_subjects.append(subject)
        return strong_subjects

class Timetable:
    def __init__(self, student_id: str, date: str):
        self.student_id = student_id
        self.date = date
        self.schedule = {}  # time_slot: {subject, teacher, room}
        
    def add_class(self, start_time: str, end_time: str, subject: str, 
                  teacher: str = "", room: str = "", topic: str = ""):
        """Add a class to the timetable"""
        time_slot = f"{start_time}-{end_time}"
        self.schedule[time_slot] = {
            'subject': subject,
            'teacher': teacher,
            'room': room,
            'topic': topic,
            'start_time': start_time,
            'end_time': end_time
        }
    
    def get_schedule_list(self):
        """Get schedule as sorted list"""
        return sorted(self.schedule.items(), key=lambda x: x[1]['start_time'])
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'date': self.date,
            'schedule': self.schedule
        }
