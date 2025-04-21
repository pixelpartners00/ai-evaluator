import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { studentService, teacherService } from "../../services/api";

const TestResults = ({ userId }) => {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [attempt, setAttempt] = useState(null);
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);

      // First, get the attempt
      const attempts = await studentService.getAttempts(userId);
      const currentAttempt = attempts.attempts?.find(
        (a) => a._id === attemptId
      );

      if (!currentAttempt) {
        throw new Error("Attempt not found");
      }

      setAttempt(currentAttempt);

      // Then get the test details
      const testResponse = await teacherService.getTest(currentAttempt.test_id);
      setTest(testResponse.test);
    } catch (err) {
      console.error("Failed to fetch results:", err);
      setError("Failed to load test results. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get the letter grade
  const getLetterGrade = (score) => {
    if (score >= 90) return "A";
    if (score >= 80) return "B";
    if (score >= 70) return "C";
    if (score >= 60) return "D";
    return "F";
  };

  // Helper function to get score color class
  const getScoreColorClass = (score) => {
    if (score >= 70) return "text-green-600";
    if (score >= 60) return "text-amber-600";
    return "text-red-600";
  };

  if (loading) {
    return <div className="text-center py-8">Loading results...</div>;
  }

  if (error || !attempt || !test) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error || "Failed to load test results"}</p>
        <button
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          onClick={() => navigate("/student/dashboard")}
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Test Results</h1>
        <Link
          to="/student/dashboard"
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Back to Dashboard
        </Link>
      </div>

      {/* Results Summary Card */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">{test.title}</h2>
        <p className="text-gray-600 mb-4">{test.description}</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-gray-500 text-sm">Score</div>
            <div
              className={`text-3xl font-bold ${getScoreColorClass(
                attempt.score
              )}`}
            >
              {attempt.score.toFixed(1)}%
            </div>
            <div className={`text-xl ${getScoreColorClass(attempt.score)}`}>
              Grade: {getLetterGrade(attempt.score)}
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-gray-500 text-sm">Questions</div>
            <div className="text-3xl font-bold">{test.questions.length}</div>
            <div className="text-gray-600">
              {
                attempt.answers.filter(
                  (_, i) =>
                    attempt.answers[i] === test.questions[i].correct_answer
                ).length
              }{" "}
              correct
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-gray-500 text-sm">Completion Time</div>
            <div className="text-3xl font-bold">
              {new Date(attempt.completed_at).toLocaleDateString()}
            </div>
            <div className="text-gray-600">
              {new Date(attempt.completed_at).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Questions & Answers Review */}
      <div className="bg-white shadow-md rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Review Your Answers</h3>

        <div className="space-y-6">
          {test.questions.map((question, index) => {
            const studentAnswer = attempt.answers[index];
            const questionType = question.type || "mcq"; // Default to mcq for backward compatibility
            const questionScore = attempt.question_scores
              ? attempt.question_scores[index]
              : null;
            const feedback = attempt.feedback ? attempt.feedback[index] : null;

            // For MCQ questions
            const isCorrect =
              questionType === "mcq" &&
              studentAnswer === question.correct_answer;

            return (
              <div
                key={index}
                className={`p-4 rounded-lg border ${
                  questionType === "mcq"
                    ? isCorrect
                      ? "border-green-200 bg-green-50"
                      : "border-red-200 bg-red-50"
                    : "border-blue-200 bg-blue-50"
                }`}
              >
                <div className="flex items-start">
                  <div className="mr-3">
                    {questionType === "mcq" ? (
                      <span
                        className={`inline-block w-6 h-6 rounded-full text-center ${
                          isCorrect ? "bg-green-500" : "bg-red-500"
                        } text-white font-bold`}
                      >
                        {isCorrect ? "✓" : "✗"}
                      </span>
                    ) : (
                      <span className="inline-block w-6 h-6 rounded-full text-center bg-blue-500 text-white font-bold">
                        {Math.round(questionScore)}
                      </span>
                    )}
                  </div>
                  <div className="flex-1">
                    <h4 className="text-md font-medium">
                      Question {index + 1}: {question.text}
                    </h4>

                    {/* For MCQ questions, show options */}
                    {questionType === "mcq" && (
                      <div className="mt-3 ml-2 space-y-1">
                        {question.options.map((option, optIndex) => (
                          <div
                            key={optIndex}
                            className={`p-2 rounded ${
                              optIndex === studentAnswer &&
                              optIndex === question.correct_answer
                                ? "bg-green-200"
                                : optIndex === studentAnswer
                                ? "bg-red-200"
                                : optIndex === question.correct_answer
                                ? "bg-green-100"
                                : ""
                            }`}
                          >
                            <div className="flex items-center">
                              <span className="mr-2 text-sm font-medium">
                                {String.fromCharCode(65 + optIndex)}.
                              </span>
                              <span>
                                {option}
                                {optIndex === question.correct_answer && (
                                  <span className="ml-2 text-green-600 font-medium">
                                    (Correct Answer)
                                  </span>
                                )}
                              </span>
                            </div>
                          </div>
                        ))}

                        {!isCorrect && (
                          <div className="mt-2 text-sm text-red-600">
                            You selected{" "}
                            {studentAnswer !== null
                              ? String.fromCharCode(65 + studentAnswer)
                              : "no option"}
                            , but the correct answer was{" "}
                            {String.fromCharCode(65 + question.correct_answer)}.
                          </div>
                        )}
                      </div>
                    )}

                    {/* For paragraph questions, show student answer and feedback */}
                    {questionType === "paragraph" && (
                      <div className="mt-3">
                        <div className="mb-3">
                          <div className="font-medium mb-1">Your Answer:</div>
                          <div className="p-3 bg-white border rounded">
                            {studentAnswer || (
                              <em className="text-gray-500">
                                No answer provided
                              </em>
                            )}
                          </div>
                        </div>

                        <div className="mb-3">
                          <div className="font-medium mb-1">Score:</div>
                          <div className="flex items-center">
                            <div
                              className={`text-lg font-bold ${
                                questionScore >= 7
                                  ? "text-green-600"
                                  : questionScore >= 4
                                  ? "text-amber-600"
                                  : "text-red-600"
                              }`}
                            >
                              {questionScore !== null
                                ? questionScore.toFixed(1)
                                : 0}{" "}
                              / 10
                            </div>
                          </div>
                        </div>

                        <div>
                          <div className="font-medium mb-1">AI Feedback:</div>
                          <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm">
                            {feedback || "No feedback available"}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TestResults;
