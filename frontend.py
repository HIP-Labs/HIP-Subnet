import time
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from hip.miner.db import Option, Task, get_db

app = FastAPI()


class Answer(BaseModel):
    answer: str = Field(..., title="The answer to the question")
    id: str = Field(..., title="The id of the question")


class TaskDTO(BaseModel):
    id: str
    label: str
    type: str
    options: List[str]
    value: str
    image: str
    expiry: int
    answer: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


@app.get("/api/tasks", response_model=List[TaskDTO])
async def get_tasks(db: Session = Depends(get_db)):
    current_time = int(time.time())
    # Remove expired tasks with grace period of 5 seconds
    expired_tasks = db.query(Task).filter(Task.expiry < current_time - 5).all()
    for task in expired_tasks:
        db.delete(task)
    db.commit()
    # Get non-expired tasks with empty answer
    tasks = db.query(Task).filter(Task.expiry >= current_time, Task.answer == "").all()

    # Convert tasks to DTOs
    task_dtos = []
    for task in tasks:
        options = db.query(Option).filter(Option.task_id == task.id).all()
        option_list = [str(option.option) for option in options]
        task_dto = TaskDTO(
            id=str(task.id),
            label=str(task.label),
            type=str(task.type),
            options=option_list,
            value=str(task.value),
            image=str(task.image),
            expiry=int(task.expiry),  # type: ignore
            answer=str(task.answer),
        )
        task_dtos.append(task_dto)
    return task_dtos


@app.get("/api/task/{task_id}", response_model=TaskDTO)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == task_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Task not found")

    options = db.query(Option).filter(Option.task_id == task.id).all()
    option_list = [option.option for option in options]

    task_dto = TaskDTO(
        id=task.id,  # type: ignore
        label=task.label,  # type: ignore
        type=task.type,  # type: ignore
        options=option_list,  # type: ignore
        value=task.value,  # type: ignore
        image=task.image,  # type: ignore
        expiry=task.expiry,  # type: ignore
        answer=task.answer,  # type: ignore
    )
    return task_dto


@app.post("/api/answer")
async def post_answer(answer: Answer, db: Session = Depends(get_db)):
    # remove all expired tasks
    db.query(Task).filter(Task.expiry < int(time.time())).delete()
    db.commit()

    task = db.query(Task).filter(Task.id == answer.id).first()
    if task:
        task.answer = answer.answer  # type: ignore
        db.commit()  # Explicitly commit the session
    else:
        print(f"Task with id {answer.id} not found")
    return JSONResponse(
        status_code=200, content={"status": "success", "message": "Answer updated"}
    )


@app.post("/api/task")
async def post_task(task: TaskDTO, db: Session = Depends(get_db)):
    dbTask = Task(
        id=task.id,
        label=task.label,
        type=task.type,
        value=task.value,
        image=task.image,
        expiry=task.expiry,
        answer="",
    )
    db.add(dbTask)
    db.commit()
    db.refresh(dbTask)
    # Create the associated options
    for option_text in task.options:
        option = Option(task_id=task.id, option=option_text)
        db.add(option)
    db.commit()
    return JSONResponse(
        status_code=200, content={"status": "success", "message": "Task added"}
    )


@app.get("/")
async def root():
    # redirect to the index.html file
    return RedirectResponse("/index.html")


# mount the public directory to the root path after the apis have been defined
app.mount("/", StaticFiles(directory="public"), name="public")
