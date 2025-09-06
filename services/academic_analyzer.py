from typing import Dict, List, Tuple
from models.student import StudentProfile
from config import Config

class AcademicAnalyzer:
    def __init__(self):
        self.weak_threshold = Config.WEAK_SUBJECT_THRESHOLD
        self.strong_threshold = Config.STRONG_SUBJECT_THRESHOLD
    
    def analyze_student_performance(self, student: StudentProfile) -> Dict:
        """Comprehensive analysis of student's academic performance"""
        
        analysis = {
            'student_id': student.student_id,
            'weak_subjects': [],
            'strong_subjects': [],
            'improvement_areas': [],
            'learning_gaps': [],
            'performance_trends': {},
            'recommendations': []
        }
        
        # Analyze each subject
        for subject in student.academic_performance:
            avg_score = student.get_average_score(subject)
            trend = self._calculate_trend(student.academic_performance[subject])
            
            analysis['performance_trends'][subject] = {
                'average_score': avg_score,
                'trend': trend,
                'latest_score': self._get_latest_score(student.academic_performance[subject])
            }
            
            # Categorize subjects
            if avg_score < self.weak_threshold:
                analysis['weak_subjects'].append({
                    'subject': subject,
                    'score': avg_score,
                    'trend': trend
                })
            elif avg_score >= self.strong_threshold:
                analysis['strong_subjects'].append({
                    'subject': subject,
                    'score': avg_score,
                    'trend': trend
                })
        
        # Identify specific improvement areas
        analysis['improvement_areas'] = self._identify_improvement_areas(student)
        
        # Generate learning gap analysis
        analysis['learning_gaps'] = self._analyze_learning_gaps(student)
        
        # Create actionable recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis, student)
        
        return analysis
    
    def _calculate_trend(self, performance_history: List[Dict]) -> str:
        """Calculate performance trend (improving, declining, stable)"""
        if len(performance_history) < 2:
            return "insufficient_data"
        
        scores = [entry['score'] for entry in performance_history[-5:]]  # Last 5 scores
        
        if len(scores) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        diff = avg_second - avg_first
        
        if diff > 5:
            return "improving"
        elif diff < -5:
            return "declining"
        else:
            return "stable"
    
    def _get_latest_score(self, performance_history: List[Dict]) -> float:
        """Get the most recent score"""
        if not performance_history:
            return 0.0
        return performance_history[-1]['score']
    
    def _identify_improvement_areas(self, student: StudentProfile) -> List[Dict]:
        """Identify specific areas needing improvement"""
        improvement_areas = []
        
        # Focus on subjects with declining trends or low scores
        for subject in student.academic_performance:
            avg_score = student.get_average_score(subject)
            trend = self._calculate_trend(student.academic_performance[subject])
            
            if trend == "declining" or avg_score < self.weak_threshold:
                # Analyze recent topics for this subject
                recent_topics = self._get_recent_poor_topics(student, subject)
                
                improvement_areas.append({
                    'subject': subject,
                    'priority': self._calculate_priority(avg_score, trend),
                    'recent_poor_topics': recent_topics,
                    'suggested_focus': self._suggest_focus_areas(subject, avg_score)
                })
        
        # Sort by priority
        improvement_areas.sort(key=lambda x: x['priority'], reverse=True)
        
        return improvement_areas
    
    def _get_recent_poor_topics(self, student: StudentProfile, subject: str) -> List[str]:
        """Get topics where student recently performed poorly"""
        # This would integrate with more detailed performance tracking
        # For demo, return some common challenging topics per subject
        
        challenging_topics = {
            'mathematics': ['integration', 'differentiation', 'complex numbers', 'trigonometry'],
            'physics': ['thermodynamics', 'electromagnetism', 'quantum mechanics', 'optics'],
            'chemistry': ['organic chemistry', 'chemical bonding', 'electrochemistry'],
            'biology': ['genetics', 'cell biology', 'ecology', 'evolution'],
            'english': ['grammar', 'essay writing', 'comprehension', 'vocabulary']
        }
        
        return challenging_topics.get(subject.lower(), ['fundamental concepts'])
    
    def _calculate_priority(self, avg_score: float, trend: str) -> int:
        """Calculate improvement priority (1-10)"""
        priority = 0
        
        # Base priority on score
        if avg_score < 40:
            priority += 5
        elif avg_score < 60:
            priority += 3
        elif avg_score < 70:
            priority += 1
        
        # Adjust for trend
        if trend == "declining":
            priority += 3
        elif trend == "stable" and avg_score < self.weak_threshold:
            priority += 2
        
        return min(priority, 10)
    
    def _suggest_focus_areas(self, subject: str, avg_score: float) -> List[str]:
        """Suggest specific focus areas for improvement"""
        
        focus_suggestions = {
            'mathematics': {
                'low': ['basic arithmetic', 'fundamental concepts', 'problem-solving steps'],
                'medium': ['formula application', 'word problems', 'concept connections'],
                'high': ['advanced problems', 'proof techniques', 'real-world applications']
            },
            'physics': {
                'low': ['basic formulas', 'unit conversions', 'conceptual understanding'],
                'medium': ['problem solving', 'graph interpretation', 'laboratory skills'],
                'high': ['complex calculations', 'theoretical applications', 'research methods']
            }
        }
        
        level = 'low' if avg_score < 50 else 'medium' if avg_score < 70 else 'high'
        return focus_suggestions.get(subject.lower(), {}).get(level, ['practice fundamentals'])
    
    def _analyze_learning_gaps(self, student: StudentProfile) -> List[Dict]:
        """Identify learning gaps across subjects"""
        gaps = []
        
        # Cross-subject analysis
        subjects = list(student.academic_performance.keys())
        
        for i, subject1 in enumerate(subjects):
            for subject2 in subjects[i+1:]:
                gap = self._find_subject_gap(student, subject1, subject2)
                if gap:
                    gaps.append(gap)
        
        return gaps
    
    def _find_subject_gap(self, student: StudentProfile, subject1: str, subject2: str) -> Dict:
        """Find learning gaps between related subjects"""
        
        # Define subject relationships and expected skill transfers
        skill_connections = {
            ('mathematics', 'physics'): 'mathematical problem solving',
            ('physics', 'chemistry'): 'scientific reasoning',
            ('chemistry', 'biology'): 'molecular understanding',
            ('english', 'history'): 'analytical writing'
        }
        
        score1 = student.get_average_score(subject1)
        score2 = student.get_average_score(subject2)
        
        # Check for significant gaps
        score_diff = abs(score1 - score2)
        
        if score_diff > 20:  # Significant gap
            weaker_subject = subject1 if score1 < score2 else subject2
            stronger_subject = subject2 if score1 < score2 else subject1
            
            connection_key = (weaker_subject.lower(), stronger_subject.lower())
            reverse_key = (stronger_subject.lower(), weaker_subject.lower())
            
            skill = skill_connections.get(connection_key) or skill_connections.get(reverse_key)
            
            if skill:
                return {
                    'weaker_subject': weaker_subject,
                    'stronger_subject': stronger_subject,
                    'gap_size': score_diff,
                    'connecting_skill': skill,
                    'recommendation': f'Use {stronger_subject} strengths to improve {weaker_subject}'
                }
        
        return None
    
    def _generate_recommendations(self, analysis: Dict, student: StudentProfile) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommendations for weak subjects
        for weak_subject in analysis['weak_subjects']:
            subject = weak_subject['subject']
            recommendations.append(
                f"Focus on {subject} fundamentals with daily 10-minute practice sessions"
            )
        
        # Recommendations based on trends
        for subject, trend_data in analysis['performance_trends'].items():
            if trend_data['trend'] == 'declining':
                recommendations.append(
                    f"Address declining {subject} performance with targeted review sessions"
                )
        
        # Interest-based recommendations
        for interest in student.interests:
            weak_subjects = [ws['subject'] for ws in analysis['weak_subjects']]
            if weak_subjects:
                recommendations.append(
                    f"Connect your interest in {interest} to {weak_subjects[0]} for better engagement"
                )
        
        return recommendations[:5]  # Return top 5 recommendations
