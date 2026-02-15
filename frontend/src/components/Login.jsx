import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Login.css';

function Login({ setUserRole }) {
    const navigate = useNavigate();
    const [selectedRole, setSelectedRole] = useState(null);

    const handleRoleSelect = async (role) => {
        setSelectedRole(role);

        if (role === 'admin') {
            try {
                await authAPI.adminLogin({});
                setUserRole('admin');
                navigate('/admin/dashboard');
            } catch (error) {
                console.error('Admin login failed:', error);
            }
        } else if (role === 'applicant') {
            setUserRole('applicant');
            navigate('/applicant');
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>🚀 AI Hiring Assistant</h1>
                    <p>Automated Technical Recruitment Platform</p>
                </div>

                <div className="role-selection">
                    <h2>Select Your Role</h2>

                    <div className="role-cards">
                        <div
                            className="role-card admin-card"
                            onClick={() => handleRoleSelect('admin')}
                        >
                            <div className="role-icon">👨‍💼</div>
                            <h3>Admin</h3>
                            <p>Access dashboard and manage candidates</p>
                            <button className="role-btn admin-btn">Enter as Admin</button>
                        </div>

                        <div
                            className="role-card applicant-card"
                            onClick={() => handleRoleSelect('applicant')}
                        >
                            <div className="role-icon">👨‍💻</div>
                            <h3>Applicant</h3>
                            <p>Submit application and take assessment</p>
                            <button className="role-btn applicant-btn">Apply Now</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
