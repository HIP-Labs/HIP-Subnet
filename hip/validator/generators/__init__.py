from .captcha_generator import generate_captcha_task
from .image_generator import generate_image_task
from .llm_generator import generate_llm_task
from .math_generator import generate_math_task

# exporting as generator
__all__ = [
    "generate_captcha_task",
    "generate_image_task",
    "generate_llm_task",
    "generate_math_task",
]
