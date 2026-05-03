import os
from fastapi import HTTPException
import google.generativeai as genai
from app.models import Question
import numpy as np

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Dynamically get available model
def get_available_model():
    try:
        models_list = genai.list_models()
        for model in models_list:
            if "generateContent" in model.supported_generation_methods:
                return model.name.split("/")[-1]
    except:
        pass
    return "gemini-pro"  # Fallback

MODEL_NAME = get_available_model()

semantic_model = None

def get_semantic_model():
    global semantic_model
    if semantic_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load semantic model: {e}")
            semantic_model = False
    return semantic_model if semantic_model is not False else None


def _call_gemini(prompt: str) -> str:
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured. Set GEMINI_API_KEY environment variable.",
        )

    response = genai.GenerativeModel(MODEL_NAME).generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=250,
        )
    )
    return response.text.strip()


def compute_semantic_similarity(correct_answer: str, student_answer: str) -> float:
    """Compute semantic similarity between correct and student answers using sentence transformers."""
    model = get_semantic_model()
    if not model or not correct_answer or not student_answer:
        return 0.0
    try:
        from sentence_transformers import util
        embeddings = model.encode([correct_answer, student_answer], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
        return float(similarity)
    except Exception as e:
        print(f"Error in semantic similarity: {e}")
        return 0.0


def evaluate_answer(question: Question, student_answer: str) -> tuple[float, str, float]:
    """Evaluate student answer with both Gemini AI and semantic similarity."""
    
    max_marks = question.marks  # Get marks from question
    
    # MCQ: Check if the letter choice matches
    if question.question_type.lower() == "mcq":
        # Extract the letter from correct answer (e.g., "A)" or "A.")
        correct_answer = question.answer.strip()
        student_answer = student_answer.strip().upper()
        
        # Find the correct letter choice
        import re
        match = re.match(r'^([A-D])\)', correct_answer) or re.match(r'^([A-D])\.', correct_answer) or re.match(r'^([A-D])', correct_answer)
        correct_letter = match.group(1) if match else correct_answer[:1].upper()
        
        score = max_marks if student_answer == correct_letter else 0.0
        semantic_score = score
        explanation = f"MCQ evaluation ({max_marks} marks). Student chose: {student_answer}, Correct choice: {correct_letter}"
        return score, explanation, semantic_score

    # Short answer: Semantic + Gemini hybrid evaluation
    if question.question_type.lower() == "short":
        semantic_sim = compute_semantic_similarity(question.answer, student_answer)
        semantic_score = semantic_sim * max_marks  # Scale to 0-max_marks
        
        prompt = (
            f"Rate the following short answer on a scale of 0-5.\n"
            f"Question: {question.question_text}\n"
            f"Expected answer: {question.answer}\n"
            f"Student answer: {student_answer}\n"
            f"Provide only a number (0-5) and brief explanation."
        )
        ai_response = _call_gemini(prompt)
        
        try:
            ai_score = float(ai_response.split()[0])
            ai_score = min(5.0, max(0.0, ai_score))
        except (ValueError, IndexError):
            ai_score = semantic_sim * 5.0
        
        # Scale AI score to max_marks
        ai_score_scaled = (ai_score / 5.0) * max_marks
        final_score = (semantic_score * 0.4 + ai_score_scaled * 0.6)  # Weighted hybrid
        explanation = f"Short answer ({max_marks} marks). Semantic: {semantic_sim:.2%}. AI: {ai_score}/5. Final: {final_score:.1f}/{max_marks}."
        return min(max_marks, final_score), explanation, semantic_score

    # Long answer: Deep semantic + comprehensive Gemini evaluation
    if question.question_type.lower() in ["long", "case-based"]:
        semantic_sim = compute_semantic_similarity(question.answer, student_answer)
        semantic_score = semantic_sim * max_marks  # Scale to max_marks
        
        prompt = (
            f"Comprehensively evaluate this long answer on a rubric (0-5 scale).\n"
            f"Question: {question.question_text}\n"
            f"Expected answer: {question.answer}\n"
            f"Student answer: {student_answer}\n"
            f"Consider: accuracy, completeness, clarity, depth of understanding.\n"
            f"Provide score (0-5) and detailed justification."
        )
        ai_response = _call_gemini(prompt)
        
        try:
            ai_score = float(ai_response.split()[0])
            ai_score = min(5.0, max(0.0, ai_score))
        except (ValueError, IndexError):
            ai_score = semantic_sim * 5.0
        
        # Scale AI score to max_marks
        ai_score_scaled = (ai_score / 5.0) * max_marks
        final_score = (semantic_score * 0.3 + ai_score_scaled * 0.7)  # AI weighted more for long answers
        explanation = f"{question.question_type.title()} ({max_marks} marks). Semantic: {semantic_sim:.2%}. AI: {ai_score}/5. Final: {final_score:.1f}/{max_marks}."
        return min(max_marks, final_score), explanation, semantic_score

    # Code-based: Syntax + Logic + Semantic evaluation
    if question.question_type.lower() == "code-based":
        semantic_sim = compute_semantic_similarity(question.answer, student_answer)
        semantic_score = semantic_sim * max_marks
        
        prompt = (
            f"Evaluate this code answer on a rubric (0-5 scale).\n"
            f"Question: {question.question_text}\n"
            f"Expected code: {question.answer}\n"
            f"Student code: {student_answer}\n"
            f"Consider: syntax correctness, logic, efficiency, best practices.\n"
            f"Provide score (0-5) and feedback."
        )
        ai_response = _call_gemini(prompt)
        
        try:
            ai_score = float(ai_response.split()[0])
            ai_score = min(5.0, max(0.0, ai_score))
        except (ValueError, IndexError):
            ai_score = semantic_sim * 5.0
        
        # Scale AI score to max_marks
        ai_score_scaled = (ai_score / 5.0) * max_marks
        final_score = (semantic_score * 0.35 + ai_score_scaled * 0.65)
        explanation = f"Code-based ({max_marks} marks). Semantic: {semantic_sim:.2%}. AI: {ai_score}/5. Final: {final_score:.1f}/{max_marks}."
        return min(max_marks, final_score), explanation, semantic_score
    
    # Default fallback
    return 0.0, "Unable to evaluate question type", 0.0

    # Code-based: Semantic + Logic check
    if question.question_type.lower() == "code-based":
        semantic_sim = compute_semantic_similarity(question.answer, student_answer)
        semantic_score = semantic_sim * 5.0
        
        prompt = (
            f"Evaluate this code solution (0-5).\n"
            f"Question: {question.question_text}\n"
            f"Expected code: {question.answer}\n"
            f"Student code: {student_answer}\n"
            f"Consider: correctness, efficiency, readability, best practices.\n"
            f"Provide score and feedback."
        )
        ai_response = _call_gemini(prompt)
        
        try:
            ai_score = float(ai_response.split()[0])
            ai_score = min(5.0, max(0.0, ai_score))
        except (ValueError, IndexError):
            ai_score = semantic_score
        
        final_score = (semantic_score * 0.3 + ai_score * 0.7)
        explanation = f"Code semantic similarity: {semantic_sim:.2%}. AI evaluation: {ai_score}/5. Combined: {final_score:.1f}/5. Feedback: {ai_response}"
        return min(5.0, final_score), explanation, semantic_score

    # Fallback
    score = 0.0
    return score, "Unknown question type.", 0.0
