import random
import uuid
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
import torch
from hip.protocol import TaskSynapse
from hip.validator import text_generator
from io import BytesIO
import base64

from hip.validator.words import get_random_animals, get_random_objects

pipeline = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
).to("cuda:1")


def generate_image_task() -> TaskSynapse:
    """
    Generates an image based on the prompt
    @param prompt: The prompt to generate the image
    @return: The base64 encoded image
    """
    type_to_prompt = random.choice(["animal", "object"])
    choices = []
    label = "What [replace] do you see in the given image?"
    if type_to_prompt == "animal":
        choices = get_random_animals()
        label = label.replace("[replace]", "animal")
    elif type_to_prompt == "object":
        choices = get_random_objects()
        label = label.replace("[replace]", "object")
    answer = f"{random.choice(choices)}"
    image = pipeline(prompt=answer, guidance_scale=0.0, num_inference_steps=1).images[0]
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # Append the data type
    image_base64 = f"data:image/png;base64,{image_base64}"
    return TaskSynapse(
        id=str(uuid.uuid4()),
        label=label,
        type="select",
        options=choices,
        value="",
        image=image_base64,
        answer=answer,
    )


if __name__ == "__main__":
    task = generate_image_task()
