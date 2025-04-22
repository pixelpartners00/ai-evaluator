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
        import json
        import re
        import time
        
        # For paragraph questions, use a staged approach generating one question at a time
        # instead of all questions at once (which causes timeouts)
        if 'paragraph' in question_types and not 'mcq' in question_types:
            print(f"Using staged approach for {num_questions} paragraph questions")
            return Test._generate_paragraph_questions_staged(
                title, description, num_questions, subject_area, created_by, time_limit
            )
            
        # For MCQ questions or mixed types, use the standard approach
        # Use a longer timeout for paragraph questions (they take longer to generate)
        timeout = 300 if 'paragraph' in question_types else 180
        mistral = MistralAPI(debug=True, timeout=timeout)
        
        # Construct prompt for test generation
        context = f"Subject: {subject_area}" if subject_area else ""
        
        # Calculate distribution of question types
        has_mcq = 'mcq' in question_types
        has_paragraph = 'paragraph' in question_types
        
        # Define explicit question type requirements
        question_type_instruction = ""
        if has_mcq and not has_paragraph:
            question_type_instruction = f"Generate EXACTLY {num_questions} multiple choice questions. DO NOT include any paragraph or essay questions. You MUST create {num_questions} questions, not more or less."
        elif has_paragraph and not has_mcq:
            question_type_instruction = f"""
            Generate EXACTLY {num_questions} paragraph/essay questions. DO NOT include any multiple choice questions. 
            You MUST create EXACTLY {num_questions} questions, not more or less.
            Each paragraph question MUST include:
            1. A detailed question text that requires an essay response
            2. A comprehensive model answer (3-4 paragraphs) for grading
            3. A list of 5-8 important keywords/concepts that should be included in a good answer
            """
        else:
            # If both types are requested, distribute them evenly
            mcq_count = num_questions // 2
            para_count = num_questions - mcq_count
            question_type_instruction = f"""
            Generate EXACTLY {num_questions} questions with this specific distribution: 
            - {mcq_count} multiple choice questions 
            - {para_count} paragraph/essay questions
            You MUST create exactly this number of questions with this exact distribution.
            
            For each paragraph question, include:
            1. A detailed question text that requires an essay response
            2. A comprehensive model answer (3-4 paragraphs) for grading
            3. A list of 5-8 important keywords/concepts that should be included in a good answer
            """
        
        prompt = f"""
        Create a test on the topic: {title}
        {context}
        Description: {description}
        
        {question_type_instruction}
        
        For multiple choice questions, include:
        1. The question text
        2. Four possible answer options
        3. The index of the correct answer (0-3)
        
        For paragraph questions, include:
        1. The question text
        2. A model answer that would receive full marks
        3. A list of keywords/concepts that should be included in a good answer
        
        Format your response as a valid JSON array of questions with proper formatting.
        Ensure all JSON is correctly formatted with no trailing commas or syntax errors.
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
        
        IMPORTANT: Your response must be valid JSON with proper formatting. Double-check for syntax errors, especially:
        - Make sure all strings are properly quoted with double quotes
        - All properties and string values need to be enclosed in double quotes
        - No trailing commas in arrays or objects
        - Correct use of brackets and braces
        """
        
        try:
            # Get AI-generated questions
            response = mistral.get_response(prompt, instructions)
            
            print(f"Raw API response (first 1000 chars): {response[:1000]}...")
            
            # Enhanced JSON parsing with more robust error handling
            try:
                # First, try to parse directly in case the response is already valid JSON
                questions = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try extraction and fixing approaches
                
                # Try to extract JSON array if embedded in text
                json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    
                    # Try to fix common JSON issues
                    # Fix trailing commas
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*\]', ']', json_str)
                    
                    # Ensure properties are correctly quoted
                    json_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
                    
                    try:
                        questions = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        print(f"JSON parse error: {str(e)}")
                        print(f"Attempted to parse: {json_str[:500]}...")
                        raise Exception(f"Failed to parse the generated questions: {str(e)}")
                else:
                    raise Exception("No valid JSON found in the response")
            
            # Safeguard: If the questions is not a list, wrap it
            if not isinstance(questions, list):
                if isinstance(questions, dict):
                    questions = [questions]
                else:
                    raise Exception("Generated questions are not in the expected format")
            
            print(f"Successfully parsed {len(questions)} questions")
                    
            # Post-processing to ensure only requested question types are included
            filtered_questions = []
            for question in questions:
                q_type = question.get('type', 'mcq')
                if q_type in question_types:
                    # Ensure paragraph questions have keywords
                    if q_type == 'paragraph' and 'keywords' not in question:
                        # Extract keywords from model answer if not provided
                        model_answer = question.get('model_answer', '')
                        # Simple keyword extraction - split by spaces and take unique words over 5 chars
                        words = set([word.strip('.,;:()[]{}"\'"').lower() for word in model_answer.split() if len(word) > 5])
                        question['keywords'] = list(words)[:8]  # Take up to 8 keywords
                    
                    # Ensure paragraph questions have a max_score
                    if q_type == 'paragraph' and 'max_score' not in question:
                        question['max_score'] = 10
                        
                    filtered_questions.append(question)
            
            # If we've had to filter out unwanted question types, make sure we still have some questions
            if not filtered_questions and questions:
                filtered_questions = questions
            
            # Check if we have enough questions
            if len(filtered_questions) < num_questions:
                print(f"Warning: Generated only {len(filtered_questions)} questions but {num_questions} were requested")
                
                # If we specifically requested paragraph questions but got fewer than needed,
                # try to generate additional questions to make up the difference
                if has_paragraph and not has_mcq and len(filtered_questions) < num_questions:
                    remaining = num_questions - len(filtered_questions)
                    print(f"Attempting to generate {remaining} additional paragraph questions...")
                    
                    # Create additional paragraph questions manually
                    for i in range(remaining):
                        # Create a more specific prompt for a single paragraph question
                        additional_prompt = f"""
                        Create a detailed paragraph/essay question on the topic: {title}
                        {context}
                        Description: {description}
                        
                        Generate ONE well-formed question suitable for an advanced student exam.
                        Include a comprehensive model answer (3-4 paragraphs) and a list of 5-8 important keywords.
                        
                        Format your response as a valid JSON object with proper formatting.
                        """
                        
                        additional_instructions = """
                        Generate a single paragraph question in valid JSON format with:
                        {
                          "text": "The detailed question text",
                          "type": "paragraph",
                          "model_answer": "A comprehensive model answer (3-4 paragraphs)",
                          "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
                          "max_score": 10
                        }
                        """
                        
                        try:
                            additional_response = mistral.get_response(additional_prompt, additional_instructions)
                            
                            # Parse the additional question
                            try:
                                # Try direct parsing first
                                additional_question = json.loads(additional_response)
                                
                                # If we got a list with one item, use that item
                                if isinstance(additional_question, list) and len(additional_question) > 0:
                                    additional_question = additional_question[0]
                                
                                # Set type to paragraph if not already set
                                additional_question['type'] = 'paragraph'
                                
                                # Add max_score if missing
                                if 'max_score' not in additional_question:
                                    additional_question['max_score'] = 10
                                
                                # Add to our filtered questions
                                filtered_questions.append(additional_question)
                                print(f"Successfully added additional paragraph question {i+1}/{remaining}")
                                
                            except json.JSONDecodeError:
                                # Try to extract JSON object if embedded in text
                                json_match = re.search(r'\{.*\}', additional_response, re.DOTALL)
                                if json_match:
                                    json_str = json_match.group(0)
                                    # Fix common JSON formatting issues
                                    json_str = re.sub(r',\s*}', '}', json_str)
                                    json_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
                                    
                                    additional_question = json.loads(json_str)
                                    additional_question['type'] = 'paragraph'
                                    if 'max_score' not in additional_question:
                                        additional_question['max_score'] = 10
                                    
                                    filtered_questions.append(additional_question)
                                    print(f"Successfully added additional paragraph question {i+1}/{remaining}")
                                else:
                                    print(f"Failed to parse additional question {i+1}: No valid JSON found")
                        except Exception as e:
                            print(f"Error generating additional question {i+1}: {str(e)}")
                        
                        # Brief pause between requests to avoid rate limiting
                        time.sleep(1)
            
            # Create test with generated questions
            test = Test.create(
                title=title,
                description=description,
                created_by=created_by,
                questions=filtered_questions,
                time_limit=time_limit
            )
            
            return test
            
        except Exception as e:
            print(f"Error generating AI test: {str(e)}")
            raise Exception(f"Failed to generate AI test: {str(e)}")
            
    @staticmethod
    def _generate_paragraph_questions_staged(title, description, num_questions, subject_area=None, created_by=None, time_limit=60):
        """
        Generate paragraph questions one by one to avoid timeouts
        """
        from mistral_wrapper import MistralAPI
        import json
        import re
        import time
        
        print(f"Generating {num_questions} paragraph questions individually")
        questions = []
        mistral = MistralAPI(debug=True, timeout=120)  # Use a shorter timeout for individual questions
        context = f"Subject: {subject_area}" if subject_area else ""
        
        for i in range(num_questions):
            print(f"Generating paragraph question {i+1}/{num_questions}")
            
            # Generate a single paragraph question with a shorter, more focused prompt
            prompt = f"""
            Create ONE detailed paragraph/essay question about {title}.
            {context}
            Description: {description}
            
            Make this question #{i+1} in a series of {num_questions} questions on this topic.
            
            The question should:
            1. Be well-formed and challenging
            2. Require a well-structured essay response
            3. Be suitable for an educational assessment
            
            Format as JSON with these fields:
            - text: question text
            - type: "paragraph" 
            - model_answer: 3-4 paragraph comprehensive answer
            - keywords: 5-8 key concepts
            - max_score: 10
            """
            
            instructions = """
            You are creating ONE paragraph question in valid JSON format:
            {
              "text": "The detailed question text",
              "type": "paragraph",
              "model_answer": "A comprehensive model answer (3-4 paragraphs)",
              "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
              "max_score": 10
            }
            
            Ensure proper JSON formatting with double quotes, no trailing commas, and proper use of brackets.
            """
            
            try:
                response = mistral.get_response(prompt, instructions)
                
                try:
                    # Try direct parsing first
                    question = json.loads(response)
                    
                    # If we got a list with one item, use that item
                    if isinstance(question, list) and len(question) > 0:
                        question = question[0]
                        
                except json.JSONDecodeError:
                    # Try to extract JSON object if embedded in text
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if not json_match:
                        print(f"Failed to find JSON in response for question {i+1}")
                        print(f"Response preview: {response[:200]}...")
                        # Create a simple fallback question
                        question = {
                            "text": f"Question #{i+1} about {title}. Please explain the key concepts related to this topic.",
                            "type": "paragraph",
                            "model_answer": f"This is a model answer about {title} covering key concepts in the field.",
                            "keywords": ["concept", "theory", "analysis", "critical thinking", "evaluation"],
                            "max_score": 10
                        }
                    else:
                        json_str = json_match.group(0)
                        # Fix common JSON formatting issues
                        json_str = re.sub(r',\s*}', '}', json_str)
                        json_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
                        
                        question = json.loads(json_str)
                
                # Ensure type is set correctly
                question['type'] = 'paragraph'
                
                # Ensure max_score is present
                if 'max_score' not in question:
                    question['max_score'] = 10
                    
                # Ensure keywords are present
                if 'keywords' not in question or not question['keywords']:
                    model_answer = question.get('model_answer', '')
                    # Simple keyword extraction
                    words = set([word.strip('.,;:()[]{}"\'"').lower() for word in model_answer.split() if len(word) > 5])
                    question['keywords'] = list(words)[:8]  # Take up to 8 keywords
                
                questions.append(question)
                print(f"Successfully generated question {i+1}")
                
            except Exception as e:
                print(f"Error generating question {i+1}: {str(e)}")
                # Create a simple fallback question in case of error
                questions.append({
                    "text": f"Question #{i+1} about {title}. Please explain the key concepts related to this topic.",
                    "type": "paragraph",
                    "model_answer": f"This is a model answer about {title} covering key concepts in the field.",
                    "keywords": ["concept", "theory", "analysis", "critical thinking", "evaluation"],
                    "max_score": 10
                })
                
            # Brief pause between questions
            time.sleep(1)
        
        # Create test with the generated questions
        test = Test.create(
            title=title,
            description=description,
            created_by=created_by,
            questions=questions,
            time_limit=time_limit
        )
        
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