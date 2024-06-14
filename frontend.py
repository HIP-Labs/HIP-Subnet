from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
import os
from fastapi.middleware.cors import CORSMiddleware
from hip.miner.db import SQLiteClient

app = FastAPI()

tasks_db = SQLiteClient("tasks.db")
tasks_db.check_schema()
tasks_db.connect()
tasks_db.create_tables()
tasks_db.remove_expired_tasks()


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
    id: str = Field(..., title="The id of the question")


@app.get("/api/tasks")
async def get_tasks():
    tasks = tasks_db.get_all_unanswered_tasks()
    return JSONResponse(content=tasks)


@app.post("/api/answer")
async def post_answer(answer: Answer):
    tasks_db.update_answer(answer.id, answer.answer)
    return JSONResponse(
        status_code=200, content={"status": "success", "message": "Answer updated"}
    )


@app.get("/")
async def root():
    # redirect to the index.html file
    return RedirectResponse("/index.html")


# mount the public directory to the root path after the apis have been defined
app.mount("/", StaticFiles(directory="public"), name="public")
