# AI Evaluator

A modern educational testing platform with AI-powered test generation and automated essay grading

## Overview

AI Evaluator is an advanced educational assessment platform that enables teachers to create, manage, and evaluate tests while providing students with a streamlined interface for taking tests and reviewing detailed feedback. The application leverages artificial intelligence to generate test content and evaluate free-response answers.

## Features

### For Teachers

- **Test Creation**: Create multiple-choice and free-response questions manually
- **AI Test Generation**: Generate complete tests on any subject using AI
- **Test Management**: Edit, delete, and track all created tests
- **Automatic Grading**: AI-powered evaluation of student paragraph/essay responses
- **Dashboard**: Overview of all tests with status and statistics

### For Students

- **Test Taking**: User-friendly interface for taking tests with timer functionality
- **Detailed Feedback**: Comprehensive feedback on test performance
- **Progress Tracking**: Dashboard showing completed tests and scores
- **AI-Generated Feedback**: Receive personalized feedback on paragraph answers

### For Administrators

- **Teacher Approval**: Manage teacher account approvals
- **System Management**: Monitor system usage and performance

## Screenshots

### Teacher Dashboard

<!-- Insert screenshot here -->

### Test Creation

<!-- Insert screenshot here -->

### AI Test Generation

<!-- Insert screenshot here -->

### Student Test Taking

<!-- Insert screenshot here -->

### Test Results and Feedback

<!-- Insert screenshot here -->

## Technology Stack

### Frontend

- React.js with React Router for navigation
- Tailwind CSS for styling
- Axios for API communication

### Backend

- Flask RESTful API
- MongoDB database
- Mistral LLM for AI capabilities
- Authentication system with role-based permissions

## Installation and Setup

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- MongoDB

### Frontend Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/ai-evaluator.git
   cd ai-evaluator
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Run development server:
   ```
   npm run dev
   ```

### Backend Setup

1. Navigate to the API directory:

   ```
   cd api
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:

   ```
   MISTRAL_API_URL=your_mistral_api_url
   MONGODB_URI=your_mongodb_connection_string
   ```

5. Run the API server:
   ```
   python app.py
   ```

## Usage

### Default Admin Account

- Username: admin
- Password: admin

### User Roles

- **Student**: Can take tests and view results
- **Teacher**: Can create and manage tests (requires admin approval)
- **Admin**: Can approve teacher accounts and manage the system

## Project Structure

```
ai-evaluator/
├── api/                 # Backend Flask API
│   ├── app.py           # Main API application
│   ├── controllers.py   # API controllers
│   ├── models.py        # Data models
│   ├── database.py      # Database connection
│   └── mistral_wrapper.py  # AI integration
├── src/                 # React frontend
│   ├── components/      # UI components
│   ├── services/        # API service layer
│   └── App.jsx          # Main application component
├── public/              # Static assets
├── package.json         # Frontend dependencies
└── README.md            # Project documentation
```

## AI Integration

The application integrates with the Mistral Large Language Model (LLM) for:

1. Generating complete tests with questions and answers
2. Evaluating student paragraph/essay responses
3. Providing meaningful feedback on written answers

## Future Enhancements

- Interactive question types (drag-and-drop, fill-in-blanks)
- Advanced analytics for teachers
- Plagiarism detection
- Group/class management capabilities
- Mobile app version

## License

[MIT License](LICENSE)

## Contributors

- Your Name - Initial work

## Acknowledgments

- Mistral AI for providing the LLM API
- The MongoDB team for the database solution
- TailwindCSS for the styling framework
