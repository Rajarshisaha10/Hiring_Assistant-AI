# AI Hiring Assistant - FastAPI + React

Modern React application with **FastAPI** REST API backend for automated technical recruitment.

## 🚀 Quick Start

### Backend Setup (FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python app.py
```
Backend runs on: **http://localhost:5000**

**API Documentation**: http://localhost:5000/docs (automatic Swagger UI)

### Frontend Setup (React)
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Frontend runs on: **http://localhost:5173**

## 📁 Project Structure

```
Hiring_Assistant-AI/
├── app.py                  # FastAPI REST API ⚡
├── requirements.txt        # Python dependencies
├── project/                # Backend modules
│   ├── question_selector.py
│   ├── judge.py
│   └── questions.json
└── frontend/               # React application
    ├── src/
    │   ├── components/     # React components
    │   ├── services/       # API service
    │   └── main.jsx
    └── package.json
```

## 🎯 Features

- ✅ Role-based access (Admin/Applicant)
- ✅ Resume upload & AI scoring
- ✅ Dynamic coding assessments
- ✅ Real-time score calculation
- ✅ Candidate management dashboard
- ✅ Modern, responsive UI
- ✅ Automatic API documentation (FastAPI)

## 🛠️ Tech Stack

**Backend:**
- **FastAPI** (High-performance async API)
- **Uvicorn** (ASGI server)
- **Pydantic** (Data validation)
- Python ML libraries

**Frontend:**
- React 18
- Vite
- React Router
- Axios

## 📝 API Endpoints

FastAPI provides **automatic interactive documentation** at:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

**Main Endpoints:**
- `POST /api/auth/admin` - Admin login
- `GET /api/dashboard/stats` - Dashboard data
- `POST /api/applicant/submit` - Submit application
- `GET /api/applicant/{id}/coding` - Get coding questions
- `POST /api/applicant/{id}/coding` - Submit answers
- `GET /api/candidates` - List candidates
- `GET /api/candidate/{id}` - Candidate details

## ⚡ Why FastAPI?

- **Faster**: 2-3x faster than Flask
- **Async support**: Better performance for I/O operations
- **Auto documentation**: Swagger UI included
- **Type safety**: Pydantic models for validation
- **Modern**: Built on latest Python standards

## 🎨 Design

Modern UI with:
- Gradient backgrounds
- Smooth animations
- Responsive layouts
- Premium aesthetics

## 📄 License

MIT License
