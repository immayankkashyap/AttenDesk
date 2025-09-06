# from services.gemini_service import LlamaService

# def test_ollama():
#     print("🧪 Testing Ollama + Llama integration...")
    
#     # Initialize service
#     llama = LlamaService()
    
#     # Test model connection
#     if llama.test_model_connection():
#         print("✅ Ollama connection successful!")
        
#         # Test task generation
#         test_context = {
#             'duration_minutes': 15,
#             'break_type': 'short',
#             'previous_subject': 'Mathematics',
#             'next_subject': 'Physics', 
#             'weak_subjects': ['Physics'],
#             'interests': ['space science'],
#             'learning_style': 'visual'
#         }
        
#         print("\n🎯 Testing task generation...")
#         tasks = llama.generate_micro_tasks(test_context)
        
#         print(f"📚 Generated {len(tasks)} tasks:")
#         for i, task in enumerate(tasks, 1):
#             print(f"\n{i}. {task['title']}")
#             print(f"   ⏱️  {task['duration_minutes']} minutes")
#             print(f"   📖 Subject: {task['subject']}")
#             print(f"   📝 {task['description']}")
#             if task['instructions']:
#                 print(f"   📋 Steps: {', '.join(task['instructions'][:2])}...")
        
#         print("\n✅ Ollama integration test complete!")
        
#     else:
#         print("❌ Ollama connection failed!")
#         print("Make sure:")
#         print("1. Ollama is installed: curl -fsSL https://ollama.ai/install.sh | sh")
#         print("2. Ollama is running: ollama serve")
#         print("3. Model is pulled: ollama pull llama3.2:3b")

# if __name__ == '__main__':
#     test_ollama()
