from pathlib import Path
path = Path("app/main.py")
text = path.read_text(encoding='utf-8')
start = text.index('async function loadExamSummary()')
end = text.index('async function submitAnswer()', start)
new_func = '''            async function loadExamSummary() {
                try {
                    const session_id = Number(document.getElementById('summary-session-id').value);
                    if (!session_id) {
                        alert('Enter an exam session ID.');
                        return;
                    }
                    const response = await fetch(`/exam-summary/${session_id}`);
                    const data = await response.json();
                    const container = document.getElementById('summary-response');
                    if (response.ok) {
                        container.innerHTML = `
                        <div style="margin-bottom: 20px;">
                            <h3 style="color: #1a3d7c; margin: 0 0 12px 0;">Exam Score Summary</h3>
                            <p style="margin: 8px 0;"><strong>Total Score:</strong> ${data.total_score.toFixed(1)} / ${data.max_score.toFixed(1)}</p>
                            <p style="margin: 8px 0;"><strong>Percentage:</strong> ${data.percentage.toFixed(2)}%</p>
                            <div style="background: linear-gradient(to right, #4CAF50 0%, #4CAF50 ${data.percentage}%, #e0e0e0 ${data.percentage}%, #e0e0e0 100%); height: 24px; border-radius: 4px; margin: 12px 0;"></div>
                            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;" />\n                            <h4 style="color: #1a3d7c; margin: 12px 0;">Question Wise Results</h4>\n                            ${data.results.map((r, idx) => `\n                                <div style="padding: 12px; background: #f9f9f9; margin: 8px 0; border-left: 4px solid ${r.score === 5 ? '#4CAF50' : '#f44336'}; border-radius: 4px;">\n                                    <p style="margin: 0 0 8px 0;"><strong>Q${idx+1}:</strong> ${r.question_text.substring(0, 100)}...</p>\n                                    <p style="margin: 0 0 8px 0;"><strong>Score:</strong> ${r.score.toFixed(1)}/5.0</p>\n                                    <p style="margin: 0 0 8px 0; font-size: 12px;"><strong>Explanation:</strong> ${r.explanation.substring(0, 200)}...</p>\n                                </div>\n                            `).join('')}
                        </div>
                    `;
                    } else {
                        container.innerHTML = `<p style="color: red;">Error: ${data.detail || 'Unable to load summary'}</p>`;
                    }
                } catch (error) {
                    document.getElementById('summary-response').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            }
'''
path.write_text(text[:start] + new_func + text[end:])
print('patched')
