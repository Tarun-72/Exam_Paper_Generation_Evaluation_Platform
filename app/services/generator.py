import os
from sqlalchemy.orm import Session
import google.generativeai as genai
from fastapi import HTTPException
from app import models
from app.services.plagiarism_detector import check_plagiarism, store_question_embedding

def get_marks_for_question_type(question_type: str) -> float:
    """Return marks based on question type."""
    marks_mapping = {
        "mcq": 1.0,
        "short": 3.0,
        "case-based": 4.0,
        "code-based": 4.0,
        "long": 5.0,
    }
    return marks_mapping.get(question_type.lower(), 5.0)


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


def _call_gemini(prompt: str) -> str:
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.",
        )

    print(f"Using API key: {API_KEY[:10]}... (length: {len(API_KEY)})")
    print(f"Using model: {MODEL_NAME}")
    print(f"Prompt: {prompt[:100]}...")

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        print(f"Model created successfully: {model}")

        # Try the simpler API format
        response = model.generate_content(prompt)
        print(f"Response received: {response}")
        text = response.text.strip()
        print(f"Response text: {text[:100]}...")
        return text
    except Exception as e:
        print(f"Gemini API error: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {str(e)}"
        )


def generate_question(db: Session, topic: str, difficulty: str, question_type: str) -> models.Question:
    """Generate a unique question with plagiarism check."""
    print(f"Starting question generation for topic: {topic}, difficulty: {difficulty}, type: {question_type}")

    prompt = (
        f"Generate a {difficulty} level {question_type} question on {topic} with answer. "
        "Return the question followed by the answer on a new line, separated by 'Answer:'."
    )
    print(f"Generated prompt: {prompt}")

    errors = []
    for attempt in range(3):
        print(f"Attempt {attempt + 1}/3")
        try:
            raw = _call_gemini(prompt)
            print(f"Raw response: {raw}")
            if not raw or not raw.strip():
                print(f"Empty response on attempt {attempt + 1}")
                errors.append(f"Attempt {attempt + 1}: Empty response")
                continue
        except HTTPException as he:
            print(f"HTTP Error on attempt {attempt + 1}: {he.detail}")
            errors.append(f"Attempt {attempt + 1}: {he.detail}")
            continue
        except Exception as e:
            print(f"Error in _call_gemini on attempt {attempt + 1}: {e}")
            errors.append(f"Attempt {attempt + 1}: {str(e)}")
            continue
        
        if "Answer:" in raw:
            question_text, answer = raw.split("Answer:", 1)
        else:
            parts = raw.split("\n")
            question_text = parts[0]
            answer = " ".join(parts[1:]) if len(parts) > 1 else ""

        question_text = question_text.strip()
        answer = answer.strip()
        if not question_text or not answer:
            print(f"Empty question or answer on attempt {attempt + 1}")
            errors.append(f"Attempt {attempt + 1}: Empty question or answer")
            continue

        duplicate = (
            db.query(models.Question)
            .filter(models.Question.question_text == question_text)
            .first()
        )
        if duplicate:
            print(f"Duplicate question on attempt {attempt + 1}")
            errors.append(f"Attempt {attempt + 1}: Duplicate question")
            continue

        # Check for plagiarism/similarity
        try:
            plagiarism_result = check_plagiarism(db, question_text, similarity_threshold=0.85)
            if plagiarism_result["is_plagiarized"]:
                print(f"Plagiarism detected on attempt {attempt + 1}")
                errors.append(f"Attempt {attempt + 1}: Plagiarism detected")
                continue
        except Exception as e:
            print(f"Error in plagiarism check on attempt {attempt + 1}: {e}")
            errors.append(f"Attempt {attempt + 1}: Plagiarism check error - {str(e)}")
            continue

        question = models.Question(
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            question_text=question_text,
            answer=answer,
            marks=get_marks_for_question_type(question_type),
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # Store embedding for future plagiarism checks
        store_question_embedding(db, question.id)
        
        return question

    error_detail = f"Unable to generate a unique question after 3 attempts. Errors: {' | '.join(errors)}"
    print(f"Final error: {error_detail}")
    raise HTTPException(status_code=500, detail=error_detail)
