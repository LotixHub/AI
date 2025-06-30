from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
def start_interview():
    # Placeholder for starting an interview
    return {"message": "Interview started"}

@router.post("/answer")
def submit_answer():
    # Placeholder for submitting an answer
    return {"message": "Answer submitted"}
