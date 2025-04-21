import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { studentService } from "../../services/api";

const TakeTest = ({ userId }) => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    startTest();
  }, []);

  // Timer effect
  useEffect(() => {
    if (!timeLeft || !test) return;

    const timerId = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerId);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerId);
  }, [timeLeft, test]);

  // Format time as mm:ss
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const startTest = async () => {
    try {
      setLoading(true);
      const response = await studentService.startTest(testId, userId);
      setTest(response.test);
      setAttempt(response.attempt);
      setTimeLeft(response.test.time_limit * 60); // Convert minutes to seconds

      // Initialize answers array with null values (no answer selected)
      setAnswers(new Array(response.test.questions.length).fill(null));
    } catch (err) {
      console.error("Failed to start test:", err);
      setError(
        err.response?.data?.error || "Failed to start test. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, answerIndex) => {
    setAnswers((prev) => {
      const newAnswers = [...prev];
      newAnswers[questionIndex] = answerIndex;
      return newAnswers;
    });
  };

  const handleParagraphAnswerChange = (questionIndex, answerText) => {
    setAnswers((prev) => {
      const newAnswers = [...prev];
      newAnswers[questionIndex] = answerText;
      return newAnswers;
    });
  };

  const goToPreviousQuestion = () => {
    setCurrentQuestion((prev) => Math.max(0, prev - 1));
  };

  const goToNextQuestion = () => {
    setCurrentQuestion((prev) => Math.min(test.questions.length - 1, prev + 1));
  };

  const handleSubmit = async () => {
    if (submitting) return; // Prevent double submission

    const unansweredQuestions = answers.filter((a) => a === null).length;

    // Check if there are unanswered questions and confirm submission
    if (unansweredQuestions > 0) {
      const confirm = window.confirm(
        `You have ${unansweredQuestions} unanswered questions. Are you sure you want to submit?`
      );
      if (!confirm) return;
    }

    try {
      setSubmitting(true);
      const response = await studentService.submitTest(attempt._id, answers);
      navigate(`/student/results/${response.attempt._id}`);
    } catch (err) {
      console.error("Failed to submit test:", err);
      setError(
        err.response?.data?.error || "Failed to submit test. Please try again."
      );
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading test...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
        <button
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          onClick={() => navigate("/student/dashboard")}
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  if (!test) return null;

  const currentQuestionData = test.questions[currentQuestion];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{test.title}</h1>
        <div className="text-right">
          <div
            className={`font-mono text-lg font-bold ${
              timeLeft < 60 ? "text-red-600 animate-pulse" : ""
            }`}
          >
            Time Left: {formatTime(timeLeft)}
          </div>
          <div className="text-sm text-gray-500">
            Question {currentQuestion + 1} of {test.questions.length}
          </div>
        </div>
      </div>

      {/* Question Navigation */}
      <div className="bg-white shadow-md rounded-lg mb-6 p-4">
        <div className="flex flex-wrap gap-2">
          {test.questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestion(index)}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm 
                ${
                  index === currentQuestion
                    ? "bg-indigo-600 text-white"
                    : answers[index] !== null
                    ? "bg-green-100 text-green-800 border border-green-600"
                    : "bg-gray-200 text-gray-800"
                }`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Current Question */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">
          Question {currentQuestion + 1}: {currentQuestionData.text}
        </h2>

        <div className="space-y-3">
          {currentQuestionData.type === "paragraph" ? (
            <textarea
              className="w-full p-3 border rounded-lg"
              rows="5"
              value={answers[currentQuestion] || ""}
              onChange={(e) =>
                handleParagraphAnswerChange(currentQuestion, e.target.value)
              }
            />
          ) : (
            currentQuestionData.options.map((option, index) => (
              <label
                key={index}
                className={`block p-3 border rounded-lg cursor-pointer
                  ${
                    answers[currentQuestion] === index
                      ? "border-indigo-600 bg-indigo-50"
                      : "hover:bg-gray-50"
                  }`}
              >
                <div className="flex items-center">
                  <input
                    type="radio"
                    className="mr-3"
                    name={`question-${currentQuestion}`}
                    checked={answers[currentQuestion] === index}
                    onChange={() => handleAnswerChange(currentQuestion, index)}
                  />
                  <span>{option}</span>
                </div>
              </label>
            ))
          )}
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={goToPreviousQuestion}
          disabled={currentQuestion === 0}
          className={`px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600
            ${currentQuestion === 0 ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          Previous
        </button>

        {currentQuestion < test.questions.length - 1 ? (
          <button
            onClick={goToNextQuestion}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className={`px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700
              ${submitting ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {submitting ? "Submitting..." : "Submit Test"}
          </button>
        )}
      </div>

      {/* Submit Button (always visible at bottom) */}
      <div className="mt-8 text-center">
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className={`px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-bold
            ${submitting ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {submitting ? "Submitting..." : "Submit Test"}
        </button>
        <p className="text-sm text-gray-500 mt-2">
          Click to submit your answers and complete the test
        </p>
      </div>
    </div>
  );
};

export default TakeTest;
