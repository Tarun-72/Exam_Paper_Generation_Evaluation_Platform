#!/usr/bin/env python3
"""Run plagiarism checks on all existing questions in database."""

from app.models import Question
from app.database import SessionLocal
from app.services.plagiarism_detector import store_question_embedding

print("=" * 80)
print("PLAGIARISM CHECK ON ALL EXISTING QUESTIONS")
print("=" * 80)

db = SessionLocal()
questions = db.query(Question).all()

print(f"\nTotal questions: {len(questions)}")
print("Starting plagiarism check and embedding storage...\n")

checked = 0
skipped = 0

for idx, q in enumerate(questions, 1):
    try:
        success = store_question_embedding(db, q.id)
        if success:
            print(f"  {idx:2}. ✓ Question {q.id}: Plagiarism checked and embedding stored")
            checked += 1
        else:
            print(f"  {idx:2}. ⚠ Question {q.id}: Failed to store embedding")
            skipped += 1
    except Exception as e:
        print(f"  {idx:2}. ✗ Question {q.id}: Error - {str(e)[:60]}")
        skipped += 1

db.close()

print("\n" + "=" * 80)
print(f"SUMMARY:")
print(f"  ✓ Successfully checked: {checked}")
print(f"  ⚠ Skipped/Failed: {skipped}")
print(f"  Total processed: {checked + skipped}")
print("\n✅ Plagiarism checking complete!")
print("=" * 80)
