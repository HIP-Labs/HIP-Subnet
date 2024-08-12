from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import bittensor as bt
import uuid
from hip.protocol import TaskSynapse
from hip.validator.generators.image_generator import generate_image_task
from hip.validator.generators.llm_generator import generate_llm_task
from hip.validator.generators.captcha_generator import generate_captcha_task
from hip.validator.generators.math_generator import generate_math_task

app = FastAPI()

class ModelSubmission(BaseModel):
    model_name: str
    task_type: str
    num_tasks: int
    callback_url: Optional[str] = None

class SubmissionResponse(BaseModel):
    submission_id: str

submissions = {}

@app.post("/submit_model", response_model=SubmissionResponse)
async def submit_model(submission: ModelSubmission):
    submission_id = str(uuid.uuid4())
    submissions[submission_id] = submission
    bt.logging.info(f"Received model submission: {submission}")
    return SubmissionResponse(submission_id=submission_id)

@app.get("/submission_status/{submission_id}")
async def get_submission_status(submission_id: str):
    if submission_id not in submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
    # will need to change to check the status of the submission instead of just returning processing
    return {"status": "processing"}

@app.get("/get_trained_model/{submission_id}")
async def get_trained_model(submission_id: str):
    if submission_id not in submissions:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission = submissions[submission_id]
    
    # In a real implementation, you'd retrieve the trained model based on the submission
    # For this example, we'll just return a success message
    return {"message": "Model trained successfully", "model_name": submission.model_name}

def generate_external_task(model_name: str, task_type: str) -> TaskSynapse:
    # This function should be implemented to generate tasks based on the submitted model
    # For now, I have used the existing task generators as placeholders
    task_generators = {
        "image": generate_image_task,
        "llm": generate_llm_task,
        "captcha": generate_captcha_task,
        "math": generate_math_task
    }
    
    if task_type not in task_generators:
        raise ValueError(f"Unsupported task type: {task_type}")
    
    return task_generators[task_type]()
