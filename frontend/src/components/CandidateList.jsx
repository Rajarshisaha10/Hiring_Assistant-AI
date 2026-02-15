import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import './CandidateList.css';

function CandidateList() {
    const navigate = useNavigate();
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCandidates();
    }, []);

    const fetchCandidates = async () => {
        try {
            const response = await dashboardAPI.getCandidates();
            setCandidates(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch candidates:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading candidates...</div>;
    }

    return (
        <div className="candidate-list-container">
            <header className="page-header">
                <h1>👥 All Candidates</h1>
                <button onClick={() => navigate('/admin/dashboard')} className="back-btn">
                    ← Back to Dashboard
                </button>
            </header>

            <div className="candidates-grid">
                {candidates.length === 0 ? (
                    <p className="no-data">No candidates found</p>
                ) : (
                    candidates.map((candidate) => (
                        <div
                            key={candidate.id}
                            className="candidate-card"
                            onClick={() => navigate(`/admin/candidate/${candidate.id}`)}
                        >
                            <div className="candidate-header">
                                <h3>{candidate.name}</h3>
                                <span className={`status-badge ${candidate.status}`}>
                                    {candidate.status}
                                </span>
                            </div>
                            <p className="candidate-email">{candidate.email}</p>
                            <div className="candidate-scores">
                                <div className="score-item">
                                    <span>Resume:</span>
                                    <strong>{candidate.resume_score}</strong>
                                </div>
                                <div className="score-item">
                                    <span>Coding:</span>
                                    <strong>{candidate.coding_score || 'N/A'}</strong>
                                </div>
                                <div className="score-item highlight">
                                    <span>AI Score:</span>
                                    <strong>{candidate.ai_score}</strong>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default CandidateList;
