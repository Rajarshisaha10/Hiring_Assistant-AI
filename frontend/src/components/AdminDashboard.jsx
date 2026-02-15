import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import './AdminDashboard.css';

function AdminDashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const response = await dashboardAPI.getStats();
            setStats(response.data.stats);
            setCandidates(response.data.candidates);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading">Loading dashboard...</div>;
    }

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h1>📊 Admin Dashboard</h1>
                <button onClick={() => navigate('/')} className="logout-btn">Logout</button>
            </header>

            <div className="stats-grid">
                <div className="stat-card total">
                    <h3>Total Applicants</h3>
                    <p className="stat-number">{stats?.total || 0}</p>
                </div>
                <div className="stat-card approved">
                    <h3>Approved</h3>
                    <p className="stat-number">{stats?.approved || 0}</p>
                </div>
                <div className="stat-card rejected">
                    <h3>Rejected</h3>
                    <p className="stat-number">{stats?.rejected || 0}</p>
                </div>
                <div className="stat-card pending">
                    <h3>Pending</h3>
                    <p className="stat-number">{stats?.pending || 0}</p>
                </div>
                <div className="stat-card average">
                    <h3>Average Score</h3>
                    <p className="stat-number">{stats?.avg_score || 0}</p>
                </div>
            </div>

            <div className="dashboard-actions">
                <button onClick={() => navigate('/admin/candidates')} className="action-btn">
                    View All Candidates
                </button>
            </div>

            <div className="recent-candidates">
                <h2>Recent Candidates</h2>
                {candidates.length === 0 ? (
                    <p className="no-data">No candidates yet</p>
                ) : (
                    <div className="candidates-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Resume Score</th>
                                    <th>Coding Score</th>
                                    <th>AI Score</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {candidates.slice(0, 5).map((candidate) => (
                                    <tr key={candidate.id} onClick={() => navigate(`/admin/candidate/${candidate.id}`)}>
                                        <td>{candidate.name}</td>
                                        <td>{candidate.email}</td>
                                        <td>{candidate.resume_score}</td>
                                        <td>{candidate.coding_score || 'N/A'}</td>
                                        <td className="ai-score">{candidate.ai_score}</td>
                                        <td>
                                            <span className={`status-badge ${candidate.status}`}>
                                                {candidate.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AdminDashboard;
