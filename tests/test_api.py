import requests
import json

# API base URL
BASE_URL = 'http://localhost:5000/api'

def test_demo_setup():
    """Test demo data setup"""
    response = requests.post(f'{BASE_URL}/demo-setup')
    print("Demo Setup Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_generate_curriculum():
    """Test curriculum generation"""
    data = {
        'student_id': 'DEMO001',
        'date': '2025-09-04'
    }
    
    response = requests.post(f'{BASE_URL}/generate-curriculum', json=data)
    print("\nCurriculum Generation Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_complete_flow():
    """Test complete API flow"""
    print("=== TESTING SMART CURRICULUM API ===\n")
    
    # Step 1: Setup demo data
    print("1. Setting up demo data...")
    demo_response = test_demo_setup()
    
    if demo_response['success']:
        print("✅ Demo setup successful!\n")
        
        # Step 2: Generate curriculum
        print("2. Generating curriculum...")
        curriculum_response = test_generate_curriculum()
        
        if curriculum_response['success']:
            print("✅ Curriculum generation successful!\n")
            
            # Display curriculum summary
            curriculum = curriculum_response['curriculum']
            print(f"📚 Generated curriculum for student: {curriculum['student_id']}")
            print(f"📅 Date: {curriculum['date']}")
            print(f"🕐 Total learning time: {curriculum['estimated_learning_time']} minutes")
            print(f"📖 Subjects covered: {', '.join(curriculum['subjects_covered'])}")
            print(f"✅ Total tasks: {curriculum['total_tasks']}")
            
            print("\n📋 BREAK-BY-BREAK CURRICULUM:")
            print("=" * 50)
            
            for i, break_period in enumerate(curriculum['break_periods'], 1):
                print(f"\n🕐 Break {i}: {break_period['start_time']}-{break_period['end_time']} ({break_period['duration_minutes']} min)")
                
                if break_period['previous_class']:
                    print(f"   ⬅️  After: {break_period['previous_class']['subject']}")
                if break_period['next_class']:
                    print(f"   ➡️  Before: {break_period['next_class']['subject']}")
                
                for j, task in enumerate(break_period['assigned_tasks'], 1):
                    print(f"\n   📚 Task {j}: {task['title']}")
                    print(f"      ⏱️  Duration: {task['duration_minutes']} minutes")
                    print(f"      📊 Difficulty: {task['difficulty']}")
                    print(f"      📖 Subject: {task['subject']}")
                    print(f"      💡 Goal: {task['learning_objectives'][0] if task['learning_objectives'] else 'Learn and practice'}")
                    
                    if 'instructions' in task and task['instructions']:
                        print(f"      📋 Steps:")
                        for step in task['instructions'][:3]:  # Show first 3 steps
                            print(f"         • {step}")
            
        else:
            print("❌ Curriculum generation failed!")
            print(curriculum_response)
    else:
        print("❌ Demo setup failed!")
        print(demo_response)

if __name__ == '__main__':
    test_complete_flow()
