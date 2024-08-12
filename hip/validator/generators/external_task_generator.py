from transformers import AutoModelForCausalLM, AutoTokenizer
import bittensor as bt
from hip.protocol import TaskSynapse
import uuid

def generate_external_task(model_name: str, task_type: str) -> TaskSynapse: # Fingers crossed lol.
    try:
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Generate a prompt based on the task type
        if task_type == "text_generation":
            prompt = "Generate a short story about:"
        elif task_type == "question_answering":
            prompt = "Answer the following question:"
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

        # Generate text using the model
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=100)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Create a TaskSynapse object
        task = TaskSynapse(
            id=str(uuid.uuid4()),
            label=f"{task_type} task",
            type="text",
            options=[],
            value=generated_text,
            image="",
            answer=""
        )

        return task
    except Exception as e:
        bt.logging.error(f"Error generating external task: {str(e)}")
        raise