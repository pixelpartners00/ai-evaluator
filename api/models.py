from datetime import datetime
from database import Database
from passlib.hash import pbkdf2_sha256
from bson import ObjectId

db = Database()
db.connect()

class User:
    @staticmethod
    def create(username, email, password, role, first_name="", last_name=""):
        """
        Create a new user
        """
        hashed_password = pbkdf2_sha256.hash(password)
        
        # For teachers, set approved status to false by default
        is_approved = True if role != 'teacher' else False
        
        user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "is_approved": is_approved,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.insert_one('users', user)
        user['_id'] = str(result.inserted_id)
        return user
    
    @staticmethod
    def get_by_id(user_id):
        """
        Get user by ID
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except Exception:
            return None
    
    @staticmethod
    def get_by_username(username):
        """
        Get user by username
        """
        user = db.find_one('users', {'username': username})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def get_by_email(email):
        """
        Get user by email
        """
        user = db.find_one('users', {'email': email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def verify_password(user, password):
        """
        Verify user password
        """
        return pbkdf2_sha256.verify(password, user['password'])
    
    @staticmethod
    def update(user_id, update_data):
        """
        Update user information
        """
        update_data['updated_at'] = datetime.utcnow()
        
        # Don't allow updating certain fields
        if 'role' in update_data:
            del update_data['role']
        if '_id' in update_data:
            del update_data['_id']
            
        db.update_one('users', {'_id': ObjectId(user_id)}, {'$set': update_data})
        return User.get_by_id(user_id)
    
    @staticmethod
    def approve_teacher(teacher_id):
        """
        Approve a teacher account
        """
        return db.update_one(
            'users', 
            {'_id': ObjectId(teacher_id), 'role': 'teacher'}, 
            {'$set': {'is_approved': True, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def get_pending_teachers():
        """
        Get all pending teacher approvals
        """
        teachers = db.find('users', {'role': 'teacher', 'is_approved': False})
        for teacher in teachers:
            teacher['_id'] = str(teacher['_id'])
        return teachers


class Test:
    @staticmethod
    def create(title, description, created_by, questions, time_limit=60):
        """
        Create a new test
        """
        test = {
            "title": title,
            "description": description,
            "created_by": created_by,  # user_id of teacher
            "questions": questions,
            "time_limit": time_limit,  # in minutes
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.insert_one('tests', test)
        test['_id'] = str(result.inserted_id)
        return test
    
    @staticmethod
    def get_by_id(test_id):
        """
        Get test by ID
        """
        try:
            test = db.find_one('tests', {'_id': ObjectId(test_id)})
            if test:
                test['_id'] = str(test['_id'])
            return test
        except Exception:
            return None
    
    @staticmethod
    def get_by_teacher(teacher_id):
        """
        Get all tests created by a teacher
        """
        tests = db.find('tests', {'created_by': teacher_id})
        for test in tests:
            test['_id'] = str(test['_id'])
        return tests
    
    @staticmethod
    def get_all_tests():
        """
        Get all tests
        """
        tests = db.find('tests', {})
        for test in tests:
            test['_id'] = str(test['_id'])
        return tests
    
    @staticmethod
    def update(test_id, update_data):
        """
        Update test information
        """
        update_data['updated_at'] = datetime.utcnow()
        
        # Don't allow updating certain fields
        if 'created_by' in update_data:
            del update_data['created_by']
        if '_id' in update_data:
            del update_data['_id']
            
        db.update_one('tests', {'_id': ObjectId(test_id)}, {'$set': update_data})
        return Test.get_by_id(test_id)
    
    @staticmethod
    def delete(test_id):
        """
        Delete a test
        """
        return db.delete_one('tests', {'_id': ObjectId(test_id)})


class TestAttempt:
    @staticmethod
    def create(test_id, student_id, answers=None):
        """
        Create a new test attempt
        """
        if answers is None:
            answers = []
            
        attempt = {
            "test_id": test_id,
            "student_id": student_id,
            "answers": answers,
            "score": 0,
            "is_completed": False,
            "started_at": datetime.utcnow(),
            "completed_at": None
        }
        
        result = db.insert_one('test_attempts', attempt)
        attempt['_id'] = str(result.inserted_id)
        return attempt
    
    @staticmethod
    def get_by_id(attempt_id):
        """
        Get attempt by ID
        """
        try:
            attempt = db.find_one('test_attempts', {'_id': ObjectId(attempt_id)})
            if attempt:
                attempt['_id'] = str(attempt['_id'])
            return attempt
        except Exception:
            return None
    
    @staticmethod
    def get_by_student_and_test(student_id, test_id):
        """
        Get attempts by a student for a specific test
        """
        attempts = db.find('test_attempts', {'student_id': student_id, 'test_id': test_id})
        for attempt in attempts:
            attempt['_id'] = str(attempt['_id'])
        return attempts
    
    @staticmethod
    def get_by_student(student_id):
        """
        Get all attempts by a student
        """
        attempts = db.find('test_attempts', {'student_id': student_id})
        for attempt in attempts:
            attempt['_id'] = str(attempt['_id'])
        return attempts
    
    @staticmethod
    def update(attempt_id, update_data):
        """
        Update attempt information
        """
        if 'is_completed' in update_data and update_data['is_completed']:
            update_data['completed_at'] = datetime.utcnow()
            
        db.update_one('test_attempts', {'_id': ObjectId(attempt_id)}, {'$set': update_data})
        return TestAttempt.get_by_id(attempt_id)