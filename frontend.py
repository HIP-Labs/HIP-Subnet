from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
from tinydb import TinyDB, where
import os
import json
from fastapi.middleware.cors import CORSMiddleware

# define absolute paths to the databases
tasks_path = os.path.join(os.path.dirname(__file__), "tasks_db.json")
tasks_db = TinyDB("./tasks_db.json")
answers_path = os.path.join(os.path.dirname(__file__), "answers_db.json")
answers_db = TinyDB(answers_path)

app = FastAPI()

enable_cors = os.environ.get("CORS")
if enable_cors:
    # enable cors
    print("Warning: CORS enabled for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class Answer(BaseModel):
    answer: str = Field(..., title="The answer to the question")
    captchaValue: str = Field(..., title="The captcha value")
    id: str = Field(..., title="The id of the question")


@app.get("/api/tasks")
async def get_tasks():
    tasks = tasks_db.all()
    return JSONResponse(content=tasks)


@app.post("/api/answer")
async def post_answer(answer: Answer):
    # see if question is in the tasks_db
    question = tasks_db.get(where("id") == answer.id)
    if question is None:
        return JSONResponse(
            content={"status": "error", "message": "Question not found"}
        )
    # question must not be a list
    if isinstance(question, list):
        return JSONResponse(
            content={"status": "error", "message": "Question not found"}
        )
    # check if question type is "select" if yes then check if the answer is in the options
    if question["type"] == "select":
        if answer.answer not in question["options"]:
            return JSONResponse(
                content={"status": "error", "message": "Answer not in options"}
            )
    # check if the answer is already in the answers_db
    existing_answer = answers_db.get(where("id") == answer.id)
    if existing_answer is not None:
        return JSONResponse(
            content={"status": "error", "message": "Answer already exists"}
        )

    answers_db.insert(answer.dict())
    tasks_db.remove(where("id") == answer.id)
    return JSONResponse(content={"status": "ok"})


@app.get("/")
async def root():
    # redirect to the index.html file
    return RedirectResponse("/index.html")


# mount the public directory to the root path after the apis have been defined
app.mount("/", StaticFiles(directory="public"), name="public")
