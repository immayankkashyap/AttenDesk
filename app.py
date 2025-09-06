from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config
from models.student import StudentProfile, Timetable
from services.curriculum_generator import CurriculumGenerator
import json
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for mobile app integration

# Initialize services
curriculum_generator = CurriculumGenerator()

# In-memory storage (replace with database in production)
students_db = {}
timetables_db = {}
# In app.py (for simplicity)
section_timetables = {}  # key: "<semester>-<section>", value: timetable JSON dictionary

@app.route('/api/set-section-timetable', methods=['POST'])
def set_section_timetable():
    data = request.json
    semester = data.get('semester')
    section = data.get('section')
    if not semester or not section:
        return jsonify({"success": False, "message": "Missing semester or section"}), 400
    
    key = f"{semester}-{section}"
    section_timetables[key] = data
    
    return jsonify({"success": True, "message": "Section timetable saved."})

@app.route('/api/get-section-timetable', methods=['GET'])
def get_section_timetable():
    semester = request.args.get('semester')
    section = request.args.get('section')
    if not semester or not section:
        return jsonify({"success": False, "message": "Missing semester or section"}), 400
    
    key = f"{semester}-{section}"
    timetable = section_timetables.get(key)
    if timetable:
        return jsonify({"success": True, "timetable": timetable})
    else:
        return jsonify({"success": False, "message": "Timetable not found"}), 404


@app.route('/')
def home():
    """Home page with API documentation"""
    return jsonify({
        'message': 'Smart Curriculum Generator API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/generate-curriculum': 'Generate daily curriculum',
            'POST /api/register-student': 'Register new student',
            'POST /api/update-performance': 'Update student performance',
            'GET /api/student/<student_id>': 'Get student profile',
            'POST /api/set-timetable': 'Set student timetable'
        }
    })

@app.route('/api/register-student', methods=['POST'])
def register_student():
    """Register a new student"""
    try:
        data = request.json
        
        # Create student profile
        student = StudentProfile(
            student_id=data['student_id'],
            name=data['name'],
            grade=data.get('grade', ''),
            section=data.get('section', '')
        )
        
        # Set optional attributes
        # Set semester and section fields
        student.semester = data.get('semester', '')
        student.section = data.get('section', '')
        if 'interests' in data:
            student.interests = data['interests']
        if 'career_goals' in data:
            student.career_goals = data['career_goals']
        if 'learning_style' in data:
            student.learning_style = data['learning_style']
        
        # Store in database
        students_db[student.student_id] = student
        
        return jsonify({
            'success': True,
            'message': 'Student registered successfully',
            'student_profile': student.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/update-performance', methods=['POST'])
def update_performance():
    """Update student academic performance"""
    try:
        data = request.json
        student_id = data['student_id']
        
        if student_id not in students_db:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        student = students_db[student_id]
        
        # Update performance
        for subject_data in data['performance']:
            student.update_performance(
                subject=subject_data['subject'],
                score=subject_data['score'],
                test_type=subject_data.get('test_type', 'exam')
            )
        
        return jsonify({
            'success': True,
            'message': 'Performance updated successfully',
            'updated_profile': student.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/set-timetable', methods=['POST'])
def set_timetable():
    """Set student timetable"""
    try:
        data = request.json
        student_id = data['student_id']
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Create timetable
        timetable = Timetable(student_id, date)
        
        # Add classes
        for class_data in data['classes']:
            timetable.add_class(
                start_time=class_data['start_time'],
                end_time=class_data['end_time'],
                subject=class_data['subject'],
                teacher=class_data.get('teacher', ''),
                room=class_data.get('room', ''),
                topic=class_data.get('topic', '')
            )
        
        # Store timetable
        timetables_db[f"{student_id}_{date}"] = timetable
        
        return jsonify({
            'success': True,
            'message': 'Timetable set successfully',
            'timetable': timetable.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/generate-curriculum', methods=['POST'])
def generate_curriculum():
    """Generate personalized daily curriculum"""
    try:
        data = request.json
        student_id = data['student_id']
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get student profile
        if student_id not in students_db:
            return jsonify({
                'success': False,
                'error': 'Student not found. Please register first.'
            }), 404
        
        student = students_db[student_id]
        
        # Get timetable
        timetable_key = f"{student_id}_{date}"
        if timetable_key not in timetables_db:
            return jsonify({
                'success': False,
                'error': 'Timetable not found. Please set timetable first.'
            }), 404
        
        timetable = timetables_db[timetable_key]
        
        # Generate curriculum
        daily_curriculum = curriculum_generator.generate_daily_curriculum(student, timetable_dict=None, date=date)
        
        return jsonify({
            'success': True,
            'curriculum': daily_curriculum.to_dict(),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Error generating curriculum: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate curriculum: {str(e)}'
        }), 500

@app.route('/api/student/<student_id>', methods=['GET'])
def get_student_profile(student_id):
    """Get student profile"""
    try:
        if student_id not in students_db:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        student = students_db[student_id]
        
        return jsonify({
            'success': True,
            'student': student.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/demo-setup', methods=['POST'])
def demo_setup():
    """Setup demo data for testing"""
    try:
        # Create demo student
        demo_student = StudentProfile(
            student_id='DEMO001',
            name='Alice Johnson',
            grade='10',
            section='A'
        )
        
        # Set interests and goals
        demo_student.interests = ['artificial intelligence', 'space science', 'mathematics']
        demo_student.career_goals = ['become a software engineer', 'work at NASA']
        demo_student.learning_style = 'visual'
        
        # Add performance data
        demo_student.update_performance('Mathematics', 75)
        demo_student.update_performance('Mathematics', 70)
        demo_student.update_performance('Physics', 45)  # Weak subject
        demo_student.update_performance('Physics', 50)
        demo_student.update_performance('Chemistry', 85)
        demo_student.update_performance('English', 90)
        
        # Store student
        students_db[demo_student.student_id] = demo_student
        
        # Create demo timetable
        today = datetime.now().strftime('%Y-%m-%d')
        demo_timetable = Timetable('DEMO001', today)
        
        # Add classes
        demo_timetable.add_class('09:00', '10:00', 'Mathematics', 'Mr. Smith', 'Room 101', 'Calculus')
        demo_timetable.add_class('10:15', '11:15', 'Physics', 'Mrs. Johnson', 'Lab 1', 'Thermodynamics')
        demo_timetable.add_class('11:30', '12:30', 'Chemistry', 'Dr. Brown', 'Lab 2', 'Organic Chemistry')
        demo_timetable.add_class('14:00', '15:00', 'English', 'Ms. Davis', 'Room 205', 'Literature')
        
        # Store timetable
        timetables_db[f"DEMO001_{today}"] = demo_timetable
        
        return jsonify({
            'success': True,
            'message': 'Demo data created successfully',
            'demo_student_id': 'DEMO001',
            'demo_date': today
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

