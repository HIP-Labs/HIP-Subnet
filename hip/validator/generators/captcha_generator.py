import uuid
from captcha.image import ImageCaptcha
import random
from io import BytesIO
import base64

from hip.protocol import TaskSynapse


def generate_random_string(length=5):
    return "".join(random.choices("12346789ABCDEFGHIJKLMNPQRTUVWXYZ", k=length))


def generate_captcha() -> dict[str, str]:
    image = ImageCaptcha()
    captcha_text = generate_random_string()
    data: BytesIO = image.generate(captcha_text)
    image_base64 = base64.b64encode(data.getvalue()).decode("utf-8")
    mime_type = "data:image/png;base64,"
    return {
        "image": mime_type + image_base64,
        "text": captcha_text,
    }


def generate_captcha_task():
    generated_captcha = generate_captcha()
    return TaskSynapse(
        id=str(uuid.uuid4()),
        label="Enter the text from the image",
        type="text",
        options=[],
        value="",
        image=generated_captcha["image"],
        answer=generated_captcha["text"],
    )


if __name__ == "__main__":
    print(generate_captcha())
