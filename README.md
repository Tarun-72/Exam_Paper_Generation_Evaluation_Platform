# AI Exam Paper Generation & Auto-Evaluation MVP

A minimal FastAPI backend for generating exam questions, building exams, submitting answers, and evaluating responses using Gemini API.

## Requirements

* Python 3.11+ (or 3.10+)
* `GEMINI_API_KEY` environment variable set to your Gemini API key

## Install

```powershell
cd "c:\Users\suman\OneDrive\Desktop\Desktop\DATASCIENCE_AI\Intern\Exam_Paper_Generation_Evaluation_Platform"
pip install -r requirements.txt
```

## Run

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## User Interface

Open `http://127.0.0.1:8000/` for the basic interactive frontend.

## Swagger UI

Open `http://127.0.0.1:8000/docs`

## Endpoints

### 1. Generate a question

POST `/generate-question`

Body:

```json
{
  "topic": "Python functions",
  "difficulty": "easy",
  "question_type": "mcq"
}
```

### 2. Create an exam

POST `/create-exam`

Body:

```json
{
  "total_questions": 3,
  "difficulty_split": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
}
```

### 2b. Start a new exam session

POST `/start-exam-session`

Body:

```json
{
  "total_questions": 3,
  "difficulty_split": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
}
```

Response includes:
- `session_id`: Unique identifier for this exam session
- `questions`: Array of exam questions

### 3. Submit an answer

POST `/submit-exam`

Body:

```json
{
  "question_id": 1,
  "student_answer": "My answer text here"
}
```

### 3b. Submit exam answers in batch

POST `/submit-exam-batch`

Body:

```json
{
  "submissions": [
    { "question_id": 1, "student_answer": "Answer A" },
    { "question_id": 2, "student_answer": "Answer B" }
  ]
}
```

### 4. Get results

GET `/results`

### 5. Get exam auto-scoring summary

GET `/exam-summary/{session_id}`

Returns:
- `session_id`: Exam session ID
- `total_score`: Sum of all question scores
- `max_score`: Maximum possible score (number_of_questions * 5)
- `percentage`: Percentage score
- `results`: Array of per-question results with explanations

Example response:

```json
{
  "session_id": 1,
  "total_score": 12.5,
  "max_score": 15.0,
  "percentage": 83.33,
  "results": [
    {
      "question_id": 1,
      "question_text": "...",
      "correct_answer": "...",
      "student_answer": "...",
      "score": 5.0,
      "explanation": "..."
    }
  ]
}
```

## Notes

* Questions are stored in SQLite at `exam_system.db`
* Duplicate question texts are checked before saving
* MCQs are scored by exact answer match
* Subjective answers use Gemini for evaluation and explanations
* Exam sessions track student progress and auto-calculate scores
* Batch submissions support multiple questions in one request
* Auto-scoring summary shows per-question breakdown with AI explanations

## New Features

### Exam Session Management
- Start exam sessions that persist question state
- Track student progress per session
- Auto-calculate total score percentage

### Auto-Scoring Dashboard
The UI automatically displays a summary after exam submission with:
- Total score and percentage
- Per-question score breakdown
- AI-generated explanations for each answer
- Progress indicator bar

### Batch Submission
- Submit all exam answers at once
- Automatic evaluation for all questions
- Session-linked results for reporting

## Example Workflow

1. **Generate Questions** → Add questions to the bank
2. **Start Exam Session** → Create a new exam session with specific difficulty distribution
3. **Take Exam** → Answer questions in the interactive preview
4. **Submit Batch** → Submit all answers at once
5. **View Summary** → See auto-scored results with explanations
