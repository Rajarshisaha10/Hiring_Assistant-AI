# 3-Phase Assessment System

## Overview
The hiring assistant now implements a complete 3-phase assessment pipeline with weighted scoring:

### Phase 1: Resume Assessment (30% weight)
- Automated resume scoring based on:
  - Skill extraction
  - Experience parsing
  - Project count analysis
- Score: 0-100

### Phase 2: Coding Assessment (40% weight)
- Timed coding challenges with test case validation
- Auto-generated temporary Python files created for each test
- Features:
  - Multiple test cases per question
  - 5-second execution timeout
  - Automatic JSON output comparison
  - Real-time feedback on pass/fail
- Score: 0-100 (based on test case pass rate)

### Phase 3: HR Assessment (30% weight)
- Behavioral and cultural fit questions
- 4 randomly selected HR questions from pool of 8
- Scoring based on response quality and length:
  - 100: 50+ words
  - 85: 30-49 words
  - 70: 15-29 words
  - 50: 5-14 words
  - 20: 1-4 words
- Score: 0-100

## Final Score Calculation
```
Final Score = (Resume Score × 0.30) + (Coding Score × 0.40) + (HR Score × 0.30)
```

### Verdict System
- **80-100**: Strong match - highly recommended
- **65-79**: Good match - recommended
- **50-64**: Moderate match - consider
- **40-49**: Below average - manual review
- **0-39**: Poor match - not recommended

## File Structure

### Backend Files
- `app.py`: Main FastAPI application with 3-phase endpoints
- `project/questions.json`: Coding assessment questions
- `project/question_selector.py`: Coding question selection logic
- `project/hr_questions.json`: HR assessment questions
- `project/hr_selector.py`: HR question selection logic
- `project/judge.py`: Code execution and evaluation engine

### Frontend Components
- `CodingAssessment.jsx`: Phase 2 - Coding challenges
- `HRAssessment.jsx`: Phase 3 - HR questions
- `ApplicantPortal.jsx`: Entry point for applicants

## API Endpoints

### Coding Phase
- `GET /api/applicant/{id}/coding` - Get coding questions
- `POST /api/applicant/{id}/coding` - Submit coding answers + auto-transition to HR

### HR Phase
- `GET /api/applicant/{id}/hr` - Get HR questions
- `POST /api/applicant/{id}/hr` - Submit HR answers + generate final score

## Candidate Dashboard Integration
The admin dashboard now displays:
- Resume Score
- Coding Score
- HR Score (when available)
- Final Score (when assessment complete)
- Assessment status and phase

## User Experience Flow
1. **Application**: Submit resume → Instant resume scoring
2. **Coding**: Solve 3 coding questions → Get test feedback
3. **Transition**: Automatic redirect to HR phase after coding
4. **HR**: Answer 4 behavioral questions → Get final results
5. **Results**: View comprehensive scoring breakdown with verdict
