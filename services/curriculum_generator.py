from typing import Dict, List
from models.student import StudentProfile
from models.curriculum import DailyCurriculum, BreakPeriod, MicroTask
from services.timetable_analyzer import TimetableAnalyzer
from services.academic_analyzer import AcademicAnalyzer
from services.gemini_service import GeminiService
from datetime import datetime
import uuid

class CurriculumGenerator:
    def __init__(self):
        self.timetable_analyzer = TimetableAnalyzer()
        self.academic_analyzer = AcademicAnalyzer()
        self.gemini_service = GeminiService()
        
    def generate_daily_curriculum(self, student, timetable_dict=None, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Use section timetable if personal timetable not provided
        if timetable_dict is None:
            semester = getattr(student, 'semester', None)
            section = getattr(student, 'section', None)
            key = f"{semester}-{section}"
            timetable_dict = section_timetables.get(key)
            if timetable_dict is None:
                raise Exception("No timetable found for student's section")
        
        # Step 1: Analyze timetable to find break periods
        break_periods = self.timetable_analyzer.analyze_daily_schedule(timetable_dict)
        
        # Step 2: Analyze student's academic performance
        academic_analysis = self.academic_analyzer.analyze_student_performance(student)
        
        # Step 3: Generate curriculum for each break period
        daily_curriculum = DailyCurriculum(student.student_id, date)
        
        for break_period in break_periods:
            # Generate micro-tasks for this break
            tasks = self._generate_break_tasks(break_period, student, academic_analysis)
            
            # Convert tasks to MicroTask objects
            micro_tasks = []
            for task_data in tasks:
                micro_task = self._create_micro_task(task_data)
                micro_tasks.append(micro_task)
            
            # Assign tasks to break period
            break_period.assigned_tasks = micro_tasks
            
            # Add to daily curriculum
            daily_curriculum.add_break_curriculum(break_period)
        
        return daily_curriculum
    
    def _generate_break_tasks(self, break_period: BreakPeriod, 
                            student: StudentProfile, academic_analysis: Dict) -> List[Dict]:
        """Generate tasks for a specific break period"""
        
        # Build context for AI generation
        context = self._build_generation_context(break_period, student, academic_analysis)
        
        # Use Gemini to generate intelligent tasks
        tasks = self.gemini_service.generate_micro_tasks(context)
        
        # Post-process and validate tasks
        validated_tasks = self._validate_and_enhance_tasks(tasks, context)
        
        return validated_tasks
    
    def _build_generation_context(self, break_period: BreakPeriod, 
                                student: StudentProfile, academic_analysis: Dict) -> Dict:
        """Build comprehensive context for task generation"""
        
        context = {
            'duration_minutes': break_period.duration_minutes,
            'break_type': break_period.break_type,
            'student_id': student.student_id,
            'learning_style': student.learning_style,
            'interests': student.interests,
            'career_goals': student.career_goals,
            'weak_subjects': [ws['subject'] for ws in academic_analysis['weak_subjects']],
            'strong_subjects': [ss['subject'] for ss in academic_analysis['strong_subjects']],
            'improvement_areas': academic_analysis['improvement_areas'],
            'recent_poor_topics': []
        }
        
        # Add class context
        if break_period.previous_class:
            context['previous_subject'] = break_period.previous_class['subject']
            context['previous_topic'] = break_period.previous_class.get('topic', '')
        
        if break_period.next_class:
            context['next_subject'] = break_period.next_class['subject']
            context['next_topic'] = break_period.next_class.get('topic', '')
        
        # Add recent poor topics
        for area in academic_analysis['improvement_areas']:
            context['recent_poor_topics'].extend(area['recent_poor_topics'])
        
        return context
    
    def _validate_and_enhance_tasks(self, tasks: List[Dict], context: Dict) -> List[Dict]:
        """Validate and enhance generated tasks"""
        
        validated_tasks = []
        total_duration = 0
        max_duration = context['duration_minutes'] - 2  # Leave 2 minutes buffer
        
        for task in tasks:
            # Validate duration
            task_duration = task.get('duration_minutes', 10)
            if total_duration + task_duration <= max_duration:
                
                # Enhance task with additional metadata
                enhanced_task = self._enhance_task(task, context)
                validated_tasks.append(enhanced_task)
                total_duration += task_duration
                
            if len(validated_tasks) >= 2:  # Max 2 tasks per break
                break
        
        # If no tasks fit, create a shorter task
        if not validated_tasks and max_duration > 5:
            fallback_task = self._create_fallback_task(max_duration, context)
            validated_tasks.append(fallback_task)
        
        return validated_tasks
    
    def _enhance_task(self, task: Dict, context: Dict) -> Dict:
        """Enhance task with additional metadata and personalization"""
        
        enhanced = task.copy()
        
        # Add unique ID
        enhanced['task_id'] = str(uuid.uuid4())
        
        # Add personalization explanation
        enhanced['personalization_reason'] = self._get_personalization_reason(task, context)
        
        # Add difficulty adjustment based on student performance
        enhanced['difficulty'] = self._adjust_difficulty(task, context)
        
        # Add engagement elements
        enhanced['gamification'] = self._add_gamification_elements(task, context)
        
        # Add success metrics
        enhanced['success_criteria'] = self._define_success_criteria(task)
        
        return enhanced
    
    def _get_personalization_reason(self, task: Dict, context: Dict) -> str:
        """Generate explanation for task personalization"""
        
        reasons = []
        
        # Check weak subject alignment
        task_subject = task.get('subject', '').lower()
        weak_subjects = [ws.lower() for ws in context.get('weak_subjects', [])]
        
        if task_subject in weak_subjects:
            reasons.append(f"targets your {task_subject} weakness")
        
        # Check interest alignment
        interests = [interest.lower() for interest in context.get('interests', [])]
        task_content = (task.get('title', '') + ' ' + task.get('description', '')).lower()
        
        for interest in interests:
            if interest in task_content:
                reasons.append(f"connects to your interest in {interest}")
                break
        
        # Check class transition
        if context.get('previous_subject') and context.get('next_subject'):
            if task_subject in context['previous_subject'].lower() or task_subject in context['next_subject'].lower():
                reasons.append(f"bridges {context['previous_subject']} and {context['next_subject']}")
        
        if reasons:
            return "This task " + " and ".join(reasons) + "."
        else:
            return "This task matches your current learning needs."
    
    def _adjust_difficulty(self, task: Dict, context: Dict) -> str:
        """Adjust task difficulty based on student performance"""
        
        original_difficulty = task.get('difficulty', 'medium')
        task_subject = task.get('subject', '').lower()
        
        # Check student performance in this subject
        weak_subjects = [ws.lower() for ws in context.get('weak_subjects', [])]
        strong_subjects = [ss.lower() for ss in context.get('strong_subjects', [])]
        
        if task_subject in weak_subjects:
            # Make it easier for weak subjects
            if original_difficulty == 'hard':
                return 'medium'
            elif original_difficulty == 'medium':
                return 'easy'
        elif task_subject in strong_subjects:
            # Make it more challenging for strong subjects
            if original_difficulty == 'easy':
                return 'medium'
            elif original_difficulty == 'medium':
                return 'hard'
        
        return original_difficulty
    
    def _add_gamification_elements(self, task: Dict, context: Dict) -> Dict:
        """Add gamification elements to increase engagement"""
        
        gamification = {
            'points': self._calculate_points(task),
            'badges': self._get_potential_badges(task, context),
            'streak_bonus': context['duration_minutes'] > 20,  # Bonus for long breaks
            'challenge_level': task.get('difficulty', 'medium')
        }
        
        return gamification
    
    def _calculate_points(self, task: Dict) -> int:
        """Calculate points based on task characteristics"""
        
        base_points = task.get('duration_minutes', 10)
        difficulty_multiplier = {
            'easy': 1.0,
            'medium': 1.5,
            'hard': 2.0
        }
        
        multiplier = difficulty_multiplier.get(task.get('difficulty', 'medium'), 1.5)
        return int(base_points * multiplier)
    
    def _get_potential_badges(self, task: Dict, context: Dict) -> List[str]:
        """Define badges that can be earned"""
        
        badges = []
        
        # Subject-specific badges
        subject = task.get('subject', '').lower()
        if subject in context.get('weak_subjects', []):
            badges.append(f"{subject.title()} Improver")
        
        # Duration badges
        duration = task.get('duration_minutes', 0)
        if duration >= 20:
            badges.append("Deep Learner")
        elif duration <= 10:
            badges.append("Quick Thinker")
        
        # Interest badges
        interests = context.get('interests', [])
        task_content = (task.get('title', '') + ' ' + task.get('description', '')).lower()
        
        for interest in interests:
            if interest.lower() in task_content:
                badges.append(f"{interest.title()} Explorer")
                break
        
        return badges
    
    def _define_success_criteria(self, task: Dict) -> List[str]:
        """Define clear success criteria for the task"""
        
        criteria = []
        
        # Time-based criteria
        criteria.append(f"Complete within {task.get('duration_minutes', 10)} minutes")
        
        # Task-specific criteria
        if 'instructions' in task and task['instructions']:
            criteria.append(f"Follow all {len(task['instructions'])} steps")
        
        # Learning objective criteria
        if 'learning_objective' in task:
            criteria.append(f"Achieve: {task['learning_objective']}")
        
        # Engagement criteria
        criteria.append("Stay focused throughout the activity")
        
        return criteria
    
    def _create_fallback_task(self, duration_minutes: int, context: Dict) -> Dict:
        """Create a simple fallback task when generation fails"""
        
        weak_subjects = context.get('weak_subjects', ['general'])
        subject = weak_subjects[0] if weak_subjects else 'general'
        
        return {
            'task_id': str(uuid.uuid4()),
            'title': f'Quick {subject.title()} Review',
            'description': f'Spend {duration_minutes} minutes reviewing your {subject} notes or textbook',
            'duration_minutes': duration_minutes,
            'subject': subject,
            'difficulty': 'easy',
            'instructions': [
                'Get your notes or textbook',
                'Review the most recent topic',
                'Write down 2-3 key points',
                'Think about questions you have'
            ],
            'learning_objective': f'Reinforce recent {subject} learning',
            'engagement_hook': 'Quick confidence boost before next class',
            'connection': 'Prepares you for upcoming classes',
            'personalization_reason': f'Focuses on your {subject} studies',
            'gamification': {
                'points': duration_minutes,
                'badges': ['Quick Reviewer'],
                'streak_bonus': False,
                'challenge_level': 'easy'
            },
            'success_criteria': [
                f'Complete within {duration_minutes} minutes',
                'Review at least one topic',
                'Note key concepts'
            ]
        }
    
    def _create_micro_task(self, task_data: Dict) -> MicroTask:
        """Convert task data dictionary to MicroTask object"""
        
        micro_task = MicroTask(
            task_id=task_data.get('task_id', str(uuid.uuid4())),
            title=task_data.get('title', 'Learning Task'),
            description=task_data.get('description', ''),
            duration_minutes=task_data.get('duration_minutes', 10),
            difficulty=task_data.get('difficulty', 'medium'),
            subject=task_data.get('subject', 'general')
        )
        
        # Add additional attributes
        micro_task.skills_targeted = task_data.get('skills_targeted', [])
        micro_task.learning_objectives = [task_data.get('learning_objective', 'Learn something new')]
        micro_task.instructions = task_data.get('instructions', [])
        micro_task.resources = task_data.get('resources', [])
        
        return micro_task
