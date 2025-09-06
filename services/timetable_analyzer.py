from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models.curriculum import BreakPeriod

class TimetableAnalyzer:
    def __init__(self):
        self.break_threshold_minutes = 5  # Minimum break duration to consider
    
    def analyze_daily_schedule(self, timetable_dict: Dict) -> List[BreakPeriod]:
        """Analyze timetable and identify break periods"""
        
        if not timetable_dict or not timetable_dict.get('schedule'):
            return []
        
        schedule = timetable_dict['schedule']
        
        # Convert schedule to sorted list of time slots
        time_slots = []
        for time_range, class_info in schedule.items():
            start_time = self._parse_time(class_info['start_time'])
            end_time = self._parse_time(class_info['end_time'])
            time_slots.append({
                'start': start_time,
                'end': end_time,
                'subject': class_info['subject'],
                'info': class_info
            })
        
        # Sort by start time
        time_slots.sort(key=lambda x: x['start'])
        
        # Find breaks between classes
        breaks = []
        
        for i in range(len(time_slots) - 1):
            current_class = time_slots[i]
            next_class = time_slots[i + 1]
            
            # Calculate break duration
            break_start = current_class['end']
            break_end = next_class['start']
            duration_minutes = self._calculate_duration(break_start, break_end)
            
            if duration_minutes >= self.break_threshold_minutes:
                break_type = self._classify_break_type(duration_minutes)
                
                break_period = BreakPeriod(
                    start_time=self._time_to_string(break_start),
                    end_time=self._time_to_string(break_end),
                    duration_minutes=duration_minutes,
                    break_type=break_type
                )
                
                # Set context classes
                break_period.previous_class = current_class['info']
                break_period.next_class = next_class['info']
                
                breaks.append(break_period)
        
        return breaks
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime object"""
        try:
            # Handle formats like "9:00", "09:00", "9:00 AM"
            time_str = time_str.strip().upper()
            
            if 'AM' in time_str or 'PM' in time_str:
                return datetime.strptime(time_str, "%I:%M %p")
            else:
                return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            # Fallback parsing
            try:
                return datetime.strptime(time_str, "%H:%M")
            except:
                # Default to current time if parsing fails
                return datetime.now().replace(second=0, microsecond=0)
    
    def _time_to_string(self, dt: datetime) -> str:
        """Convert datetime to time string"""
        return dt.strftime("%H:%M")
    
    def _calculate_duration(self, start: datetime, end: datetime) -> int:
        """Calculate duration in minutes between two times"""
        duration = end - start
        return int(duration.total_seconds() / 60)
    
    def _classify_break_type(self, duration_minutes: int) -> str:
        """Classify break type based on duration"""
        if duration_minutes <= 15:
            return "short"
        elif duration_minutes <= 45:
            return "medium"  
        elif 60 <= duration_minutes <= 120:
            return "lunch"
        else:
            return "long"
    
    def get_subject_transitions(self, breaks: List[BreakPeriod]) -> List[Dict]:
        """Identify subject transitions that need bridging"""
        transitions = []
        
        for break_period in breaks:
            if break_period.previous_class and break_period.next_class:
                prev_subject = break_period.previous_class['subject']
                next_subject = break_period.next_class['subject']
                
                if prev_subject != next_subject:
                    transitions.append({
                        'break_time': f"{break_period.start_time}-{break_period.end_time}",
                        'from_subject': prev_subject,
                        'to_subject': next_subject,
                        'duration': break_period.duration_minutes,
                        'transition_type': self._get_transition_type(prev_subject, next_subject)
                    })
        
        return transitions
    
    def _get_transition_type(self, from_subject: str, to_subject: str) -> str:
        """Determine the type of subject transition"""
        
        # Define subject relationships
        related_subjects = {
            'mathematics': ['physics', 'chemistry', 'computer science'],
            'physics': ['mathematics', 'chemistry'],
            'chemistry': ['physics', 'biology', 'mathematics'],
            'biology': ['chemistry'],
            'english': ['literature', 'history'],
            'history': ['geography', 'social studies'],
        }
        
        from_lower = from_subject.lower()
        to_lower = to_subject.lower()
        
        # Check if subjects are related
        for subject, related in related_subjects.items():
            if subject in from_lower and any(r in to_lower for r in related):
                return "related"
            if subject in to_lower and any(r in from_lower for r in related):
                return "related"
        
        # Check for STEM to non-STEM transitions
        stem_subjects = ['mathematics', 'physics', 'chemistry', 'biology', 'computer']
        is_from_stem = any(s in from_lower for s in stem_subjects)
        is_to_stem = any(s in to_lower for s in stem_subjects)
        
        if is_from_stem and not is_to_stem:
            return "stem_to_humanities"
        elif not is_from_stem and is_to_stem:
            return "humanities_to_stem"
        elif is_from_stem and is_to_stem:
            return "stem_to_stem"
        else:
            return "unrelated"
