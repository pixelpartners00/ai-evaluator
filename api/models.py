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
    def generate_ai_test(title, description, num_questions, question_types, subject_area=None, created_by=None, time_limit=60):
        """
        Generate a test using AI with Mistral
        
        Args:
            title (str): Test title
            description (str): Test description
            num_questions (int): Number of questions to generate
            question_types (list): Types of questions to include: 'mcq', 'paragraph', or both
            subject_area (str): Optional subject area for context
            created_by (str): Teacher user ID
            time_limit (int): Test time limit in minutes
            
        Returns:
            dict: Generated test object
        """
        from mistral_wrapper import MistralAPI
        
        mistral = MistralAPI()
        
        # Construct prompt for test generation
        context = f"Subject: {subject_area}" if subject_area else ""
        prompt = f"""
        Create a test on the topic: {title}
        {context}
        Description: {description}
        
        Generate {num_questions} questions with the following distribution:
        - {'Multiple choice questions' if 'mcq' in question_types else ''}
        - {'Paragraph/essay questions' if 'paragraph' in question_types else ''}
        
        For multiple choice questions, include:
        1. The question text
        2. Four possible answer options
        3. The index of the correct answer (0-3)
        
        For paragraph questions, include:
        1. The question text
        2. A model answer that would receive full marks
        
        Format your response as a valid JSON array of questions.
        """
        
        # Set instructions for AI to generate structured test data
        instructions = """
        You are a professional educator creating test content. Generate well-formed questions in valid JSON format.
        Each question should have:
        1. 'text' (string): The question text
        2. 'type' (string): Either 'mcq' or 'paragraph'
        3. For MCQ type:
           - 'options' (array of strings): Four answer choices
           - 'correct_answer' (number): Index (0-3) of correct option
        4. For paragraph type:
           - 'model_answer' (string): Example of a complete, correct answer
           - 'keywords' (array of strings): Important concepts that should be included
           - 'max_score' (number): Maximum points for the question (default: 10)
        
        Example:
        [
          {
            "text": "What is the capital of France?",
            "type": "mcq",
            "options": ["Berlin", "London", "Paris", "Madrid"],
            "correct_answer": 2
          },
          {
            "text": "Explain the water cycle and its importance to ecosystems.",
            "type": "paragraph",
            "model_answer": "The water cycle is the continuous movement of water within Earth and its atmosphere...",
            "keywords": ["evaporation", "condensation", "precipitation", "collection", "ecosystems"],
            "max_score": 10
          }
        ]
        """
        
        try:
            # Get AI-generated questions
            response = mistral.get_response(prompt, instructions)
            
            # Parse JSON response - handle potential formatting issues
            import json
            import re
            
            # Extract JSON array if embedded in text
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
                
            questions = json.loads(response)
            
            # Create test with generated questions
            test = Test.create(
                title=title,
                description=description,
                created_by=created_by,
                questions=questions,
                time_limit=time_limit
            )
            
            return test
            
        except Exception as e:
            print(f"Error generating AI test: {str(e)}")
            raise Exception(f"Failed to generate AI test: {str(e)}")
    
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
            "question_scores": [],  # Individual question scores
            "feedback": [],         # Feedback for each question
            "is_completed": False,
            "started_at": datetime.utcnow(),
            "completed_at": None
        }
        
        result = db.insert_one('test_attempts', attempt)
        attempt['_id'] = str(result.inserted_id)
        return attempt
    
    @staticmethod
    def evaluate_paragraph_answer(student_answer, question):
        """
        Use Mistral API to evaluate a paragraph answer against a model answer
        
        Args:
            student_answer (str): The student's written response
            question (dict): Question object containing model answer and max score
            
        Returns:
            dict: Evaluation results with score and feedback
        """
        from mistral_wrapper import MistralAPI
        
        # Default max score is 10 if not specified
        max_score = question.get('max_score', 10)
        model_answer = question.get('model_answer', "")
        keywords = question.get('keywords', [])
        
        # If student didn't answer, return 0 with feedback
        if not student_answer or student_answer.strip() == "":
            return {
                "score": 0,
                "feedback": "No answer provided."
            }
            
        # Prepare evaluation prompt
        prompt = f"""
        Question: {question['text']}
        
        Model answer: {model_answer}
        
        Important keywords/concepts: {', '.join(keywords)}
        
        Student answer: {student_answer}
        
        Evaluate the student's answer against the model answer and assign a score out of {max_score} points.
        Consider:
        1. Content accuracy and completeness
        2. Inclusion of key concepts: {', '.join(keywords)}
        3. Clarity of explanation
        """
        
        # Instructions for consistent evaluation format
        instructions = f"""
        You are an objective educator evaluating student responses. Provide your evaluation as a JSON object with these fields:
        1. "score": A number from 0 to {max_score}
        2. "feedback": Constructive feedback explaining the score with specific strengths and areas for improvement
        
        Example:
        {{
          "score": 7,
          "feedback": "Good explanation of key concepts X and Y. Mentioned most key terms. Could improve by elaborating on Z and connecting concepts more clearly."
        }}
        """
        
        try:
            mistral = MistralAPI()
            response = mistral.get_response(prompt, instructions)
            
            # Extract JSON from response
            import json
            import re
            
            # Try to extract JSON object if embedded in text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
                
            evaluation = json.loads(response)
            
            # Ensure score is within bounds
            score = min(max(float(evaluation.get("score", 0)), 0), max_score)
            
            return {
                "score": score,
                "feedback": evaluation.get("feedback", "")
            }
            
        except Exception as e:
            print(f"Error evaluating paragraph answer: {str(e)}")
            # Fallback evaluation if AI fails
            return {
                "score": 0,
                "feedback": f"Error evaluating answer: {str(e)[:100]}"
            }
    
    @staticmethod
    def submit_with_evaluation(attempt_id, answers):
        """
        Submit a test attempt with AI evaluation of paragraph answers
        
        Args:
            attempt_id (str): The test attempt ID
            answers (list): List of student answers
            
        Returns:
            dict: Updated attempt with scores and feedback
        """
        # Get attempt and test data
        attempt = TestAttempt.get_by_id(attempt_id)
        if not attempt:
            raise Exception("Test attempt not found")
            
        test = Test.get_by_id(attempt['test_id'])
        if not test:
            raise Exception("Test not found")
            
        # Calculate scores and provide feedback
        questions = test['questions']
        question_scores = []
        feedback = []
        total_possible_points = 0
        total_earned_points = 0
        
        for i, answer in enumerate(answers):
            if i >= len(questions):
                break  # Don't process if there are more answers than questions
                
            question = questions[i]
            question_type = question.get('type', 'mcq')  # Default to mcq for backward compatibility
            
            if question_type == 'mcq':
                # Score MCQ questions as before
                correct = (answer == question.get('correct_answer'))
                points = 1 if correct else 0
                question_scores.append(points)
                feedback.append("Correct" if correct else "Incorrect")
                total_possible_points += 1
                total_earned_points += points
                
            elif question_type == 'paragraph':
                # Use AI to evaluate paragraph answers
                max_score = question.get('max_score', 10)
                evaluation = TestAttempt.evaluate_paragraph_answer(answer, question)
                
                question_scores.append(evaluation['score'])
                feedback.append(evaluation['feedback'])
                total_possible_points += max_score
                total_earned_points += evaluation['score']
        
        # Calculate overall percentage score
        overall_score = (total_earned_points / total_possible_points * 100) if total_possible_points > 0 else 0
        
        # Update the attempt with scores and feedback
        update_data = {
            'answers': answers,
            'question_scores': question_scores,
            'feedback': feedback,
            'score': overall_score,
            'is_completed': True,
            'completed_at': datetime.utcnow()
        }
        
        return TestAttempt.update(attempt_id, update_data)
    
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