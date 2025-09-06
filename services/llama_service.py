import ollama
import json
import re
from typing import Dict, List, Optional

class LlamaService:
    def __init__(self, model_name="llama3.2:3b"):
        self.model_name = model_name
        self.client = ollama.Client()
        
        # Check if model is available
        try:
            models = self.client.list()
            available_models = [m['name'] for m in models['models']]
            if self.model_name not in available_models:
                print(f"⚠️  Model {self.model_name} not found. Pulling now...")
                self.client.pull(self.model_name)
                print(f"✅ Model {self.model_name} ready!")
        except Exception as e:
            print(f"❌ Error setting up Llama: {e}")
            print("Make sure Ollama is installed and running!")
    
    def generate_micro_tasks(self, context: Dict) -> List[Dict]:
        """Generate micro-tasks using local Llama model"""
        
        prompt = self._build_task_generation_prompt(context)
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{
                    'role': 'user', 
                    'content': prompt
                }],
                options={
                    'temperature': 0.7,
                    'top_k': 40,
                    'top_p': 0.9,
                    'num_predict': 500  # Limit response length
                }
            )
            
            # Parse the response to extract structured tasks
            response_text = response['message']['content']
            tasks = self._parse_llama_response(response_text)
            
            return tasks
            
        except Exception as e:
            print(f"Error generating tasks with Llama: {e}")
            # Fallback to pre-defined tasks
            return self._get_fallback_tasks(context)
    
    def _build_task_generation_prompt(self, context: Dict) -> str:
        """Build optimized prompt for local Llama model"""
        
        prompt = f"""You are an AI tutor creating micro-learning tasks for a student's {context['duration_minutes']}-minute break.

STUDENT INFO:
- Break: {context['duration_minutes']} minutes ({context['break_type']} break)
- Previous class: {context.get('previous_subject', 'None')}
- Next class: {context.get('next_subject', 'None')}
- Weak subjects: {', '.join(context.get('weak_subjects', []))}
- Interests: {', '.join(context.get('interests', []))}
- Learning style: {context.get('learning_style', 'visual')}

CREATE exactly 2 specific micro-tasks:

Task 1:
Title: [specific title]
Duration: [X minutes, must fit in {context['duration_minutes']} min total]
Subject: [subject name]
Description: [what student will do]
Steps: [3 specific action steps]
Why: [connection to their needs]

Task 2:
Title: [specific title]  
Duration: [X minutes, must fit in {context['duration_minutes']} min total]
Subject: [subject name]
Description: [what student will do]
Steps: [3 specific action steps]
Why: [connection to their needs]

Focus on bridging classes and addressing weak subjects through their interests."""

        return prompt
    
    def _parse_llama_response(self, response_text: str) -> List[Dict]:
        """Parse Llama response into structured tasks"""
        
        tasks = []
        
        # Split by "Task 1:" and "Task 2:"
        task_sections = re.split(r'Task \d+:', response_text)
        
        for i, section in enumerate(task_sections[1:], 1):  # Skip first empty section
            if not section.strip():
                continue
                
            task = self._extract_task_from_section(section, i)
            if task:
                tasks.append(task)
        
        # If parsing fails, try simpler approach
        if not tasks:
            tasks = self._simple_parse(response_text)
        
        return tasks[:2]  # Max 2 tasks
    
    def _extract_task_from_section(self, section: str, task_number: int) -> Dict:
        """Extract structured task data from text section"""
        
        task = {
            'task_id': f'task_{task_number}',
            'title': 'Learning Activity',
            'description': '',
            'duration_minutes': 10,
            'subject': 'general',
            'difficulty': 'medium',
            'instructions': [],
            'learning_objective': 'Practice key concepts',
            'engagement_hook': '',
            'connection': ''
        }
        
        lines = section.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract title
            if line.lower().startswith('title:'):
                task['title'] = line.split(':', 1)[1].strip()
            
            # Extract duration
            elif line.lower().startswith('duration:'):
                duration_text = line.split(':', 1)[1].strip()
                numbers = re.findall(r'\d+', duration_text)
                if numbers:
                    task['duration_minutes'] = int(numbers[0])
            
            # Extract subject
            elif line.lower().startswith('subject:'):
                task['subject'] = line.split(':', 1)[1].strip().lower()
            
            # Extract description
            elif line.lower().startswith('description:'):
                task['description'] = line.split(':', 1)[1].strip()
            
            # Extract steps/instructions
            elif line.lower().startswith('steps:'):
                steps_text = line.split(':', 1)[1].strip()
                # Try to parse numbered steps
                if steps_text:
                    task['instructions'] = [steps_text]
            
            elif re.match(r'^\d+\.', line):  # Numbered step
                task['instructions'].append(line)
            
            # Extract why/connection
            elif line.lower().startswith('why:'):
                task['connection'] = line.split(':', 1)[1].strip()
        
        return task
    
    def _simple_parse(self, text: str) -> List[Dict]:
        """Simple fallback parsing when structured parsing fails"""
        
        # Look for any task-like content
        sentences = text.split('.')
        
        tasks = []
        current_task = {
            'task_id': 'simple_task_1',
            'title': 'Quick Learning Activity',
            'description': 'Review and practice key concepts',
            'duration_minutes': 10,
            'subject': 'general',
            'difficulty': 'medium',
            'instructions': [
                'Review your recent notes',
                'Practice key concepts', 
                'Write down important points'
            ],
            'learning_objective': 'Reinforce learning',
            'connection': 'Prepare for upcoming classes'
        }
        
        # Try to extract meaningful content
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if meaningful_sentences:
            current_task['description'] = meaningful_sentences[0]
            if len(meaningful_sentences) > 1:
                current_task['instructions'] = meaningful_sentences[1:4]
        
        tasks.append(current_task)
        
        return tasks
    
    def _get_fallback_tasks(self, context: Dict) -> List[Dict]:
        """Intelligent fallback tasks when LLM fails"""
        
        duration = context.get('duration_minutes', 15)
        weak_subjects = context.get('weak_subjects', [])
        interests = context.get('interests', [])
        previous_subject = context.get('previous_subject', '')
        next_subject = context.get('next_subject', '')
        
        tasks = []
        
        # Task 1: Address weak subject if available
        if weak_subjects:
            subject = weak_subjects[0]
            task1 = {
                'task_id': 'fallback_task_1',
                'title': f'{subject.title()} Quick Review',
                'description': f'Review fundamental concepts in {subject} to strengthen understanding',
                'duration_minutes': min(duration // 2, 10),
                'subject': subject.lower(),
                'difficulty': 'easy',
                'instructions': [
                    f'Open your {subject} notes or textbook',
                    'Review the most challenging recent topic',
                    'Write down 3 key points you learned',
                    'Think of one question to ask your teacher'
                ],
                'learning_objective': f'Strengthen {subject} fundamentals',
                'engagement_hook': f'Build confidence in {subject}',
                'connection': f'This addresses your {subject} weakness and prepares you for future classes'
            }
            tasks.append(task1)
        
        # Task 2: Bridge classes or explore interests
        if previous_subject and next_subject and previous_subject != next_subject:
            # Create bridging task
            task2 = {
                'task_id': 'fallback_task_2', 
                'title': f'{previous_subject} to {next_subject} Bridge',
                'description': f'Connect concepts from {previous_subject} class to prepare for {next_subject}',
                'duration_minutes': duration - tasks[0]['duration_minutes'] if tasks else duration,
                'subject': 'interdisciplinary',
                'difficulty': 'medium',
                'instructions': [
                    f'Think about what you learned in {previous_subject}',
                    f'Consider how it might connect to {next_subject}',
                    'Write down any connections you notice',
                    'Prepare questions for your next teacher'
                ],
                'learning_objective': 'Connect learning across subjects',
                'engagement_hook': 'See the big picture of learning',
                'connection': f'Bridges your {previous_subject} and {next_subject} classes'
            }
            tasks.append(task2)
        
        elif interests:
            # Create interest-based task
            interest = interests[0]
            task2 = {
                'task_id': 'fallback_task_2',
                'title': f'{interest.title()} Learning Connection',
                'description': f'Explore how your interest in {interest} connects to your studies',
                'duration_minutes': duration - tasks[0]['duration_minutes'] if tasks else duration,
                'subject': 'interdisciplinary',
                'difficulty': 'medium',
                'instructions': [
                    f'Think about your interest in {interest}',
                    'Find connections to your recent classes',
                    'Look up one interesting fact online',
                    'Write down how this motivates your studies'
                ],
                'learning_objective': f'Connect {interest} interest with academics',
                'engagement_hook': 'Make learning personal and exciting',
                'connection': f'Uses your {interest} interest to boost motivation'
            }
            tasks.append(task2)
        
        # If no tasks created yet, create a generic one
        if not tasks:
            tasks.append({
                'task_id': 'fallback_generic',
                'title': 'Mindful Learning Review',
                'description': 'Take time to review and organize your recent learning',
                'duration_minutes': duration,
                'subject': 'general',
                'difficulty': 'easy',
                'instructions': [
                    'Look through your recent notes',
                    'Organize your thoughts',
                    'Identify what you learned today',
                    'Set an intention for your next class'
                ],
                'learning_objective': 'Consolidate recent learning',
                'engagement_hook': 'Prepare your mind for learning',
                'connection': 'Helps you be more focused in upcoming classes'
            })
        
        return tasks[:2]

    def test_model_connection(self) -> bool:
        """Test if Llama model is working"""
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': 'Say "Hello, I am ready to help with education!"'}],
                options={'num_predict': 50}
            )
            
            print(f"✅ Llama model test: {response['message']['content']}")
            return True
        except Exception as e:
            print(f"❌ Llama model test failed: {e}")
            return False
