from captcha.image import ImageCaptcha
import random
from io import BytesIO
import base64


def generate_random_string(length=5):
    return "".join(random.choices("12346789ABCDEFGHIJKLMNPQRTUVWXYZ", k=length))


def generate_capcha() -> dict[str, str]:
    image = ImageCaptcha()
    captcha_text = generate_random_string()
    data: BytesIO = image.generate(captcha_text)
    image_base64 = base64.b64encode(data.getvalue()).decode("utf-8")
    mime_type = "data:image/png;base64,"
    return {
        "image": mime_type + image_base64,
        "text": captcha_text,
    }


if __name__ == "__main__":
    print(generate_capcha())
