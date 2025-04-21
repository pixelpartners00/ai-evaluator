from flask import jsonify, request
from models import User, Test, TestAttempt

class AuthController:
    @staticmethod
    def register():
        """Handle user registration"""
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Check if role is valid
        if data['role'] not in ['student', 'teacher']:
            return jsonify({"error": "Role must be either 'student' or 'teacher'"}), 400
        
        # Check if username already exists
        if User.get_by_username(data['username']):
            return jsonify({"error": "Username already exists"}), 400
        
        # Check if email already exists
        if User.get_by_email(data['email']):
            return jsonify({"error": "Email already exists"}), 400
        
        # Create user
        user = User.create(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        # Remove password from response
        user.pop('password', None)
        
        return jsonify({
            "message": "User registered successfully", 
            "user": user,
            "approval_required": data['role'] == 'teacher' and not user['is_approved']
        }), 201
    
    @staticmethod
    def login():
        """Handle user login"""
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({"error": "Username and password are required"}), 400
        
        # Check if user exists
        user = User.get_by_username(data['username'])
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Verify password
        if not User.verify_password(user, data['password']):
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Check if user is approved (for teachers)
        if user['role'] == 'teacher' and not user['is_approved']:
            return jsonify({"error": "Your account is pending approval"}), 403
        
        # Generate access token
        # In a real app, use JWT here
        token = f"{user['_id']}:{user['role']}"
        
        # Remove password from response
        user.pop('password', None)
        
        return jsonify({
            "message": "Login successful",
            "user": user,
            "token": token
        }), 200


class AdminController:
    @staticmethod
    def get_pending_teachers():
        """Get all pending teacher approvals"""
        teachers = User.get_pending_teachers()
        
        # Remove passwords from response
        for teacher in teachers:
            teacher.pop('password', None)
            
        return jsonify({"teachers": teachers}), 200
    
    @staticmethod
    def approve_teacher(teacher_id):
        """Approve a teacher account"""
        # Check if teacher exists
        teacher = User.get_by_id(teacher_id)
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404
        
        # Check if teacher is already approved
        if teacher['is_approved']:
            return jsonify({"error": "Teacher is already approved"}), 400
        
        # Approve teacher
        User.approve_teacher(teacher_id)
        
        return jsonify({"message": "Teacher approved successfully"}), 200


class TeacherController:
    @staticmethod
    def create_test():
        """Create a new test"""
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'questions', 'created_by']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Validate that questions is a list
        if not isinstance(data['questions'], list) or not data['questions']:
            return jsonify({"error": "Questions must be a non-empty list"}), 400
        
        # Check that each question has required fields
        for i, question in enumerate(data['questions']):
            if not isinstance(question, dict):
                return jsonify({"error": f"Question at index {i} is not a valid object"}), 400
                
            if 'text' not in question:
                return jsonify({"error": f"Question at index {i} is missing 'text' field"}), 400
                
            if 'options' not in question or not isinstance(question['options'], list):
                return jsonify({"error": f"Question at index {i} is missing 'options' field or it's not a list"}), 400
                
            if 'correct_answer' not in question:
                return jsonify({"error": f"Question at index {i} is missing 'correct_answer' field"}), 400
        
        # Create test
        test = Test.create(
            title=data['title'],
            description=data['description'],
            created_by=data['created_by'],
            questions=data['questions'],
            time_limit=data.get('time_limit', 60)
        )
        
        return jsonify({
            "message": "Test created successfully", 
            "test": test
        }), 201
    
    @staticmethod
    def get_tests(teacher_id):
        """Get all tests created by a teacher"""
        tests = Test.get_by_teacher(teacher_id)
        return jsonify({"tests": tests}), 200
    
    @staticmethod
    def get_test(test_id):
        """Get a specific test by ID"""
        test = Test.get_by_id(test_id)
        if not test:
            return jsonify({"error": "Test not found"}), 404
            
        return jsonify({"test": test}), 200
    
    @staticmethod
    def update_test(test_id):
        """Update a test"""
        data = request.get_json()
        
        # Check if test exists
        test = Test.get_by_id(test_id)
        if not test:
            return jsonify({"error": "Test not found"}), 404
        
        # Update test
        updated_test = Test.update(test_id, data)
        
        return jsonify({
            "message": "Test updated successfully",
            "test": updated_test
        }), 200
    
    @staticmethod
    def delete_test(test_id):
        """Delete a test"""
        # Check if test exists
        test = Test.get_by_id(test_id)
        if not test:
            return jsonify({"error": "Test not found"}), 404
        
        # Delete test
        Test.delete(test_id)
        
        return jsonify({"message": "Test deleted successfully"}), 200


class StudentController:
    @staticmethod
    def get_available_tests():
        """Get all available tests for students"""
        # In a real app, you might want to filter tests based on some criteria
        tests = Test.get_all_tests()
        
        # Remove questions' correct answers for students
        for test in tests:
            for question in test.get('questions', []):
                question.pop('correct_answer', None)
                
        return jsonify({"tests": tests}), 200
    
    @staticmethod
    def start_test(test_id, student_id):
        """Start a test attempt"""
        # Check if test exists
        test = Test.get_by_id(test_id)
        if not test:
            return jsonify({"error": "Test not found"}), 404
        
        # Create test attempt
        attempt = TestAttempt.create(test_id, student_id)
        
        # Return test without correct answers
        for question in test.get('questions', []):
            question.pop('correct_answer', None)
            
        return jsonify({
            "message": "Test started successfully",
            "attempt": attempt,
            "test": test
        }), 201
    
    @staticmethod
    def submit_test(attempt_id):
        """Submit a test attempt"""
        data = request.get_json()
        
        # Validate data
        if 'answers' not in data:
            return jsonify({"error": "Answers are required"}), 400
        
        # Get attempt
        attempt = TestAttempt.get_by_id(attempt_id)
        if not attempt:
            return jsonify({"error": "Test attempt not found"}), 404
        
        # Check if attempt is already completed
        if attempt['is_completed']:
            return jsonify({"error": "Test attempt already completed"}), 400
        
        # Get test
        test = Test.get_by_id(attempt['test_id'])
        if not test:
            return jsonify({"error": "Test not found"}), 404
        
        # Calculate score
        correct_count = 0
        questions = test['questions']
        answers = data['answers']
        
        for i, answer in enumerate(answers):
            if i < len(questions) and answer == questions[i]['correct_answer']:
                correct_count += 1
        
        score = (correct_count / len(questions)) * 100 if len(questions) > 0 else 0
        
        # Update attempt
        update_data = {
            'answers': answers,
            'score': score,
            'is_completed': True
        }
        
        updated_attempt = TestAttempt.update(attempt_id, update_data)
        
        return jsonify({
            "message": "Test submitted successfully",
            "attempt": updated_attempt
        }), 200
    
    @staticmethod
    def get_attempts(student_id):
        """Get all test attempts by a student"""
        attempts = TestAttempt.get_by_student(student_id)
        
        # Add test info to each attempt
        for attempt in attempts:
            test = Test.get_by_id(attempt['test_id'])
            if test:
                attempt['test'] = {
                    'title': test['title'],
                    'description': test['description'],
                    'time_limit': test['time_limit']
                }
                
        return jsonify({"attempts": attempts}), 200