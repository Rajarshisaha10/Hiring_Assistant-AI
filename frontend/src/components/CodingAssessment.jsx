import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { applicantAPI } from '../services/api';
import './CodingAssessment.css';

function CodingAssessment() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [resumeScore, setResumeScore] = useState(0);
    const [codingScore, setCodingScore] = useState(null);
    const [aiScore, setAiScore] = useState(0);
    const [testResults, setTestResults] = useState([]);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchCodingData();
    }, [id]);

    const fetchCodingData = async () => {
        try {
            const response = await applicantAPI.getCodingQuestions(id);
            setQuestions(response.data.questions);
            setResumeScore(response.data.resume_score);
            setCodingScore(response.data.coding_score);
            setAiScore(response.data.ai_score);
            setTestResults(response.data.test_results);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch coding questions:', error);
            setLoading(false);
        }
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers(prev => ({ ...prev, [questionId]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const formattedAnswers = questions.map(q => ({
                question_id: q.id,
                answer: answers[q.id] || ''
            }));

            const response = await applicantAPI.submitCodingAnswers(id, formattedAnswers);

            if (response.data.success) {
                setCodingScore(response.data.coding_score);
                setTestResults(response.data.test_results);
                // Navigate to HR assessment after 2 seconds
                setTimeout(() => {
                    navigate(`/hr-assessment/${id}`);
                }, 2000);
            }
            setSubmitting(false);
        } catch (error) {
            console.error('Failed to submit answers:', error);
            setSubmitting(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading assessment...</div>;
    }

    return (
        <div className="coding-container">
            <div className="coding-header">
                <h1>💻 Coding Assessment</h1>
                <div className="scores">
                    <div className="score-item">
                        <span>Resume Score:</span>
                        <strong>{resumeScore}</strong>
                    </div>
                    {codingScore !== null && (
                        <>
                            <div className="score-item">
                                <span>Coding Score:</span>
                                <strong>{codingScore}</strong>
                            </div>
                            <div className="score-item highlight">
                                <span>AI Score:</span>
                                <strong>{aiScore}</strong>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {codingScore === null ? (
                <form onSubmit={handleSubmit} className="assessment-form">
                    <div className="questions-list">
                        {questions.map((question, index) => (
                            <div key={question.id} className="question-card">
                                <h3>Question {index + 1}</h3>
                                <p className="question-text">{question.question}</p>

                                <div className="code-editor">
                                    <textarea
                                        value={answers[question.id] || ''}
                                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                        placeholder="Write your code here..."
                                        rows="10"
                                    />
                                </div>
                            </div>
                        ))}
                    </div>

                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={submitting}
                    >
                        {submitting ? 'Submitting...' : 'Submit Answers'}
                    </button>
                </form>
            ) : (
                <div className="results-section">
                    <h2>✅ Coding Assessment Complete!</h2>
                    <p className="transition-message">Preparing HR Assessment...</p>

                    <div className="final-scores">
                        <div className="score-card">
                            <h3>Resume Score</h3>
                            <p className="score">{resumeScore}/100</p>
                        </div>
                        <div className="score-card">
                            <h3>Coding Score</h3>
                            <p className="score">{codingScore}/100</p>
                        </div>
                    </div>

                    {testResults.length > 0 && (
                        <div className="test-results">
                            <h3>Test Results Summary</h3>
                            <div className="results-preview">
                                {testResults.slice(0, 3).map((result, index) => (
                                    <div key={index} className={`test-result ${result.passed ? 'passed' : 'failed'}`}>
                                        <span>{result.title}:</span>
                                        <strong>{result.passed ? '✓ Passed' : '✗ Failed'}</strong>
                                    </div>
                                ))}
                                {testResults.length > 3 && (
                                    <p className="more-results">...and {testResults.length - 3} more test results</p>
                                )}
                            </div>
                        </div>
                    )}

                    <div className="loading-spinner">
                        <div className="spinner"></div>
                        <p>Redirecting to next phase...</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CodingAssessment;
