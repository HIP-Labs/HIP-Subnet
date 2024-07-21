import random
import uuid
from PIL import Image, ImageDraw, ImageFont
from hip.protocol import TaskSynapse
from io import BytesIO
import base64


def generate_math_task() -> TaskSynapse:
    """
    Generates an image containing a math equation and the answer
    @return: The base64 encoded image in a TaskSynapse object
    """
    width, height = 200, 100
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Generate a basic math task (e.g., addition, subtraction)
    num1 = random.randint(0, 9)
    num2 = random.randint(0, 9)
    operation = random.choice(["+", "-", "*"])

    result = 0

    if operation == "+":
        result = num1 + num2
    elif operation == "-":
        result = num1 - num2
    else:
        result = num1 * num2

    math_task = f"{num1} {operation} {num2} = ?"

    # Define the font and size
    font = ImageFont.load_default()
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font = ImageFont.load_default(size=32)
    bbox = draw.textbbox((0, 0), math_task, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), math_task, fill="black", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # Append the data type
    image_base64 = f"data:image/png;base64,{image_base64}"
    return TaskSynapse(
        id=str(uuid.uuid4()),
        label="Solve the math task",
        type="text",
        options=[],
        value="",
        image=image_base64,
        answer=str(result),
    )


if __name__ == "__main__":
    task = generate_math_task()
    print(task.to_dict())
