"""Plagiarism detection service using sentence transformers."""
from sqlalchemy.orm import Session
from app.models import Question
import numpy as np

plagiarism_model = None

def get_plagiarism_model():
    global plagiarism_model
    if plagiarism_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Using a model that doesn't require cached_download
            plagiarism_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load plagiarism model: {e}")
            print("Falling back to simpler similarity check")
            plagiarism_model = False
    return plagiarism_model if plagiarism_model is not False else None


def compute_question_embedding(question_text: str) -> list | None:
    """Generate embedding for a question using sentence transformer."""
    model = get_plagiarism_model()
    if not model or not question_text:
        return None
    try:
        embedding = model.encode(question_text, convert_to_tensor=False)
        return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
    except Exception as e:
        print(f"Error encoding question: {e}")
        return None


def check_plagiarism(db: Session, new_question_text: str, similarity_threshold: float = 0.85) -> dict:
    """Check if a new question is similar to existing questions in database."""
    model = get_plagiarism_model()
    
    try:
        if model:
            # Use sentence transformer if available
            from sentence_transformers import util
            import torch

            new_embedding = model.encode(new_question_text, convert_to_tensor=True)
            existing_questions = db.query(Question).all()
            max_similarity = 0.0
            similar_question_id = None
            
            for question in existing_questions:
                if question.embedding:
                    try:
                        existing_embedding = torch.tensor(np.array(question.embedding), dtype=torch.float32)
                        similarity = util.pytorch_cos_sim(new_embedding, existing_embedding).item()
                        
                        if similarity > max_similarity:
                            max_similarity = similarity
                            if similarity >= similarity_threshold:
                                similar_question_id = question.id
                    except Exception as e:
                        print(f"Error comparing embeddings: {e}")
                        continue
            
            is_plagiarized = max_similarity >= similarity_threshold
        else:
            # Fallback to simple text similarity
            print("Using fallback similarity check (text-based)")
            existing_questions = db.query(Question).all()
            max_similarity = 0.0
            similar_question_id = None
            
            # Simple word overlap similarity
            new_words = set(new_question_text.lower().split())
            
            for question in existing_questions:
                if question.question_text:
                    existing_words = set(question.question_text.lower().split())
                    if len(new_words) > 0 and len(existing_words) > 0:
                        intersection = len(new_words & existing_words)
                        union = len(new_words | existing_words)
                        similarity = intersection / union if union > 0 else 0.0
                        
                        if similarity > max_similarity:
                            max_similarity = similarity
                            if similarity >= 0.7:  # Lower threshold for text-based
                                similar_question_id = question.id
            
            is_plagiarized = max_similarity >= 0.7
        
        return {
            "is_plagiarized": is_plagiarized,
            "similarity": float(max_similarity),
            "similar_question_id": similar_question_id,
            "threshold": similarity_threshold
        }
    except Exception as e:
        print(f"Error in plagiarism check: {e}")
        # Default to not plagiarized on error
        return {"is_plagiarized": False, "similarity": 0.0, "similar_question_id": None, "threshold": similarity_threshold}


def store_question_embedding(db: Session, question_id: int) -> bool:
    """Store embedding for a question in database."""
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return False
        
        model = get_plagiarism_model()
        
        if model:
            # Try to store embedding if model is available
            embedding = compute_question_embedding(question.question_text)
            if embedding:
                question.embedding = embedding
        
        # Mark as checked regardless of embedding availability
        question.is_plagiarism_checked = True
        db.add(question)
        db.commit()
        return True
    except Exception as e:
        print(f"Error storing embedding: {e}")
    
    return False
