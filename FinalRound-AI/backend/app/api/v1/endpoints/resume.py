from fastapi import APIRouter

router = APIRouter()

@router.post("/build")
def build_resume():
    # Placeholder for building a resume
    return {"message": "Resume built"}
