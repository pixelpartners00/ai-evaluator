from flask import Flask, jsonify, request
from flask_cors import CORS
from mistral_wrapper import MistralAPI
from controllers import AuthController, AdminController, TeacherController, StudentController
from models import User, Test

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Mistral API
mistral_api = MistralAPI()

# Create admin user on startup
def create_admin():
    # Check if admin user exists
    admin = User.get_by_username('admin')
    if not admin:
        # Create admin user
        User.create(
            username='admin',
            email='admin@example.com',
            password='admin',
            role='admin',
            first_name='Admin',
            last_name='User'
        )
        print("Admin user created successfully!")

# Health check endpoint
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

# Mistral API endpoint
@app.route('/api/ask', methods=['POST'])
def ask_mistral():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        prompt = data['prompt']
        response = mistral_api.get_response(prompt)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    return AuthController.register()

@app.route('/api/auth/login', methods=['POST'])
def login():
    return AuthController.login()

# Admin routes
@app.route('/api/admin/teachers/pending', methods=['GET'])
def get_pending_teachers():
    # In a real app, check if user is admin first
    return AdminController.get_pending_teachers()

@app.route('/api/admin/teachers/<teacher_id>/approve', methods=['POST'])
def approve_teacher(teacher_id):
    # In a real app, check if user is admin first
    return AdminController.approve_teacher(teacher_id)

# Teacher routes
@app.route('/api/tests', methods=['POST'])
def create_test():
    # In a real app, check if user is teacher first
    return TeacherController.create_test()

@app.route('/api/tests/generate', methods=['POST'])
def generate_ai_test():
    # In a real app, check if user is an approved teacher first
    return TeacherController.generate_ai_test()

@app.route('/api/teachers/<teacher_id>/tests', methods=['GET'])
def get_teacher_tests(teacher_id):
    # In a real app, check if user is authorized first
    return TeacherController.get_tests(teacher_id)

@app.route('/api/tests/<test_id>', methods=['GET'])
def get_test(test_id):
    # In a real app, check permissions based on user role
    return TeacherController.get_test(test_id)

@app.route('/api/tests/<test_id>', methods=['PUT'])
def update_test(test_id):
    # In a real app, check if user is the test creator
    return TeacherController.update_test(test_id)

@app.route('/api/tests/<test_id>', methods=['DELETE'])
def delete_test(test_id):
    # In a real app, check if user is the test creator
    return TeacherController.delete_test(test_id)

# Student routes
@app.route('/api/tests/available', methods=['GET'])
def get_available_tests():
    # In a real app, check if user is student first
    
    # Fixed issue: StudentController was using a non-existent method
    # Instead, get all tests and filter out sensitive data
    tests = Test.get_all_tests()
    
    # Remove questions' correct answers for students
    for test in tests:
        for question in test.get('questions', []):
            question.pop('correct_answer', None)
            
    return jsonify({"tests": tests}), 200

@app.route('/api/tests/<test_id>/start', methods=['POST'])
def start_test(test_id):
    # In a real app, get student_id from authenticated user
    data = request.get_json()
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "student_id is required"}), 400
        
    return StudentController.start_test(test_id, student_id)

@app.route('/api/attempts/<attempt_id>/submit', methods=['POST'])
def submit_test(attempt_id):
    # In a real app, check if user is the one who started the attempt
    return StudentController.submit_test(attempt_id)

@app.route('/api/students/<student_id>/attempts', methods=['GET'])
def get_student_attempts(student_id):
    # In a real app, check if user is authorized
    return StudentController.get_attempts(student_id)

# Add missing method to Test model
@app.route('/api/tests/all', methods=['GET'])
def get_all_tests():
    """Get all tests (admin/teacher view)"""
    tests = Test.get_all_tests()
    return jsonify({"tests": tests}), 200

if __name__ == '__main__':
    # Create admin user before starting the app
    create_admin()
    app.run(debug=True, host='0.0.0.0', port=5000)
