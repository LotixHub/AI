from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from . import crud, models, schemas, security
from .database import SessionLocal, engine, get_db
from .config import settings
import openai

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

openai.api_key = settings.OPENAI_API_KEY

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/interview/questions")
async def get_interview_questions(request: schemas.InterviewRequest, current_user: schemas.User = Depends(get_current_user)):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate 5 interview questions for a {request.job_role} position.",
            max_tokens=150
        )
        return {"questions": response.choices[0].text.strip().split('\n')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/answer")
async def submit_answer(request: schemas.AnswerRequest, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Provide feedback on this answer for the question '{request.question}':\n\nAnswer: {request.answer}",
            max_tokens=200
        )
        feedback = response.choices[0].text.strip()
        crud.save_answer(db, user_id=current_user.id, question=request.question, answer=request.answer, feedback=feedback)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
