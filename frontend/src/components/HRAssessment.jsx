import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { applicantAPI } from '../services/api';
import './HRAssessment.css';

function HRAssessment() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [hrQuestions, setHRQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [codingScore, setCodingScore] = useState(0);
    const [submitting, setSubmitting] = useState(false);
    const [finalResults, setFinalResults] = useState(null);

    useEffect(() => {
        fetchHRData();
    }, [id]);

    const fetchHRData = async () => {
        try {
            const response = await applicantAPI.getHRQuestions(id);
            setHRQuestions(response.data.hr_questions);
            setCodingScore(response.data.coding_score);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch HR questions:', error);
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
            const formattedAnswers = hrQuestions.map(q => ({
                question_id: q.id,
                answer: answers[q.id] || ''
            }));

            const response = await applicantAPI.submitHRAnswers(id, formattedAnswers);

            if (response.data.success) {
                setFinalResults(response.data);
            }
            setSubmitting(false);
        } catch (error) {
            console.error('Failed to submit HR answers:', error);
            setSubmitting(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading HR Assessment...</div>;
    }

    if (finalResults) {
        return (
            <div className="hr-results-container">
                <div className="results-section">
                    <h2>✅ Assessment Complete!</h2>
                    <p className="completion-message">Thank you for completing all assessment phases!</p>

                    <div className="final-scores">
                        <div className="score-card">
                            <h3>Resume Score</h3>
                            <p className="score">{finalResults.breakdown.resume_score}/100</p>
                        </div>
                        <div className="score-card">
                            <h3>Coding Score</h3>
                            <p className="score">{finalResults.breakdown.coding_score}/100</p>
                        </div>
                        <div className="score-card">
                            <h3>HR Score</h3>
                            <p className="score">{finalResults.breakdown.hr_score}/100</p>
                        </div>
                        <div className="score-card highlight">
                            <h3>Final Score</h3>
                            <p className="score">{finalResults.final_score}/100</p>
                        </div>
                    </div>

                    <div className="verdict-box">
                        <h3>Assessment Verdict</h3>
                        <p className="verdict-text">{finalResults.final_verdict}</p>
                    </div>

                    <button onClick={() => navigate('/')} className="home-btn">
                        Return to Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="hr-assessment-container">
            <div className="hr-header">
                <h1>💼 HR Assessment</h1>
                <p className="phase-info">Phase 3 of 3 | Coding Score: {codingScore}/100</p>
            </div>

            <form onSubmit={handleSubmit} className="hr-assessment-form">
                <div className="hr-questions-list">
                    {hrQuestions.map((question, index) => (
                        <div key={question.id} className="hr-question-card">
                            <div className="question-header">
                                <h3>Question {index + 1}</h3>
                                <span className={`category-badge ${question.type}`}>{question.type}</span>
                            </div>
                            <p className="question-text">{question.question}</p>

                            <div className="answer-input">
                                <textarea
                                    value={answers[question.id] || ''}
                                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                                    placeholder="Share your detailed response here..."
                                    rows="6"
                                    className="hr-textarea"
                                />
                                <div className="char-counter">
                                    {(answers[question.id] || '').length} characters
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <button
                    type="submit"
                    className="submit-btn"
                    disabled={submitting}
                >
                    {submitting ? 'Submitting...' : 'Complete Assessment'}
                </button>
            </form>
        </div>
    );
}

export default HRAssessment;
