import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { applicantAPI } from '../services/api';
import './ApplicantPortal.css';

function ApplicantPortal() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        resume: null
    });
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e) => {
        setFormData(prev => ({ ...prev, resume: e.target.files[0] }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);

        try {
            const submitData = new FormData();
            submitData.append('name', formData.name);
            submitData.append('email', formData.email);
            if (formData.resume) {
                submitData.append('resume', formData.resume);
            }

            const response = await applicantAPI.submitApplication(submitData);

            if (response.data.success) {
                const applicantId = response.data.applicant_id;
                navigate(`/applicant/${applicantId}/coding`);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to submit application');
            setSubmitting(false);
        }
    };

    return (
        <div className="applicant-container">
            <div className="applicant-card">
                <div className="applicant-header">
                    <h1>🎯 Apply for Position</h1>
                    <p>Submit your application and take the coding assessment</p>
                </div>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="applicant-form">
                    <div className="form-group">
                        <label htmlFor="name">Full Name *</label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            required
                            placeholder="Enter your full name"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email Address *</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            required
                            placeholder="your.email@example.com"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="resume">Resume (PDF/DOC)</label>
                        <input
                            type="file"
                            id="resume"
                            name="resume"
                            onChange={handleFileChange}
                            accept=".pdf,.doc,.docx"
                        />
                        <small>Upload your resume for AI-powered scoring</small>
                    </div>

                    <button
                        type="submit"
                        className="submit-btn"
                        disabled={submitting}
                    >
                        {submitting ? 'Submitting...' : 'Submit & Continue to Assessment'}
                    </button>
                </form>

                <button onClick={() => navigate('/')} className="back-btn">
                    ← Back to Home
                </button>
            </div>
        </div>
    );
}

export default ApplicantPortal;
