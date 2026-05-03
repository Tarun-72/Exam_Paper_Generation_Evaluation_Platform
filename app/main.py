from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import exam, student, teacher
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Exam Paper Generation & Auto-Evaluation Platform",
    description="Complete platform with question generation, auto-evaluation, semantic similarity, plagiarism detection, teacher review, and analytics.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exam.router)
app.include_router(student.router)
app.include_router(teacher.router)

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>AI Exam Platform</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 24px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
            h1 { color: #1a3d7c; text-align: center; margin-bottom: 32px; }
            h2, h3 { color: #2c5aa0; }
            .container { max-width: 1400px; margin: 0 auto; }
            .card { background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
            .card-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px; }
            label { display: block; margin-top: 14px; font-weight: 600; color: #333; }
            input, select, textarea { width: 100%; padding: 12px; margin-top: 8px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
            input:focus, select:focus, textarea:focus { outline: none; border-color: #1a73e8; box-shadow: 0 0 0 3px rgba(26,115,232,0.1); }
            button { margin-top: 16px; padding: 12px 24px; border: none; background: #1a73e8; color: white; border-radius: 8px; cursor: pointer; font-weight: 600; transition: background 0.3s; }
            button:hover { background: #155ac4; }
            button.secondary { background: #34a853; }
            button.secondary:hover { background: #2d8e47; }
            button.danger { background: #ea4335; }
            button.danger:hover { background: #d33425; }
            pre { background: #f5f7fa; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 12px; border-left: 4px solid #1a73e8; }
            .result-success { color: #34a853; }
            .result-error { color: #ea4335; }
            .tab-buttons { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
            .tab-btn { padding: 8px 16px; background: #e8f0fe; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; }
            .tab-btn.active { background: #1a73e8; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .warning-box { background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 12px; margin-bottom: 16px; color: #856404; }
            .success-box { background: #d4edda; border: 1px solid #28a745; border-radius: 8px; padding: 12px; margin-bottom: 16px; color: #155724; }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
            .metric { background: #f5f7fa; padding: 16px; border-radius: 8px; text-align: center; }
            .metric-value { font-size: 28px; font-weight: 700; color: #1a73e8; }
            .metric-label { font-size: 12px; color: #666; margin-top: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Exam Paper Generation & Auto-Evaluation Platform</h1>

            <div class="tab-buttons">
                <button class="tab-btn active" onclick="switchTab('student')">Student Mode</button>
                <button class="tab-btn" onclick="switchTab('teacher')">Teacher Review</button>
                <button class="tab-btn" onclick="switchTab('analytics')">Analytics</button>
            </div>

            <!-- STUDENT TAB -->
            <div id="student" class="tab-content active">
                <div class="card">
                    <h2>Create & Start Exam</h2>
                    <label>Total Questions</label>
                    <input id="exam-total" type="number" min="1" value="5" />
                    <label>Difficulty Split</label>
                    <div class="grid-2">
                        <div>
                            <label>Easy (%)</label>
                            <input id="exam-easy" type="number" min="0" max="100" value="30" />
                        </div>
                        <div>
                            <label>Medium (%)</label>
                            <input id="exam-medium" type="number" min="0" max="100" value="50" />
                        </div>
                        <div>
                            <label>Hard (%)</label>
                            <input id="exam-hard" type="number" min="0" max="100" value="20" />
                        </div>
                    </div>
                    <button onclick="createExam()">Create Exam</button>
                    <button class="secondary" onclick="startExam()">Start Timed Exam</button>
                    <pre id="exam-response">Exam session status will appear here...</pre>
                    <p id="exam-timer" style="font-weight: 600; color: #1a73e8;">Timer: 00:00</p>
                    <div class="warning-box" style="display:none;" id="cheating-warning">
                        ⚠️ Switching tabs detected. This may be flagged as cheating.
                    </div>
                </div>

                <div class="card">
                    <h2>Exam Questions & Answers</h2>
                    <div id="exam-preview" style="margin-bottom: 20px;">No exam loaded. Create an exam first.</div>
                    <button class="secondary" onclick="submitExamBatch()">Submit Exam</button>
                    <pre id="exam-batch-response">Submission result appears here...</pre>
                </div>

                <div class="card-row">
                    <div class="card">
                        <h2>Submit Single Answer</h2>
                        <label>Question ID</label>
                        <input id="submit-qid" type="number" min="1" />
                        <label>Your Answer</label>
                        <textarea id="submit-answer" rows="4" placeholder="Enter your answer..."></textarea>
                        <button onclick="submitAnswer()">Submit Answer</button>
                        <pre id="submit-response">Result appears here...</pre>
                    </div>

                    <div class="card">
                        <h2>View Exam Summary</h2>
                        <label>Exam Session ID</label>
                        <input id="summary-session-id" type="number" min="1" />
                        <button onclick="loadExamSummary()">Load Summary</button>
                        <div id="summary-response" style="margin-top: 16px;"></div>
                    </div>
                </div>
            </div>

            <!-- TEACHER TAB -->
            <div id="teacher" class="tab-content">
                <div class="card-row">
                    <div class="card">
                        <h2>Generate Question</h2>
                        <label>Topic</label>
                        <input id="q-topic" placeholder="e.g., Python programming, Machine Learning" />
                        <label>Difficulty</label>
                        <select id="q-difficulty">
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                        </select>
                        <label>Question Type</label>
                        <select id="q-type">
                            <option value="mcq">MCQ (Multiple Choice)</option>
                            <option value="short">Short Answer</option>
                            <option value="long">Long Answer</option>
                            <option value="case-based">Case-Based</option>
                            <option value="code-based">Code-Based</option>
                        </select>
                        <button onclick="generateQuestion()">Generate Question</button>
                        <pre id="generate-response">Response will appear here...</pre>
                    </div>

                    <div class="card">
                        <h2>All Questions</h2>
                        <button onclick="loadQuestions()">Refresh Question Bank</button>
                        <pre id="questions-response">Question bank will appear here...</pre>
                    </div>
                </div>

                <div class="card-row">
                    <div class="card">
                        <h2>Review Exam Session</h2>
                        <label>Exam Session ID</label>
                        <input id="review-session-id" type="number" min="1" />
                        <button class="secondary" onclick="loadSessionReview()">Load for Review</button>
                        <pre id="review-response" style="margin-top: 16px;">Session review will appear here...</pre>
                    </div>

                    <div class="card">
                        <h2>Override Score</h2>
                        <label>Submission ID</label>
                        <input id="override-sub-id" type="number" min="1" />
                        <label>New Score (0-5)</label>
                        <input id="override-score" type="number" min="0" max="5" step="0.5" value="4" />
                        <label>Feedback</label>
                        <textarea id="override-feedback" rows="3" placeholder="Teacher feedback..."></textarea>
                        <button class="danger" onclick="overrideScore()">Save Override</button>
                        <pre id="override-response">Response will appear here...</pre>
                    </div>
                </div>

                <div class="card">
                    <h2>Detailed Session Review</h2>
                    <div id="detailed-review" style="max-height: 800px; overflow-y: auto;"></div>
                </div>
            </div>

            <!-- ANALYTICS TAB -->
            <div id="analytics" class="tab-content">
                <div class="card">
                    <h2>Performance Analytics</h2>
                    <button onclick="loadAnalytics()">Refresh Analytics</button>
                    <div id="analytics-response" style="margin-top: 20px;"></div>
                </div>

                <div class="card">
                    <h2>Plagiarism Detection</h2>
                    <button onclick="loadPlagiarismStats()">Check Plagiarism Stats</button>
                    <pre id="plagiarism-response">Plagiarism statistics will appear here...</pre>
                </div>
            </div>
        </div>

        <script>
            let currentExam = [];
            let currentSessionId = null;
            let examTimerInterval = null;
            let examSeconds = 0;
            let tabSwitchDetected = false;

            // Anti-cheating: Track tab visibility
            document.addEventListener('visibilitychange', function() {
                if (examTimerInterval) {
                    tabSwitchDetected = true;
                    document.getElementById('cheating-warning').style.display = 'block';
                    console.warn('Tab switch detected during exam!');
                }
            });

            function switchTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }

            function formatTime(seconds) {
                const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
                const secs = String(seconds % 60).padStart(2, '0');
                return `${mins}:${secs}`;
            }

            async function generateQuestion() {
                try {
                    const topic = document.getElementById('q-topic').value.trim();
                    const difficulty = document.getElementById('q-difficulty').value;
                    const question_type = document.getElementById('q-type').value;
                    if (!topic) { alert('Enter a topic'); return; }
                    
                    const response = await fetch('/generate-question', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ topic, difficulty, question_type })
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    document.getElementById('generate-response').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('generate-response').textContent = `Error: ${error.message}`;
                }
            }

            async function createExam() {
                try {
                    const total_questions = Number(document.getElementById('exam-total').value);
                    const easy = Number(document.getElementById('exam-easy').value) / 100;
                    const medium = Number(document.getElementById('exam-medium').value) / 100;
                    const hard = Number(document.getElementById('exam-hard').value) / 100;
                    
                    const difficulty_split = { easy, medium, hard };
                    const response = await fetch('/start-exam-session', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ total_questions, difficulty_split, subject: 'General' })
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    currentExam = data.questions || [];
                    currentSessionId = data.session_id;
                    const examResponse = document.getElementById('exam-response');
                    if (examResponse) {
                        examResponse.textContent = `Exam Session ID: ${data.session_id} loaded with ${data.questions.length} questions.`;
                    }
                    renderExamPreview();
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }

            function renderExamPreview() {
                const container = document.getElementById('exam-preview');
                if (!currentExam.length) {
                    container.innerHTML = 'No exam loaded.';
                    return;
                }
                container.innerHTML = currentExam.map((q, idx) => `
                    <div style="padding: 16px; margin-bottom: 16px; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <strong>Q${idx+1}:</strong>
                            <span style="background: #e3f2fd; padding: 4px 12px; border-radius: 4px; font-size: 12px;">${q.difficulty} - ${q.question_type}</span>
                        </div>
                        <p style="margin: 0 0 12px 0;">${q.question_text.split('\\n').join('<br/>')}</p>
                        <textarea id="answer-${q.id}" placeholder="Your answer..." style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace;"></textarea>
                    </div>
                `).join('');
            }

            function startExam() {
                if (!currentExam.length) { alert('Create an exam first.'); return; }
                if (examTimerInterval) clearInterval(examTimerInterval);
                examSeconds = 0;
                tabSwitchDetected = false;
                document.getElementById('cheating-warning').style.display = 'none';
                document.getElementById('exam-timer').textContent = `Timer: ${formatTime(examSeconds)}`;
                examTimerInterval = setInterval(() => {
                    examSeconds += 1;
                    document.getElementById('exam-timer').textContent = `Timer: ${formatTime(examSeconds)}`;
                }, 1000);
                alert('Exam started! Timer is running. Answer the questions and click Submit when done.');
            }

            async function submitExamBatch() {
                try {
                    if (!currentExam.length) { alert('No exam loaded.'); return; }
                    const submissions = currentExam.map(q => ({
                        question_id: q.id,
                        student_answer: document.getElementById(`answer-${q.id}`).value || ''
                    }));
                    const response = await fetch('/submit-exam-batch', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ submissions, session_id: currentSessionId })
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    document.getElementById('exam-batch-response').textContent = JSON.stringify(data, null, 2);
                    if (examTimerInterval) { clearInterval(examTimerInterval); examTimerInterval = null; }
                    document.getElementById('summary-session-id').value = currentSessionId;
                    setTimeout(() => loadExamSummary(), 500);
                } catch (error) {
                    document.getElementById('exam-batch-response').textContent = `Error: ${error.message}`;
                }
            }

            async function submitAnswer() {
                try {
                    const question_id = Number(document.getElementById('submit-qid').value);
                    const student_answer = document.getElementById('submit-answer').value;
                    if (!question_id || !student_answer.trim()) { alert('Fill all fields'); return; }
                    const response = await fetch('/submit-exam', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question_id, student_answer })
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    document.getElementById('submit-response').innerHTML = `
                        <div style="color: green;"><strong>✓ Submitted Successfully</strong></div>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                } catch (error) {
                    document.getElementById('submit-response').innerHTML = `<div style="color: red;"><strong>✗ Error: ${error.message}</strong></div>`;
                }
            }

            async function loadExamSummary() {
                try {
                    const session_id = Number(document.getElementById('summary-session-id').value);
                    if (!session_id) { alert('Enter session ID'); return; }
                    const response = await fetch(`/exam-summary/${session_id}`);
                    const data = await response.json();
                    const container = document.getElementById('summary-response');
                    if (response.ok) {
                        const percent = data.percentage;
                        const color = percent >= 70 ? '#4CAF50' : percent >= 40 ? '#FF9800' : '#f44336';
                        container.innerHTML = `
                            <div style="background: ${color}; color: white; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                                <h3 style="margin: 0;">Score: ${data.total_score.toFixed(1)} / ${data.max_score.toFixed(1)}</h3>
                                <p style="margin: 8px 0;">Percentage: ${data.percentage.toFixed(1)}%</p>
                                <div style="background: rgba(255,255,255,0.3); height: 20px; border-radius: 4px; overflow: hidden;">
                                    <div style="background: white; height: 100%; width: ${data.percentage}%;"></div>
                                </div>
                            </div>
                            <h4>Question Results:</h4>
                            ${data.results.map((r, i) => `
                                <div style="padding: 12px; margin: 8px 0; background: ${r.score >= 3 ? '#e8f5e9' : '#ffebee'}; border-radius: 6px; border-left: 4px solid ${r.score >= 3 ? '#4CAF50' : '#f44336'};">
                                    <strong>Q${i+1}:</strong> ${r.question_text.substring(0, 80)}...<br/>
                                    <span style="color: #666;">Score: ${r.score.toFixed(1)}/5</span>
                                </div>
                            `).join('')}
                        `;
                    } else {
                        container.innerHTML = `<p style="color: red;">Error: ${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('summary-response').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            }

            async function loadQuestions() {
                try {
                    const response = await fetch('/questions');
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    
                    // Group questions by difficulty
                    const groupedByDifficulty = { easy: [], medium: [], hard: [] };
                    data.forEach(q => {
                        if (groupedByDifficulty[q.difficulty]) {
                            groupedByDifficulty[q.difficulty].push(q);
                        }
                    });
                    
                    let html = `<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 12px;">`;
                    
                    // Show summary cards
                    ['easy', 'medium', 'hard'].forEach(difficulty => {
                        const count = groupedByDifficulty[difficulty].length;
                        const colors = { easy: '#34a853', medium: '#ff9800', hard: '#ea4335' };
                        const color = colors[difficulty];
                        html += `
                            <div style="background: ${color}; color: white; padding: 12px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 24px; font-weight: 700;">${count}</div>
                                <div style="font-size: 12px; text-transform: uppercase;">${difficulty} Questions</div>
                            </div>
                        `;
                    });
                    
                    html += `</div><div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #f9f9f9;">`;
                    
                    // Display questions in compact list
                    if (data.length === 0) {
                        html += `<p style="text-align: center; color: #999;">No questions available</p>`;
                    } else {
                        data.forEach((q, idx) => {
                            const diffColors = { easy: '#34a853', medium: '#ff9800', hard: '#ea4335' };
                            const color = diffColors[q.difficulty];
                            html += `
                                <div style="padding: 10px; margin-bottom: 8px; background: white; border-radius: 4px; border-left: 4px solid ${color}; font-size: 12px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                        <strong>Q${q.id}:</strong>
                                        <span style="background: ${color}; color: white; padding: 2px 6px; border-radius: 2px; font-size: 10px;">${q.question_type}</span>
                                    </div>
                                    <div style="color: #666; margin-bottom: 4px;">${q.question_text.substring(0, 70)}...</div>
                                    <div style="font-size: 10px; color: #999;">
                                        <strong>Topic:</strong> ${q.topic} | <strong>Difficulty:</strong> ${q.difficulty}
                                    </div>
                                </div>
                            `;
                        });
                    }
                    
                    html += `</div><p style="font-size: 12px; color: #666; margin-top: 8px;">Total: ${data.length} questions</p>`;
                    document.getElementById('questions-response').innerHTML = html;
                } catch (error) {
                    document.getElementById('questions-response').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            }

            async function loadResults() {
                try {
                    const response = await fetch('/results');
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    document.getElementById('results-response').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('results-response').textContent = `Error: ${error.message}`;
                }
            }

            // TEACHER FUNCTIONS
            function editScoreFromReview(submission_id, auto_score) {
                // Populate the override form with submission details
                document.getElementById('override-sub-id').value = submission_id;
                document.getElementById('override-score').value = auto_score;
                document.getElementById('override-feedback').value = '';
                
                // Scroll to the override form
                document.querySelector('.card h2:nth-of-type(2)').scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Highlight the override form briefly
                const overrideCard = document.getElementById('override-sub-id').closest('.card');
                overrideCard.style.boxShadow = '0 0 0 3px #ff9800';
                setTimeout(() => {
                    overrideCard.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)';
                }, 1500);
                
                // Focus on the feedback field
                document.getElementById('override-feedback').focus();
            }

            async function loadSessionReview() {
                try {
                    const session_id = Number(document.getElementById('review-session-id').value);
                    if (!session_id) { alert('Enter session ID'); return; }
                    const response = await fetch(`/teacher/review/${session_id}`);
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    
                    document.getElementById('review-response').textContent = `Loaded session: ${data.session_name} with ${data.total_submissions} submissions`;
                    
                    let html = `<h4>${data.session_name}</h4><div style="max-height: 600px; overflow-y: auto;">`;
                    data.submissions.forEach(s => {
                        html += `
                            <div style="padding: 16px; margin: 12px 0; background: #f5f5f5; border-radius: 8px;">
                                <p><strong>Q${s.question_id}:</strong> ${s.question_text.substring(0, 100)}...</p>
                                <p>Auto Score: <span style="color: #1a73e8; font-weight: 600;">${s.auto_score.toFixed(1)}/5</span></p>
                                <p>Student Answer: ${s.student_answer.substring(0, 150)}...</p>
                                <button onclick="editScoreFromReview(${s.submission_id}, ${s.auto_score})" style="padding: 6px 12px; font-size: 12px; background: #ff9800; color: white; border: none; border-radius: 4px; cursor: pointer;">Edit Score</button>
                            </div>
                        `;
                    });
                    html += `</div>`;
                    document.getElementById('detailed-review').innerHTML = html;
                } catch (error) {
                    document.getElementById('review-response').textContent = `Error: ${error.message}`;
                }
            }

            async function overrideScore() {
                try {
                    const sub_id = Number(document.getElementById('override-sub-id').value);
                    const score = Number(document.getElementById('override-score').value);
                    const feedback = document.getElementById('override-feedback').value;
                    if (!sub_id || !feedback.trim()) { alert('Fill all fields'); return; }
                    
                    const response = await fetch(`/teacher/override-score?submission_id=${sub_id}&new_score=${score}&feedback=${encodeURIComponent(feedback)}`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    
                    document.getElementById('override-response').innerHTML = `<div class="success-box">✓ Score updated to ${score}/5 - Refreshing...</div>`;
                    
                    // Auto-refresh session review and exam summary after 1 second
                    setTimeout(() => {
                        const session_id = document.getElementById('review-session-id').value;
                        if (session_id) {
                            loadSessionReview();
                            document.getElementById('summary-session-id').value = session_id;
                            loadExamSummary();
                        }
                        document.getElementById('override-response').innerHTML = `<div class="success-box">✓ Score updated to ${score}/5</div>`;
                    }, 1000);
                } catch (error) {
                    document.getElementById('override-response').innerHTML = `<div style="color: red;">✗ Error: ${error.message}</div>`;
                }
            }

            // ANALYTICS FUNCTIONS
            async function loadAnalytics() {
                try {
                    const response = await fetch('/analytics/performance');
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    
                    // Calculate totals
                    const totalSubmissions = Object.values(data.score_distribution).reduce((a, b) => a + b, 0);
                    const passRate = totalSubmissions > 0 ? ((Object.values(data.score_distribution).slice(3).reduce((a, b) => a + b, 0) / totalSubmissions) * 100).toFixed(1) : 0;
                    const avgPercentage = (data.average_score / 5) * 100;
                    
                    let html = `
                        <div class="grid-2">
                            <div class="metric">
                                <div class="metric-value">${data.total_exams}</div>
                                <div class="metric-label">Total Exams Conducted</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.average_score.toFixed(1)}<span style="font-size: 14px;">/5</span></div>
                                <div class="metric-label">Class Average</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${totalSubmissions}</div>
                                <div class="metric-label">Total Submissions</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${passRate}%</div>
                                <div class="metric-label">Pass Rate (≥3/5)</div>
                            </div>
                        </div>

                        <div style="margin-top: 30px; background: #f9f9f9; padding: 20px; border-radius: 8px;">
                            <h4 style="margin-top: 0;">Overall Performance Bar</h4>
                            <div style="background: #e0e0e0; height: 30px; border-radius: 6px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #ea4335, #ff9800, #34a853); height: 100%; width: ${avgPercentage}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 12px;">
                                    ${avgPercentage.toFixed(0)}%
                                </div>
                            </div>
                        </div>

                        <div style="margin-top: 30px;">
                            <h4>Score Range Distribution</h4>
                            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px;">
                    `;
                    
                    const rangeLabels = {
                        "0-1": { color: "#ea4335", label: "Very Poor" },
                        "1-2": { color: "#ff6d00", label: "Poor" },
                        "2-3": { color: "#ff9800", label: "Fair" },
                        "3-4": { color: "#fbc02d", label: "Good" },
                        "4-5": { color: "#34a853", label: "Excellent" }
                    };
                    
                    for (const [range, count] of Object.entries(data.score_distribution)) {
                        const percentage = totalSubmissions > 0 ? ((count / totalSubmissions) * 100).toFixed(1) : 0;
                        const rangeInfo = rangeLabels[range] || { color: "#999", label: range };
                        html += `
                            <div style="background: white; padding: 12px; border: 2px solid ${rangeInfo.color}; border-radius: 6px; text-align: center;">
                                <div style="font-size: 24px; font-weight: 700; color: ${rangeInfo.color};">${count}</div>
                                <div style="font-size: 11px; color: #666; margin: 4px 0;">${percentage}%</div>
                                <div style="font-size: 12px; font-weight: 600; color: ${rangeInfo.color};">${range}</div>
                                <div style="font-size: 10px; color: #888;">${rangeInfo.label}</div>
                            </div>
                        `;
                    }
                    
                    html += `</div></div>`;

                    html += `
                        <div style="margin-top: 30px;">
                            <h4>Performance by Question Difficulty</h4>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                    `;
                    
                    const difficultyColors = {
                        "easy": { color: "#34a853", bg: "#e8f5e9" },
                        "medium": { color: "#ff9800", bg: "#fff3e0" },
                        "hard": { color: "#ea4335", bg: "#ffebee" }
                    };
                    
                    for (const [diff, stats] of Object.entries(data.difficulty_performance)) {
                        const percentage = (stats.average / 5) * 100;
                        const diffInfo = difficultyColors[diff] || { color: "#999", bg: "#f5f5f5" };
                        html += `
                            <div style="background: ${diffInfo.bg}; padding: 16px; border-radius: 8px; border-left: 4px solid ${diffInfo.color};">
                                <div style="font-weight: 600; color: ${diffInfo.color}; text-transform: uppercase; font-size: 12px; margin-bottom: 8px;">${diff} Questions</div>
                                <div style="font-size: 28px; font-weight: 700; color: ${diffInfo.color};">${stats.average.toFixed(2)}/5</div>
                                <div style="font-size: 12px; color: #666; margin-top: 4px;">Avg: ${percentage.toFixed(0)}%</div>
                                <div style="font-size: 12px; color: #666; margin-top: 2px;">Count: ${stats.count} questions</div>
                                <div style="background: #ddd; height: 4px; border-radius: 2px; margin-top: 8px; overflow: hidden;">
                                    <div style="background: ${diffInfo.color}; height: 100%; width: ${percentage}%;"></div>
                                </div>
                            </div>
                        `;
                    }
                    
                    html += `</div></div>`;
                    
                    document.getElementById('analytics-response').innerHTML = html;
                } catch (error) {
                    document.getElementById('analytics-response').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            }

            async function loadPlagiarismStats() {
                try {
                    const response = await fetch('/analytics/plagiarism');
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
                    document.getElementById('plagiarism-response').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('plagiarism-response').textContent = `Error: ${error.message}`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/debug")
def debug_info():
    import os
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    debug_data = {
        "api_key_set": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0,
    }
    
    # List available models
    if api_key:
        try:
            genai.configure(api_key=api_key)
            models_list = genai.list_models()
            available_models = []
            for model in models_list:
                if "generateContent" in model.supported_generation_methods:
                    available_models.append(model.name)
            debug_data["available_models"] = available_models
            
            # Try to use the first available model
            if available_models:
                model_name = available_models[0].split("/")[-1]
                debug_data["using_model"] = model_name
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'API working' in one sentence.")
                debug_data["gemini_test"] = "success"
                debug_data["gemini_response"] = response.text[:50]
            else:
                debug_data["gemini_test"] = "no models"
        except Exception as e:
            debug_data["gemini_test"] = "failed"
            debug_data["gemini_error"] = str(e)
    
    return debug_data
