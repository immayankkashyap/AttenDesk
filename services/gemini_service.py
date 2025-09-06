import google.generativeai as genai
import json
from config import Config
from typing import Dict, List, Optional

class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_micro_tasks(self, context: Dict) -> List[Dict]:
        """Generate micro-tasks using Gemini AI"""
        
        prompt = self._build_task_generation_prompt(context)
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse the response to extract structured tasks
            tasks = self._parse_gemini_response(response.text)
            return tasks
            
        except Exception as e:
            print(f"Error generating tasks with Gemini: {e}")
            # Fallback to pre-defined tasks
            return self._get_fallback_tasks(context)
    
    def _build_task_generation_prompt(self, context: Dict) -> str:
        """Build intelligent prompt for Gemini"""
        
        prompt = f"""
You are an AI tutor creating personalized micro-learning tasks for a student.

STUDENT CONTEXT:
- Break Duration: {context['duration_minutes']} minutes
- Previous Class: {context.get('previous_subject', 'None')}
- Next Class: {context.get('next_subject', 'None')}
- Weak Subjects: {', '.join(context.get('weak_subjects', []))}
- Strong Subjects: {', '.join(context.get('strong_subjects', []))}
- Interests: {', '.join(context.get('interests', []))}
- Learning Style: {context.get('learning_style', 'visual')}
- Recent Poor Topics: {', '.join(context.get('recent_poor_topics', []))}

REQUIREMENTS:
1. Create exactly 2 micro-tasks that fit within {context['duration_minutes']} minutes
2. Tasks should be specific, actionable, and engaging
3. If there's a subject transition, create bridging activities
4. Address weak subjects while incorporating student interests
5. Match the student's {context.get('learning_style', 'visual')} learning style

OUTPUT FORMAT (JSON):
{{
    "tasks": [
        {{
            "title": "Specific task title",
            "description": "Clear description of what student will do",
            "duration_minutes": number,
            "subject": "subject name",
            "difficulty": "easy/medium/hard",
            "instructions": ["step 1", "step 2", "step 3"],
            "learning_objective": "What student will learn",
            "engagement_hook": "Why this is interesting/relevant",
            "connection": "How this connects to their classes/interests"
        }}
    ]
}}

Focus on making tasks that are immediately actionable and connect to the student's academic journey.
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Parse Gemini response into structured tasks"""
        try:
            # Try to extract JSON from the response
            import re
            
            # Find JSON block in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return parsed.get('tasks', [])
            else:
                # If no JSON found, parse text manually
                return self._parse_text_response(response_text)
                
        except json.JSONDecodeError:
            print("Could not parse JSON from Gemini response")
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, text: str) -> List[Dict]:
        """Parse text response when JSON parsing fails"""
        tasks = []
        
        # Simple text parsing logic
        lines = text.split('\n')
        current_task = {}
        
        for line in lines:
            line = line.strip()
            if 'title:' in line.lower() or line.startswith('1.') or line.startswith('2.'):
                if current_task:
                    tasks.append(current_task)
                current_task = {
                    'title': line.split(':', 1)[-1].strip() if ':' in line else line,
                    'description': '',
                    'duration_minutes': 10,
                    'subject': 'general',
                    'difficulty': 'medium',
                    'instructions': [],
                    'learning_objective': '',
                    'engagement_hook': '',
                    'connection': ''
                }
            elif 'description:' in line.lower():
                current_task['description'] = line.split(':', 1)[-1].strip()
            elif 'duration:' in line.lower():
                try:
                    current_task['duration_minutes'] = int(''.join(filter(str.isdigit, line)))
                except:
                    current_task['duration_minutes'] = 10
        
        if current_task:
            tasks.append(current_task)
            
        return tasks[:2]  # Return max 2 tasks
    
    def _get_fallback_tasks(self, context: Dict) -> List[Dict]:
        """Fallback tasks when Gemini API fails"""
        
        duration = context.get('duration_minutes', 15)
        weak_subjects = context.get('weak_subjects', [])
        interests = context.get('interests', [])
        
        fallback_tasks = [
            {
                'title': 'Quick Review Session',
                'description': f'Review key concepts from {weak_subjects[0] if weak_subjects else "recent classes"}',
                'duration_minutes': min(duration // 2, 10),
                'subject': weak_subjects[0] if weak_subjects else 'general',
                'difficulty': 'easy',
                'instructions': [
                    'Open your notes or textbook',
                    'Review the last topic covered',
                    'Create 3 quick summary points'
                ],
                'learning_objective': 'Reinforce recent learning',
                'engagement_hook': 'Quick confidence booster',
                'connection': 'Prepares you for upcoming classes'
            },
            {
                'title': 'Interest-Based Learning',
                'description': f'Explore how {interests[0] if interests else "your interests"} connect to academics',
                'duration_minutes': min(duration // 2, 15),
                'subject': 'interdisciplinary',
                'difficulty': 'medium',
                'instructions': [
                    'Think about your interests',
                    'Find connections to school subjects',
                    'Note down interesting facts'
                ],
                'learning_objective': 'Connect interests with academics',
                'engagement_hook': 'Make learning personal',
                'connection': 'Builds motivation for studying'
            }
        ]
        
        return fallback_tasks[:2]

    def generate_explanation(self, task: Dict, student_context: Dict) -> str:
        """Generate explanation for why this task was recommended"""
        
        prompt = f"""
Explain in 2-3 sentences why this learning task is perfect for this student right now:

TASK: {task['title']} - {task['description']}
STUDENT: Weak in {student_context.get('weak_subjects', [])}, interested in {student_context.get('interests', [])}, has {task['duration_minutes']} minutes

Make it personal and motivating.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return f"This task helps strengthen your {task['subject']} skills while connecting to your interests."
