import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import './CandidateDetail.css';

function CandidateDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [candidate, setCandidate] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCandidateDetail();
    }, [id]);

    const fetchCandidateDetail = async () => {
        try {
            const response = await dashboardAPI.getCandidate(id);
            setCandidate(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch candidate details:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading candidate details...</div>;
    }

    if (!candidate) {
        return <div className="error">Candidate not found</div>;
    }

    return (
        <div className="candidate-detail-container">
            <header className="page-header">
                <h1>Candidate Profile</h1>
                <button onClick={() => navigate('/admin/candidates')} className="back-btn">
                    ← Back to Candidates
                </button>
            </header>

            <div className="profile-card">
                <div className="profile-header">
                    <div className="profile-avatar">{candidate.name.charAt(0)}</div>
                    <div className="profile-info">
                        <h2>{candidate.name}</h2>
                        <p>{candidate.email}</p>
                        <span className={`status-badge ${candidate.status}`}>
                            {candidate.status}
                        </span>
                    </div>
                </div>

                <div className="profile-scores">
                    <div className="score-box">
                        <h3>Resume Score</h3>
                        <p className="score">{candidate.resume_score}/100</p>
                    </div>
                    <div className="score-box">
                        <h3>Coding Score</h3>
                        <p className="score">{candidate.coding_score || 'N/A'}</p>
                    </div>
                    <div className="score-box highlight">
                        <h3>AI Score</h3>
                        <p className="score">{candidate.ai_score}/100</p>
                    </div>
                </div>

                <div className="profile-details">
                    <div className="detail-row">
                        <span>Stage:</span>
                        <strong>{candidate.stage}</strong>
                    </div>
                    <div className="detail-row">
                        <span>AI Verdict:</span>
                        <strong>{candidate.ai_verdict}</strong>
                    </div>
                    {candidate.resume_filename && (
                        <div className="detail-row">
                            <span>Resume:</span>
                            <strong>{candidate.resume_filename}</strong>
                        </div>
                    )}
                </div>

                {candidate.coding_session && (
                    <div className="coding-session-info">
                        <h3>Coding Session Details</h3>
                        <p>Questions: {candidate.coding_session.questions?.length || 0}</p>
                        <p>Test Results: {candidate.coding_session.test_results?.length || 0}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default CandidateDetail;
