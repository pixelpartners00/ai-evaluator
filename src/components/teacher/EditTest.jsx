import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { teacherService } from "../../services/api";

const EditTest = ({ userId }) => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    time_limit: 60,
    questions: [],
  });

  // Fetch the test data when component mounts
  useEffect(() => {
    const fetchTest = async () => {
      try {
        setLoading(true);
        const response = await teacherService.getTest(testId);

        // Initialize form with test data
        setFormData({
          title: response.test.title,
          description: response.test.description,
          time_limit: response.test.time_limit,
          questions: response.test.questions,
        });
      } catch (err) {
        console.error("Failed to fetch test:", err);
        setError("Failed to load test data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchTest();
  }, [testId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleQuestionChange = (index, field, value) => {
    setFormData((prev) => {
      const updatedQuestions = [...prev.questions];
      updatedQuestions[index] = {
        ...updatedQuestions[index],
        [field]: value,
      };
      return { ...prev, questions: updatedQuestions };
    });
  };

  const handleOptionChange = (questionIndex, optionIndex, value) => {
    setFormData((prev) => {
      const updatedQuestions = [...prev.questions];
      const updatedOptions = [...updatedQuestions[questionIndex].options];
      updatedOptions[optionIndex] = value;
      updatedQuestions[questionIndex] = {
        ...updatedQuestions[questionIndex],
        options: updatedOptions,
      };
      return { ...prev, questions: updatedQuestions };
    });
  };

  const handleCorrectAnswerChange = (questionIndex, value) => {
    setFormData((prev) => {
      const updatedQuestions = [...prev.questions];
      updatedQuestions[questionIndex].correct_answer = parseInt(value);
      return { ...prev, questions: updatedQuestions };
    });
  };

  const addQuestion = () => {
    setFormData((prev) => ({
      ...prev,
      questions: [
        ...prev.questions,
        {
          text: "",
          type: "mcq",
          options: ["", "", "", ""],
          correct_answer: 0,
        },
      ],
    }));
  };

  const removeQuestion = (index) => {
    if (formData.questions.length === 1) {
      return; // Don't remove the last question
    }

    setFormData((prev) => {
      const updatedQuestions = [...prev.questions];
      updatedQuestions.splice(index, 1);
      return { ...prev, questions: updatedQuestions };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.title.trim()) {
      setError("Test title is required");
      return;
    }

    if (!formData.description.trim()) {
      setError("Test description is required");
      return;
    }

    // Validate that all questions have text
    for (let i = 0; i < formData.questions.length; i++) {
      const question = formData.questions[i];
      const questionType = question.type || "mcq";

      if (!question.text.trim()) {
        setError(`Question ${i + 1} text is required`);
        return;
      }

      // For MCQ questions, validate options
      if (questionType === "mcq") {
        for (let j = 0; j < question.options.length; j++) {
          if (!question.options[j].trim()) {
            setError(`Option ${j + 1} for question ${i + 1} is required`);
            return;
          }
        }
      }

      // For paragraph questions, validate model answer
      if (questionType === "paragraph" && !question.model_answer?.trim()) {
        setError(`Model answer for paragraph question ${i + 1} is required`);
        return;
      }
    }

    setSubmitting(true);

    try {
      await teacherService.updateTest(testId, formData);
      navigate("/teacher/dashboard");
    } catch (err) {
      console.error("Failed to update test:", err);
      setError(
        err.response?.data?.error || "Failed to update test. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading test data...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Edit Test</h1>
        <button
          onClick={() => navigate("/teacher/dashboard")}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Cancel
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-md rounded-lg p-6"
      >
        <div className="mb-6">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="title"
          >
            Test Title*
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <div className="mb-6">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="description"
          >
            Test Description*
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-24"
            required
          />
        </div>

        <div className="mb-6">
          <label
            className="block text-gray-700 text-sm font-bold mb-2"
            htmlFor="time_limit"
          >
            Time Limit (minutes)
          </label>
          <input
            type="number"
            id="time_limit"
            name="time_limit"
            value={formData.time_limit}
            onChange={handleChange}
            min="5"
            max="180"
            className="shadow appearance-none border rounded w-32 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>

        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Questions</h2>
            <button
              type="button"
              onClick={addQuestion}
              className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Add Question
            </button>
          </div>

          {formData.questions.map((question, qIndex) => {
            const questionType = question.type || "mcq";
            return (
              <div key={qIndex} className="bg-gray-50 p-4 rounded-lg mb-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">Question {qIndex + 1}</h3>
                  <button
                    type="button"
                    onClick={() => removeQuestion(qIndex)}
                    className="text-red-500 hover:text-red-700"
                    disabled={formData.questions.length === 1}
                  >
                    Remove
                  </button>
                </div>

                <div className="mb-4">
                  <label
                    className="block text-gray-700 text-sm font-bold mb-2"
                    htmlFor={`question-type-${qIndex}`}
                  >
                    Question Type
                  </label>
                  <select
                    id={`question-type-${qIndex}`}
                    value={questionType}
                    onChange={(e) =>
                      handleQuestionChange(qIndex, "type", e.target.value)
                    }
                    className="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  >
                    <option value="mcq">Multiple Choice</option>
                    <option value="paragraph">Paragraph</option>
                  </select>
                </div>

                <div className="mb-4">
                  <label
                    className="block text-gray-700 text-sm font-bold mb-2"
                    htmlFor={`question-${qIndex}`}
                  >
                    Question Text*
                  </label>
                  <textarea
                    id={`question-${qIndex}`}
                    value={question.text}
                    onChange={(e) =>
                      handleQuestionChange(qIndex, "text", e.target.value)
                    }
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Enter question text"
                    required
                  />
                </div>

                {questionType === "mcq" ? (
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2">
                      Options*
                    </label>
                    {question.options.map((option, oIndex) => (
                      <div key={oIndex} className="flex items-center mb-2">
                        <input
                          type="radio"
                          id={`option-${qIndex}-${oIndex}`}
                          name={`correct-${qIndex}`}
                          value={oIndex}
                          checked={question.correct_answer === oIndex}
                          onChange={(e) =>
                            handleCorrectAnswerChange(qIndex, e.target.value)
                          }
                          className="mr-2"
                        />
                        <input
                          type="text"
                          value={option}
                          onChange={(e) =>
                            handleOptionChange(qIndex, oIndex, e.target.value)
                          }
                          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                          placeholder={`Option ${oIndex + 1}`}
                          required
                        />
                      </div>
                    ))}
                    <p className="text-xs text-gray-600">
                      Select the radio button next to the correct answer.
                    </p>
                  </div>
                ) : (
                  <div className="mb-4">
                    <label
                      className="block text-gray-700 text-sm font-bold mb-2"
                      htmlFor={`model-answer-${qIndex}`}
                    >
                      Model Answer (for grading)*
                    </label>
                    <textarea
                      id={`model-answer-${qIndex}`}
                      value={question.model_answer || ""}
                      onChange={(e) =>
                        handleQuestionChange(
                          qIndex,
                          "model_answer",
                          e.target.value
                        )
                      }
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-24"
                      placeholder="Enter model answer"
                      required
                    />
                    <div className="mt-2">
                      <label
                        className="block text-gray-700 text-sm font-bold mb-2"
                        htmlFor={`keywords-${qIndex}`}
                      >
                        Keywords (comma-separated)
                      </label>
                      <input
                        type="text"
                        id={`keywords-${qIndex}`}
                        value={question.keywords?.join(", ") || ""}
                        onChange={(e) => {
                          const keywordsArray = e.target.value
                            .split(",")
                            .map((k) => k.trim())
                            .filter((k) => k);
                          handleQuestionChange(
                            qIndex,
                            "keywords",
                            keywordsArray
                          );
                        }}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        placeholder="E.g., concept1, concept2, concept3"
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className={`px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none focus:shadow-outline ${
              submitting ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {submitting ? "Saving Changes..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditTest;
