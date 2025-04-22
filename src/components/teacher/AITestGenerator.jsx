// filepath: c:\Users\Dusk Light\Desktop\ai-evaluator\src\components\teacher\AITestGenerator.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { teacherService } from "../../services/api";

const AITestGenerator = ({ userId }) => {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [generatingTest, setGeneratingTest] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    time_limit: 60,
    num_questions: 5,
    question_types: ["mcq"],
    subject_area: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleQuestionTypeChange = (type) => {
    setFormData((prev) => {
      const currentTypes = [...prev.question_types];

      // Toggle the type (add or remove)
      if (currentTypes.includes(type)) {
        // Don't allow removing if it's the only type selected
        if (currentTypes.length > 1) {
          return {
            ...prev,
            question_types: currentTypes.filter((t) => t !== type),
          };
        }
      } else {
        return {
          ...prev,
          question_types: [...currentTypes, type],
        };
      }

      return prev;
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

    // Validate number of questions
    const numQuestions = parseInt(formData.num_questions);
    if (isNaN(numQuestions) || numQuestions < 1 || numQuestions > 20) {
      setError("Number of questions must be between 1 and 20");
      return;
    }

    setLoading(true);
    setGeneratingTest(true);

    try {
      const response = await teacherService.generateAITest({
        ...formData,
        created_by: userId,
        num_questions: numQuestions,
      });

      // Navigate to dashboard on success
      navigate("/teacher/dashboard");
    } catch (err) {
      console.error("Failed to generate test:", err);
      setError(
        err.response?.data?.error ||
          "Failed to generate test. Please try again."
      );
      setGeneratingTest(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Generate Test with AI</h1>
        <button
          onClick={() => navigate("/teacher/dashboard")}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          disabled={generatingTest}
        >
          Cancel
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {generatingTest ? (
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <div className="mb-4">
            <svg
              className="animate-spin h-10 w-10 text-indigo-600 mx-auto"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>

          <h2 className="text-xl font-semibold mb-2">
            Generating Test Questions
          </h2>

          <p className="text-gray-600 mb-4">
            Our AI is creating your test based on the topic "{formData.title}".
            {formData.question_types.includes("paragraph") ? (
              <span className="block mt-2 text-orange-600">
                Paragraph questions take longer to generate (up to 2-3 minutes)
                due to the creation of detailed model answers.
              </span>
            ) : (
              " This may take a minute..."
            )}
          </p>

          {/* Progress indicator */}
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div
              className="bg-indigo-600 h-2.5 rounded-full animate-pulse"
              style={{ width: "100%" }}
            ></div>
          </div>

          <div className="text-sm text-gray-500">
            {formData.question_types.includes("paragraph")
              ? "Please be patient. Complex questions with model answers take longer to generate."
              : "Almost there..."}
          </div>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="bg-white shadow-md rounded-lg p-6"
        >
          <div className="mb-6">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="title"
            >
              Test Topic/Title*
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
              placeholder="E.g., 'World War II', 'Photosynthesis', 'Algebra Fundamentals'"
            />
          </div>

          <div className="mb-6">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="subject_area"
            >
              Subject Area (Optional)
            </label>
            <input
              type="text"
              id="subject_area"
              name="subject_area"
              value={formData.subject_area}
              onChange={handleChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="E.g., 'History', 'Biology', 'Mathematics'"
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
              placeholder="Describe what this test should cover. Be specific about concepts, difficulty level, etc."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
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
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>

            <div>
              <label
                className="block text-gray-700 text-sm font-bold mb-2"
                htmlFor="num_questions"
              >
                Number of Questions (1-20)
              </label>
              <input
                type="number"
                id="num_questions"
                name="num_questions"
                value={formData.num_questions}
                onChange={handleChange}
                min="1"
                max="20"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Question Types
            </label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.question_types.includes("mcq")}
                  onChange={() => handleQuestionTypeChange("mcq")}
                  className="mr-2"
                />
                Multiple Choice
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.question_types.includes("paragraph")}
                  onChange={() => handleQuestionTypeChange("paragraph")}
                  className="mr-2"
                />
                Paragraph/Essay
              </label>
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {formData.question_types.includes("paragraph") && (
                <>
                  <span className="block mb-1">
                    Paragraph answers will be automatically graded by AI when
                    students submit their work.
                  </span>
                  <span className="block text-orange-600">
                    Note: Generating paragraph questions takes 2-3 minutes due
                    to creating detailed model answers.
                  </span>
                </>
              )}
            </p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h3 className="text-blue-800 font-medium mb-2">
              About AI Test Generation
            </h3>
            <p className="text-blue-700 text-sm">
              Our AI will create questions based on your specifications. For
              multiple choice questions, it will provide options and mark the
              correct answer. For paragraph questions, it will create a model
              answer and evaluation criteria.
            </p>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className={`px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none focus:shadow-outline ${
                loading ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {loading ? "Generating..." : "Generate Test with AI"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default AITestGenerator;
