import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import ApplicantPortal from './components/ApplicantPortal';
import CodingAssessment from './components/CodingAssessment';
import HRAssessment from './components/HRAssessment';
import CandidateList from './components/CandidateList';
import CandidateDetail from './components/CandidateDetail';
import './App.css';

function App() {
    const [userRole, setUserRole] = useState(null);

    return (
        <Router>
            <div className="app">
                <Routes>
                    <Route path="/" element={<Login setUserRole={setUserRole} />} />
                    <Route path="/admin/dashboard" element={<AdminDashboard />} />
                    <Route path="/admin/candidates" element={<CandidateList />} />
                    <Route path="/admin/candidate/:id" element={<CandidateDetail />} />
                    <Route path="/applicant" element={<ApplicantPortal />} />
                    <Route path="/applicant/:id/coding" element={<CodingAssessment />} />
                    <Route path="/hr-assessment/:id" element={<HRAssessment />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
